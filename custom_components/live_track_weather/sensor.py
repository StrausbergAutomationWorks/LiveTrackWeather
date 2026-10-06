"""The one sensor: how many US alerts are live, and the list the map draws.

The state is the count, and it is recorded. The live list rides in
attributes that are NOT recorded: it changes on nearly every poll, and an
attribute unique on every write mints a new recorder blob each time
(05_SHARED_LESSONS.md A7). The card reads it from the live state instead.
"""

from __future__ import annotations

from typing import Any

from homeassistant.components.sensor import SensorEntity, SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import ATTRIBUTION, DOMAIN
from .coordinator import WeatherCoordinator

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
    async_add_entities([AlertsSensor(data[entry.entry_id], entry, data["shapes_url"])])


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
