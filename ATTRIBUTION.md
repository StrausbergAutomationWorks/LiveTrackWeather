# Attribution

Live Track Weather reads public weather and hazard data at runtime, and ships
three data files of its own. Every entity carries an `attribution` with the
credit line for its source, which Home Assistant shows in the entity's details,
and the Live Track map card shows each source's credit in its attribution line
while that source's data are on screen. If you show this data to others, for
example on a public dashboard, keep the credit with it and read the source's
own terms.

None of these organisations made or endorsed this integration.

## Shipped in this repository

| File | From | Licence |
|---|---|---|
| `custom_components/live_track_weather/www/nws_zones.json.gz` | US National Weather Service county, zone, marine and fire-weather zone shapefiles (<https://www.weather.gov/gis/>), simplified to about 500 m | US Government work |
| `custom_components/live_track_weather/data/nws_hazard_colours.json` | the National Weather Service's hazard colour table | US Government work |
| `custom_components/live_track_weather/data/volcano_threat_zones.json.gz` | USGS National Volcanic Threat Layer (2024) | CC0 |
| `custom_components/live_track_weather/frontend/live-track-map-card.js` | [LiveTrackMapCard](https://github.com/StrausbergAutomationWorks/LiveTrackMapCard) release, vendored byte for byte; derived from [nathan-gs/ha-map-card](https://github.com/nathan-gs/ha-map-card) | MIT; the bundle keeps the licence notices of the code it includes (Leaflet and others) |

## Read at runtime, with no key

US Government works, no copyright; the credit lines name the source:

> Data: US National Weather Service (alerts, forecasts, observations, storm and winter reports)
>
> Severe weather outlook: NOAA Storm Prediction Center, spc.noaa.gov
>
> Tropical cyclones: NOAA National Hurricane Center, nhc.noaa.gov
>
> Tropical cyclones: JTWC via NASA EONET, eonet.gsfc.nasa.gov
>
> River stages and forecasts: NOAA National Water Prediction Service, water.noaa.gov
>
> Earthquakes: USGS Earthquake Hazards Program, earthquake.usgs.gov
>
> Shaking: USGS ShakeMap, earthquake.usgs.gov
>
> Volcanoes: USGS Volcano Hazards Program, volcanoes.usgs.gov
>
> Elevation: USGS 3D Elevation Program, nationalmap.gov
>
> Depth: NOAA National Centers for Environmental Information, DEM mosaic

**MET Norway** (warnings, marine forecasts, point forecasts), under the
Norwegian Licence for Open Government Data (NLOD) 2.0 and Creative Commons
Attribution 4.0 (<https://api.met.no/doc/License>). MET asks to be named as
the source. Live Track Weather rounds the areas, recolours the warnings and
converts units, so the line says modified:

> Data from MET Norway (api.met.no), CC BY 4.0, modified

**Natural Resources Canada**, CDEM, Open Government Licence - Canada:

> Elevation: Natural Resources Canada, CDEM (Open Government Licence - Canada)

**Kartverket** (Norway), Creative Commons Attribution 4.0:

> Elevation: Kartverket (CC BY 4.0)
>
> Depth: Kartverket (CC BY 4.0)

**Mapzen Terrain Tiles** on AWS Open Data. The notice Mapzen's Joerd
attribution (`tilezen/joerd`, `docs/attribution.md`) asks for, verbatim:

> ArcticDEM terrain data DEM(s) were created from DigitalGlobe, Inc., imagery
> and funded under National Science Foundation awards 1043681, 1559691, and
> 1542736; Australia terrain data © Commonwealth of Australia (Geoscience
> Australia) 2017; Austria terrain data © offene Daten Österreichs – Digitales
> Geländemodell (DGM) Österreich; Canada terrain data contains information
> licensed under the Open Government Licence – Canada; Europe terrain data
> produced using Copernicus data and information funded by the European Union -
> EU-DEM layers; Global ETOPO1 terrain data U.S. National Oceanic and
> Atmospheric Administration; Mexico terrain data source: INEGI, Continental
> relief, 2016; New Zealand terrain data Copyright 2011 Crown copyright (c) Land
> Information New Zealand and the New Zealand Government (All rights reserved);
> Norway terrain data © Kartverket; United Kingdom terrain data © Environment
> Agency copyright and/or database right 2015. All rights reserved; United
> States 3DEP (formerly NED) and global GMTED2010 and SRTM terrain data
> courtesy of the U.S. Geological Survey.

## Read at runtime with the user's own key or account

Each person who installs Live Track Weather gets their own; none is shipped.

**NASA FIRMS** (fire detections, VIIRS near real time), with the user's own
MAP_KEY. NASA advises against using fire detections alone for decisions on the
ground.

> Fires: NASA FIRMS (VIIRS NRT), firms.modaps.eosdis.nasa.gov; standing heat sources removed by NASA's standard-product classification

**AirNow** (fine-particle air quality), with the user's own API key. AirNow's
data are preliminary and not verified:

> Air quality: AirNow (US EPA and partners), airnow.gov; preliminary data, not verified

**KNMI** radar over the Netherlands, with the user's own WMS key, under
Creative Commons Attribution 4.0; cut and resized into map tiles:

> Radar: KNMI, CC BY 4.0, modified

**GeoNames** (METAR observations, sea names), with the user's own username,
under Creative Commons Attribution 4.0:

> Observations: METAR via GeoNames (CC BY 4.0)
>
> Sea name: GeoNames (CC BY 4.0)

**MET Norway Frost** (station observations), with the user's own client ID.
Frost's answers carry Creative Commons Attribution 3.0 Norway:

> Observations: MET Norway (frost.met.no), CC BY 3.0 NO, modified

## Drawn by the map card

The weather radar, radar motion, lightning and cloud layers come from the
LiveTrackMapCard bundle, which credits each source (RainViewer, NOAA nowCOAST,
Environment and Climate Change Canada's GeoMet, FMI, DWD, JMA, KNMI,
EUMETSAT) in the map's attribution line while it is shown. See that card's
README.
