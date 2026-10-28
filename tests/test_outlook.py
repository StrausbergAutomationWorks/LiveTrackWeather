"""The SPC Day 1 categorical outlook (contract D16; Lee 2026-10-28: Day 1 categorical only,
Marginal and up). Fixtures are SPC's own files of 2026-10-28: Day 1 issued 16:20Z (general
thunderstorms, Marginal, Slight) and Day 2 issued 17:20Z (general thunderstorms only).
"""

import copy
import json
import unittest
from datetime import datetime, timezone

from _load import FIXTURES, load

ol = load("outlook")
const = load("const")
NOW = datetime(2026, 10, 28, 19, 0, tzinfo=timezone.utc)


def fx(name):
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


DAY1 = fx("spc_day1otlk_cat_20261028T1620Z.geojson")
QUIET = fx("spc_day2otlk_cat_20261028T1720Z_tstm_only.geojson")


class TestParse(unittest.TestCase):
    def test_marginal_and_up_only(self):
        o = ol.parse(DAY1, NOW)
        self.assertEqual([p["event"] for p in o["polygons"]], ["Marginal Risk", "Slight Risk"])
        self.assertEqual(o["styles"], {"Marginal Risk": {"color": "#66A366", "priority": 5},
                                       "Slight Risk": {"color": "#FFE066", "priority": 4}})
        self.assertEqual((o["level"], o["risk"]), (2, "Slight Risk"))
        self.assertTrue(all(p["type"] == "MultiPolygon" for p in o["polygons"]))

    def test_times(self):
        o = ol.parse(DAY1, NOW)
        self.assertEqual((o["issued"], o["valid_from"], o["valid_to"]),
                         ("2026-10-28T16:20:00Z", "2026-10-28T16:30:00Z", "2026-10-29T12:00:00Z"))

    def test_quiet_day_draws_nothing(self):
        o = ol.parse(QUIET, NOW)
        self.assertEqual((o["polygons"], o["styles"], o["level"], o["risk"]), ([], {}, 0, None))
        self.assertEqual(o["valid_to"], "2026-10-30T12:00:00Z")

    def test_expired_outlook_draws_nothing(self):
        self.assertEqual(ol.parse(DAY1, datetime(2026, 10, 29, 12, 0, tzinfo=timezone.utc)), ol.empty())
        self.assertEqual(ol.parse(DAY1, datetime(2026, 10, 29, 11, 59, tzinfo=timezone.utc))["level"], 2)

    def test_coordinates_rounded(self):
        o = ol.parse(DAY1, NOW)
        pt = o["polygons"][0]["coordinates"][0][0][0]
        self.assertEqual(len(pt), 2)
        self.assertEqual(pt, [round(pt[0], 3), round(pt[1], 3)])
        raw = next(f for f in DAY1["features"] if f["properties"]["LABEL"] == "MRGL")["geometry"]["coordinates"][0][0][0]
        self.assertAlmostEqual(pt[0], raw[0], places=3)

    def test_rounding_to_a_metre_scale(self):
        # SPC's own coordinates carry two decimals (the fixture), so round it here
        doc = copy.deepcopy(DAY1)
        f = next(f for f in doc["features"] if f["properties"]["LABEL"] == "SLGT")
        f["geometry"] = {"type": "Polygon", "coordinates": [[[-93.123456, 45.987654], [-92.0, 45.0], [-93.0, 44.5], [-93.123456, 45.987654]]]}
        p = next(p for p in ol.parse(doc, NOW)["polygons"] if p["event"] == "Slight Risk")
        self.assertEqual(p["coordinates"][0][0], [-93.123, 45.988])

    def test_every_category_and_fallback_colours(self):
        doc = copy.deepcopy(DAY1)
        tmpl = next(f for f in doc["features"] if f["properties"]["LABEL"] == "SLGT")
        doc["features"] = []
        for cat in ("TSTM", "MRGL", "SLGT", "ENH", "MDT", "HIGH"):
            f = copy.deepcopy(tmpl)
            f["properties"]["LABEL"] = cat
            f["properties"]["fill"] = "" if cat in ("ENH", "HIGH") else "#abcdef"
            doc["features"].append(f)
        o = ol.parse(doc, NOW)
        self.assertEqual([p["event"] for p in o["polygons"]],
                         ["Marginal Risk", "Slight Risk", "Enhanced Risk", "Moderate Risk", "High Risk"])
        self.assertEqual({e: s["priority"] for e, s in o["styles"].items()},
                         {"Marginal Risk": 5, "Slight Risk": 4, "Enhanced Risk": 3, "Moderate Risk": 2, "High Risk": 1})
        self.assertEqual(o["styles"]["Enhanced Risk"]["color"], "#FFA366")
        self.assertEqual(o["styles"]["High Risk"]["color"], "#EE99EE")
        self.assertEqual(o["styles"]["Moderate Risk"]["color"], "#ABCDEF")
        self.assertEqual((o["level"], o["risk"]), (5, "High Risk"))

    def test_malformed(self):
        self.assertEqual(ol.parse(None, NOW), ol.empty())
        self.assertEqual(ol.parse({"features": "x"}, NOW), ol.empty())
        doc = copy.deepcopy(DAY1)
        for f in doc["features"]:
            f["geometry"] = {"type": "GeometryCollection", "geometries": []}
        self.assertEqual(ol.parse(doc, NOW)["polygons"], [])
        doc = copy.deepcopy(DAY1)
        for f in doc["features"]:
            f["geometry"]["coordinates"] = []
        self.assertEqual(ol.parse(doc, NOW)["polygons"], [])

    def test_spc_time(self):
        self.assertEqual(ol.spc_time("202610281630"), datetime(2026, 10, 28, 16, 30, tzinfo=timezone.utc))
        for bad in (None, "", "2026102816", "20261328163a", "202613281630", 202610281630):
            self.assertIsNone(ol.spc_time(bad))


class TestConstants(unittest.TestCase):
    def test_under_the_alerts_and_the_source(self):
        self.assertLess(const.OUTLOOK_SHAPE_ORDER, 0)
        self.assertEqual(const.SPC_DAY1_URL, "https://www.spc.noaa.gov/products/outlook/day1otlk_cat.lyr.geojson")
        self.assertEqual(const.SPC_POLL_S, 300)


if __name__ == "__main__":
    unittest.main()
