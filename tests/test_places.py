"""places: is a place inside an alert (Weather SSOT item 334), against NWS's own answers.

The fixture is one moment, 2026-11-17 05:25Z: the alerts any of 38 points touches, each point's zones as
NWS's /zones?point= gave them, and the alerts NWS's /alerts/active?point= gave for it. The local answer
must equal NWS's at every point (MEASURED 38 of 38 before this test was written, Weather SSOT 2r).
"""

import json
import unittest
from datetime import datetime, timezone

from _load import COMP, FIXTURES, load

alerts = load("alerts")
places = load("places")
met = load("met")

FIX = json.loads((FIXTURES / "places_nws_20261117T0525Z.json").read_text(encoding="utf-8"))
COLOURS = json.loads((COMP / "data" / "nws_hazard_colours.json").read_text(encoding="utf-8"))["events"]
LIVE = alerts.live_list(FIX, COLOURS)
RECORDS = LIVE["records"]
# NWS's point answers name alerts by `id` (a urn); the records carry `@id` (a link a user can open).
URL_OF = {f["properties"]["id"]: f["properties"]["@id"] for f in FIX["features"]}
POINTS = {p["name"]: p for p in FIX["points"]}


def at(point, records=RECORDS, keys="nws"):
    k = set(point["zones"]) if keys == "nws" else keys
    return places.alerts_at(records, k, point["lat"], point["lon"])


class TestAgainstNws(unittest.TestCase):
    def test_every_point_equals_nws(self):
        self.assertEqual(len(FIX["points"]), 38)
        for p in FIX["points"]:
            ours = {r["id"] for r in at(p)}
            nws = {URL_OF[i] for i in p["nws_ids"]}
            self.assertEqual(ours, nws, p["name"])

    def test_points_with_alerts_are_most_of_them(self):
        # the comparison is not passing on empty sets
        self.assertGreaterEqual(sum(1 for p in FIX["points"] if p["nws_ids"]), 25)

    def test_polygon_warning_does_not_fill_its_county(self):
        # point_19: in county/TXC311, which the Flood Warning's polygon touches, but outside the polygon
        p = POINTS["point_19"]
        self.assertIn("county/TXC311", p["zones"])
        flood = [r for r in RECORDS if r["polygon"] is not None and r["event"] == "Flood Warning"]
        self.assertTrue(flood)
        self.assertEqual(at(p), [])
        # the same warning holds point_18, inside its polygon, in the same county
        self.assertTrue(any(r["event"] == "Flood Warning" for r in at(POINTS["point_18"])))

    def test_polygon_records_keep_no_zones(self):
        for r in RECORDS:
            if r["polygon"] is not None:
                self.assertEqual(r["zones"], [])

    def test_sitka_land_point_is_not_in_the_marine_zone(self):
        # the shape file's 500 m simplification put point_13 inside forecast/PKZ032; NWS says it is on land
        p = POINTS["point_13"]
        self.assertNotIn("forecast/PKZ032", p["zones"])
        self.assertTrue(any("forecast/PKZ032" in r["zones"] for r in RECORDS))
        self.assertEqual(at(p), [])
        self.assertTrue(at(p, keys={"forecast/PKZ032"}))

    def test_unknown_zones_still_test_polygons(self):
        p = POINTS["point_18"]
        found = at(p, keys=None)
        self.assertTrue(found)
        self.assertTrue(all(r["polygon"] is not None for r in found))
        self.assertEqual(at(POINTS["point_00"], keys=None), [])


class TestZoneAnswers(unittest.TestCase):
    def read(self, name):
        return json.loads((FIXTURES / f"nws_zones_point_{name}_20261117.json").read_text(encoding="utf-8"))

    def test_land_point(self):
        self.assertEqual(places.zone_keys(self.read("chicago_loop")),
                         {"county/ILC031", "fire/ILZ014", "forecast/ILZ104"})

    def test_water_point(self):
        self.assertEqual(places.zone_keys(self.read("lake_michigan")), {"forecast/LMZ779"})

    def test_properties_id_when_no_feature_id(self):
        doc = {"features": [{"properties": {"@id": "https://api.weather.gov/zones/county/ILC043"}}]}
        self.assertEqual(places.zone_keys(doc), {"county/ILC043"})

    def test_not_an_answer(self):
        for bad in (None, [], {}, {"features": None}, "x"):
            self.assertIsNone(places.zone_keys(bad))
        self.assertEqual(places.zone_keys({"features": []}), set())


class TestGeometry(unittest.TestCase):
    SQUARE_WITH_HOLE = {"type": "Polygon", "coordinates": [
        [[0, 0], [10, 0], [10, 10], [0, 10], [0, 0]],
        [[4, 4], [6, 4], [6, 6], [4, 6], [4, 4]]]}

    def test_inside_outside_hole(self):
        g = self.SQUARE_WITH_HOLE
        self.assertTrue(places.contains(g, 2, 2))      # lat 2, lon 2
        self.assertFalse(places.contains(g, 5, 5))     # in the hole
        self.assertFalse(places.contains(g, 11, 5))
        self.assertFalse(places.contains(g, 5, -1))

    def test_lat_lon_order(self):
        tall = {"type": "Polygon", "coordinates": [[[0, 0], [1, 0], [1, 50], [0, 50], [0, 0]]]}  # lon 0-1, lat 0-50
        self.assertTrue(places.contains(tall, 40, 0.5))
        self.assertFalse(places.contains(tall, 0.5, 40))

    def test_multipolygon(self):
        g = {"type": "MultiPolygon", "coordinates": [
            [[[0, 0], [1, 0], [1, 1], [0, 1], [0, 0]]], [[[5, 5], [6, 5], [6, 6], [5, 6], [5, 5]]]]}
        self.assertTrue(places.contains(g, 5.5, 5.5))
        self.assertTrue(places.contains(g, 0.5, 0.5))
        self.assertFalse(places.contains(g, 3, 3))

    def test_not_a_polygon(self):
        for g in (None, {}, {"type": "Point", "coordinates": [0, 0]}, {"type": "Polygon", "coordinates": []}):
            self.assertFalse(places.contains(g, 0, 0))

    def test_distance(self):
        self.assertAlmostEqual(places.distance_m(0, 0, 0, 1), 111195, delta=5)
        self.assertAlmostEqual(places.distance_m(41.88, -87.63, 41.88, -87.63), 0)


G = {"id": "LOT/76,73", "forecast": "f", "hourly": "h"}


class TestCache(unittest.TestCase):
    def keys(self, c, lat, lon, now, reuse=1000, keep=86400):
        p = places.cached_point(c, lat, lon, now, reuse, keep)
        return None if p is None else p["keys"]

    def test_reuse_within_distance_only(self):
        c = places.remember([], 41.0, -87.0, {"county/A"}, G, 1000.0, 1000, 64)
        self.assertEqual(self.keys(c, 41.0, -87.0, 1001.0), {"county/A"})
        self.assertEqual(self.keys(c, 41.008, -87.0, 1001.0), {"county/A"})  # ~890 m
        self.assertIsNone(self.keys(c, 41.01, -87.0, 1001.0))               # ~1,110 m

    def test_grid_comes_back(self):
        c = places.remember([], 41.0, -87.0, {"county/A"}, G, 1.0, 1000, 64)
        self.assertEqual(places.cached_point(c, 41.0, -87.0, 2.0, 1000, 86400), {"keys": {"county/A"}, "grid": G})
        c = places.remember([], 26.0, -90.0, {"forecast/GMZ046"}, None, 1.0, 1000, 64)
        self.assertEqual(places.cached_point(c, 26.0, -90.0, 2.0, 1000, 86400), {"keys": {"forecast/GMZ046"}, "grid": None})

    def test_zones_era_entry_is_asked_again(self):
        # stored by /zones?point= (dd39604, 9e483c7): no "grid" field, so the place learns its grid
        c = [{"lat": 41.0, "lon": -87.0, "keys": ["county/A"], "at": 5.0}]
        self.assertIsNone(places.cached_point(c, 41.0, -87.0, 6.0, 1000, 86400))

    def test_nearest_wins(self):
        c = places.remember([], 41.0, -87.0, {"near"}, None, 1.0, 1000, 64)
        c = places.remember(c, 41.006, -87.0, {"far"}, None, 2.0, 500, 64)   # 667 m away: kept beside it
        self.assertEqual(len(c), 2)
        self.assertEqual(self.keys(c, 41.001, -87.0, 3.0), {"near"})

    def test_stale_is_not_reused(self):
        c = places.remember([], 41.0, -87.0, {"county/A"}, None, 0.0, 1000, 64)
        self.assertIsNone(self.keys(c, 41.0, -87.0, 86400.0))

    def test_same_spot_replaced(self):
        c = places.remember([], 41.0, -87.0, {"old"}, None, 1.0, 1000, 64)
        c = places.remember(c, 41.0001, -87.0, {"new"}, G, 2.0, 1000, 64)
        self.assertEqual(len(c), 1)
        self.assertEqual(self.keys(c, 41.0, -87.0, 3.0), {"new"})

    def test_capped_newest_kept(self):
        c = []
        for i in range(10):
            c = places.remember(c, 40.0 + i, -87.0, {f"k{i}"}, None, float(i), 1000, 4)
        self.assertEqual([e["keys"] for e in c], [["k6"], ["k7"], ["k8"], ["k9"]])

    def test_outside_nws_area_is_an_empty_answer(self):
        c = places.remember([], 60.0, 10.0, set(), None, 1.0, 1000, 64)
        self.assertEqual(self.keys(c, 60.0, 10.0, 2.0), set())

    def test_bad_entries_ignored(self):
        c = [{"lat": "x", "grid": None}, {}, {"lat": 41.0, "lon": -87.0, "keys": ["a"], "grid": None, "at": 5.0}]
        self.assertEqual(self.keys(c, 41.0, -87.0, 6.0), {"a"})


class TestPoints(unittest.TestCase):
    """places.point_info on NWS /points answers of 2026-11-17 (ltw349_probe.py)."""

    def read(self, name):
        return json.loads((FIXTURES / f"nws_points_{name}_20261117.json").read_text(encoding="utf-8"))

    def test_land_keys_equal_zones_answer(self):
        info = places.point_info(self.read("chicago_loop"))
        zones = places.zone_keys(json.loads((FIXTURES / "nws_zones_point_chicago_loop_20261117.json").read_text(encoding="utf-8")))
        self.assertEqual(info["keys"], zones)
        self.assertEqual(info["keys"], {"county/ILC031", "fire/ILZ014", "forecast/ILZ104"})

    def test_land_grid(self):
        g = places.point_info(self.read("chicago_loop"))["grid"]
        self.assertEqual(g["id"], "LOT/76,73")
        self.assertTrue(g["forecast"].endswith("/gridpoints/LOT/76,73/forecast"))
        self.assertTrue(g["hourly"].endswith("/gridpoints/LOT/76,73/forecast/hourly"))

    def test_lake_keys_and_no_grid(self):
        # a marine grid is named (MKX/107,13) but NWS answers 404 for its forecast: no county, so no grid
        info = places.point_info(self.read("lake_michigan"))
        self.assertEqual(info["keys"], {"forecast/LMZ779"})
        zones = places.zone_keys(json.loads((FIXTURES / "nws_zones_point_lake_michigan_20261117.json").read_text(encoding="utf-8")))
        self.assertEqual(info["keys"], zones)
        self.assertIsNone(info["grid"])

    def test_gulf_no_grid(self):
        info = places.point_info(self.read("gulf_offshore"))
        self.assertEqual(info["keys"], {"forecast/GMZ046"})
        self.assertIsNone(info["grid"])

    def test_404_body_is_not_an_answer(self):
        self.assertIsNone(places.point_info(self.read("toronto_404")))
        for bad in (None, [], {}, {"properties": None}):
            self.assertIsNone(places.point_info(bad))


def rec(event, severity, priority=100, rid=None, source="NWS"):
    return {"source": source, "id": rid or event, "event": event, "severity": severity, "headline": None,
            "onset": None, "ends": None, "priority": priority, "zones": ["z"], "polygon": None}


class TestSummary(unittest.TestCase):
    def test_worst_first(self):
        s = places.summary([rec("Small Craft Advisory", "Minor", 120), rec("Tornado Warning", "Extreme", 2),
                            rec("Flood Watch", "Severe", 60), rec("Gale Warning", "Moderate", 80)], "all")
        self.assertEqual([a["event"] for a in s["alerts"]],
                         ["Tornado Warning", "Flood Watch", "Gale Warning", "Small Craft Advisory"])
        self.assertTrue(s["on"])
        self.assertEqual(s["highest"], "Tornado Warning")
        self.assertEqual(s["counted"], 4)

    def test_same_severity_by_nws_priority(self):
        s = places.summary([rec("B", "Severe", 50), rec("A", "Severe", 10)], "all")
        self.assertEqual([a["event"] for a in s["alerts"]], ["A", "B"])

    def test_thresholds(self):
        found = [rec("Statement", "Unknown"), rec("Advisory", "Minor"), rec("Watch", "Moderate")]
        self.assertTrue(places.summary(found, "all")["on"])
        s = places.summary(found, "moderate")
        self.assertTrue(s["on"])
        self.assertEqual(s["highest"], "Watch")
        self.assertEqual(s["counted"], 1)
        s = places.summary(found, "severe")
        self.assertFalse(s["on"])
        self.assertIsNone(s["highest"])
        self.assertEqual(len(s["alerts"]), 3)  # listed either way
        self.assertFalse(places.summary([rec("Warning", "Severe")], "extreme")["on"])
        self.assertTrue(places.summary([rec("Warning", "Extreme")], "extreme")["on"])

    def test_all_counts_unknown_severity(self):
        # NWS gives some statements severity "Unknown"; "Any alert" means them too (Lee 2026-11-16)
        s = places.summary([rec("Special Weather Statement", "Unknown")], "all")
        self.assertTrue(s["on"])
        self.assertEqual(s["highest"], "Special Weather Statement")

    def test_unknown_threshold_counts_everything(self):
        self.assertTrue(places.summary([rec("Statement", "Unknown")], "nonsense")["on"])

    def test_nothing(self):
        s = places.summary([], "all")
        self.assertEqual(s, {"on": False, "alerts": [], "highest": None, "counted": 0})

    def test_one_alert_listed_once(self):
        s = places.summary([rec("Gale Warning", "Moderate", rid="x"), rec("Gale Warning", "Moderate", rid="x")], "all")
        self.assertEqual(len(s["alerts"]), 1)

    def test_listed_fields(self):
        s = places.summary([rec("Gale Warning", "Moderate")], "all")
        self.assertEqual(set(s["alerts"][0]), {"event", "severity", "headline", "onset", "ends", "source", "id"})

    def test_real_point(self):
        s = places.summary(at(POINTS["point_03"]), "all")
        self.assertTrue(s["on"])
        self.assertEqual(len(s["alerts"]), 4)
        self.assertTrue(all(a["source"] == "NWS" and a["id"].startswith("https://api.weather.gov/alerts/")
                            for a in s["alerts"]))


class TestNwsRecord(unittest.TestCase):
    def test_every_wanted_alert_has_a_record(self):
        self.assertEqual(len(RECORDS), LIVE["count"])

    def test_polygon_kept_at_full_precision(self):
        f = next(f for f in FIX["features"] if f.get("geometry"))
        r = next(r for r in RECORDS if r["id"] == f["properties"]["@id"])
        self.assertEqual(r["polygon"], f["geometry"])

    def test_ends_falls_back_to_expires(self):
        r = places.nws_record({"event": "X", "expires": "2026-11-17T12:00:00Z", "ends": None}, None, 5)
        self.assertEqual(r["ends"], "2026-11-17T12:00:00Z")
        self.assertEqual(r["severity"], "Unknown")

    def test_records_not_in_the_map_sensors_attributes(self):
        sensor_src = (COMP / "sensor.py").read_text(encoding="utf-8")
        self.assertNotIn('"records"', sensor_src)


class TestMet(unittest.TestCase):
    CAP = met.parse_cap((FIXTURES / "met_cap_gale_yellow_E3_20261028.xml").read_bytes())

    def test_severity_parsed(self):
        self.assertEqual(self.CAP["severity"], "Moderate")

    def test_drawn_caps_handed_over(self):
        out = met.publish_warnings([self.CAP], datetime(2026, 10, 28, 22, 30, tzinfo=timezone.utc))
        self.assertEqual(out["caps"], [self.CAP])
        gone = met.publish_warnings([self.CAP], datetime(2026, 10, 29, 1, 0, tzinfo=timezone.utc))
        self.assertEqual(gone["caps"], [])

    def test_record_and_inside(self):
        r = places.met_record(self.CAP, "https://api.met.no/weatherapi/metalerts/2.0/current")
        self.assertEqual(r["source"], "MET Norway")
        self.assertEqual(r["severity"], "Moderate")
        self.assertTrue(r["event"].endswith(", yellow"), r["event"])
        self.assertTrue(r["id"].endswith("?cap=" + self.CAP["id"]))
        ring = self.CAP["rings"][0]
        lat = sum(p[1] for p in ring[:-1]) / (len(ring) - 1)
        lon = sum(p[0] for p in ring[:-1]) / (len(ring) - 1)
        self.assertTrue(places.contains(r["polygon"], lat, lon), "centroid of a convex-ish sea area")
        self.assertEqual(places.alerts_at([r], None, lat, lon), [r])
        self.assertEqual(places.alerts_at([r], None, 41.88, -87.63), [])

    def test_no_rings_no_record(self):
        self.assertIsNone(places.met_record({"id": "x", "rings": []}, "u"))


if __name__ == "__main__":
    unittest.main()
