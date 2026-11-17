"""Forecast at a watched place (Weather SSOT item 349): NWS and MET Norway answers in Home Assistant's forecast shape.

Pure Python, no Home Assistant import. Lee 2026-11-17 01:55: NWS's gridpoint forecast (daily and hourly) on US land
and territories, MET Norway's Locationforecast everywhere else and on all water. MEASURED 2026-11-17
(20_Research/REPORT_349_measure_20261117.md): NWS has no forecast on water at all (point and zone forecasts 404),
MET answers everywhere.

Every value is in the entity's native units: degrees Celsius, km/h, mm, hPa. NWS is asked with ?units=si (degC,
km/h); MET gives m/s, converted here.

Three forecast types from both sources, so an entity that moves from NWS to MET keeps its features:
  hourly       NWS's hourly periods; MET's steps that carry next_1_hours (about 2.5 days)
  twice_daily  NWS's day and night periods as they are; MET's steps grouped into day (06-18) and night (18-06)
  daily        NWS's day period with the night after it (high and low); MET's steps grouped by date
MET's day and night are taken in SOLAR time, longitude/15 hours from UTC: MET gives no time zone, and a place's
day is closer to the sun's than to the Home Assistant server's time zone (INFERRED, the simple rule chosen).
"""

from __future__ import annotations

import re
from datetime import datetime, timedelta, timezone
from typing import Any

NWS = "NWS"
MET = "MET Norway"

# NWS icon codes (api.weather.gov/icons) -> Home Assistant conditions. Day or night comes from the icon's path.
_NWS_CONDITIONS = {
    "skc": "sunny", "few": "partlycloudy", "sct": "partlycloudy", "bkn": "cloudy", "ovc": "cloudy",
    "wind_skc": "windy", "wind_few": "windy-variant", "wind_sct": "windy-variant", "wind_bkn": "windy-variant",
    "wind_ovc": "windy-variant",
    "snow": "snowy", "blizzard": "snowy",
    "rain_snow": "snowy-rainy", "rain_sleet": "snowy-rainy", "snow_sleet": "snowy-rainy", "fzra": "snowy-rainy",
    "rain_fzra": "snowy-rainy", "snow_fzra": "snowy-rainy", "sleet": "snowy-rainy",
    "rain": "rainy", "rain_showers": "rainy", "rain_showers_hi": "rainy",
    "tsra": "lightning-rainy", "tsra_sct": "lightning-rainy", "tsra_hi": "lightning-rainy",
    "tornado": "exceptional", "hurricane": "exceptional", "tropical_storm": "exceptional", "dust": "exceptional",
    "smoke": "exceptional", "hot": "exceptional", "cold": "exceptional",
    "haze": "fog", "fog": "fog",
}
_ICON = re.compile(r"/icons/[a-z]+/(day|night)/([a-z_]+)")
_COMPASS = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE", "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"]
_NUM = re.compile(r"\d+(?:\.\d+)?")


def nws_condition(icon: str | None) -> str | None:
    """'https://api.weather.gov/icons/land/night/tsra,40/rain,20?size=medium' -> 'lightning-rainy' (the first code)."""
    m = _ICON.search(icon or "")
    if not m:
        return None
    cond = _NWS_CONDITIONS.get(m.group(2))
    if cond == "sunny" and m.group(1) == "night":
        return "clear-night"
    return cond


def met_condition(symbol: str | None) -> str | None:
    """MET symbol codes ('lightrainshowers_day', 'clearsky_night', 'heavysnowandthunder') -> HA conditions."""
    if not symbol:
        return None
    base, _, period = symbol.partition("_")
    if base in ("clearsky", "fair"):
        return "clear-night" if period == "night" else "sunny"
    if base == "partlycloudy":
        return "partlycloudy"
    if base == "cloudy":
        return "cloudy"
    if base == "fog":
        return "fog"
    if "thunder" in base:
        return "lightning-rainy"
    if "sleet" in base:
        return "snowy-rainy"
    if "snow" in base:
        return "snowy"
    if base.startswith("heavyrain"):
        return "pouring"
    if "rain" in base:
        return "rainy"
    return None


def wind_kmh(text: str | None) -> float | None:
    """NWS windSpeed with ?units=si: '6 km/h' -> 6.0; '8 to 16 km/h' -> 16.0, the upper end of the range."""
    nums = [float(n) for n in _NUM.findall(text or "")]
    return max(nums) if nums else None


def bearing(text: str | None) -> float | None:
    """'SSW' -> 202.5."""
    if text in _COMPASS:
        return _COMPASS.index(text) * 22.5
    return None


def _val(q: Any) -> Any:
    return q.get("value") if isinstance(q, dict) else None


def _parse(t: str) -> datetime:
    return datetime.fromisoformat(t.replace("Z", "+00:00"))


# ------------------------------------------------------------------ NWS

def nws_twice_daily(doc: Any) -> list[dict[str, Any]]:
    out = []
    for p in ((doc or {}).get("properties") or {}).get("periods") or []:
        out.append({
            "datetime": p.get("startTime"),
            "is_daytime": bool(p.get("isDaytime")),
            "condition": nws_condition(p.get("icon")),
            "native_temperature": p.get("temperature"),
            "precipitation_probability": _val(p.get("probabilityOfPrecipitation")),
            "native_wind_speed": wind_kmh(p.get("windSpeed")),
            "wind_bearing": bearing(p.get("windDirection")),
            "detailed_description": p.get("detailedForecast"),
        })
    return out


def nws_daily(doc: Any) -> list[dict[str, Any]]:
    """Each day period with the night after it: the day's temperature is the high, the night's the low. A night first
    in the list (it is evening) stands alone, its temperature as the low."""
    halves = nws_twice_daily(doc)
    out = []
    i = 0
    while i < len(halves):
        h = halves[i]
        if h["is_daytime"]:
            night = halves[i + 1] if i + 1 < len(halves) and not halves[i + 1]["is_daytime"] else None
            pops = [x for x in (h["precipitation_probability"], night and night["precipitation_probability"]) if x is not None]
            winds = [x for x in (h["native_wind_speed"], night and night["native_wind_speed"]) if x is not None]
            out.append({"datetime": h["datetime"], "condition": h["condition"],
                        "native_temperature": h["native_temperature"],
                        "native_templow": night["native_temperature"] if night else None,
                        "precipitation_probability": max(pops) if pops else None,
                        "native_wind_speed": max(winds) if winds else None,
                        "wind_bearing": h["wind_bearing"], "detailed_description": h["detailed_description"]})
            i += 2 if night else 1
        else:
            out.append({"datetime": h["datetime"], "condition": h["condition"], "native_temperature": None,
                        "native_templow": h["native_temperature"],
                        "precipitation_probability": h["precipitation_probability"],
                        "native_wind_speed": h["native_wind_speed"], "wind_bearing": h["wind_bearing"],
                        "detailed_description": h["detailed_description"]})
            i += 1
    return out


def nws_hourly(doc: Any) -> list[dict[str, Any]]:
    out = []
    for p in ((doc or {}).get("properties") or {}).get("periods") or []:
        out.append({
            "datetime": p.get("startTime"),
            "is_daytime": p.get("isDaytime"),
            "condition": nws_condition(p.get("icon")),
            "native_temperature": p.get("temperature"),
            "native_dew_point": _val(p.get("dewpoint")),
            "humidity": _val(p.get("relativeHumidity")),
            "precipitation_probability": _val(p.get("probabilityOfPrecipitation")),
            "native_wind_speed": wind_kmh(p.get("windSpeed")),
            "wind_bearing": bearing(p.get("windDirection")),
        })
    return out


def nws_updated(doc: Any) -> str | None:
    return ((doc or {}).get("properties") or {}).get("updateTime")


# ------------------------------------------------------------------ MET

def _met_steps(doc: Any) -> list[dict[str, Any]]:
    return (((doc or {}).get("properties") or {}).get("timeseries")) or []


def _ms_to_kmh(v: Any) -> float | None:
    return round(v * 3.6, 1) if isinstance(v, (int, float)) else None


def met_hourly(doc: Any) -> list[dict[str, Any]]:
    out = []
    for s in _met_steps(doc):
        d = s.get("data") or {}
        n1 = d.get("next_1_hours")
        if not n1:
            continue
        i = (d.get("instant") or {}).get("details") or {}
        out.append({
            "datetime": s.get("time"),
            "condition": met_condition((n1.get("summary") or {}).get("symbol_code")),
            "native_temperature": i.get("air_temperature"),
            "humidity": i.get("relative_humidity"),
            "native_pressure": i.get("air_pressure_at_sea_level"),
            "cloud_coverage": i.get("cloud_area_fraction"),
            "native_wind_speed": _ms_to_kmh(i.get("wind_speed")),
            "wind_bearing": i.get("wind_from_direction"),
            "native_precipitation": (n1.get("details") or {}).get("precipitation_amount"),
        })
    return out


def _solar_offset(lon: float) -> timedelta:
    return timedelta(hours=round(lon / 15))


def _grouped(doc: Any, lon: float, key) -> list[tuple[Any, list[dict[str, Any]]]]:
    """MET steps grouped by key(solar local time), in order. Each step's precipitation is next_1_hours where it has one,
    else next_6_hours (the 6-hourly steps), so no hour is counted twice."""
    off = _solar_offset(lon)
    groups: dict[Any, list[dict[str, Any]]] = {}
    for s in _met_steps(doc):
        d = s.get("data") or {}
        local = _parse(s["time"]) + off
        nxt = d.get("next_1_hours") or d.get("next_6_hours") or d.get("next_12_hours") or {}
        i = (d.get("instant") or {}).get("details") or {}
        groups.setdefault(key(local), []).append({
            "time": s["time"], "local": local, "temp": i.get("air_temperature"),
            "wind": _ms_to_kmh(i.get("wind_speed")), "bearing": i.get("wind_from_direction"),
            "humidity": i.get("relative_humidity"), "pressure": i.get("air_pressure_at_sea_level"),
            "symbol": (nxt.get("summary") or {}).get("symbol_code"),
            "precip": (nxt.get("details") or {}).get("precipitation_amount")
            if (d.get("next_1_hours") or d.get("next_6_hours")) else None,
            "hourly": "next_1_hours" in d,
        })
    return list(groups.items())


def _summarise(steps: list[dict[str, Any]], noon_hour: int) -> dict[str, Any]:
    temps = [s["temp"] for s in steps if s["temp"] is not None]
    winds = [s["wind"] for s in steps if s["wind"] is not None]
    precip = [s["precip"] for s in steps if s["precip"] is not None]
    rep = min(steps, key=lambda s: abs(s["local"].hour + s["local"].minute / 60 - noon_hour))
    return {"temps": temps, "wind": max(winds) if winds else None,
            "precip": round(sum(precip), 1) if precip else None,
            "condition": met_condition(rep["symbol"]), "bearing": rep["bearing"]}


def met_daily(doc: Any, lon: float) -> list[dict[str, Any]]:
    out = []
    for _, steps in _grouped(doc, lon, lambda t: t.date()):
        s = _summarise(steps, 12)
        out.append({"datetime": steps[0]["time"], "condition": s["condition"],
                    "native_temperature": max(s["temps"]) if s["temps"] else None,
                    "native_templow": min(s["temps"]) if s["temps"] else None,
                    "native_precipitation": s["precip"], "native_wind_speed": s["wind"], "wind_bearing": s["bearing"]})
    return out


def _half(t: datetime) -> tuple:
    """Day 06:00-17:59 belongs to its date; night 18:00-05:59 to the evening it begins."""
    if 6 <= t.hour < 18:
        return (t.date(), True)
    return ((t - timedelta(hours=6)).date(), False)


def met_twice_daily(doc: Any, lon: float) -> list[dict[str, Any]]:
    out = []
    for (_, is_day), steps in _grouped(doc, lon, _half):
        s = _summarise(steps, 12 if is_day else 0)
        temps = s["temps"]
        out.append({"datetime": steps[0]["time"], "is_daytime": is_day, "condition": s["condition"],
                    "native_temperature": (max(temps) if is_day else min(temps)) if temps else None,
                    "native_precipitation": s["precip"], "native_wind_speed": s["wind"], "wind_bearing": s["bearing"]})
    return out


def met_updated(doc: Any) -> str | None:
    return (((doc or {}).get("properties") or {}).get("meta") or {}).get("updated_at")


# ------------------------------------------------------------------ now

def current(hourly: list[dict[str, Any]], now: datetime) -> dict[str, Any] | None:
    """The hour holding `now`: the last hourly entry that has started (the first if none has). This is the forecast
    for this hour, not an observation (observations are item 350)."""
    started = [h for h in hourly if h.get("datetime") and _parse(h["datetime"]) <= now]
    if started:
        return started[-1]
    return hourly[0] if hourly else None


def build(source: str, daily_doc: Any, hourly_doc: Any, lon: float, now: datetime | None = None) -> dict[str, Any]:
    """Everything a place's weather entity shows, from one source's answers. For MET daily_doc and hourly_doc are the
    same Locationforecast answer."""
    now = now or datetime.now(timezone.utc)
    if source == NWS:
        hourly = nws_hourly(hourly_doc)
        res = {"daily": nws_daily(daily_doc), "twice_daily": nws_twice_daily(daily_doc), "hourly": hourly,
               "updated": nws_updated(daily_doc) or nws_updated(hourly_doc)}
    else:
        hourly = met_hourly(hourly_doc)
        res = {"daily": met_daily(hourly_doc, lon), "twice_daily": met_twice_daily(hourly_doc, lon), "hourly": hourly,
               "updated": met_updated(hourly_doc)}
    res["source"] = source
    res["now"] = current(hourly, now)
    return res
