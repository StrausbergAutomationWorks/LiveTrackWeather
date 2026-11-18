"""Earthquakes for the shared map and the watched places (Weather SSOT item 352; contract D20 in
06_MAP_CONTRACT_OVERLAYS.md). Pure Python, no Home Assistant import; usgs_coordinator.py fetches.

Decided by Lee 2026-11-17 (18:16 and 19:27 CST), on 20_Research/REPORT_usgs_survey_20261117.md sections 5-6:
  * every event of USGS's all_day feed on the map: markers for M4.5 and up or felt, the rest as a D19 point layer with
    a minimum-magnitude option (default none);
  * ShakeMap's intensity contours for the biggest, through D12 (the rule is proposed: SHAKEMAP_MMI, SHAKEMAP_MAG,
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
from .places import distance_m

QUAKE_FEED_URL = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_day.geojson"
QUAKE_ATTRIBUTION = "Earthquakes: USGS Earthquake Hazards Program, earthquake.usgs.gov"
SHAKE_ATTRIBUTION = "Shaking: USGS ShakeMap, earthquake.usgs.gov"

MARKER_MAG = 4.5            # markers from this magnitude, or for any felt quake (Lee)
# (magnitude from, km within): "Alert at X" (Lee 19:27)
ALERT_RULES = ((7.0, 600.0), (6.0, 300.0), (5.0, 150.0), (4.0, 50.0))
# ShakeMap lines (proposed): a marker's quake with a ShakeMap whose maximum intensity reaches strong shaking (MMI 6), or
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
