"""Storm and winter reports on the map (Weather SSOT items 312 and 353, contract D21): NWS Local Storm Reports of the
last 24 hours as two D19 point layers.

Pure Python, no Home Assistant import. Source chosen by Lee 2026-11-18 02:01 after both were measured (Weather SSOT row
312): NWS's Local Storm Report map service, layer 0 "Last_24_Hours", a rolling 24-hour window updated every 30 minutes
by its own description, over SPC's day files. MEASURED 2026-11-18 (bin\\ltw312_lsr_probe*.py): fields `wfo_id`,
`wfo`, `lsr_validtime` (epoch milliseconds), `valid_time` (the same as text), `descript` (the report type, title
case: "Tstm Wnd Gst"), `loc_desc`, `state`, `magnitude` (text), `units` ("MPH", "mph", "Inch", "TInch" for a trace,
a blank), `remarks` (often a single space); `f=geojson` answers directly; `UPPER(descript) IN (...)` works in the
WHERE; ETag and 304; 2,000 records at most per request, so the answer is read in pages (bin\\ltw353_probe2.py:
`exceededTransferLimit` at the top level and in `properties`, pages ordered newest first join with no repeat).

STORM (item 312; Lee 02:01, "Ok" to the recommendation): tornado and waterspout, funnel cloud, hail (and marine hail),
thunderstorm wind gust and damage (and marine thunderstorm wind), flash flood, flood. Funnel cloud, waterspout and the
marine types were not in the 72 hours measured: their names are NWS's LSR event types (INFERRED spelling, matched
whatever the case).

WINTER (item 353; Lee 02:5x: its own checkbox; snow and ice, plus cold, avalanche and ice jam): the spellings MEASURED
in IEM's archive of the same NWS products (bin\\ltw353_probe.py, five storm days 2021-2025) and, for Snow, in NWS's
service; FREEZING DRIZZLE seen in neither (INFERRED); FREEZE put under cold here.

Drawn (chosen here, Lee may change): SPC's colours for the storm types (tornado red, wind blue, hail green), teal for
flooding; NWS's hazard colours for snow, blizzard, ice and cold; a significant report larger with a dark ring; older
reports paler, in three steps: under 1 hour, 1 to 6 hours, 6 to 24 hours. The file changes as reports age, so its URL
does too (D19: versioned by content).
"""

from __future__ import annotations

import math
from datetime import datetime, timezone
from typing import Any

URL = "https://mapservices.weather.noaa.gov/vector/rest/services/obs/nws_local_storm_reports/MapServer/0/query"
WINDOW_S = 24 * 3600
AGES = ((3600, "new", 0.0), (6 * 3600, "recent", 0.4), (WINDOW_S, "older", 0.65))   # (up to, name, white mixed in)
PAGE = 2000                # the layer's maxRecordCount (measured)
MAX_PAGES = 10
SIG_OUTLINE = "#212121"
HAIL_SIG_IN = 2.0
WIND_SIG_KT = 65.0         # SPC's significant wind; 74.8 mph
KT_MPH = 1.15078
SNOW_SIG_IN = 12.0
SLEET_SIG_IN = 0.5
ICE_SIG_IN = 0.25
COLUMNS = [{"key": "type", "label": "Type"}, {"key": "magnitude", "label": "Magnitude"},
           {"key": "place", "label": "Place"}, {"key": "time", "label": "Time (UTC)"},
           {"key": "office", "label": "NWS office"}, {"key": "remarks", "label": "Remarks"}]


def _mix(hex_colour: str, white: float) -> str:
    r, g, b = (int(hex_colour[i:i + 2], 16) for i in (1, 3, 5))
    return "#%02X%02X%02X" % tuple(round(c + (255 - c) * white) for c in (r, g, b))


def _styles(base: dict[str, tuple[str, str, int, int]]) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for kind, (colour, label, radius, sig_radius) in base.items():
        for _limit, age, white in AGES:
            out[f"{kind}_{age}"] = {"color": _mix(colour, white), "label": label, "radius": radius}
            if sig_radius != radius:
                out[f"{kind}_sig_{age}"] = {"color": _mix(colour, white), "label": f"{label}, significant",
                                            "radius": sig_radius, "outline": SIG_OUTLINE}
    return out


def _params(kinds: dict[str, str]) -> dict[str, Any]:
    return {"where": "UPPER(descript) IN (%s)" % ",".join(f"'{k}'" for k in kinds), "outFields": "*",
            "f": "geojson", "returnGeometry": "true", "orderByFields": "lsr_validtime DESC,objectid",
            "resultRecordCount": PAGE}


class ReportSet:
    """One publisher's reports: which types (upper case, as NWS writes them) map to which kind, how each kind is drawn,
    which types are significant whatever their size, the query, the file's meta source and the credit."""

    def __init__(self, key: str, kinds: dict[str, str], base: dict[str, tuple[str, str, int, int]],
                 always_sig: frozenset[str], source: str, attribution: str) -> None:
        self.key, self.kinds, self.base, self.always_sig = key, kinds, base, always_sig
        self.styles = _styles(base)
        self.params = _params(kinds)
        self.source, self.attribution = source, attribution


STORM = ReportSet(
    "storm_reports",
    {"TORNADO": "tornado", "WATERSPOUT": "tornado", "FUNNEL CLOUD": "funnel", "HAIL": "hail",
     "MARINE HAIL": "hail", "TSTM WND GST": "wind", "TSTM WND DMG": "wind", "MARINE TSTM WIND": "wind",
     "FLASH FLOOD": "flash_flood", "FLOOD": "flood"},
    {   # kind -> (colour, label, radius, significant radius)
        "tornado": ("#D50000", "Tornado report", 5, 7),
        "funnel": ("#FF8A80", "Funnel cloud report", 4, 4),
        "hail": ("#2E7D32", "Hail report", 4, 6),
        "wind": ("#1565C0", "Thunderstorm wind report", 4, 6),
        "flash_flood": ("#00838F", "Flash flood report", 4, 4),
        "flood": ("#4DD0E1", "Flood report", 4, 4),
    },
    frozenset(), "NWS LSR last 24 hours", "Storm reports: NWS Local Storm Reports, mapservices.weather.noaa.gov")

WINTER = ReportSet(
    "winter_reports",
    {"SNOW": "snow", "HEAVY SNOW": "snow", "SNOW SQUALL": "snow", "BLIZZARD": "blizzard",
     "SLEET": "sleet", "HEAVY SLEET": "sleet", "FREEZING RAIN": "ice", "FREEZING DRIZZLE": "ice", "ICE STORM": "ice",
     "SNOW/ICE DMG": "damage", "EXTREME COLD": "cold", "WIND CHILL": "cold", "EXTR WIND CHILL": "cold",
     "FREEZE": "cold", "AVALANCHE": "avalanche", "ICE JAM": "ice_jam", "ICE JAM FLOODING": "ice_jam"},
    {
        "snow": ("#7B68EE", "Snow report", 4, 6),
        "blizzard": ("#FF4500", "Blizzard report", 5, 5),
        "sleet": ("#BA55D3", "Sleet report", 4, 6),
        "ice": ("#8B008B", "Freezing rain or ice report", 4, 6),
        "damage": ("#616161", "Snow or ice damage report", 4, 4),
        "cold": ("#0000FF", "Cold report", 4, 4),
        "avalanche": ("#795548", "Avalanche report", 5, 5),
        "ice_jam": ("#006064", "Ice jam report", 4, 4),
    },
    frozenset({"ICE STORM"}), "NWS LSR last 24 hours, winter",
    "Winter reports: NWS Local Storm Reports, mapservices.weather.noaa.gov")

# item 312's names, kept: the storm set
KINDS, BASE, STYLES, PARAMS, ATTRIBUTION = STORM.kinds, STORM.base, STORM.styles, STORM.params, STORM.attribution


def _num(v: Any) -> float | None:
    if isinstance(v, bool):
        return None
    try:
        x = float(str(v).strip())
    except (TypeError, ValueError):
        return None
    return x if math.isfinite(x) else None


def magnitude(kind: str, mag: Any, units: Any) -> tuple[str | None, bool]:
    """(the magnitude as shown, significant). Hail in inches (and mm), wind in mph (and km/h), knots converted; snow
    in inches (and cm), sleet and ice in inches (and mm), a trace as "trace"; cold in deg F (and deg C)."""
    m = _num(mag)
    u = str(units or "").strip().upper()
    if kind == "tornado":
        return None, True
    if kind in ("snow", "sleet", "ice") and u == "TINCH":
        return "trace", False
    if kind == "cold" and u == "F" and m is not None:
        return f"{m:g} °F ({(m - 32) * 5 / 9:.0f} °C)", False
    if m is None or m <= 0:
        return None, False
    if kind == "hail" and u in ("INCH", "IN", ""):
        return f"{m:.2f} in ({m * 25.4:.0f} mm)", m >= HAIL_SIG_IN
    if kind == "wind" and u in ("MPH", "KTS", "KT", "KNOTS"):
        mph = m * KT_MPH if u.startswith("K") else m
        return f"{mph:.0f} mph ({mph * 1.609344:.0f} km/h)", mph / KT_MPH >= WIND_SIG_KT - 1e-9
    if kind == "snow" and u in ("INCH", "IN"):
        return f"{m:.1f} in ({m * 2.54:.0f} cm)", m >= SNOW_SIG_IN
    if kind in ("sleet", "ice") and u in ("INCH", "IN"):
        return f"{m:.2f} in ({m * 25.4:.0f} mm)", m >= (SLEET_SIG_IN if kind == "sleet" else ICE_SIG_IN)
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


def more(doc: Any) -> bool:
    """True when the service says this page was cut at its record limit (another page follows)."""
    if not isinstance(doc, dict):
        return False
    props = doc.get("properties")
    return doc.get("exceededTransferLimit") is True or (isinstance(props, dict)
                                                        and props.get("exceededTransferLimit") is True)


def merge(docs: list[Any]) -> dict[str, Any]:
    """Pages -> one FeatureCollection (their features in order)."""
    feats: list[Any] = []
    for d in docs:
        if isinstance(d, dict) and isinstance(d.get("features"), list):
            feats.extend(d["features"])
    return {"type": "FeatureCollection", "features": feats}


def points(doc: Any, now: datetime, rs: ReportSet = STORM) -> list[list[Any]] | None:
    """The service's GeoJSON -> D19 points [lon, lat, style, type, magnitude, place, time, office, remarks] for the
    report set's types; None when it is not GeoJSON."""
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
        descript = str(p.get("descript") or "").strip().upper()
        kind = rs.kinds.get(descript)
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
        sig = sig or descript in rs.always_sig
        style = f"{kind}_sig_{age}" if sig and f"{kind}_sig_{age}" in rs.styles else f"{kind}_{age}"
        place = ", ".join(x for x in (str(p.get("loc_desc") or "").strip(), str(p.get("state") or "").strip()) if x)
        remarks = str(p.get("remarks") or "").strip()
        office = str(p.get("wfo") or "").strip() or str(p.get("wfo_id") or "").strip()
        out.append([round(lon, 4), round(lat, 4), style, str(p.get("descript")).strip(), shown, place or None,
                    when.strftime("%Y-%m-%d %H:%M"), office or None, remarks[:500] or None])
    return out
