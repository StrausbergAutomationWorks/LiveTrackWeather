"""The fire-and-smoke map's two publishers (06_MAP_CONTRACT_OVERLAYS.md D19): fetch, build the point file, serve it.

* FireMap: FIRMS's keyless 24-hour VIIRS files for the chosen regions, conditional (ETag), every MAP_POLL_S, with the
  standing heat sources removed by a per-region list built from the keyed API's standard product and kept in
  .storage (MAP_STATIC_STORE_KEY) for MAP_STATIC_REFRESH_S. Nothing is published for a region without its list:
  without one, every mill would be drawn as a fire.
* AirSitesMap: AirNow's `data/` for the chosen regions' boxes, PM2.5, the last complete hour.
* PointsView: `/api/live_track_weather/points/<layer>/<digest>`, signed in (the card asks with hass.callApi), the
  gzipped file with a long private cache: the URL changes when the points do.

A failed fetch keeps the last good file for MAP_KEEP_S. Parsing and gzip run in the executor: the Global files are
4-5 MB each and the world's standard-product answer about 28 MB (measured 2026-11-17).
"""

from __future__ import annotations

import asyncio
import json
import logging
import time
from datetime import datetime, timedelta, timezone
from typing import Any

import aiohttp
from aiohttp import web

from homeassistant.components.http import KEY_HASS, HomeAssistantView
from homeassistant.components.sensor import SensorEntity, SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.storage import Store
from homeassistant.helpers.update_coordinator import CoordinatorEntity, DataUpdateCoordinator, UpdateFailed

from . import firemap, hazards
from .const import (AIRNOW_DATA_URL, CONF_AIRNOW_KEY, CONF_FIRMS_KEY, CONF_MAP_REGIONS, DOMAIN, FIRMS_AREA_URL,
                    FIRMS_AVAIL_URL, MAP_KEEP_S, MAP_POINTS_PATH, MAP_POLL_S, MAP_STATIC_REFRESH_S,
                    MAP_STATIC_STORE_KEY, REQUEST_TIMEOUT, USER_AGENT)

_LOGGER = logging.getLogger(__name__)
_GAP_S = 1.5            # between calls to one service
_BIG_TIMEOUT = 300      # the world's standard product is about 28 MB


def _files(hass: HomeAssistant) -> dict[str, tuple[str, bytes]]:
    """layer -> (digest, gzipped file), shared with the view; the previous file is kept for a page mid-fetch."""
    return hass.data.setdefault(DOMAIN, {}).setdefault("points", {})


class _PointMap(DataUpdateCoordinator[dict[str, Any]]):
    LAYER = ""
    KEY_OPTION = ""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        super().__init__(hass, _LOGGER, name=f"{DOMAIN} {self.LAYER}", update_interval=timedelta(seconds=MAP_POLL_S))
        self.entry = entry
        self.key = (entry.options.get(self.KEY_OPTION) or "").strip()
        self.regions = firemap.regions_of(entry.options.get(CONF_MAP_REGIONS))
        self._session = async_get_clientsession(hass)
        self._last_call = 0.0
        self._good_at = 0.0
        self.reason: str | None = None

    @classmethod
    def wanted(cls, entry: ConfigEntry) -> bool:
        return bool((entry.options.get(cls.KEY_OPTION) or "").strip()) and bool(
            firemap.regions_of(entry.options.get(CONF_MAP_REGIONS)))

    async def _get(self, url: str, params: dict[str, str] | None = None, headers: dict[str, str] | None = None,
                   timeout: int = REQUEST_TIMEOUT) -> tuple[int, str, dict[str, str]]:
        wait = _GAP_S - (time.monotonic() - self._last_call)
        if wait > 0:
            await asyncio.sleep(wait)
        try:
            async with self._session.get(url, params=params, headers={"User-Agent": USER_AGENT, **(headers or {})},
                                         timeout=aiohttp.ClientTimeout(total=timeout)) as resp:
                text = await resp.text() if resp.status == 200 else ""
                return resp.status, text, dict(resp.headers)
        except (aiohttp.ClientError, TimeoutError) as err:
            _LOGGER.debug("%s request failed: %s", self.LAYER, type(err).__name__)
            return 0, "", {}
        finally:
            self._last_call = time.monotonic()

    async def _publish(self, points: list[list[Any]], columns: list[dict[str, str]], meta: dict[str, Any]) -> dict:
        digest, gz = await self.hass.async_add_executor_job(firemap.point_file, points, columns, meta)
        files = _files(self.hass)
        prev = files.get(self.LAYER)
        files[self.LAYER] = (digest, gz)
        if prev and prev[0] != digest:
            files[f"{self.LAYER}:prev"] = prev
        self._good_at = time.time()
        self.reason = None
        return {"count": len(points), "url": f"{MAP_POINTS_PATH}/{self.LAYER}/{digest}",
                "updated": datetime.now(timezone.utc).isoformat(timespec="seconds")}

    def _keep_or_fail(self, reason: str) -> dict[str, Any]:
        """A failed poll: the last good file stays for MAP_KEEP_S, then the layer goes unavailable."""
        self.reason = reason
        if self.data and time.time() - self._good_at < MAP_KEEP_S:
            _LOGGER.debug("%s: %s; keeping the last good file", self.LAYER, reason)
            return self.data
        raise UpdateFailed(reason)


class FireMap(_PointMap):
    LAYER = "fires"
    KEY_OPTION = CONF_FIRMS_KEY

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        super().__init__(hass, entry)
        self._store: Store[dict[str, Any]] = Store(hass, 1, MAP_STATIC_STORE_KEY)
        self._lists: dict[str, Any] | None = None
        self._cache: dict[str, tuple[str, list[list[Any]]]] = {}   # url -> (etag, points)

    async def _load_lists(self) -> dict[str, Any]:
        if self._lists is None:
            stored = await self._store.async_load()
            self._lists = stored if isinstance(stored, dict) and isinstance(stored.get("regions"), dict) else {
                "regions": {}}
        return self._lists

    async def _static_list(self, region: str, max_dates: dict[str, str] | None) -> tuple[set | None, dict | None]:
        """The region's cells, built when missing, stale or built with other windows. Returns (cells or None,
        max_dates as now known)."""
        lists = await self._load_lists()
        spec = firemap.REGIONS[region]
        have = lists["regions"].get(region)
        if (isinstance(have, dict) and have.get("windows") == spec["windows"]
                and time.time() - have.get("built", 0) < MAP_STATIC_REFRESH_S):
            return {tuple(c) for c in have.get("cells", [])}, max_dates
        if max_dates is None:
            status, text, _ = await self._get(f"{FIRMS_AVAIL_URL}/{self.key}/ALL")
            max_dates = hazards.sp_max_dates(text) if status == 200 else {}
        cells: set[tuple[int, int]] = set()
        calls = 0
        for src in hazards.STATIC_SOURCES:
            if not max_dates.get(src):
                continue
            for first in firemap.list_windows(max_dates[src], spec["windows"]):
                for area in spec["boxes"]:
                    status, text, _ = await self._get(f"{FIRMS_AREA_URL}/{self.key}/{src}/{area}/5/{first}",
                                                      timeout=_BIG_TIMEOUT)
                    got = await self.hass.async_add_executor_job(firemap.static_cells_csv, text) if status == 200 \
                        else None
                    if got is None:
                        _LOGGER.warning("FIRMS standard product for the %s list did not answer (%s); fires there "
                                        "are not drawn until it does", region, status)
                        return self._old_cells(have), max_dates
                    cells |= got
                    calls += 1
        if not calls:
            return self._old_cells(have), max_dates
        lists["regions"][region] = {"built": time.time(), "windows": spec["windows"], "max_dates": max_dates,
                                    "cells": sorted([list(c) for c in cells])}
        await self._store.async_save(lists)
        _LOGGER.info("Standing heat sources for %s: %d cells from %d standard-product calls", region, len(cells), calls)
        return cells, max_dates

    @staticmethod
    def _old_cells(have: Any) -> set | None:
        """A stale list still beats none."""
        return {tuple(c) for c in have["cells"]} if isinstance(have, dict) and have.get("cells") is not None else None

    async def _async_update_data(self) -> dict[str, Any]:
        cells: set[tuple[int, int]] = set()
        max_dates = None
        for region in self.regions:
            got, max_dates = await self._static_list(region, max_dates)
            if got is None:
                return self._keep_or_fail(f"no list of standing heat sources for {region} yet")
            cells |= got
        now = datetime.now(timezone.utc)
        points: list[list[Any]] = []
        for fregion in firemap.file_regions(self.regions):
            for product, prefix, sat in firemap.VIIRS_FILES:
                url = firemap.file_url(product, prefix, fregion)
                etag, held = self._cache.get(url, (None, None))
                status, text, headers = await self._get(url, headers={"If-None-Match": etag} if etag else None,
                                                        timeout=_BIG_TIMEOUT)
                if status == 304 and held is not None:
                    rows = held
                elif status == 200:
                    rows = await self.hass.async_add_executor_job(firemap.parse_fire_file, text, sat, now)
                    if rows is None:
                        return self._keep_or_fail(f"FIRMS's {prefix} {fregion} file was not CSV")
                    if headers.get("ETag"):
                        self._cache[url] = (headers["ETag"], rows)
                else:
                    return self._keep_or_fail(f"FIRMS's {prefix} {fregion} file answered {status}")
                # rows held across polls age: drop what has passed 24 h since
                points.extend(p for p in rows if (now - datetime.strptime(p[3], "%Y-%m-%d %H:%M").replace(
                    tzinfo=timezone.utc)).total_seconds() <= 24 * 3600)
        kept = await self.hass.async_add_executor_job(firemap.drop_standing, points, cells)
        return await self._publish(kept, firemap.FIRE_COLUMNS, {"source": "NASA FIRMS VIIRS NRT",
                                                                "regions": self.regions})


class AirSitesMap(_PointMap):
    LAYER = "air_quality"
    KEY_OPTION = CONF_AIRNOW_KEY

    @classmethod
    def wanted(cls, entry: ConfigEntry) -> bool:
        return super().wanted(entry) and bool(firemap.airnow_boxes(firemap.regions_of(
            entry.options.get(CONF_MAP_REGIONS))))

    async def _async_update_data(self) -> dict[str, Any]:
        hour = firemap.airnow_hour(datetime.now(timezone.utc))
        points: list[list[Any]] = []
        for area in firemap.airnow_boxes(self.regions):
            status, text, _ = await self._get(AIRNOW_DATA_URL, params={
                "startDate": hour, "endDate": hour, "parameters": "PM25", "BBOX": area, "dataType": "B",
                "format": "application/json", "verbose": "1", "monitorType": "0", "includerawconcentrations": "0",
                "API_KEY": self.key})
            if status != 200:
                return self._keep_or_fail(f"AirNow answered {status}")
            try:
                body = json.loads(text)
            except ValueError:
                body = None
            rows = firemap.parse_airnow_sites(body)
            if rows is None:
                return self._keep_or_fail("AirNow's answer was not a list")
            points.extend(rows)
        return await self._publish(firemap.dedupe(points), firemap.AQI_COLUMNS, {"source": "AirNow PM2.5",
                                                                                 "hour": hour})


class PointsView(HomeAssistantView):
    """`MAP_POINTS_PATH/<layer>/<digest>`: the current or previous file, gzipped. Signed in."""

    url = MAP_POINTS_PATH + "/{layer}/{digest}"
    name = f"api:{DOMAIN}:points"
    requires_auth = True

    async def get(self, request: web.Request, layer: str, digest: str) -> web.Response:
        files = _files(request.app[KEY_HASS])
        for key in (layer, f"{layer}:prev"):
            held = files.get(key)
            if held and held[0] == digest:
                return web.Response(body=held[1], content_type="application/json", headers={
                    "Content-Encoding": "gzip", "Cache-Control": "private, max-age=86400"})
        return web.Response(status=404)


class PointsSensor(CoordinatorEntity[_PointMap], SensorEntity):
    """One D19 publisher: the count as the state, where to fetch the points, and how to draw them."""

    _attr_has_entity_name = True
    _attr_state_class = SensorStateClass.MEASUREMENT
    _unrecorded_attributes = frozenset({"points_url", "point_styles", "updated", "regions", "reason"})

    # ! PERMANENT from first install: the unique_id and so the entity_id derive from these keys.
    _KINDS = {
        "fires": ("fire_detections", "Fire detections", "detections", "mdi:fire", firemap.FIRE_STYLE,
                  firemap.FIRE_ATTRIBUTION, 1),
        "air_quality": ("air_quality_sites", "Air quality sites", "sites", "mdi:air-filter", firemap.AQI_STYLES,
                        firemap.AQI_ATTRIBUTION, 0),
    }

    def __init__(self, coordinator: _PointMap, entry: ConfigEntry) -> None:
        super().__init__(coordinator)
        key, name, unit, icon, styles, attribution, order = self._KINDS[coordinator.LAYER]
        self._styles, self._order = styles, order
        self._attr_unique_id = f"{entry.entry_id}_{key}"
        self._attr_name = name
        self._attr_native_unit_of_measurement = unit
        self._attr_icon = icon
        self._attr_attribution = attribution
        self._attr_device_info = DeviceInfo(identifiers={(DOMAIN, entry.entry_id)}, name="Live Track Weather",
                                            model="NWS active alerts", entry_type=DeviceEntryType.SERVICE)

    @property
    def native_value(self) -> int | None:
        return (self.coordinator.data or {}).get("count")

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        d = self.coordinator.data or {}
        return {"points_url": d.get("url"), "point_styles": self._styles, "point_order": self._order,
                "updated": d.get("updated"), "regions": self.coordinator.regions, "reason": self.coordinator.reason}
