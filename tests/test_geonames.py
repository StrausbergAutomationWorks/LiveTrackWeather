"""GeoNames with the user's username (Weather SSOT item 352 step 4b): geonames.py.

! Only ONE real GeoNames answer exists yet: Lee's account answered 401 "not confirmed" on 2026-11-18
(geonames_401_not_confirmed_20261118.json). Every other answer below is CONSTRUCTED from GeoNames' documented shapes
(the weather example Marc Wick posted on GeoNames' forum in 2024, Safe Software's 2008 example, the exception page)
and must be replaced by real answers once the account works.
"""

import json
import unittest
from datetime import datetime, timedelta, timezone

from _load import FIXTURES, load

gn = load("geonames")
observe = load("observe")

NOT_CONFIRMED = json.loads((FIXTURES / "geonames_401_not_confirmed_20261118.json").read_text(encoding="utf-8"))

# CONSTRUCTED, in the documented shape (field names and types as in GeoNames' examples).
MUNICH = {"weatherObservation": {
    "elevation": 448, "lng": 11.7833, "observation": "EDDM 121350Z 26012G24KT 9999 FEW030 15/08 Q1015 NOSIG",
    "ICAO": "EDDM", "clouds": "few clouds", "dewPoint": "8", "cloudsCode": "FEW", "datetime": "2024-06-12 13:50:00",
    "countryCode": "DE", "temperature": "15", "humidity": 63, "stationName": "Munich", "weatherCondition": "n/a",
    "windDirection": 260, "hectoPascAltimeter": 1015, "windSpeed": "12", "lat": 48.35}}
# The forum's real Bangalore answer as posted (no observation, datetime or ICAO were shown there), with those added.
BANGALORE = {"weatherObservation": {
    "countryCode": "IN", "temperature": "29", "humidity": 66, "stationName": "Bangalore / Hindustan",
    "weatherCondition": "n/a", "windDirection": 250, "hectoPascAltimeter": 1011, "windSpeed": "11", "lat": 12.95,
    "lng": 77.6667, "ICAO": "VOBG", "datetime": "2024-06-12 06:30:00"}}


class TestStatus(unittest.TestCase):
    def test_real_401(self):
        self.assertEqual(gn.status(NOT_CONFIRMED)[0], 10)
        self.assertFalse(gn.answered(401, NOT_CONFIRMED))
        self.assertEqual(gn.backoff_s(401, NOT_CONFIRMED), gn.AUTH_BACKOFF_S)
        self.assertEqual(gn.check_error(401, NOT_CONFIRMED), "geonames_not_confirmed")
        # real, 2026-11-18 ~06:2xZ, the same username's next answer
        unknown = json.loads((FIXTURES / "geonames_401_user_does_not_exist_20261118.json").read_text(encoding="utf-8"))
        self.assertEqual(gn.check_error(401, unknown), "geonames_user_rejected")
        self.assertEqual(gn.backoff_s(401, unknown), gn.AUTH_BACKOFF_S)

    def test_limits_and_errors(self):
        def st(v, msg=""):
            return {"status": {"message": msg, "value": v}}
        self.assertEqual(gn.backoff_s(200, st(19)), 3600)
        self.assertEqual(gn.backoff_s(200, st(18)), 3 * 3600)
        self.assertEqual(gn.backoff_s(200, st(20)), 24 * 3600)
        self.assertEqual(gn.backoff_s(200, st(22)), gn.OTHER_BACKOFF_S)
        self.assertEqual(gn.backoff_s(200, st(10, "invalid user")), gn.AUTH_BACKOFF_S)
        self.assertEqual(gn.backoff_s(200, st(15, "no ocean")), 0, "no result is an answer")
        self.assertEqual(gn.backoff_s(200, MUNICH), 0)
        self.assertEqual(gn.backoff_s(200, None), gn.OTHER_BACKOFF_S, "not JSON")
        self.assertEqual(gn.backoff_s(503, None), gn.OTHER_BACKOFF_S)
        self.assertTrue(gn.answered(200, st(15)))
        self.assertTrue(gn.answered(404, st(15)), "no result whatever the HTTP status")
        self.assertFalse(gn.answered(200, []))
        self.assertFalse(gn.answered(500, {}))
        self.assertEqual(gn.status({"status": {"value": "x", "message": "m"}}), (-1, "m"))
        self.assertIsNone(gn.status({"status": "x"}))

    def test_check_error(self):
        def st(v, msg=""):
            return {"status": {"message": msg, "value": v}}
        self.assertIsNone(gn.check_error(200, {"gtopo30": 181, "lat": 41.88, "lng": -87.64}))
        self.assertEqual(gn.check_error(200, st(10, "user account not enabled to use the free webservice. "
                                                    "Please enable it on your account page")), "geonames_not_enabled")
        self.assertEqual(gn.check_error(200, st(10, "invalid user")), "geonames_user_rejected")
        self.assertEqual(gn.check_error(401, None), "geonames_user_rejected")
        self.assertEqual(gn.check_error(200, st(19, "the hourly limit of 1000 credits")), "geonames_over_limit")
        self.assertEqual(gn.check_error(503, None), "geonames_cannot_connect")
        self.assertEqual(gn.check_error(200, {"other": 1}), "geonames_cannot_connect")


class TestBudget(unittest.TestCase):
    def test_poll(self):
        self.assertEqual(gn.poll_s(1, 300), 300)
        self.assertEqual(gn.poll_s(8, 300), 300, "8 places at 5 minutes is 4,608 credits a day")
        self.assertEqual(gn.poll_s(9, 300), 312)
        self.assertEqual(gn.poll_s(20, 300), 692)
        self.assertEqual(gn.poll_s(0, 300), 300)
        for n in (1, 5, 20, 100):
            s = gn.poll_s(n, 300)
            self.assertLessEqual(n * gn.CREDITS_WEATHER * 86400 / s, gn.DAILY_SHARE + 1e-6)
            self.assertLessEqual(n * gn.CREDITS_WEATHER * 3600 / s, 500, "under half the hourly 1,000")

    def test_params(self):
        self.assertEqual(gn.params("u", 59.913912, 10.752212), {"username": "u", "lat": "59.9139", "lng": "10.7522"})
        self.assertEqual(gn.params("u"), {"username": "u"})
        self.assertTrue(gn.WEATHER_URL.startswith("https://secure.geonames.org/"))
        self.assertEqual(gn.scrub("a=SECRET&b", "SECRET"), "a=<username>&b")
        self.assertEqual(gn.scrub("x", None), "x")


class TestMetar(unittest.TestCase):
    def test_wind(self):
        self.assertEqual(gn.metar_wind("EGLL 180020Z 24015G25KT 9999"),
                         {"wind_speed": 27.78, "wind_gust": 46.3, "wind_direction": 240.0})
        self.assertEqual(gn.metar_wind("XXXX 1Z VRB03KT"), {"wind_speed": 5.56, "wind_gust": None, "wind_direction": None})
        self.assertEqual(gn.metar_wind("XXXX 1Z 00000KT"), {"wind_speed": 0.0, "wind_gust": None, "wind_direction": None})
        self.assertEqual(gn.metar_wind("UUEE 1Z 27005MPS 9999")["wind_speed"], 18.0)
        self.assertEqual(gn.metar_wind("XXXX 1Z 090010KMH")["wind_speed"], 10.0, "three-digit speed")
        self.assertEqual(gn.metar_wind("XXXX 1Z 36010KT")["wind_direction"], 0.0)
        self.assertIsNone(gn.metar_wind("XXXX 1Z /////KT 9999"))
        self.assertIsNone(gn.metar_wind("R27/240015KT"), "not a token of its own")
        self.assertIsNone(gn.metar_wind(None))

    def test_temperature(self):
        self.assertEqual(gn.metar_temperature("X 1Z 9999 M05/M10 Q1000"), -5.0)
        self.assertEqual(gn.metar_temperature("X 1Z 9999 12/07 Q1000"), 12.0)
        self.assertEqual(gn.metar_temperature("X 1Z 9999 12/ Q1000"), 12.0)
        self.assertIsNone(gn.metar_temperature("X 1Z 1/2SM"))
        self.assertIsNone(gn.metar_temperature(None))


class TestWeather(unittest.TestCase):
    def test_parse(self):
        st, ob = gn.parse_weather(MUNICH, 48.1374, 11.5755)
        self.assertEqual((st["id"], st["name"], st["provider"]), ("EDDM", "Munich", "GeoNames (METAR)"))
        self.assertAlmostEqual(st["km"], 28.4, delta=0.5)
        self.assertEqual(ob, {"time": "2024-06-12T13:50:00+00:00", "temperature": 15.0, "wind_speed": 22.22,
                              "wind_gust": 44.45, "wind_direction": 260.0})

    def test_fields_when_no_metar(self):
        _st, ob = gn.parse_weather(BANGALORE, 12.97, 77.59)
        self.assertEqual((ob["wind_speed"], ob["wind_direction"], ob["wind_gust"], ob["temperature"]),
                         (20.37, 250.0, None, 29.0))
        calm = json.loads(json.dumps(BANGALORE))
        calm["weatherObservation"]["windSpeed"] = "00"
        self.assertIsNone(gn.parse_weather(calm, 12.97, 77.59)[1]["wind_direction"], "calm has no direction")
        metar_t = json.loads(json.dumps(MUNICH))
        del metar_t["weatherObservation"]["temperature"]
        self.assertEqual(gn.parse_weather(metar_t, 48.1, 11.6)[1]["temperature"], 15.0, "from the METAR")

    def test_no_station(self):
        self.assertIsNone(gn.parse_weather({"status": {"message": "no observation found", "value": 15}}, 1, 2))
        self.assertIsNone(gn.parse_weather(None, 1, 2))
        bad = json.loads(json.dumps(MUNICH))
        bad["weatherObservation"]["datetime"] = "12 June"
        self.assertIsNone(gn.parse_weather(bad, 1, 2))
        nameless = json.loads(json.dumps(MUNICH))
        del nameless["weatherObservation"]["ICAO"], nameless["weatherObservation"]["stationName"]
        self.assertIsNone(gn.parse_weather(nameless, 1, 2))
        nopos = json.loads(json.dumps(MUNICH))
        del nopos["weatherObservation"]["lat"]
        self.assertIsNone(gn.parse_weather(nopos, 1, 2)[0]["km"])

    def test_feeds_item_350s_pick(self):
        got = gn.parse_weather(MUNICH, 48.1374, 11.5755)
        when = datetime(2024, 6, 12, 13, 50, tzinfo=timezone.utc)
        p = observe.pick([got], when + timedelta(minutes=30))
        self.assertEqual(p["wind"]["station"]["id"], "EDDM")
        self.assertEqual(p["temperature"]["obs"]["temperature"], 15.0)
        self.assertEqual(observe.pick([got], when + timedelta(hours=3)), {"wind": None, "temperature": None},
                         "older than 2 hours: unavailable, as for NWS")


class TestOcean(unittest.TestCase):
    def test_ocean(self):
        self.assertEqual(gn.parse_ocean({"ocean": {"distance": "0", "geonameId": 2960848, "name": "North Sea"}}),
                         (True, "North Sea"))
        self.assertEqual(gn.parse_ocean({"status": {"message": "we are afraid we could not find an ocean", "value": 15}}),
                         (True, None), "land: answered, no sea")
        self.assertEqual(gn.parse_ocean(NOT_CONFIRMED), (False, None))
        self.assertEqual(gn.parse_ocean(None), (False, None))
        self.assertEqual(gn.parse_ocean({"ocean": {"name": "  "}}), (False, None))


if __name__ == "__main__":
    unittest.main()
