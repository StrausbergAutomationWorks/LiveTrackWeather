"""Live Track Weather for Home Assistant.

US weather alerts for the shared Live Track map, from the National Weather
Service. Original work, not affiliated with NWS or NOAA.

The shapes the alerts name (every NWS county and zone, about 3.6 MB gzipped)
ship with each release in www/ and are served at a URL that changes when the
file does, so a browser downloads them once per release and caches them for a
month. The sensor's attributes say which shapes to fill and how.

! Only www/nws_zones.json.gz is shipped. A request for .../nws_zones.json is
answered with the .gz and Content-Encoding: gzip, by aiohttp's FileResponse,
which tries <path>.gz first when the client accepts gzip (read from
aiohttp 3.14.3 on HA 2026.9.4). Every browser accepts gzip; a client that
does not gets a 404.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from homeassistant.components.http import StaticPathConfig
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .const import CONF_KNMI_KEY, COLOURS_FILE, DOMAIN, SHAPES_DIR, SHAPES_FILE
from .coordinator import WeatherCoordinator
from .firemap_coordinator import AirSitesMap, FireMap, PointsView
from .knmi_relay import KnmiRelay, KnmiTileView
from .met_coordinator import (MetMarineCoordinator, MetPointCoordinator,
                              MetWarningsCoordinator)
from .outlook_coordinator import OutlookCoordinator
from .places_watch import PlaceWatch
from .storm_coordinator import StormCoordinator
from .shared_map_card import async_offer_map_card, async_withdraw_map_card
from . import usgs
from .usgs_coordinator import QuakeCoordinator, RiverCoordinator, StormReportCoordinator, VolcanoCoordinator

# ! A new platform needs a FULL Home Assistant restart, not a reload
# (06_MAP_CONTRACT.md D6a-0c).
PLATFORMS: list[Platform] = [Platform.SENSOR, Platform.GEO_LOCATION, Platform.BINARY_SENSOR, Platform.WEATHER]

HERE = Path(__file__).parent


def _read_static() -> tuple[str, dict]:
    """Hash of the shipped shape file, and the colour table."""
    gz = (HERE / SHAPES_DIR / (SHAPES_FILE + ".gz")).read_bytes()
    colours = json.loads((HERE / COLOURS_FILE).read_text(encoding="utf-8"))["events"]
    return hashlib.sha256(gz).hexdigest()[:12], colours


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    data = hass.data.setdefault(DOMAIN, {})
    if "shapes_url" not in data:
        # A route cannot be removed from HA's web server, so register it once
        # per run, not once per config entry setup (a reload sets up again).
        digest, colours = await hass.async_add_executor_job(_read_static)
        base = f"/{DOMAIN}/shapes/{digest}"
        await hass.http.async_register_static_paths(
            [StaticPathConfig(base, str(HERE / SHAPES_DIR), cache_headers=True)])
        data["shapes_url"] = f"{base}/{SHAPES_FILE}"
        data["colours"] = colours
    # LiveTrackMapCard, shipped in frontend/: served once per run at its own path (not the
    # shapes path above), offered, and the one dashboard resource row reconciled
    # (backlog 291). Never raises.
    await async_offer_map_card(hass, DOMAIN, HERE / "frontend")
    coordinator = WeatherCoordinator(hass, entry, data["colours"])
    await coordinator.async_config_entry_first_refresh()
    data[entry.entry_id] = coordinator
    # Tropical cyclones (D15). Its first refresh never raises: NHC or EONET being
    # down at start-up must not stop the alerts.
    storms = StormCoordinator(hass, entry)
    await storms.async_refresh()
    data[f"{entry.entry_id}_storms"] = storms
    # The SPC Day 1 outlook (D16). Never raises either.
    outlook = OutlookCoordinator(hass, entry)
    await outlook.async_refresh()
    data[f"{entry.entry_id}_outlook"] = outlook
    # MET Norway (Weather SSOT item 310): warnings, marine forecasts, forecast points. Never raise. Their
    # first refresh runs in the background: a cold start fetches one CAP file per warning (18 on
    # 2026-10-28), and set-up must not wait on MET.
    for suffix, cls in (("met_warnings", MetWarningsCoordinator), ("met_marine", MetMarineCoordinator),
                        ("met_points", MetPointCoordinator)):
        c = cls(hass, entry)
        data[f"{entry.entry_id}_{suffix}"] = c
        entry.async_create_background_task(hass, c.async_refresh(), f"{DOMAIN} {suffix} first refresh")
    # KNMI radar for the Netherlands (Weather SSOT item 278, D13 "Relays"): only with the user's own key.
    # The tile view is registered once per run (a route cannot be removed) and answers 404 with no relay.
    if "knmi_view" not in data:
        hass.http.register_view(KnmiTileView())
        data["knmi_view"] = True
    key = (entry.options.get(CONF_KNMI_KEY) or "").strip()
    if key:
        relay = KnmiRelay(hass, entry, key)
        data["knmi_relay"] = relay
        data[f"{entry.entry_id}_knmi"] = relay
        entry.async_create_background_task(hass, relay.async_refresh(), f"{DOMAIN} knmi first refresh")
    # The fire-and-smoke map (D19): fire detections and air-quality sites as point files, only with the user's
    # keys and regions. The view is registered once per run (a route cannot be removed).
    if "points_view" not in data:
        hass.http.register_view(PointsView())
        data["points_view"] = True
    for suffix, cls in (("fire_map", FireMap), ("air_sites_map", AirSitesMap)):
        if cls.wanted(entry):
            c = cls(hass, entry)
            data[f"{entry.entry_id}_{suffix}"] = c
            entry.async_create_background_task(hass, c.async_refresh(), f"{DOMAIN} {suffix} first refresh")
    # Earthquakes (Weather SSOT item 352, contract D20): markers, a point layer, ShakeMap lines; never raises, and its
    # first refresh runs in the background so set-up never waits on USGS.
    quakes = QuakeCoordinator(hass, entry)
    data[f"{entry.entry_id}_quakes"] = quakes
    entry.async_create_background_task(hass, quakes.async_refresh(), f"{DOMAIN} quakes first refresh")
    # Elevated volcanoes (item 352 step 2): markers, and places inside a threat-layer zone at Watch/Orange and up
    volcanoes = VolcanoCoordinator(hass, entry)
    data[f"{entry.entry_id}_volcanoes"] = volcanoes
    entry.async_create_background_task(hass, volcanoes.async_refresh(), f"{DOMAIN} volcanoes first refresh")
    # Rivers forecast into flood (item 352 step 3): markers only
    rivers = RiverCoordinator(hass, entry)
    data[f"{entry.entry_id}_rivers"] = rivers
    entry.async_create_background_task(hass, rivers.async_refresh(), f"{DOMAIN} rivers first refresh")
    # Storm reports (item 312, contract D21): a D19 point layer of NWS Local Storm Reports, the last 24 hours
    reports = StormReportCoordinator(hass, entry)
    data[f"{entry.entry_id}_storm_reports"] = reports
    entry.async_create_background_task(hass, reports.async_refresh(), f"{DOMAIN} storm reports first refresh")
    # Places (Weather SSOT item 334): home and any watched person, tracker or zone, each inside an alert or
    # not. Reads the alerts and MET warnings above; adds only NWS /zones lookups, kept in .storage.
    watch = PlaceWatch(hass, entry, coordinator, data[f"{entry.entry_id}_met_warnings"])
    # item 352: quakes near a place turn it on (usgs.ALERT_RULES)
    watch.add_source(quakes, lambda d, lat, lon: usgs.alert_records(d.get("events") or [], lat, lon))
    watch.add_source(volcanoes, lambda d, lat, lon: usgs.volcano_alert_records(d.get("elevated") or [],
                                                                               volcanoes.zones, lat, lon))
    await watch.async_start()
    data[f"{entry.entry_id}_places"] = watch
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(_async_update_listener))
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload. The map card is NOT withdrawn here: every restart and reload unloads, and that is
    not an uninstall (card SSOT 67.6); async_remove_entry does it."""
    unloaded = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unloaded:
        hass.data.get(DOMAIN, {}).pop(entry.entry_id, None)
        hass.data.get(DOMAIN, {}).pop(f"{entry.entry_id}_storms", None)
        hass.data.get(DOMAIN, {}).pop(f"{entry.entry_id}_outlook", None)
        for suffix in ("met_warnings", "met_marine", "met_points", "knmi", "places", "fire_map", "air_sites_map",
                       "quakes", "volcanoes", "rivers", "storm_reports"):
            hass.data.get(DOMAIN, {}).pop(f"{entry.entry_id}_{suffix}", None)
        hass.data.get(DOMAIN, {}).pop("knmi_relay", None)
    return unloaded


async def async_remove_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """The entry was deleted. The domain's LAST entry withdraws the map card."""
    if not [e for e in hass.config_entries.async_entries(DOMAIN)
            if e.entry_id != entry.entry_id]:
        await async_withdraw_map_card(hass, DOMAIN)


async def _async_update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload when options change, so a new interval takes effect."""
    await hass.config_entries.async_reload(entry.entry_id)
