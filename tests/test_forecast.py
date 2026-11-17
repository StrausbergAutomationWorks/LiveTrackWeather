"""forecast: NWS and MET Norway answers in Home Assistant's forecast shape (Weather SSOT item 349).

Fixtures: Denver's NWS daily and hourly gridpoint forecasts of 2026-11-17 with ?units=si (the hourly cut to 48
periods), and MET Norway's Locationforecast compact at Longyearbyen of 2026-10-28 (the MET Norway item's fixture).
"""

import json
import unittest
from datetime import datetime, timezone

from _load import FIXTURES, load

fc = load("forecast")

NWS_D = json.loads((FIXTURES / "nws_forecast_denver_si_20261117.json").read_text(encoding="utf-8"))
NWS_H = json.loads((FIXTURES / "nws_hourly_denver_si_20261117.json").read_text(encoding="utf-8"))
MET = json.loads((FIXTURES / "met_locationforecast_longyearbyen_20261028T2113Z.json").read_text(encoding="utf-8"))
MET_LON = 15.6267
PER_D = NWS_D["properties"]["periods"]
PER_H = NWS_H["properties"]["periods"]
STEPS = MET["properties"]["timeseries"]


class TestConditions(unittest.TestCase):
    def test_nws_icons(self):
        u = "https://api.weather.gov/icons/land/{}/{}?size=medium"
        self.assertEqual(fc.nws_condition(u.format("day", "skc")), "sunny")
        self.assertEqual(fc.nws_condition(u.format("night", "skc")), "clear-night")
        self.assertEqual(fc.nws_condition(u.format("night", "few")), "partlycloudy")
        self.assertEqual(fc.nws_condition(u.format("day", "bkn")), "cloudy")
        self.assertEqual(fc.nws_condition(u.format("day", "tsra,40/rain,20")), "lightning-rainy")
        self.assertEqual(fc.nws_condition(u.format("day", "rain_showers,30")), "rainy")
        self.assertEqual(fc.nws_condition(u.format("day", "snow,60")), "snowy")
        self.assertEqual(fc.nws_condition(u.format("day", "rain_snow")), "snowy-rainy")
        self.assertEqual(fc.nws_condition(u.format("day", "wind_skc")), "windy")
        self.assertEqual(fc.nws_condition(u.format("day", "wind_bkn")), "windy-variant")
        self.assertEqual(fc.nws_condition(u.format("day", "tornado")), "exceptional")
        self.assertEqual(fc.nws_condition(u.format("day", "fog")), "fog")
        self.assertIsNone(fc.nws_condition(u.format("day", "nothing_known")))
        self.assertIsNone(fc.nws_condition(None))
        self.assertIsNone(fc.nws_condition("https://example.org/x.png"))

    def test_every_fixture_icon_maps(self):
        for p in PER_D + PER_H:
            self.assertIsNotNone(fc.nws_condition(p["icon"]), p["icon"])

    def test_met_symbols(self):
        self.assertEqual(fc.met_condition("clearsky_day"), "sunny")
        self.assertEqual(fc.met_condition("clearsky_night"), "clear-night")
        self.assertEqual(fc.met_condition("fair_polartwilight"), "sunny")
        self.assertEqual(fc.met_condition("partlycloudy_night"), "partlycloudy")
        self.assertEqual(fc.met_condition("cloudy"), "cloudy")
        self.assertEqual(fc.met_condition("fog"), "fog")
        self.assertEqual(fc.met_condition("lightrainshowersandthunder_day"), "lightning-rainy")
        self.assertEqual(fc.met_condition("heavysleet"), "snowy-rainy")
        self.assertEqual(fc.met_condition("lightsnowshowers_day"), "snowy")
        self.assertEqual(fc.met_condition("heavyrain"), "pouring")
        self.assertEqual(fc.met_condition("lightrain"), "rainy")
        self.assertIsNone(fc.met_condition(None))
        self.assertIsNone(fc.met_condition("somethingnew"))

    def test_every_fixture_symbol_maps(self):
        for s in STEPS:
            for k in ("next_1_hours", "next_6_hours"):
                sym = ((s["data"].get(k) or {}).get("summary") or {}).get("symbol_code")
                if sym:
                    self.assertIsNotNone(fc.met_condition(sym), sym)


class TestNwsValues(unittest.TestCase):
    def test_wind(self):
        self.assertEqual(fc.wind_kmh("6 km/h"), 6.0)
        self.assertEqual(fc.wind_kmh("8 to 16 km/h"), 16.0)
        self.assertIsNone(fc.wind_kmh(""))
        self.assertIsNone(fc.wind_kmh(None))

    def test_bearing(self):
        self.assertEqual(fc.bearing("N"), 0.0)
        self.assertEqual(fc.bearing("SSW"), 202.5)
        self.assertEqual(fc.bearing("NNW"), 337.5)
        self.assertIsNone(fc.bearing("X"))
        self.assertIsNone(fc.bearing(None))

    def test_fixture_is_si(self):
        self.assertEqual(NWS_D["properties"]["units"], "si")
        self.assertTrue(all(p["temperatureUnit"] == "C" for p in PER_D + PER_H))


class TestNws(unittest.TestCase):
    def test_twice_daily_is_the_periods(self):
        t = fc.nws_twice_daily(NWS_D)
        self.assertEqual(len(t), len(PER_D))
        for x, p in zip(t, PER_D):
            self.assertEqual(x["datetime"], p["startTime"])
            self.assertEqual(x["is_daytime"], p["isDaytime"])
            self.assertEqual(x["native_temperature"], p["temperature"])
            self.assertEqual(x["detailed_description"], p["detailedForecast"])
        self.assertEqual(t[0]["native_wind_speed"], 6.0)    # "6 km/h"
        self.assertEqual(t[0]["condition"], "cloudy")       # night/bkn

    def test_daily_pairs_day_with_its_night(self):
        d = fc.nws_daily(NWS_D)
        # the list opens at night ("Overnight"): it stands alone, as a low
        self.assertFalse(PER_D[0]["isDaytime"])
        self.assertIsNone(d[0]["native_temperature"])
        self.assertEqual(d[0]["native_templow"], PER_D[0]["temperature"])
        # then each day with the night after it
        self.assertEqual(d[1]["datetime"], PER_D[1]["startTime"])
        self.assertEqual(d[1]["native_temperature"], PER_D[1]["temperature"])
        self.assertEqual(d[1]["native_templow"], PER_D[2]["temperature"])
        days = sum(1 for p in PER_D if p["isDaytime"])
        self.assertEqual(len(d), 1 + days)
        for x in d[1:]:
            self.assertGreaterEqual(x["native_temperature"], x["native_templow"] if x["native_templow"] is not None else -99)

    def test_daily_rain_chance_is_the_higher_half(self):
        d = fc.nws_daily(NWS_D)
        pops = [p["probabilityOfPrecipitation"]["value"] for p in PER_D[1:3]]
        self.assertEqual(d[1]["precipitation_probability"], max(pops))

    def test_daily_rain_chance_higher_of_unequal_halves(self):
        def per(t, day, pop):
            return {"startTime": t, "isDaytime": day, "temperature": 5, "windSpeed": "8 km/h", "windDirection": "N",
                    "icon": None, "detailedForecast": "", "probabilityOfPrecipitation": {"value": pop}}
        doc = {"properties": {"periods": [per("2026-11-17T06:00:00-06:00", True, 20),
                                          per("2026-11-17T18:00:00-06:00", False, 60)]}}
        self.assertEqual(fc.nws_daily(doc)[0]["precipitation_probability"], 60)

    def test_daily_when_list_opens_with_day(self):
        doc = {"properties": {"periods": PER_D[1:]}}
        d = fc.nws_daily(doc)
        self.assertEqual(d[0]["native_temperature"], PER_D[1]["temperature"])
        self.assertEqual(d[0]["native_templow"], PER_D[2]["temperature"])

    def test_hourly(self):
        h = fc.nws_hourly(NWS_H)
        self.assertEqual(len(h), 48)
        self.assertEqual(h[0]["native_temperature"], PER_H[0]["temperature"])
        self.assertEqual(h[0]["humidity"], PER_H[0]["relativeHumidity"]["value"])
        self.assertEqual(h[0]["native_dew_point"], PER_H[0]["dewpoint"]["value"])
        self.assertEqual(h[0]["native_wind_speed"], 4.0)

    def test_empty(self):
        for bad in (None, {}, {"properties": {}}, {"properties": {"periods": None}}):
            self.assertEqual(fc.nws_daily(bad), [])
            self.assertEqual(fc.nws_hourly(bad), [])


class TestMet(unittest.TestCase):
    def test_hourly_is_the_steps_with_next_1_hours(self):
        h = fc.met_hourly(MET)
        n1 = [s for s in STEPS if "next_1_hours" in s["data"]]
        self.assertEqual(len(h), len(n1))
        i = n1[0]["data"]["instant"]["details"]
        self.assertEqual(h[0]["native_temperature"], i["air_temperature"])
        self.assertEqual(h[0]["native_wind_speed"], round(i["wind_speed"] * 3.6, 1))   # m/s -> km/h
        self.assertEqual(h[0]["native_pressure"], i["air_pressure_at_sea_level"])
        self.assertEqual(h[0]["native_precipitation"], n1[0]["data"]["next_1_hours"]["details"]["precipitation_amount"])

    def test_daily_by_solar_date(self):
        d = fc.met_daily(MET, MET_LON)
        # Longyearbyen is UTC+1 by the sun: steps fall on as many dates as their solar times cover
        dates = {(fc._parse(s["time"]) + fc._solar_offset(MET_LON)).date() for s in STEPS}
        self.assertEqual(len(d), len(dates))
        for x in d:
            self.assertIsNotNone(x["native_temperature"])
            self.assertLessEqual(x["native_templow"], x["native_temperature"])

    def test_daily_highs_are_the_steps_extremes(self):
        d = fc.met_daily(MET, MET_LON)
        off = fc._solar_offset(MET_LON)
        first_date = (fc._parse(STEPS[0]["time"]) + off).date()
        temps = [s["data"]["instant"]["details"]["air_temperature"] for s in STEPS
                 if (fc._parse(s["time"]) + off).date() == first_date]
        self.assertEqual(d[0]["native_temperature"], max(temps))
        self.assertEqual(d[0]["native_templow"], min(temps))

    def test_precipitation_not_counted_twice(self):
        # hourly steps count their hour; 6-hourly steps their six hours
        d = fc.met_daily(MET, MET_LON)
        total = 0.0
        for s in STEPS:
            data = s["data"]
            n = data.get("next_1_hours") or data.get("next_6_hours")
            if n:
                total += n["details"].get("precipitation_amount") or 0.0
        self.assertAlmostEqual(sum(x["native_precipitation"] or 0 for x in d), total, places=1)

    def test_twice_daily_alternates(self):
        t = fc.met_twice_daily(MET, MET_LON)
        self.assertGreater(len(t), 4)
        for a, b in zip(t, t[1:]):
            self.assertNotEqual(a["is_daytime"], b["is_daytime"])

    def test_half_boundaries(self):
        d = datetime(2026, 11, 17, tzinfo=timezone.utc)
        self.assertEqual(fc._half(d.replace(hour=6)), (d.date(), True))
        self.assertEqual(fc._half(d.replace(hour=17, minute=59)), (d.date(), True))
        self.assertEqual(fc._half(d.replace(hour=18)), (d.date(), False))
        self.assertEqual(fc._half(d.replace(hour=5, minute=59)), (datetime(2026, 11, 16).date(), False))

    def test_twice_daily_night_low_and_noon_condition(self):
        def step(t, temp, sym):
            return {"time": t, "data": {"instant": {"details": {"air_temperature": temp, "wind_speed": 1.0}},
                                        "next_1_hours": {"summary": {"symbol_code": sym},
                                                         "details": {"precipitation_amount": 0.0}}}}
        doc = {"properties": {"timeseries": [
            step("2026-11-17T06:00:00Z", 1.0, "cloudy"), step("2026-11-17T12:00:00Z", 5.0, "clearsky_day"),
            step("2026-11-17T18:00:00Z", 3.0, "lightrain"), step("2026-11-18T03:00:00Z", -1.0, "heavyrain")]}}
        t = fc.met_twice_daily(doc, 0.0)
        self.assertEqual([x["is_daytime"] for x in t], [True, False])
        self.assertEqual(t[0]["native_temperature"], 5.0)
        self.assertEqual(t[0]["condition"], "sunny")      # the step nearest noon, not the first
        self.assertEqual(t[1]["native_temperature"], -1.0)  # a night shows its low

    def test_solar_offset(self):
        self.assertEqual(fc._solar_offset(15.6).total_seconds(), 3600)
        self.assertEqual(fc._solar_offset(-87.6).total_seconds(), -6 * 3600)
        self.assertEqual(fc._solar_offset(-157.9).total_seconds(), -11 * 3600)


class TestBuild(unittest.TestCase):
    def test_nws(self):
        now = fc._parse(PER_H[3]["startTime"])
        b = fc.build(fc.NWS, NWS_D, NWS_H, -104.99, now)
        self.assertEqual(b["source"], fc.NWS)
        self.assertEqual(b["updated"], NWS_D["properties"]["updateTime"])
        self.assertEqual(len(b["hourly"]), 48)
        self.assertEqual(b["now"]["datetime"], PER_H[3]["startTime"])
        self.assertEqual(b["daily"], fc.nws_daily(NWS_D))
        self.assertEqual(len(b["twice_daily"]), len(PER_D))
        self.assertEqual({k for k in b}, {"daily", "twice_daily", "hourly", "updated", "source", "now"})

    def test_met(self):
        now = fc._parse(STEPS[2]["time"])
        b = fc.build(fc.MET, MET, MET, MET_LON, now)
        self.assertEqual(b["source"], fc.MET)
        self.assertEqual(b["updated"], MET["properties"]["meta"]["updated_at"])
        self.assertEqual(b["now"]["datetime"], STEPS[2]["time"])

    def test_current_before_first_hour(self):
        h = fc.nws_hourly(NWS_H)
        early = datetime(2000, 1, 1, tzinfo=timezone.utc)
        self.assertEqual(fc.current(h, early), h[0])
        self.assertIsNone(fc.current([], early))

    def test_current_mid_hour(self):
        h = fc.nws_hourly(NWS_H)
        t = fc._parse(PER_H[5]["startTime"]).replace(minute=30)
        self.assertEqual(fc.current(h, t)["datetime"], PER_H[5]["startTime"])


if __name__ == "__main__":
    unittest.main()
