"""observe: the nearest NWS station's latest report at a place (Weather SSOT item 350).

Fixtures are NWS's own answers of 2026-11-17 (bin\\ltw350_probe.py): the Grand Canyon Trailer Village gridpoint's
stations list (an APRS station 1.1 km away, the airport 12.6 km), KORD's latest (no gust), KLOT's plain latest (the
report served with every value null), HNYM8's (no temperature, calm wind) and G0564's (a gust).
"""

import json
import unittest
from datetime import datetime, timedelta, timezone

from _load import FIXTURES, load

ob = load("observe")
pl = load("places")


def fx(name):
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


STATIONS = fx("nws_stations_grand_canyon_20261117.json")
KORD = fx("nws_latest_KORD_20261117.json")
KLOT = fx("nws_latest_KLOT_empty_20261117.json")
HNYM8 = fx("nws_latest_HNYM8_notemp_20261117.json")
G0564 = fx("nws_latest_G0564_gust_20261117.json")
GC = (36.0540, -112.1150)   # Grand Canyon Trailer Village
NOW = datetime(2026, 11, 17, 9, 0, tzinfo=timezone.utc)


def report(time="2026-11-17T08:30:00+00:00", **vals):
    p = {"timestamp": time}
    for k, nws in (("temperature", "temperature"), ("wind_speed", "windSpeed"), ("wind_gust", "windGust"),
                   ("wind_direction", "windDirection")):
        unit = {"temperature": "wmoUnit:degC", "wind_direction": "wmoUnit:degree_(angle)"}.get(k, "wmoUnit:km_h-1")
        p[nws] = {"unitCode": unit, "value": vals.get(k), "qualityControl": "V" if vals.get(k) is not None else "Z"}
    return ob.parse({"properties": p})


ST = [{"id": s, "name": s, "provider": "ASOS", "km": k} for s, k in (("A", 5.0), ("B", 20.0), ("C", 40.0))]


class TestStations(unittest.TestCase):
    def test_nearest_first_by_the_place(self):
        s = ob.stations(STATIONS, *GC)
        self.assertEqual(s[0]["id"], "AR412")
        self.assertAlmostEqual(s[0]["km"], 1.1, delta=0.1)
        self.assertEqual(s[0]["provider"], "APRSWXNET")
        self.assertEqual([x["km"] for x in s], sorted(x["km"] for x in s))
        self.assertEqual(len(s), len(STATIONS["features"]))

    def test_airports_only(self):
        s = ob.stations(STATIONS, *GC, airports_only=True)
        self.assertEqual(s[0]["id"], "KGCN")
        self.assertAlmostEqual(s[0]["km"], 12.6, delta=0.1)
        self.assertTrue(s and all(x["provider"] in ob.AIRPORT_PROVIDERS for x in s))
        self.assertNotIn("AR412", {x["id"] for x in s})
        self.assertIn("KCMR", {x["id"] for x in s})   # OTHER-MTR counts as an airport

    def test_bad_entries_skipped(self):
        doc = {"features": [{"properties": {"stationIdentifier": "X"}, "geometry": None},
                            {"properties": {}, "geometry": {"coordinates": [0, 0]}},
                            {"properties": {"stationIdentifier": "OK", "provider": ""},
                             "geometry": {"coordinates": [-112.0, 36.0]}}]}
        s = ob.stations(doc, *GC)
        self.assertEqual([x["id"] for x in s], ["OK"])
        self.assertIsNone(s[0]["provider"])
        self.assertEqual(ob.stations(doc, *GC, airports_only=True), [])
        for bad in (None, {}, [], {"features": None}):
            self.assertEqual(ob.stations(bad, *GC), [])


class TestParse(unittest.TestCase):
    def test_airport(self):
        o = ob.parse(KORD)
        p = KORD["properties"]
        self.assertEqual(o["time"], p["timestamp"])
        self.assertEqual(o["temperature"], p["temperature"]["value"])
        self.assertEqual(o["wind_speed"], p["windSpeed"]["value"])
        self.assertEqual(o["wind_direction"], p["windDirection"]["value"])
        self.assertIsNone(o["wind_gust"])   # none reported

    def test_empty_report(self):
        o = ob.parse(KLOT)
        self.assertEqual([o[f] for f in ob.FIELDS], [None] * 4)

    def test_no_thermometer_calm_wind(self):
        o = ob.parse(HNYM8)
        self.assertIsNone(o["temperature"])
        self.assertEqual(o["wind_speed"], 0.0)   # calm is a value, not a gap

    def test_gust(self):
        self.assertEqual(ob.parse(G0564)["wind_gust"], G0564["properties"]["windGust"]["value"])

    def test_units_and_flags(self):
        def one(unit, value, qc="V", field="windSpeed"):
            return ob.parse({"properties": {"timestamp": "2026-11-17T08:00:00+00:00",
                                            field: {"unitCode": unit, "value": value, "qualityControl": qc}}})
        self.assertEqual(one("wmoUnit:m_s-1", 10)["wind_speed"], 36.0)
        self.assertEqual(one("wmoUnit:degF", 50, field="temperature")["temperature"], 10.0)
        self.assertIsNone(one("wmoUnit:knot", 10)["wind_speed"])
        self.assertIsNone(one("wmoUnit:km_h-1", 10, qc="X")["wind_speed"])
        self.assertIsNone(one("wmoUnit:km_h-1", 10, qc="B")["wind_speed"])
        self.assertEqual(one("wmoUnit:km_h-1", 10, qc="Q")["wind_speed"], 10.0)
        self.assertIsNone(one("wmoUnit:km_h-1", True)["wind_speed"])
        self.assertIsNone(one("wmoUnit:km_h-1", "10")["wind_speed"])
        self.assertIsNone(one("wmoUnit:degC", 5, field="windDirection")["wind_direction"])
        self.assertIsNone(one("wmoUnit:K", 280, field="temperature")["temperature"])

    def test_not_an_observation(self):
        for bad in (None, [], {}, {"properties": None}, {"properties": {"timestamp": None}},
                    {"properties": {"timestamp": "yesterday"}}, {"properties": {"timestamp": "2026-11-17T08:00:00"}}):
            self.assertIsNone(ob.parse(bad), bad)


class TestPick(unittest.TestCase):
    def test_fresh_boundary(self):
        o = report("2026-11-17T07:00:00+00:00", wind_speed=5)
        self.assertTrue(ob.fresh(o, NOW))                                   # exactly 2 h
        self.assertFalse(ob.fresh(o, NOW + timedelta(seconds=1)))
        self.assertFalse(ob.fresh(None, NOW))
        self.assertEqual(ob.age_s(o, NOW), 7200)

    def test_falls_back_past_empty_and_stale(self):
        stale = report("2026-11-17T06:00:00+00:00", wind_speed=30, temperature=1)
        p = ob.pick([(ST[0], stale), (ST[1], report(wind_speed=12, wind_gust=None, wind_direction=200)),
                     (ST[2], report(temperature=4))], NOW)
        self.assertEqual(p["wind"]["station"]["id"], "B")
        self.assertEqual(p["temperature"]["station"]["id"], "C")
        self.assertTrue(ob.complete(p))

    def test_nearest_wins_and_empty_and_404_skipped(self):
        p = ob.pick([(ST[0], ob.parse(KLOT) | {"time": "2026-11-17T08:15:00+00:00"}), (ST[1], None),
                     (ST[2], report(wind_speed=3, temperature=2))], NOW)
        self.assertEqual(p["wind"]["station"]["id"], "C")
        p = ob.pick([(ST[0], report(wind_speed=3, temperature=2)), (ST[1], report(wind_speed=9, temperature=9))],
                    NOW)
        self.assertEqual((p["wind"]["station"]["id"], p["temperature"]["station"]["id"]), ("A", "A"))

    def test_wind_group_keeps_its_own_gust(self):
        # the nearest's calm with no gust is not mixed with a further station's gust
        p = ob.pick([(ST[0], report(wind_speed=0, wind_gust=None)), (ST[1], report(wind_speed=20, wind_gust=40))],
                    NOW)
        self.assertEqual(p["wind"]["station"]["id"], "A")
        self.assertIsNone(p["wind"]["obs"]["wind_gust"])

    def test_temperature_alone(self):
        p = ob.pick([(ST[0], ob.parse(HNYM8)), (ST[1], ob.parse(KORD))], NOW)
        self.assertEqual(p["wind"]["station"]["id"], "A")
        self.assertEqual(p["temperature"]["station"]["id"], "B")

    def test_nothing(self):
        p = ob.pick([], NOW)
        self.assertEqual(p, {"wind": None, "temperature": None})
        self.assertFalse(ob.complete(p))
        self.assertFalse(ob.complete({"wind": {"x": 1}, "temperature": None}))


class TestPointStations(unittest.TestCase):
    def test_points_name_the_list(self):
        land = pl.point_info(fx("nws_points_chicago_loop_20261117.json"))
        lake = pl.point_info(fx("nws_points_lake_michigan_20261117.json"))
        gulf = pl.point_info(fx("nws_points_gulf_offshore_20261117.json"))
        self.assertEqual(land["stations"], "https://api.weather.gov/gridpoints/LOT/76,73/stations")
        self.assertEqual(lake["stations"], "https://api.weather.gov/gridpoints/MKX/107,13/stations")
        self.assertIsNone(gulf["stations"])   # open water far offshore: no list, no sensors' station

    def test_cache_keeps_it_and_asks_older_entries_again(self):
        now = 1_000_000.0
        c = pl.remember([], 41.88, -87.63, {"forecast/ILZ014"}, None, now, 1000, 64, stations="https://x/stations")
        self.assertEqual(pl.cached_point(c, 41.88, -87.63, now, 1000, 86400)["stations"], "https://x/stations")
        c = pl.remember([], 41.88, -87.63, set(), None, now, 1000, 64)
        self.assertIsNone(pl.cached_point(c, 41.88, -87.63, now, 1000, 86400)["stations"])
        old = [{"lat": 41.88, "lon": -87.63, "keys": [], "grid": None, "at": now}]   # stored before item 350
        self.assertIsNone(pl.cached_point(old, 41.88, -87.63, now, 1000, 86400))


if __name__ == "__main__":
    unittest.main()
