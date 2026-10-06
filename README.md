# Live Track Weather

US weather alerts from the National Weather Service for the Live Track map in
Home Assistant: warnings, watches, advisories and statements, filled
translucent on the map in the NWS's own colours.

Original work by StrausbergAutomationWorks. Not affiliated with, or endorsed
by, the National Weather Service or NOAA.

**Status: in development. Not yet released.**

## What it adds

One sensor, `US alerts`. Its state is the number of active US alerts. Its
attributes carry the live list the map draws:

| Attribute | Holds |
|---|---|
| `shapes_url` | where the shape file is served (see below) |
| `zones` | `{shape key: event}`, one event per zone: the highest-priority one |
| `polygons` | storm-based warnings that carry their own polygon |
| `styles` | `{event: {color, priority, pattern}}` for the events drawn |
| `updated` | when NWS last updated the alert list |

These attributes change on nearly every poll and are deliberately **not
recorded** in Home Assistant's history. The count is.

No location is configured. Every active US alert is listed, and the map shows
the ones on screen.

## The shapes

Alerts name NWS counties and forecast, marine, offshore and fire zones. Their
outlines (11,651 shapes, simplified to about 500 m) ship with each release as
`www/nws_zones.json.gz`, about 3.6 MB, and are served by Home Assistant at a
URL that changes with the file, so a browser downloads them once per release.

`tools/build_shapes.py` rebuilds that file from the NWS shapefiles
(https://www.weather.gov/gis/); the file records the edition and the hash of
each source zip. `tools/build_colours.py` rebuilds the colour table from the
NWS hazard map page (https://www.weather.gov/help-map).

## Data use

Polls `https://api.weather.gov/alerts/active` every 180 seconds by default
(adjustable, 60 to 900), about 100 KB per poll. NWS data is a work of the US
Government.

## Licence

MIT. See `LICENSE`.
