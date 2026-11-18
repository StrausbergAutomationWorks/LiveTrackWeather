"""The one sensor: how many US alerts are live, and the list the map draws.

The state is the count, and it is recorded. The live list rides in
attributes that are NOT recorded: it changes on nearly every poll, and an
attribute unique on every write mints a new recorder blob each time
(05_SHARED_LESSONS.md A7). The card reads it from the live state instead.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity, SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import knmi, place_sensors
from .const import (ATTRIBUTION, DOMAIN, KNMI_ATTRIBUTION, MET_ATTRIBUTION, MET_MARINE_SHAPE_ORDER,
                    MET_WARNINGS_SHAPE_ORDER, OUTLOOK_SHAPE_ORDER, SPC_ATTRIBUTION)
from .coordinator import WeatherCoordinator
from .knmi_relay import KnmiRelay
from .met_coordinator import MetMarineCoordinator, MetWarningsCoordinator
from .outlook_coordinator import OutlookCoordinator
from .storm_coordinator import StormCoordinator

# ! PERMANENT from first install: the unique_id and so the entity_id derive
# from it (00_START_HERE.md damage item 2). Confirmed by Lee 2026-10-05:
# "alerts", not "warnings", because it carries watches, advisories and
# statements too.
SENSOR_KEY = "us_alerts"
SENSOR_NAME = "US alerts"

LIVE_ATTRS = ("shapes_url", "zones", "polygons", "styles", "updated", "unknown_events")


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    data = hass.data[DOMAIN]
    async_add_entities([AlertsSensor(data[entry.entry_id], entry, data["shapes_url"]),
                        StormShapesSensor(data[f"{entry.entry_id}_storms"], entry),
                        OutlookSensor(data[f"{entry.entry_id}_outlook"], entry),
                        MetWarningsSensor(data[f"{entry.entry_id}_met_warnings"], entry),
                        MetMarineSensor(data[f"{entry.entry_id}_met_marine"], entry)])
    if f"{entry.entry_id}_knmi" in data:
        async_add_entities([KnmiRadarSensor(data[f"{entry.entry_id}_knmi"], entry)])
    # the fire-and-smoke map (D19)
    from .firemap_coordinator import AirSitesMap, FireMap, PointsSensor
    for suffix, cls in (("fire_map", FireMap), ("air_sites_map", AirSitesMap)):
        if f"{entry.entry_id}_{suffix}" in data:
            async_add_entities([PointsSensor(data[f"{entry.entry_id}_{suffix}"], entry)])
    # item 352: earthquakes, the point layer (D19) and the ShakeMap lines (D12)
    quakes = data[f"{entry.entry_id}_quakes"]
    async_add_entities([QuakePointsSensor(quakes, entry), ShakeSensor(quakes, entry)])
    # item 350: wind and temperature observed at each watched place
    place_sensors.async_add(hass, entry, async_add_entities)


class AlertsSensor(CoordinatorEntity[WeatherCoordinator], SensorEntity):
    _attr_has_entity_name = True
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = "alerts"
    _attr_icon = "mdi:weather-cloudy-alert"
    _attr_attribution = ATTRIBUTION
    _unrecorded_attributes = frozenset(LIVE_ATTRS)

    def __init__(self, coordinator: WeatherCoordinator, entry: ConfigEntry,
                 shapes_url: str) -> None:
        super().__init__(coordinator)
        self._shapes_url = shapes_url
        self._attr_unique_id = f"{entry.entry_id}_{SENSOR_KEY}"
        self._attr_name = SENSOR_NAME
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name="Live Track Weather",
            model="NWS active alerts",
            entry_type=DeviceEntryType.SERVICE,
        )

    @property
    def native_value(self) -> int | None:
        return (self.coordinator.data or {}).get("count")

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        d = self.coordinator.data or {}
        return {
            "shapes_url": self._shapes_url,
            "zones": d.get("zones", {}),
            "polygons": d.get("polygons", []),
            "styles": d.get("styles", {}),
            "updated": d.get("updated"),
            "unknown_events": d.get("unknown_events", []),
        }


# ! PERMANENT from first install, like SENSOR_KEY (00_START_HERE.md damage item 2).
STORM_SENSOR_KEY = "tropical_cyclones"
STORM_SENSOR_NAME = "Tropical cyclones"
STORM_LIVE_ATTRS = ("zones", "polygons", "styles", "updated")


class StormShapesSensor(CoordinatorEntity[StormCoordinator], SensorEntity):
    """How many tropical cyclones are drawn, and the shapes the card draws for them:
    cones, wind extents and tracks, as D12 `polygons` with no shape file (D15).
    The storms themselves are geo_location entities."""

    _attr_has_entity_name = True
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = "storms"
    _attr_icon = "mdi:weather-hurricane"
    _unrecorded_attributes = frozenset(STORM_LIVE_ATTRS)

    def __init__(self, coordinator: StormCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_{STORM_SENSOR_KEY}"
        self._attr_name = STORM_SENSOR_NAME
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name="Live Track Weather",
            model="NWS active alerts",
            entry_type=DeviceEntryType.SERVICE,
        )

    @property
    def native_value(self) -> int | None:
        return (self.coordinator.data or {}).get("count")

    # ! No attribution: every storm marker credits its own source (D4d), and a
    # credit here repeated both in the map's attribution line (look page, 2026-10-27).

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        d = self.coordinator.data or {}
        return {
            "zones": {},
            "polygons": d.get("polygons", []),
            "styles": d.get("styles", {}),
            "updated": d.get("updated"),
        }


# ! PERMANENT from first install, like SENSOR_KEY (00_START_HERE.md damage item 2).
OUTLOOK_SENSOR_KEY = "severe_weather_outlook"
OUTLOOK_SENSOR_NAME = "Severe weather outlook"
OUTLOOK_LIVE_ATTRS = ("zones", "polygons", "styles")


class OutlookSensor(CoordinatorEntity[OutlookCoordinator], SensorEntity):
    """SPC's Day 1 categorical outlook, Marginal and up (contract D16): the state is the highest
    risk level today, 0 (none) to 5 (High), recorded; the areas ride as D12 `polygons` with no
    shape file, drawn beneath the alerts (`shape_order`)."""

    _attr_has_entity_name = True
    _attr_icon = "mdi:weather-lightning"
    _attr_attribution = SPC_ATTRIBUTION
    _unrecorded_attributes = frozenset(OUTLOOK_LIVE_ATTRS)

    def __init__(self, coordinator: OutlookCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_{OUTLOOK_SENSOR_KEY}"
        self._attr_name = OUTLOOK_SENSOR_NAME
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name="Live Track Weather",
            model="NWS active alerts",
            entry_type=DeviceEntryType.SERVICE,
        )

    @property
    def native_value(self) -> int | None:
        return (self.coordinator.data or {}).get("level")

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        d = self.coordinator.data or {}
        return {
            "risk": d.get("risk"),
            "issued": d.get("issued"),
            "valid_from": d.get("valid_from"),
            "valid_to": d.get("valid_to"),
            "zones": {},
            "polygons": d.get("polygons", []),
            "styles": d.get("styles", {}),
            "shape_order": OUTLOOK_SHAPE_ORDER,
        }


# ! PERMANENT from first install, like SENSOR_KEY (00_START_HERE.md damage item 2).
MET_WARNINGS_KEY = "met_norway_warnings"
MET_WARNINGS_NAME = "MET Norway warnings"
MET_MARINE_KEY = "met_norway_marine_forecasts"
MET_MARINE_NAME = "MET Norway marine forecasts"
MET_LIVE_ATTRS = ("zones", "polygons", "styles")


def _device(entry: ConfigEntry) -> DeviceInfo:
    return DeviceInfo(identifiers={(DOMAIN, entry.entry_id)}, name="Live Track Weather",
                      model="NWS active alerts", entry_type=DeviceEntryType.SERVICE)


class MetWarningsSensor(CoordinatorEntity[MetWarningsCoordinator], SensorEntity):
    """MET Norway's current warnings, land, coast and sea (Weather SSOT item 310): the state is how many are
    drawn, recorded; the areas ride as D12 `polygons` with no shape file, beside the US alerts, each with the
    `info` the card shows when it is clicked."""

    _attr_has_entity_name = True
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = "warnings"
    _attr_icon = "mdi:alert-outline"
    _attr_attribution = MET_ATTRIBUTION
    _unrecorded_attributes = frozenset(MET_LIVE_ATTRS)

    def __init__(self, coordinator: MetWarningsCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_{MET_WARNINGS_KEY}"
        self._attr_name = MET_WARNINGS_NAME
        self._attr_device_info = _device(entry)

    @property
    def native_value(self) -> int | None:
        return (self.coordinator.data or {}).get("count")

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        d = self.coordinator.data or {}
        return {"highest": d.get("highest"), "zones": {}, "polygons": d.get("polygons", []),
                "styles": d.get("styles", {}), "shape_order": MET_WARNINGS_SHAPE_ORDER}


class MetMarineSensor(CoordinatorEntity[MetMarineCoordinator], SensorEntity):
    """MET Norway's sea-area and coastal text forecasts (Weather SSOT item 310): every area a D12 polygon whose
    forecast the card shows when it is clicked, beneath the warnings. The state is how many areas, recorded."""

    _attr_has_entity_name = True
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = "areas"
    _attr_icon = "mdi:waves"
    _attr_attribution = MET_ATTRIBUTION
    _unrecorded_attributes = frozenset(MET_LIVE_ATTRS)

    def __init__(self, coordinator: MetMarineCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_{MET_MARINE_KEY}"
        self._attr_name = MET_MARINE_NAME
        self._attr_device_info = _device(entry)

    @property
    def native_value(self) -> int | None:
        return (self.coordinator.data or {}).get("count")

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        d = self.coordinator.data or {}
        return {"issued": d.get("issued"), "zones": {}, "polygons": d.get("polygons", []),
                "styles": d.get("styles", {}), "shape_order": MET_MARINE_SHAPE_ORDER}


# ! PERMANENT from first install, as above: sensor.live_track_weather_knmi_radar (Weather SSOT item 278).
KNMI_SENSOR_KEY = "knmi_radar"
KNMI_SENSOR_NAME = "KNMI radar"


class KnmiRadarSensor(CoordinatorEntity[KnmiRelay], SensorEntity):
    """KNMI's radar relay for the Netherlands (Weather SSOT item 278, contract D13 "Relays"): exists only with
    the user's own KNMI key. The state is the newest frame's time; `radar_relay` is what the card reads, not
    recorded (it changes every frame). Without a usable frame `radar_relay` carries no `time`, and the card
    uses its other sources there."""

    _attr_has_entity_name = True
    _attr_device_class = SensorDeviceClass.TIMESTAMP
    _attr_icon = "mdi:radar"
    _attr_attribution = KNMI_ATTRIBUTION
    _unrecorded_attributes = frozenset({"radar_relay"})

    def __init__(self, coordinator: KnmiRelay, entry: ConfigEntry) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_{KNMI_SENSOR_KEY}"
        self._attr_name = KNMI_SENSOR_NAME
        self._attr_device_info = _device(entry)

    @property
    def native_value(self) -> datetime | None:
        when = (self.coordinator.data or {}).get("time")
        return knmi.parse_time(when) if when else None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        relay = self.coordinator.relay()
        return {"radar_relay": relay} if relay else {}


# ! PERMANENT from first install, as above (Weather SSOT item 352, contract D20):
# sensor.live_track_weather_earthquakes and sensor.live_track_weather_earthquake_shaking.
QUAKE_SENSOR_KEY = "earthquakes"
QUAKE_SENSOR_NAME = "Earthquakes"
SHAKE_SENSOR_KEY = "earthquake_shaking"
SHAKE_SENSOR_NAME = "Earthquake shaking"
QUAKE_POINT_ORDER = 2
SHAKE_SHAPE_ORDER = 5


class QuakePointsSensor(CoordinatorEntity, SensorEntity):
    """The day's earthquakes not drawn as markers, as a D19 point file (D20). The state is the number of points."""

    _attr_has_entity_name = True
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = "quakes"
    _attr_icon = "mdi:pulse"
    _unrecorded_attributes = frozenset({"points_url", "point_styles", "updated", "reason"})

    def __init__(self, coordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator)
        from . import usgs
        self._usgs = usgs
        self._attr_unique_id = f"{entry.entry_id}_{QUAKE_SENSOR_KEY}"
        self._attr_name = QUAKE_SENSOR_NAME
        self._attr_attribution = usgs.QUAKE_ATTRIBUTION
        self._attr_device_info = _device(entry)

    @property
    def native_value(self) -> int | None:
        return (self.coordinator.data or {}).get("count")

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        d = self.coordinator.data or {}
        return {"points_url": d.get("url"), "point_styles": self._usgs.QUAKE_STYLES, "point_order": QUAKE_POINT_ORDER,
                "quakes_today": d.get("quakes_today"), "min_magnitude": self.coordinator.min_mag,
                "updated": d.get("updated"), "reason": self.coordinator.reason}


class ShakeSensor(CoordinatorEntity, SensorEntity):
    """ShakeMap's intensity contours for the biggest quakes of the day, as D12 lines with no shape file (D20), above
    every fill. The state is how many ShakeMaps are drawn."""

    _attr_has_entity_name = True
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = "shakemaps"
    _attr_icon = "mdi:waveform"
    _unrecorded_attributes = frozenset({"zones", "polygons", "styles", "quakes"})

    def __init__(self, coordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator)
        from . import usgs
        self._attr_unique_id = f"{entry.entry_id}_{SHAKE_SENSOR_KEY}"
        self._attr_name = SHAKE_SENSOR_NAME
        self._credit = usgs.SHAKE_ATTRIBUTION
        self._attr_device_info = _device(entry)

    @property
    def attribution(self) -> str | None:
        """Only while a ShakeMap is drawn: the card credits a publisher's string whenever it exists (seen live
        2026-11-18)."""
        return self._credit if (self.coordinator.data or {}).get("polygons") else None

    @property
    def native_value(self) -> int | None:
        d = self.coordinator.data or {}
        return len(d["shakemaps"]) if d.get("updated") else None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        d = self.coordinator.data or {}
        return {"zones": {}, "polygons": d.get("polygons", []), "styles": d.get("styles", {}),
                "shape_order": SHAKE_SHAPE_ORDER, "quakes": d.get("shakemaps", [])}
