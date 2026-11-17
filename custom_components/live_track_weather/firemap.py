"""Fire detections and air-quality sites for the shared map, as point files (06_MAP_CONTRACT_OVERLAYS.md D19).

Decided by Lee 2026-11-17 (12:12-13:06 CST, Weather SSOT items 309 and 333): fire points drawn everywhere on screen,
standing heat sources gone entirely, AirNow sites drawn too, HMS smoke left off; the integration publishes a file and
the card fills it; the regions are the user's choice; a detection stays solid until it drops off; VIIRS only; the
world's standing-source list from one 5-day window.

Nothing here talks to Home Assistant; firemap_coordinator.py fetches and serves.

* Fires: FIRMS's keyless 24-hour files, NOAA-20 and NOAA-21 VIIRS, per region (the Global files make the others
  redundant). Every row in them is NRT and at most about 24 h old (measured 2026-11-17: newest 3-4 h behind).
* Standing heat sources: the 0.02-degree cells holding standard-product detections NASA classed as volcano, static
  land source or offshore (types 1-3), and the cells next to them (hazards.standing). Per region box, from the keyed
  area API. MEASURED 2026-11-17 (report 309/333 section 7): one 5-day window costs 10 transactions for the lower 48,
  Hawaii or Alaska, 20 for Canada, 180 for the world, and the world's answer is about 28 MB, so the region list is
  parsed for cells alone, row by row, never as dicts.
* AirNow: `data/`, PM2.5, one hour, by box; a site with no valid AQI is left out.
"""

from __future__ import annotations

import csv
import gzip
import hashlib
import io
import json
from datetime import datetime, timedelta, timezone
from typing import Any, Iterable

from .hazards import CELL_DEG, STATIC_TYPES, standing

FIRMS_FILES_URL = "https://firms.modaps.eosdis.nasa.gov/data/active_fire"
VIIRS_FILES = (("noaa-20-viirs-c2", "J1_VIIRS_C2", "NOAA-20"), ("noaa-21-viirs-c2", "J2_VIIRS_C2", "NOAA-21"))

# region -> FIRMS file region, the standard-product boxes ("w,s,e,n"), windows of the list, AirNow boxes
REGIONS: dict[str, dict[str, Any]] = {
    "us": {"firms": "USA_contiguous_and_Hawaii", "boxes": ("-125,24,-66,50", "-161,18,-154,23"), "windows": 6,
           "airnow": ("-125,24,-66,50", "-161,18,-154,23")},
    "alaska": {"firms": "Alaska", "boxes": ("-170,51,-129,72",), "windows": 6, "airnow": ("-170,51,-129,72",)},
    "canada": {"firms": "Canada", "boxes": ("-141,41,-52,84",), "windows": 6, "airnow": ("-141,41,-52,84",)},
    "world": {"firms": "Global", "boxes": ("-180,-90,180,90",), "windows": 1, "airnow": ()},
}
REGION_ORDER = ("us", "alaska", "canada", "world")

FIRE_STYLE = {"fire": {"color": "#FF3D00", "label": "Fire detected (NASA FIRMS, VIIRS)", "radius": 3,
                       "outline": "#7A1A00"}}
FIRE_COLUMNS = [{"key": "time", "label": "Detected (UTC)"}, {"key": "satellite", "label": "Satellite"},
                {"key": "frp", "label": "Fire radiative power (MW)"}, {"key": "confidence", "label": "Confidence"}]
FIRE_ATTRIBUTION = ("Fires: NASA FIRMS (VIIRS NRT), firms.modaps.eosdis.nasa.gov; standing heat sources removed by "
                    "NASA's standard-product classification")

# AirNow's category numbers (1-6) and EPA's colours
AQI_STYLES = {
    "good": {"color": "#00E400", "label": "PM2.5: Good"},
    "moderate": {"color": "#FFFF00", "label": "PM2.5: Moderate"},
    "usg": {"color": "#FF7E00", "label": "PM2.5: Unhealthy for Sensitive Groups"},
    "unhealthy": {"color": "#FF0000", "label": "PM2.5: Unhealthy"},
    "very_unhealthy": {"color": "#8F3F97", "label": "PM2.5: Very Unhealthy"},
    "hazardous": {"color": "#7E0023", "label": "PM2.5: Hazardous"},
}
for _s in AQI_STYLES.values():
    _s.update(radius=5, outline="#333333")
AQI_CATEGORY = {1: "good", 2: "moderate", 3: "usg", 4: "unhealthy", 5: "very_unhealthy", 6: "hazardous"}
AQI_COLUMNS = [{"key": "site", "label": "Site"}, {"key": "agency", "label": "Agency"},
               {"key": "aqi", "label": "PM2.5 AQI"}, {"key": "hour", "label": "Hour (UTC)"}]
AQI_ATTRIBUTION = "Air quality: AirNow (US EPA and partners), airnow.gov; preliminary data, not verified"


def regions_of(option: Any) -> list[str]:
    """The options' `fire_map_regions` -> the known regions, in a fixed order; anything else is dropped."""
    chosen = set(option) if isinstance(option, (list, tuple, set)) else set()
    return [r for r in REGION_ORDER if r in chosen]


def file_regions(regions: list[str]) -> list[str]:
    """The FIRMS file regions to fetch: the Global file alone when the world is chosen."""
    if "world" in regions:
        return ["Global"]
    return [REGIONS[r]["firms"] for r in regions]


def file_url(product: str, prefix: str, region: str) -> str:
    return f"{FIRMS_FILES_URL}/{product}/csv/{prefix}_{region}_24h.csv"


def airnow_boxes(regions: list[str]) -> list[str]:
    """AirNow's boxes for the chosen regions; the world adds none (AirNow covers the US and Canada)."""
    out: list[str] = []
    for r in regions:
        out.extend(REGIONS[r]["airnow"])    # no two regions share a box
    return out


def static_cells_csv(text: str | None) -> set[tuple[int, int]] | None:
    """A standard-product area answer -> the cells of its type 1-3 rows, read row by row. None when the answer is
    not FIRMS's CSV (an error text)."""
    if not isinstance(text, str) or not text.startswith("latitude,longitude"):
        return None
    rows = csv.reader(io.StringIO(text))
    head = next(rows)
    try:
        i_lat, i_lon, i_type = head.index("latitude"), head.index("longitude"), head.index("type")
    except ValueError:
        return None
    out = set()
    for row in rows:
        try:
            if row[i_type].strip() in STATIC_TYPES:
                out.add((round(float(row[i_lat]) / CELL_DEG), round(float(row[i_lon]) / CELL_DEG)))
        except (IndexError, ValueError):
            continue
    return out


def list_windows(max_date: str, windows: int) -> list[str]:
    """The first days of `windows` 5-day windows ending at the standard product's last day, newest first."""
    end = datetime.strptime(max_date, "%Y-%m-%d")
    return [(end - timedelta(days=5 * w + 4)).strftime("%Y-%m-%d") for w in range(windows)]


def parse_fire_file(text: str | None, satellite: str, now: datetime, max_age_h: float = 24) -> list[list[Any]] | None:
    """A keyless 24-hour VIIRS file -> D19 points [lon, lat, "fire", time, satellite, frp, confidence], younger than
    `max_age_h`. None when the text is not FIRMS's CSV."""
    if not isinstance(text, str) or not text.startswith("latitude,longitude"):
        return None
    rows = csv.reader(io.StringIO(text))
    head = next(rows)
    try:
        ix = {k: head.index(k) for k in ("latitude", "longitude", "acq_date", "acq_time")}
    except ValueError:
        return None
    i_frp = head.index("frp") if "frp" in head else None
    i_conf = head.index("confidence") if "confidence" in head else None
    out = []
    for row in rows:
        try:
            lat, lon = float(row[ix["latitude"]]), float(row[ix["longitude"]])
            t = datetime.strptime(f"{row[ix['acq_date']]} {int(row[ix['acq_time']]):04d}", "%Y-%m-%d %H%M")
        except (IndexError, ValueError):
            continue
        if not (-90 <= lat <= 90 and -180 <= lon <= 180):
            continue
        t = t.replace(tzinfo=timezone.utc)
        if (now - t).total_seconds() > max_age_h * 3600:
            continue
        frp = None
        if i_frp is not None and i_frp < len(row) and row[i_frp] not in ("",):
            try:
                frp = round(float(row[i_frp]), 1)
            except ValueError:
                frp = None
        conf = _confidence(row[i_conf] if i_conf is not None and i_conf < len(row) else None)
        out.append([round(lon, 4), round(lat, 4), "fire", t.strftime("%Y-%m-%d %H:%M"), satellite, frp, conf])
    return out


def _confidence(v: str | None) -> str | None:
    """VIIRS confidence as words: l, n, h."""
    return {"l": "low", "n": "nominal", "h": "high"}.get((v or "").strip().lower()) or ((v or "").strip() or None)


def drop_standing(points: Iterable[list[Any]], cells: set[tuple[int, int]]) -> list[list[Any]]:
    """Points not on a listed standing heat source or next to one."""
    return [p for p in points if not standing({"lat": p[1], "lon": p[0]}, cells)]


def parse_airnow_sites(body: Any) -> list[list[Any]] | None:
    """AirNow `data/` rows -> D19 points [lon, lat, style, site, agency, aqi, hour]. None when it is not a list."""
    if not isinstance(body, list):
        return None
    out = []
    for r in body:
        if not isinstance(r, dict):
            continue
        lat, lon, aqi = r.get("Latitude"), r.get("Longitude"), r.get("AQI")
        style = AQI_CATEGORY.get(r.get("Category"))
        if not all(isinstance(v, (int, float)) and not isinstance(v, bool) for v in (lat, lon, aqi)):
            continue
        if aqi < 0 or style is None or not (-90 <= lat <= 90 and -180 <= lon <= 180):
            continue
        hour = r.get("UTC")
        hour = hour.replace("T", " ") if isinstance(hour, str) else None
        out.append([round(lon, 4), round(lat, 4), style, r.get("SiteName") or None, r.get("AgencyName") or None,
                    int(aqi), hour])
    return out


def dedupe(points: Iterable[list[Any]]) -> list[list[Any]]:
    """Points with the same position and style are one (two overlapping boxes ask for one site twice)."""
    seen, out = set(), []
    for p in points:
        k = (p[0], p[1], p[2])
        if k in seen:
            continue
        seen.add(k)
        out.append(p)
    return out


def point_file(points: list[list[Any]], columns: list[dict[str, str]], meta: dict[str, Any]) -> tuple[str, bytes]:
    """The D19 file, gzipped, and its digest (12 hex of the SHA-256 of the JSON, so the same points give the same
    URL). Points sorted, so the digest does not depend on fetch order."""
    pts = sorted(points, key=lambda p: (p[2], p[0], p[1], str(p[3:])))
    body = json.dumps({"meta": meta, "columns": columns, "points": pts}, separators=(",", ":"),
                      ensure_ascii=False).encode("utf-8")
    digest = hashlib.sha256(body).hexdigest()[:12]
    return digest, gzip.compress(body, compresslevel=6, mtime=0)


def airnow_hour(now: datetime) -> str:
    """The last complete hour, as AirNow's startDate/endDate take it."""
    return (now.replace(minute=0, second=0, microsecond=0) - timedelta(hours=1)).strftime("%Y-%m-%dT%H")
