"""MET Norway's warnings, marine forecasts and forecast points (Weather SSOT item 310; Lee 2026-10-28 17:04).
Fixtures are MET's own answers of 2026-10-28 evening: the warning feed (18 warnings), three CAP files (a Yellow
gale, a Yellow gale over four polygons, a Green cancellation), the sea and coastal text forecasts, and
Locationforecast at Longyearbyen.
"""

import copy
import json
import unittest
from datetime import datetime, timezone

from _load import FIXTURES, load

met = load("met")
const = load("const")
NOW = datetime(2026, 10, 28, 22, 10, tzinfo=timezone.utc)


def raw(name):
    return (FIXTURES / name).read_bytes()


def js(name):
    return json.loads(raw(name))


RSS = raw("met_alerts_current_en_20261028T2207Z.rss")
GALE = raw("met_cap_gale_yellow_E3_20261028.xml")
MULTI = raw("met_cap_multipolygon_20261028.xml")
GREEN = raw("met_cap_green_20261028.xml")
SEA = js("met_textforecast_sea_en_20261028T2140Z.json")
COAST = js("met_textforecast_coast_en_20261028T1609Z.json")
LYR = js("met_locationforecast_longyearbyen_20261028T2113Z.json")


class TestFeed(unittest.TestCase):
    def test_rss_lists_every_warning(self):
        ids = met.parse_rss(RSS)
        self.assertEqual(len(ids), 18)
        self.assertEqual(ids[0], "2.49.0.1.578.0.261028220000.0858_1_0")
        self.assertEqual(len(set(ids)), 18)

    def test_rss_bad(self):
        for bad in (None, b"", b"<rss><channel><item><title>x</title></item>", b"not xml"):
            self.assertEqual(met.parse_rss(bad), [])


class TestCap(unittest.TestCase):
    def test_english_info_and_fields(self):
        c = met.parse_cap(GALE)
        self.assertEqual((c["status"], c["msg_type"], c["event"], c["colour"], c["level"], c["area"], c["domain"]),
                         ("Actual", "Alert", "Gale Force", "Yellow", 2, "E3", "marine"))
        self.assertEqual(c["headline"], "Gale Force, E3, 28 October 22:00 UTC to 29 October 00:00 UTC.")
        self.assertEqual(c["description"], "Southwest gale 8.")
        self.assertTrue(c["instruction"].startswith("Do not go out in a small boat"))
        self.assertEqual((c["onset"], c["expires"]), (datetime(2026, 10, 28, 22, 0, tzinfo=timezone.utc),
                                                      datetime(2026, 10, 29, 0, 0, tzinfo=timezone.utc)))

    def test_ring_is_lon_lat_and_closed(self):
        # CAP: "67.5,0.0 70.0,0.0 70.0,10.0 68.22,10.0 67.5,10.0 67.5,0.0" (lat,lon)
        r = met.parse_cap(GALE)["rings"]
        self.assertEqual(r, [[[0.0, 67.5], [0.0, 70.0], [10.0, 70.0], [10.0, 68.22], [10.0, 67.5], [0.0, 67.5]]])
        self.assertEqual(met._ring("1,2 3,4 5,6"), [[2.0, 1.0], [4.0, 3.0], [6.0, 5.0], [2.0, 1.0]])
        self.assertIsNone(met._ring("1,2 3,4"))
        self.assertIsNone(met._ring("1,2 3;4 5,6"))

    def test_four_polygons(self):
        self.assertEqual(len(met.parse_cap(MULTI)["rings"]), 4)

    def test_norwegian_only_falls_back_to_the_first_info(self):
        no = GALE.decode("utf-8")
        start = no.index("<info>", no.index("<info>") + 1)
        no = no[:start] + no[no.index("</info>", start) + 7:]
        c = met.parse_cap(no.encode("utf-8"))
        self.assertEqual(c["event"], "Kuling")

    def test_colour_from_level_when_none(self):
        x = GALE.decode("utf-8").replace("<value>Yellow</value>", "<value>Purple</value>").replace(
            "2; yellow; Moderate", "3; orange; Severe")
        self.assertEqual(met.parse_cap(x.encode("utf-8"))["colour"], "Orange")

    def test_bad(self):
        for bad in (None, b"", b"<alert/>", b"oops"):
            self.assertIsNone(met.parse_cap(bad))


class TestWarnings(unittest.TestCase):
    def test_drawn(self):
        w = met.publish_warnings([met.parse_cap(x) for x in (GALE, MULTI, GREEN)], NOW)
        self.assertEqual(w["count"], 2)
        self.assertEqual(w["highest"], "Yellow")
        self.assertEqual(w["styles"], {"Yellow warning": {"color": "#FFD500", "priority": 3}})
        self.assertEqual([(p["type"], len(p["coordinates"])) for p in w["polygons"]], [("Polygon", 1), ("MultiPolygon", 4)])
        p = w["polygons"][0]
        self.assertEqual(p["info"]["title"], "Gale Force, E3, 28 October 22:00 UTC to 29 October 00:00 UTC.")
        self.assertEqual(p["info"]["text"].split("\n"), [
            "Southwest gale 8.",
            "Moderately high waves: Waves with breaking crests forming spindrift. Considerable airborne spray.",
            "Do not go out in a small boat: High risk of dangerous situations when in a small boat at sea",
            "Wed 28 Oct 22:00 to Thu 29 Oct 00:00 UTC", "Yellow level. MET Norway"])
        self.assertEqual(p["warning"], "2.49.0.1.578.0.261028220000.0858_1_0")

    def test_green_is_a_cancellation_and_not_drawn(self):
        c = met.parse_cap(GREEN)
        self.assertEqual(c["colour"], "Green")
        self.assertTrue(c["headline"].startswith("Cancelled"))
        self.assertEqual(met.publish_warnings([c], NOW), met.empty_warnings())

    def test_every_colour(self):
        base = met.parse_cap(GALE)
        caps = []
        for col in ("Red", "Orange", "Yellow"):
            c = copy.deepcopy(base)
            c["colour"] = col
            caps.append(c)
        w = met.publish_warnings(caps, NOW)
        self.assertEqual(w["styles"], {"Red warning": {"color": "#E8202A", "priority": 1},
                                       "Orange warning": {"color": "#FF8C00", "priority": 2},
                                       "Yellow warning": {"color": "#FFD500", "priority": 3}})
        self.assertEqual(w["highest"], "Red")
        self.assertEqual(met.publish_warnings(caps[1:], NOW)["highest"], "Orange")

    def test_expired_cancelled_test_and_empty_not_drawn(self):
        c = met.parse_cap(GALE)
        self.assertEqual(met.publish_warnings([c], datetime(2026, 10, 29, 0, 0, tzinfo=timezone.utc))["count"], 0)
        self.assertEqual(met.publish_warnings([c], datetime(2026, 10, 28, 23, 59, tzinfo=timezone.utc))["count"], 1)
        for k, v in (("msg_type", "Cancel"), ("status", "Test"), ("rings", []), ("colour", None)):
            d = dict(c)
            d[k] = v
            self.assertEqual(met.publish_warnings([d], NOW)["count"], 0, k)
        d = dict(c)
        d["expires"] = None
        self.assertEqual(met.publish_warnings([d, None], NOW)["count"], 1)

    def test_rounded(self):
        c = met.parse_cap(GALE)
        c["rings"] = [[[1.23456, 2.34567], [1.23456, 2.34567], [3.0, 4.0], [5.0, 6.0], [1.23456, 2.34567]]]
        p = met.publish_warnings([c], NOW)["polygons"][0]
        self.assertEqual(p["coordinates"], [[[1.235, 2.346], [3.0, 4.0], [5.0, 6.0], [1.235, 2.346]]])


class TestMarine(unittest.TestCase):
    def test_every_area(self):
        m = met.publish_marine(SEA, COAST)
        self.assertEqual(m["count"], 56 + 39)
        self.assertEqual(m["styles"], {"Sea area forecast": {"color": "#4F86B5", "priority": 2},
                                       "Coastal forecast": {"color": "#2E9C9C", "priority": 1}})
        self.assertEqual(m["issued"], "2026-10-28T21:40:19Z")
        self.assertEqual(sum(p["event"] == "Sea area forecast" for p in m["polygons"]), 56)

    def test_to_the_pole(self):
        north = max(pt[1] for p in met.publish_marine(SEA, None)["polygons"] for ring in p["coordinates"] for pt in ring)
        self.assertGreaterEqual(north, 89.99)  # MET's own: 89.999
        titles = {p["info"]["title"] for p in met.publish_marine(None, COAST)["polygons"]}
        self.assertIn("Spitsbergen", titles)

    def test_info(self):
        m = met.publish_marine(SEA, COAST)
        e3 = next(p for p in m["polygons"] if p["info"]["title"] == "E3")
        lines = e3["info"]["text"].split("\n")
        self.assertEqual(lines[0], "Forecast for E3 from Wednesday, 28 October 22:00 to Friday, 30 October 10:00")
        self.assertIn("Wind warning: Southwest gale 8 from Wednesday 22utc until Thursday 00utc", lines)
        self.assertTrue(lines[-2].startswith("Synopsis: Storm centre 980 hPa"))
        self.assertEqual(lines[-1], "MET Norway")
        coast = next(p for p in m["polygons"] if p["event"] == "Coastal forecast")
        self.assertFalse(any(x.startswith("Synopsis") for x in coast["info"]["text"].split("\n")))

    def test_warning_names(self):
        doc = copy.deepcopy(SEA)
        p = doc["features"][0]["properties"]
        p["ice_warning"], p["polarlow_warning"], p["wind_warning"] = "Icing", "A polar low", " "
        text = met.publish_marine(doc, None)["polygons"][0]["info"]["text"]
        self.assertIn("Ice warning: Icing", text)
        self.assertIn("Polar low warning: A polar low", text)
        self.assertNotIn("Wind warning", text)

    def test_bad(self):
        self.assertEqual(met.publish_marine(None, None)["count"], 0)
        doc = copy.deepcopy(SEA)
        doc["features"][0]["geometry"] = {"type": "Point", "coordinates": [1, 2]}
        doc["features"][1]["properties"]["text"] = ""
        doc["features"][2] = "x"
        self.assertEqual(met.publish_marine(doc, None)["count"], 53)


class TestPoint(unittest.TestCase):
    def test_longyearbyen(self):
        p = met.point(LYR, "Longyearbyen", 78.2232, 15.6267)
        self.assertEqual((p["key"], p["name"], p["lat"], p["lon"]), ("longyearbyen", "Longyearbyen forecast", 78.2232, 15.6267))
        a = p["attrs"]
        self.assertEqual((a["identity"], a["marker_label"], a["map_layer"], a["marker_color"]),
                         ("Longyearbyen", "2°", "fixed", "#1F6FB2"))
        self.assertEqual((a["temperature_c"], a["wind_speed_kmh"], a["wind_from_deg"], a["pressure_hpa"]),
                         (1.8, 13.7, 189.0, 1001.1))
        self.assertEqual((a["next_1h_conditions"], a["next_6h_precipitation_mm"]), ("Partly cloudy", 0.0))
        self.assertEqual((a["forecast_for"], a["forecast_updated"]), ("2026-10-28T21:00:00Z", "2026-10-28T21:13:34Z"))
        lines = a["forecast"].split("\n")
        self.assertEqual(lines[0], "Now: 1.8 °C, partly cloudy, wind 14 km/h from S")
        self.assertEqual(lines[1], "Thu 29 Oct 06:00 UTC: 0 °C, partly cloudy, 0.0 mm in 6 h")
        self.assertEqual(len(lines), 5)
        self.assertEqual(a["marker_info"], {"title": "Longyearbyen forecast",
                                            "text": a["forecast"] + "\nMade Wed 28 Oct 21:13 UTC. MET Norway"})

    def test_bad(self):
        self.assertIsNone(met.point(None, "x", 0, 0))
        self.assertIsNone(met.point({"properties": {"meta": {}, "timeseries": []}}, "x", 0, 0))
        doc = copy.deepcopy(LYR)
        del doc["properties"]["timeseries"][0]["data"]["instant"]["details"]["air_temperature"]
        self.assertIsNone(met.point(doc, "x", 0, 0))

    def test_conditions(self):
        self.assertEqual(met.conditions("lightrainshowersandthunder_day"), "Light rain showers and thunder")
        self.assertEqual(met.conditions("clearsky_polartwilight"), "Clear sky")
        self.assertEqual(met.conditions("heavysleet"), "Heavy sleet")
        for bad in (None, "", "tornado", 3):
            self.assertIsNone(met.conditions(bad))

    def test_compass_and_when(self):
        self.assertEqual([met._compass(d) for d in (0, 22.4, 22.5, 189, 337.4, 337.5, 359.9)], ["N", "N", "NE", "S", "NW", "N", "N"])
        self.assertEqual(met._when(datetime(2026, 11, 5, 0, 0, tzinfo=timezone.utc)), "Thu 5 Nov 00:00")


class TestConstants(unittest.TestCase):
    def test_rules(self):
        self.assertEqual(const.MET_POINTS, (("Longyearbyen", 78.2232, 15.6267),))
        self.assertEqual((const.MET_WARNINGS_SHAPE_ORDER, const.MET_MARINE_SHAPE_ORDER), (0, -5))
        self.assertGreater(const.MET_MARINE_SHAPE_ORDER, const.OUTLOOK_SHAPE_ORDER)
        self.assertEqual(const.MET_ALERTS_RSS, "https://api.met.no/weatherapi/metalerts/2.0/current.rss")
        self.assertGreaterEqual(const.MET_ALERTS_POLL_S, 300)
        self.assertGreaterEqual(const.MET_POINT_POLL_S, 1800)
        self.assertTrue(const.MET_ATTRIBUTION.startswith("Data from MET Norway"))
        self.assertNotIn(". ", const.MET_ATTRIBUTION)
        self.assertIn("+https://", const.USER_AGENT)


if __name__ == "__main__":
    unittest.main()
