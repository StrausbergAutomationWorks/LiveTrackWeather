"""MET Norway's Frost: observed weather (Weather SSOT item 311; contract D22; Lee 2026-11-18 03:31 to ~04:2x).

Pure Python, no Home Assistant import. Off unless the user enters their own Frost client ID in the options (Frost's
terms: a client ID per user, tied to a valid email). Two uses:
  * the map: one marker per Svalbard or Jan Mayen station whose newest temperature AND wind are each at most 2 hours
    old (contract D22);
  * measured wind and temperature at a watched place outside the National Weather Service's area whose nearest Frost
    station is in Norway or Svalbard (countryCode NO or SJ), ahead of GeoNames, in item 350's shapes (observe.py).

MEASURED 2026-11-18 (Weather SSOT 2z; bin\\ltw311_measure.py, ltw311_measure2.py, raw bin\\frost311\\): HTTP Basic,
the client ID as the user; /sources?country=SJ lists 48 stations (31 KB); one referencetime=latest answer for all 48
(80 KB, Cache-Control max-age 6-60 s, no validator); /sources?geometry=nearest(POINT(lon lat))&nearestmaxcount=10
answers 6-7 KB nearest first with `distance` and `countryCode` (Frost lists Swedish, Finnish, Danish, Russian and
Estonian SYNOP stations too); a client ID Frost does not know answers 401; HTTP 412 is "no time series". Several
series of one element per station (hourly, 30-, 10- and 1-minute; a METAR-like 30-minute series with qualityCode 2
beside the 10-minute one at Svalbard Lufthavn), so the newest value is used. Quality codes (Frost's
availableQualityCodes): 5 (very uncertain) and 7 (erroneous) are not used; 6 ("controlled and corrected, or missing
and interpolated - automatic") IS used and named in the popup (Lee 2026-11-18): MET's own stations stamp their newest
hour 6, and the hours before it read 0 (measured 10:38Z at 8 stations), so rejecting it dropped them for part of every
hour. Reference times came 3-6 minutes ahead at Sorkappoya, and 75 years ahead offshore.
"""

from __future__ import annotations

import math
import re
from datetime import datetime, timezone
from typing import Any

from .places import distance_m

BASE = "https://frost.met.no"
SOURCES_URL = f"{BASE}/sources/v0.jsonld"
OBS_URL = f"{BASE}/observations/v0.jsonld"
CHECK_PARAMS = {"ids": "SN99840"}     # the options' check of a new client ID: one station, about 1 KB
PROVIDER = "MET Norway (Frost)"
ATTRIBUTION = "Observations: MET Norway (frost.met.no), CC BY 3.0 NO, modified"

MAP_COUNTRY = "SJ"                    # Svalbard and Jan Mayen
PLACE_COUNTRIES = frozenset({"NO", "SJ"})
NEAREST_MAX = 10
MAX_AGE_S = 2 * 3600                  # as item 350: older than this is not shown
AHEAD_S = 15 * 60                     # a reference time this far ahead counts as now; further ahead it is dropped
MERGE_M = 1000                        # of two map stations closer than this only one is drawn
BAD_QUALITY = frozenset({5, 7})
AUTO_ONLY = 6   # used, and named in the popup (Lee 2026-11-18, "Use it, mark it"): MET stamps its newest hour 6
RETRY_MIN_S = 60
RETRY_DEFAULT_S = 600

COLOR = "#00796B"
GROUP, GROUP_LABEL, GROUP_ORDER = "observations", "Observed weather (MET Norway)", 0

T, WS, WD, GUST = "air_temperature", "wind_speed", "wind_from_direction", "max(wind_speed_of_gust PT1H)"
RH, PRESSURE, SNOW = "relative_humidity", "air_pressure_at_sea_level", "surface_snow_thickness"
MAP_ELEMENTS = (T, WS, WD, GUST, RH, PRESSURE, SNOW)
PLACE_ELEMENTS = (T, WS, WD, GUST)
_LEVEL = {T: 2, RH: 2, WS: 10, WD: 10, GUST: 10}   # the standard sensor heights, preferred on a tie
_ID = re.compile(r"^SN\d+$")
_ROMAN = re.compile(r"^(?=[IVX])X{0,3}(IX|IV|V?I{0,3})$")   # I to XXXIX
_DUR = re.compile(r"^PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?$")


def sources_params() -> dict[str, str]:
    return {"types": "SensorSystem", "country": MAP_COUNTRY}


def nearest_params(lat: float, lon: float) -> dict[str, str]:
    """The place's nearest stations; the location rounded to 4 decimals (about 11 m)."""
    return {"types": "SensorSystem", "geometry": f"nearest(POINT({lon:.4f} {lat:.4f}))",
            "nearestmaxcount": str(NEAREST_MAX)}


def latest_params(ids: list[str], elements: tuple[str, ...]) -> dict[str, str]:
    return {"sources": ",".join(ids), "referencetime": "latest", "maxage": "PT2H", "elements": ",".join(elements)}


def title_name(raw: Any) -> str | None:
    """Frost's upper-case station name in title case, Roman numerals kept: `BJØRNØYA II` -> `Bjørnøya II`."""
    if not isinstance(raw, str) or not raw.strip():
        return None
    parts = re.split(r"([\s\-/()]+)", raw.strip())
    return "".join(p if not p or not p[0].isalnum() else (p.upper() if _ROMAN.match(p.upper()) else p.capitalize())
                   for p in parts)


def _num(v: Any) -> float | None:
    if isinstance(v, bool) or not isinstance(v, (int, float)):
        return None
    f = float(v)
    return f if math.isfinite(f) else None


def _time(s: Any) -> datetime | None:
    if not isinstance(s, str):
        return None
    try:
        t = datetime.fromisoformat(s.replace("Z", "+00:00"))
    except ValueError:
        return None
    return t if t.tzinfo is not None else None


def _dur_s(s: Any) -> int:
    m = _DUR.match(s) if isinstance(s, str) else None
    if not m or not any(m.groups()):
        return 10 ** 9
    h, mi, se = (int(g) if g else 0 for g in m.groups())
    return h * 3600 + mi * 60 + se


def parse_sources(doc: Any) -> list[dict[str, Any]]:
    """/sources -> [{"id", "name", "lat", "lon", "country", "holders"}] in the answer's order (nearest first for a
    nearest() search). A source without an SN id or a position is left out."""
    out = []
    for s in (doc.get("data") if isinstance(doc, dict) else None) or []:
        try:
            sid = s["id"]
            lon, lat = s["geometry"]["coordinates"][:2]
            lat, lon = float(lat), float(lon)
        except (KeyError, TypeError, ValueError, IndexError):
            continue
        if not isinstance(sid, str) or not _ID.match(sid) or not (math.isfinite(lat) and math.isfinite(lon)):
            continue
        holders = [h for h in (s.get("stationHolders") or []) if isinstance(h, str)]
        out.append({"id": sid, "name": title_name(s.get("name")) or sid, "lat": lat, "lon": lon,
                    "country": s.get("countryCode"), "holders": holders})
    return out


def parse_latest(doc: Any, now: datetime) -> dict[str, dict[str, dict[str, Any]]]:
    """A referencetime=latest answer -> {station id: {element: {"value", "time"}}}, the newest usable value of each
    element; on a tie the better quality code, then the standard height, then the finer resolution."""
    out: dict[str, dict[str, dict[str, Any]]] = {}
    for d in (doc.get("data") if isinstance(doc, dict) else None) or []:
        if not isinstance(d, dict) or not isinstance(d.get("sourceId"), str):
            continue
        sid = d["sourceId"].split(":")[0]
        ref = _time(d.get("referenceTime"))
        if ref is None or (ref - now).total_seconds() > AHEAD_S:
            continue
        for o in d.get("observations") or []:
            if not isinstance(o, dict) or not isinstance(o.get("elementId"), str):
                continue
            q = o.get("qualityCode")
            v = _num(o.get("value"))
            if v is None or q in BAD_QUALITY:
                continue
            e = o["elementId"]
            level = (o.get("level") or {}).get("value") if isinstance(o.get("level"), dict) else None
            rank = (ref, -(q if isinstance(q, int) else 9), level == _LEVEL.get(e), -_dur_s(o.get("timeResolution")))
            cur = out.setdefault(sid, {}).get(e)
            if cur is None or rank > cur["_rank"]:
                out[sid][e] = {"value": v, "time": ref, "q": q, "_rank": rank}
    return out


def _fresh(v: dict[str, Any] | None, now: datetime) -> bool:
    return v is not None and (now - v["time"]).total_seconds() <= MAX_AGE_S


def _compass(deg: float) -> str:
    names = ("N", "NE", "E", "SE", "S", "SW", "W", "NW")
    return names[int(((deg % 360) + 22.5) // 45) % 8]


def _when(t: datetime) -> str:
    return t.astimezone(timezone.utc).strftime("%H:%M UTC %d %b")


def _iso(t: datetime) -> str:
    return t.astimezone(timezone.utc).isoformat()


def _kmh(ms: float) -> float:
    return round(ms * 3.6, 1)


def station_markers(sources: list[dict[str, Any]], latest: dict[str, dict[str, dict[str, Any]]],
                    now: datetime) -> list[dict[str, Any]]:
    """The map's markers (contract D22): every station with a fresh temperature AND a fresh wind speed, one per
    MERGE_M (the newer temperature, then the lower id), as records for geo_location.py."""
    cands = []
    for s in sources:
        r = latest.get(s["id"]) or {}
        if _fresh(r.get(T), now) and _fresh(r.get(WS), now):
            cands.append((s, r))
    cands.sort(key=lambda c: (-c[1][T]["time"].timestamp(), c[0]["id"]))
    kept: list[tuple[dict[str, Any], dict[str, Any]]] = []
    for s, r in cands:
        if any(distance_m(s["lat"], s["lon"], k["lat"], k["lon"]) < MERGE_M for k, _ in kept):
            continue
        kept.append((s, r))
    return [_marker(s, r, now) for s, r in sorted(kept, key=lambda c: c[0]["id"])]


def _marker(s: dict[str, Any], r: dict[str, Any], now: datetime) -> dict[str, Any]:
    vals = {e: v for e, v in r.items() if _fresh(v, now)}
    t = vals[T]
    temp = t["value"]
    attrs: dict[str, Any] = {"identity": s["id"], "marker_label": f"{round(temp)}°", "marker_color": COLOR,
                             "map_layer": "fixed", "marker_group": GROUP, "marker_group_label": GROUP_LABEL,
                             "marker_group_order": GROUP_ORDER, "temperature_c": temp}
    for key, el, conv in (("wind_speed_kmh", WS, _kmh), ("wind_from_deg", WD, None), ("wind_gust_kmh", GUST, _kmh),
                          ("humidity_pct", RH, None), ("pressure_hpa", PRESSURE, None), ("snow_depth_cm", SNOW, None)):
        if el in vals:
            attrs[key] = conv(vals[el]["value"]) if conv else vals[el]["value"]
    attrs["observed"] = _iso(t["time"])
    if s["holders"]:
        attrs["station_holders"] = ", ".join(s["holders"])

    def at(el: str) -> str:
        """A value older than the temperature carries its own time."""
        return f" ({vals[el]['time'].astimezone(timezone.utc).strftime('%H:%M UTC')})" if vals[el]["time"] < t["time"] else ""

    lines = [f"Temperature {temp:.1f} °C"]
    wind = f"Wind {round(attrs['wind_speed_kmh'])} km/h"
    if "wind_from_deg" in attrs:
        wind += f" from {_compass(attrs['wind_from_deg'])} ({round(attrs['wind_from_deg'])}°)"
    wind += at(WS)
    if "wind_gust_kmh" in attrs:
        # Frost's gust is the highest of the hour ending at its reference time
        wind += f", gusts {round(attrs['wind_gust_kmh'])} km/h in the hour to {vals[GUST]['time'].strftime('%H:%M UTC')}"
    lines.append(wind)
    if "humidity_pct" in attrs:
        lines.append(f"Humidity {round(attrs['humidity_pct'])} %" + at(RH))
    if "pressure_hpa" in attrs:
        lines.append(f"Pressure {attrs['pressure_hpa']:.1f} hPa at sea level" + at(PRESSURE))
    if "snow_depth_cm" in attrs:
        lines.append(f"Snow depth {attrs['snow_depth_cm']:g} cm" + at(SNOW))
    auto = [word for word, els in (("temperature", (T,)), ("wind", (WS, WD, GUST)), ("humidity", (RH,)),
                                   ("pressure", (PRESSURE,)), ("snow depth", (SNOW,)))
            if any(vals.get(e, {}).get("q") == AUTO_ONLY for e in els)]
    if auto:
        attrs["automatic_check_only"] = auto
    lines.append(f"Measured {_when(t['time'])}")
    if auto:
        lines.append("Automatic check only: " + ", ".join(auto))
    lines.append("MET Norway (Frost)" + (f"; station: {attrs['station_holders']}" if s["holders"] else ""))
    attrs["marker_info"] = {"title": f"{s['name']}, measured", "text": "\n".join(lines)}
    attrs["attribution"] = ATTRIBUTION
    return {"key": s["id"].lower(), "name": s["name"], "lat": s["lat"], "lon": s["lon"], "attrs": attrs}


def in_area(nearest: list[dict[str, Any]]) -> bool:
    """A place is Frost's (Lee 2026-11-18: ahead of GeoNames in Norway and Svalbard) when its nearest Frost station is
    in Norway or Svalbard and Jan Mayen, by Frost's own countryCode."""
    return bool(nearest) and nearest[0].get("country") in PLACE_COUNTRIES


def place_reports(nearest: list[dict[str, Any]], latest: dict[str, dict[str, dict[str, Any]]], lat: float, lon: float,
                  now: datetime) -> list[tuple[dict[str, Any], dict[str, Any]]]:
    """The place's nearest stations as [(station, report)] in item 350's shapes (observe.pick), nearest first by the
    place's own distance. A report holds only values at most 2 hours old; its time is the oldest of them, so
    observe.fresh() holds for every value it carries. Wind speed, gust and direction come from one station."""
    out = []
    for s in nearest:
        r = latest.get(s["id"]) or {}
        rep: dict[str, Any] = {"temperature": None, "wind_speed": None, "wind_gust": None, "wind_direction": None}
        times = []
        if _fresh(r.get(T), now):
            rep["temperature"] = r[T]["value"]
            times.append(r[T]["time"])
        if _fresh(r.get(WS), now):
            rep["wind_speed"] = round(r[WS]["value"] * 3.6, 2)    # as observe.py's
            times.append(r[WS]["time"])
            if _fresh(r.get(GUST), now):
                rep["wind_gust"] = round(r[GUST]["value"] * 3.6, 2)
                times.append(r[GUST]["time"])
            if _fresh(r.get(WD), now):
                rep["wind_direction"] = r[WD]["value"]
                times.append(r[WD]["time"])
        if not times:
            continue
        rep["time"] = _iso(min(min(times), now))
        km = round(distance_m(lat, lon, s["lat"], s["lon"]) / 1000, 1)
        out.append(({"id": s["id"], "name": s["name"], "provider": PROVIDER, "km": km}, rep))
    out.sort(key=lambda sr: sr[0]["km"])
    return out


def retry_s(headers: Any) -> int:
    """Seconds to leave Frost alone after a 429 or 503: its Retry-After (documented), RETRY_MIN_S at least,
    RETRY_DEFAULT_S when absent or not a number of seconds."""
    try:
        v = int(str((headers or {}).get("Retry-After")).strip())
    except (TypeError, ValueError):
        return RETRY_DEFAULT_S
    return max(RETRY_MIN_S, v)


def check_error(http: int) -> str | None:
    """The options' check of a new client ID (CHECK_PARAMS): None when Frost takes it, else an error key."""
    if http == 200:
        return None
    if http == 401:
        return "frost_id_rejected"
    return "frost_cannot_connect"
