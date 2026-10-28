"""Polling for MET Norway's warnings, marine forecasts and forecast points (Weather SSOT item 310).

MET's terms, all kept here: the application named in the User-Agent; `If-Modified-Since` with the previous
`Last-Modified`; never faster than the feed changes; each install's interval jittered once so installs do not
poll in step; a 403 or 429 stops every MET request for MET_BACKOFF_S; a 203 (a deprecated version) is logged
once. A CAP file never changes, so each warning's is fetched once and kept while the warning is listed.
None of these coordinators raises: a failure keeps the last good answer, which is re-read against the clock.
"""

from __future__ import annotations

import json
import logging
import random
import time
from datetime import datetime, timedelta, timezone
from typing import Any

import aiohttp

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from . import met
from .const import (DOMAIN, MET_ALERTS_CAP, MET_ALERTS_POLL_S, MET_ALERTS_RSS, MET_BACKOFF_S, MET_CAP_PER_POLL,
                    MET_COAST_EVERY_S, MET_COAST_URL, MET_JITTER_S, MET_MARINE_KEEP_S, MET_MARINE_POLL_S,
                    MET_POINT_POLL_S, MET_POINT_URL, MET_POINTS, MET_SEA_URL, REQUEST_TIMEOUT, USER_AGENT)

_LOGGER = logging.getLogger(__name__)


class MetClient:
    """One per Home Assistant run: conditional GETs to MET and the shared back-off."""

    def __init__(self, hass: HomeAssistant) -> None:
        self._session = async_get_clientsession(hass)
        self._lm: dict[str, str] = {}
        self._body: dict[str, bytes] = {}
        self.fetched_at: dict[str, float] = {}
        self._block_until = 0.0
        self._warned: set[str] = set()

    def _warn_once(self, key: str, msg: str, *args: Any) -> None:
        if key not in self._warned:
            self._warned.add(key)
            _LOGGER.warning(msg, *args)

    async def get(self, key: str, url: str, params: dict[str, str] | None = None,
                  conditional: bool = True) -> bytes | None:
        """The newest body for `key` (new, or the last one when MET says 304 or fails); None if never had."""
        if time.monotonic() < self._block_until:
            return self._body.get(key)
        headers = {"User-Agent": USER_AGENT}
        if conditional and key in self._lm:
            headers["If-Modified-Since"] = self._lm[key]
        try:
            async with self._session.get(url, params=params, headers=headers,
                                         timeout=aiohttp.ClientTimeout(total=REQUEST_TIMEOUT)) as r:
                if r.status in (200, 203):
                    if r.status == 203:
                        self._warn_once(f"203 {url}", "MET Norway says %s is deprecated (HTTP 203)", url)
                    self._body[key] = await r.read()
                    if r.headers.get("Last-Modified"):
                        self._lm[key] = r.headers["Last-Modified"]
                    self.fetched_at[key] = time.monotonic()
                elif r.status == 304:
                    self.fetched_at[key] = time.monotonic()
                elif r.status in (403, 429):
                    self._block_until = time.monotonic() + MET_BACKOFF_S
                    self._warn_once(f"block {r.status}", "MET Norway answered %s; no MET requests for %s min",
                                    r.status, MET_BACKOFF_S // 60)
                else:
                    _LOGGER.debug("MET Norway %s answered %s", url, r.status)
        except (aiohttp.ClientError, TimeoutError) as err:
            _LOGGER.debug("MET Norway %s failed: %s", url, type(err).__name__)
        return self._body.get(key)

    def cached(self, key: str) -> bytes | None:
        """The last body for `key`, without asking MET."""
        return self._body.get(key)

    def forget(self, key: str) -> None:
        self._body.pop(key, None)
        self._lm.pop(key, None)
        self.fetched_at.pop(key, None)


def met_client(hass: HomeAssistant) -> MetClient:
    data = hass.data.setdefault(DOMAIN, {})
    if "met_client" not in data:
        data["met_client"] = MetClient(hass)
    return data["met_client"]


def _interval(base: int) -> timedelta:
    return timedelta(seconds=base + random.randint(0, MET_JITTER_S))


def _json(raw: bytes | None) -> Any:
    if not raw:
        return None
    try:
        return json.loads(raw)
    except ValueError:
        return None


class MetWarningsCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        super().__init__(hass, _LOGGER, config_entry=entry, name=f"{DOMAIN}_met_warnings",
                         update_interval=_interval(MET_ALERTS_POLL_S))
        self._met = met_client(hass)
        self._caps: dict[str, dict[str, Any]] = {}

    async def _async_update_data(self) -> dict[str, Any]:
        rss = await self._met.get("alerts_rss", MET_ALERTS_RSS, {"lang": "en"})
        ids = await self.hass.async_add_executor_job(met.parse_rss, rss) if rss else []
        for gone in [g for g in self._caps if g not in ids]:
            self._caps.pop(gone)
        fetched = 0
        for g in ids:
            if g in self._caps or fetched >= MET_CAP_PER_POLL:
                continue
            fetched += 1
            raw = await self._met.get(f"cap {g}", MET_ALERTS_CAP, {"cap": g}, conditional=False)
            self._met.forget(f"cap {g}")
            cap = met.parse_cap(raw) if raw else None
            if cap:
                self._caps[g] = cap
        return met.publish_warnings([self._caps[g] for g in ids if g in self._caps], datetime.now(timezone.utc))


class MetMarineCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        super().__init__(hass, _LOGGER, config_entry=entry, name=f"{DOMAIN}_met_marine",
                         update_interval=_interval(MET_MARINE_POLL_S))
        self._met = met_client(hass)
        self._coast_at = 0.0

    async def _async_update_data(self) -> dict[str, Any]:
        sea = await self._met.get("sea_en", MET_SEA_URL)
        if time.monotonic() - self._coast_at >= MET_COAST_EVERY_S or "coast_en" not in self._met.fetched_at:
            self._coast_at = time.monotonic()
            coast = await self._met.get("coast_en", MET_COAST_URL)
        else:
            coast = self._met.cached("coast_en")
        now = time.monotonic()
        sea = sea if now - self._met.fetched_at.get("sea_en", -1e18) <= MET_MARINE_KEEP_S else None
        coast = coast if now - self._met.fetched_at.get("coast_en", -1e18) <= MET_MARINE_KEEP_S else None
        docs = await self.hass.async_add_executor_job(lambda: (_json(sea), _json(coast)))
        return met.publish_marine(*docs)


class MetPointCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        super().__init__(hass, _LOGGER, config_entry=entry, name=f"{DOMAIN}_met_points",
                         update_interval=_interval(MET_POINT_POLL_S))
        self._met = met_client(hass)

    async def _async_update_data(self) -> dict[str, Any]:
        points = []
        for name, lat, lon in MET_POINTS:
            raw = await self._met.get(f"point {name}", MET_POINT_URL, {"lat": f"{lat:.4f}", "lon": f"{lon:.4f}"})
            doc = await self.hass.async_add_executor_job(_json, raw) if raw else None
            rec = met.point(doc, name, lat, lon) if doc else None
            if rec:
                points.append(rec)
        return {"points": points}
