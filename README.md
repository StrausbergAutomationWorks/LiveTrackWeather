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
| `styles` | `{event: {color, priority}}` for the events drawn: the NWS's own values |
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

## Map card

The alerts are drawn by [LiveTrackMapCard](https://github.com/StrausbergAutomationWorks/LiveTrackMapCard)
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

**The alerts need no entity filter.** The sensor is not a `geo_location` entity,
so auto-entities does not give it to the card: the card finds it on its own, as
any entity whose `shapes_url` is a string and whose `zones` is a mapping. Put the
card on a dashboard and the alerts appear. The card options are
`shape_layers` (`auto`, the default, for every publisher found; `false` for
none; or a list naming the entities with your own label) and `shape_style` for
opacity and outline. The alerts get a checkbox in the layer control at the
map's top right, ticked by default; each viewer's choice is kept in their own
browser. The NWS credit appears in the map's attribution line while alerts are
shown. See the card's README, section
[Shapes on the map](https://github.com/StrausbergAutomationWorks/LiveTrackMapCard#shapes-on-the-map).

**The weather radar** is the card's own overlay (`weather_radar`, on by
default, with its own checkbox). It needs nothing from this integration; the
card picks the sharpest source for each tile. See the card's README, section
[Weather radar](https://github.com/StrausbergAutomationWorks/LiveTrackMapCard#weather-radar).

Other map cards do not draw the alerts.

## Data use

Polls `https://api.weather.gov/alerts/active` every 180 seconds by default
(adjustable, 60 to 900), about 100 KB per poll. NWS data is a work of the US
Government.

## Licence

MIT. See `LICENSE`.
