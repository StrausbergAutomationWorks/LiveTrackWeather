# Live Track Weather

**English** · [Deutsch](README.de.md) · [Français](README.fr.md) · [Nederlands](README.nl.md) · [简体中文](README.zh-Hans.md) · [Español](README.es.md) · [Italiano](README.it.md) · [Dansk](README.da.md) · [Kalaallisut](README.kl.md) · [All languages](#languages)

**Weather alerts, storms, earthquakes, floods, wildfires, radar and live weather
for Home Assistant, on one map.** Live Track Weather puts US National Weather
Service warnings, hurricanes and typhoons, severe-storm outlooks, earthquakes,
volcanoes, river floods, storm and snow reports, wildfire and smoke data, MET
Norway warnings and Svalbard weather stations on your Home Assistant map, and
watches your home, your family's phones and your camper for danger.

> **Live Track Weather is one module of Live Track**, a family of Home
> Assistant integrations that draw everything that moves, and the weather it
> moves through, on one shared map: aircraft, ships, trains, and now weather.
> Install it on its own, or beside the other modules
> ([list below](#part-of-live-track-the-other-modules)).

**Status: 0.1.0, the first release.** Added to the Marketplace by link
([below](#install-it-step-by-step)); it is not in the Marketplace's catalog yet.

Original work by StrausbergAutomationWorks. Not affiliated with, or endorsed
by, the National Weather Service, NOAA, the National Hurricane Center, the
Storm Prediction Center, the Joint Typhoon Warning Center, NASA, the US
Geological Survey, the EPA, MET Norway, KNMI or GeoNames.

> ⚠ **Not an emergency alerting system.** It shows public data, a few minutes
> late at best. For warnings that protect lives, use your phone's emergency
> alerts, a NOAA Weather Radio and your local authorities, and follow
> evacuation orders.

---

## Contents

1. [Everything it does](#everything-it-does)
2. [Part of Live Track: the other modules](#part-of-live-track-the-other-modules)
3. [Before you start](#before-you-start)
4. [Install it, step by step](#install-it-step-by-step)
5. [Set it up, step by step](#set-it-up-step-by-step)
6. [Free keys that switch on more, step by step](#free-keys-that-switch-on-more-step-by-step)
7. [Put the map on a dashboard](#put-the-map-on-a-dashboard)
8. [Use it in automations](#use-it-in-automations)
9. [Everything on the map, in detail](#everything-on-the-map-in-detail)
10. [Everything at your places, in detail](#everything-at-your-places-in-detail)
11. [All the entities it creates](#all-the-entities-it-creates)
12. [What it sends and downloads](#what-it-sends-and-downloads)
13. [Languages](#languages)
14. [Credits and licences](#credits-and-licences)
15. [Keywords](#keywords)

---

## Everything it does

### On the map, with nothing to set up

| What | Where | From |
|---|---|---|
| **Weather alerts**: warnings, watches, advisories and statements, filled translucent in the Weather Service's own colours | the whole US, its coasts and waters | National Weather Service |
| **Tornado, severe thunderstorm, flash flood and other storm-based warnings**, drawn by their own polygon | the US | National Weather Service |
| **Hurricanes, tropical storms, typhoons and cyclones**: a marker per storm, the forecast cone, the forecast track, the wind field and the past track | the whole world | National Hurricane Center; Joint Typhoon Warning Center via NASA EONET |
| **Today's severe-weather outlook**: Marginal to High risk of severe thunderstorms | the US | NOAA Storm Prediction Center |
| **Earthquakes** of the last 24 hours: markers for the big and the felt ones, dots for the rest, shaking lines for the strongest | the whole world | US Geological Survey |
| **Elevated volcanoes**, in their aviation colour code | US volcanoes | USGS Volcano Hazards Program |
| **Rivers in flood or forecast to flood**, minor, moderate or major | US river and tide gauges | NOAA National Water Prediction Service |
| **Storm reports**: tornadoes, funnel clouds, hail, damaging wind, floods | the US | NWS Local Storm Reports |
| **Winter reports**: snow totals, blizzards, sleet, freezing rain and ice storms, extreme cold, avalanches, ice jams | the US | NWS Local Storm Reports |
| **MET Norway's weather warnings**, beside the US ones | Norway, its seas, Svalbard | MET Norway |
| **Marine forecasts** for 56 sea areas and 39 coastal areas, click to read | the North Sea to the North Pole | MET Norway |
| **A forecast dot at Longyearbyen**, Svalbard, click for the forecast | Svalbard | MET Norway |
| **Weather radar** and **lightning**: the sharpest radar for what is on screen | the world | drawn by the Live Track map card |

### At your places, with nothing to set up

"Your places" are your home, and any person, phone, device tracker or zone you
choose to watch. Each place gets:

* **Alert at …**: on while the place is inside a weather alert, a nearby
  strong earthquake or an erupting volcano's hazard zone. Ready for
  automations: turn on the lights, send a phone notification, close the
  garage.
* **Forecast at …**: a full weather forecast that follows the place as it
  moves, for every weather card on your dashboard. National Weather Service
  forecasts on US land; MET Norway's everywhere else, and on all water.
* **Wind at …**, **Wind gust at …**, **Wind direction at …** and
  **Temperature at …**: what the nearest weather station measured. Roll the
  awning in when it gusts.
* **Elevation at …** and **Depth at …**: the height of the ground, and the
  depth of the water under a boat.

### Switched on by your own free key or account

| Free key or account | What it adds |
|---|---|
| **NASA FIRMS** map key | wildfire alerts near your places; every satellite fire detection on the map |
| **AirNow** API key | wildfire smoke and air quality (PM2.5 AQI) alerts at your US places; every air-quality monitor on the map |
| **KNMI** API key | sharper radar over the Netherlands |
| **GeoNames** username | measured wind and temperature outside the US, from the nearest airport; the sea's name and water-or-land for depth |
| **MET Norway Frost** client ID | every weather station in Svalbard and Jan Mayen on the map; measured wind and temperature at your places in Norway and Svalbard |

Each takes a few minutes to get: [step by step below](#free-keys-that-switch-on-more-step-by-step).

---

## Part of Live Track: the other modules

Live Track is a set of Home Assistant integrations, one per kind of moving
thing, all drawn on the same map card. Each works on its own; together they
make one live picture. They share the map card and a Python library
([saw-livetrack](https://github.com/StrausbergAutomationWorks/LiveTrackCore)),
so installing another one adds no requests to a source another already reads.

| Module | What it puts on the map | Status |
|---|---|---|
| [Live Track Aircraft](https://github.com/StrausbergAutomationWorks/LiveTrackAircraft) | aircraft overhead from ADS-B, with routes and type icons | released |
| [Live Track Ships](https://github.com/StrausbergAutomationWorks/LiveTrackShips) | ships and boats from AIS, near you or anywhere | released |
| [Live Track Commuter Rail](https://github.com/StrausbergAutomationWorks/LiveTrackCommuterRail) | commuter trains in North America, Europe and Australia | released |
| [Live Track Intercity Rail](https://github.com/StrausbergAutomationWorks/LiveTrackIntercityRail) | intercity and long-distance trains in North America, Europe and Australia | released |
| [Live Track SALT](https://github.com/StrausbergAutomationWorks/LiveTrackSALT) | immigration and federal law-enforcement aircraft and vessels, from public lists | released |
| **Live Track Weather** | weather, storms and natural hazards (this module) | released |
| Live Track Stations | departure boards and "time to leave" alerts for every station | planned |
| Live Track Satellites | satellites passing overhead | planned |
| Live Track Freight Trains | freight and work trains where railways publish them | planned |
| Live Track Transit | city buses, trams, ferries and metro | planned |
| Live Track Intercity Buses | intercity and regional coaches | planned |
| Live Track Commuter Buses | commuter buses | planned |
| [LiveTrackMapCard](https://github.com/StrausbergAutomationWorks/LiveTrackMapCard) | the shared map card every module draws on | released, installed with each module |

Everything is free and open source. Nothing is held back for sponsors.

---

## Before you start

* **Home Assistant** 2026.11 or later.
* **The Marketplace** (HACS) in your Home Assistant, to install and update it
  the easy way. Without it you can copy the files by hand.
* **Internet access** for Home Assistant: everything comes from public weather
  services.
* **Optional: auto-entities** from the Marketplace, to put the storm,
  earthquake and station markers on the map (see
  [Put the map on a dashboard](#put-the-map-on-a-dashboard)). The alerts and
  shapes appear without it.
* Nothing to pay and no account needed for the basics. The free keys above are
  optional.

---

## Install it, step by step

### From the Marketplace (recommended)

Live Track Weather is not in the Marketplace's catalog yet. Add it by its link:

1. In Home Assistant, open **Settings → Marketplace** (HACS).
2. Choose **Add from link** (or the three-dot menu → **Custom repositories**).
3. Enter `StrausbergAutomationWorks/LiveTrackWeather`. If asked for the type,
   choose **Integration**.
4. Find **Live Track Weather** in the list and choose **Download** or
   **Install**.
5. **Restart Home Assistant**: **Settings → System → Repairs** offers the
   restart, or use **Settings → System → Restart**.

### By hand

1. Download the source code of the
   [latest release](https://github.com/StrausbergAutomationWorks/LiveTrackWeather/releases/latest).
2. Copy its `custom_components/live_track_weather` folder into the
   `custom_components` folder of your Home Assistant configuration folder
   (create `custom_components` if it is not there).
3. Restart Home Assistant.

---

## Set it up, step by step

1. Open **Settings → Devices & services**.
2. Choose **Add integration** (bottom right) and search for
   **Live Track Weather**.
3. Choose **Submit**. There is nothing to type: one Live Track Weather covers
   the whole world.

That is all. Alerts, storms, earthquakes, volcanoes, floods, storm reports and
MET Norway's warnings start appearing within a few minutes, and your home is
watched: **Alert at Home**, **Forecast at Home**, **Wind at Home**,
**Temperature at Home**, **Elevation at Home** and **Depth at Home**.

### Change what it watches: the options

Open **Settings → Devices & services → Live Track Weather → Configure**
(the cog). Every option, in plain words:

| Option | What it does | Default |
|---|---|---|
| **Seconds between polls** | how often the US alert list is fetched, 60 to 900 seconds | 180 |
| **Watch home** | your home gets the "… at Home" sensors and forecast; switch off to drop them | on |
| **Also watch these people, device trackers or zones** | each gets its own "Alert at …", "Forecast at …", wind, temperature, elevation and depth, and they follow it as it moves. Pick a family member's phone, a camper's tracker, a holiday home zone | none |
| **Alerts that turn a place on** | any alert (advisories and statements included), or only Moderate, Severe or Extreme ones. Every alert is still listed in the sensor | any alert |
| **Measured wind and temperature from airport stations only** | off: the nearest station of any kind (often closer to a campground); on: airports only | off |
| **NASA FIRMS MAP_KEY** | fire alerts and fire detections (see [free keys](#free-keys-that-switch-on-more-step-by-step)) | empty |
| **A fire counts within** | how close a fire must be to turn a place on, 5 to 150 km | 50 km |
| **AirNow API key** | smoke alerts and air-quality sites | empty |
| **Smoke counts from PM2.5 AQI** | the air-quality index that turns a place on | 90 |
| **Fire detections and air-quality sites on the map** | which regions to draw: lower 48 states and Hawaii, Alaska, Canada, the whole world (fires only) | none |
| **Smallest earthquake on the map's point layer** | leaves out the small earthquake dots below a magnitude; the markers stay | empty: every quake |
| **KNMI API key** | sharper radar over the Netherlands | empty |
| **GeoNames username** | weather outside the US, sea names | empty |
| **MET Norway Frost client ID** | Svalbard and Jan Mayen stations; measured weather in Norway | empty |

Each key is checked once when you enter it, and you are told if it does not
work. Leave a field empty to switch that part off.

---

## Free keys that switch on more, step by step

All of these are free and personal: each person who installs Live Track Weather
gets their own. Paste each into **Settings → Devices & services → Live Track
Weather → Configure**.

### NASA FIRMS (wildfires)

1. Open <https://firms.modaps.eosdis.nasa.gov/api/map_key/>.
2. Enter your email address and request a **MAP_KEY**. It arrives by email.
3. Paste it into **NASA FIRMS MAP_KEY**, and set **A fire counts within** if
   50 km is not right for you.
4. To see fires on the map, also tick a region under **Fire detections and
   air-quality sites on the map**.

### AirNow (smoke and air quality, US)

1. Open <https://docs.airnowapi.org/> and choose **Request an AirNow API
   Account**.
2. Confirm the email, sign in, and copy your **API key** from your account
   page.
3. Paste it into **AirNow API key**.

### KNMI (radar over the Netherlands)

1. Register at the KNMI Data Platform, <https://developer.dataplatform.knmi.nl/>.
2. Request a key for the **WMS** API. (A key for the Open Data API does not
   work here.)
3. Paste it into **KNMI API key**. The map then uses KNMI's radar over the
   Netherlands; without it, RainViewer's.

### GeoNames (weather outside the US)

1. Create a free account at <https://www.geonames.org/login>.
2. Open the confirmation email GeoNames sends, and confirm.
3. Sign in, open your account page and **enable the free web services**.
4. Enter your **username** (not your password) into **GeoNames username**.

### MET Norway Frost (Svalbard stations, weather in Norway)

1. Open <https://frost.met.no/auth/requestCredentials.html>.
2. Enter your email address. You get a **client ID** and a client secret.
3. Paste the **client ID** into **MET Norway Frost client ID**. The secret is
   not needed.

---

## Put the map on a dashboard

The map is [LiveTrackMapCard](https://github.com/StrausbergAutomationWorks/LiveTrackMapCard),
the card every Live Track module draws on. **It is installed with Live Track
Weather**: nothing to download, nothing to copy into `www`, no resource to add.

1. Open a dashboard, choose the pencil (**Edit dashboard**), then **Add card**.
2. Scroll to the bottom and choose **Manual**.
3. Paste this, and choose **Save**:

```yaml
type: custom:auto-entities
card:
  type: custom:live-track-map-card
filter:
  include:
    - domain: geo_location
      attributes:
        source: live_track_weather
```

The weather alerts, the outlook, MET Norway's areas, the storm cones and
tracks, the earthquake shaking lines and the dot layers appear on their own.
The markers (storms, earthquakes, volcanoes, river gauges, the Longyearbyen
forecast and the Svalbard stations) come through the filter above, which needs
[auto-entities](https://github.com/thomasloven/lovelace-auto-entities) from the
Marketplace. With other Live Track modules installed, add one more `- domain:
geo_location` filter for each of their sources (`live_track_aircraft`,
`live_track_ships` and so on).

**On the map:**

* The **layer control** at the top right has a checkbox for every layer: the
  US alerts, the outlook, tropical cyclones, MET Norway's warnings and marine
  forecasts, earthquakes, earthquake shaking, storm reports, winter reports,
  fire detections, air-quality sites, weather radar, radar motion, lightning
  and clouds. Each viewer's choice is kept in their own browser.
* **Click** a marker, an area, a line or a dot to read about it.
* The **filter card** (`custom:live-track-map-filter-card`) can hide the
  Svalbard stations, as **Observed weather (MET Norway)**.
* Each source's credit appears in the map's attribution line while its data
  are shown.

If your dashboards' resources are set in YAML (`lovelace: resource_mode: yaml`),
nothing can be registered for you: a **Repairs** issue then gives the exact
line to add. Any other map card that shows `geo_location` entities shows the
markers, but not the alerts, areas or dots.

---

## Use it in automations

Everything is an ordinary Home Assistant entity, so the automation editor
works with it, no code needed.

**A phone notification when home is inside an alert:**

1. **Settings → Automations & scenes → Create automation → Create new
   automation**.
2. **When**: *Entity → State*, entity **Alert at Home**, to **Unsafe** (on).
3. **Then do**: *Notifications → Send a notification via mobile_app_…*, with
   a message such as `Weather alert at home: {{ state_attr('binary_sensor.live_track_weather_alert_at_home', 'highest') }}`.
4. Save.

**Roll the awning in on a gust:** *When* **Wind gust at Home** is above
50 km/h (or 30 mph), *then* close the awning's cover.

**Other ideas:** flash a light when **Severe weather outlook** reaches 3
(Enhanced); warn the camper's owner when **Alert at Camper** turns on because
of a wildfire within 50 km; notify when **Temperature at Cabin** drops below
freezing; show **Forecast at Boat** on a weather card while it is at sea.

---

## Everything on the map, in detail

### US weather alerts

Every active National Weather Service alert: warnings, watches, advisories and
statements for counties, land zones, marine, offshore and fire-weather zones,
filled translucent in the Weather Service's own colour for each event (the
highest-priority one where alerts overlap). Storm-based warnings such as
tornado, severe thunderstorm and flash flood warnings are drawn by their own
polygon, not the whole county. No location is set: the map shows what is on
screen. The zone outlines (11,651, simplified to about 500 m, about 3.6 MB)
ship with each release and are downloaded once per release by each browser.

**Sensor `US alerts`**: the number of active alerts; its attributes carry the
list the map draws (`zones`, `polygons`, `styles`, `updated`, `shapes_url`),
which change on nearly every poll and are not recorded in history.

### Tropical cyclones: hurricanes, typhoons, cyclones

Every active tropical cyclone in the world, a marker per storm labelled with its
name and coloured by category: depression blue, tropical storm teal, categories
1 to 5 gold, orange, dark orange, red and magenta, post-tropical grey. Hover for
its class, wind, pressure and movement.

* **National Hurricane Center** storms (Atlantic, eastern and central Pacific):
  the forecast cone (blue), the forecast track (red), the winds of 34, 50 and
  64 knots now (yellow, orange, red) and the past track (black).
* **Every other basin**, from the Joint Typhoon Warning Center through NASA's
  EONET: the marker and the past track. A storm whose last fix is more than 24
  hours old is not shown.

Markers are `geo_location.storm_<id>` (`geo_location.storm_ep222026`), with
attributes `storm_class`, `storm_category` (TD, TS, H1-H5, PT), `max_wind_kmh`,
`pressure_hpa`, `course_deg`, `speed_kmh`, `last_seen`, `advisory_number` and
`storm_source`. They come and go with the storms and have no unique ID, so they
cannot be renamed in the interface. **Sensor `Tropical cyclones`**: the number
of storms.

### Severe weather outlook

The Storm Prediction Center's Day 1 categorical outlook: where severe
thunderstorms may happen today, from 1 Marginal, 2 Slight, 3 Enhanced, 4
Moderate to 5 High, in the Center's own colours, beneath the alerts.
**Sensor `Severe weather outlook`**: the highest risk anywhere in the US today,
0 to 5, recorded so it can drive an automation; attributes `risk`, `issued`,
`valid_from`, `valid_to`. The general-thunderstorm area is not drawn.

### Earthquakes

Every earthquake the US Geological Survey lists for the last 24 hours,
worldwide (about 240 a day):

* **Markers** for magnitude 4.5 and up, and any quake people reported feeling,
  labelled with the magnitude (`geo_location.quake_<USGS id>`). Click for the
  time, depth, felt reports, the strongest shaking, the PAGER alert level and
  USGS's event page. The "tsunami flag" is not a warning; tsunami warnings come
  from NOAA (tsunami.gov).
* **Dots** for every other quake (and quarry blasts and explosions in grey), on
  their own layer: **sensor `Earthquakes`**. The option **Smallest earthquake
  on the map's point layer** leaves out the small ones.
* **Shaking lines** (USGS ShakeMap) for the day's biggest quakes, magnitude 6
  and up or strong shaking, at most five: **sensor `Earthquake shaking`**.

### Elevated volcanoes

Every US volcano at alert level Advisory or aviation colour code Yellow and up,
a marker in its colour code labelled with its name
(`geo_location.volcano_<number>`). Click for the alert level, the colour code,
since when, the observatory's synopsis and links to the notice and the
volcano's page.

### Rivers flooding now or forecast to flood

Every US river or tide gauge at **minor flood or worse now**, or forecast to
reach it, labelled Minor, Moderate or Major in the Weather Service's flood
colours (`geo_location.river_<gauge id>`). **A dark ring means it is flooding
now**; without the ring it is a forecast. Click for the stage now, the forecast
stage, the flood stages, the flow and the gauge's page. ⚠ A few gauges carry
placeholder-looking flood stages and so show Major (Devils Lake, North Dakota).

### Storm reports

Every NWS Local Storm Report of the last 24 hours of a tornado or waterspout, a
funnel cloud, hail, thunderstorm wind or damage, a flash flood or a flood: red
for tornadoes, blue for wind, green for hail, teal for flooding. A significant
report (any tornado, hail of 2 inches or more, wind of 65 knots or more) is
larger with a dark ring. Reports fade as they age: under an hour, 1 to 6 hours,
6 to 24 hours. Click for the type, the size or speed, the place, the time, the
NWS office and the remarks. **Sensor `Storm reports`**: the number of dots.
⚠ These are reports as people send them, before the Weather Service checks
them, and can take 30 minutes to appear.

### Winter reports

From the same reports, on their own layer beneath the storm reports: snow, heavy
snow and snow squalls (slate blue), blizzards (orange-red), sleet (orchid),
freezing rain, freezing drizzle and ice storms (dark magenta), snow and ice
damage (grey), extreme cold and wind chill (blue), avalanches (brown) and ice
jams (dark teal), each with a thin dark ring. Significant (12 inches of snow,
half an inch of sleet, a quarter inch of ice, any ice storm) is larger. Click
for the amount in inches and cm or mm, or the temperature in °F and °C.
**Sensor `Winter reports`**. ⚠ A big storm brings thousands of reports; where
two would overlap one is drawn, so zoom in.

### MET Norway: warnings, marine forecasts, the Longyearbyen forecast

* **Warnings** for Norway's land, coast and seas and the seas to the North
  Pole, in MET's yellow, orange or red, beside the US alerts. Click one for
  what is expected, the consequences, the advice and when (in English).
  **Sensor `MET Norway warnings`**.
* **Marine forecasts** for 56 sea areas and 39 coastal areas, Svalbard's
  included, beneath the warnings. Click one for its forecast and any wind, ice
  or polar-low warning. **Sensor `MET Norway marine forecasts`**.
* **A forecast dot at Longyearbyen**, labelled with the temperature; click it
  for the forecast every six hours for a day
  (`geo_location.met_forecast_longyearbyen`).

### Measured weather in Svalbard and Jan Mayen (Frost client ID)

A teal dot for each weather station in Svalbard, Bjørnøya, Hopen and Jan Mayen
whose temperature and wind are both less than two hours old (about 30),
labelled with the temperature (`geo_location.frost_sn99840` for Svalbard
Lufthavn, and so on). Click one for the temperature, wind and direction, the
highest gust of the last hour, humidity, pressure, snow depth and the time.
Stations that report temperature only are not drawn; of two stations closer
than 1 km one is drawn. Values Frost marks very uncertain or erroneous are not
used; values only checked automatically so far (MET's newest hour usually is)
are shown, and the popup says "Automatic check only".

### Wildfires and air quality (FIRMS and AirNow keys)

Choose regions under **Fire detections and air-quality sites on the map**:

* **Fire detections** (needs the FIRMS key): every satellite fire detection of
  the last 24 hours (NOAA-20 and NOAA-21 VIIRS) as small red dots. Mills,
  refineries, gas flares and other standing heat sources NASA has classified
  are left out. Click for when, which satellite, its fire radiative power and
  NASA's confidence. **Sensor `Fire detections`**.
* **Air quality sites** (needs the AirNow key; the US and Canada): every
  fine-particle (PM2.5) monitor, coloured by its AQI in the EPA's colours,
  every hour. **Sensor `Air quality sites`**.

### Weather radar, lightning and clouds

Drawn by the map card itself, nothing to set up: one radar layer that picks the
sharpest source for what is on screen (RainViewer, NOAA nowCOAST and Canada's
GeoMet in North America; Finland's FMI and Germany's DWD in Europe; Japan's
JMA; KNMI over the Netherlands with your key), radar motion, lightning from
nowCOAST, and clouds from GOES and EUMETSAT satellites.

---

## Everything at your places, in detail

### Alert at …

**`Alert at Home`** (`binary_sensor.live_track_weather_alert_at_home`, device
class *safety*: on means unsafe), and one per person, tracker or zone you
watch. It turns on when the place is:

* inside a **US weather alert** or a **MET Norway warning** (by the Weather
  Service's own rule: a tornado or flood warning counts inside its polygon, not
  the whole county; the zones come from the Weather Service itself, so a place
  on a coast or a county line gets the right answer);
* near a strong **earthquake** in the last 24 hours: magnitude 4 within 50 km,
  5 within 150 km, 6 within 300 km, 7 within 600 km;
* inside the hazard zone of a **volcano** at Watch or Orange and up (USGS's
  National Volcanic Threat Layer, shipped with the integration);
* with the FIRMS key, near a **wildfire** (within the distance you set,
  50 km by default; detections reach Home Assistant 2 to 4 hours after the
  satellite passes);
* with the AirNow key, in **wildfire smoke**: the closest PM2.5 monitor within
  50 miles at or above the AQI you set, 90 by default (US places).

Attributes: `alerts` (every alert at the place, worst first, with `event`,
`severity`, `headline`, `onset`, `ends`, `source` and a link), `highest`,
`zones`; with the keys, `fires_near`, `nearest_fire_km`, `pm25_aqi`,
`pm25_site` and more. A moving tracker's zones are asked again after it moves
more than 1 km. NASA advises against using fire detections alone for decisions
on the ground: follow evacuation orders.

### Forecast at …

**`Forecast at Home`** (`weather.live_track_weather_forecast_at_home`), and one
per watched place, for every weather card and `weather.get_forecasts`: daily,
day-and-night and hourly.

* **On US land**: the National Weather Service's forecast for the place's
  2.5 km grid, seven days of day and night with the written forecast, and
  hourly for six and a half days.
* **Everywhere else, and on all water**: MET Norway's forecast, hourly for
  about two and a half days, then six-hourly to about ten days.

It changes source as the place moves (a boat leaving harbour, a camper crossing
into Canada).

### Wind at …, Wind gust at …, Wind direction at …, Temperature at …

What the nearest weather station measured, for each watched place
(`sensor.live_track_weather_wind_at_home` and so on).

* **In the US**: the nearest National Weather Service station of any network
  (airports, fire-weather and road stations, volunteer stations), or airports
  only by option; the next, up to three, when one has nothing recent.
* **In Norway and Svalbard**, with a Frost client ID: the nearest of MET
  Norway's own stations (measured at 22 places across Norway: 0.4 to 11 km
  away). The gust is the highest of the last hour.
* **Elsewhere**, with a GeoNames username: the nearest airport's weather report
  (METAR), within about 100 km.
* A sensor is **unavailable** when no report younger than two hours has its
  value. A gust is unknown when none was reported. Attributes: `station`,
  `station_name`, `provider`, `distance_km`, `observed`, `age_min`.

### Elevation at … and Depth at …

**`Elevation at Home`** and **`Depth at Home`**, and one each per watched place,
checked at start-up and after a move of more than 500 m.

* **Elevation** from the first source with a value: USGS 3DEP (US and border
  regions, to 1 m), Natural Resources Canada, Kartverket (mainland Norway),
  then Mapzen's Terrain Tiles for the rest of the world.
* **On water** the elevation is the surface and **Depth** is the depth under
  the place, from Kartverket in Norway or NOAA NCEI elsewhere (the Great Lakes
  included); unknown on land. With a GeoNames username, `sea` names the sea.
* ⚠ Known limits: Svalbard's elevation is about 35 m too high (no better
  source found); rivers, harbours and reservoirs have no depth; in shallow seas
  without GeoNames the elevation is the sea floor; a lake below sea level
  reached only by the terrain tiles shows 0.

---

## All the entities it creates

| Entity | What it is |
|---|---|
| `sensor.live_track_weather_us_alerts` | number of active US alerts; the list the map draws |
| `sensor.live_track_weather_tropical_cyclones` | number of tropical cyclones |
| `sensor.live_track_weather_severe_weather_outlook` | highest severe-storm risk today, 0 to 5 |
| `sensor.live_track_weather_met_norway_warnings` | MET Norway warnings drawn |
| `sensor.live_track_weather_met_norway_marine_forecasts` | MET Norway marine forecast areas |
| `sensor.live_track_weather_earthquakes` | earthquake dots on the map |
| `sensor.live_track_weather_earthquake_shaking` | ShakeMaps drawn |
| `sensor.live_track_weather_storm_reports` | storm reports drawn |
| `sensor.live_track_weather_winter_reports` | winter reports drawn |
| `sensor.live_track_weather_fire_detections` | fire detections (FIRMS key and a region) |
| `sensor.live_track_weather_air_quality_sites` | air-quality sites (AirNow key and a region) |
| `sensor.live_track_weather_knmi_radar` | newest KNMI radar frame (KNMI key) |
| `geo_location.storm_…`, `quake_…`, `volcano_…`, `river_…`, `met_forecast_…`, `frost_…` | the markers; they come and go and have no unique ID |
| `binary_sensor.live_track_weather_alert_at_home` | Alert at Home (and one per watched place) |
| `weather.live_track_weather_forecast_at_home` | Forecast at Home (and one per watched place) |
| `sensor.live_track_weather_wind_at_home`, `…_wind_gust_at_home`, `…_wind_direction_at_home`, `…_temperature_at_home` | measured weather at Home (and per place) |
| `sensor.live_track_weather_elevation_at_home`, `…_depth_at_home` | elevation and depth at Home (and per place) |

Attributes that change on every poll (lists, shapes, popups) are kept out of
Home Assistant's history, so your database does not grow with them.

---

## What it sends and downloads

**About your location.** Your home's and each watched place's location is sent,
rounded to about 11 m, only where a service needs it: to the National Weather
Service to learn the place's zones, forecast grid and stations; outside the
US forecast area, to MET Norway for its forecast; to USGS (and, where USGS has
nothing, Natural Resources Canada, Kartverket and NOAA NCEI) for elevation and
depth, at start-up and after a move of more than 500 m; with your keys, to NASA
FIRMS (a box around the place), AirNow, GeoNames and MET Norway's Frost. Switch
**Watch home** off and watch nothing else, and no location is sent. Nothing else
about you is sent anywhere.

**How much.** The US alert list about 100 KB every 3 minutes (adjustable); the
others ask only for a changed file where the service allows it: hurricane
advisories every 5 minutes, EONET every 30, the outlook every 5, MET Norway's
warnings every 5, marine forecasts every 15-30 and point forecasts every 30
(each a minute later at random, as MET asks, and nothing for 30 minutes after a
refusal); USGS earthquakes every 5 minutes (about 170 KB), volcanoes every 10,
rivers every 30, storm reports every 10; Frost every 10 minutes (about 80 KB);
GeoNames within half its free 10,000 daily credits; KNMI at most about 24
requests an hour, and only while a map shows it. After an error, each service
is left alone for a while before it is asked again.

---

## Languages

This README: **English**, [Deutsch](README.de.md), [Français](README.fr.md),
[Nederlands](README.nl.md), [简体中文](README.zh-Hans.md),
[Español](README.es.md), [Italiano](README.it.md), [Dansk](README.da.md) and
[Kalaallisut](README.kl.md) (a short draft; until a native speaker has read it,
the Danish page is the reliable one). Each translated README is complete.

The setup dialog and the options appear in your Home Assistant language when it
is one of these: English, Dansk, Deutsch, Español, Français, Gaeilge,
Íslenska, Italiano, Nederlands, Norsk Bokmål, Polski, Português, Português
(BR), Suomi, Svenska and 简体中文. Any other language shows English.

Found a mistake in a translation, or need another language? Tell us at
<https://github.com/StrausbergAutomationWorks/LiveTrackWeather/issues>.

---

## Credits and licences

* The National Weather Service, the National Hurricane Center, the Storm
  Prediction Center, the National Water Prediction Service, the Joint Typhoon
  Warning Center, NASA and the US Geological Survey are US Government
  agencies; their data are works of the US Government. AirNow data are
  preliminary and not verified (US EPA and partners).
* **MET Norway**: data under the Norwegian Licence for Open Government Data
  (NLOD) 2.0 and Creative Commons Attribution 4.0; Frost's observations under
  Creative Commons Attribution 3.0 Norway. This integration rounds the areas,
  recolours the warnings and converts units.
* **KNMI**: radar under Creative Commons Attribution 4.0, cut and resized into
  map tiles.
* **GeoNames**: METAR reports and sea names under Creative Commons Attribution
  4.0.
* **Elevation**: Natural Resources Canada's CDEM, Open Government Licence -
  Canada; Kartverket, Creative Commons Attribution 4.0; NOAA NCEI, US
  Government. **Terrain Tiles**: Mapzen, and the sources listed in Mapzen's
  Joerd attribution (`tilezen/joerd`, `docs/attribution.md`): ArcticDEM terrain
  data DEM(s) were created from DigitalGlobe, Inc., imagery and funded under
  National Science Foundation awards 1043681, 1559691, and 1542736; Australia
  terrain data © Commonwealth of Australia (Geoscience Australia) 2017; Austria
  terrain data © offene Daten Österreichs – Digitales Geländemodell (DGM)
  Österreich; Canada terrain data contains information licensed under the Open
  Government Licence – Canada; Europe terrain data produced using Copernicus
  data and information funded by the European Union - EU-DEM layers; Global
  ETOPO1 terrain data U.S. National Oceanic and Atmospheric Administration;
  Mexico terrain data source: INEGI, Continental relief, 2016; New Zealand
  terrain data Copyright 2011 Crown copyright (c) Land Information New Zealand
  and the New Zealand Government (All rights reserved); Norway terrain data ©
  Kartverket; United Kingdom terrain data © Environment Agency copyright and/or
  database right 2015. All rights reserved; United States 3DEP (formerly NED)
  and global GMTED2010 and SRTM terrain data courtesy of the U.S. Geological
  Survey.
* **Volcano hazard zones**: USGS National Volcanic Threat Layer (2024, CC0).

None of these organisations made or endorsed this integration.

**Code**: MIT, in [LICENSE](LICENSE).

**For developers:** `tools/build_shapes.py` rebuilds the alert zone file from
the NWS shapefiles (<https://www.weather.gov/gis/>) and `tools/build_colours.py`
the colour table from the NWS hazard map page; the tests run with
`python -m unittest discover -s tests`.

---

## Keywords

Home Assistant weather · Home Assistant weather alerts · NWS alerts · National
Weather Service warnings · weather warning map · tornado warning · severe
thunderstorm warning · flash flood warning · winter storm warning · hurricane
tracker · tropical storm tracker · typhoon tracker · cyclone tracker · hurricane
cone · NHC · JTWC · SPC outlook · severe weather outlook · earthquake map ·
earthquake alert · USGS earthquakes · ShakeMap · volcano alert · river flood
map · flood gauge · NWPS · local storm reports · hail reports · snow totals ·
blizzard · ice storm · wildfire map · wildfire alert · fire detection · NASA
FIRMS · VIIRS · smoke alert · air quality · AQI · PM2.5 · AirNow · weather radar
· rain radar · lightning map · MET Norway · yr · Svalbard weather · Longyearbyen
· Jan Mayen · Frost API · marine forecast · sea area forecast · KNMI radar ·
GeoNames · METAR · weather station · wind gust sensor · temperature sensor ·
forecast for a device tracker · camper weather · boat weather · RV weather ·
elevation sensor · water depth · geo_location · binary_sensor · weather entity
· map card · Lovelace · HACS · Marketplace · Live Track · LiveTrack ·
StrausbergAutomationWorks
