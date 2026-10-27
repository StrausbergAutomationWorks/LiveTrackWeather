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

from .const import COLOURS_FILE, DOMAIN, SHAPES_DIR, SHAPES_FILE
from .coordinator import WeatherCoordinator
from .storm_coordinator import StormCoordinator
from .shared_map_card import async_offer_map_card, async_withdraw_map_card

# ! A new platform needs a FULL Home Assistant restart, not a reload
# (06_MAP_CONTRACT.md D6a-0c).
PLATFORMS: list[Platform] = [Platform.SENSOR, Platform.GEO_LOCATION]

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
    return unloaded


async def async_remove_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """The entry was deleted. The domain's LAST entry withdraws the map card."""
    if not [e for e in hass.config_entries.async_entries(DOMAIN)
            if e.entry_id != entry.entry_id]:
        await async_withdraw_map_card(hass, DOMAIN)


async def _async_update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload when options change, so a new interval takes effect."""
    await hass.config_entries.async_reload(entry.entry_id)
