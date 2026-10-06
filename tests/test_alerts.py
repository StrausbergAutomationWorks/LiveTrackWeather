"""alerts.live_list against a real night: NWS /alerts/active, 2026-10-05 23:58Z,
390 alerts, with the colour table and shape file this release ships."""

import gzip
import json
import unittest

from _load import COMP, FIXTURES, load

alerts = load("alerts")

DOC = json.loads((FIXTURES / "alerts_active_20261005T2358Z.json").read_text(encoding="utf-8"))
COLOURS = json.loads((COMP / "data" / "nws_hazard_colours.json").read_text(encoding="utf-8"))["events"]
SHAPES = json.loads(gzip.decompress((COMP / "www" / "nws_zones.json.gz").read_bytes()))["shapes"]
LIVE = alerts.live_list(DOC, COLOURS)


def feats():
    return DOC["features"]


class TestFilter(unittest.TestCase):
    def test_count_is_every_actual_alert(self):
        actual = [f for f in feats() if f["properties"]["status"] == "Actual"]
        self.assertEqual(len(actual), 389)
        self.assertEqual(LIVE["count"], 389)

    def test_test_message_is_never_drawn(self):
        self.assertNotIn("Test Message", LIVE["styles"])
        self.assertNotIn("Test Message", LIVE["zones"].values())

    def test_test_message_dropped_even_if_marked_actual(self):
        doc = {"features": [{"geometry": None, "properties": {
            "status": "Actual", "event": "Test Message",
            "affectedZones": ["https://api.weather.gov/zones/forecast/ILZ014"]}}]}
        self.assertEqual(alerts.live_list(doc, COLOURS)["count"], 0)

    def test_exercise_and_system_dropped(self):
        for status in ("Exercise", "System", "Test", "Draft", None):
            doc = {"features": [{"geometry": None, "properties": {
                "status": status, "event": "Gale Warning",
                "affectedZones": ["https://api.weather.gov/zones/forecast/LMZ740"]}}]}
            self.assertEqual(alerts.live_list(doc, COLOURS)["zones"], {}, status)


class TestZones(unittest.TestCase):
    def test_zone_key(self):
        self.assertEqual(alerts.zone_key("https://api.weather.gov/zones/forecast/ILZ014"), "forecast/ILZ014")
        self.assertEqual(alerts.zone_key("https://api.weather.gov/zones/county/ILC031"), "county/ILC031")
        self.assertEqual(alerts.zone_key("https://api.weather.gov/zones/fire/WAZ658"), "fire/WAZ658")
        self.assertIsNone(alerts.zone_key("https://example.org/nothing"))

    def test_every_named_zone_is_in_the_shipped_shapes(self):
        missing = sorted(k for k in LIVE["zones"] if k not in SHAPES)
        self.assertEqual(missing, [])

    def test_every_zone_takes_its_highest_priority_event(self):
        named = {}
        for f in feats():
            p = f["properties"]
            if p["status"] != "Actual" or f["geometry"]:
                continue
            for u in p["affectedZones"]:
                named.setdefault(alerts.zone_key(u), set()).add(p["event"])
        self.assertEqual(set(LIVE["zones"]), set(named))
        for key, events in named.items():
            want = min(events, key=lambda e: COLOURS[e]["priority"])
            self.assertEqual(LIVE["zones"][key], want, key)
        # The night had real overlaps; make sure the rule was exercised.
        self.assertTrue(any(len(e) > 1 for e in named.values()))

    def test_gale_warning_beats_small_craft_advisory(self):
        doc = {"features": [
            {"geometry": None, "properties": {"status": "Actual", "event": e,
             "affectedZones": ["https://api.weather.gov/zones/forecast/LMZ740"]}}
            for e in ("Small Craft Advisory", "Gale Warning", "Small Craft Advisory")]}
        self.assertEqual(alerts.live_list(doc, COLOURS)["zones"], {"forecast/LMZ740": "Gale Warning"})


class TestPolygons(unittest.TestCase):
    def test_polygon_alerts_draw_their_polygon_only(self):
        poly = [f for f in feats() if f["geometry"] and f["properties"]["status"] == "Actual"]
        self.assertEqual(len(poly), 30)
        self.assertEqual(len(LIVE["polygons"]), 30)
        # A zone named only by polygon alerts is not filled.
        only_poly = set()
        for f in poly:
            only_poly |= {alerts.zone_key(u) for u in f["properties"]["affectedZones"]}
        for f in feats():
            if not f["geometry"] and f["properties"]["status"] == "Actual":
                only_poly -= {alerts.zone_key(u) for u in f["properties"]["affectedZones"]}
        self.assertTrue(only_poly)
        self.assertFalse(only_poly & set(LIVE["zones"]))

    def test_coordinates_rounded_to_three_decimals(self):
        for p in LIVE["polygons"]:
            for ring in p["coordinates"]:
                for x, y in ring:
                    self.assertEqual(x, round(x, 3))
                    self.assertEqual(y, round(y, 3))

    def test_rounding_applies_to_finer_input(self):
        # NWS polygons arrive with 2-3 decimals, so the real night cannot
        # show the rounding; this one can.
        doc = {"features": [{"geometry": {"type": "Polygon", "coordinates": [[
            [-87.123456, 41.987654], [-87.0, 42.0], [-87.2, 42.1], [-87.123456, 41.987654]]]},
            "properties": {"status": "Actual", "event": "Tornado Warning", "affectedZones": []}}]}
        ring = alerts.live_list(doc, COLOURS)["polygons"][0]["coordinates"][0]
        self.assertEqual(ring[0], [-87.123, 41.988])

    def test_highest_priority_last(self):
        pr = [LIVE["styles"][p["event"]]["priority"] for p in LIVE["polygons"]]
        self.assertEqual(pr, sorted(pr, reverse=True))


class TestStyles(unittest.TestCase):
    def test_styles_are_nws_values_for_present_events_only(self):
        drawn = set(LIVE["zones"].values()) | {p["event"] for p in LIVE["polygons"]}
        self.assertEqual(set(LIVE["styles"]), drawn)
        for e, s in LIVE["styles"].items():
            self.assertEqual(s["color"], COLOURS[e]["color"])
            self.assertEqual(s["priority"], COLOURS[e]["priority"])
            self.assertEqual(s["pattern"], alerts.DEFAULT_PATTERN)
        self.assertEqual(LIVE["unknown_events"], [])

    def test_unknown_event_is_grey_and_last(self):
        doc = {"features": [{"geometry": None, "properties": {
            "status": "Actual", "event": "Brand New Warning",
            "affectedZones": ["https://api.weather.gov/zones/forecast/ILZ014"]}},
            {"geometry": None, "properties": {
            "status": "Actual", "event": "Frost Advisory",
            "affectedZones": ["https://api.weather.gov/zones/forecast/ILZ014"]}}]}
        out = alerts.live_list(doc, COLOURS)
        self.assertEqual(out["unknown_events"], ["Brand New Warning"])
        # Outranked by a known event: not drawn, so no style.
        self.assertEqual(out["zones"]["forecast/ILZ014"], "Frost Advisory")
        self.assertNotIn("Brand New Warning", out["styles"])
        # Alone: drawn grey.
        alone = alerts.live_list({"features": doc["features"][:1]}, COLOURS)
        self.assertEqual(alone["zones"]["forecast/ILZ014"], "Brand New Warning")
        self.assertEqual(alone["styles"]["Brand New Warning"]["color"], "#808080")


class TestSize(unittest.TestCase):
    def test_live_list_stays_small(self):
        # 390 alerts that night; the list must not grow with forecaster prose.
        size = len(json.dumps(LIVE, separators=(",", ":")))
        self.assertLess(size, 64 * 1024, size)


if __name__ == "__main__":
    unittest.main()
