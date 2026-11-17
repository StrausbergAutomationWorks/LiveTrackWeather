"""Observed wind and temperature at a watched place (Weather SSOT item 350; Lee 2026-11-17 03:58).

Pure Python, no Home Assistant import. The nearest NWS observation station of any network (or, by option, airports
only), falling back through up to MAX_STATIONS listed stations when one is empty, stale or 404. MEASURED 2026-11-17
(20_Research/REPORT_350_measure_20261117.md):
  - /points names a stations list everywhere NWS works, water included; outside NWS's area /points answers 404 and
    there is nothing.
  - each station carries `provider`; the airport networks are ASOS, ASOS-HFM, OTHER-MTR (METAR sites), OTHER-HFM and
    NonFedAWOS. RAWS, MesoWest, APRSWXNET (amateur and citizen) and the rest are not airports.
  - a report is "empty" when every value is null; plain /observations/latest served such a report where the same
    report had its values under ?require_qc=true, so the caller asks require_qc=true.
  - a station that stops reporting: an old timestamp, a 404, empty reports, or one sensor null for hours.
  - airports report a gust only when there is one: a null gust is "none reported", kept as None, not filled in.

Wind speed, gust and direction come from one station's report (a gust from 40 km away beside a calm from 12 km away
would mean nothing); temperature is picked on its own, so a station whose thermometer is out still gives wind.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from .places import distance_m

AIRPORT_PROVIDERS = frozenset({"ASOS", "ASOS-HFM", "OTHER-MTR", "OTHER-HFM", "NonFedAWOS"})
MAX_STATIONS = 3          # the nearest and up to two more, asked only while something is missing
MAX_AGE_S = 2 * 3600      # older than this is unavailable (Lee 03:58)
FIELDS = ("temperature", "wind_speed", "wind_gust", "wind_direction")
_NWS_KEYS = {"temperature": "temperature", "wind_speed": "windSpeed", "wind_gust": "windGust",
             "wind_direction": "windDirection"}
# MADIS quality-control flags that reject a value outright: X rejected, B subjectively bad. Q ("questioned") is kept:
# it marks a value that failed a neighbour or temporal check, which a lone station in the desert can do honestly.
_REJECTED_QC = frozenset({"X", "B"})


def stations(doc: Any, lat: float, lon: float, airports_only: bool = False) -> list[dict[str, Any]]:
    """A gridpoint's stations list, nearest to the place first, as [{"id", "name", "provider", "km"}]. The distance
    is the place's own (the list's `distance` is from the grid point)."""
    out = []
    for f in (doc.get("features") if isinstance(doc, dict) else None) or []:
        try:
            p = f["properties"]
            sid = p["stationIdentifier"]
            slon, slat = f["geometry"]["coordinates"][:2]
            km = distance_m(lat, lon, float(slat), float(slon)) / 1000
        except (KeyError, TypeError, ValueError, IndexError):
            continue
        provider = p.get("provider") or None
        if airports_only and provider not in AIRPORT_PROVIDERS:
            continue
        out.append({"id": sid, "name": p.get("name"), "provider": provider, "km": round(km, 1)})
    out.sort(key=lambda s: s["km"])
    return out


def _value(q: Any, field: str) -> float | None:
    if not isinstance(q, dict) or q.get("qualityControl") in _REJECTED_QC:
        return None
    v = q.get("value")
    if not isinstance(v, (int, float)) or isinstance(v, bool):
        return None
    unit = (q.get("unitCode") or "").split(":")[-1]
    if field == "temperature":
        if unit == "degF":
            return round((v - 32) / 1.8, 2)
        return float(v) if unit in ("degC", "") else None
    if field == "wind_direction":
        return float(v) if unit in ("degree_(angle)", "") else None
    if unit == "m_s-1":
        return round(v * 3.6, 2)
    return float(v) if unit in ("km_h-1", "") else None


def parse(doc: Any) -> dict[str, Any] | None:
    """An /observations/latest answer -> {"time": ISO, "temperature" C, "wind_speed" km/h, "wind_gust" km/h,
    "wind_direction" degrees}, each None when not reported; None when it is not an observation."""
    p = doc.get("properties") if isinstance(doc, dict) else None
    if not isinstance(p, dict) or not isinstance(p.get("timestamp"), str):
        return None
    try:
        if datetime.fromisoformat(p["timestamp"]).tzinfo is None:
            return None
    except ValueError:
        return None
    out: dict[str, Any] = {"time": p["timestamp"]}
    for f in FIELDS:
        out[f] = _value(p.get(_NWS_KEYS[f]), f)
    return out


def age_s(obs: dict[str, Any], now: datetime) -> float:
    return (now - datetime.fromisoformat(obs["time"])).total_seconds()


def fresh(obs: dict[str, Any] | None, now: datetime, max_age_s: float = MAX_AGE_S) -> bool:
    return obs is not None and age_s(obs, now) <= max_age_s


def pick(reports: list[tuple[dict[str, Any], dict[str, Any] | None]], now: datetime) -> dict[str, Any]:
    """From [(station, parsed report or None)] in distance order: {"wind": {"station", "obs"} | None,
    "temperature": {"station", "obs"} | None}, each the nearest station with a fresh report carrying that value."""
    out: dict[str, Any] = {"wind": None, "temperature": None}
    for st, obs in reports:
        if not fresh(obs, now):
            continue
        if out["wind"] is None and obs["wind_speed"] is not None:
            out["wind"] = {"station": st, "obs": obs}
        if out["temperature"] is None and obs["temperature"] is not None:
            out["temperature"] = {"station": st, "obs": obs}
    return out


def complete(p: dict[str, Any]) -> bool:
    return p.get("wind") is not None and p.get("temperature") is not None
