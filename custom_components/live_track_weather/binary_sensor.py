"""One binary sensor per watched place: on while the place is inside an alert (Weather SSOT item 334).

Lee 2026-11-16: "Alert at X"; on for any alert, raised by the CAP-severity setting; home is watched by
default and the user may switch it off and add people, device trackers or zones. Device class `safety`:
on means unsafe. The alerts at the place ride in attributes, worst first; they change only when the alerts
at that place change, so they are recorded.
"""

from __future__ import annotations

from typing import Any

from homeassistant.components.binary_sensor import BinarySensorDeviceClass, BinarySensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .places_watch import HOME, Place, PlaceWatch

# ! PERMANENT from first install: the unique_id, and so the entity_id, derive from these
# (00_START_HERE.md damage item 2). binary_sensor.live_track_weather_alert_at_home for home; a watched
# entity's unique_id carries its entity id, its name the entity's friendly name when first created.
UID_PREFIX = "alert_at_"
PLACES_ATTRIBUTION = ("Alerts: US National Weather Service; MET Norway (api.met.no), CC BY 4.0; earthquakes: USGS. "
                      "Zones: US National Weather Service")


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
        if (ent.domain == "binary_sensor" and ent.unique_id.startswith(f"{entry.entry_id}_{UID_PREFIX}")
                and ent.unique_id not in wanted):
            reg.async_remove(ent.entity_id)
    async_add_entities([PlaceAlertSensor(hass, watch, p, entry) for p in watch.places])


class PlaceAlertSensor(BinarySensorEntity):
    _attr_has_entity_name = True
    _attr_device_class = BinarySensorDeviceClass.SAFETY
    _attr_should_poll = False
    _attr_attribution = PLACES_ATTRIBUTION

    def __init__(self, hass: HomeAssistant, watch: PlaceWatch, place: Place, entry: ConfigEntry) -> None:
        self._watch = watch
        self._place = place
        self._attr_unique_id = unique_id(entry, place)
        if place.key == HOME:
            label = "Home"
        else:
            st = hass.states.get(place.entity_id)
            label = (st.attributes.get("friendly_name") if st else None) or place.entity_id.split(".", 1)[-1]
        self._attr_name = f"Alert at {label}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name="Live Track Weather",
            model="NWS active alerts",
            entry_type=DeviceEntryType.SERVICE,
        )

    async def async_added_to_hass(self) -> None:
        self.async_on_remove(self._watch.async_add_listener(self._handle))

    @callback
    def _handle(self) -> None:
        self.async_write_ha_state()

    @property
    def is_on(self) -> bool | None:
        return self._watch.result(self._place.key).get("on")

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        r = self._watch.result(self._place.key)
        attrs: dict[str, Any] = {
            "place": self._place.key,
            "alerts": r.get("alerts", []),
            "highest": r.get("highest"),
            "threshold": self._watch.threshold,
            "zones": r.get("zones"),
        }
        if r.get("reason"):
            attrs["reason"] = r["reason"]
        # item 351: shown whether or not they turn the place on (present only with the user's own keys)
        hz = self._watch.hazard_attributes(self._place.key)
        attrs.update(hz)
        return attrs
