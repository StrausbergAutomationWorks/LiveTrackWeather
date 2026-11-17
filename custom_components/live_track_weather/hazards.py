"""Fire and smoke at a watched place (Weather SSOT item 351; Lee 2026-11-17 04:56), shown on item 334's "Alert at X".

Pure Python, no Home Assistant import. Lee's decisions: fire from NASA FIRMS's keyed API (each user's own MAP_KEY);
standing heat sources (mills, refineries, flares) left out by a list of spots that recur; "near" is far enough away
to leave time to pack up and move an RV; one detection is enough; smoke from a same-day source, AirNow (each user's
own key), counted just before it becomes a breathing problem; both shown on "Alert at X". MEASURED 2026-11-17
(20_Research/REPORT_309_333_measure_20261117.md; the keyed API and AirNow's replacement in Weather SSOT 2u):
  - FIRMS's area API takes a box west,south,east,north, a source and a day range 1..5 ("Invalid day range. Expects
    [1..5]."); day range 1 is today in UTC, so 2 is asked and anything older than FIRE_MAX_AGE_H dropped. Columns by
    name: latitude, longitude, acq_date, acq_time, satellite, instrument, confidence, version, frp, daynight (Landsat
    has no frp or version). Versions seen: 2.0NRT, 2.0URT, 6.1NRT.
  - near Indiana Dunes 89% of detections in 8 days came from 11 spots of about 2 km seen on 4+ days (the mills).
    THE LIST: NASA's own classification. FIRMS's standard product (SP, about 3.5 months behind the NRT data) carries
    `type`: 0 vegetation fire, 1 volcano, 2 other static land source, 3 offshore; the Indiana Dunes mills come back as
    types 2 and 3 at the same 7-36 km the NRT data keeps flagging, wildfires as 0. A place's list is the 0.02 degree
    cells holding SP detections of types 1-3 over the last STATIC_WINDOWS x 5 days of SP, and a detection in such a
    cell or one next to it is a standing source. NOT learned from the NRT data's recurrence: the API gives at most 5
    days, and a wildfire burning several days in the same 2 km would then be listed and hidden.
  - AirNow's observation/current/ziplatlong/ (the old latLong service answers 410 since 2026-10-01) gives the closest
    reading per pollutant within a fixed 50 miles: parameterName, nowcastAQI, aqiCategoryName, siteName,
    reportingAgency, dateObserved, hourObserved, localTimeZone; no site position. "No observations" comes back as a
    WebServiceError object.

FIRE_KM_DEFAULT (INFERRED, the user may change it in the options): observed wildfires ran 0.3-10.5 km/h (CSIRO), a
grassfire under critical conditions 1.6-17 km/h (Cruz, Alexander and Kilinc 2022); FIRMS's detections reach us 2-4
hours after the overpass (measured), and packing up takes about an hour: a fire running 10 km/h covers 50 km in those
five hours. The extreme grassfire would need more; one detection is enough, whatever its confidence (Lee).
SMOKE_AQI_DEFAULT (INFERRED): AQI 101 starts "Unhealthy for Sensitive Groups", where breathing trouble begins for
people with asthma or lung disease; 90 is just before it.
"""

from __future__ import annotations

import csv
import io
import math
from datetime import datetime, timedelta, timezone
from typing import Any

from .places import distance_m

FIRE_SOURCES = ("VIIRS_NOAA21_NRT", "VIIRS_NOAA20_NRT", "MODIS_NRT", "LANDSAT_NRT")
FIRE_DAY_RANGE = 2          # today and yesterday in UTC; older than FIRE_MAX_AGE_H is dropped
FIRE_MAX_AGE_H = 24
STATIC_SOURCES = ("VIIRS_NOAA20_SP", "VIIRS_NOAA21_SP")
STATIC_WINDOWS = 6          # 6 x 5 days (the API's maximum day range) of the standard product
STATIC_TYPES = frozenset({"1", "2", "3"})   # volcano, other static land source, offshore
CELL_DEG = 0.02             # about 2 km
FIRE_KM_DEFAULT = 50
SMOKE_AQI_DEFAULT = 90
SMOKE_PARAMETER = "PM2.5"
_COMPASS = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]


def box(lat: float, lon: float, km: float) -> str:
    """FIRMS's area: west,south,east,north holding a circle of `km` around the point, 3 decimals."""
    dlat = km / 111.0
    dlon = km / (111.0 * max(0.05, math.cos(math.radians(lat))))
    w, e = max(-180.0, lon - dlon), min(180.0, lon + dlon)
    s, n = max(-90.0, lat - dlat), min(90.0, lat + dlat)
    return f"{w:.3f},{s:.3f},{e:.3f},{n:.3f}"


def parse_firms(text: str | None, source: str) -> list[dict[str, Any]] | None:
    """An area answer's rows as [{"lat", "lon", "time" ISO UTC, "source", "satellite", "confidence", "frp",
    "version"}]; None when the answer is not FIRMS's CSV (an error text such as "Invalid MAP_KEY.")."""
    if not isinstance(text, str) or not text.startswith("latitude,longitude"):
        return None
    out = []
    for row in csv.DictReader(io.StringIO(text)):
        try:
            lat, lon = float(row["latitude"]), float(row["longitude"])
            t = datetime.strptime(f"{row['acq_date']} {int(row['acq_time']):04d}", "%Y-%m-%d %H%M")
        except (KeyError, TypeError, ValueError):
            continue
        frp = row.get("frp")
        try:
            frp = float(frp) if frp not in (None, "") else None
        except ValueError:
            frp = None
        out.append({"lat": lat, "lon": lon, "time": t.replace(tzinfo=timezone.utc).isoformat(), "source": source,
                    "satellite": row.get("satellite"), "confidence": row.get("confidence"), "frp": frp,
                    "version": row.get("version"), "type": row.get("type")})
    return out


def cell(lat: float, lon: float) -> tuple[int, int]:
    return (round(lat / CELL_DEG), round(lon / CELL_DEG))


def static_cells(sp_detections: list[dict[str, Any]]) -> set[tuple[int, int]]:
    """The cells holding standard-product detections NASA classed as static (volcano, industry, offshore)."""
    return {cell(d["lat"], d["lon"]) for d in sp_detections if (d.get("type") or "").strip() in STATIC_TYPES}


def sp_max_dates(text: str | None) -> dict[str, str]:
    """FIRMS's data_availability CSV (data_id,min_date,max_date) -> {data_id: max_date} for the standard products."""
    out = {}
    if isinstance(text, str) and text.startswith("data_id"):
        for row in csv.DictReader(io.StringIO(text)):
            if row.get("data_id") in STATIC_SOURCES and row.get("max_date"):
                try:
                    datetime.strptime(row["max_date"], "%Y-%m-%d")
                except ValueError:
                    continue
                out[row["data_id"]] = row["max_date"]
    return out


def static_windows(max_date: str) -> list[str]:
    """The first days of STATIC_WINDOWS 5-day windows ending at the standard product's last day, newest first."""
    end = datetime.strptime(max_date, "%Y-%m-%d")
    return [(end - timedelta(days=5 * w + 4)).strftime("%Y-%m-%d") for w in range(STATIC_WINDOWS)]


def standing(det: dict[str, Any], cells: set[tuple[int, int]]) -> bool:
    """A detection in a listed (static) cell or a cell next to it (a mill's detections wander by a pixel)."""
    y, x = cell(det["lat"], det["lon"])
    return any((y + dy, x + dx) in cells for dy in (-1, 0, 1) for dx in (-1, 0, 1))


def bearing(lat: float, lon: float, lat2: float, lon2: float) -> str:
    """Compass point from the place to the fire."""
    p1, p2 = math.radians(lat), math.radians(lat2)
    dl = math.radians(lon2 - lon)
    deg = math.degrees(math.atan2(math.sin(dl) * math.cos(p2),
                                  math.cos(p1) * math.sin(p2) - math.sin(p1) * math.cos(p2) * math.cos(dl)))
    return _COMPASS[round((deg % 360) / 45) % 8]


def fires_near(detections: list[dict[str, Any]], lat: float, lon: float, km: float, cells: set[tuple[int, int]],
               now: datetime, max_age_h: float = FIRE_MAX_AGE_H) -> list[dict[str, Any]]:
    """Detections within `km` of the place, younger than `max_age_h`, not standing sources; nearest first, each with
    its "km" and "bearing"."""
    out = []
    for d in detections:
        age_h = (now - datetime.fromisoformat(d["time"])).total_seconds() / 3600
        if age_h > max_age_h or standing(d, cells):
            continue
        dist = distance_m(lat, lon, d["lat"], d["lon"]) / 1000
        if dist <= km:
            out.append({**d, "km": round(dist, 1), "bearing": bearing(lat, lon, d["lat"], d["lon"])})
    out.sort(key=lambda d: d["km"])
    return out


def fire_record(fires: list[dict[str, Any]]) -> dict[str, Any] | None:
    """One record for "Alert at X" from the fires near it (nearest named); None when there are none. It counts
    whatever the CAP-severity setting is: its own test is the distance."""
    if not fires:
        return None
    f = fires[0]
    more = f", and {len(fires) - 1} more within the distance" if len(fires) > 1 else ""
    return {
        "source": "NASA FIRMS",
        "id": f"firms {f['time']} {f['lat']:.3f},{f['lon']:.3f}",
        "event": f"Fire detected {f['km']:.0f} km {f['bearing']}",
        "severity": "Severe",
        "headline": (f"A satellite fire detection {f['km']:.0f} km {f['bearing']} ({f['source']}, {f.get('version') or 'NRT'}, "
                     f"{f['time'][11:16]} UTC){more}."),
        "onset": f["time"],
        "ends": None,
        "priority": 0,
        "always": True,
        "km": f["km"],
    }


def parse_airnow(body: Any) -> dict[str, Any] | None:
    """AirNow's ziplatlong answer -> the PM2.5 reading {"aqi", "category", "site", "agency", "observed"} or None
    (no reading within 50 miles, an error envelope, or no PM2.5 row)."""
    if not isinstance(body, list):
        return None
    for row in body:
        if not isinstance(row, dict) or row.get("parameterName") != SMOKE_PARAMETER:
            continue
        aqi = row.get("nowcastAQI")
        if not isinstance(aqi, (int, float)) or isinstance(aqi, bool) or aqi < 0:
            return None
        return {"aqi": int(aqi), "category": row.get("aqiCategoryName"), "site": row.get("siteName"),
                "agency": row.get("reportingAgency"),
                "observed": f"{row.get('dateObserved')} {row.get('hourObserved')} {row.get('localTimeZone')}".strip()}
    return None


def airnow_error(body: Any) -> str | None:
    """The message of AirNow's error envelope ({"WebServiceError": [{"Message": ...}]}), if it is one."""
    if isinstance(body, dict):
        errs = body.get("WebServiceError")
        if isinstance(errs, list) and errs and isinstance(errs[0], dict):
            return str(errs[0].get("Message") or "")
    return None


def smoke_record(reading: dict[str, Any] | None, threshold: int) -> dict[str, Any] | None:
    """A record for "Alert at X" when the nearest PM2.5 NowCast AQI is at or above `threshold`; None otherwise. It
    counts whatever the CAP-severity setting is: its own test is the AQI."""
    if not reading or reading["aqi"] < threshold:
        return None
    return {
        "source": "AirNow",
        "id": f"airnow {reading['site']} {reading['observed']}",
        "event": f"Smoke: PM2.5 AQI {reading['aqi']}",
        "severity": "Moderate",
        "headline": (f"Fine particles (PM2.5) at AQI {reading['aqi']}, {reading['category']}, at {reading['site']} "
                     f"({reading['agency']}), the closest monitor within 50 miles, {reading['observed']}."),
        "onset": None,
        "ends": None,
        "priority": 0,
        "always": True,
        "aqi": reading["aqi"],
    }
