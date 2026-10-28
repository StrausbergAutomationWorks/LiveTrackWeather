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

Original work by StrausbergAutomationWorks. Not affiliated with, or endorsed
by, the National Weather Service, NOAA, the National Hurricane Center, the
Storm Prediction Center, the Joint Typhoon Warning Center or NASA.

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

**The weather radar** is the card's own overlay (`weather_radar`, on by
default, with its own checkbox). It needs nothing from this integration; the
card picks the sharpest source for each tile. See the card's README, section
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

The National Weather Service, the National Hurricane Center, the Storm
Prediction Center, the Joint Typhoon Warning Center and NASA are US Government
agencies; their data are works of the US Government.

## Licence

MIT. See `LICENSE`.
