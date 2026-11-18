"""Elevation and depth at a watched place, worldwide (Weather SSOT item 352 step 4b).

Pure Python (Pillow for the terrain tile), no Home Assistant import. Lee 2026-11-17 23:31: "Elevation at X" from a
chain of land sources, the first that has a value; a separate "Depth at X" on water; the water rule as proposed in
20_Research/REPORT_elevation_world_20261117.md 4.8. Lee 2026-11-18 (after the rule was MEASURED at 28 more places,
bin\\ltw352b_probe4.txt): where only AWS Terrain Tiles answers, water is decided by GeoNames' ocean test, not by NOAA.

Land, in order (each MEASURED 2026-11-18 unless marked):
  1. USGS 3DEP (usgs.parse_elevation): the US, its territories, the border regions of Canada and Mexico.
  2. NRCan CDEM, asked only inside CANADA_BOX: {"altitude": number|null}; null outside Canada (Chicago).
  3. Kartverket's point API, asked only inside KARTVERKET_BOX: `z` null outside Norway (Stockholm, Helsinki, Skagen,
     the Baltic, Svalbard); on the sea `terreng` "Havflate" and `z` the depth as a negative number (Oslofjord -37.8).
  4. AWS Terrain Tiles (Terrarium PNG, z15, the pixel under the place): everywhere; ground, not rooftops. On the open
     ocean it gives 0 (Atlantic, Pacific, Mediterranean) but in shallow seas the SEA FLOOR (North Sea -74, English
     Channel -53, Baltic -150); wrong at Longyearbyen (53 where the contours give about 15-20).

Water:
  * 3DEP or NRCan answered: water when NOAA NCEI's DEM_all value is negative and at least WATER_MARGIN_M below the
    land value (Lee 23:31). Right at the Pacific off California (0 / -2007), Lake Ontario (74.8 / -149.6), Lake
    Michigan, Death Valley (land: -84.7 / -85.4). Rivers, harbours and reservoirs read as land (Mississippi, Hudson,
    Lake Mead, St. Lawrence at Quebec): NOAA has no depth there, so depth stays unknown.
  * Kartverket answered: its own `terreng`, "Havflate" is the sea; its `z` there IS the depth.
  * only Terrain Tiles answered: GeoNames' oceanJSON names a sea there (needs the user's GeoNames username); without
    it, unknown. NOAA there is not trusted either way (Lee 2026-11-18): it reads the North Sea and the Channel as
    land (TT and NOAA agree on the sea floor) and Jericho and coastal Kirkenes as water (NOAA's world grid dips
    below zero at coasts).
On water "Elevation at X" shows the surface: the land value, or 0 where that is negative (the sea floor of a shallow
sea, Kartverket's depth). ! A lake below sea level reached only through Terrain Tiles (the Dead Sea, the Caspian)
would show 0, not its surface: not handled.
"""

from __future__ import annotations

import io
import math
from typing import Any

from . import usgs

NRCAN_URL = "https://geogratis.gc.ca/services/elevation/cdem/altitude"
KARTVERKET_URL = "https://ws.geonorge.no/hoydedata/v1/punkt"
TERRAIN_URL = "https://s3.amazonaws.com/elevation-tiles-prod/terrarium/{z}/{x}/{y}.png"
TERRAIN_Z = 15
TERRAIN_PX = 256
NOAA_URL = "https://gis.ngdc.noaa.gov/arcgis/rest/services/DEM_mosaics/DEM_all/ImageServer/identify"

# (south, north, west, east). Canada's: a box around the country, so a place in Europe is never sent to NRCan.
# Kartverket's: answers null outside Norway inside it (MEASURED), Norway's corners inside it (Lindesnes 57.98 N,
# Nordkapp 71.17 N, Vardo 31.1 E, Utsira 4.885 E).
CANADA_BOX = (41.5, 84.0, -141.5, -52.0)
KARTVERKET_BOX = (57.0, 72.0, 4.0, 32.0)
WATER_MARGIN_M = 5.0

SRC_3DEP = "usgs_3dep"
SRC_NRCAN = "nrcan_cdem"
SRC_KARTVERKET = "kartverket"
SRC_TERRAIN = "aws_terrain_tiles"
SRC_NOAA = "noaa_ncei"

ATTRIBUTION = {
    SRC_3DEP: usgs.ELEV_ATTRIBUTION,
    SRC_NRCAN: "Elevation: Natural Resources Canada, CDEM (Open Government Licence - Canada)",
    SRC_KARTVERKET: "Elevation: Kartverket (CC BY 4.0)",
    SRC_TERRAIN: ("Elevation: Mapzen Terrain Tiles on AWS Open Data: 3DEP, SRTM and GMTED2010 (USGS), ETOPO1 (NOAA), "
                  "EU-DEM (Copernicus), CDEM (Canada, OGL), Kartverket, Geoscience Australia, LINZ, INEGI, "
                  "Environment Agency, data.gv.at, ArcticDEM; the full notice is in the README"),
}
DEPTH_ATTRIBUTION = {
    SRC_NOAA: "Depth: NOAA National Centers for Environmental Information, DEM mosaic",
    SRC_KARTVERKET: "Depth: Kartverket (CC BY 4.0)",
}


def _in(box: tuple[float, float, float, float], lat: float, lon: float) -> bool:
    s, n, w, e = box
    return s <= lat <= n and w <= lon <= e


def in_canada_box(lat: float, lon: float) -> bool:
    return _in(CANADA_BOX, lat, lon)


def in_kartverket_box(lat: float, lon: float) -> bool:
    return _in(KARTVERKET_BOX, lat, lon)


def _finite(v: Any) -> float | None:
    if isinstance(v, bool):
        return None
    try:
        f = float(v)
    except (TypeError, ValueError):
        return None
    return f if math.isfinite(f) and f > -12000 else None


def nrcan_params(lat: float, lon: float) -> dict[str, str]:
    return {"lat": f"{lat:.4f}", "lon": f"{lon:.4f}"}


def parse_nrcan(doc: Any) -> dict[str, Any] | None:
    """NRCan's CDEM altitude answer -> {"m", "resolution_m", "source"}; None for null (outside Canada)."""
    if not isinstance(doc, dict):
        return None
    m = _finite(doc.get("altitude"))
    if m is None:
        return None
    return {"m": round(m, 1), "resolution_m": None, "source": SRC_NRCAN}


def kartverket_params(lat: float, lon: float) -> dict[str, str]:
    return {"nord": f"{lat:.4f}", "ost": f"{lon:.4f}", "koordsys": "4258", "geojson": "false"}


def parse_kartverket(doc: Any) -> dict[str, Any] | None:
    """Kartverket's point answer -> {"m", "resolution_m", "source", "water"}; None where `z` is null (outside Norway).
    On the sea (`terreng` "Havflate") `m` is the depth as a negative number."""
    try:
        p = doc["punkter"][0]
    except (KeyError, IndexError, TypeError):
        return None
    if not isinstance(p, dict):
        return None
    m = _finite(p.get("z"))
    if m is None:
        return None
    return {"m": round(m, 1), "resolution_m": 1.0 if p.get("datakilde") == "dtm1" else None,
            "source": SRC_KARTVERKET, "water": p.get("terreng") == "Havflate"}


def terrain_tile(lat: float, lon: float, z: int = TERRAIN_Z) -> tuple[int, int, int, int]:
    """(x, y, pixel x, pixel y) of the Web Mercator tile and pixel under the place."""
    lat = max(-85.0511, min(85.0511, lat))
    n = 2 ** z
    xf = (lon + 180.0) / 360.0 * n
    yf = (1.0 - math.asinh(math.tan(math.radians(lat))) / math.pi) / 2.0 * n
    x, y = min(int(xf), n - 1), min(int(yf), n - 1)
    return x, y, min(int((xf - int(xf)) * TERRAIN_PX), TERRAIN_PX - 1), min(int((yf - int(yf)) * TERRAIN_PX),
                                                                           TERRAIN_PX - 1)


def terrain_url(x: int, y: int, z: int = TERRAIN_Z) -> str:
    return TERRAIN_URL.format(z=z, x=x, y=y)


def decode_terrarium(png: bytes, px: int, py: int) -> float | None:
    """The metres at one pixel of a Terrarium tile: R*256 + G + B/256 - 32768. None when it is not a 256-pixel
    picture. Blocking (Pillow): run it in the executor."""
    from PIL import Image
    try:
        with Image.open(io.BytesIO(png)) as im:
            if im.size != (TERRAIN_PX, TERRAIN_PX):
                return None
            r, g, b = im.convert("RGB").getpixel((px, py))[:3]
    except (OSError, ValueError):
        return None
    return round(r * 256 + g + b / 256 - 32768, 1)


def terrain_record(m: float | None) -> dict[str, Any] | None:
    return None if m is None else {"m": m, "resolution_m": None, "source": SRC_TERRAIN}


def noaa_params(lat: float, lon: float) -> dict[str, str]:
    geo = '{"x":%s,"y":%s,"spatialReference":{"wkid":4326}}' % (f"{lon:.4f}", f"{lat:.4f}")
    return {"geometry": geo, "geometryType": "esriGeometryPoint", "returnGeometry": "false",
            "returnCatalogItems": "false", "f": "json"}


def parse_noaa(doc: Any) -> float | None:
    """DEM_all identify -> metres (negative under water); None for NoData or an error answer."""
    if not isinstance(doc, dict) or "error" in doc:
        return None
    m = _finite(doc.get("value"))
    return None if m is None else round(m, 1)


def water_by_noaa(land_m: float | None, noaa_m: float | None) -> bool | None:
    """The approved rule (Lee 23:31), for a 3DEP or NRCan value only; None when either is missing."""
    if land_m is None or noaa_m is None:
        return None
    return noaa_m < 0 and noaa_m <= land_m - WATER_MARGIN_M


def needs_noaa(land: dict[str, Any] | None) -> bool:
    """NOAA is asked for the water test after 3DEP or NRCan; after Terrain Tiles only once GeoNames finds a sea."""
    return bool(land) and land["source"] in (SRC_3DEP, SRC_NRCAN)


async def run_chain(lat: float, lon: float, *, epqs: Any, nrcan: Any, kartverket: Any, terrain: Any, noaa: Any,
                    sea: Any, has_geonames: bool) -> tuple[dict[str, Any] | None, bool]:
    """The order of asking (places_watch.py supplies the requests). Each source is an async callable (lat, lon) ->
    (answered, value): epqs, nrcan, kartverket and terrain give a land record or None, noaa metres or None, sea a sea
    name or None. -> (decide()'s answer, or None when no land source answered and one could not be asked; failed: a
    source that should have answered could not be asked, so the check is repeated after the gap). GeoNames never
    marks it failed: it rests on its own after an error."""
    failed = False
    land: dict[str, Any] | None = None
    steps = [(epqs, True), (nrcan, in_canada_box(lat, lon)), (kartverket, in_kartverket_box(lat, lon)),
             (terrain, True)]
    for ask, wanted in steps:
        if land is not None or not wanted:
            continue
        ok, land = await ask(lat, lon)
        failed = failed or not ok
    noaa_ok, noaa_m = (await noaa(lat, lon)) if needs_noaa(land) else (True, None)
    sea_ok, sea_name = False, None
    terrain_only = bool(land) and land["source"] == SRC_TERRAIN
    if has_geonames and (terrain_only or decide(land, noaa_m, noaa_ok, None, False, True)["on_water"]):
        sea_ok, sea_name = await sea(lat, lon)
        if terrain_only and sea_name is not None:
            noaa_ok, noaa_m = await noaa(lat, lon)
    failed = failed or not noaa_ok
    if land is None and failed:
        return None, True
    return decide(land, noaa_m, noaa_ok, sea_name, sea_ok, has_geonames), failed


def decide(land: dict[str, Any] | None, noaa_m: float | None, noaa_ok: bool, sea: str | None, sea_ok: bool,
           has_geonames: bool) -> dict[str, Any]:
    """What both sensors show. land: a parse_* record or None; noaa_m and noaa_ok: NOAA's value and whether it
    answered; sea and sea_ok: GeoNames' sea name and whether it answered (a name or "no ocean here").
    -> {"m", "resolution_m", "source", "on_water", "reason", "depth_m", "depth_source", "depth_reason", "sea"}"""
    out: dict[str, Any] = {"m": None, "resolution_m": None, "source": None, "on_water": None, "reason": None,
                           "depth_m": None, "depth_source": None, "depth_reason": None, "sea": None}
    if not land:
        out["reason"] = out["depth_reason"] = "no elevation source answered here"
        return out
    src = land["source"]
    out.update(m=land["m"], resolution_m=land["resolution_m"], source=src)
    if src == SRC_KARTVERKET:
        on_water: bool | None = bool(land.get("water"))
        depth = -land["m"] if on_water and land["m"] < 0 else None
        depth_src = SRC_KARTVERKET
        if on_water and depth is None:
            out["depth_reason"] = "Kartverket gives no depth here"
    elif src in (SRC_3DEP, SRC_NRCAN):
        on_water = water_by_noaa(land["m"], noaa_m)
        depth = -noaa_m if on_water and noaa_m is not None else None
        depth_src = SRC_NOAA
        if on_water is None:
            out["depth_reason"] = ("NOAA's depth service did not answer" if not noaa_ok
                                   else "NOAA has no value here")
    else:
        # Lee 2026-11-18: only GeoNames' ocean test decides here; NOAA gives the depth once it says sea.
        depth_src = SRC_NOAA
        if not has_geonames:
            on_water = None
            out["depth_reason"] = "water or land cannot be told here without a GeoNames username"
        elif not sea_ok:
            on_water = None
            out["depth_reason"] = "GeoNames did not answer"
        else:
            on_water = sea is not None
        depth = -noaa_m if on_water and noaa_m is not None and noaa_m < 0 else None
        if on_water and depth is None:
            out["depth_reason"] = ("NOAA's depth service did not answer" if not noaa_ok
                                   else "NOAA has no depth here")
    out["on_water"] = on_water
    if on_water:
        out["m"] = land["m"] if land["m"] > 0 else 0.0
        if depth is not None:
            out.update(depth_m=round(depth, 1), depth_source=depth_src)
        out["sea"] = sea
    elif on_water is False:
        out["depth_reason"] = "not on water"
    return out
