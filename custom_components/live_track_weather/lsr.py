"""Storm reports on the map (Weather SSOT item 312, contract D21): NWS Local Storm Reports of the last 24 hours as a D19
point layer.

Pure Python, no Home Assistant import. Source chosen by Lee 2026-11-18 02:01 after both were measured (Weather SSOT row
312): NWS's Local Storm Report map service, layer 0 "Last_24_Hours", a rolling 24-hour window updated every 30 minutes
by its own description, over SPC's day files. MEASURED 2026-11-18 (bin\\ltw312_lsr_probe*.py): fields `wfo_id`,
`wfo`, `lsr_validtime` (epoch milliseconds), `valid_time` (the same as text), `descript` (the report type, title
case: "Tstm Wnd Gst"), `loc_desc`, `state`, `magnitude` (text), `units` ("MPH", "mph", "Inch", "TInch" for a trace,
a blank), `remarks` (often a single space); `f=geojson` answers directly; `UPPER(descript) IN (...)` works in the
WHERE; ETag and 304; 2,000 records at most per request.

Which reports (Lee 02:01, "Ok" to the recommendation): tornado and waterspout, funnel cloud, hail (and marine hail),
thunderstorm wind gust and damage (and marine thunderstorm wind), flash flood, flood. Funnel cloud, waterspout and the
marine types were not in the 72 hours measured: their names are NWS's LSR event types (INFERRED spelling, matched
whatever the case). Snow, rain, non-thunderstorm wind, fog and the rest are not drawn.

Drawn (chosen here, Lee may change): SPC's colours for the storm types (tornado red, wind blue, hail green), teal for
flooding; a significant report (any tornado or waterspout, hail 2 inches or more, wind 65 kt, 74.8 mph, or more) larger
with a dark ring; older reports paler, in three steps: under 1 hour, 1 to 6 hours, 6 to 24 hours. The file changes as
reports age, so its URL does too (D19: versioned by content).
"""

from __future__ import annotations

import math
from datetime import datetime, timezone
from typing import Any

URL = "https://mapservices.weather.noaa.gov/vector/rest/services/obs/nws_local_storm_reports/MapServer/0/query"
ATTRIBUTION = "Storm reports: NWS Local Storm Reports, mapservices.weather.noaa.gov"
WINDOW_S = 24 * 3600
AGES = ((3600, "new", 0.0), (6 * 3600, "recent", 0.4), (WINDOW_S, "older", 0.65))   # (up to, name, white mixed in)

# report type (upper case, as NWS writes it) -> kind
KINDS = {"TORNADO": "tornado", "WATERSPOUT": "tornado", "FUNNEL CLOUD": "funnel", "HAIL": "hail",
         "MARINE HAIL": "hail", "TSTM WND GST": "wind", "TSTM WND DMG": "wind", "MARINE TSTM WIND": "wind",
         "FLASH FLOOD": "flash_flood", "FLOOD": "flood"}
PARAMS = {"where": "UPPER(descript) IN (%s)" % ",".join(f"'{k}'" for k in KINDS), "outFields": "*",
          "f": "geojson", "returnGeometry": "true"}
BASE = {   # kind -> (colour, label, radius, significant radius)
    "tornado": ("#D50000", "Tornado report", 5, 7),
    "funnel": ("#FF8A80", "Funnel cloud report", 4, 4),
    "hail": ("#2E7D32", "Hail report", 4, 6),
    "wind": ("#1565C0", "Thunderstorm wind report", 4, 6),
    "flash_flood": ("#00838F", "Flash flood report", 4, 4),
    "flood": ("#4DD0E1", "Flood report", 4, 4),
}
SIG_OUTLINE = "#212121"
HAIL_SIG_IN = 2.0
WIND_SIG_KT = 65.0         # SPC's significant wind; 74.8 mph
KT_MPH = 1.15078
COLUMNS = [{"key": "type", "label": "Type"}, {"key": "magnitude", "label": "Magnitude"},
           {"key": "place", "label": "Place"}, {"key": "time", "label": "Time (UTC)"},
           {"key": "office", "label": "NWS office"}, {"key": "remarks", "label": "Remarks"}]


def _mix(hex_colour: str, white: float) -> str:
    r, g, b = (int(hex_colour[i:i + 2], 16) for i in (1, 3, 5))
    return "#%02X%02X%02X" % tuple(round(c + (255 - c) * white) for c in (r, g, b))


def _styles() -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for kind, (colour, label, radius, sig_radius) in BASE.items():
        for _limit, age, white in AGES:
            out[f"{kind}_{age}"] = {"color": _mix(colour, white), "label": label, "radius": radius}
            if sig_radius != radius:
                out[f"{kind}_sig_{age}"] = {"color": _mix(colour, white), "label": f"{label}, significant",
                                            "radius": sig_radius, "outline": SIG_OUTLINE}
    return out


STYLES = _styles()


def _num(v: Any) -> float | None:
    if isinstance(v, bool):
        return None
    try:
        x = float(str(v).strip())
    except (TypeError, ValueError):
        return None
    return x if math.isfinite(x) else None


def magnitude(kind: str, mag: Any, units: Any) -> tuple[str | None, bool]:
    """(the magnitude as shown, significant). Hail in inches (and mm), wind in mph (and km/h); knots converted."""
    m = _num(mag)
    u = str(units or "").strip().upper()
    if kind == "tornado":
        return None, True
    if m is None or m <= 0:
        return None, False
    if kind == "hail" and u in ("INCH", "IN", ""):
        return f"{m:.2f} in ({m * 25.4:.0f} mm)", m >= HAIL_SIG_IN
    if kind == "wind" and u in ("MPH", "KTS", "KT", "KNOTS"):
        mph = m * KT_MPH if u.startswith("K") else m
        return f"{mph:.0f} mph ({mph * 1.609344:.0f} km/h)", mph / KT_MPH >= WIND_SIG_KT - 1e-9
    return f"{m:g} {str(units or '').strip()}".strip(), False


def age_name(age_s: float) -> str | None:
    """The age band of a report this many seconds old; None when it is outside the window (or in the future by more
    than 10 minutes)."""
    if age_s < -600:
        return None
    for limit, name, _white in AGES:
        if age_s < limit:
            return name
    return None


def points(doc: Any, now: datetime) -> list[list[Any]] | None:
    """The service's GeoJSON -> D19 points [lon, lat, style, type, magnitude, place, time, office, remarks]; None when
    it is not GeoJSON."""
    if not isinstance(doc, dict) or not isinstance(doc.get("features"), list):
        return None
    out = []
    for f in doc["features"]:
        if not isinstance(f, dict):
            continue
        p = f.get("properties")
        g = f.get("geometry")
        if not isinstance(p, dict) or not isinstance(g, dict):
            continue
        kind = KINDS.get(str(p.get("descript") or "").strip().upper())
        try:
            lon, lat = (float(c) for c in g["coordinates"][:2])
            ms = float(p["lsr_validtime"])
        except (KeyError, TypeError, ValueError):
            continue
        if kind is None or not (math.isfinite(lon) and math.isfinite(lat) and -90 <= lat <= 90 and -180 <= lon <= 180):
            continue
        when = datetime.fromtimestamp(ms / 1000, timezone.utc)
        age = age_name((now - when).total_seconds())
        if age is None:
            continue
        shown, sig = magnitude(kind, p.get("magnitude"), p.get("units"))
        style = f"{kind}_sig_{age}" if sig and f"{kind}_sig_{age}" in STYLES else f"{kind}_{age}"
        place = ", ".join(x for x in (str(p.get("loc_desc") or "").strip(), str(p.get("state") or "").strip()) if x)
        remarks = str(p.get("remarks") or "").strip()
        office = str(p.get("wfo") or "").strip() or str(p.get("wfo_id") or "").strip()
        out.append([round(lon, 4), round(lat, 4), style, str(p.get("descript")).strip(), shown, place or None,
                    when.strftime("%Y-%m-%d %H:%M"), office or None, remarks[:500] or None])
    return out
