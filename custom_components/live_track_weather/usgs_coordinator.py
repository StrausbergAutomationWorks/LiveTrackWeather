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

from . import firemap, usgs
from .const import CONF_QUAKE_MIN_MAG, DOMAIN, MAP_POINTS_PATH, QUAKE_KEEP_S, QUAKE_POLL_S, REQUEST_TIMEOUT, USER_AGENT
from .firemap_coordinator import _files

_LOGGER = logging.getLogger(__name__)

LAYER = "quakes"


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
        try:
            async with self._session.get(url, headers={"User-Agent": USER_AGENT},
                                         timeout=aiohttp.ClientTimeout(total=REQUEST_TIMEOUT)) as resp:
                if resp.status != 200:
                    return resp.status, None
                raw = await resp.read()
        except (aiohttp.ClientError, TimeoutError) as err:
            _LOGGER.debug("USGS request failed: %s", type(err).__name__)
            return 0, None
        try:
            return 200, await self.hass.async_add_executor_job(json.loads, raw)
        except ValueError:
            return 0, None

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
