"""Earthquakes for the shared map and the watched places (Weather SSOT item 352; contract D20 in
06_MAP_CONTRACT_OVERLAYS.md). Pure Python, no Home Assistant import; usgs_coordinator.py fetches.

Decided by Lee 2026-11-17 (18:16 and 19:27 CST), on 20_Research/REPORT_usgs_survey_20261117.md sections 5-6:
  * every event of USGS's all_day feed on the map: markers for M4.5 and up or felt, the rest as a D19 point layer with
    a minimum-magnitude option (default none);
  * ShakeMap's intensity contours for the biggest, through D12 (the rule confirmed by Lee 2026-11-17 20:44: SHAKEMAP_MMI, SHAKEMAP_MAG,
    SHAKEMAP_MAX);
  * "Alert at X" on for a quake of M4.0+ within 50 km, M5.0+ within 150, M6.0+ within 300, M7.0+ within 600
    (epicentral distance; MEASURED basis: report section 5.1), counted whatever the CAP-severity setting.

The feed carries quarry blasts and explosions too (`type`); they are points only, never markers or alerts.
"""

from __future__ import annotations

import math
import re
from datetime import datetime, timezone
from typing import Any

from .hazards import bearing
from .places import contains, distance_m

QUAKE_FEED_URL = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_day.geojson"
QUAKE_ATTRIBUTION = "Earthquakes: USGS Earthquake Hazards Program, earthquake.usgs.gov"
SHAKE_ATTRIBUTION = "Shaking: USGS ShakeMap, earthquake.usgs.gov"

MARKER_MAG = 4.5            # markers from this magnitude, or for any felt quake (Lee)
# (magnitude from, km within): "Alert at X" (Lee 19:27)
ALERT_RULES = ((7.0, 600.0), (6.0, 300.0), (5.0, 150.0), (4.0, 50.0))
# ShakeMap lines (confirmed by Lee 2026-11-17 20:44): a marker's quake with a ShakeMap whose maximum intensity reaches strong shaking (MMI 6), or
# M6.0+, at most the five largest.
SHAKEMAP_MMI = 6.0
SHAKEMAP_MAG = 6.0
SHAKEMAP_MAX = 5

MARKER_COLOURS = ((7.0, "#7F0000"), (6.0, "#C2185B"), (4.5, "#6A1B9A"))
MARKER_FELT_COLOUR = "#9575CD"

QUAKE_STYLES = {
    "m_lt2": {"color": "#D1C4E9", "label": "Earthquake, below M2", "radius": 2, "outline": "#4A148C"},
    "m2": {"color": "#B39DDB", "label": "Earthquake, M2", "radius": 3, "outline": "#4A148C"},
    "m3": {"color": "#9575CD", "label": "Earthquake, M3", "radius": 4, "outline": "#4A148C"},
    "m4": {"color": "#6A1B9A", "label": "Earthquake, M4 and up", "radius": 5, "outline": "#4A148C"},
    "other": {"color": "#9E9E9E", "label": "Explosion or quarry blast", "radius": 2, "outline": "#616161"},
}
QUAKE_COLUMNS = [{"key": "mag", "label": "Magnitude"}, {"key": "place", "label": "Place"},
                 {"key": "time", "label": "Time (UTC)"}, {"key": "depth", "label": "Depth (km)"},
                 {"key": "status", "label": "Status"}]

# ShakeMap's intensity words (USGS's scale: II-III weak, IV light, V moderate, VI strong, VII very strong, VIII severe,
# IX violent, X+ extreme)
_ROMAN = ("I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X")
_WORDS = ("not felt", "weak", "weak", "light", "moderate", "strong", "very strong", "severe", "violent", "extreme")
# USGS's own contour colours, if a file lacks them: those read from one cont_mmi.json (the 2026-10-22 M7.0 near Nagqu,
# 3.5-8.0); a value not read here is grey.
SHAKE_FALLBACK = {3.5: "#90f2ff", 4.0: "#80ffff", 4.5: "#7cffc7", 5.0: "#7cff90", 5.5: "#bbff4a", 6.0: "#ffff00",
                  6.5: "#ffe200", 7.0: "#ffc600", 7.5: "#ffaa00", 8.0: "#ff9100"}
SHAKE_CASING = "#424242"
_HEX = re.compile(r"^#[0-9A-Fa-f]{6}$")


def min_magnitude(option: Any) -> float | None:
    """The option `quake_min_magnitude`: a number from 0 to 9, else None (every event)."""
    if isinstance(option, bool) or not isinstance(option, (int, float)):
        return None
    return float(option) if 0 <= option <= 9 else None


def _num(v: Any) -> float | None:
    return float(v) if isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v) else None


def _when(ms: Any) -> datetime | None:
    v = _num(ms)
    return datetime.fromtimestamp(v / 1000, tz=timezone.utc) if v is not None else None


def _key(event_id: str) -> str:
    return re.sub(r"[^a-z0-9]", "_", event_id.lower())


def parse_feed(doc: Any) -> list[dict[str, Any]] | None:
    """USGS's summary GeoJSON -> one dict per event with a position and a magnitude; None when it is not the feed."""
    if not isinstance(doc, dict) or not isinstance(doc.get("features"), list):
        return None
    out = []
    for f in doc["features"]:
        if not isinstance(f, dict) or not isinstance(f.get("properties"), dict):
            continue
        p, g = f["properties"], f.get("geometry") or {}
        c = g.get("coordinates") if isinstance(g, dict) else None
        if not isinstance(c, list) or len(c) < 2 or not isinstance(f.get("id"), str) or not f["id"]:
            continue
        lon, lat, mag = _num(c[0]), _num(c[1]), _num(p.get("mag"))
        if lon is None or lat is None or mag is None or not (-90 <= lat <= 90 and -180 <= lon <= 180):
            continue
        when = _when(p.get("time"))
        if when is None:
            continue
        types = {t for t in (p.get("types") or "").split(",") if t}
        out.append({
            "id": f["id"], "key": _key(f["id"]), "mag": mag, "mag_type": p.get("magType"),
            "place": p.get("place") or None, "title": p.get("title") or f"M {mag:g}", "time": when,
            "updated": _when(p.get("updated")) or when, "lat": lat, "lon": lon,
            "depth": _num(c[2]) if len(c) > 2 else None,
            "felt": int(p["felt"]) if _num(p.get("felt")) is not None else None,
            "cdi": _num(p.get("cdi")), "mmi": _num(p.get("mmi")),
            "alert": p.get("alert") if isinstance(p.get("alert"), str) else None,
            "tsunami": p.get("tsunami") == 1, "status": p.get("status") or None,
            "type": p.get("type") or "earthquake",
            "url": p["url"] if isinstance(p.get("url"), str) and p["url"].startswith("https://") else None,
            "detail": p["detail"] if isinstance(p.get("detail"), str) and p["detail"].startswith("https://") else None,
            "types": types,
        })
    return out


def is_quake(ev: dict[str, Any]) -> bool:
    return ev["type"] == "earthquake"


def is_marker(ev: dict[str, Any]) -> bool:
    """M4.5 and up, or felt (Lee)."""
    return is_quake(ev) and (ev["mag"] >= MARKER_MAG or (ev["felt"] or 0) > 0)


def marker_colour(ev: dict[str, Any]) -> str:
    for mag, colour in MARKER_COLOURS:
        if ev["mag"] >= mag:
            return colour
    return MARKER_FELT_COLOUR


def _utc(t: datetime) -> str:
    return t.astimezone(timezone.utc).strftime("%Y-%m-%d %H:%M")


def roman(mmi: float) -> str:
    """6.0 -> 'VI, strong'; 6.5 -> 'VI-VII, strong to very strong'."""
    lo = max(1, min(10, int(math.floor(mmi + 1e-9))))
    if mmi - lo >= 0.25 and lo < 10:
        w1, w2 = _WORDS[lo - 1], _WORDS[lo]
        return f"{_ROMAN[lo - 1]}-{_ROMAN[lo]}, {w1}" + (f" to {w2}" if w2 != w1 else "")
    return f"{_ROMAN[lo - 1]}, {_WORDS[lo - 1]}"


def quake_record(ev: dict[str, Any]) -> dict[str, Any]:
    """The marker's record for geo_location.py: key, name, position, attributes (D20)."""
    lines = [f"{_utc(ev['time'])} UTC" + (f", depth {ev['depth']:.0f} km" if ev["depth"] is not None else "")]
    if ev["felt"]:
        lines.append(f"Felt reports: {ev['felt']}" + (f", community intensity {roman(ev['cdi'])}"
                                                     if ev["cdi"] is not None else ""))
    if ev["mmi"] is not None:
        lines.append(f"ShakeMap's strongest shaking: {roman(ev['mmi'])}")
    if ev["alert"]:
        lines.append(f"PAGER alert: {ev['alert']}")
    if ev["tsunami"]:
        lines.append("Tsunami flag set: the quake is in a region and of a size where NOAA's tsunami centres assess "
                     "it. It is not a warning; warnings come from NOAA (tsunami.gov).")
    lines.append(f"{'Reviewed' if ev['status'] == 'reviewed' else 'Automatic, may be revised'}. USGS")
    attrs: dict[str, Any] = {
        "identity": ev["id"], "marker_label": f"{ev['mag']:.1f}", "marker_color": marker_colour(ev),
        "map_layer": "fixed", "magnitude": ev["mag"], "magnitude_type": ev["mag_type"], "place": ev["place"],
        "time": ev["time"].isoformat(), "depth_km": ev["depth"], "felt": ev["felt"],
        "community_intensity": ev["cdi"], "max_intensity": ev["mmi"], "pager_alert": ev["alert"],
        "tsunami_flag": ev["tsunami"], "review_status": ev["status"], "last_seen": ev["updated"].isoformat(),
        "marker_info": {"title": ev["title"][:200], "text": "\n".join(lines)[:4000]},
        "attribution": QUAKE_ATTRIBUTION,
    }
    if ev["url"]:
        attrs["marker_links"] = [{"label": "USGS event page", "url": ev["url"]}]
    return {"key": ev["key"], "name": ev["title"], "lat": ev["lat"], "lon": ev["lon"], "attrs": attrs}


def point_style(ev: dict[str, Any]) -> str:
    if not is_quake(ev):
        return "other"
    m = ev["mag"]
    return "m4" if m >= 4 else "m3" if m >= 3 else "m2" if m >= 2 else "m_lt2"


def quake_points(events: list[dict[str, Any]], min_mag: float | None) -> list[list[Any]]:
    """D19 points [lon, lat, style, magnitude, place, time, depth, status] for every event not drawn as a marker, at or
    above `min_mag` (None: all)."""
    out = []
    for ev in events:
        if is_marker(ev) or (min_mag is not None and ev["mag"] < min_mag):
            continue
        out.append([round(ev["lon"], 4), round(ev["lat"], 4), point_style(ev), round(ev["mag"], 2), ev["place"],
                    _utc(ev["time"]), round(ev["depth"], 1) if ev["depth"] is not None else None, ev["status"]])
    return out


def shakemap_candidates(events: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """The markers' quakes whose ShakeMap is drawn: with a ShakeMap, and MMI 6+ or M6.0+; the largest SHAKEMAP_MAX."""
    c = [ev for ev in events if is_marker(ev) and "shakemap" in ev["types"] and ev["detail"]
         and ((ev["mmi"] or 0) >= SHAKEMAP_MMI or ev["mag"] >= SHAKEMAP_MAG)]
    c.sort(key=lambda ev: (-ev["mag"], ev["id"]))
    return c[:SHAKEMAP_MAX]


def contours_url(detail: Any) -> str | None:
    """The preferred ShakeMap's cont_mmi.json in an event's detail GeoJSON (the first listed is USGS's preferred)."""
    try:
        sm = detail["properties"]["products"]["shakemap"][0]
        url = sm["contents"]["download/cont_mmi.json"]["url"]
    except (KeyError, IndexError, TypeError):
        return None
    return url if isinstance(url, str) and url.startswith("https://") else None


def _round_lines(geom: dict[str, Any]) -> dict[str, Any] | None:
    t, coords = geom.get("type"), geom.get("coordinates")
    if t == "LineString":
        coords, t = [coords], "MultiLineString"
    if t != "MultiLineString" or not isinstance(coords, list):
        return None
    lines = []
    for line in coords:
        pts = []
        for pt in line if isinstance(line, list) else []:
            if isinstance(pt, list) and len(pt) >= 2 and _num(pt[0]) is not None and _num(pt[1]) is not None:
                q = [round(pt[0], 3), round(pt[1], 3)]
                if not pts or pts[-1] != q:
                    pts.append(q)
        if len(pts) >= 2:
            lines.append(pts)
    return {"type": "MultiLineString", "coordinates": lines} if lines else None


def shake_event(value: float) -> str:
    return f"Intensity {value:.1f}"


def shakemap_shapes(doc: Any, ev: dict[str, Any]) -> tuple[list[dict[str, Any]], dict[str, dict[str, Any]]]:
    """cont_mmi.json -> (D12 polygons items, styles for their events). Lines only; empty when the file is not one."""
    items: list[dict[str, Any]] = []
    styles: dict[str, dict[str, Any]] = {}
    if not isinstance(doc, dict) or not isinstance(doc.get("features"), list):
        return items, styles
    for f in doc["features"]:
        if not isinstance(f, dict):
            continue
        props = f.get("properties") or {}
        value = _num(props.get("value"))
        geom = _round_lines(f.get("geometry") or {})
        if value is None or geom is None or props.get("units", "mmi") != "mmi":
            continue
        name = shake_event(value)
        colour = props.get("color") if isinstance(props.get("color"), str) and _HEX.match(props["color"]) else \
            SHAKE_FALLBACK.get(round(value * 2) / 2, "#808080")
        styles[name] = {"color": colour.upper(), "priority": int(round((10.5 - value) * 2)), "casing": SHAKE_CASING}
        items.append({"event": name, "quake": ev["key"], **geom,
                      "info": {"title": f"Shaking: intensity {roman(value)}",
                               "text": f"{ev['title']}\n{_utc(ev['time'])} UTC\nUSGS ShakeMap"}})
    return items, styles


def _severity(mag: float) -> str:
    """For ordering a place's list only: a quake record counts whatever the CAP-severity setting is."""
    return "Extreme" if mag >= 7 else "Severe" if mag >= 6 else "Moderate"


def alert_records(events: list[dict[str, Any]], lat: float, lon: float) -> list[dict[str, Any]]:
    """"Alert at X" records: each earthquake of the feed within its magnitude's distance of the place, nearest first."""
    out = []
    for ev in events:
        if not is_quake(ev):
            continue
        reach = next((km for mag, km in ALERT_RULES if ev["mag"] >= mag), None)
        if reach is None:
            continue
        km = distance_m(lat, lon, ev["lat"], ev["lon"]) / 1000
        if km > reach:
            continue
        way = bearing(lat, lon, ev["lat"], ev["lon"])
        out.append({
            "source": "USGS", "id": ev["url"] or f"usgs {ev['id']}",
            "event": f"Earthquake M{ev['mag']:.1f}, {km:.0f} km {way}",
            "severity": _severity(ev["mag"]),
            "headline": (f"{ev['title']}: {km:.0f} km {way} of the place at {_utc(ev['time'])[11:]} UTC"
                         + (f", depth {ev['depth']:.0f} km" if ev["depth"] is not None else "") + "."),
            "onset": ev["time"].isoformat(), "ends": None, "priority": 0, "always": True, "km": round(km, 1),
        })
    out.sort(key=lambda r: r["km"])
    return out


# ---------------------------------------------------------------------------------------------- elevated volcanoes
# Weather SSOT item 352 step 2 (Lee 19:27): markers for every volcano HANS lists as elevated (Advisory/Yellow and up);
# "Alert at X" on while the place is inside the National Volcanic Threat Layer zone of a volcano at Watch/Orange or up,
# unscaled. The layer ships as data/volcano_threat_zones.json.gz, keyed by GVPJoinCode = HANS vnum (report section 6).

HANS_BASE = "https://volcanoes.usgs.gov/hans-public/api/volcano"
HANS_ELEVATED_URL = f"{HANS_BASE}/getElevatedVolcanoes"
HANS_CAP_URL = f"{HANS_BASE}/getCapElevated"
HANS_US_URL = f"{HANS_BASE}/getUSVolcanoes"
VOLCANO_ATTRIBUTION = "Volcanoes: USGS Volcano Hazards Program, volcanoes.usgs.gov"
VOLCANO_COLOURS = {"YELLOW": "#FFD600", "ORANGE": "#FF9100", "RED": "#D50000"}
_LEVEL_COLOUR = {"ADVISORY": "YELLOW", "WATCH": "ORANGE", "WARNING": "RED"}
# Lee: Watch/Orange and up. HANS gives a ground alert level and an aviation colour code, which can differ; either at
# Watch/Orange or above counts.
ALERT_LEVELS = ("WATCH", "WARNING")
ALERT_COLOURS = ("ORANGE", "RED")


def _https(v: Any) -> str | None:
    return v if isinstance(v, str) and v.startswith("https://") else None


def us_volcanoes(doc: Any) -> dict[str, dict[str, Any]] | None:
    """getUSVolcanoes -> {vnum: {name, lat, lon, elevation_m, threat, url}}; None when it is not the list."""
    if not isinstance(doc, list):
        return None
    out = {}
    for v in doc:
        if not isinstance(v, dict) or not isinstance(v.get("vnum"), str):
            continue
        lat, lon = _num(v.get("latitude")), _num(v.get("longitude"))
        if lat is None or lon is None or not (-90 <= lat <= 90 and -180 <= lon <= 180):
            continue
        out[v["vnum"]] = {"name": v.get("volcano_name"), "lat": lat, "lon": lon,
                          "elevation_m": _num(v.get("elevation_meters")), "threat": v.get("nvews_threat") or None,
                          "url": _https(v.get("volcano_url"))}
    return out


def _sent(v: Any) -> str | None:
    """HANS's 'sent_utc' ('2026-11-13 21:04:48') as an ISO instant."""
    try:
        return datetime.strptime(v, "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc).isoformat()
    except (TypeError, ValueError):
        return None


def elevated(elev: Any, cap: Any, us: dict[str, dict[str, Any]] | None) -> list[dict[str, Any]] | None:
    """getElevatedVolcanoes (+ getCapElevated's CAP fields and synopsis, where it lists the volcano as elevated now),
    joined to getUSVolcanoes by vnum for the position. None when the elevated list is not one; a volcano with no
    position is left out."""
    if not isinstance(elev, list):
        return None
    caps = {c["vnum"]: c for c in (cap if isinstance(cap, list) else [])
            if isinstance(c, dict) and isinstance(c.get("vnum"), str) and c.get("is_elevated_cap") is True}
    out = []
    for v in elev:
        if not isinstance(v, dict) or not isinstance(v.get("vnum"), str):
            continue
        where = (us or {}).get(v["vnum"])
        if where is None:
            continue
        level = (v.get("alert_level") or "").upper() or None
        colour = (v.get("color_code") or "").upper() or None
        c = caps.get(v["vnum"], {})
        out.append({"vnum": v["vnum"], "name": v.get("volcano_name") or where["name"], "lat": where["lat"],
                    "lon": where["lon"], "level": level, "colour": colour, "since": _sent(v.get("sent_utc")),
                    "observatory": v.get("obs_fullname") or None, "notice_url": _https(v.get("notice_url")),
                    "synopsis": c.get("synopsis") or None, "cap_severity": c.get("cap_severity") or None,
                    "url": where["url"], "threat": where["threat"], "elevation_m": where["elevation_m"]})
    return out


def volcano_colour(v: dict[str, Any]) -> str:
    code = v["colour"] if v["colour"] in VOLCANO_COLOURS else _LEVEL_COLOUR.get(v["level"] or "", "YELLOW")
    return VOLCANO_COLOURS[code]


def volcano_record(v: dict[str, Any]) -> dict[str, Any]:
    """The marker's record for geo_location.py (D20)."""
    title = f"{v['name']}: {v['level'] or '?'} / {v['colour'] or '?'}"
    lines = []
    if v["since"]:
        lines.append(f"Since {v['since'][:16].replace('T', ' ')} UTC")
    if v["synopsis"]:
        lines.append(v["synopsis"])
    if v["observatory"]:
        lines.append(v["observatory"])
    lines.append("Alert level for people on the ground; colour code for aviation. USGS")
    links = [x for x in ({"label": "HANS notice", "url": v["notice_url"]}, {"label": "Volcano page", "url": v["url"]})
             if x["url"]]
    attrs: dict[str, Any] = {
        "identity": v["vnum"], "marker_label": v["name"], "marker_color": volcano_colour(v), "map_layer": "fixed",
        "alert_level": v["level"], "color_code": v["colour"], "since": v["since"], "observatory": v["observatory"],
        "threat": v["threat"], "elevation_m": v["elevation_m"], "synopsis": v["synopsis"],
        "marker_info": {"title": title[:200], "text": "\n".join(lines)[:4000]}, "attribution": VOLCANO_ATTRIBUTION,
    }
    if links:
        attrs["marker_links"] = links
    return {"key": v["vnum"], "name": v["name"], "lat": v["lat"], "lon": v["lon"], "attrs": attrs}


def threat_zones(doc: Any) -> dict[str, list[dict[str, Any]]]:
    """The shipped threat-layer file -> {vnum: [{name, zone, threat, geometry}]}; empty when it is not one."""
    z = doc.get("zones") if isinstance(doc, dict) else None
    return {k: v for k, v in z.items() if isinstance(v, list)} if isinstance(z, dict) else {}


def counts_for_places(v: dict[str, Any]) -> bool:
    """Watch/Orange and up (Lee): the alert level or the colour code."""
    return v["level"] in ALERT_LEVELS or v["colour"] in ALERT_COLOURS


def volcano_alert_records(volcanoes: list[dict[str, Any]], zones: dict[str, list[dict[str, Any]]], lat: float,
                          lon: float) -> list[dict[str, Any]]:
    """"Alert at X" records: each volcano at Watch/Orange or up whose threat-layer zone holds the place."""
    out = []
    for v in volcanoes:
        if not counts_for_places(v):
            continue
        hit = next((z for z in zones.get(v["vnum"], []) if contains(z.get("geometry"), lat, lon)), None)
        if hit is None:
            continue
        km = distance_m(lat, lon, v["lat"], v["lon"]) / 1000
        out.append({
            "source": "USGS", "id": v["notice_url"] or f"hans {v['vnum']}",
            "event": f"Volcano: {v['name']}, {v['level'] or '?'} / {v['colour'] or '?'}",
            "severity": v["cap_severity"] or "Unknown",
            "headline": (f"{v['name']} is at {v['level'] or '?'} / {v['colour'] or '?'}, and the place is inside its "
                         f"{hit.get('zone', 'hazard').lower()} hazard zone (USGS National Volcanic Threat Layer), "
                         f"{km:.0f} km from the volcano." + (f" {v['synopsis']}" if v["synopsis"] else "")),
            "onset": v["since"], "ends": None, "priority": 0, "always": True, "km": round(km, 1),
        })
    return out


# ------------------------------------------------------------------------------------- rivers forecast into flood
# Weather SSOT item 352 step 3 (Lee 19:27): gauges NOAA's National Water Prediction Service forecasts at minor flood
# or worse, as markers. Not USGS's data, but part of the same build; kept here with it. MEASURED 2026-11-18: every field
# is a string, empty when absent; `secvalue` -999 when there is no flow; `fcsttime` 'YYYY-MM-DD HH:MM:SS', read as UTC
# (INFERRED: the service does not say, and its issuance times sit an hour or two before now in UTC).

RIVER_URL = ("https://mapservices.weather.noaa.gov/eventdriven/rest/services/water/riv_gauges/MapServer/15/query")
RIVER_PARAMS = {"where": "status IN ('minor','moderate','major')", "outFields": "*", "f": "geojson",
                "returnGeometry": "true"}
RIVER_ATTRIBUTION = "River forecasts: NOAA National Water Prediction Service, water.noaa.gov"
RIVER_COLOURS = {"minor": "#FF9900", "moderate": "#FF0000", "major": "#CC33FF"}


def _fnum(v: Any) -> float | None:
    """A NWPS string field as a number; None for '' or the -999 sentinel."""
    try:
        x = float(v)
    except (TypeError, ValueError):
        return None
    return None if x <= -999 or not math.isfinite(x) else x


def _utc_text(v: Any) -> str | None:
    try:
        return datetime.strptime(v, "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc).isoformat()
    except (TypeError, ValueError):
        return None


def river_name(location: str, waterbody: str) -> str:
    if location and waterbody and waterbody.lower() not in location.lower() and "gauge" not in waterbody.lower():
        return f"{waterbody} at {location}"
    return location or waterbody


def river_gauges(doc: Any) -> list[dict[str, Any]] | None:
    """The map service's GeoJSON -> one dict per gauge at minor flood or worse; None when it is not GeoJSON."""
    if not isinstance(doc, dict) or not isinstance(doc.get("features"), list):
        return None
    out = []
    for f in doc["features"]:
        p = f.get("properties") if isinstance(f, dict) else None
        if not isinstance(p, dict):
            continue
        status = (p.get("status") or "").lower()
        lid = (p.get("gaugelid") or "").strip()
        lat, lon = _fnum(p.get("latitude")), _fnum(p.get("longitude"))
        if status not in RIVER_COLOURS or not lid or lat is None or lon is None \
                or not (-90 <= lat <= 90 and -180 <= lon <= 180):
            continue
        location, water = (p.get("location") or "").strip(), (p.get("waterbody") or "").strip()
        out.append({"lid": lid.upper(), "key": re.sub(r"[^a-z0-9]", "_", lid.lower()), "status": status,
                    "name": river_name(location, water) or lid.upper(), "waterbody": water or None,
                    "state": p.get("state") or None, "lat": lat, "lon": lon, "forecast": _fnum(p.get("forecast")),
                    "units": p.get("units") or None, "time": _utc_text(p.get("fcsttime")),
                    "issued": _utc_text(p.get("fcstissunc")), "action": _fnum(p.get("action")),
                    "flood": _fnum(p.get("flood")), "moderate": _fnum(p.get("moderate")),
                    "major": _fnum(p.get("major")), "flow": _fnum(p.get("secvalue")),
                    "flow_units": p.get("secunit") or None, "url": _https(p.get("url"))})
    return out


def _g(v: float | None) -> str:
    return f"{v:g}" if v is not None else "?"


def river_record(g: dict[str, Any]) -> dict[str, Any]:
    """The marker's record for geo_location.py (D20)."""
    u = g["units"] or ""
    when = (datetime.fromisoformat(g["time"]).strftime("%H:%M UTC %d %b") if g["time"] else "a time not given")
    lines = [f"Forecast: {g['status']} flood, {_g(g['forecast'])} {u} at {when}".replace(" ,", ","),
             "Flood stages: " + ", ".join(f"{k} {_g(g[k])} {u}".strip() for k in ("action", "flood", "moderate", "major")
                                          if g[k] is not None)]
    if g["flow"] is not None:
        lines.append(f"Forecast flow: {_g(g['flow'])} {g['flow_units'] or ''}".strip())
    if g["waterbody"]:
        lines.append(g["waterbody"] + (f", {g['state']}" if g["state"] else ""))
    lines.append("NOAA NWPS")
    attrs: dict[str, Any] = {
        "identity": g["lid"], "marker_label": g["status"].capitalize(), "marker_color": RIVER_COLOURS[g["status"]],
        "map_layer": "fixed", "flood_category": g["status"], "waterbody": g["waterbody"],
        "forecast_stage": g["forecast"], "stage_units": g["units"], "forecast_time": g["time"],
        "forecast_issued": g["issued"], "action_stage": g["action"], "flood_stage": g["flood"],
        "moderate_stage": g["moderate"], "major_stage": g["major"],
        "marker_info": {"title": g["name"][:200], "text": "\n".join(lines)[:4000]}, "attribution": RIVER_ATTRIBUTION,
    }
    if g["url"]:
        attrs["marker_links"] = [{"label": "NWPS gauge page", "url": g["url"]}]
    return {"key": g["key"], "name": g["name"], "lat": g["lat"], "lon": g["lon"], "attrs": attrs}


# ---------------------------------------------------------------------------------------- elevation at a place
# Weather SSOT item 352 step 4 (Lee 19:27): "Elevation at X" from USGS's 3DEP Elevation Point Query Service, checked at
# start-up, then only after a move of more than ELEV_MOVE_M and no sooner than ELEV_GAP_S. MEASURED 2026-11-18
# (bin\\ltw352e_probe.py, 14 public places): a value in the US, Puerto Rico, Guam, Alaska, Hawaii, on Lake Michigan
# (its surface), and also at Toronto, Windsor ON and Mexico City (coarser data, 10-31 m); outside its coverage
# (Oslo, the open Gulf) HTTP 200 with the TEXT "Invalid or missing input parameters.", and in the open Pacific
# "Call failed. ..."; 0.3-15 s per answer. `resolution` is metres for some rasters and degrees for others.

EPQS_URL = "https://epqs.nationalmap.gov/v1/json"
ELEV_ATTRIBUTION = "Elevation: USGS 3D Elevation Program, nationalmap.gov"
ELEV_MOVE_M = 500
ELEV_GAP_S = 600
_M_PER_DEG = 111320.0


def epqs_params(lat: float, lon: float) -> dict[str, str]:
    return {"x": f"{lon:.4f}", "y": f"{lat:.4f}", "wkid": "4326", "units": "Meters", "includeDate": "false"}


def parse_elevation(doc: Any) -> dict[str, Any] | None:
    """An EPQS answer (parsed JSON) -> {"m": metres, "resolution_m": metres or None}; None when it holds no elevation
    (USGS answers plain text outside its coverage, which arrives here as None, and -1000000 for no data)."""
    if not isinstance(doc, dict):
        return None
    try:
        m = float(doc.get("value"))
    except (TypeError, ValueError):
        return None
    if not math.isfinite(m) or m <= -1000:
        return None
    res = _num(doc.get("resolution"))
    if res is not None:
        res = res * _M_PER_DEG if res < 0.01 else res     # degrees (1/3 arc-second is 0.0000926) or metres
        res = round(res, 1)
    return {"m": round(m, 1), "resolution_m": res}


def elevation_due(prev_lat: float | None, prev_lon: float | None, prev_at: float | None, failed: bool, lat: float,
                  lon: float, now: float, move_m: float = ELEV_MOVE_M, gap_s: float = ELEV_GAP_S
                  ) -> tuple[bool, float | None]:
    """(ask now, or seconds to wait before a move may be asked about). Never asked: now. A failed ask: again after the
    gap. Otherwise only a move of more than `move_m` from the spot last asked, and not sooner than `gap_s` after it."""
    if prev_at is None or prev_lat is None or prev_lon is None:
        return True, None
    moved = distance_m(lat, lon, prev_lat, prev_lon) > move_m
    if not (moved or failed):
        return False, None
    elapsed = now - prev_at
    if elapsed >= gap_s:
        return True, None
    return False, gap_s - elapsed
