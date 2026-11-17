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

# Places: is home, or a person, tracker or zone, inside an alert (Weather SSOT item 334; Lee 2026-11-16:
# a binary sensor "Alert at X"; on for any alert, a setting raises it by CAP severity; home watched by
# default, the user may switch it off and add people, device trackers or zones).
CONF_WATCH_HOME = "watch_home"
CONF_WATCH_ENTITIES = "watch_entities"
CONF_ALERT_THRESHOLD = "alert_threshold"
DEFAULT_WATCH_HOME = True
WATCH_DOMAINS = ("person", "device_tracker", "zone")
# NWS says which zones hold a point; the answer is kept and reused for any place within this distance of
# the point asked. A tracker that moves further is asked about again, at most once per alerts poll.
ZONES_URL = "https://api.weather.gov/zones"  # item 334's first lookup, replaced by POINTS_URL 2026-11-17
POINTS_URL = "https://api.weather.gov/points"
ZONES_REUSE_M = 1000
# A kept answer older than this is asked again (NWS reissues its zones about once a year).
ZONES_KEEP_S = 30 * 86400
ZONES_CACHE_MAX = 64
ZONES_STORE_KEY = f"{DOMAIN}.place_zones"

# Forecast at a watched place (Weather SSOT item 349; Lee 2026-11-17 01:55): NWS's gridpoint daily and hourly on US
# land and territories, MET Norway's Locationforecast elsewhere and on all water; one weather entity per place,
# "Forecast at X". MEASURED 2026-11-17: NWS's forecasts answer max-age up to 3,600 and 304 to If-Modified-Since;
# MET's Expires is about 30 min (MET_POINT_POLL_S below).
FORECAST_TICK_S = 300           # how often each place's forecast is looked at; fetched only when due
FORECAST_NWS_MIN_S = 900        # an NWS forecast is asked again after its max-age, but not sooner than this
FORECAST_NWS_MAX_S = 3600       # ... and not later than this
FORECAST_MOVE_GAP_S = 600       # a moving place is asked about a new spot at most this often

# Observed wind and temperature at a watched place (Weather SSOT item 350; Lee 2026-11-17 03:58): the nearest NWS
# station of any network, or airports only by option; four sensors per place. MEASURED 2026-11-17: a station's
# latest report is 4-5 KB with max-age up to 300 and answers 304 to If-Modified-Since; it reaches api.weather.gov
# 18-50 min after it was taken, so asking more often than OBS_POLL_S buys nothing. The stations list (29-142 KB) is
# cached for 24 h.
CONF_OBSERVE_AIRPORTS_ONLY = "observe_airports_only"
DEFAULT_OBSERVE_AIRPORTS_ONLY = False
OBS_POLL_S = 300
STATIONS_KEEP_S = 86400
OBS_LATEST_PARAMS = {"require_qc": "true"}   # plain /latest served empty copies of good reports (MEASURED)

# Files shipped in the component.
SHAPES_DIR = "www"
SHAPES_FILE = "nws_zones.json"  # shipped ONLY as nws_zones.json.gz, see __init__.py
COLOURS_FILE = "data/nws_hazard_colours.json"

ATTRIBUTION = "Data: US National Weather Service"

# Tropical cyclones (Weather SSOT item 302, contract D15).
NHC_URL = "https://www.nhc.noaa.gov/CurrentStorms.json"
EONET_URL = "https://eonet.gsfc.nasa.gov/api/v3/events/geojson?status=open&category=severeStorms"
# NHC answers max-age=300 and an ETag; between advisories it answers 304.
NHC_POLL_S = 300
EONET_POLL_S = 1800
# A source that keeps failing: its last good answer is kept this long, then
# dropped. NHC advises every 6 h; EONET's fixes are 6-hourly too.
NHC_KEEP_S = 2 * 3600
EONET_KEEP_S = 3 * 3600
# An EONET storm whose last fix is older than this is not drawn: EONET closes
# storms late (open storms with fixes 2.6 and 4.6 days old, 2026-10-28).
# MEASURED 2026-10-27/28 (Weather SSOT 2n): JTWC fixes are 6-hourly and EONET
# publishes them about 4.9 h after the fix time, so a live storm's last fix
# peaks near 10.4 h; one late fix reached 16.4 h. 24 h survives two missed
# publications in a row (about 22.9 h). Lee, 2026-10-28.
EONET_STALE_H = 24

# The SPC Day 1 categorical outlook (contract D16; Lee 2026-10-28). SPC answers max-age=120
# and an ETag; Day 1 is reissued five times a day.
SPC_DAY1_URL = "https://www.spc.noaa.gov/products/outlook/day1otlk_cat.lyr.geojson"
SPC_POLL_S = 300
SPC_ATTRIBUTION = "Severe weather outlook: NOAA Storm Prediction Center, spc.noaa.gov"
# D12 as amended for D16: a publisher with a lower shape_order is drawn beneath the others.
# The alerts carry none (0), so the outlook sits under them (Lee: "drawn under the alerts").
OUTLOOK_SHAPE_ORDER = -10

# MET Norway (Weather SSOT item 310; Lee 2026-10-28 17:04: MET's warnings as polygons beside the US
# ones, the sea-area forecasts as clickable polygons, a forecast dot at Longyearbyen, "for all areas they
# cover"). MET's terms (REPORT_metno_20261005.md 5, REPORT_metno_endpoints_20261028.md 3): identify
# the application (USER_AGENT above), honour Expires, send If-Modified-Since, spread requests, coordinates
# to 4 decimals, 20 requests a second for ALL installs together, back off on 403 and 429.
MET_BASE = "https://api.met.no/weatherapi"
MET_ALERTS_RSS = f"{MET_BASE}/metalerts/2.0/current.rss"
MET_ALERTS_CAP = f"{MET_BASE}/metalerts/2.0/current"
MET_SEA_URL = f"{MET_BASE}/textforecast/3.0/sea_en"
MET_COAST_URL = f"{MET_BASE}/textforecast/3.0/coast_en"
MET_POINT_URL = f"{MET_BASE}/locationforecast/2.0/compact"
# Measured 2026-10-28: the warning feed's Expires is 2-3 minutes after Last-Modified; the sea forecast's
# about 30, the coastal one's hours; a point forecast's 30.
MET_ALERTS_POLL_S = 300
MET_MARINE_POLL_S = 900
MET_COAST_EVERY_S = 1800
MET_POINT_POLL_S = 1800
# Each install adds up to this many seconds to its interval, once, so installs do not poll in step.
MET_JITTER_S = 60
# CAP files fetched per poll at most (a CAP never changes; a cold start with many warnings spreads out).
MET_CAP_PER_POLL = 25
# After a 403 or 429 nothing is asked of MET for this long.
MET_BACKOFF_S = 1800
# A marine forecast not refreshed for this long is no longer drawn.
MET_MARINE_KEEP_S = 24 * 3600
# One credit line for every MET entity (D4d: the credit before any full stop). CC BY 4.0 asks to say
# when the data were changed: rounded and recoloured.
MET_ATTRIBUTION = "Data from MET Norway (api.met.no), CC BY 4.0, modified"
# D12 as amended for D16: the warnings beside the US alerts (0); the marine forecasts beneath them.
MET_WARNINGS_SHAPE_ORDER = 0
MET_MARINE_SHAPE_ORDER = -5
# Forecast points: (name, latitude, longitude), 4 decimals. Lee 2026-10-28: Longyearbyen.
MET_POINTS = (("Longyearbyen", 78.2232, 15.6267),)

# KNMI radar for the Netherlands, relayed with the user's OWN key (Weather SSOT item 278, section 0 item 8;
# contract D13 "Relays"). The key is a KNMI Data Platform key for the WMS API (an Open Data API key is refused,
# measured 2026-10-05); it goes in the Authorization header. 1,000 requests an hour per key (X-Ratelimit-Limit).
# What the relayed area is and why one picture per frame: knmi.py.
CONF_KNMI_KEY = "knmi_wms_key"
KNMI_WMS = "https://api.dataplatform.knmi.nl/wms/adaguc-server"
KNMI_DATASET = "radar_reflectivity_composites"
# MEASURED 2026-10-28 (bin\ltw278_probe2.py, sheet bin\ltw278\sheet_styles.png): two layers, four styles.
# `Reflectivity`'s styles paint the whole radar disc; `radar/nearest` is white and greys. The look is Lee's pick.
KNMI_LAYER = "precipitation"
KNMI_STYLE = "precip-smooth-white-to-purple/bilinear"
# Frames every 5 minutes; the newest listed was 8.7 min old when measured.
KNMI_POLL_S = 300
KNMI_JITTER_S = 30
# This relay's own fuse: it needs at most 24 an hour (12 capabilities, 12 pictures). Beyond it, or with fewer
# than KNMI_RESERVE left on the key, it asks nothing until KNMI's reset.
KNMI_BUDGET_PER_H = 120
KNMI_RESERVE = 100
# A frame whose picture failed is not asked for again for this long.
KNMI_RETRY_S = 120
KNMI_RELAY_ID = "knmi"
KNMI_TILE_PATH = f"/api/{DOMAIN}/radar/knmi"
# CC BY 4.0 (the dataset's page, read 2026-10-28). Cut and resized here, so "modified".
KNMI_ATTRIBUTION = "Radar: KNMI, CC BY 4.0, modified"
