"""Watch places: is home, or a person, device tracker or zone, inside an alert (Weather SSOT item 334).

The decisions are in places.py; this holds the places, their locations and their NWS zones, and tells
each place's entity when to redraw. It reads the alerts and MET Norway coordinators the map already polls:
no alert request is added. The one request it adds is NWS /zones?point=, asked for a place's location
once and kept (in .storage, ZONES_STORE_KEY), asked again only for a point more than ZONES_REUSE_M from
any point already asked, at most once per alerts poll per place, and after ZONES_KEEP_S.

! Each place's location is SENT TO NWS (api.weather.gov) to learn its zones, rounded to 4 decimals
(about 11 m). The README's "Data use" says so.
"""

from __future__ import annotations

import logging
import time
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

import aiohttp

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_LATITUDE, ATTR_LONGITUDE, STATE_HOME
from homeassistant.core import CALLBACK_TYPE, Event, EventStateChangedData, HomeAssistant, callback
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.event import async_call_later, async_track_state_change_event
from homeassistant.helpers.storage import Store

from . import places
from .const import (CONF_ALERT_THRESHOLD, CONF_SCAN_INTERVAL, CONF_WATCH_ENTITIES, CONF_WATCH_HOME,
                    DEFAULT_SCAN_INTERVAL, DEFAULT_WATCH_HOME, MET_ALERTS_CAP, REQUEST_TIMEOUT, USER_AGENT,
                    ZONES_CACHE_MAX, ZONES_KEEP_S, ZONES_REUSE_M, ZONES_STORE_KEY, ZONES_URL)

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
        # place key -> (keys, lat, lon) of the last answer that place used
        self._place_keys: dict[str, tuple[set[str], float, float]] = {}
        self._results: dict[str, dict[str, Any]] = {}
        self._listeners: list[CALLBACK_TYPE] = []
        self._timers: dict[str, CALLBACK_TYPE] = {}

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
        self._recompute()

    # ------------------------------------------------------------------ entities

    @callback
    def async_add_listener(self, cb: CALLBACK_TYPE) -> CALLBACK_TYPE:
        self._listeners.append(cb)

        def remove() -> None:
            if cb in self._listeners:
                self._listeners.remove(cb)
        return remove

    def result(self, key: str) -> dict[str, Any]:
        return self._results.get(key) or {}

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
                continue
            lat, lon = loc
            keys = places.cached_keys(self._cache, lat, lon, now, ZONES_REUSE_M, ZONES_KEEP_S)
            if keys is not None:
                self._place_keys[p.key] = (keys, lat, lon)
            else:
                self._maybe_ask(p, lat, lon)
                # Until NWS answers for the new spot, the place keeps the zones of its last answer.
                held = self._place_keys.get(p.key)
                keys = held[0] if held else None
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
            self.hass, self._ask(place, lat, lon), f"live_track_weather zones for {place.key}")

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
            keys = await self._fetch_zones(lat, lon)
        finally:
            self._inflight.discard(place.key)
        if keys is None:
            return
        self._cache = places.remember(self._cache, lat, lon, keys, time.time(), ZONES_REUSE_M, ZONES_CACHE_MAX)
        self._store.async_delay_save(lambda: {"points": self._cache}, 10)
        self._place_keys[place.key] = (keys, lat, lon)
        self._recompute()

    async def _fetch_zones(self, lat: float, lon: float) -> set[str] | None:
        """The NWS zones holding the point; an empty set where NWS has none (it answers 400 for a point
        outside its area, MEASURED 2026-11-17); None when it could not be asked."""
        try:
            async with self._session.get(
                ZONES_URL, params={"point": f"{lat:.4f},{lon:.4f}"},
                headers={"User-Agent": USER_AGENT, "Accept": "application/geo+json"},
                timeout=aiohttp.ClientTimeout(total=REQUEST_TIMEOUT),
            ) as resp:
                if resp.status == 400:
                    return set()
                if resp.status != 200:
                    _LOGGER.debug("NWS zones answered HTTP %s", resp.status)
                    return None
                doc = await resp.json(content_type=None)
        except (aiohttp.ClientError, TimeoutError, ValueError) as err:
            _LOGGER.debug("NWS zones lookup failed: %s", type(err).__name__)
            return None
        return places.zone_keys(doc)
