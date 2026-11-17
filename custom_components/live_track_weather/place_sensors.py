"""Observed wind and temperature at each watched place (Weather SSOT item 350; Lee 2026-11-17 03:58).

Four sensors per place, the same places as items 334 and 349: "Wind at X", "Wind gust at X", "Wind direction at X"
and "Temperature at X". Each shows the nearest NWS station's latest report that carries its value (wind speed, gust
and direction from one station's report, temperature picked on its own), with the station, its network (`provider`),
its distance from the place and the report's age as attributes; unavailable when no report younger than 2 hours
has it. A gust is unknown when the station reported none: airports report a gust only while it is gusting.
Added to the sensor platform by sensor.py.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity, SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import DEGREE, UnitOfSpeed, UnitOfTemperature
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import observe
from .const import DOMAIN
from .places_watch import HOME, Place, PlaceWatch

ATTRIBUTION = "Observations: US National Weather Service"

# ! PERMANENT from first install: the unique_id, and so the entity_id, derive from these keys
# (00_START_HERE.md damage item 2): sensor.live_track_weather_wind_at_home and so on for home.
# key: (name, which pick, report field, device class, unit, state class, display decimals)
# Display decimals: HA converts km/h to the user's unit (seen live: 9.252 km/h shown as 5.74892627057982 mph).
KINDS = {
    "wind_at": ("Wind at", "wind", "wind_speed", SensorDeviceClass.WIND_SPEED, UnitOfSpeed.KILOMETERS_PER_HOUR,
                SensorStateClass.MEASUREMENT, 1),
    "wind_gust_at": ("Wind gust at", "wind", "wind_gust", SensorDeviceClass.WIND_SPEED,
                     UnitOfSpeed.KILOMETERS_PER_HOUR, SensorStateClass.MEASUREMENT, 1),
    "wind_direction_at": ("Wind direction at", "wind", "wind_direction", SensorDeviceClass.WIND_DIRECTION, DEGREE,
                          SensorStateClass.MEASUREMENT_ANGLE, 0),
    "temperature_at": ("Temperature at", "temperature", "temperature", SensorDeviceClass.TEMPERATURE,
                       UnitOfTemperature.CELSIUS, SensorStateClass.MEASUREMENT, 1),
}


def unique_id(entry: ConfigEntry, kind: str, place: Place) -> str:
    return f"{entry.entry_id}_{kind}_{place.key}"


def place_label(hass: HomeAssistant, place: Place) -> str:
    if place.key == HOME:
        return "Home"
    st = hass.states.get(place.entity_id)
    return (st.attributes.get("friendly_name") if st else None) or place.entity_id.split(".", 1)[-1]


@callback
def async_add(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    watch: PlaceWatch | None = hass.data[DOMAIN].get(f"{entry.entry_id}_places")
    places = watch.places if watch else []
    # A place the user took out of the options takes its sensors with it.
    wanted = {unique_id(entry, k, p) for k in KINDS for p in places}
    prefixes = tuple(f"{entry.entry_id}_{k}_" for k in KINDS)
    reg = er.async_get(hass)
    for ent in er.async_entries_for_config_entry(reg, entry.entry_id):
        if ent.domain == "sensor" and ent.unique_id.startswith(prefixes) and ent.unique_id not in wanted:
            reg.async_remove(ent.entity_id)
    if watch:
        async_add_entities([PlaceObservation(hass, watch, p, entry, k) for p in places for k in KINDS])


class PlaceObservation(SensorEntity):
    _attr_has_entity_name = True
    _attr_should_poll = False
    _attr_attribution = ATTRIBUTION
    # the age changes on every redraw; keep it out of the recorder's attributes (05_SHARED_LESSONS.md A7)
    _unrecorded_attributes = frozenset({"age_min", "observed"})

    def __init__(self, hass: HomeAssistant, watch: PlaceWatch, place: Place, entry: ConfigEntry, kind: str) -> None:
        name, self._group, self._field, dev, unit, state_class, decimals = KINDS[kind]
        self._attr_suggested_display_precision = decimals
        self._watch = watch
        self._place = place
        self._attr_unique_id = unique_id(entry, kind, place)
        self._attr_name = f"{name} {place_label(hass, place)}"
        self._attr_device_class = dev
        self._attr_native_unit_of_measurement = unit
        self._attr_state_class = state_class
        self._attr_device_info = DeviceInfo(identifiers={(DOMAIN, entry.entry_id)}, name="Live Track Weather",
                                            model="NWS active alerts", entry_type=DeviceEntryType.SERVICE)

    async def async_added_to_hass(self) -> None:
        self.async_on_remove(self._watch.async_add_obs_listener(self._handle))

    @callback
    def _handle(self, key: str) -> None:
        if key == self._place.key:
            self.async_write_ha_state()

    def _chosen(self) -> dict[str, Any] | None:
        """The pick for this sensor's value, if its report is still younger than 2 hours."""
        pick = self._watch.observation(self._place.key).get("pick") or {}
        chosen = pick.get(self._group)
        if chosen is None or not observe.fresh(chosen["obs"], datetime.now(timezone.utc)):
            return None
        return chosen

    @property
    def available(self) -> bool:
        return self._chosen() is not None

    @property
    def native_value(self) -> float | None:
        chosen = self._chosen()
        return chosen["obs"].get(self._field) if chosen else None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        ob = self._watch.observation(self._place.key)
        attrs: dict[str, Any] = {"place": self._place.key}
        pick = ob.get("pick") or {}
        chosen = pick.get(self._group)
        if chosen:
            st, obs = chosen["station"], chosen["obs"]
            attrs.update(station=st["id"], station_name=st.get("name"), provider=st.get("provider"),
                         distance_km=st.get("km"), observed=obs["time"],
                         age_min=round(observe.age_s(obs, datetime.now(timezone.utc)) / 60))
        if ob.get("reason"):
            attrs["reason"] = ob["reason"]
        return attrs
