"""Constants for Live Track Weather."""

from __future__ import annotations

DOMAIN = "live_track_weather"
VERSION = "0.1.0"

USER_AGENT = (
    f"LiveTrackWeather/{VERSION} "
    "(+https://github.com/StrausbergAutomationWorks/LiveTrackWeather)"
)

ALERTS_URL = "https://api.weather.gov/alerts/active"
REQUEST_TIMEOUT = 60

# One poll is about 100 KB on the wire (gzip; about 1.4 MB decoded), and NWS
# sends a new ETag on every response, so a conditional request never saves a
# byte (measured 2026-10-05). 180 s is about 50 MB a day; a warning polygon
# lives 30 to 60 minutes, so three minutes late is a small part of its life
# on a map that is not an alerting system.
CONF_SCAN_INTERVAL = "scan_interval"
DEFAULT_SCAN_INTERVAL = 180
MIN_SCAN_INTERVAL = 60
MAX_SCAN_INTERVAL = 900

# Polls that may fail in a row before the sensor goes unavailable. Until then
# the last good list is served, so a hiccup does not blank the map.
MAX_TRANSIENT_FAILURES = 3

# Files shipped in the component.
SHAPES_DIR = "www"
SHAPES_FILE = "nws_zones.json"  # shipped ONLY as nws_zones.json.gz, see __init__.py
COLOURS_FILE = "data/nws_hazard_colours.json"

ATTRIBUTION = "Data: US National Weather Service"
