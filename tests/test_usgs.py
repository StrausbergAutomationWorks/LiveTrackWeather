"""usgs: earthquakes for the map and the places (Weather item 352, contract D20).

Fixtures are USGS's own answers, saved by bin\\usgs_probe.py on 2026-11-17 at 23:30Z: the all_day feed (239 events),
the 2026-10-22 M7.0 near Nagqu's detail GeoJSON and its ShakeMap cont_mmi.json.
"""

import copy
import json
import math
import unittest
from datetime import datetime, timezone

from _load import FIXTURES, load

us = load("usgs")
pl = load("places")

FEED = json.loads((FIXTURES / "usgs_all_day_20261117T2330Z.json").read_text(encoding="utf-8"))
DETAIL = json.loads((FIXTURES / "usgs_detail_us6000u43g_20261117.json").read_text(encoding="utf-8"))
CONT = json.loads((FIXTURES / "usgs_cont_mmi_us6000u43g_20261117.json").read_text(encoding="utf-8"))
EVENTS = us.parse_feed(FEED)


def ev(**kw):
    """A synthetic event as parse_feed makes it."""
    base = {"id": "xx1", "key": "xx1", "mag": 4.0, "mag_type": "ml", "place": "somewhere", "title": "M 4.0 - x",
            "time": datetime(2026, 11, 17, 12, 0, tzinfo=timezone.utc),
            "updated": datetime(2026, 11, 17, 12, 5, tzinfo=timezone.utc), "lat": 41.0, "lon": -88.0, "depth": 10.0,
            "felt": None, "cdi": None, "mmi": None, "alert": None, "tsunami": False, "status": "reviewed",
            "type": "earthquake", "url": "https://earthquake.usgs.gov/earthquakes/eventpage/xx1",
            "detail": "https://earthquake.usgs.gov/earthquakes/feed/v1.0/detail/xx1.geojson", "types": {"origin"}}
    base.update(kw)
    return base


def north_of(lat, lon, km):
    """A point `km` due north (great circle, the same radius as places.distance_m)."""
    return lat + math.degrees(km * 1000 / 6371008.8), lon


class TestFeed(unittest.TestCase):
    def test_every_event_parsed(self):
        self.assertEqual(len(EVENTS), 239)
        self.assertEqual(len(EVENTS), FEED["metadata"]["count"])

    def test_not_a_feed(self):
        self.assertIsNone(us.parse_feed(None))
        self.assertIsNone(us.parse_feed({"features": "x"}))
        self.assertEqual(us.parse_feed({"features": [{"properties": {}, "geometry": None, "id": "a"}]}), [])

    def test_fields(self):
        e = EVENTS[0]
        self.assertEqual(e["id"], "aka2026wuvyao")
        self.assertEqual((e["lon"], e["lat"], e["depth"]), (-152.137, 60.734, 21.8))
        self.assertEqual(e["time"].tzinfo, timezone.utc)
        self.assertEqual(e["types"], {"origin", "phase-data"})
        self.assertFalse(e["tsunami"])

    def test_bad_rows_skipped(self):
        doc = copy.deepcopy(FEED)
        doc["features"][0]["properties"]["mag"] = None
        doc["features"][1]["geometry"]["coordinates"] = [200, 10]
        doc["features"][2]["properties"]["time"] = None
        doc["features"][3]["id"] = ""
        self.assertEqual(len(us.parse_feed(doc)), 235)

    def test_key_is_safe(self):
        self.assertEqual(us.parse_feed({"features": [{"id": "US-6000.AB", "properties": {"mag": 1, "time": 0},
                                                      "geometry": {"coordinates": [0, 0]}}]})[0]["key"], "us_6000_ab")

    def test_http_links_dropped(self):
        doc = {"features": [{"id": "a", "properties": {"mag": 1, "time": 0, "url": "http://x", "detail": "ftp://y"},
                             "geometry": {"coordinates": [0, 0]}}]}
        e = us.parse_feed(doc)[0]
        self.assertIsNone(e["url"])
        self.assertIsNone(e["detail"])


class TestMarkers(unittest.TestCase):
    def test_count_of_the_day(self):
        markers = [e for e in EVENTS if us.is_marker(e)]
        self.assertEqual(len(markers), 17)

    def test_rule(self):
        self.assertTrue(us.is_marker(ev(mag=4.5)))
        self.assertFalse(us.is_marker(ev(mag=4.49)))
        self.assertTrue(us.is_marker(ev(mag=1.0, felt=1)))
        self.assertFalse(us.is_marker(ev(mag=1.0, felt=0)))
        self.assertFalse(us.is_marker(ev(mag=5.0, type="quarry blast")), "a blast is never a marker")

    def test_colour_bands(self):
        self.assertEqual(us.marker_colour(ev(mag=7.0)), "#7F0000")
        self.assertEqual(us.marker_colour(ev(mag=6.99)), "#C2185B")
        self.assertEqual(us.marker_colour(ev(mag=6.0)), "#C2185B")
        self.assertEqual(us.marker_colour(ev(mag=5.99)), "#6A1B9A")
        self.assertEqual(us.marker_colour(ev(mag=4.5)), "#6A1B9A")
        self.assertEqual(us.marker_colour(ev(mag=3.0, felt=4)), "#9575CD")

    def test_record(self):
        r = us.quake_record(ev(mag=4.94, felt=31, cdi=5.5, mmi=6.0, alert="green", tsunami=True))
        a = r["attrs"]
        self.assertEqual((r["key"], r["lat"], r["lon"]), ("xx1", 41.0, -88.0))
        self.assertEqual(a["marker_label"], "4.9")
        self.assertEqual(a["map_layer"], "fixed")
        self.assertEqual(a["marker_links"], [{"label": "USGS event page",
                                              "url": "https://earthquake.usgs.gov/earthquakes/eventpage/xx1"}])
        self.assertIn("Tsunami flag set", a["marker_info"]["text"])
        self.assertIn("not a warning", a["marker_info"]["text"])
        self.assertIn("VI, strong", a["marker_info"]["text"])
        self.assertIn("Felt reports: 31", a["marker_info"]["text"])
        self.assertEqual(a["attribution"], us.QUAKE_ATTRIBUTION)
        self.assertTrue(a["tsunami_flag"])
        self.assertEqual(a["time"], "2026-11-17T12:00:00+00:00")
        self.assertEqual(a["last_seen"], "2026-11-17T12:05:00+00:00")

    def test_record_without_link_or_tsunami(self):
        a = us.quake_record(ev(url=None, status="automatic"))["attrs"]
        self.assertNotIn("marker_links", a)
        self.assertNotIn("Tsunami", a["marker_info"]["text"])
        self.assertIn("Automatic, may be revised", a["marker_info"]["text"])

    def test_every_marker_of_the_day_builds(self):
        for e in EVENTS:
            if us.is_marker(e):
                r = us.quake_record(e)
                self.assertLessEqual(len(r["attrs"]["marker_info"]["title"]), 200)
                self.assertTrue(r["attrs"]["marker_color"].startswith("#"))


class TestPoints(unittest.TestCase):
    def test_markers_are_not_points(self):
        pts = us.quake_points(EVENTS, None)
        self.assertEqual(len(pts), 239 - 17)

    def test_min_magnitude(self):
        n = sum(1 for e in EVENTS if not us.is_marker(e) and e["mag"] >= 2.5)
        self.assertEqual(len(us.quake_points(EVENTS, 2.5)), n)
        self.assertLess(n, 239 - 17)

    def test_styles(self):
        self.assertEqual(us.point_style(ev(mag=1.99)), "m_lt2")
        self.assertEqual(us.point_style(ev(mag=2.0)), "m2")
        self.assertEqual(us.point_style(ev(mag=2.99)), "m2")
        self.assertEqual(us.point_style(ev(mag=3.0)), "m3")
        self.assertEqual(us.point_style(ev(mag=4.0)), "m4")
        self.assertEqual(us.point_style(ev(mag=-0.3)), "m_lt2")
        self.assertEqual(us.point_style(ev(mag=3.0, type="explosion")), "other")
        for s in {us.point_style(e) for e in EVENTS}:
            self.assertIn(s, us.QUAKE_STYLES)

    def test_blasts_are_points(self):
        pts = us.quake_points(EVENTS, None)
        self.assertTrue(any(p[2] == "other" for p in pts), "the day had quarry blasts and explosions")

    def test_point_shape(self):
        p = us.quake_points([ev(mag=2.123, lon=-88.123456, lat=41.987654, depth=None)], None)[0]
        self.assertEqual(p, [-88.1235, 41.9877, "m2", 2.12, "somewhere", "2026-11-17 12:00", None, "reviewed"])
        self.assertEqual(len(p), 3 + len(us.QUAKE_COLUMNS))

    def test_styles_valid_for_d19(self):
        for s in us.QUAKE_STYLES.values():
            self.assertRegex(s["color"], r"^#[0-9A-F]{6}$")
            self.assertRegex(s["outline"], r"^#[0-9A-F]{6}$")
            self.assertTrue(2 <= s["radius"] <= 10)

    def test_option(self):
        self.assertIsNone(us.min_magnitude(None))
        self.assertIsNone(us.min_magnitude(True))
        self.assertIsNone(us.min_magnitude("3"))
        self.assertIsNone(us.min_magnitude(-0.1))
        self.assertIsNone(us.min_magnitude(9.1))
        self.assertEqual(us.min_magnitude(0), 0.0)
        self.assertEqual(us.min_magnitude(2.5), 2.5)


class TestRoman(unittest.TestCase):
    def test_words(self):
        self.assertEqual(us.roman(6.0), "VI, strong")
        self.assertEqual(us.roman(6.5), "VI-VII, strong to very strong")
        self.assertEqual(us.roman(3.5), "III-IV, weak to light")
        self.assertEqual(us.roman(2.5), "II-III, weak")
        self.assertEqual(us.roman(10.0), "X, extreme")
        self.assertEqual(us.roman(5.47), "V-VI, moderate to strong")
        self.assertEqual(us.roman(5.1), "V, moderate")


class TestShakeMap(unittest.TestCase):
    def test_none_of_the_day(self):
        self.assertEqual(us.shakemap_candidates(EVENTS), [], "no quake of 2026-11-17 reached the rule")

    def test_rule(self):
        sm = {"origin", "shakemap"}
        self.assertEqual(len(us.shakemap_candidates([ev(mag=4.6, mmi=6.0, types=sm)])), 1)
        self.assertEqual(len(us.shakemap_candidates([ev(mag=4.6, mmi=5.99, types=sm)])), 0)
        self.assertEqual(len(us.shakemap_candidates([ev(mag=6.0, mmi=None, types=sm)])), 1)
        self.assertEqual(len(us.shakemap_candidates([ev(mag=6.5, types={"origin"})])), 0, "no ShakeMap")
        self.assertEqual(len(us.shakemap_candidates([ev(mag=3.0, mmi=7.0, types=sm)])), 0, "not a marker")
        self.assertEqual(len(us.shakemap_candidates([ev(mag=6.5, types=sm, detail=None)])), 0)

    def test_five_largest(self):
        sm = {"shakemap"}
        many = [ev(id=f"e{i}", mag=6.0 + i / 10, types=sm) for i in range(7)]
        got = us.shakemap_candidates(many)
        self.assertEqual([e["id"] for e in got], ["e6", "e5", "e4", "e3", "e2"])

    def test_contours_url(self):
        self.assertEqual(us.contours_url(DETAIL), DETAIL["properties"]["products"]["shakemap"][0]["contents"][
            "download/cont_mmi.json"]["url"])
        self.assertIsNone(us.contours_url({}))
        bad = copy.deepcopy(DETAIL)
        bad["properties"]["products"]["shakemap"][0]["contents"]["download/cont_mmi.json"]["url"] = "http://x"
        self.assertIsNone(us.contours_url(bad))

    def test_shapes(self):
        q = ev(mag=7.0, title="M 7.0 - near Nagqu")
        items, styles = us.shakemap_shapes(CONT, q)
        self.assertEqual(len(items), 10)
        self.assertEqual({i["type"] for i in items}, {"MultiLineString"})
        self.assertEqual(styles["Intensity 8.0"], {"color": "#FF9100", "priority": 5, "casing": "#424242"})
        self.assertEqual(styles["Intensity 3.5"]["priority"], 14)
        self.assertEqual(styles["Intensity 3.5"]["color"], "#90F2FF")
        it = next(i for i in items if i["event"] == "Intensity 6.0")
        self.assertEqual(it["info"]["title"], "Shaking: intensity VI, strong")
        self.assertIn("M 7.0 - near Nagqu", it["info"]["text"])
        self.assertEqual(it["quake"], "xx1")
        for i in items:
            self.assertIn(i["event"], styles)
            for line in i["coordinates"]:
                self.assertGreaterEqual(len(line), 2)
                for x, y in line:
                    self.assertEqual(round(x, 3), x)
                    self.assertEqual(round(y, 3), y)

    def test_priorities_order(self):
        _, styles = us.shakemap_shapes(CONT, ev())
        order = sorted(styles, key=lambda k: styles[k]["priority"])
        self.assertEqual(order[0], "Intensity 8.0")
        self.assertEqual(order[-1], "Intensity 3.5")

    def test_fallback_colour_and_bad_files(self):
        doc = {"features": [{"properties": {"value": 6.0, "units": "mmi", "color": "yellow"},
                             "geometry": {"type": "LineString", "coordinates": [[1, 2], [1, 2], [3, 4]]}},
                            {"properties": {"value": 9.0}, "geometry": {"type": "LineString",
                                                                        "coordinates": [[1, 2], [3, 4]]}},
                            {"properties": {"value": 5.0, "units": "pga"}, "geometry": {"type": "LineString",
                                                                                        "coordinates": [[1, 2], [3, 4]]}},
                            {"properties": {"value": 4.0}, "geometry": {"type": "LineString", "coordinates": [[1, 2]]}},
                            {"properties": {"value": 4.0}, "geometry": {"type": "Polygon", "coordinates": []}}]}
        items, styles = us.shakemap_shapes(doc, ev())
        self.assertEqual([i["event"] for i in items], ["Intensity 6.0", "Intensity 9.0"])
        self.assertEqual(items[0]["coordinates"], [[[1, 2], [3, 4]]], "a repeated point is dropped")
        self.assertEqual(styles["Intensity 6.0"]["color"], "#FFFF00")
        self.assertEqual(styles["Intensity 9.0"]["color"], "#808080")
        self.assertEqual(us.shakemap_shapes(None, ev()), ([], {}))


class TestAlerts(unittest.TestCase):
    HOME = (41.88, -87.63)

    def at(self, mag, km, **kw):
        lat, lon = north_of(*self.HOME, km)
        return us.alert_records([ev(mag=mag, lat=lat, lon=lon, **kw)], *self.HOME)

    def test_thresholds(self):
        for mag, reach in ((4.0, 50), (5.0, 150), (6.0, 300), (7.0, 600)):
            self.assertEqual(len(self.at(mag, reach - 0.5)), 1, (mag, reach))
            self.assertEqual(len(self.at(mag, reach + 0.5)), 0, (mag, reach))
        self.assertEqual(len(self.at(4.99, 51)), 0)
        self.assertEqual(len(self.at(5.99, 151)), 0)
        self.assertEqual(len(self.at(6.99, 301)), 0)
        self.assertEqual(len(self.at(3.99, 1)), 0)
        self.assertEqual(len(self.at(8.0, 599)), 1)

    def test_record(self):
        r = self.at(5.2, 120)[0]
        self.assertTrue(r["always"])
        self.assertEqual(r["source"], "USGS")
        self.assertEqual(r["event"], "Earthquake M5.2, 120 km N")
        self.assertEqual(r["km"], 120.0)
        self.assertEqual(r["severity"], "Moderate")
        self.assertTrue(pl.counts(r, "extreme"), "counts whatever the CAP-severity setting")
        self.assertEqual(self.at(6.0, 10)[0]["severity"], "Severe")
        self.assertEqual(self.at(7.0, 10)[0]["severity"], "Extreme")

    def test_blasts_never(self):
        self.assertEqual(self.at(4.5, 5, type="quarry blast"), [])

    def test_nearest_first(self):
        far, near = north_of(*self.HOME, 40), north_of(*self.HOME, 10)
        got = us.alert_records([ev(id="a", lat=far[0], lon=far[1]), ev(id="b", lat=near[0], lon=near[1])], *self.HOME)
        self.assertEqual([r["km"] for r in got], [10.0, 40.0])

    def test_summary_lists_it(self):
        s = pl.summary(self.at(4.5, 20), "severe")
        self.assertTrue(s["on"])
        self.assertEqual(s["alerts"][0]["km"], 20.0)


if __name__ == "__main__":
    unittest.main()


# ------------------------------------------------------------------------------------------- volcanoes (step 2)
import gzip  # noqa: E402

from _load import COMP  # noqa: E402

ELEV = json.loads((FIXTURES / "hans_getElevatedVolcanoes_20261117.json").read_text(encoding="utf-8"))
CAPS = json.loads((FIXTURES / "hans_getCapElevated_20261117.json").read_text(encoding="utf-8"))
USV = json.loads((FIXTURES / "hans_getUSVolcanoes_20261117.json").read_text(encoding="utf-8"))
ZONES = us.threat_zones(json.loads(gzip.decompress((COMP / "data" / "volcano_threat_zones.json.gz").read_bytes())))
US_INDEX = us.us_volcanoes(USV)


def vol(**kw):
    base = {"vnum": "311120", "name": "Great Sitkin", "lat": 52.0765, "lon": -176.1109, "level": "WATCH",
            "colour": "ORANGE", "since": "2026-11-13T21:04:48+00:00", "observatory": "Alaska Volcano Observatory",
            "notice_url": "https://volcanoes.usgs.gov/hans-public/notice/x", "synopsis": "Slow eruption",
            "cap_severity": "Minor", "url": "https://avo.alaska.edu/v", "threat": "High Threat", "elevation_m": 1740}
    base.update(kw)
    return base


class TestVolcanoes(unittest.TestCase):
    def test_us_list(self):
        self.assertEqual(len(US_INDEX), 170)
        self.assertEqual(US_INDEX["311800"]["name"], "Adagdak")
        self.assertIsNone(us.us_volcanoes({"x": 1}))

    def test_elevated_of_the_day(self):
        got = us.elevated(ELEV, CAPS, US_INDEX)
        self.assertEqual([(v["name"], v["level"], v["colour"]) for v in got],
                         [("Great Sitkin", "WATCH", "ORANGE"), ("Kilauea", "ADVISORY", "YELLOW"),
                          ("Ahyi Seamount", "ADVISORY", "YELLOW")])
        gs = got[0]
        self.assertEqual(gs["since"], "2026-11-13T21:04:48+00:00")
        self.assertEqual((gs["lat"], gs["lon"]), (US_INDEX["311120"]["lat"], US_INDEX["311120"]["lon"]))
        self.assertEqual(gs["cap_severity"], "Minor")
        self.assertTrue(gs["synopsis"].startswith("Slow eruption"))
        self.assertIsNone(got[1]["synopsis"], "Kilauea's CAP row says it is no longer elevated: not used")

    def test_no_position_no_marker(self):
        self.assertEqual(us.elevated(ELEV, CAPS, {}), [])
        self.assertIsNone(us.elevated(None, CAPS, US_INDEX))
        self.assertEqual(len(us.elevated(ELEV, None, US_INDEX)), 3, "the CAP list is optional")

    def test_colours(self):
        self.assertEqual(us.volcano_colour(vol()), "#FF9100")
        self.assertEqual(us.volcano_colour(vol(colour="RED")), "#D50000")
        self.assertEqual(us.volcano_colour(vol(colour="YELLOW", level="ADVISORY")), "#FFD600")
        self.assertEqual(us.volcano_colour(vol(colour=None, level="WARNING")), "#D50000")
        self.assertEqual(us.volcano_colour(vol(colour="UNASSIGNED", level="WATCH")), "#FF9100")

    def test_record(self):
        r = us.volcano_record(vol())
        a = r["attrs"]
        self.assertEqual((r["key"], r["name"]), ("311120", "Great Sitkin"))
        self.assertEqual(a["marker_label"], "Great Sitkin")
        self.assertEqual(a["map_layer"], "fixed")
        self.assertEqual(a["marker_info"]["title"], "Great Sitkin: WATCH / ORANGE")
        self.assertIn("Since 2026-11-13 21:04 UTC", a["marker_info"]["text"])
        self.assertEqual([x["label"] for x in a["marker_links"]], ["HANS notice", "Volcano page"])
        self.assertEqual(a["attribution"], us.VOLCANO_ATTRIBUTION)
        self.assertNotIn("marker_links", us.volcano_record(vol(notice_url=None, url=None))["attrs"])

    def test_zone_file(self):
        self.assertEqual(len(ZONES), 161)
        self.assertEqual(sum(len(z) for z in ZONES.values()), 174)
        self.assertEqual(ZONES["311120"][0]["zone"], "Near-volcano")
        self.assertEqual(us.threat_zones(None), {})

    def test_which_count(self):
        self.assertTrue(us.counts_for_places(vol()))
        self.assertTrue(us.counts_for_places(vol(level="ADVISORY", colour="ORANGE")), "colour alone")
        self.assertTrue(us.counts_for_places(vol(level="WARNING", colour="YELLOW")), "level alone")
        self.assertFalse(us.counts_for_places(vol(level="ADVISORY", colour="YELLOW")))

    def test_alert_inside_the_zone(self):
        v = vol()
        got = us.volcano_alert_records([v], ZONES, 52.0765, -176.1109)   # the summit
        self.assertEqual(len(got), 1)
        r = got[0]
        self.assertTrue(r["always"])
        self.assertEqual(r["event"], "Volcano: Great Sitkin, WATCH / ORANGE")
        self.assertEqual(r["severity"], "Minor")
        self.assertIn("near-volcano hazard zone", r["headline"])
        self.assertTrue(pl.counts(r, "extreme"))

    def test_no_alert_outside_or_below(self):
        self.assertEqual(us.volcano_alert_records([vol()], ZONES, 53.5, -176.1), [], "about 160 km north")
        self.assertEqual(us.volcano_alert_records([vol(level="ADVISORY", colour="YELLOW")], ZONES, 52.0765,
                                                  -176.1109), [])
        self.assertEqual(us.volcano_alert_records([vol(vnum="999999")], ZONES, 52.0765, -176.1109), [], "no zone")

    def test_edge_of_the_zone(self):
        """Inside near the zone's edge, outside just beyond it: the zone, not a radius, decides."""
        geom = ZONES["311120"][0]["geometry"]
        ring = geom["coordinates"][0][0] if geom["type"] == "MultiPolygon" else geom["coordinates"][0]
        lon_e = max(p[0] for p in ring)
        lat_e = next(p[1] for p in ring if p[0] == lon_e)
        self.assertEqual(us.volcano_alert_records([vol()], ZONES, lat_e, lon_e + 0.01), [])
        self.assertEqual(len(us.volcano_alert_records([vol()], ZONES, lat_e, lon_e - 0.02)), 1)


class TestVolcanoInputs(unittest.TestCase):
    """Pins for the two mutants that survived the first run (bin\\ltw352v_mutate.txt)."""

    def test_out_of_range_position_dropped(self):
        got = us.us_volcanoes([{"vnum": "1", "latitude": 95, "longitude": 10}, {"vnum": "2", "latitude": 10,
                                                                                  "longitude": 190},
                               {"vnum": "3", "latitude": 10, "longitude": 10}])
        self.assertEqual(list(got), ["3"])

    def test_bad_zone_entries_dropped(self):
        self.assertEqual(us.threat_zones({"zones": {"1": "x", "2": [{"zone": "Near-volcano"}]}}),
                         {"2": [{"zone": "Near-volcano"}]})
        self.assertEqual(us.threat_zones({"zones": []}), {})
