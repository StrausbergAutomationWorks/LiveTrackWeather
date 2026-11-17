"""Watch places: home, and any watched person, device tracker or zone (Weather SSOT items 334 and 349).

For each place: is it inside an alert (item 334, binary_sensor), and its forecast (item 349, weather). The decisions
are in places.py and forecast.py; this holds the places, their locations and what NWS says about them, fetches the
forecasts, and tells each place's entities when to redraw.

Alerts: read from the alerts and MET Norway coordinators the map already polls; no alert request is added.

The place's own lookup: NWS /points/{lat},{lon}, asked once for a place's location and kept (in .storage,
ZONES_STORE_KEY), asked again only for a point more than ZONES_REUSE_M from any point already asked, at most once per
alerts poll per place, and after ZONES_KEEP_S. One answer serves both items: its zone links are item 334's keys, its
grid item 349's forecast (MEASURED 2026-11-17, 20_Research/REPORT_349_measure_20261117.md). It replaced
/zones?point= (dd39604, 9e483c7) on 2026-11-17.

Forecasts: NWS's gridpoint daily and hourly for a place on US land (a grid with a county), asked with ?units=si and
If-Modified-Since, refreshed at the answer's own max-age (between FORECAST_NWS_MIN_S and FORECAST_NWS_MAX_S);
MET Norway's Locationforecast for every other place, through MetClient (MET's terms: User-Agent, 4 decimals,
If-Modified-Since, the shared back-off), every MET_POINT_POLL_S plus a jitter. A place that moves to a new grid
cell, or more than ZONES_REUSE_M for MET, is asked again, at most once per FORECAST_MOVE_GAP_S.

! Each place's location is SENT TO NWS (api.weather.gov) to learn its zones and grid, rounded to 4 decimals
(about 11 m), and, for a place outside NWS's land forecasts, to MET Norway (api.met.no) for its forecast, also
rounded to 4 decimals. The README's "Data use" says so.
"""

from __future__ import annotations

import json
import logging
import random
import time
from collections.abc import Callable
from dataclasses import dataclass
from datetime import timedelta
from typing import Any

import aiohttp

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_LATITUDE, ATTR_LONGITUDE, STATE_HOME
from homeassistant.core import CALLBACK_TYPE, Event, EventStateChangedData, HomeAssistant, callback
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.event import (async_call_later, async_track_state_change_event,
                                         async_track_time_interval)
from homeassistant.helpers.storage import Store

from . import forecast, places
from .const import (CONF_ALERT_THRESHOLD, CONF_SCAN_INTERVAL, CONF_WATCH_ENTITIES, CONF_WATCH_HOME,
                    DEFAULT_SCAN_INTERVAL, DEFAULT_WATCH_HOME, FORECAST_MOVE_GAP_S, FORECAST_NWS_MAX_S,
                    FORECAST_NWS_MIN_S, FORECAST_TICK_S, MET_ALERTS_CAP, MET_JITTER_S, MET_POINT_POLL_S,
                    MET_POINT_URL, POINTS_URL, REQUEST_TIMEOUT, USER_AGENT, ZONES_CACHE_MAX, ZONES_KEEP_S,
                    ZONES_REUSE_M, ZONES_STORE_KEY)
from .met_coordinator import met_client

_LOGGER = logging.getLogger(__name__)

HOME = "home"


@dataclass(frozen=True)
class Place:
    key: str               # "home", or the watched entity's id
    entity_id: str | None  # None for Home Assistant's home location


def places_from(opts: dict[str, Any]) -> list[Place]:
    out = []
    if opts.get(CONF_WATCH_HOME, DEFAULT_WATCH_HOME):
        out.append(Place(HOME, None))
    for eid in opts.get(CONF_WATCH_ENTITIES) or []:
        if isinstance(eid, str) and eid and eid != HOME:
            out.append(Place(eid, eid))
    return out


def _max_age(headers: Any) -> int | None:
    for part in (headers.get("Cache-Control") or "").split(","):
        k, _, v = part.strip().partition("=")
        if k == "max-age" and v.isdigit():
            return int(v)
    return None


class PlaceWatch:
    def __init__(self, hass: HomeAssistant, entry: ConfigEntry, alerts, met) -> None:
        opts = {**entry.data, **entry.options}
        self.hass = hass
        self.entry = entry
        self.places = places_from(opts)
        self.threshold = opts.get(CONF_ALERT_THRESHOLD) or places.DEFAULT_THRESHOLD
        if self.threshold not in places.THRESHOLDS:
            self.threshold = places.DEFAULT_THRESHOLD
        self._gap_s = int(opts.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL))
        self._alerts = alerts
        self._met = met
        self._session = async_get_clientsession(hass)
        self._store: Store[dict[str, Any]] = Store(hass, 1, ZONES_STORE_KEY)
        self._cache: list[dict[str, Any]] = []
        self._asked: dict[str, float] = {}
        self._inflight: set[str] = set()
        # place key -> (point info {"keys", "grid"}, lat, lon) of the last answer that place used
        self._point: dict[str, tuple[dict[str, Any], float, float]] = {}
        self._results: dict[str, dict[str, Any]] = {}
        self._listeners: list[CALLBACK_TYPE] = []
        self._timers: dict[str, CALLBACK_TYPE] = {}
        # forecasts, place key -> state (see _forecast_check)
        self._fc: dict[str, dict[str, Any]] = {}
        self._fc_listeners: list[Callable[[str], None]] = []
        self._nws_lm: dict[str, tuple[str, Any]] = {}   # url -> (Last-Modified, parsed doc)
        self._met_jitter = random.randint(0, MET_JITTER_S)

    async def async_start(self) -> None:
        if not self.places:
            return
        self.entry.async_on_unload(self._cancel_timers)
        stored = await self._store.async_load()
        if isinstance(stored, dict) and isinstance(stored.get("points"), list):
            self._cache = stored["points"]
        self.entry.async_on_unload(self._alerts.async_add_listener(self._recompute))
        if self._met is not None:
            self.entry.async_on_unload(self._met.async_add_listener(self._recompute))
        ids = [p.entity_id for p in self.places if p.entity_id]
        if ids:
            self.entry.async_on_unload(async_track_state_change_event(self.hass, ids, self._on_state))
        self.entry.async_on_unload(async_track_time_interval(
            self.hass, self._on_tick, timedelta(seconds=FORECAST_TICK_S)))
        self._recompute()

    # ------------------------------------------------------------------ entities

    @callback
    def async_add_listener(self, cb: CALLBACK_TYPE) -> CALLBACK_TYPE:
        self._listeners.append(cb)

        def remove() -> None:
            if cb in self._listeners:
                self._listeners.remove(cb)
        return remove

    @callback
    def async_add_forecast_listener(self, cb: Callable[[str], None]) -> CALLBACK_TYPE:
        self._fc_listeners.append(cb)

        def remove() -> None:
            if cb in self._fc_listeners:
                self._fc_listeners.remove(cb)
        return remove

    def result(self, key: str) -> dict[str, Any]:
        return self._results.get(key) or {}

    def forecast(self, key: str) -> dict[str, Any]:
        """{"data": forecast.build(...) or None, "grid": "LOT/76,73" or None, "reason": str or None}."""
        fc = self._fc.get(key) or {}
        return {"data": fc.get("data"), "grid": fc.get("grid_id"), "reason": fc.get("reason")}

    # ------------------------------------------------------------------ locations

    def location(self, place: Place) -> tuple[float, float] | None:
        cfg = self.hass.config
        if place.entity_id is None:
            return (cfg.latitude, cfg.longitude)
        st = self.hass.states.get(place.entity_id)
        if st is None:
            return None
        lat, lon = st.attributes.get(ATTR_LATITUDE), st.attributes.get(ATTR_LONGITUDE)
        if isinstance(lat, (int, float)) and isinstance(lon, (int, float)):
            return (float(lat), float(lon))
        # A tracker with no coordinates that says it is home (a router tracker, say) is at home.
        if st.state == STATE_HOME:
            return (cfg.latitude, cfg.longitude)
        return None

    @callback
    def _on_state(self, event: Event[EventStateChangedData]) -> None:
        self._recompute()

    @callback
    def _on_tick(self, _now: Any) -> None:
        self._recompute()

    # ------------------------------------------------------------------ the answer

    def _records(self) -> list[dict[str, Any]] | None:
        if not self._alerts.last_update_success or not self._alerts.data:
            return None
        recs = list(self._alerts.data.get("records") or [])
        if self._met is not None and self._met.data:
            for cap in self._met.data.get("caps") or []:
                r = places.met_record(cap, MET_ALERTS_CAP)
                if r:
                    recs.append(r)
        return recs

    @callback
    def _recompute(self) -> None:
        records = self._records()
        now = time.time()
        for p in self.places:
            loc = self.location(p)
            if loc is None:
                self._results[p.key] = {"on": None, "alerts": [], "highest": None, "reason": "no location"}
                self._fc.setdefault(p.key, {})["reason"] = "no location"
                continue
            lat, lon = loc
            info = places.cached_point(self._cache, lat, lon, now, ZONES_REUSE_M, ZONES_KEEP_S)
            if info is not None:
                self._point[p.key] = (info, lat, lon)
            else:
                self._maybe_ask(p, lat, lon)
                # Until NWS answers for the new spot, the place keeps its last answer.
                held = self._point.get(p.key)
                info = held[0] if held else None
            keys = info["keys"] if info is not None else None
            self._forecast_check(p, info, lat, lon)
            if records is None:
                self._results[p.key] = {"on": None, "alerts": [], "highest": None, "reason": "alerts unavailable",
                                        "zones": sorted(keys) if keys is not None else None}
                continue
            s = places.summary(places.alerts_at(records, keys, lat, lon), self.threshold)
            if keys is None and not s["on"]:
                # Zone-based alerts could not be tested yet: unknown, not "no alert".
                s["on"] = None
                s["reason"] = "zones not known yet"
            s["zones"] = sorted(keys) if keys is not None else None
            self._results[p.key] = s
        for cb in list(self._listeners):
            cb()

    def _maybe_ask(self, place: Place, lat: float, lon: float) -> None:
        if place.key in self._inflight:
            return
        mono = time.monotonic()
        wait = self._gap_s - (mono - self._asked.get(place.key, -1e18))
        if wait > 0:
            # Look again the moment asking is allowed, not at whatever event comes after it: a moved tracker
            # then waits at most one poll interval (measured 174 s on 2026-11-17, when a reload had lined the
            # alerts poll up with the gap by chance).
            if place.key not in self._timers:
                self._timers[place.key] = async_call_later(self.hass, wait + 1, self._timer_fired(place.key))
            return
        self._asked[place.key] = mono
        self._inflight.add(place.key)
        self.entry.async_create_background_task(
            self.hass, self._ask(place, lat, lon), f"live_track_weather point for {place.key}")

    def _timer_fired(self, key: str) -> Callable[[Any], None]:
        @callback
        def fired(_now: Any) -> None:
            self._timers.pop(key, None)
            self._recompute()
        return fired

    @callback
    def _cancel_timers(self) -> None:
        for unsub in self._timers.values():
            unsub()
        self._timers.clear()

    async def _ask(self, place: Place, lat: float, lon: float) -> None:
        try:
            info = await self._fetch_point(lat, lon)
        finally:
            self._inflight.discard(place.key)
        if info is None:
            return
        self._cache = places.remember(self._cache, lat, lon, info["keys"], info["grid"], time.time(),
                                      ZONES_REUSE_M, ZONES_CACHE_MAX)
        self._store.async_delay_save(lambda: {"points": self._cache}, 10)
        self._point[place.key] = (info, lat, lon)
        self._recompute()

    async def _fetch_point(self, lat: float, lon: float) -> dict[str, Any] | None:
        """What NWS says about the point; {"keys": set(), "grid": None} where NWS has nothing (404 outside its area,
        MEASURED 2026-11-17 at Toronto and Oslo; 400 for a point it will not take); None when it could not be asked."""
        try:
            async with self._session.get(
                f"{POINTS_URL}/{lat:.4f},{lon:.4f}",
                headers={"User-Agent": USER_AGENT, "Accept": "application/geo+json"},
                timeout=aiohttp.ClientTimeout(total=REQUEST_TIMEOUT),
            ) as resp:
                if resp.status in (400, 404):
                    return {"keys": set(), "grid": None}
                if resp.status != 200:
                    _LOGGER.debug("NWS points answered HTTP %s", resp.status)
                    return None
                doc = await resp.json(content_type=None)
        except (aiohttp.ClientError, TimeoutError, ValueError) as err:
            _LOGGER.debug("NWS points lookup failed: %s", type(err).__name__)
            return None
        return places.point_info(doc)

    # ------------------------------------------------------------------ forecasts

    @callback
    def _forecast_check(self, place: Place, info: dict[str, Any] | None, lat: float, lon: float) -> None:
        """Decide the place's forecast source and spot; fetch when due. Waits for the place's first NWS answer,
        which says whether it is on US land."""
        fc = self._fc.setdefault(place.key, {})
        if info is None:
            fc.setdefault("reason", "point not known yet")
            return
        grid = info.get("grid")
        if grid and fc.get("nws_refused") != grid["id"]:
            source, spot = forecast.NWS, f"nws {grid['id']}"
        else:
            source = forecast.MET
            same = (fc.get("source") == forecast.MET and fc.get("lat") is not None
                    and places.distance_m(lat, lon, fc["lat"], fc["lon"]) <= ZONES_REUSE_M)
            spot = fc["spot"] if same else f"met {lat:.4f},{lon:.4f}"
        mono = time.monotonic()
        if spot != fc.get("spot"):
            if (fc.get("data") is not None and fc.get("spot") is not None
                    and mono - fc.get("fetched", -1e18) < FORECAST_MOVE_GAP_S):
                return  # moved, but asked about another spot too recently: keep the held forecast for now
            fc.update(source=source, spot=spot, lat=lat, lon=lon, grid=grid if source == forecast.NWS else None,
                      grid_id=grid["id"] if source == forecast.NWS else None, due=0.0)
        if fc.get("inflight") or mono < fc.get("due", 0.0):
            return
        fc["inflight"] = True
        self.entry.async_create_background_task(
            self.hass, self._fetch_forecast(place.key), f"live_track_weather forecast for {place.key}")

    async def _fetch_forecast(self, key: str) -> None:
        fc = self._fc[key]
        try:
            if fc["source"] == forecast.NWS:
                await self._fetch_nws(key, fc)
            else:
                await self._fetch_met(key, fc)
        finally:
            fc["inflight"] = False
            fc["fetched"] = time.monotonic()
        for cb in list(self._fc_listeners):
            cb(key)
        if fc.get("due") == 0.0:
            self._recompute()   # NWS refused the grid: ask MET now, not at the next tick

    async def _nws_get(self, url: str) -> tuple[int, Any, int | None]:
        """(status, parsed doc or None, max-age). A 304 returns the doc held for the URL."""
        headers = {"User-Agent": USER_AGENT, "Accept": "application/geo+json"}
        held = self._nws_lm.get(url)
        if held:
            headers["If-Modified-Since"] = held[0]
        try:
            async with self._session.get(url, params={"units": "si"}, headers=headers,
                                         timeout=aiohttp.ClientTimeout(total=REQUEST_TIMEOUT)) as resp:
                age = _max_age(resp.headers)
                if resp.status == 304 and held:
                    return 200, held[1], age
                if resp.status != 200:
                    return resp.status, None, age
                raw = await resp.read()
                lm = resp.headers.get("Last-Modified")
        except (aiohttp.ClientError, TimeoutError) as err:
            _LOGGER.debug("NWS forecast failed: %s", type(err).__name__)
            return 0, None, None
        try:
            doc = await self.hass.async_add_executor_job(json.loads, raw)
        except ValueError:
            return 0, None, None
        if lm:
            self._nws_lm[url] = (lm, doc)
        return 200, doc, age

    async def _fetch_nws(self, key: str, fc: dict[str, Any]) -> None:
        grid = fc["grid"]
        sd, daily, age_d = await self._nws_get(grid["forecast"])
        sh, hourly, age_h = await self._nws_get(grid["hourly"])
        if sd == 404 or sh == 404:
            # NWS will not forecast this grid (a marine grid answers 404, MEASURED 2026-11-17): MET instead.
            fc["nws_refused"] = grid["id"]
            fc["due"] = 0.0
            fc["reason"] = "NWS has no forecast here; MET Norway's instead"
            return
        if daily is None or hourly is None:
            fc["due"] = time.monotonic() + FORECAST_NWS_MIN_S
            if fc.get("data") is None:
                # Nothing held yet: MET's forecast this time, NWS again at the next try.
                await self._fetch_met(key, fc, fallback=True)
            return
        ages = [a for a in (age_d, age_h) if a is not None]
        wait = min(ages) if ages else FORECAST_NWS_MIN_S
        fc["due"] = time.monotonic() + max(FORECAST_NWS_MIN_S, min(FORECAST_NWS_MAX_S, wait))
        fc["data"] = await self.hass.async_add_executor_job(forecast.build, forecast.NWS, daily, hourly, fc["lon"])
        fc["reason"] = None

    async def _fetch_met(self, key: str, fc: dict[str, Any], fallback: bool = False) -> None:
        client = met_client(self.hass)
        ckey = f"place {key}"
        if fc.get("met_spot") != fc["spot"]:
            client.forget(ckey)   # a new spot: no If-Modified-Since from the old one
            fc["met_spot"] = fc["spot"]
        raw = await client.get(ckey, MET_POINT_URL, {"lat": f"{fc['lat']:.4f}", "lon": f"{fc['lon']:.4f}"})
        if not fallback:
            fc["due"] = time.monotonic() + MET_POINT_POLL_S + self._met_jitter
        if not raw:
            if fc.get("data") is None:
                fc["reason"] = "MET Norway did not answer"
            return
        try:
            doc = await self.hass.async_add_executor_job(json.loads, raw)
        except ValueError:
            return
        fc["data"] = await self.hass.async_add_executor_job(forecast.build, forecast.MET, doc, doc, fc["lon"])
        fc["reason"] = None if not fallback else "NWS did not answer; MET Norway's forecast meanwhile"
