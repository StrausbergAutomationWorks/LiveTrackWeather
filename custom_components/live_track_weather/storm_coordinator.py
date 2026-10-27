"""Polling coordinator for tropical cyclones (contract D15).

* NHC `CurrentStorms.json` every 5 minutes with If-None-Match (it changes with
  each advisory; measured unchanged for 4.5 h between two). Each storm's cone,
  forecast track and current wind extent carry the advisory number in their
  URL, so they are fetched once per advisory and kept by URL; the best track's
  URL does not change, so it is fetched again when the advisory does.
* EONET open severeStorms every 30 minutes.

A failed request never clears the map: the last good answer of that source is
kept for NHC_KEEP_S or EONET_KEEP_S, then dropped (a storm shown long after its
source went quiet is worse than none). This coordinator never raises, so a
source being down never makes the entities unavailable.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timedelta, timezone
from typing import Any

import aiohttp

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from . import storms as st
from .const import (
    DOMAIN,
    EONET_KEEP_S,
    EONET_POLL_S,
    EONET_STALE_H,
    EONET_URL,
    NHC_KEEP_S,
    NHC_POLL_S,
    NHC_URL,
    REQUEST_TIMEOUT,
    USER_AGENT,
)

_LOGGER = logging.getLogger(__name__)

# NHC product kinds this coordinator reads, and how each file is parsed.
_PRODUCTS = {
    "trackCone": ("cone", st.cone_polygons),
    "forecastTrack": ("forecast", st.forecast_line),
    "initialWindExtent": ("wind", st.wind_extent),
    "bestTrackGIS": ("past", st.best_track_points),
}


def _parse_json(raw: bytes) -> Any:
    try:
        return json.loads(raw)
    except ValueError:
        return None


def _parse_product(fn, raw: bytes) -> Any:
    kml = st.kml_from_kmz(raw)
    if kml is None:
        return None
    try:
        return fn(kml)
    except Exception:  # noqa: BLE001 - a bad file must not stop the others
        return None


class StormCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        super().__init__(hass, _LOGGER, config_entry=entry, name=f"{DOMAIN}_storms",
                         update_interval=timedelta(seconds=NHC_POLL_S))
        self._session = async_get_clientsession(hass)
        self._nhc_etag: str | None = None
        self._nhc: list[dict] = []
        self._nhc_ok: datetime | None = None
        self._eonet_doc: Any = None
        self._eonet_ok: datetime | None = None
        self._eonet_tried: datetime | None = None
        # (url, advisory) -> parsed product, for the products in use only
        self._products: dict[tuple[str, int | None], Any] = {}

    async def _get(self, url: str, etag: str | None = None) -> tuple[int | None, bytes | None, str | None]:
        headers = {"User-Agent": USER_AGENT}
        if etag:
            headers["If-None-Match"] = etag
        try:
            async with self._session.get(url, headers=headers,
                                         timeout=aiohttp.ClientTimeout(total=REQUEST_TIMEOUT)) as r:
                if r.status == 200:
                    return 200, await r.read(), r.headers.get("ETag")
                return r.status, None, None
        except (aiohttp.ClientError, TimeoutError) as err:
            _LOGGER.debug("%s failed: %s", url, type(err).__name__)
            return None, None, None

    async def _poll_nhc(self, now: datetime) -> None:
        status, body, etag = await self._get(NHC_URL, self._nhc_etag)
        if status == 304:
            self._nhc_ok = now
        elif status == 200 and body:
            doc = await self.hass.async_add_executor_job(_parse_json, body)
            if isinstance(doc, dict) and isinstance(doc.get("activeStorms"), list):
                self._nhc = st.nhc_storms(doc)
                self._nhc_etag = etag
                self._nhc_ok = now
        else:
            _LOGGER.debug("NHC CurrentStorms answered %s", status)
        if self._nhc_ok is None or (now - self._nhc_ok).total_seconds() > NHC_KEEP_S:
            self._nhc = []
            self._nhc_etag = None

    async def _poll_eonet(self, now: datetime) -> None:
        if self._eonet_tried and (now - self._eonet_tried).total_seconds() < EONET_POLL_S:
            pass
        else:
            self._eonet_tried = now
            status, body, _ = await self._get(EONET_URL)
            if status == 200 and body:
                doc = await self.hass.async_add_executor_job(_parse_json, body)
                if isinstance(doc, dict) and isinstance(doc.get("features"), list):
                    self._eonet_doc = doc
                    self._eonet_ok = now
            else:
                _LOGGER.debug("EONET answered %s", status)
        if self._eonet_ok is None or (now - self._eonet_ok).total_seconds() > EONET_KEEP_S:
            self._eonet_doc = None

    async def _products_for(self, s: dict) -> dict[str, Any]:
        out: dict[str, Any] = {}
        for kind, (name, fn) in _PRODUCTS.items():
            url = (s.get("links") or {}).get(kind)
            if not url:
                continue
            key = (url, s.get("advisory"))
            if key not in self._products:
                status, body, _ = await self._get(url)
                if status != 200 or not body:
                    # keep the last parse of this kind for this storm, if any
                    old = next((v for (u, _a), v in self._products.items() if u == url), None)
                    if old is not None:
                        out[name] = old
                    continue
                self._products[key] = await self.hass.async_add_executor_job(_parse_product, fn, body)
            out[name] = self._products[key]
        return out

    async def _async_update_data(self) -> dict[str, Any]:
        now = datetime.now(timezone.utc)
        await self._poll_nhc(now)
        await self._poll_eonet(now)
        eonet = st.eonet_storms(self._eonet_doc, now, EONET_STALE_H) if self._eonet_doc else []
        storms = st.merge(self._nhc, eonet)
        records, polygons, in_use = [], [], set()
        for s in storms:
            products = await self._products_for(s) if s["source"] == "nhc" else {}
            for kind in _PRODUCTS:
                url = (s.get("links") or {}).get(kind)
                if url:
                    in_use.add(url)
            records.append(st.entity_record(s))
            polygons += st.shapes_for(s, products)
        # forget files no storm points at any more, and older advisories of those that do
        latest = {}
        for (u, a) in self._products:
            if u in in_use:
                latest[u] = max(latest.get(u, -1), a if a is not None else -1)
        self._products = {(u, a): v for (u, a), v in self._products.items()
                          if u in in_use and (a if a is not None else -1) == latest[u]}
        attributions = sorted({r["attrs"]["attribution"] for r in records})
        return {
            "storms": records,
            "polygons": polygons,
            "styles": st.STYLES,
            "count": len(records),
            "attribution": "; ".join(attributions) if attributions else st.ATTRIBUTION_NHC,
            "updated": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
        }
