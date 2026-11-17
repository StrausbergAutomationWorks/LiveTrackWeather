"""Is a place inside an alert? (Weather SSOT item 334.) Pure Python, no Home Assistant import.

The rule is NWS's own, and the map's:
  * an alert that carries its own polygon (a storm-based warning) holds a place only inside that polygon,
    never merely because the place is in one of the counties the polygon touches;
  * any other NWS alert holds a place when one of its affectedZones is a zone that holds the place;
  * a MET Norway warning holds a place inside its own polygons.

Which NWS zones hold a place comes from NWS itself (/zones?point=lat,lon), NOT from the simplified shape
file the map draws: MEASURED 2026-11-17 (Weather SSOT 2r) the shape file's ~500 m simplification put a
point on land at Sitka inside a marine zone, while matching by NWS's own zone keys agreed with NWS's
/alerts/active?point= at 38 of 38 points. Holding the shape file in Home Assistant would also cost about
20 MB packed, 140 MB as json.loads gives it.
"""

from __future__ import annotations

import math
from typing import Any

# CAP severity, both NWS and MET Norway. "Unknown" (and anything else) ranks 0.
SEVERITY_RANK = {"Minor": 1, "Moderate": 2, "Severe": 3, "Extreme": 4}
# The option that sets what turns a place's entity on. "all" counts every alert, Unknown severity included.
THRESHOLDS = {"all": 0, "moderate": 2, "severe": 3, "extreme": 4}
DEFAULT_THRESHOLD = "all"

_ZONES_MARKER = "/zones/"


def zone_key(url: str | None) -> str | None:
    """'https://api.weather.gov/zones/forecast/ILZ014' -> 'forecast/ILZ014' (as alerts.zone_key)."""
    if not isinstance(url, str):
        return None
    i = url.find(_ZONES_MARKER)
    return url[i + len(_ZONES_MARKER):] if i >= 0 else None


def zone_keys(doc: Any) -> set[str] | None:
    """The zone keys in an NWS /zones?point= answer; None when the answer is not one.

    MEASURED 2026-11-17: public zones come back as type `public` with an id under /zones/forecast/, marine
    ones as `coastal` or `offshore`, also under /zones/forecast/, so the id's path is the key the alerts use.
    """
    if not isinstance(doc, dict) or not isinstance(doc.get("features"), list):
        return None
    keys = set()
    for f in doc["features"]:
        if not isinstance(f, dict):
            continue
        k = zone_key(f.get("id") or (f.get("properties") or {}).get("@id"))
        if k:
            keys.add(k)
    return keys


def _rings(geom: Any) -> list:
    if not isinstance(geom, dict):
        return []
    if geom.get("type") == "Polygon":
        return [geom.get("coordinates") or []]
    if geom.get("type") == "MultiPolygon":
        return geom.get("coordinates") or []
    return []


def _in_ring(lon: float, lat: float, ring: list) -> bool:
    inside = False
    n = len(ring)
    if n < 3:
        return False
    j = n - 1
    for i in range(n):
        xi, yi = ring[i][0], ring[i][1]
        xj, yj = ring[j][0], ring[j][1]
        if (yi > lat) != (yj > lat) and lon < (xj - xi) * (lat - yi) / (yj - yi) + xi:
            inside = not inside
        j = i
    return inside


def contains(geom: Any, lat: float, lon: float) -> bool:
    """A GeoJSON Polygon or MultiPolygon ([lon, lat] order) holds the point; holes are honoured."""
    for poly in _rings(geom):
        if poly and _in_ring(lon, lat, poly[0]) and not any(_in_ring(lon, lat, h) for h in poly[1:]):
            return True
    return False


def distance_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Great-circle distance in metres."""
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp, dl = p2 - p1, math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * 6371008.8 * math.asin(min(1.0, math.sqrt(a)))


def cached_keys(cache: list[dict[str, Any]], lat: float, lon: float, now: float,
                reuse_m: float, keep_s: float) -> set[str] | None:
    """Zone keys kept for a point asked within `reuse_m` of this one and less than `keep_s` ago; None if none.
    The nearest such point wins."""
    best = None
    for e in cache:
        try:
            if now - float(e["at"]) >= keep_s:
                continue
            d = distance_m(lat, lon, float(e["lat"]), float(e["lon"]))
        except (KeyError, TypeError, ValueError):
            continue
        if d <= reuse_m and (best is None or d < best[0]):
            best = (d, e)
    return set(best[1].get("keys") or ()) if best else None


def remember(cache: list[dict[str, Any]], lat: float, lon: float, keys: set[str], now: float,
             reuse_m: float, max_n: int) -> list[dict[str, Any]]:
    """The cache with this answer added: an older answer for the same spot (within reuse_m) is replaced,
    and only the newest `max_n` are kept."""
    kept = []
    for e in cache:
        try:
            if distance_m(lat, lon, float(e["lat"]), float(e["lon"])) <= reuse_m:
                continue
        except (KeyError, TypeError, ValueError):
            continue
        kept.append(e)
    kept.append({"lat": round(lat, 4), "lon": round(lon, 4), "keys": sorted(keys), "at": now})
    kept.sort(key=lambda e: e.get("at", 0))
    return kept[-max_n:]


def nws_record(props: dict[str, Any], geom: Any, priority: int) -> dict[str, Any]:
    """What a place's entity needs of one NWS alert. `geom` is kept only when it is the alert's own polygon,
    at full precision (the map's copy is rounded to 3 decimals)."""
    polygon = geom if isinstance(geom, dict) and geom.get("type") in ("Polygon", "MultiPolygon") else None
    return {
        "source": "NWS",
        "id": props.get("@id") or props.get("id"),
        "event": props.get("event") or "Unknown",
        "severity": props.get("severity") or "Unknown",
        "headline": props.get("headline"),
        "onset": props.get("onset") or props.get("effective"),
        "ends": props.get("ends") or props.get("expires"),
        "priority": priority,
        "zones": [] if polygon else sorted({k for k in map(zone_key, props.get("affectedZones") or []) if k}),
        "polygon": polygon,
    }


def met_record(cap: dict[str, Any], cap_url: str) -> dict[str, Any] | None:
    """What a place's entity needs of one MET Norway warning (a parsed CAP that the map draws)."""
    rings = cap.get("rings") or []
    if not rings:
        return None
    geom = ({"type": "Polygon", "coordinates": [rings[0]]} if len(rings) == 1
            else {"type": "MultiPolygon", "coordinates": [[r] for r in rings]})
    colour = cap.get("colour")
    event = cap.get("event") or "Warning"
    when = cap.get("onset")
    ends = cap.get("expires")
    return {
        "source": "MET Norway",
        "id": f"{cap_url}?cap={cap['id']}" if cap.get("id") else None,
        "event": f"{event}, {colour.lower()}" if isinstance(colour, str) else event,
        "severity": cap.get("severity") or "Unknown",
        "headline": cap.get("headline"),
        "onset": when.isoformat() if hasattr(when, "isoformat") else when,
        "ends": ends.isoformat() if hasattr(ends, "isoformat") else ends,
        # MET has no NWS priority; ranked after NWS events of the same severity
        "priority": 1000 - (cap.get("level") or 0),
        "zones": [],
        "polygon": geom,
    }


def alerts_at(records: list[dict[str, Any]], keys: set[str] | None, lat: float, lon: float) -> list[dict[str, Any]]:
    """Every alert holding the point. `keys` are the NWS zones holding it (None: not known, so zone-based
    alerts cannot be tested; polygons still are)."""
    found = []
    for r in records:
        if r.get("polygon") is not None:
            if contains(r["polygon"], lat, lon):
                found.append(r)
        elif keys and keys.intersection(r.get("zones") or ()):
            found.append(r)
    return found


def counts(record: dict[str, Any], threshold: str) -> bool:
    return SEVERITY_RANK.get(record.get("severity"), 0) >= THRESHOLDS.get(threshold, 0)


def summary(found: list[dict[str, Any]], threshold: str) -> dict[str, Any]:
    """The entity's state and the alerts it lists: worst first (severity, then NWS's own priority)."""
    ordered = sorted(found, key=lambda r: (-SEVERITY_RANK.get(r.get("severity"), 0), r.get("priority", 999),
                                           r.get("event") or ""))
    seen = set()
    alerts = []
    for r in ordered:
        if r.get("id") in seen:
            continue
        seen.add(r.get("id"))
        alerts.append({k: r.get(k) for k in ("event", "severity", "headline", "onset", "ends", "source", "id")})
    on = [a for a in alerts if counts(a, threshold)]
    return {"on": bool(on), "alerts": alerts, "highest": on[0]["event"] if on else None, "counted": len(on)}
