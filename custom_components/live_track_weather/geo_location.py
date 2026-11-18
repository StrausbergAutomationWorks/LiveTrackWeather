"""One geo_location entity per tropical cyclone on the map (contract D15).

! NO unique_id, by design (06_MAP_CONTRACT.md D1, Lee 2026-09-23): storms come
and go, and anything WITH a unique_id stays in the entity registry for good.
So no device_info either (it needs a unique_id; 05_SHARED_LESSONS.md A9).
The entity id comes from `suggested_object_id`, `storm_<ATCF id>`
(`geo_location.storm_ep222026`), or `storm_eonet_<n>` for an EONET storm whose
JTWC code is not known. A storm that leaves the sources is removed.
"""

from __future__ import annotations

from typing import Any

from homeassistant.components.geo_location import GeolocationEvent
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfLength
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.util.location import distance as ha_distance

from .const import DOMAIN, MET_ATTRIBUTION
from .met_coordinator import MetPointCoordinator
from .storm_coordinator import StormCoordinator


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    coordinator: StormCoordinator = hass.data[DOMAIN][f"{entry.entry_id}_storms"]
    manager = _StormEntities(hass, coordinator, async_add_entities)
    entry.async_on_unload(coordinator.async_add_listener(manager.update))
    manager.update()
    # MET Norway forecast points (Weather SSOT item 310): a dot that, clicked, shows the forecast.
    points: MetPointCoordinator = hass.data[DOMAIN][f"{entry.entry_id}_met_points"]
    pm = _StormEntities(hass, points, async_add_entities, key="points", factory=ForecastPoint)
    entry.async_on_unload(points.async_add_listener(pm.update))
    pm.update()
    # Earthquakes, M4.5 and up or felt (Weather SSOT item 352, contract D20)
    quakes = hass.data[DOMAIN][f"{entry.entry_id}_quakes"]
    qm = _StormEntities(hass, quakes, async_add_entities, key="quakes", factory=QuakeEvent)
    entry.async_on_unload(quakes.async_add_listener(qm.update))
    qm.update()


class _StormEntities:
    def __init__(self, hass: HomeAssistant, coordinator, add: AddEntitiesCallback,
                 key: str = "storms", factory=None) -> None:
        self.hass = hass
        self.coordinator = coordinator
        self.add = add
        self.key = key
        self.factory = factory or StormEvent
        self.entities: dict[str, GeolocationEvent] = {}

    @callback
    def update(self) -> None:
        records = {r["key"]: r for r in (self.coordinator.data or {}).get(self.key, [])}
        for key in [k for k in self.entities if k not in records]:
            entity = self.entities.pop(key)
            if entity.hass is not None:
                self.hass.async_create_task(entity.async_remove(force_remove=True))
        new = []
        for key, rec in records.items():
            if key in self.entities:
                self.entities[key].set_record(rec)
            else:
                entity = self.factory(rec)
                self.entities[key] = entity
                new.append(entity)
        if new:
            self.add(new)


class StormEvent(GeolocationEvent):
    _attr_should_poll = False
    _attr_source = DOMAIN
    _attr_unit_of_measurement = UnitOfLength.KILOMETERS
    # ! No `icon`: the card draws an icon in preference to `marker_label`, and the
    # storm's name is the label (D15; the look page showed the word "icon").

    def __init__(self, rec: dict[str, Any]) -> None:
        self._key = rec["key"]
        self._rec = rec

    @callback
    def set_record(self, rec: dict[str, Any]) -> None:
        self._rec = rec
        if self.hass is not None:
            self.async_write_ha_state()

    @property
    def suggested_object_id(self) -> str:
        """The entity id: storm_<key>. Not the name, which changes as a storm
        strengthens ("Tropical Storm Vance" to "Hurricane Vance")."""
        return f"storm_{self._key}"

    @property
    def name(self) -> str:
        return self._rec["name"]

    @property
    def latitude(self) -> float | None:
        return self._rec["lat"]

    @property
    def longitude(self) -> float | None:
        return self._rec["lon"]

    @property
    def distance(self) -> float | None:
        """The entity STATE, km from home. Never also an attribute."""
        if self.hass is None:
            return None
        return round(ha_distance(self.hass.config.latitude, self.hass.config.longitude,
                                 self._rec["lat"], self._rec["lon"]) / 1000, 1)

    @property
    def attribution(self) -> str | None:
        return self._rec["attrs"].get("attribution")

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        return {k: v for k, v in self._rec["attrs"].items() if k != "attribution"}


class ForecastPoint(StormEvent):
    """A MET Norway forecast point (Weather SSOT item 310): a dot labelled with the temperature; clicked, the card
    opens the entity, whose attributes are the forecast. ! NO unique_id, as for every geo_location here (D1)."""

    @property
    def suggested_object_id(self) -> str:
        return f"met_forecast_{self._key}"

    @property
    def attribution(self) -> str | None:
        return MET_ATTRIBUTION


class QuakeEvent(StormEvent):
    """An earthquake of the day, M4.5 and up or felt (Weather SSOT item 352, contract D20): a dot labelled with the
    magnitude; clicked, `marker_info` and a link to USGS's event page. ! NO unique_id (D1): quakes never recur."""

    _unrecorded_attributes = frozenset({"marker_info", "marker_links"})

    @property
    def suggested_object_id(self) -> str:
        return f"quake_{self._key}"
