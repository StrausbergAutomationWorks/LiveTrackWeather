# Live Track Weather

Weather for the Live Track map in Home Assistant:

* **US weather alerts** from the National Weather Service: warnings, watches,
  advisories and statements, filled translucent on the map in the NWS's own
  colours.
* **Tropical cyclones worldwide**: one marker per storm, with its past track
  and, from the National Hurricane Center, the forecast cone, the forecast
  track and the current wind extent.
* **Today's severe-weather outlook** from NOAA's Storm Prediction Center: where
  severe thunderstorms are expected today, from Marginal to High risk, in the
  Storm Prediction Center's own colours.
* **MET Norway's warnings and marine forecasts**, and a forecast dot at
  Longyearbyen, Svalbard.
* **KNMI's radar over the Netherlands**, with your own free KNMI key: sharper
  than the worldwide radar the map uses there otherwise.

Original work by StrausbergAutomationWorks. Not affiliated with, or endorsed
by, the National Weather Service, NOAA, the National Hurricane Center, the
Storm Prediction Center, the Joint Typhoon Warning Center, NASA, MET Norway or
KNMI.

**Status: in development. Not yet released.**

## What it adds

### US alerts

One sensor, `US alerts`. Its state is the number of active US alerts. Its
attributes carry the live list the map draws:

| Attribute | Holds |
|---|---|
| `shapes_url` | where the shape file is served (see below) |
| `zones` | `{shape key: event}`, one event per zone: the highest-priority one |
| `polygons` | storm-based warnings that carry their own polygon |
| `styles` | `{event: {color, priority}}` for the events drawn: the NWS's own values |
| `updated` | when NWS last updated the alert list |

These attributes change on nearly every poll and are deliberately **not
recorded** in Home Assistant's history. The count is.

No location is configured. Every active US alert is listed, and the map shows
the ones on screen.

### Tropical cyclones

Every active tropical cyclone in the world, with nothing to configure.

**One `geo_location` entity per storm**, `geo_location.storm_<id>`, where the id
is the storm's ATCF number (`geo_location.storm_ep222026`). A storm's entity
appears when the storm does and is removed when it is gone. Storms have no
unique ID on purpose, so they never pile up in the entity registry; the cost
is that they cannot be renamed in the UI. Their attributes:

| Attribute | Holds |
|---|---|
| `marker_label` | the storm's name (`Vance`) |
| `storm_class` | `Tropical Storm`, `Hurricane`, `Typhoon`, `Cyclone`, `Post-Tropical Cyclone` and so on |
| `storm_category` | `TD`, `TS`, `H1` to `H5` (Saffir-Simpson, by sustained wind), or `PT` for post-tropical and remnant lows |
| `max_wind_kmh` | sustained wind, km/h |
| `pressure_hpa` | minimum pressure (National Hurricane Center storms only) |
| `course_deg`, `speed_kmh` | movement (National Hurricane Center storms only; absent when stationary) |
| `last_seen` | the time of the advisory or fix |
| `advisory_number` | National Hurricane Center storms only |
| `storm_source` | `nhc` or `jtwc_eonet` |

**One sensor, `Tropical cyclones`.** Its state is the number of storms on the
map. Its attributes carry the shapes the map draws, in the same form as the
alerts' (`polygons`, `styles`); they change often and are **not recorded**.

| Shape | For | Colour |
|---|---|---|
| Forecast cone | National Hurricane Center storms | blue, translucent |
| Forecast track | National Hurricane Center storms | red line on a thin white line |
| Past track | every storm | black line on a thin white line |
| Winds of 34, 50 and 64 kt now | National Hurricane Center storms | yellow, orange, red, translucent |

Markers are coloured by category: depression blue, tropical storm teal,
categories 1 to 5 gold, orange, dark orange, red and magenta, post-tropical
grey.

**Where the storms come from.** The National Hurricane Center covers the
Atlantic and the eastern and central Pacific. Every other basin comes from the
Joint Typhoon Warning Center, as published by NASA's EONET; these storms get a
marker and a past track. Where both list a storm, the National Hurricane
Center's is used. EONET keeps storms open for days after their last fix, so a
storm whose last EONET fix is more than 24 hours old is not shown (fixes come
every 6 hours and reach EONET about 5 hours later). If a source cannot be
reached, the last good answer is kept for 2 hours (National Hurricane Center)
or 3 hours (EONET) before its storms leave the map.

### Severe weather outlook

The Storm Prediction Center's Day 1 categorical outlook: the risk of severe
thunderstorms from now until 12:00 UTC tomorrow, as areas from 1 Marginal
through 2 Slight, 3 Enhanced and 4 Moderate to 5 High. Nothing to configure.

**One sensor, `Severe weather outlook`.** Its state is the highest risk level
anywhere in the US today, 0 (none) to 5 (High), and it is recorded, so it can
drive an automation. Its attributes:

| Attribute | Holds |
|---|---|
| `risk` | the highest risk's name (`Slight Risk`), or none |
| `issued`, `valid_from`, `valid_to` | when the outlook was issued and the period it covers, UTC |
| `polygons`, `styles` | the areas the map draws and their colours (not recorded) |
| `shape_order` | `-10`: the map draws the outlook beneath the alerts |

The Storm Prediction Center's general-thunderstorm area is not drawn: it is not
a severe risk, and on an ordinary day it covers much of the country. A quiet day
draws nothing. An outlook whose period is over is not drawn, even if the Storm
Prediction Center cannot be reached.

### MET Norway: warnings, marine forecasts, forecast points

From the Norwegian Meteorological Institute's open API (`api.met.no`), for every
area it covers. Nothing to configure.

**`MET Norway warnings`:** every current warning for Norway's land, coast and
sea areas, the sea areas reaching the North Pole, drawn beside the US alerts in
MET's yellow, orange or red. The state is how many are drawn, recorded.
Click a warning on the map to read it: what is expected, the consequences, the
advice and the time it is valid (English). Warnings MET has cancelled (its green
level) are not drawn.

**`MET Norway marine forecasts`:** MET's text forecasts for its 56 sea areas
(the North Sea to the pole) and 39 coastal areas (Svalbard's included), each an
area on the map, beneath the warnings. Click an area to read its forecast, with
any wind, ice or polar-low warning; the sea areas add MET's synopsis. The state
is how many areas, recorded.

**Forecast points:** a dot at Longyearbyen, Svalbard, labelled with the
temperature. Click it and the card shows the forecast: now, then every six hours
for a day (attribute `marker_info`; also `forecast`, `temperature_c`, `wind_speed_kmh`, `wind_from_deg`,
`next_1h_conditions`, ...). It is a `geo_location` entity,
`geo_location.met_forecast_longyearbyen`, with no unique id, like the storms.

### KNMI radar over the Netherlands (optional)

The map's weather radar uses RainViewer over the Netherlands unless you give
this integration your own key for KNMI's radar (the Royal Netherlands
Meteorological Institute). KNMI's keyed service cannot be read by a browser on
its own, so Home Assistant relays it.

1. Register at KNMI's Data Platform (https://developer.dataplatform.knmi.nl/)
   and request a key for the **WMS** API. A key for the Open Data API does not
   work here.
2. In Home Assistant: Settings > Devices & services > Live Track Weather >
   Configure, and paste the key into **KNMI API key**. It is checked with KNMI
   once. Leave the field empty to stop using KNMI.

**`KNMI radar`** (`sensor.live_track_weather_knmi_radar`) then appears. Its
state is the newest radar frame's time (every 5 minutes); its `radar_relay`
attribute is what the map card reads. The card draws KNMI's radar for the map
tiles wholly inside the relayed area, about 2.1-7.7 E and 50.3-54.6 N (the
Netherlands, Belgium's north and Germany's edge, all inside KNMI's radar
range), and its usual sources around it.

The tiles are served by Home Assistant at `/api/live_track_weather/radar/knmi/`
and only to a signed-in user: the card asks Home Assistant to sign each tile's
address, so nobody else who can reach your Home Assistant spends your key.

### Alerts at your places

**`Alert at Home`** (`binary_sensor.live_track_weather_alert_at_home`) is on
while your Home Assistant's home location is inside an alert: a US alert from
the National Weather Service or a MET Norway warning. Its device class is
`safety`, so on means unsafe, and it is ready for automations.

In Settings > Devices & services > Live Track Weather > Configure you can:

* switch **Watch home** off;
* **also watch** people, device trackers and zones. Each gets its own
  `Alert at ...` sensor, named after it, which follows it as it moves. A
  tracker needs coordinates; one that only says it is home counts as home;
* choose **which alerts turn a place on**: any alert (the default:
  advisories, statements, watches and warnings), or only those NWS or MET
  rate Moderate, Severe or Extreme.

Each sensor lists every alert at its place in its `alerts` attribute, worst
first, whatever the setting: `event`, `severity`, `headline`, `onset`, `ends`,
`source` and `id` (a link to the alert). `highest` names the worst alert that
counts, and `zones` the NWS zones holding the place.

A place is inside an alert by the National Weather Service's own rule: a
storm-based warning with its own polygon (a tornado or flood warning, say)
counts only inside that polygon, not across the whole county it touches; any
other US alert counts in the zones it names. The zones holding a place come
from NWS itself, not from the simplified shapes the map draws, so a place on a
coast or a county line gets the answer NWS would give. A moving tracker's
zones are asked again after it has moved more than 1 km, at most once per
poll; until then it keeps those of its last spot.

#### Fire and smoke at your places (optional, your own keys)

With your own free keys, `Alert at ...` also turns on for fire and smoke near
the place, whatever the alert setting above:

* **Fire**, with a **NASA FIRMS MAP_KEY**
  (https://firms.modaps.eosdis.nasa.gov/api/map_key/): a satellite fire
  detection (NOAA-20 and NOAA-21 VIIRS, MODIS, Landsat) within the distance you
  set, 50 km by default: far enough to pack up and move. Detections reach Home
  Assistant 2 to 4 hours after the satellite passes, sometimes within minutes in
  the US; one detection is enough. Mills, refineries, gas flares, volcanoes and
  other standing heat sources are left out by NASA's own classification of the
  place's area (FIRMS's standard product, which runs about 3.5 months behind),
  not by how often a spot repeats, so a wildfire burning for days is not
  hidden; one within about 2 km of a listed source would be. A source newer
  than that classification still turns the place on.
* **Smoke**, with an **AirNow API key** (https://docs.airnowapi.org/): the
  closest fine-particle (PM2.5) monitor within 50 miles at or above the AQI you
  set, 90 by default: just before AQI 101, where breathing becomes a problem
  for people with asthma or lung disease. US places only (AirNow also covers
  parts of Canada and Mexico).

The sensor shows `fires_near`, `nearest_fire_km`, `fires_within_km`,
`fires_checked` (when FIRMS last answered; until then the counts are unknown)
and `standing_sources_listed`, and `pm25_aqi`, `pm25_site`, `pm25_observed` and
`smoke_aqi_threshold`, whether or not they turn it on; a fire or smoke that
does is listed in `alerts` with `km` or `aqi`. NASA advises against using its
fire detections alone for decisions on the ground: follow evacuation orders.

### Fire detections and air quality on the map (optional, your own keys)

Choose regions under **Fire detections and air-quality sites on the map** (the
lower 48 states and Hawaii, Alaska, Canada, the whole world; none by default)
and the map gets up to two more layers, each with its own checkbox:

* **Fire detections** (`sensor.live_track_weather_fire_detections`, needs the
  FIRMS key): every satellite fire detection of the last 24 hours in those
  regions, NOAA-20 and NOAA-21 VIIRS, as small red dots, solid until they are
  24 hours old. Standing heat sources are left out as for the places above:
  NASA's standard-product classification for each chosen region (30 days of it;
  for the whole world one 5-day window). Click a dot for when, which satellite,
  its fire radiative power and NASA's confidence.
* **Air quality sites** (`sensor.live_track_weather_air_quality_sites`, needs
  the AirNow key; the US and Canada only): every fine-particle (PM2.5) monitor
  reporting, coloured by its AQI in the EPA's colours, refreshed each hour.
  Click one for the site, its agency, the AQI and the hour.

A sensor's state is how many points it publishes; the points themselves travel
as one file the map fetches with your sign-in (`points_url`), so thousands of
them cost the map no more than the ones on screen. Needs a Live Track map card
that draws points (contract D19).

### Earthquakes

Every earthquake USGS lists for the last 24 hours, worldwide (its `all_day`
feed, about 240 a day, most in California, Nevada and Alaska):

* **Markers** for M4.5 and up, and for any quake people reported feeling,
  labelled with the magnitude and coloured by it (`geo_location.quake_<USGS
  id>`). Click one for the time, depth, felt reports, ShakeMap's strongest
  shaking, the PAGER alert and USGS's event page. A quake's "tsunami flag" is
  USGS saying NOAA's tsunami centres assess quakes of that size and place; it
  is not a warning (those come from NOAA, tsunami.gov).
* **Earthquakes** (`sensor.live_track_weather_earthquakes`): every other quake
  of the day as a small dot (and quarry blasts and explosions in grey), on one
  layer with its own checkbox. Set **Smallest earthquake on the map's point
  layer** in the options to leave out the dots below a magnitude; the markers
  stay. Its state is how many dots it publishes; `quakes_today` counts them
  all.
* **Earthquake shaking** (`sensor.live_track_weather_earthquake_shaking`):
  USGS ShakeMap's intensity lines for the day's biggest quakes, those whose
  ShakeMap reaches strong shaking (intensity VI) or of magnitude 6.0 and up, at
  most the five largest; click a line for its intensity.

`Alert at ...` turns on for a quake of **M4.0 or more within 50 km** of the
place, **M5.0 within 150 km**, **M6.0 within 300 km** or **M7.0 within 600 km**
(from the epicentre), about where USGS's "Did You Feel It?" reports show light
shaking or stronger, whatever the alert setting; it stays on while the quake is
in USGS's 24-hour feed, and is listed in `alerts` with its distance (`km`).
Automatic solutions are revised by USGS, and a quake can move, change size or
be deleted.

### Elevated volcanoes

Every US volcano the USGS Volcano Hazards Program lists as elevated (alert level
Advisory or aviation colour code Yellow and up, from its HANS notices) gets a
marker in its colour code, labelled with its name
(`geo_location.volcano_<number>`). Click one for its alert level and colour code,
since when, the observatory's synopsis and links to the notice and the volcano's
page. The alert level speaks to people on the ground, the colour code to
aircraft.

`Alert at ...` turns on while the place is inside the hazard zone of a volcano
at **Watch or Orange and up** (either the alert level or the colour code),
whatever the alert setting. The zones are USGS's National Volcanic Threat Layer
(2024, CC0): for 161 US volcanoes, the area near the vents that lava, pyroclastic
flows, ballistics, lahars and heavy ashfall could reach, and for some Cascade and
Alaska volcanoes the distal lahar paths down their valleys. They ship with the
integration (about 93 KB), so no location is sent for them. Ash carried further
downwind is covered by the National Weather Service's Ashfall Advisories and
Warnings, which are US alerts above.

### A forecast for each place

Each watched place also gets a weather entity, **`Forecast at Home`**
(`weather.live_track_weather_forecast_at_home`) and `Forecast at ...` for each
person, tracker or zone you watch. It follows its place and works with every
weather card and with `weather.get_forecasts`: daily, twice-daily (day and
night) and hourly.

* On US land and territories it is the **National Weather Service's** own
  forecast for the place's 2.5 km grid: seven days of day and night periods,
  each with NWS's written forecast (`detailed_description`), and hourly for
  six and a half days with humidity and dew point. The daily forecast pairs
  each day with the night after it (high and low); wind speed is the upper end
  of NWS's range.
* Everywhere else, **and on all water** (NWS publishes no forecast for lakes or
  the sea), it is **MET Norway's** Locationforecast: hourly for about two and a
  half days, then every six hours to about ten days, with pressure and cloud
  cover.
  Its days and nights are counted in solar time (longitude ÷ 15 hours from UTC),
  as MET gives no time zone.

The entity changes source as its place moves (a boat leaving harbour, a camper
crossing into Canada). Its current values are the forecast for this hour, not a
measurement. Attributes: `source`, `forecast_updated` (when the forecaster last
changed it; NWS offices update at their own pace), `grid` (the NWS grid, e.g.
`LOT/76,73`) and `place`. Units are Celsius, km/h, mm and hPa; Home Assistant
shows them in yours.

### Measured wind and temperature at each place

Each watched place in the US also gets four sensors with what the nearest
National Weather Service station last measured: **`Wind at Home`**,
**`Wind gust at Home`**, **`Wind direction at Home`** and
**`Temperature at Home`** (`sensor.live_track_weather_wind_at_home` and so on),
and the same for each person, tracker or zone you watch. They suit an
automation that rolls the awning in on a gust.

* The station is the nearest one NWS lists for the place, of any network:
  airports, fire-weather and state road stations, and volunteer stations,
  which are often much closer to a campground than the nearest airport. The
  option **Measured wind and temperature from airport stations only** uses
  airports alone.
* If the nearest has nothing recent (it stopped reporting, its report is empty,
  or NWS has no report for it), the next is asked, up to three. Wind speed,
  gust and direction always come from one station's report; temperature may
  come from another (a station's thermometer can be out while its wind still
  reports).
* A sensor is **unavailable** when no report younger than two hours has its
  value. Reports reach NWS's service 20 to 50 minutes after they are taken, so
  "now" is never quite now; `age_min` says how old the value is.
* **Gust** is unknown when the station reported no gust: airports report one
  only while it is gusting.
* Attributes: `station`, `station_name`, `provider` (the network), `distance_km`
  (from the place), `observed`, `age_min` and `place`. Units are km/h, degrees
  and Celsius; Home Assistant shows them in yours.
* Outside the US, and on open water far offshore, NWS lists no station and the
  sensors are unavailable. On a lake or near the coast the nearest station is
  usually on land; `distance_km` says how far.

## The alert shapes

Alerts name NWS counties and forecast, marine, offshore and fire zones. Their
outlines (11,651 shapes, simplified to about 500 m) ship with each release as
`www/nws_zones.json.gz`, about 3.6 MB, and are served by Home Assistant at a
URL that changes with the file, so a browser downloads them once per release.

`tools/build_shapes.py` rebuilds that file from the NWS shapefiles
(https://www.weather.gov/gis/); the file records the edition and the hash of
each source zip. `tools/build_colours.py` rebuilds the colour table from the
NWS hazard map page (https://www.weather.gov/help-map).

## Map card

The alerts and the storms are drawn by [LiveTrackMapCard](https://github.com/StrausbergAutomationWorks/LiveTrackMapCard)
(`custom:live-track-map-card`), the one map every Live Track integration
renders on. It fills each alert's zones and counties translucent in the NWS
colour, draws storm-based warnings by their own polygon, and carries the
weather radar overlay.

**The card is installed with the integration.** This integration carries a
released copy of the card, serves it, and registers it as a dashboard resource
when Home Assistant starts; there is nothing to download or copy into `www`.
Every Live Track integration does the same, and they keep exactly one resource
row between them: the highest card version any of them carries, never a
downgrade. A card you installed through HACS is left alone. Removing this
integration hands the row to another Live Track integration, or removes it if
none is left. See the card's README, section
[Live Track](https://github.com/StrausbergAutomationWorks/LiveTrackMapCard#live-track).

If your dashboards' resources are set in YAML (`lovelace: resource_mode: yaml`),
nothing can be registered for you. A Repairs issue then gives the exact line to
add; it looks like this, with the integration's own address in place of the
placeholders:

```yaml
lovelace:
  resource_mode: yaml
  resources:
    - url: /live_track_weather/map-card/<12 hex>/live-track-map-card.js?v=<version>&h=<12 hex>
      type: module
```

If the integration's files are removed (through HACS, say) while it is still
set up, and no other Live Track integration is installed, nothing is left to
tidy the row: remove it in Settings > Dashboards > Resources. To install the
card by hand instead, follow the card's README; the resource row of a
hand-installed copy under `/local/` is pointed at an integration's copy only
when that copy is a newer release.

**The alerts, the outlook and the storms' shapes need no entity filter.** Their
sensors are not `geo_location` entities, so auto-entities does not give them to the card:
the card finds them on its own, as any entity whose `zones` is a mapping and
that carries a `shapes_url` string or a `polygons` list. Put the card on a
dashboard and they appear. The card options are
`shape_layers` (`auto`, the default, for every publisher found; `false` for
none; or a list naming the entities with your own label) and `shape_style` for
opacity and outline. The alerts get a checkbox in the layer control at the
map's top right, ticked by default; each viewer's choice is kept in their own
browser. The NWS credit appears in the map's attribution line while alerts are
shown. See the card's README, section
[Shapes on the map](https://github.com/StrausbergAutomationWorks/LiveTrackMapCard#shapes-on-the-map).

**The storm markers are `geo_location` entities**, so they reach the card the way
every Live Track marker does, through the dashboard's `geo_location` filter. Each
is a disc in its category's colour with the storm's name on it, drawn beneath
every other marker; a long name runs past the disc. Hovering shows the storm's
class and name, its wind and pressure, its movement, and its source. The
`Tropical cyclones` checkbox in the layer control shows and hides the cones,
tracks and wind areas; the markers stay. Each source's credit appears in the
map's attribution line while its storms are shown.

**The outlook** has its own checkbox, `Severe weather outlook`, ticked by default,
and is drawn beneath the alerts and the storms, so warnings stay on top. Its
credit appears in the attribution line while it is shown.

**MET Norway's warnings and marine forecasts** each have their own checkbox, ticked
by default; the marine forecasts are drawn beneath the warnings. Both are
clickable: the card opens the area's text when one is clicked (LiveTrackMapCard
`0.1.1` or later; an older card draws them without the text). MET's credit
appears in the attribution line while either, or the Longyearbyen dot, is shown.

**The weather radar** is the card's own overlay (`weather_radar`, on by
default, with its own checkbox). It needs nothing from this integration; the
card picks the sharpest source for each tile. With a KNMI key, the card finds
the `KNMI radar` sensor by its `radar_relay` attribute and uses it over the
Netherlands; without one, or whenever the relay has no current frame, it uses
its other sources there. See the card's README, section
[Weather radar](https://github.com/StrausbergAutomationWorks/LiveTrackMapCard#weather-radar).

Other map cards do not draw the alerts or the storms' shapes; any map card that
shows `geo_location` entities shows the storm markers.

## Data use

* **Alerts:** polls `https://api.weather.gov/alerts/active` every 180 seconds by
  default (adjustable, 60 to 900), about 100 KB per poll.
* **National Hurricane Center:** `https://www.nhc.noaa.gov/CurrentStorms.json`
  every 5 minutes, asking only for a changed file (5 to 9 KB when it has
  changed, nothing otherwise); each storm's cone, track and wind files once per
  advisory, and its past track when the advisory changes.
* **NASA EONET:** open severe storms every 30 minutes, about 120 KB.
* **Storm Prediction Center:** the Day 1 categorical outlook every 5 minutes,
  asking only for a changed file (about 5 KB when it has changed).
* **MET Norway** (`api.met.no`), each asking only for a changed file and each
  interval a minute longer at random per install, as MET asks: the warning list
  every 5 minutes (about 17 KB when changed) and each warning's CAP file once
  (5 to 9 KB); the sea-area forecasts every 15 minutes and the coastal ones every
  30 (about 115 and 37 KB when changed); the Longyearbyen forecast every 30
  minutes (about 40 KB). If MET answers 403 or 429, nothing is asked of it for
  30 minutes. Each request names this integration in its User-Agent, as MET's
  terms require, and sends your Home Assistant's IP address to MET in Norway.
* **KNMI** (only with your key, `api.dataplatform.knmi.nl`): the radar's list
  of frames every 5 minutes (about 14 KB), and one picture of the relayed area
  per 5-minute frame (about 20 KB dry, more in rain), and only when a map is
  showing it: at most about 24 requests an hour, however many browsers have
  the map open, of the 1,000 an hour KNMI allows a key. If KNMI answers 429,
  or fewer than 100 requests are left on the key, nothing is asked until
  KNMI's hour resets. Each request carries your key.
* **Your places (alerts, forecasts and measured weather):** to learn a watched
  place's NWS zones, forecast grid and weather stations, its location is sent
  to the National Weather Service (`https://api.weather.gov/points/`),
  rounded to 4 decimals (about 11 m): your home's once, then again only every
  30 days; a moving person or tracker's when it has moved more than 1 km, at
  most once per poll. The
  answers are kept in Home Assistant (`.storage/live_track_weather.place_zones`).
  The alerts are the ones already polled above. Each place's forecast: on US
  land, NWS's daily and hourly forecast for its grid (about 15 and 165 KB),
  asked again when NWS says it may have changed (at most hourly, at least every
  15 minutes apart, and only for a changed file); elsewhere and on water, MET
  Norway's forecast for the place (about 40 KB, every 30 minutes and a
  random minute, only for a changed file), which sends the place's location,
  rounded to 4 decimals, to MET in Norway. A moving place's forecast is asked
  for a new spot at most every 10 minutes. Each US place's measured weather:
  the list of NWS stations for its grid (30 to 140 KB, once a day), then the
  nearest station's latest report (about 5 KB, every 5 minutes, only for a
  changed file), and the next station's, up to three, only while wind or
  temperature is still missing. These name stations, not your location.
  Switch **Watch home** off and watch nothing else, and no location is sent.
* **NASA FIRMS** (only with your key, `firms.modaps.eosdis.nasa.gov`): for
  each place, a box around it as wide as the fire distance (rounded to 3
  decimals, so it shows the place to within the box) with your key, four
  requests every 15 minutes (each a few hundred bytes to a few KB); once a
  month or after a move of half the distance, up to 12 requests for its
  standing heat sources and one for the product dates. Your key allows 5,000
  requests in 10 minutes.
* **AirNow** (only with your key, `www.airnowapi.org`): each place's location,
  rounded to 4 decimals, with your key, every 30 minutes (about 1 KB).
* **The fire and air-quality map layers** (only with a region chosen): every
  30 minutes, NASA FIRMS's public 24-hour VIIRS files for those regions, two
  per region, asked again only when changed (the whole world's are about 5 MB
  each, the US's about 150-200 KB); once a month, NASA's standard product for
  each region's standing heat sources with your FIRMS key (about 120 of your
  5,000 transactions for the US, 360 for the world, the world's answers about
  28 MB each), kept in `.storage/saw_firms_static_cells`; and AirNow's hourly
  PM2.5 readings for the regions' boxes with your AirNow key (about 340 KB for
  the lower 48). Nothing about your location is sent for these.
* **USGS earthquakes** (`earthquake.usgs.gov`): the `all_day` feed every 5
  minutes (about 170 KB, less on the wire); for each quake whose ShakeMap is
  drawn, its detail file (about 60 KB) once per revision and its intensity
  lines (about 50 KB) once. Nothing about your location is sent.
* **USGS volcanoes** (`volcanoes.usgs.gov`): the elevated volcanoes and their
  CAP notices every 10 minutes (2 to 3 KB each), and the list of US volcanoes
  (about 170 KB) once a day. Nothing about your location is sent.

The National Weather Service, the National Hurricane Center, the Storm
Prediction Center, the Joint Typhoon Warning Center, NASA and the US Geological Survey are US Government
agencies; their data are works of the US Government.

MET Norway's data are licensed under the Norwegian Licence for Open Government
Data (NLOD) 2.0 and Creative Commons Attribution 4.0; this integration rounds the
areas' coordinates and recolours the warnings. Not made or endorsed by MET Norway.

KNMI's radar data are licensed under Creative Commons Attribution 4.0; this
integration cuts and resizes KNMI's pictures into map tiles. Not made or
endorsed by KNMI.

## Licence

MIT. See `LICENSE`.
