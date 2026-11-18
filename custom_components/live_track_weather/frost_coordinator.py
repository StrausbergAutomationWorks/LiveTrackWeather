"""Polling MET Norway's Frost with the user's own client ID (Weather SSOT item 311; contract D22).

Frost's terms, kept here: a client ID per user (the option, sent as the HTTP Basic user); cache headers respected
(Frost sends max-age 6-60 s and no validator, and nothing here asks more often than every FROST_POLL_S); well under one
request a second on average. A 401 (a client ID Frost does not know) stops every Frost request until the options
change; a 429 or 503 stops them for Retry-After seconds; 403 ("too many observations") is logged once. A failure keeps
the last good answer, which still leaves by the 2-hour rule. Nothing here raises.
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

from . import frost
from .const import DOMAIN, FROST_POLL_S, FROST_SOURCES_S, MET_JITTER_S, REQUEST_TIMEOUT, USER_AGENT

_LOGGER = logging.getLogger(__name__)


class FrostClient:
    """One per Home Assistant run and client ID: the requests and the shared rest after an error."""

    def __init__(self, hass: HomeAssistant, client_id: str) -> None:
        self.hass = hass
        self.client_id = client_id
        self._session = async_get_clientsession(hass)
        self._auth = aiohttp.BasicAuth(client_id, "")
        self._block_until = 0.0
        self.rejected = False
        self._warned: set[str] = set()

    def _warn_once(self, key: str, msg: str, *args: Any) -> None:
        if key not in self._warned:
            self._warned.add(key)
            _LOGGER.warning(msg, *args)

    async def get(self, url: str, params: dict[str, str]) -> tuple[int, Any]:
        """(HTTP status, parsed JSON or None); (0, None) while Frost is being left alone or did not answer."""
        if self.rejected or time.monotonic() < self._block_until:
            return 0, None
        try:
            async with self._session.get(url, params=params, auth=self._auth, headers={"User-Agent": USER_AGENT},
                                         timeout=aiohttp.ClientTimeout(total=REQUEST_TIMEOUT)) as r:
                status = r.status
                if status == 200:
                    raw = await r.read()
                elif status == 401:
                    self.rejected = True
                    self._warn_once("401", "MET Norway's Frost does not know this client ID (HTTP 401); "
                                    "nothing more is asked of Frost until the options change")
                    return status, None
                elif status in (429, 503):
                    rest = frost.retry_s(r.headers)
                    self._block_until = time.monotonic() + rest
                    _LOGGER.debug("Frost answered %s; no Frost requests for %s s", status, rest)
                    return status, None
                else:
                    if status == 403:
                        self._warn_once("403", "MET Norway's Frost refused a request as too large (HTTP 403)")
                    elif status != 412:
                        _LOGGER.debug("Frost %s answered %s", url, status)
                    return status, None
        except (aiohttp.ClientError, TimeoutError) as err:
            _LOGGER.debug("Frost %s failed: %s", url, type(err).__name__)
            return 0, None
        try:
            return 200, await self.hass.async_add_executor_job(json.loads, raw)
        except ValueError:
            return 0, None


def frost_client(hass: HomeAssistant, client_id: str, fresh: bool = False) -> FrostClient:
    """The run's client for this client ID; a new ID, or `fresh` (each entry set-up, so an options change clears a
    401 or a rest), gets a new one."""
    data = hass.data.setdefault(DOMAIN, {})
    held = data.get("frost_client")
    if fresh or held is None or held.client_id != client_id:
        held = data["frost_client"] = FrostClient(hass, client_id)
    return held


async def async_check_id(hass: HomeAssistant, client_id: str) -> str | None:
    """The options' check of a new client ID: one /sources request for one station. None when Frost takes it."""
    try:
        async with async_get_clientsession(hass).get(
                frost.SOURCES_URL, params=frost.CHECK_PARAMS, auth=aiohttp.BasicAuth(client_id, ""),
                headers={"User-Agent": USER_AGENT}, timeout=aiohttp.ClientTimeout(total=REQUEST_TIMEOUT)) as resp:
            return frost.check_error(resp.status)
    except (aiohttp.ClientError, TimeoutError):
        return "frost_cannot_connect"


class FrostStationsCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """The map's Svalbard and Jan Mayen stations (contract D22): the list once a day, the readings every
    FROST_POLL_S plus a jitter chosen once per install."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry, client_id: str) -> None:
        super().__init__(hass, _LOGGER, config_entry=entry, name=f"{DOMAIN}_frost",
                         update_interval=timedelta(seconds=FROST_POLL_S + random.randint(0, MET_JITTER_S)))
        self._frost = frost_client(hass, client_id)
        self._sources: list[dict[str, Any]] = []
        self._sources_at = -1e18
        self._latest: dict[str, dict[str, dict[str, Any]]] = {}

    async def _async_update_data(self) -> dict[str, Any]:
        if not self._sources or time.monotonic() - self._sources_at >= FROST_SOURCES_S:
            status, doc = await self._frost.get(frost.SOURCES_URL, frost.sources_params())
            if status == 200:
                found = frost.parse_sources(doc)
                if found:
                    self._sources, self._sources_at = found, time.monotonic()
        now = datetime.now(timezone.utc)
        if self._sources:
            status, doc = await self._frost.get(
                frost.OBS_URL, frost.latest_params([s["id"] for s in self._sources], frost.MAP_ELEMENTS))
            if status == 200:
                self._latest = frost.parse_latest(doc, now)
            elif status == 412:
                self._latest = {}
        return {"stations": frost.station_markers(self._sources, self._latest, now)}
