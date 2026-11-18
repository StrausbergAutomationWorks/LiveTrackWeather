"""Watch places: home, and any watched person, device tracker or zone (Weather SSOT items 334, 349 and 350).

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

Observations (item 350): the stations list /points names for the place (cached STATIONS_KEEP_S), nearest to the
place first (airports only by option), and up to observe.MAX_STATIONS stations' latest reports, asked with
?require_qc=true and If-Modified-Since every OBS_POLL_S; the next station only while wind or temperature is still
missing. A moving place is not asked more often; its location at the next poll is used. No location is sent: only
station ids. Outside NWS's area, with the user's Frost client ID (item 311; Lee 2026-11-18), MET Norway's Frost first:
the place's 10 nearest Frost stations (asked again after a move of more than ZONES_REUSE_M), and, when the nearest is
in Norway or Svalbard (frost.in_area), their latest readings every FROST_POLL_S, picked as item 350 picks; what Frost
leaves missing, and every place outside Norway and Svalbard, from GeoNames with the user's username.

! Each place's location is SENT TO NWS (api.weather.gov) to learn its zones and grid, rounded to 4 decimals
(about 11 m), and, for a place outside NWS's land forecasts, to MET Norway (api.met.no) for its forecast, also
rounded to 4 decimals; and (item 352 step 4) to USGS's elevation service (epqs.nationalmap.gov), rounded to 4
decimals, at start-up and after each move of more than 500 m, at most every 10 minutes. With each such elevation
check (item 352 step 4b), where USGS has nothing: to NRCan (inside a box around Canada) and Kartverket (inside a box
around Norway), 4 decimals; a z15 terrain tile's address to AWS (about 1 km); and, for the water test and the depth,
to NOAA NCEI, 4 decimals. With the user's GeoNames username only: to GeoNames (4 decimals) for the sea's name or the
water test once per elevation check, and, where NWS has no station, for the nearest METAR every observation poll
(stretched so every place together stays within half GeoNames' daily credits). With the user's Frost client ID only:
to MET Norway's Frost (4 decimals) for the place's nearest stations, where NWS has no station, at the first poll and
after each move of more than ZONES_REUSE_M. The README's "Data use" says so.
"""

from __future__ import annotations

import json
import logging
import random
import time
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any

import aiohttp

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_LATITUDE, ATTR_LONGITUDE, STATE_HOME
from homeassistant.core import CALLBACK_TYPE, Event, EventStateChangedData, HomeAssistant, callback
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.event import (async_call_later, async_track_state_change_event,
                                         async_track_time_interval)
from homeassistant.helpers.storage import Store

from . import elevation, forecast, frost, geonames, hazards, observe, places, usgs
from .const import (AIRNOW_URL, CONF_AIRNOW_KEY, CONF_ALERT_THRESHOLD, CONF_FIRE_KM, CONF_FIRMS_KEY,
                    CONF_FROST_ID, CONF_GEONAMES_USER, FROST_POLL_S,
                    CONF_OBSERVE_AIRPORTS_ONLY, CONF_SCAN_INTERVAL, CONF_SMOKE_AQI, CONF_WATCH_ENTITIES,
                    CONF_WATCH_HOME, DEFAULT_OBSERVE_AIRPORTS_ONLY, DEFAULT_SCAN_INTERVAL, DEFAULT_WATCH_HOME,
                    FIRE_POLL_S, FIRMS_AREA_URL, FIRMS_AVAIL_URL, FORECAST_MOVE_GAP_S, FORECAST_NWS_MAX_S,
                    FORECAST_NWS_MIN_S, FORECAST_TICK_S, MET_ALERTS_CAP, MET_JITTER_S, MET_POINT_POLL_S,
                    MET_POINT_URL, OBS_LATEST_PARAMS, OBS_POLL_S, POINTS_URL, RECUR_REFRESH_S, REQUEST_TIMEOUT,
                    SMOKE_POLL_S, STATIONS_KEEP_S, USER_AGENT, ZONES_CACHE_MAX, ZONES_KEEP_S, ZONES_REUSE_M,
                    ZONES_STORE_KEY)
from .frost_coordinator import frost_client
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
        # observations (item 350), place key -> state (see _obs_check)
        self._airports_only = bool(opts.get(CONF_OBSERVE_AIRPORTS_ONLY, DEFAULT_OBSERVE_AIRPORTS_ONLY))
        self._obs: dict[str, dict[str, Any]] = {}
        self._obs_listeners: list[Callable[[str], None]] = []
        self._stations: dict[str, tuple[Any, float]] = {}   # stations list url -> (parsed doc, monotonic fetched)
        self._obs_lm: dict[str, tuple[str, Any]] = {}       # latest url -> (Last-Modified, parsed doc)
        # fire and smoke (item 351), only with the user's own keys; place key -> state (see _hazard_records)
        self._firms_key = (opts.get(CONF_FIRMS_KEY) or "").strip() or None
        self._airnow_key = (opts.get(CONF_AIRNOW_KEY) or "").strip() or None
        self._fire_km = int(opts.get(CONF_FIRE_KM, hazards.FIRE_KM_DEFAULT))
        self._smoke_aqi = int(opts.get(CONF_SMOKE_AQI, hazards.SMOKE_AQI_DEFAULT))
        self._hz: dict[str, dict[str, Any]] = {}
        self._sp_max: tuple[dict[str, str], float] | None = None   # standard products' last days, when asked
        # item 352: other coordinators whose data turn a place on (earthquakes, volcanoes): (coordinator, records fn)
        self._sources: list[tuple[Any, Callable[[dict[str, Any], float, float], list[dict[str, Any]]]]] = []
        # item 352 step 4: elevation at each place, place key -> state (see _elev_check)
        self._elev: dict[str, dict[str, Any]] = {}
        self._elev_listeners: list[Callable[[str], None]] = []
        self._tiles: dict[tuple[int, int], bytes] = {}      # the last few terrain tiles (step 4b)
        # GeoNames (step 4b), only with the user's own username; nothing is asked before the monotonic time below
        self._gn_user = (opts.get(CONF_GEONAMES_USER) or "").strip() or None
        self._gn_until = 0.0
        # MET Norway's Frost (item 311), only with the user's own client ID
        self._frost_id = (opts.get(CONF_FROST_ID) or "").strip() or None

    def add_source(self, coordinator: Any, fn: Callable[[dict[str, Any], float, float], list[dict[str, Any]]]) -> None:
        """A coordinator whose data turn a place on: fn(data, lat, lon) gives the place's records ("always" ones).
        Call before async_start."""
        self._sources.append((coordinator, fn))

    def _source_records(self, lat: float, lon: float) -> list[dict[str, Any]]:
        out: list[dict[str, Any]] = []
        for coordinator, fn in self._sources:
            if coordinator.data:
                try:
                    out.extend(fn(coordinator.data, lat, lon))
                except Exception:  # noqa: BLE001 - one bad source must not stop the places
                    _LOGGER.exception("A hazard source failed for a place")
        return out

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
        for coordinator, _fn in self._sources:
            self.entry.async_on_unload(coordinator.async_add_listener(self._recompute))
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

    @callback
    def async_add_obs_listener(self, cb: Callable[[str], None]) -> CALLBACK_TYPE:
        self._obs_listeners.append(cb)

        def remove() -> None:
            if cb in self._obs_listeners:
                self._obs_listeners.remove(cb)
        return remove

    def observation(self, key: str) -> dict[str, Any]:
        """{"pick": observe.pick(...) or None, "reason": str or None} for the place."""
        ob = self._obs.get(key) or {}
        return {"pick": ob.get("pick"), "reason": ob.get("reason")}

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
                self._obs_set(p.key, pick=None, reason="no location")
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
            self._obs_check(p, info, lat, lon)
            self._elev_check(p, lat, lon)
            hz_recs = self._hazard_records(p, lat, lon) + self._source_records(lat, lon)
            if records is None:
                if hz_recs:
                    s = places.summary(hz_recs, self.threshold)
                    s.update(reason="alerts unavailable", zones=sorted(keys) if keys is not None else None)
                    self._results[p.key] = s
                    continue
                self._results[p.key] = {"on": None, "alerts": [], "highest": None, "reason": "alerts unavailable",
                                        "zones": sorted(keys) if keys is not None else None}
                continue
            s = places.summary(places.alerts_at(records, keys, lat, lon) + hz_recs, self.threshold)
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
                                      ZONES_REUSE_M, ZONES_CACHE_MAX, stations=info.get("stations"))
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
                    return {"keys": set(), "grid": None, "stations": None}
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
                # Moved, but asked about another spot too recently: keep the held forecast, and look again the
                # moment the gap ends. Without the timer a tracker that stops reporting after a move waited for
                # the next poll or tick as well (MEASURED live 2026-11-17, item 349: 691 s after the move).
                tkey = f"forecast {place.key}"
                if tkey not in self._timers:
                    self._timers[tkey] = async_call_later(
                        self.hass, FORECAST_MOVE_GAP_S - (mono - fc["fetched"]) + 1, self._timer_fired(tkey))
                return
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

    # ------------------------------------------------------------------ observations (item 350)

    @callback
    def _obs_set(self, key: str, **changes: Any) -> None:
        """Change a place's observation state, and tell its sensors when what they show changed."""
        ob = self._obs.setdefault(key, {})
        shown = (ob.get("pick"), ob.get("reason"))
        ob.update(changes)
        if (ob.get("pick"), ob.get("reason")) != shown:
            for cb in list(self._obs_listeners):
                cb(key)

    @callback
    def _obs_check(self, place: Place, info: dict[str, Any] | None, lat: float, lon: float) -> None:
        """Fetch the place's observations when due (every OBS_POLL_S). A moving place is not asked more often: its
        current location is used at the next poll."""
        ob = self._obs.setdefault(place.key, {})
        ob["lat"], ob["lon"] = lat, lon
        if info is None:
            if ob.get("pick") is None:
                self._obs_set(place.key, reason="point not known yet")
            return
        url = info.get("stations")
        if not url:
            # outside NWS's area: /points answered 404, and there is no station to ask
            if ob.get("source") != "geonames":
                # left NWS's area (or first seen outside it): NWS's station no longer stands for the place, and
                # Frost or GeoNames, with a client ID or a username, is asked at once
                ob.update(url=None, source="geonames", gn_due=0.0, fr_due=0.0)
                self._obs_set(place.key, pick=None)
            if self._frost_id:
                spot = ob.get("fr_spot")
                moved = spot is None or places.distance_m(spot[0], spot[1], lat, lon) > ZONES_REUSE_M
                if moved or ob.get("fr_area"):
                    # Frost decides, by its nearest station, whether the place is in Norway or Svalbard
                    self._frost_obs_check(place.key, ob)
                    return
            if self._gn_user:
                self._gn_obs_check(place.key, ob)
                return
            self._obs_set(place.key, pick=None, reason="no NWS stations here")
            return
        if ob.get("source") == "geonames":
            ob["source"] = "nws"
            self._obs_set(place.key, pick=None, reason=None)   # GeoNames' station no longer stands for the place
        mono = time.monotonic()
        if url != ob.get("url"):
            ob["url"] = url
            if ob.get("pick") is None:
                ob["due"] = 0.0   # a place's first stations list: ask now; a move waits for the next poll
        if ob.get("inflight") or mono < ob.get("due", 0.0):
            return
        ob["inflight"] = True
        self.entry.async_create_background_task(
            self.hass, self._fetch_obs(place.key), f"live_track_weather observations for {place.key}")

    async def _fetch_obs(self, key: str) -> None:
        ob = self._obs[key]
        try:
            ob["due"] = time.monotonic() + OBS_POLL_S
            doc = await self._stations_list(ob["url"])
            if doc is None:
                ob["reason"] = "NWS's station list did not answer"
                return
            sts = observe.stations(doc, ob["lat"], ob["lon"], self._airports_only)[:observe.MAX_STATIONS]
            if not sts:
                ob.update(pick=None, reason="no airport station listed" if self._airports_only else "no station listed")
                return
            reports = []
            for st in sts:
                reports.append((st, await self._latest(st["id"])))
                if observe.complete(observe.pick(reports, datetime.now(timezone.utc))):
                    break   # the next station is asked only while wind or temperature is still missing
            pick = observe.pick(reports, datetime.now(timezone.utc))
            missing = [k for k in ("wind", "temperature") if pick[k] is None]
            n = f"{len(sts)} station{'s' if len(sts) > 1 else ''}"
            ob.update(pick=pick, asked=[s["id"] for s, _ in reports],
                      reason=f"no fresh {' or '.join(missing)} from the nearest {n}" if missing else None)
        finally:
            ob["inflight"] = False
            # the age moves on even when nothing new arrived: the sensors redraw after every poll
            for cb in list(self._obs_listeners):
                cb(key)

    async def _stations_list(self, url: str) -> Any:
        held = self._stations.get(url)
        if held and time.monotonic() - held[1] < STATIONS_KEEP_S:
            return held[0]
        try:
            async with self._session.get(url, headers={"User-Agent": USER_AGENT, "Accept": "application/geo+json"},
                                         timeout=aiohttp.ClientTimeout(total=REQUEST_TIMEOUT)) as resp:
                if resp.status != 200:
                    _LOGGER.debug("NWS stations list answered HTTP %s", resp.status)
                    return held[0] if held else None
                raw = await resp.read()
        except (aiohttp.ClientError, TimeoutError) as err:
            _LOGGER.debug("NWS stations list failed: %s", type(err).__name__)
            return held[0] if held else None
        try:
            doc = await self.hass.async_add_executor_job(json.loads, raw)
        except ValueError:
            return held[0] if held else None
        self._stations[url] = (doc, time.monotonic())
        return doc

    async def _latest(self, sid: str) -> dict[str, Any] | None:
        """A station's latest report with ?require_qc=true, parsed; None for a 404, a failure or no observation."""
        url = f"https://api.weather.gov/stations/{sid}/observations/latest"
        headers = {"User-Agent": USER_AGENT, "Accept": "application/geo+json"}
        held = self._obs_lm.get(url)
        if held:
            headers["If-Modified-Since"] = held[0]
        try:
            async with self._session.get(url, params=OBS_LATEST_PARAMS, headers=headers,
                                         timeout=aiohttp.ClientTimeout(total=REQUEST_TIMEOUT)) as resp:
                if resp.status == 304 and held:
                    return observe.parse(held[1])
                if resp.status != 200:
                    if resp.status == 404:
                        self._obs_lm.pop(url, None)
                    return None
                raw = await resp.read()
                lm = resp.headers.get("Last-Modified")
        except (aiohttp.ClientError, TimeoutError) as err:
            _LOGGER.debug("NWS observation failed: %s", type(err).__name__)
            return observe.parse(held[1]) if held else None
        try:
            doc = json.loads(raw)
        except ValueError:
            return None
        if lm:
            self._obs_lm[url] = (lm, doc)
        return observe.parse(doc)

    # ------------------------------------------------------------------ GeoNames (item 352 step 4b)

    async def _gn_get(self, url: str, lat: float, lon: float) -> tuple[int, Any]:
        """(HTTP status, parsed JSON or None) from GeoNames with the user's username; (0, None) while GeoNames is
        being left alone after an error. Any error status starts that rest (geonames.backoff_s)."""
        if not self._gn_user or time.monotonic() < self._gn_until:
            return 0, None
        try:
            async with self._session.get(url, params=geonames.params(self._gn_user, lat, lon),
                                         headers={"User-Agent": USER_AGENT},
                                         timeout=aiohttp.ClientTimeout(total=REQUEST_TIMEOUT)) as resp:
                status = resp.status
                raw = await resp.read()
        except (aiohttp.ClientError, TimeoutError) as err:
            _LOGGER.debug("GeoNames failed: %s", type(err).__name__)
            status, raw = 0, b""
        try:
            doc = json.loads(raw) if raw else None
        except ValueError:
            doc = None
        rest = geonames.backoff_s(status, doc) if status else geonames.OTHER_BACKOFF_S
        if rest:
            st = geonames.status(doc)
            _LOGGER.debug("GeoNames answered HTTP %s, status %s; resting %s s", status, st[0] if st else None, rest)
            self._gn_until = time.monotonic() + rest
        return status, doc

    @callback
    def _gn_obs_check(self, key: str, ob: dict[str, Any]) -> None:
        """A place where NWS has no station: GeoNames' nearest METAR, every geonames.poll_s."""
        if ob.get("gn_inflight") or time.monotonic() < ob.get("gn_due", 0.0):
            return
        ob["gn_inflight"] = True
        self.entry.async_create_background_task(
            self.hass, self._fetch_gn_obs(key), f"live_track_weather GeoNames weather for {key}")

    async def _fetch_gn_obs(self, key: str) -> None:
        ob = self._obs[key]
        try:
            ob["gn_due"] = time.monotonic() + geonames.poll_s(len(self.places), OBS_POLL_S)
            status, doc = await self._gn_get(geonames.WEATHER_URL, ob["lat"], ob["lon"])
            if not geonames.answered(status, doc):
                ob["reason"] = "no NWS stations here, and GeoNames did not answer"
                return
            got = geonames.parse_weather(doc, ob["lat"], ob["lon"])
            if got is None:
                ob.update(pick=None, reason="no NWS stations here, and no METAR station near (GeoNames)")
                return
            pick = observe.pick([got], datetime.now(timezone.utc))
            missing = [k for k in ("wind", "temperature") if pick[k] is None]
            ob.update(pick=pick, asked=[got[0]["id"]],
                      reason=f"no fresh {' or '.join(missing)} from GeoNames' nearest METAR station" if missing
                      else None)
        finally:
            ob["gn_inflight"] = False
            for cb in list(self._obs_listeners):
                cb(key)

    # ------------------------------------------------------------------ MET Norway's Frost (item 311)

    @callback
    def _frost_obs_check(self, key: str, ob: dict[str, Any]) -> None:
        """A place where NWS has no station, with a Frost client ID: Frost every FROST_POLL_S (a move waits for it)."""
        if ob.get("fr_inflight") or time.monotonic() < ob.get("fr_due", 0.0):
            return
        ob["fr_inflight"] = True
        self.entry.async_create_background_task(
            self.hass, self._fetch_frost_obs(key), f"live_track_weather Frost weather for {key}")

    async def _fetch_frost_obs(self, key: str) -> None:
        """The place's nearest Frost stations (asked again after a move); in Norway or Svalbard, their latest readings,
        picked as item 350 picks; what Frost leaves missing, or the whole place elsewhere, from GeoNames."""
        ob = self._obs[key]
        client = frost_client(self.hass, self._frost_id)
        lat, lon = ob["lat"], ob["lon"]
        try:
            ob["fr_due"] = time.monotonic() + FROST_POLL_S
            spot = ob.get("fr_spot")
            if spot is None or places.distance_m(spot[0], spot[1], lat, lon) > ZONES_REUSE_M:
                status, doc = await client.get(frost.SOURCES_URL, frost.nearest_params(lat, lon))
                near = frost.parse_sources(doc) if status == 200 else []
                if not near:
                    # Frost did not answer: GeoNames meanwhile; the nearest stations are asked again at the next poll
                    ob["fr_area"] = None
                    await self._frost_fallback(key, ob, "MET Norway's Frost did not answer")
                    return
                ob.update(fr_spot=(lat, lon), fr_near=near, fr_area=frost.in_area(near))
            if not ob.get("fr_area"):
                await self._frost_fallback(key, ob, None)
                return
            near = ob["fr_near"]
            status, doc = await client.get(frost.OBS_URL, frost.latest_params([s["id"] for s in near],
                                                                               frost.PLACE_ELEMENTS))
            now = datetime.now(timezone.utc)
            if status not in (200, 412):
                await self._frost_fallback(key, ob, "MET Norway's Frost did not answer")
                return
            latest = frost.parse_latest(doc, now) if status == 200 else {}
            reports = frost.place_reports(near, latest, lat, lon, now)
            pick = observe.pick(reports, now)
            missing = [k for k in ("wind", "temperature") if pick[k] is None]
            reason = None
            if missing:
                reason = f"no fresh {' or '.join(missing)} from MET Norway's {len(near)} nearest stations"
                got = await self._gn_report(ob)
                if got is not None:
                    filled = observe.pick([got], now)
                    for k in missing:
                        pick[k] = filled[k]
                    still = [k for k in ("wind", "temperature") if pick[k] is None]
                    reason = (reason + "; " + ("GeoNames' nearest METAR station filled in" if not still else
                                               f"no fresh {' or '.join(still)} from GeoNames either"))
            ob.update(pick=pick, asked=[s["id"] for s in near], reason=reason)
        finally:
            ob["fr_inflight"] = False
            for cb in list(self._obs_listeners):
                cb(key)

    async def _frost_fallback(self, key: str, ob: dict[str, Any], why: str | None) -> None:
        """Outside Norway and Svalbard, or Frost failing: GeoNames as without a client ID, else no measured weather."""
        if self._gn_user:
            if time.monotonic() >= ob.get("gn_due", 0.0) and not ob.get("gn_inflight"):
                ob["gn_inflight"] = True
                await self._fetch_gn_obs(key)
            return
        if why:
            if ob.get("pick") is None:
                ob["reason"] = why
            return
        ob.update(pick=None, reason="no NWS stations here")

    async def _gn_report(self, ob: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]] | None:
        """GeoNames' nearest METAR for a Frost place's missing values: asked when due (geonames.poll_s), else the last
        answer; None without a username or a station."""
        if not self._gn_user:
            return None
        if time.monotonic() >= ob.get("gn_due", 0.0):
            ob["gn_due"] = time.monotonic() + geonames.poll_s(len(self.places), OBS_POLL_S)
            status, doc = await self._gn_get(geonames.WEATHER_URL, ob["lat"], ob["lon"])
            if geonames.answered(status, doc):
                ob["gn_got"] = geonames.parse_weather(doc, ob["lat"], ob["lon"])
        return ob.get("gn_got")

    # ------------------------------------------------------------------ fire and smoke (item 351)

    def hazard_attributes(self, key: str) -> dict[str, Any]:
        """What "Alert at X" shows of fire and smoke, whether or not they turn it on; empty without the keys."""
        hz = self._hz.get(key) or {}
        out: dict[str, Any] = {}
        if self._firms_key:
            # Until the place's first fetch has answered, the counts are unknown, not 0: seen live 2026-11-17, an
            # options reload showed home "0 fires" for some seconds where it had 6 before and after.
            checked = hz.get("dets") is not None
            fires = hz.get("near") or []
            out["fires_within_km"] = self._fire_km
            out["fires_near"] = len(fires) if checked else None
            out["nearest_fire_km"] = fires[0]["km"] if fires else None
            out["fires_checked"] = hz.get("fires_at")
            out["standing_sources_listed"] = len(hz["static"]) if hz.get("static") is not None else None
            if hz.get("fire_reason"):
                out["fire_reason"] = hz["fire_reason"]
        if self._airnow_key:
            s = hz.get("smoke")
            out["smoke_aqi_threshold"] = self._smoke_aqi
            out["pm25_aqi"] = s["aqi"] if s else None
            out["pm25_site"] = s["site"] if s else None
            out["pm25_observed"] = s["observed"] if s else None
            if hz.get("smoke_reason"):
                out["smoke_reason"] = hz["smoke_reason"]
        return out

    @callback
    def _hazard_records(self, place: Place, lat: float, lon: float) -> list[dict[str, Any]]:
        """Fire and smoke records for the place from what is held, and fetches started when due."""
        if not (self._firms_key or self._airnow_key):
            return []
        hz = self._hz.setdefault(place.key, {})
        hz["lat"], hz["lon"] = lat, lon
        mono = time.monotonic()
        recs: list[dict[str, Any]] = []
        if self._firms_key:
            if not hz.get("fire_inflight") and mono >= hz.get("fire_due", 0.0):
                hz["fire_inflight"] = True
                self.entry.async_create_background_task(
                    self.hass, self._fetch_fires(place.key), f"live_track_weather fires for {place.key}")
            near = hazards.fires_near(hz.get("dets") or [], lat, lon, self._fire_km, hz.get("static") or set(),
                                      datetime.now(timezone.utc))
            hz["near"] = near
            if r := hazards.fire_record(near):
                recs.append(r)
        if self._airnow_key:
            if not hz.get("smoke_inflight") and mono >= hz.get("smoke_due", 0.0):
                hz["smoke_inflight"] = True
                self.entry.async_create_background_task(
                    self.hass, self._fetch_smoke(place.key), f"live_track_weather smoke for {place.key}")
            if r := hazards.smoke_record(hz.get("smoke"), self._smoke_aqi):
                recs.append(r)
        return recs

    async def _firms_get(self, url: str) -> tuple[int, str]:
        try:
            async with self._session.get(url, headers={"User-Agent": USER_AGENT},
                                         timeout=aiohttp.ClientTimeout(total=REQUEST_TIMEOUT)) as resp:
                return resp.status, await resp.text()
        except (aiohttp.ClientError, TimeoutError) as err:
            _LOGGER.debug("FIRMS request failed: %s", type(err).__name__)
            return 0, ""

    async def _static_list(self, hz: dict[str, Any]) -> None:
        """The place's list of standing heat sources: NASA's static classes in the standard product around it.
        Rebuilt after RECUR_REFRESH_S x 30, or when the place is more than half the fire distance from where it was
        built; at most once per FIRE_POLL_S."""
        lat, lon = hz["lat"], hz["lon"]
        fresh = (hz.get("static") is not None and time.time() - hz.get("static_at", 0) < 30 * RECUR_REFRESH_S
                 and places.distance_m(lat, lon, hz["static_lat"], hz["static_lon"]) <= self._fire_km * 500)
        if fresh or time.monotonic() - hz.get("static_tried", -1e18) < FIRE_POLL_S:
            return
        hz["static_tried"] = time.monotonic()
        if not self._sp_max or time.time() - self._sp_max[1] > RECUR_REFRESH_S:
            status, text = await self._firms_get(f"{FIRMS_AVAIL_URL}/{self._firms_key}/ALL")
            dates = hazards.sp_max_dates(text) if status == 200 else {}
            if not dates:
                hz["fire_reason"] = "FIRMS's list of standard-product dates did not answer"
                return
            self._sp_max = (dates, time.time())
        area = hazards.box(lat, lon, self._fire_km + 5)
        sp: list[dict[str, Any]] = []
        for src in hazards.STATIC_SOURCES:
            max_date = self._sp_max[0].get(src)
            if not max_date:
                continue
            for first in hazards.static_windows(max_date):
                status, text = await self._firms_get(f"{FIRMS_AREA_URL}/{self._firms_key}/{src}/{area}/5/{first}")
                rows = hazards.parse_firms(text, src) if status == 200 else None
                if rows is None:
                    hz["fire_reason"] = f"FIRMS's standard product did not answer ({status})"
                    return
                sp.extend(rows)
        hz.update(static=hazards.static_cells(sp), static_at=time.time(), static_lat=lat, static_lon=lon)

    async def _fetch_fires(self, key: str) -> None:
        hz = self._hz[key]
        try:
            hz["fire_due"] = time.monotonic() + FIRE_POLL_S
            await self._static_list(hz)
            if hz.get("static") is None:
                return   # no list yet: asking for fires now would report every mill near the place
            area = hazards.box(hz["lat"], hz["lon"], self._fire_km)
            by_src = hz.setdefault("by_src", {})
            failed = []
            for src in hazards.FIRE_SOURCES:
                status, text = await self._firms_get(
                    f"{FIRMS_AREA_URL}/{self._firms_key}/{src}/{area}/{hazards.FIRE_DAY_RANGE}")
                rows = hazards.parse_firms(text, src) if status == 200 else None
                if rows is None:
                    failed.append(f"{src}: {status} {text.strip()[:60]}".strip())
                    continue
                by_src[src] = rows
            if by_src:
                hz["dets"] = [d for rows in by_src.values() for d in rows]
                hz["fires_at"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
            hz["fire_reason"] = ("FIRMS did not answer for " + "; ".join(failed)) if failed else None
        finally:
            hz["fire_inflight"] = False
            self._recompute()

    async def _fetch_smoke(self, key: str) -> None:
        hz = self._hz[key]
        try:
            hz["smoke_due"] = time.monotonic() + SMOKE_POLL_S
            try:
                async with self._session.get(
                        AIRNOW_URL, params={"format": "application/json", "latitude": f"{hz['lat']:.4f}",
                                            "longitude": f"{hz['lon']:.4f}", "API_KEY": self._airnow_key},
                        headers={"User-Agent": USER_AGENT},
                        timeout=aiohttp.ClientTimeout(total=REQUEST_TIMEOUT)) as resp:
                    status = resp.status
                    body = await resp.json(content_type=None)
            except (aiohttp.ClientError, TimeoutError, ValueError) as err:
                _LOGGER.debug("AirNow request failed: %s", type(err).__name__)
                hz["smoke_reason"] = "AirNow did not answer"
                return
            reading = hazards.parse_airnow(body)
            hz["smoke"] = reading
            if reading is not None:
                hz["smoke_reason"] = None
            else:
                msg = hazards.airnow_error(body)
                hz["smoke_reason"] = (f"AirNow: {msg}" if msg else
                                      f"AirNow gave no PM2.5 reading ({status})")
        finally:
            hz["smoke_inflight"] = False
            self._recompute()


    # ------------------------------------------------------------------ elevation (item 352 step 4)

    @callback
    def async_add_elev_listener(self, cb: Callable[[str], None]) -> CALLBACK_TYPE:
        self._elev_listeners.append(cb)

        def remove() -> None:
            if cb in self._elev_listeners:
                self._elev_listeners.remove(cb)
        return remove

    def elevation(self, key: str) -> dict[str, Any]:
        """{"m", "resolution_m", "source", "on_water", "checked", "reason"} for the place; empty until its first
        answer. On water "m" is the surface (step 4b)."""
        st = self._elev.get(key) or {}
        return {k: st.get(k) for k in ("m", "resolution_m", "source", "on_water", "checked", "reason")}

    def depth(self, key: str) -> dict[str, Any]:
        """{"m" (positive down), "source", "sea", "checked", "reason"} for the place (step 4b); "m" None on land."""
        st = self._elev.get(key) or {}
        return {"m": st.get("depth_m"), "source": st.get("depth_source"), "sea": st.get("sea"),
                "checked": st.get("checked"), "reason": st.get("depth_reason")}

    @callback
    def _elev_check(self, place: Place, lat: float, lon: float) -> None:
        """Ask USGS's 3DEP point query at start-up, then only after a move of more than usgs.ELEV_MOVE_M and no sooner
        than usgs.ELEV_GAP_S (Lee); a failed ask again after the gap."""
        st = self._elev.setdefault(place.key, {})
        if st.get("inflight"):
            return
        due, wait = usgs.elevation_due(st.get("lat"), st.get("lon"), st.get("at"), bool(st.get("failed")), lat, lon,
                                       time.monotonic())
        if not due:
            tkey = f"elevation {place.key}"
            if wait is not None and tkey not in self._timers:
                self._timers[tkey] = async_call_later(self.hass, wait + 1, self._timer_fired(tkey))
            return
        st.update(inflight=True, lat=lat, lon=lon, at=time.monotonic())
        self.entry.async_create_background_task(
            self.hass, self._fetch_elev(place.key, lat, lon), f"live_track_weather elevation for {place.key}")

    async def _elev_get(self, url: str, params: dict[str, str] | None, binary: bool = False) -> tuple[int, Any]:
        """(HTTP status, parsed JSON, or the bytes when binary); the JSON is None for an answer that is not JSON (3DEP's
        plain text outside its coverage, MEASURED 2026-11-18); (0, None) when the source could not be asked."""
        try:
            async with self._session.get(url, params=params, headers={"User-Agent": USER_AGENT},
                                         timeout=aiohttp.ClientTimeout(total=REQUEST_TIMEOUT)) as resp:
                status = resp.status
                raw = await resp.read() if status == 200 else b""
        except (aiohttp.ClientError, TimeoutError) as err:
            _LOGGER.debug("Elevation source %s failed: %s", url.split("/")[2], type(err).__name__)
            return 0, None
        if status != 200:
            _LOGGER.debug("Elevation source %s answered HTTP %s", url.split("/")[2], status)
            return status, None
        if binary:
            return status, raw
        try:
            return status, json.loads(raw)
        except ValueError:
            return status, None

    async def _src_json(self, url: str, params: dict[str, str], parse: Callable[[Any], Any]) -> tuple[bool, Any]:
        status, doc = await self._elev_get(url, params)
        return (True, parse(doc)) if status == 200 else (False, None)

    async def _src_epqs(self, lat: float, lon: float) -> tuple[bool, Any]:
        def parse(doc: Any) -> dict[str, Any] | None:
            got = usgs.parse_elevation(doc)   # plain text outside 3DEP's coverage arrives as None
            return {**got, "source": elevation.SRC_3DEP} if got else None
        return await self._src_json(usgs.EPQS_URL, usgs.epqs_params(lat, lon), parse)

    async def _src_nrcan(self, lat: float, lon: float) -> tuple[bool, Any]:
        return await self._src_json(elevation.NRCAN_URL, elevation.nrcan_params(lat, lon), elevation.parse_nrcan)

    async def _src_kartverket(self, lat: float, lon: float) -> tuple[bool, Any]:
        return await self._src_json(elevation.KARTVERKET_URL, elevation.kartverket_params(lat, lon),
                                    elevation.parse_kartverket)

    async def _src_noaa(self, lat: float, lon: float) -> tuple[bool, Any]:
        return await self._src_json(elevation.NOAA_URL, elevation.noaa_params(lat, lon), elevation.parse_noaa)

    async def _src_terrain(self, lat: float, lon: float) -> tuple[bool, Any]:
        """The AWS Terrain Tiles z15 tile under the place; the last few tiles are kept."""
        x, y, px, py = elevation.terrain_tile(lat, lon)
        png = self._tiles.get((x, y))
        if png is None:
            status, png = await self._elev_get(elevation.terrain_url(x, y), None, binary=True)
            if status != 200 or not png:
                return False, None
            self._tiles[(x, y)] = png
            while len(self._tiles) > 4:
                self._tiles.pop(next(iter(self._tiles)))
        m = await self.hass.async_add_executor_job(elevation.decode_terrarium, png, px, py)
        return True, elevation.terrain_record(m)

    async def _src_sea(self, lat: float, lon: float) -> tuple[bool, Any]:
        _status, doc = await self._gn_get(geonames.OCEAN_URL, lat, lon)
        return geonames.parse_ocean(doc)

    async def _fetch_elev(self, key: str, lat: float, lon: float) -> None:
        """elevation.run_chain with this integration's requests (step 4b)."""
        st = self._elev[key]
        try:
            got, failed = await elevation.run_chain(
                lat, lon, epqs=self._src_epqs, nrcan=self._src_nrcan, kartverket=self._src_kartverket,
                terrain=self._src_terrain, noaa=self._src_noaa, sea=self._src_sea,
                has_geonames=self._gn_user is not None)
            if got is None:
                st.update(failed=True, reason="no elevation service answered")
                return   # what was shown stays until a source answers
            st.update(got, failed=failed, checked=datetime.now(timezone.utc).isoformat(timespec="seconds"))
        finally:
            st["inflight"] = False
            for cb in list(self._elev_listeners):
                cb(key)
