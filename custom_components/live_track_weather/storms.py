"""Tropical cyclones for the shared map (Weather SSOT item 302, contract D15).

Two sources, both keyless:

* NOAA's National Hurricane Center, `CurrentStorms.json`, for the Atlantic,
  East and Central Pacific, with each storm's cone, forecast track, current
  wind extent and best track as KMZ (zipped KML, read here with the standard
  library: no shapefile reader ships).
* JTWC's fixes through NASA EONET (`severeStorms`), for every other basin.

Where both list a storm, NHC wins. The join is JTWC's product code in EONET's
source link, `ep2226`, which is NHC's ATCF id `ep222026`; a storm with only an
NHC link joins by name and year.

Nothing here imports Home Assistant: the coordinator fetches, this parses and
builds, and the tests run it without HA.
"""

from __future__ import annotations

import io
import re
import zipfile
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from typing import Any

KT_KMH = 1.852
MPH_KMH = 1.609344
# KML larger than this is refused rather than parsed (the largest NHC file
# measured, a basin-wide probability KML this code never reads, was 894,546 b).
MAX_KML_BYTES = 8_000_000
# Coordinate decimals: 0.001 deg, about 100 m, far finer than any of these shapes.
ROUND = 3

# Saffir-Simpson by one-minute sustained wind, kt.
CATEGORY_ORDER = ("TD", "TS", "H1", "H2", "H3", "H4", "H5")
NOT_TROPICAL = "PT"  # post-tropical, remnant, potential: no category


def category(kt: float | None) -> str | None:
    if kt is None:
        return None
    if kt < 34:
        return "TD"
    if kt < 64:
        return "TS"
    if kt < 83:
        return "H1"
    if kt < 96:
        return "H2"
    if kt < 113:
        return "H3"
    if kt < 137:
        return "H4"
    return "H5"


# Marker colours by category, in the Saffir-Simpson order but deeper than the
# usual scale colours, so every step reads on the light and the dark map
# (picked by Lee from pictures, 2026-10-28; D15).
CATEGORY_COLOURS = {
    "TD": "#3A86FF",
    "TS": "#00A6A6",
    "H1": "#F2C500",
    "H2": "#F28C00",
    "H3": "#E8590C",
    "H4": "#D62828",
    "H5": "#B5179E",
    NOT_TROPICAL: "#8C8C8C",
}

# NHC classification codes as NHC writes them out.
NHC_CLASS = {
    "TD": "Tropical Depression",
    "STD": "Subtropical Depression",
    "TS": "Tropical Storm",
    "STS": "Subtropical Storm",
    "HU": "Hurricane",
    "MH": "Major Hurricane",
    "TY": "Typhoon",
    "STY": "Super Typhoon",
    "PTC": "Post-Tropical Cyclone",
    "PC": "Potential Tropical Cyclone",
    "LO": "Remnant Low",
    "EX": "Extratropical Cyclone",
}
NHC_NOT_TROPICAL = frozenset({"PTC", "PC", "LO", "EX"})

# Shape events (D12 `polygons` events; D15). Priority 1 on top. Colours picked by
# Lee from pictures, 2026-10-28: blue cone, red forecast, black past track; the
# wind areas are NHC's own yellow, orange and red.
EVENT_FORECAST = "Forecast track"
EVENT_PAST = "Past track"
EVENT_WIND = {"64": "Hurricane-force winds", "50": "50 kt winds", "34": "Tropical-storm-force winds"}
EVENT_CONE = "Forecast cone"
STYLES = {
    EVENT_FORECAST: {"color": "#D7263D", "priority": 1},
    EVENT_PAST: {"color": "#000000", "priority": 2},
    EVENT_WIND["64"]: {"color": "#D7263D", "priority": 3},
    EVENT_WIND["50"]: {"color": "#FF8C00", "priority": 4},
    EVENT_WIND["34"]: {"color": "#FFD700", "priority": 5},
    EVENT_CONE: {"color": "#4A6FA5", "priority": 6},
}

ATTRIBUTION_NHC = "Tropical cyclones: NOAA National Hurricane Center, nhc.noaa.gov"
ATTRIBUTION_EONET = "Tropical cyclones: JTWC via NASA EONET, eonet.gsfc.nasa.gov"

_BASINS = ("al", "ep", "cp", "wp", "io", "sh")
_JTWC = re.compile(r"/products/(al|ep|cp|wp|io|sh)(\d{2})(\d{2})\.tcw", re.I)
_NHC_ARCHIVE = re.compile(r"nhc\.noaa\.gov/archive/(\d{4})/([A-Za-z0-9_-]+)\.shtml", re.I)
_ADV = re.compile(r"_(\d{3})adv_", re.I)
_TITLE_PREFIX = re.compile(
    r"^(super typhoon|typhoon|major hurricane|hurricane|severe tropical cyclone|"
    r"tropical cyclone|tropical storm|tropical depression|subtropical storm|"
    r"subtropical depression|post-tropical cyclone|cyclone)\s+", re.I)


# ---------------------------------------------------------------- helpers

def _num(v: Any) -> float | None:
    try:
        f = float(v)
    except (TypeError, ValueError):
        return None
    return f if f == f and f not in (float("inf"), float("-inf")) else None


def _lat_ok(lat: float | None) -> bool:
    return lat is not None and -90 <= lat <= 90


def _lon_ok(lon: float | None) -> bool:
    return lon is not None and -360 <= lon <= 360


def unwrap(coords: list[list[float]], ref_lon: float) -> list[list[float]]:
    """Longitudes made continuous, starting within 180 deg of `ref_lon`, so a
    shape crossing the antimeridian is drawn whole beside its storm, not
    stretched round the world."""
    out: list[list[float]] = []
    prev = ref_lon
    for lon, lat in coords:
        while lon - prev > 180:
            lon -= 360
        while lon - prev < -180:
            lon += 360
        out.append([round(lon, ROUND), round(lat, ROUND)])
        prev = lon
    return out


def _parse_time(s: Any) -> datetime | None:
    if not isinstance(s, str):
        return None
    try:
        t = datetime.fromisoformat(s.replace("Z", "+00:00"))
    except ValueError:
        return None
    return t if t.tzinfo else t.replace(tzinfo=timezone.utc)


def atcf_from_jtwc(url: Any) -> str | None:
    """`.../products/ep2226.tcw` -> `ep222026`."""
    m = _JTWC.search(url) if isinstance(url, str) else None
    return f"{m.group(1).lower()}{m.group(2)}20{m.group(3)}" if m else None


def nhc_ref(url: Any) -> tuple[str, str] | None:
    """`.../archive/2026/VANCE.shtml` -> ("2026", "VANCE")."""
    m = _NHC_ARCHIVE.search(url) if isinstance(url, str) else None
    return (m.group(1), m.group(2).upper()) if m else None


def storm_name(title: Any) -> str | None:
    """EONET's title less its class: 'Super Typhoon Champi' -> 'Champi'. The class
    in a title is the storm's HIGHEST, not its present one, so it is never used."""
    if not isinstance(title, str) or not title.strip():
        return None
    return _TITLE_PREFIX.sub("", title.strip()).strip() or None


def jtwc_class(kt: float | None, basin: str | None) -> str | None:
    cat = category(kt)
    if cat is None:
        return None
    if cat == "TD":
        return "Tropical Depression"
    if cat == "TS":
        return "Tropical Storm"
    if basin == "wp":
        return "Super Typhoon" if kt >= 130 else "Typhoon"
    if basin in ("io", "sh"):
        return "Cyclone"
    return "Hurricane"


# ---------------------------------------------------------------- KML

def _ln(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def kml_from_kmz(data: bytes) -> bytes | None:
    """The KML inside a KMZ (or the body itself if it is plain KML), or None."""
    if not data:
        return None
    try:
        z = zipfile.ZipFile(io.BytesIO(data))
    except zipfile.BadZipFile:
        return data if data.lstrip()[:1] == b"<" and len(data) <= MAX_KML_BYTES else None
    for zi in z.infolist():
        if zi.filename.lower().endswith(".kml") and zi.file_size <= MAX_KML_BYTES:
            return z.read(zi)
    return None


def _coords(text: str | None) -> list[list[float]]:
    out = []
    for tok in (text or "").split():
        parts = tok.split(",")
        if len(parts) < 2:
            continue
        lon, lat = _num(parts[0]), _num(parts[1])
        if _lon_ok(lon) and _lat_ok(lat):
            out.append([lon, lat])
    return out


def placemarks(kml: bytes) -> list[dict[str, Any]]:
    """Every Placemark: name, ExtendedData values, and geometries as
    ("Point", [lon, lat]), ("LineString", [[lon, lat], ...]) or
    ("Polygon", [outer ring, hole, ...]). Namespaces are ignored: NHC's own
    files use two (KML 2.2 and Google's 2.1)."""
    root = ET.fromstring(kml)
    out = []
    for pm in root.iter():
        if _ln(pm.tag) != "Placemark":
            continue
        rec: dict[str, Any] = {"name": None, "data": {}, "geoms": []}
        for el in pm.iter():
            ln = _ln(el.tag)
            if ln == "name" and rec["name"] is None:
                rec["name"] = (el.text or "").strip() or None
            elif ln == "Data":
                v = next((c.text for c in el if _ln(c.tag) == "value"), None)
                rec["data"][el.get("name")] = (v or "").strip()
            elif ln == "SimpleData":
                rec["data"][el.get("name")] = (el.text or "").strip()
            elif ln == "Point":
                c = next((x for x in el.iter() if _ln(x.tag) == "coordinates"), None)
                pts = _coords(c.text if c is not None else None)
                if pts:
                    rec["geoms"].append(("Point", pts[0]))
            elif ln == "LineString":
                c = next((x for x in el.iter() if _ln(x.tag) == "coordinates"), None)
                pts = _coords(c.text if c is not None else None)
                if len(pts) >= 2:
                    rec["geoms"].append(("LineString", pts))
            elif ln == "Polygon":
                rings = []
                for b in el:
                    if _ln(b.tag) not in ("outerBoundaryIs", "innerBoundaryIs"):
                        continue
                    c = next((x for x in b.iter() if _ln(x.tag) == "coordinates"), None)
                    ring = _coords(c.text if c is not None else None)
                    if len(ring) >= 4:
                        if _ln(b.tag) == "outerBoundaryIs":
                            rings.insert(0, ring)
                        else:
                            rings.append(ring)
                if rings:
                    rec["geoms"].append(("Polygon", rings))
        out.append(rec)
    return out


def cone_polygons(kml: bytes) -> list[list[list[list[float]]]]:
    """Every polygon in a cone file (NHC sends one)."""
    return [g[1] for pm in placemarks(kml) for g in pm["geoms"] if g[0] == "Polygon"]


def forecast_line(kml: bytes) -> list[list[float]] | None:
    """The forecast track: the LineString of the longest forecast period
    (`fcstpd` 120 over 72), else the longest line. The points between NHC's
    forecast times are a drawing aid, not a forecast (NHC's own note)."""
    best, best_key = None, None
    for pm in placemarks(kml):
        pd = _num(pm["data"].get("fcstpd")) or 0
        for g in pm["geoms"]:
            if g[0] == "LineString":
                key = (pd, len(g[1]))
                if best_key is None or key > best_key:
                    best, best_key = g[1], key
    return best


def wind_extent(kml: bytes) -> dict[str, list]:
    """{"34": [polygon, ...], "50": [...], "64": [...]} from an initial-radii file;
    each placemark is named by its wind threshold in kt."""
    out: dict[str, list] = {}
    for pm in placemarks(kml):
        t = (pm["name"] or "").strip()
        if t not in EVENT_WIND:
            continue
        for g in pm["geoms"]:
            if g[0] == "Polygon":
                out.setdefault(t, []).append(g[1])
    return out


def best_track_points(kml: bytes) -> list[list[float]]:
    """The best track's 6-hourly positions in document order (chronological in
    every file measured). Only positions: their values are HTML text."""
    return [g[1] for pm in placemarks(kml) for g in pm["geoms"] if g[0] == "Point"]


# ---------------------------------------------------------------- sources

def _link(s: dict, key: str) -> str | None:
    v = s.get(key)
    u = v.get("kmzFile") if isinstance(v, dict) else None
    return u if isinstance(u, str) and u.startswith("https://") else None


def nhc_storms(doc: Any) -> list[dict[str, Any]]:
    """CurrentStorms.json -> one record per storm with a valid id and position."""
    out = []
    storms = doc.get("activeStorms") if isinstance(doc, dict) else None
    for s in storms if isinstance(storms, list) else []:
        if not isinstance(s, dict):
            continue
        sid = s.get("id")
        if not (isinstance(sid, str) and re.fullmatch(r"(al|ep|cp)\d{6}", sid.lower())):
            continue
        lat, lon = _num(s.get("latitudeNumeric")), _num(s.get("longitudeNumeric"))
        if not (_lat_ok(lat) and _lon_ok(lon)):
            continue
        code = s.get("classification") if isinstance(s.get("classification"), str) else None
        kt = _num(s.get("intensity"))
        cone = _link(s, "trackCone")
        adv = _ADV.search(cone or "") or _ADV.search(_link(s, "forecastTrack") or "")
        out.append({
            "key": sid.lower(),
            "name": s.get("name") if isinstance(s.get("name"), str) else sid.upper(),
            "lat": lat, "lon": lon,
            "kt": kt,
            "class_code": code,
            "pressure": _num(s.get("pressure")),
            "move_dir": _num(s.get("movementDir")),
            "move_mph": _num(s.get("movementSpeed")),
            "time": s.get("lastUpdate") if _parse_time(s.get("lastUpdate")) else None,
            "advisory": int(adv.group(1)) if adv else None,
            "links": {k: _link(s, k) for k in ("trackCone", "forecastTrack", "initialWindExtent", "bestTrackGIS")},
            "source": "nhc",
        })
    return out


def eonet_storms(doc: Any, now: datetime, stale_h: float) -> list[dict[str, Any]]:
    """EONET open severeStorms GeoJSON -> one record per storm whose last fix is
    no older than `stale_h` hours. EONET closes storms late (Weather SSOT 302)."""
    feats = doc.get("features") if isinstance(doc, dict) else None
    groups: dict[str, dict] = {}
    for f in feats if isinstance(feats, list) else []:
        if not isinstance(f, dict):
            continue
        p, g = f.get("properties"), f.get("geometry")
        if not (isinstance(p, dict) and isinstance(g, dict) and g.get("type") == "Point"):
            continue
        if p.get("closed"):
            continue
        eid, t = p.get("id"), _parse_time(p.get("date"))
        c = g.get("coordinates")
        if not (isinstance(eid, str) and t and isinstance(c, list) and len(c) >= 2):
            continue
        lon, lat = _num(c[0]), _num(c[1])
        if not (_lat_ok(lat) and _lon_ok(lon)):
            continue
        rec = groups.setdefault(eid, {"title": p.get("title"), "sources": p.get("sources"), "fixes": []})
        kt = _num(p.get("magnitudeValue")) if p.get("magnitudeUnit") == "kts" else None
        rec["fixes"].append((t, lon, lat, kt))
    out = []
    for eid, rec in groups.items():
        fixes = sorted(rec["fixes"], key=lambda x: x[0])
        t, lon, lat, kt = fixes[-1]
        if (now - t).total_seconds() > stale_h * 3600:
            continue
        atcf, ref = None, None
        for s in rec["sources"] if isinstance(rec["sources"], list) else []:
            if isinstance(s, dict):
                atcf = atcf or atcf_from_jtwc(s.get("url"))
                ref = ref or nhc_ref(s.get("url"))
        basin = atcf[:2] if atcf else None
        out.append({
            "key": atcf or eid.lower(),
            "eonet_id": eid,
            "name": storm_name(rec["title"]) or eid,
            "lat": lat, "lon": lon,
            "kt": kt,
            "basin": basin,
            "time": t.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "track": [[x[1], x[2]] for x in fixes],
            "nhc_ref": ref,
            "source": "eonet",
        })
    return out


def merge(nhc: list[dict], eonet: list[dict]) -> list[dict]:
    """NHC wins where both list a storm: by ATCF id, else by NHC's name and year."""
    ids = {s["key"] for s in nhc}
    names = {(str((_parse_time(s["time"]) or datetime.min).year), str(s["name"]).upper()) for s in nhc}
    kept = [e for e in eonet if e["key"] not in ids and not (e["nhc_ref"] and e["nhc_ref"] in names)]
    return sorted(nhc + kept, key=lambda s: s["key"])


# ---------------------------------------------------------------- output

def entity_record(s: dict) -> dict[str, Any]:
    """What one storm's geo_location entity publishes (D15)."""
    kt = s.get("kt")
    if s["source"] == "nhc":
        code = s.get("class_code")
        cls = NHC_CLASS.get(code, code) if code else jtwc_class(kt, s["key"][:2])
        cat = NOT_TROPICAL if code in NHC_NOT_TROPICAL else category(kt)
    else:
        cls = jtwc_class(kt, s.get("basin"))
        cat = category(kt)
    attrs: dict[str, Any] = {
        "identity": s["key"].upper() if s["source"] == "nhc" or s.get("basin") else s["eonet_id"],
        "marker_label": s["name"],
        "map_layer": "weather",
        "storm_source": "nhc" if s["source"] == "nhc" else "jtwc_eonet",
        "attribution": ATTRIBUTION_NHC if s["source"] == "nhc" else ATTRIBUTION_EONET,
    }
    if cat:
        attrs["storm_category"] = cat
        attrs["marker_color"] = CATEGORY_COLOURS[cat]
    if cls:
        attrs["storm_class"] = cls
    if kt is not None:
        attrs["max_wind_kmh"] = round(kt * KT_KMH, 1)
    if s.get("pressure") is not None:
        attrs["pressure_hpa"] = int(round(s["pressure"]))
    mph = s.get("move_mph")
    if mph is not None and mph > 0 and s.get("move_dir") is not None:
        attrs["course_deg"] = float(s["move_dir"]) % 360
        attrs["speed_kmh"] = round(mph * MPH_KMH, 1)
    if s.get("time"):
        attrs["last_seen"] = s["time"]
    if s.get("advisory") is not None:
        attrs["advisory_number"] = s["advisory"]
    name = f"{cls} {s['name']}" if cls else s["name"]
    return {"key": s["key"], "name": name, "lat": s["lat"], "lon": s["lon"], "attrs": attrs}


def _poly(rings: list, ref: float) -> dict:
    return {"type": "Polygon", "coordinates": [unwrap(r, ref) for r in rings]}


def shapes_for(s: dict, products: dict[str, Any]) -> list[dict]:
    """D12 `polygons` items for one storm, lines included (D15). `products` holds
    the storm's parsed NHC files: cone, forecast, wind, past."""
    ref = s["lon"]
    out: list[dict] = []
    for rings in products.get("cone") or []:
        out.append({"event": EVENT_CONE, "storm": s["key"], **_poly(rings, ref)})
    for t in ("34", "50", "64"):
        for rings in (products.get("wind") or {}).get(t, []):
            out.append({"event": EVENT_WIND[t], "storm": s["key"], **_poly(rings, ref)})
    past = products.get("past") if s["source"] == "nhc" else s.get("track")
    if past and len(past) >= 2:
        out.append({"event": EVENT_PAST, "storm": s["key"], "type": "LineString",
                    "coordinates": unwrap(past, ref)})
    fc = products.get("forecast")
    if fc and len(fc) >= 2:
        out.append({"event": EVENT_FORECAST, "storm": s["key"], "type": "LineString",
                    "coordinates": unwrap(fc, ref)})
    return out
