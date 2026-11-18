"""GeoNames, with each user's own username (Weather SSOT item 352 step 4b; Lee 2026-11-17 23:31 and 2026-11-18).

Pure Python, no Home Assistant import. Off unless the user enters a GeoNames username in the options. Three uses:
  * weather outside NWS's stations: findNearByWeatherJSON, the nearest METAR station (within about 100 km by
    GeoNames' page) and its latest report, feeding item 350's "Wind at X", "Wind gust at X", "Wind direction at X"
    and "Temperature at X" only where NWS has no station;
  * the sea's name on "Depth at X": oceanJSON, asked once per elevation check, only on water;
  * the water test where only AWS Terrain Tiles gives an elevation (Lee 2026-11-18): a sea named there is water.

Read from GeoNames' pages (geonames.org/export, /export/credits.html, /export/webservice-exception.html), and
MEASURED 2026-11-18 ~06:43Z once Lee's account answered (bin\\ltw352b_gn_measure.py; tests/test_geonames.py
TestRealAnswers): the weather fields as below, status 15 at HTTP 200 for "no observation found" and "no ocean". 10,000 credits a day
and 1,000 an hour per username; findNearByWeatherJSON costs 2; an error is {"status": {"message", "value"}} with
value 10 authorization, 15 no result, 18 daily, 19 hourly, 20 weekly limit. The weather answer's fields, from
GeoNames' own forum (Marc Wick, 2024) and Safe Software's example (2008): "weatherObservation" with "observation"
(the raw METAR), "ICAO", "stationName", "datetime" ("YYYY-MM-DD HH:MM:SS", UTC by GeoNames' page), "temperature"
(a string, Celsius), "windSpeed" (a string, knots), "windDirection" (a number), "lat", "lng". No gust field is
documented, so the wind is read from the METAR's own wind group (direction, speed, gust and unit), the fields only
when the METAR has none. Measured: no gust field; some automatic stations send no wind at all (Toronto City).
"""

from __future__ import annotations

import math
import re
from datetime import datetime, timezone
from typing import Any

from .places import distance_m

BASE = "https://secure.geonames.org"
WEATHER_URL = f"{BASE}/findNearByWeatherJSON"
OCEAN_URL = f"{BASE}/oceanJSON"
CHECK_URL = f"{BASE}/gtopo30JSON"
PROVIDER = "GeoNames (METAR)"
ATTRIBUTION = "Observations: METAR via GeoNames (CC BY 4.0)"
SEA_ATTRIBUTION = "Sea name: GeoNames (CC BY 4.0)"

CREDITS_WEATHER = 2
DAILY_SHARE = 5000          # plan on half the 10,000 a day, so the user's other GeoNames uses have room
NO_RESULT = 15
LIMIT_BACKOFF_S = {18: 3 * 3600, 19: 3600, 20: 24 * 3600}
AUTH_BACKOFF_S = 6 * 3600
OTHER_BACKOFF_S = 15 * 60

_KT, _MPS = 1.852, 3.6
_WIND = re.compile(r"(?<!\S)(VRB|\d{3})(\d{2,3})(?:G(\d{2,3}))?(KT|MPS|KMH)(?!\S)")
_TEMP = re.compile(r"(?<!\S)(M?\d{2})/(?:M?\d{2})?(?!\S)")


def params(username: str, lat: float | None = None, lon: float | None = None) -> dict[str, str]:
    p = {"username": username}
    if lat is not None and lon is not None:
        p.update(lat=f"{lat:.4f}", lng=f"{lon:.4f}")
    return p


def status(doc: Any) -> tuple[int, str] | None:
    """GeoNames' error status (value, message), or None when the answer is not an error."""
    st = doc.get("status") if isinstance(doc, dict) else None
    if not isinstance(st, dict):
        return None
    try:
        return int(st.get("value")), str(st.get("message") or "")
    except (TypeError, ValueError):
        return -1, str(st.get("message") or "")


def answered(http: int, doc: Any) -> bool:
    """GeoNames answered the question: a result (HTTP 200), or "no result" (status 15, whatever the HTTP status: not
    measured). Not an error, a limit or nothing."""
    st = status(doc)
    if st is not None:
        return st[0] == NO_RESULT
    return http == 200 and isinstance(doc, dict)


def backoff_s(http: int, doc: Any) -> int:
    """Seconds to leave GeoNames alone after an answer; 0 when it answered (a result, or "no result")."""
    if answered(http, doc):
        return 0
    st = status(doc)
    if http == 401 or (st and st[0] == 10):
        return AUTH_BACKOFF_S
    if st and st[0] in LIMIT_BACKOFF_S:
        return LIMIT_BACKOFF_S[st[0]]
    return OTHER_BACKOFF_S


def check_error(http: int, doc: Any) -> str | None:
    """The options' check of a new username (one gtopo30JSON call, 0.1 credit): None when GeoNames takes it, else an
    error key for strings.json."""
    st = status(doc)
    if http == 200 and st is None and isinstance(doc, dict) and "gtopo30" in doc:
        return None
    msg = (st[1] if st else "").lower()
    if "confirm" in msg:
        return "geonames_not_confirmed"
    if "enable" in msg:
        return "geonames_not_enabled"
    if st and st[0] in LIMIT_BACKOFF_S:
        return "geonames_over_limit"
    if http == 401 or (st and st[0] == 10):
        return "geonames_user_rejected"
    return "geonames_cannot_connect"


def poll_s(n_places: int, base_s: int) -> int:
    """Seconds between one place's weather asks: base_s, or longer so every place together stays within DAILY_SHARE
    credits a day (also well inside the 1,000 an hour)."""
    return max(int(base_s), math.ceil(max(1, n_places) * CREDITS_WEATHER * 86400 / DAILY_SHARE))


def _num(v: Any) -> float | None:
    if isinstance(v, bool):
        return None
    try:
        f = float(v)
    except (TypeError, ValueError):
        return None
    return f if math.isfinite(f) else None


def metar_wind(metar: Any) -> dict[str, float | None] | None:
    """The METAR's wind group -> {"wind_speed", "wind_gust" km/h, "wind_direction" degrees or None (calm, VRB)};
    None when it has none."""
    if not isinstance(metar, str):
        return None
    m = _WIND.search(metar)
    if not m:
        return None
    k = {"KT": _KT, "MPS": _MPS, "KMH": 1.0}[m.group(4)]
    speed = int(m.group(2)) * k
    gust = int(m.group(3)) * k if m.group(3) else None
    direction = None if m.group(1) == "VRB" or speed == 0 else float(int(m.group(1)) % 360)
    return {"wind_speed": round(speed, 2), "wind_gust": round(gust, 2) if gust is not None else None,
            "wind_direction": direction}


def metar_temperature(metar: Any) -> float | None:
    if not isinstance(metar, str):
        return None
    m = _TEMP.search(metar)
    if not m:
        return None
    t = m.group(1)
    return -float(t[1:]) if t.startswith("M") else float(t)


def parse_weather(doc: Any, lat: float, lon: float) -> tuple[dict[str, Any], dict[str, Any]] | None:
    """findNearByWeatherJSON -> (station {"id", "name", "provider", "km"}, report {"time", "temperature" C,
    "wind_speed", "wind_gust" km/h, "wind_direction"}) in observe.py's shapes; None when there is no station."""
    w = doc.get("weatherObservation") if isinstance(doc, dict) else None
    if not isinstance(w, dict):
        return None
    try:
        when = datetime.strptime(str(w.get("datetime")), "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
    except ValueError:
        return None
    slat, slon = _num(w.get("lat")), _num(w.get("lng"))
    km = round(distance_m(lat, lon, slat, slon) / 1000, 1) if slat is not None and slon is not None else None
    sid = w.get("ICAO") or w.get("stationName")
    if not sid:
        return None
    station = {"id": str(sid), "name": w.get("stationName") or None, "provider": PROVIDER, "km": km}
    wind = metar_wind(w.get("observation"))
    if wind is None:
        kt = _num(w.get("windSpeed"))
        direction = _num(w.get("windDirection"))
        wind = {"wind_speed": round(kt * _KT, 2) if kt is not None else None, "wind_gust": None,
                "wind_direction": direction if kt else None}
    temp = _num(w.get("temperature"))
    if temp is None:
        temp = metar_temperature(w.get("observation"))
    report = {"time": when.isoformat(), "temperature": temp, **wind}
    return station, report


def parse_ocean(doc: Any) -> tuple[bool, str | None]:
    """oceanJSON -> (answered, sea name or None). (True, None) is "no ocean here" (status 15); (False, None) an error
    or an answer that is not one."""
    st = status(doc)
    if st is not None:
        return (st[0] == NO_RESULT), None
    o = doc.get("ocean") if isinstance(doc, dict) else None
    if isinstance(o, dict) and isinstance(o.get("name"), str) and o["name"].strip():
        return True, o["name"].strip()
    return False, None


def scrub(text: str, username: str | None) -> str:
    """A saved or logged answer without the username."""
    return text.replace(username, "<username>") if username else text
