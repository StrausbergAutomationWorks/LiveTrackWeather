"""Earthquakes (Weather SSOT item 352, contract D20): fetch USGS's all_day feed, publish the markers' records, the D19
point file and the ShakeMap lines, and hand the events to the watched places.

* The feed every QUAKE_POLL_S (it is regenerated every minute, max-age=60; about 170 KB, gzip on the wire).
* A ShakeMap: the event's detail GeoJSON once per `updated`, its cont_mmi.json once per URL (the URL carries the
  product's version); only for usgs.shakemap_candidates().
* A failed poll keeps the last good answer for QUAKE_KEEP_S, then everything goes (a stale quake list is worse than
  none). This coordinator never raises, so USGS being down never makes the entities unavailable.

The point file is served by firemap_coordinator.PointsView under the layer "quakes".
"""

from __future__ import annotations

import json
import logging
import time
from datetime import datetime, timedelta, timezone
from typing import Any

import aiohttp

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from . import firemap, lsr, usgs
from .const import (CONF_QUAKE_MIN_MAG, DOMAIN, LSR_KEEP_S, LSR_POLL_S, MAP_POINTS_PATH, QUAKE_KEEP_S, QUAKE_POLL_S,
                    REQUEST_TIMEOUT,
                    RIVER_KEEP_S, RIVER_POLL_S, USER_AGENT, VOLCANO_KEEP_S, VOLCANO_LIST_S, VOLCANO_POLL_S,
                    VOLCANO_ZONES_FILE)
from .firemap_coordinator import _files

_LOGGER = logging.getLogger(__name__)

LAYER = "quakes"


async def _fetch_json(hass: HomeAssistant, session: aiohttp.ClientSession, url: str,
                      params: dict[str, str] | None = None) -> tuple[int, Any]:
    """(status, parsed JSON); status 0 for a failure or a body that is not JSON."""
    try:
        async with session.get(url, params=params, headers={"User-Agent": USER_AGENT},
                               timeout=aiohttp.ClientTimeout(total=REQUEST_TIMEOUT)) as resp:
            if resp.status != 200:
                return resp.status, None
            raw = await resp.read()
    except (aiohttp.ClientError, TimeoutError) as err:
        _LOGGER.debug("request to %s failed: %s", url.split("?")[0], type(err).__name__)
        return 0, None
    try:
        return 200, await hass.async_add_executor_job(json.loads, raw)
    except ValueError:
        return 0, None


class QuakeCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        super().__init__(hass, _LOGGER, config_entry=entry, name=f"{DOMAIN}_quakes",
                         update_interval=timedelta(seconds=QUAKE_POLL_S))
        self._session = async_get_clientsession(hass)
        self.min_mag = usgs.min_magnitude(entry.options.get(CONF_QUAKE_MIN_MAG))
        self._events: list[dict[str, Any]] | None = None
        self._good_at = 0.0
        self.reason: str | None = None
        self._details: dict[tuple[str, str], str | None] = {}     # (event id, updated) -> cont_mmi url
        self._contours: dict[str, Any] = {}                       # cont_mmi url -> parsed file

    async def _get(self, url: str) -> tuple[int, Any]:
        return await _fetch_json(self.hass, self._session, url)

    async def _shakemaps(self, events: list[dict[str, Any]]) -> tuple[list, dict, list[str]]:
        polygons: list[dict[str, Any]] = []
        styles: dict[str, dict[str, Any]] = {}
        drawn: list[str] = []
        wanted = usgs.shakemap_candidates(events)
        keep_d, keep_c = set(), set()
        for ev in wanted:
            dkey = (ev["id"], ev["updated"].isoformat())
            keep_d.add(dkey)
            if dkey not in self._details:
                status, doc = await self._get(ev["detail"])
                if status != 200:
                    # keep the URL of an older version of this event, if any
                    old = next((u for (i, _), u in self._details.items() if i == ev["id"] and u), None)
                    if old:
                        keep_c.add(old)
                        if old in self._contours:
                            items, st = usgs.shakemap_shapes(self._contours[old], ev)
                            polygons += items
                            styles.update(st)
                            drawn.append(ev["id"])
                    continue
                self._details[dkey] = usgs.contours_url(doc)
            url = self._details[dkey]
            if not url:
                continue
            keep_c.add(url)
            if url not in self._contours:
                status, doc = await self._get(url)
                if status != 200:
                    continue
                self._contours[url] = doc
            items, st = usgs.shakemap_shapes(self._contours[url], ev)
            if items:
                polygons += items
                styles.update(st)
                drawn.append(ev["id"])
        self._details = {k: v for k, v in self._details.items() if k in keep_d or v in keep_c}
        self._contours = {k: v for k, v in self._contours.items() if k in keep_c}
        return polygons, styles, drawn

    async def _async_update_data(self) -> dict[str, Any]:
        status, doc = await self._get(usgs.QUAKE_FEED_URL)
        events = usgs.parse_feed(doc) if status == 200 else None
        if events is not None:
            self._events = events
            self._good_at = time.time()
            self.reason = None
        else:
            self.reason = f"USGS's feed answered {status or 'nothing'}"
            if self._events is not None and time.time() - self._good_at > QUAKE_KEEP_S:
                self._events = None
        if self._events is None:
            return {"quakes": [], "events": [], "count": None, "url": None, "quakes_today": None,
                    "polygons": [], "styles": {}, "shakemaps": [], "updated": None}
        events = self._events
        now = datetime.now(timezone.utc)
        points = usgs.quake_points(events, self.min_mag)
        digest, gz = await self.hass.async_add_executor_job(
            firemap.point_file, points, usgs.QUAKE_COLUMNS, {"source": "USGS all_day", "min_magnitude": self.min_mag})
        files = _files(self.hass)
        prev = files.get(LAYER)
        files[LAYER] = (digest, gz)
        if prev and prev[0] != digest:
            files[f"{LAYER}:prev"] = prev
        polygons, styles, drawn = await self._shakemaps(events)
        return {
            "quakes": [usgs.quake_record(ev) for ev in events if usgs.is_marker(ev)],
            "events": events,
            "count": len(points),
            "url": f"{MAP_POINTS_PATH}/{LAYER}/{digest}",
            "quakes_today": len(events),
            "polygons": polygons,
            "styles": styles,
            "shakemaps": drawn,
            "updated": now.isoformat(timespec="seconds"),
        }


class VolcanoCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Elevated volcanoes (Weather SSOT item 352 step 2, contract D20): HANS's elevated list and its CAP list every
    VOLCANO_POLL_S, the US list (positions) every VOLCANO_LIST_S, the shipped threat layer read once. The last good
    answer is kept VOLCANO_KEEP_S. Never raises."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        super().__init__(hass, _LOGGER, config_entry=entry, name=f"{DOMAIN}_volcanoes",
                         update_interval=timedelta(seconds=VOLCANO_POLL_S))
        self._session = async_get_clientsession(hass)
        self.zones: dict[str, list[dict[str, Any]]] = {}
        self._zones_read = False
        self._us: dict[str, dict[str, Any]] | None = None
        self._us_at = 0.0
        self._list: list[dict[str, Any]] | None = None
        self._good_at = 0.0
        self.reason: str | None = None

    async def _get(self, url: str) -> tuple[int, Any]:
        return await _fetch_json(self.hass, self._session, url)

    async def _async_update_data(self) -> dict[str, Any]:
        if not self._zones_read:
            self._zones_read = True
            try:
                self.zones = await self.hass.async_add_executor_job(_read_zones)
            except (OSError, ValueError) as err:
                _LOGGER.warning("The volcanic threat layer could not be read (%s); volcanoes will not turn places on",
                                type(err).__name__)
        if self._us is None or time.time() - self._us_at > VOLCANO_LIST_S:
            status, doc = await self._get(usgs.HANS_US_URL)
            got = usgs.us_volcanoes(doc) if status == 200 else None
            if got:
                self._us, self._us_at = got, time.time()
        s1, elev = await self._get(usgs.HANS_ELEVATED_URL)
        s2, cap = await self._get(usgs.HANS_CAP_URL)
        found = usgs.elevated(elev, cap if s2 == 200 else None, self._us) if s1 == 200 and self._us else None
        if found is not None:
            self._list, self._good_at, self.reason = found, time.time(), None
        else:
            self.reason = "HANS did not answer" if s1 != 200 else "USGS's volcano list not read yet"
            if self._list is not None and time.time() - self._good_at > VOLCANO_KEEP_S:
                self._list = None
        vols = self._list or []
        return {"volcanoes": [usgs.volcano_record(v) for v in vols], "elevated": vols,
                "updated": datetime.now(timezone.utc).isoformat(timespec="seconds")}


def _read_zones() -> dict[str, list[dict[str, Any]]]:
    import gzip
    from pathlib import Path
    raw = (Path(__file__).parent / VOLCANO_ZONES_FILE).read_bytes()
    return usgs.threat_zones(json.loads(gzip.decompress(raw)))


class RiverCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Rivers flooding now or forecast to (Weather SSOT item 352 step 3 and item 308, contract D20): NOAA's riv_gauges
    map service, layer 15 (forecast) and layer 0 (observed), minor and up, every RIVER_POLL_S ("Update Frequency: 30
    Minutes"; 5-7 KB each). Each layer's last good answer is kept RIVER_KEEP_S on its own. Never raises."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        super().__init__(hass, _LOGGER, config_entry=entry, name=f"{DOMAIN}_rivers",
                         update_interval=timedelta(seconds=RIVER_POLL_S))
        self._session = async_get_clientsession(hass)
        # "forecast" / "observed" -> (list or None, monotonic-free time of the last good answer)
        self._lists: dict[str, tuple[list[dict[str, Any]] | None, float]] = {"forecast": (None, 0.0),
                                                                              "observed": (None, 0.0)}
        self.reason: str | None = None

    async def _layer(self, which: str, url: str) -> str | None:
        status, doc = await _fetch_json(self.hass, self._session, url, usgs.RIVER_PARAMS)
        found = usgs.river_gauges(doc, observed=which == "observed") if status == 200 else None
        if found is not None:
            self._lists[which] = (found, time.time())
            return None
        held, at = self._lists[which]
        if held is not None and time.time() - at > RIVER_KEEP_S:
            self._lists[which] = (None, at)
        return f"NWPS {which} answered {status or 'nothing'}"

    async def _async_update_data(self) -> dict[str, Any]:
        reasons = [r for r in (await self._layer("forecast", usgs.RIVER_URL),
                               await self._layer("observed", usgs.RIVER_OBS_URL)) if r]
        self.reason = "; ".join(reasons) or None
        return {"rivers": usgs.river_records(self._lists["forecast"][0], self._lists["observed"][0]),
                "updated": datetime.now(timezone.utc).isoformat(timespec="seconds")}


class StormReportCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Storm reports (Weather SSOT item 312, contract D21): NWS Local Storm Reports of the last 24 hours, the kinds in
    lsr.KINDS, as a D19 point file under the layer "storm_reports", every LSR_POLL_S with If-None-Match. The file is
    rebuilt on every poll, since the reports' age bands move. A failed poll keeps the last good answer LSR_KEEP_S,
    then the layer empties. Never raises."""

    LAYER = "storm_reports"

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        super().__init__(hass, _LOGGER, config_entry=entry, name=f"{DOMAIN}_storm_reports",
                         update_interval=timedelta(seconds=LSR_POLL_S))
        self._session = async_get_clientsession(hass)
        self._doc: Any = None
        self._etag: str | None = None
        self._good_at = 0.0
        self.reason: str | None = None

    async def _fetch(self) -> int:
        headers = {"User-Agent": USER_AGENT}
        if self._etag and self._doc is not None:
            headers["If-None-Match"] = self._etag
        try:
            async with self._session.get(lsr.URL, params=lsr.PARAMS, headers=headers,
                                         timeout=aiohttp.ClientTimeout(total=REQUEST_TIMEOUT)) as resp:
                if resp.status == 304:
                    return 304
                if resp.status != 200:
                    return resp.status
                raw = await resp.read()
                etag = resp.headers.get("ETag")
        except (aiohttp.ClientError, TimeoutError) as err:
            _LOGGER.debug("storm reports failed: %s", type(err).__name__)
            return 0
        try:
            doc = await self.hass.async_add_executor_job(json.loads, raw)
        except ValueError:
            return 0
        if lsr.points(doc, datetime.now(timezone.utc)) is None:
            return 0
        self._doc, self._etag = doc, etag
        return 200

    async def _async_update_data(self) -> dict[str, Any]:
        status = await self._fetch()
        if status in (200, 304):
            self._good_at, self.reason = time.time(), None
        else:
            self.reason = f"NWS's storm reports answered {status or 'nothing'}"
            if self._doc is not None and time.time() - self._good_at > LSR_KEEP_S:
                self._doc, self._etag = None, None
        if self._doc is None:
            return {"count": None, "url": None, "updated": None}
        now = datetime.now(timezone.utc)
        points = lsr.points(self._doc, now) or []
        digest, gz = await self.hass.async_add_executor_job(
            firemap.point_file, points, lsr.COLUMNS, {"source": "NWS LSR last 24 hours"})
        files = _files(self.hass)
        prev = files.get(self.LAYER)
        files[self.LAYER] = (digest, gz)
        if prev and prev[0] != digest:
            files[f"{self.LAYER}:prev"] = prev
        return {"count": len(points), "url": f"{MAP_POINTS_PATH}/{self.LAYER}/{digest}",
                "updated": now.isoformat(timespec="seconds")}
