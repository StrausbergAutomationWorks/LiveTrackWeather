"""One weather entity per watched place: "Forecast at X" (Weather SSOT item 349; Lee 2026-11-17 01:55).

The same places as item 334's "Alert at X": home by default, and the people, device trackers and zones the user adds.
NWS's gridpoint forecast on US land and territories, MET Norway's Locationforecast elsewhere and on all water; the
entity follows its place and changes source as the place does. Daily, twice-daily and hourly forecasts from both
sources (forecast.py says how MET's are grouped). The current values are the forecast for this hour, not an
observation.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from homeassistant.components.weather import Forecast, WeatherEntity, WeatherEntityFeature
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfPrecipitationDepth, UnitOfPressure, UnitOfSpeed, UnitOfTemperature
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import forecast as fcmod
from .const import DOMAIN
from .places_watch import HOME, Place, PlaceWatch

# ! PERMANENT from first install: the unique_id, and so the entity_id, derive from these
# (00_START_HERE.md damage item 2): weather.live_track_weather_forecast_at_home for home; a watched entity's
# unique_id carries its entity id, its name the entity's friendly name when first created.
UID_PREFIX = "forecast_at_"
ATTRIBUTION = {fcmod.NWS: "Forecast: US National Weather Service",
               fcmod.MET: "Forecast: MET Norway (api.met.no), CC BY 4.0, modified"}


def unique_id(entry: ConfigEntry, place: Place) -> str:
    return f"{entry.entry_id}_{UID_PREFIX}{place.key}"


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    watch: PlaceWatch = hass.data[DOMAIN][f"{entry.entry_id}_places"]
    # A place the user took out of the options takes its entity with it.
    wanted = {unique_id(entry, p) for p in watch.places}
    reg = er.async_get(hass)
    for ent in er.async_entries_for_config_entry(reg, entry.entry_id):
        if (ent.domain == "weather" and ent.unique_id.startswith(f"{entry.entry_id}_{UID_PREFIX}")
                and ent.unique_id not in wanted):
            reg.async_remove(ent.entity_id)
    async_add_entities([PlaceForecast(hass, watch, p, entry) for p in watch.places])


class PlaceForecast(WeatherEntity):
    _attr_has_entity_name = True
    _attr_should_poll = False
    _attr_native_temperature_unit = UnitOfTemperature.CELSIUS
    _attr_native_wind_speed_unit = UnitOfSpeed.KILOMETERS_PER_HOUR
    _attr_native_precipitation_unit = UnitOfPrecipitationDepth.MILLIMETERS
    _attr_native_pressure_unit = UnitOfPressure.HPA
    _attr_supported_features = (WeatherEntityFeature.FORECAST_DAILY | WeatherEntityFeature.FORECAST_HOURLY
                                | WeatherEntityFeature.FORECAST_TWICE_DAILY)

    def __init__(self, hass: HomeAssistant, watch: PlaceWatch, place: Place, entry: ConfigEntry) -> None:
        self._watch = watch
        self._place = place
        self._attr_unique_id = unique_id(entry, place)
        if place.key == HOME:
            label = "Home"
        else:
            st = hass.states.get(place.entity_id)
            label = (st.attributes.get("friendly_name") if st else None) or place.entity_id.split(".", 1)[-1]
        self._attr_name = f"Forecast at {label}"
        self._attr_device_info = DeviceInfo(identifiers={(DOMAIN, entry.entry_id)}, name="Live Track Weather",
                                            model="NWS active alerts", entry_type=DeviceEntryType.SERVICE)

    async def async_added_to_hass(self) -> None:
        self.async_on_remove(self._watch.async_add_forecast_listener(self._handle))

    @callback
    def _handle(self, key: str) -> None:
        if key != self._place.key:
            return
        self.async_write_ha_state()
        self.hass.async_create_task(self.async_update_listeners(None))

    # ------------------------------------------------------------------ data

    def _data(self) -> dict[str, Any] | None:
        return self._watch.forecast(self._place.key).get("data")

    def _now(self) -> dict[str, Any]:
        d = self._data()
        if not d:
            return {}
        # the hour holding now, looked up at each read so the state moves on between fetches
        return fcmod.current(d.get("hourly") or [], datetime.now(timezone.utc)) or {}

    @property
    def available(self) -> bool:
        return True

    @property
    def attribution(self) -> str | None:
        d = self._data()
        return ATTRIBUTION.get(d["source"]) if d else None

    @property
    def condition(self) -> str | None:
        return self._now().get("condition")

    @property
    def native_temperature(self) -> float | None:
        return self._now().get("native_temperature")

    @property
    def humidity(self) -> float | None:
        return self._now().get("humidity")

    @property
    def native_dew_point(self) -> float | None:
        return self._now().get("native_dew_point")

    @property
    def native_pressure(self) -> float | None:
        return self._now().get("native_pressure")

    @property
    def native_wind_speed(self) -> float | None:
        return self._now().get("native_wind_speed")

    @property
    def wind_bearing(self) -> float | str | None:
        return self._now().get("wind_bearing")

    @property
    def cloud_coverage(self) -> float | None:
        return self._now().get("cloud_coverage")

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        f = self._watch.forecast(self._place.key)
        d = f.get("data") or {}
        attrs: dict[str, Any] = {"place": self._place.key, "source": d.get("source"),
                                 "forecast_updated": d.get("updated"), "grid": f.get("grid")}
        if f.get("reason"):
            attrs["reason"] = f["reason"]
        return attrs

    async def async_forecast_daily(self) -> list[Forecast] | None:
        d = self._data()
        return d.get("daily") if d else None

    async def async_forecast_twice_daily(self) -> list[Forecast] | None:
        d = self._data()
        return d.get("twice_daily") if d else None

    async def async_forecast_hourly(self) -> list[Forecast] | None:
        d = self._data()
        return d.get("hourly") if d else None
