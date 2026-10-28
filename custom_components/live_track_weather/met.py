"""MET Norway's warnings, marine text forecasts and point forecasts for the map. No Home Assistant import.

Lee, 2026-10-28 17:04: "put MET's warnings as polygons on the map beside the US ones, and the sea-area forecasts
as clickable polygons ... a dot ... at Longyearbyen that when clicked gives the forecast ... This API should be
used for all areas they cover." Measured that evening (Weather SSOT item 310,
`20_Research/REPORT_metno_endpoints_20261028.md`):

* Warnings: MetAlerts 2.0 `current.rss?lang=en` (17 KB, `If-Modified-Since` answers 304) names every active warning;
  each warning's CAP file (5-9 KB, never changes once issued, so fetched once) carries its polygons, colour
  (`riskMatrixColor`), awareness level and English text. MET calls its GeoJSON "beta", "slow and costly", so it is
  not used. Norway's land, coast and sea areas, the sea areas to the pole.
* Marine forecasts: Textforecast 3.0 `sea_en` (56 sea areas, to 90 N) and `coast_en` (39 coastal areas, Spitsbergen
  included), GeoJSON polygons with the forecast text and wind, ice and polar-low warnings.
* Points: Locationforecast 2.0 `compact`, anywhere on earth.

Every polygon item carries `info` {title, text}: the card shows it when the shape is clicked (D12 as amended for
item 310).
"""

from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from typing import Any

CAP_NS = "{urn:oasis:names:tc:emergency:cap:1.2}"

# riskMatrixColor -> (colour, D12 priority: 1 on top). MET's warning levels are yellow, orange and red.
# ! Green is NOT drawn: every Green in the feed of 2026-10-28 22:07Z (4 of 18) was a cancellation, an Update
# whose headline reads "Cancelled ..." and whose text says "This warning is cancelled" (measured).
WARNING_COLOURS = {
    "Red": ("#E8202A", 1),
    "Orange": ("#FF8C00", 2),
    "Yellow": ("#FFD500", 3),
}
_LEVEL_COLOUR = {1: "Green", 2: "Yellow", 3: "Orange", 4: "Red"}

MARINE_STYLES = {
    "Sea area forecast": {"color": "#4F86B5", "priority": 2},
    "Coastal forecast": {"color": "#2E9C9C", "priority": 1},
}


def _iso_time(s: Any) -> datetime | None:
    if not isinstance(s, str) or not s.strip():
        return None
    try:
        t = datetime.fromisoformat(s.strip().replace("Z", "+00:00"))
    except ValueError:
        return None
    return t if t.tzinfo else t.replace(tzinfo=timezone.utc)


def _utc(t: datetime | None) -> str | None:
    return t.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ") if t else None


def _when(t: datetime | None) -> str:
    """`Thu 29 Oct 00:00` (UTC; the day without a leading zero)."""
    if t is None:
        return "?"
    u = t.astimezone(timezone.utc)
    return u.strftime(f"%a {u.day} %b %H:%M")


def _r3(c: Any) -> Any:
    """Round [lon, lat] pairs to 0.001 deg and drop a point that repeats the one before it."""
    if isinstance(c, list) and len(c) >= 2 and all(isinstance(x, (int, float)) and not isinstance(x, bool) for x in c[:2]):
        return [round(float(c[0]), 3), round(float(c[1]), 3)]
    if isinstance(c, list):
        out = [_r3(x) for x in c]
        if out and isinstance(out[0], list) and len(out[0]) == 2 and isinstance(out[0][0], float):
            out = [out[0]] + [p for i, p in enumerate(out[1:], 1) if p != out[i - 1]]
        return out
    return c


# ---------------------------------------------------------------- warnings

def parse_rss(text: str | bytes | None) -> list[str]:
    """The warnings MetAlerts lists as current: their CAP identifiers, in the feed's order."""
    if not text:
        return []
    try:
        root = ET.fromstring(text)
    except ET.ParseError:
        return []
    out = []
    for item in root.iter("item"):
        g = (item.findtext("guid") or "").strip()
        if g and g not in out:
            out.append(g)
    return out


def _ring(s: str) -> list[list[float]] | None:
    """CAP's `lat,lon lat,lon ...` as a closed GeoJSON ring of [lon, lat]."""
    pts = []
    for pair in s.split():
        try:
            lat, lon = (float(x) for x in pair.split(","))
        except ValueError:
            return None
        pts.append([lon, lat])
    if len(pts) < 3:
        return None
    if pts[0] != pts[-1]:
        pts.append(pts[0])
    return pts if len(pts) >= 4 else None


def parse_cap(xml: str | bytes | None) -> dict[str, Any] | None:
    """One CAP warning: its English `info` (else the first), polygons and the fields the map shows."""
    if not xml:
        return None
    try:
        root = ET.fromstring(xml)
    except ET.ParseError:
        return None
    infos = root.findall(f"{CAP_NS}info")
    if not infos:
        return None
    info = next((i for i in infos if (i.findtext(f"{CAP_NS}language") or "").lower().startswith("en")), infos[0])

    def tx(el, name):
        v = el.findtext(f"{CAP_NS}{name}")
        return v.strip() if isinstance(v, str) and v.strip() else None

    params = {}
    for p in info.findall(f"{CAP_NS}parameter"):
        k, v = tx(p, "valueName"), tx(p, "value")
        if k and v:
            params[k] = v
    rings = []
    for area in info.findall(f"{CAP_NS}area"):
        for poly in area.findall(f"{CAP_NS}polygon"):
            r = _ring(poly.text or "")
            if r:
                rings.append(r)
    level = None
    m = re.match(r"\s*(\d)", params.get("awareness_level", ""))
    if m:
        level = int(m.group(1))
    colour = params.get("riskMatrixColor")
    if colour not in WARNING_COLOURS and colour != "Green":
        colour = _LEVEL_COLOUR.get(level)
    return {
        "id": tx(root, "identifier"),
        "status": tx(root, "status"),
        "msg_type": tx(root, "msgType"),
        "event": params.get("eventAwarenessName") or tx(info, "event"),
        "headline": tx(info, "headline"),
        "description": tx(info, "description"),
        "instruction": tx(info, "instruction"),
        "consequences": params.get("consequences"),
        "colour": colour,
        "level": level,
        "onset": _iso_time(tx(info, "onset")),
        "expires": _iso_time(tx(info, "expires")) or _iso_time(params.get("eventEndingTime")),
        "area": ", ".join(filter(None, (tx(a, "areaDesc") for a in info.findall(f"{CAP_NS}area")))) or None,
        "domain": params.get("geographicDomain"),
        "rings": rings,
    }


def empty_warnings() -> dict[str, Any]:
    return {"count": 0, "polygons": [], "styles": {}, "highest": None}


def publish_warnings(caps: list[dict[str, Any]], now: datetime) -> dict[str, Any]:
    """The warnings to draw now: actual, not cancelled, not expired, with an area and a colour."""
    out = empty_warnings()
    best = 0
    for c in caps:
        if not c or c.get("status") != "Actual" or c.get("msg_type") == "Cancel" or not c.get("rings"):
            continue
        if c.get("expires") is not None and now >= c["expires"]:
            continue
        colour = c.get("colour")
        if colour not in WARNING_COLOURS:
            continue
        hexc, priority = WARNING_COLOURS[colour]
        event = f"{colour} warning"
        rings = [_r3(r) for r in c["rings"]]
        geom = ({"type": "Polygon", "coordinates": [rings[0]]} if len(rings) == 1
                else {"type": "MultiPolygon", "coordinates": [[r] for r in rings]})
        lines = [x for x in (c.get("description"), c.get("consequences"), c.get("instruction")) if x]
        lines.append(f"{_when(c.get('onset'))} to {_when(c.get('expires'))} UTC")
        lines.append(f"{colour} level. MET Norway")
        out["polygons"].append({"event": event, **geom, "warning": c.get("id"),
                                "info": {"title": c.get("headline") or c.get("event") or "Warning",
                                         "text": "\n".join(lines)}})
        out["styles"][event] = {"color": hexc, "priority": priority}
        out["count"] += 1
        rank = 5 - priority
        if rank > best:
            best, out["highest"] = rank, colour
    return out


# ---------------------------------------------------------------- marine text forecasts

def _areas(doc: Any) -> list[dict[str, Any]]:
    if not isinstance(doc, dict) or not isinstance(doc.get("features"), list):
        return []
    out = []
    for f in doc["features"]:
        if not isinstance(f, dict):
            continue
        g, p = f.get("geometry"), f.get("properties")
        if not isinstance(g, dict) or g.get("type") not in ("Polygon", "MultiPolygon") \
                or not isinstance(g.get("coordinates"), list) or not g["coordinates"] or not isinstance(p, dict):
            continue
        text = p.get("text")
        if not isinstance(text, str) or not text.strip():
            continue
        out.append({"geometry": g, "area": p.get("area"), "title": p.get("title"), "text": text.strip(),
                    "warnings": [f"{k.split('_')[0].replace('polarlow', 'Polar low').capitalize()} warning: {p[k].strip()}"
                                 for k in ("wind_warning", "ice_warning", "polarlow_warning")
                                 if isinstance(p.get(k), str) and p[k].strip()]})
    return out


def publish_marine(sea: Any, coast: Any) -> dict[str, Any]:
    """Every sea and coastal forecast area, each a clickable polygon with its forecast."""
    out = {"count": 0, "polygons": [], "styles": {}, "issued": None}
    synoptic = sea.get("synoptic") if isinstance(sea, dict) and isinstance(sea.get("synoptic"), str) else None
    for doc, event in ((sea, "Sea area forecast"), (coast, "Coastal forecast")):
        for a in _areas(doc):
            lines = [a["title"]] if isinstance(a["title"], str) else []
            lines.append(a["text"])
            lines += a["warnings"]
            if event == "Sea area forecast" and synoptic:
                lines.append("Synopsis: " + " ".join(synoptic.split()))
            lines.append("MET Norway")
            out["polygons"].append({"event": event, "type": a["geometry"]["type"],
                                    "coordinates": _r3(a["geometry"]["coordinates"]),
                                    "info": {"title": a["area"] if isinstance(a["area"], str) else event,
                                             "text": "\n".join(lines)}})
            out["styles"][event] = dict(MARINE_STYLES[event])
            out["count"] += 1
        if isinstance(doc, dict) and isinstance(doc.get("lastChange"), str):
            t = _iso_time(doc["lastChange"])
            if t and (out["issued"] is None or _utc(t) > out["issued"]):
                out["issued"] = _utc(t)
    return out


# ---------------------------------------------------------------- point forecasts

_WORDS = ("clearsky", "partlycloudy", "cloudy", "fair", "fog", "light", "heavy", "rain", "sleet", "snow",
          "showers", "and", "thunder")
_SAY = {"clearsky": "clear sky", "partlycloudy": "partly cloudy"}


def conditions(symbol: Any) -> str | None:
    """MET's `symbol_code` in words: `lightrainshowersandthunder_day` -> `Light rain showers and thunder`."""
    if not isinstance(symbol, str) or not symbol:
        return None
    s = symbol.split("_")[0]
    words = []
    while s:
        w = next((w for w in _WORDS if s.startswith(w)), None)
        if w is None:
            return None
        words.append(_SAY.get(w, w))
        s = s[len(w):]
    text = " ".join(words)
    return text[0].upper() + text[1:]


def point(doc: Any, name: str, lat: float, lon: float) -> dict[str, Any] | None:
    """One forecast point as a map marker's record: the first step now, then six-hour steps for a day."""
    try:
        ts = doc["properties"]["timeseries"]
        meta = doc["properties"]["meta"]
        first = ts[0]
        inst = first["data"]["instant"]["details"]
    except (KeyError, IndexError, TypeError):
        return None
    temp = inst.get("air_temperature")
    if not isinstance(temp, (int, float)):
        return None
    attrs: dict[str, Any] = {"identity": name, "marker_label": f"{round(temp)}°", "map_layer": "fixed",
                             "marker_color": "#1F6FB2", "forecast_for": _utc(_iso_time(first.get("time")))}
    for key, src, conv in (("temperature_c", "air_temperature", None),
                           ("wind_speed_kmh", "wind_speed", lambda v: round(v * 3.6, 1)),
                           ("wind_from_deg", "wind_from_direction", None),
                           ("cloud_cover_pct", "cloud_area_fraction", None),
                           ("humidity_pct", "relative_humidity", None),
                           ("pressure_hpa", "air_pressure_at_sea_level", None)):
        v = inst.get(src)
        if isinstance(v, (int, float)):
            attrs[key] = conv(v) if conv else v
    lines = []
    for hrs in (1, 6, 12):
        blk = first["data"].get(f"next_{hrs}_hours") or {}
        cond = conditions((blk.get("summary") or {}).get("symbol_code"))
        if cond:
            attrs[f"next_{hrs}h_conditions"] = cond
        mm = (blk.get("details") or {}).get("precipitation_amount")
        if isinstance(mm, (int, float)):
            attrs[f"next_{hrs}h_precipitation_mm"] = mm
    now_words = attrs.get("next_1h_conditions") or attrs.get("next_6h_conditions")
    wind = ""
    if "wind_speed_kmh" in attrs and "wind_from_deg" in attrs:
        wind = f", wind {round(attrs['wind_speed_kmh'])} km/h from {_compass(attrs['wind_from_deg'])}"
    lines.append(f"Now: {temp:.1f} °C" + (f", {now_words.lower()}" if now_words else "") + wind)
    t0 = _iso_time(first.get("time"))
    for step in ts[1:]:
        t = _iso_time(step.get("time"))
        if t is None or t0 is None or (t - t0).total_seconds() > 30 * 3600:
            break
        if t.hour % 6 or (t - t0).total_seconds() < 5 * 3600:
            continue
        d = step.get("data") or {}
        tt = ((d.get("instant") or {}).get("details") or {}).get("air_temperature")
        blk = d.get("next_6_hours") or {}
        cond = conditions((blk.get("summary") or {}).get("symbol_code"))
        mm = (blk.get("details") or {}).get("precipitation_amount")
        if not isinstance(tt, (int, float)):
            continue
        lines.append(f"{_when(t)} UTC: {tt:.0f} °C" + (f", {cond.lower()}" if cond else "")
                     + (f", {mm} mm in 6 h" if isinstance(mm, (int, float)) else ""))
    attrs["forecast"] = "\n".join(lines)
    upd = _iso_time(meta.get("updated_at"))
    if upd:
        attrs["forecast_updated"] = _utc(upd)
    return {"key": re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_"), "name": f"{name} forecast",
            "lat": lat, "lon": lon, "attrs": attrs}


def _compass(deg: float) -> str:
    names = ("N", "NE", "E", "SE", "S", "SW", "W", "NW")
    return names[int(((deg % 360) + 22.5) // 45) % 8]
