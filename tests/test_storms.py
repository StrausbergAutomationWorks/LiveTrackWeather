"""Tropical cyclones (contract D15): NHC and EONET parsing, the join, the output.

Fixtures are real answers captured 2026-10-27 07:50-07:52Z (Weather
`20_Research/REPORT_302_step1_20261027.md`): Vance (ep222026, advisory 23) and
Olana (cp032026) from NHC; six open storms from EONET.
"""

import io
import json
import unittest
import zipfile
from datetime import datetime, timezone

from _load import FIXTURES, load

st = load("storms")
NOW = datetime(2026, 10, 27, 7, 52, 12, tzinfo=timezone.utc)


def fx(name):
    return (FIXTURES / name).read_bytes()


def nhc():
    return st.nhc_storms(json.loads(fx("nhc_CurrentStorms_20261027T0750Z.json")))


def eonet(stale_h=36, now=NOW):
    return st.eonet_storms(json.loads(fx("eonet_severeStorms_open_20261027T0752Z.geojson")), now, stale_h)


def kml(name):
    return st.kml_from_kmz(fx(name))


class TestCategory(unittest.TestCase):
    def test_boundaries(self):
        cases = {33: "TD", 34: "TS", 63: "TS", 64: "H1", 82: "H1", 83: "H2", 95: "H2",
                 96: "H3", 112: "H3", 113: "H4", 136: "H4", 137: "H5", 180: "H5"}
        for kt, cat in cases.items():
            self.assertEqual(st.category(kt), cat, kt)
        self.assertIsNone(st.category(None))

    def test_every_category_has_a_colour(self):
        for c in st.CATEGORY_ORDER + (st.NOT_TROPICAL,):
            self.assertRegex(st.CATEGORY_COLOURS[c], r"^#[0-9A-F]{6}$")

    def test_jtwc_class_by_basin(self):
        self.assertEqual(st.jtwc_class(110, "wp"), "Typhoon")
        self.assertEqual(st.jtwc_class(130, "wp"), "Super Typhoon")
        self.assertEqual(st.jtwc_class(129, "wp"), "Typhoon")
        self.assertEqual(st.jtwc_class(90, "io"), "Cyclone")
        self.assertEqual(st.jtwc_class(90, "sh"), "Cyclone")
        self.assertEqual(st.jtwc_class(90, "ep"), "Hurricane")
        self.assertEqual(st.jtwc_class(50, "wp"), "Tropical Storm")
        self.assertEqual(st.jtwc_class(30, "wp"), "Tropical Depression")
        self.assertIsNone(st.jtwc_class(None, "wp"))


class TestIds(unittest.TestCase):
    def test_atcf_from_jtwc(self):
        self.assertEqual(st.atcf_from_jtwc("https://www.metoc.navy.mil/jtwc/products/ep2226.tcw"), "ep222026")
        self.assertEqual(st.atcf_from_jtwc("https://www.metoc.navy.mil/jtwc/products/WP3026.tcw"), "wp302026")
        self.assertIsNone(st.atcf_from_jtwc("https://www.metoc.navy.mil/jtwc/products/xx2226.tcw"))
        self.assertIsNone(st.atcf_from_jtwc(None))

    def test_nhc_ref(self):
        self.assertEqual(st.nhc_ref("https://www.nhc.noaa.gov/archive/2026/VANCE.shtml"), ("2026", "VANCE"))
        self.assertIsNone(st.nhc_ref("https://example.org/VANCE.shtml"))

    def test_storm_name(self):
        self.assertEqual(st.storm_name("Super Typhoon Champi"), "Champi")
        self.assertEqual(st.storm_name("Typhoon In-fa"), "In-fa")
        self.assertEqual(st.storm_name("Hurricane Vance"), "Vance")
        self.assertEqual(st.storm_name("Tropical Cyclone Agueda"), "Agueda")
        self.assertEqual(st.storm_name("Tropical Storm Olana"), "Olana")
        self.assertIsNone(st.storm_name(""))


class TestNhc(unittest.TestCase):
    def test_current_storms(self):
        s = {x["key"]: x for x in nhc()}
        self.assertEqual(sorted(s), ["cp032026", "ep222026"])
        v = s["ep222026"]
        self.assertEqual((v["name"], v["kt"], v["class_code"], v["pressure"]), ("Vance", 45, "TS", 999))
        self.assertEqual((v["lat"], v["lon"], v["move_dir"], v["move_mph"]), (15.5, -106.3, 275, 5))
        self.assertEqual(v["advisory"], 23)
        self.assertEqual(v["time"], "2026-10-27T03:00:00.000Z")
        self.assertTrue(v["links"]["trackCone"].endswith("EP222026_023adv_CONE.kmz"))
        self.assertTrue(v["links"]["bestTrackGIS"].endswith("ep222026_best_track.kmz"))

    def test_malformed(self):
        self.assertEqual(st.nhc_storms(None), [])
        self.assertEqual(st.nhc_storms({"activeStorms": "x"}), [])
        bad = {"activeStorms": [
            {"id": "ep222026", "latitudeNumeric": 95, "longitudeNumeric": 0},
            {"id": "wp302026", "latitudeNumeric": 10, "longitudeNumeric": 0},
            {"id": "al012026", "latitudeNumeric": "x", "longitudeNumeric": 0},
            "junk",
        ]}
        self.assertEqual(st.nhc_storms(bad), [])


class TestKml(unittest.TestCase):
    def test_cone(self):
        polys = st.cone_polygons(kml("nhc_ep222026_023_cone.kmz"))
        self.assertEqual(len(polys), 1)
        self.assertEqual(len(polys[0]), 1)
        self.assertEqual(len(polys[0][0]), 1024)

    def test_forecast_line(self):
        line = st.forecast_line(kml("nhc_ep222026_023_track.kmz"))
        self.assertEqual(len(line), 7)
        self.assertEqual(line[0], [-106.3, 15.5])

    def test_forecast_prefers_longest_period(self):
        doc = (b'<kml xmlns="http://www.opengis.net/kml/2.2"><Document>'
               b'<Placemark><LineString><coordinates>1,1 2,2 3,3 4,4</coordinates></LineString>'
               b'<ExtendedData><Data name="fcstpd"><value>72</value></Data></ExtendedData></Placemark>'
               b'<Placemark><LineString><coordinates>1,1 9,9</coordinates></LineString>'
               b'<ExtendedData><Data name="fcstpd"><value>120</value></Data></ExtendedData></Placemark>'
               b'</Document></kml>')
        self.assertEqual(st.forecast_line(doc), [[1.0, 1.0], [9.0, 9.0]])

    def test_wind_extent(self):
        w = st.wind_extent(kml("nhc_ep222026_023_initialradii.kmz"))
        self.assertEqual(list(w), ["34"])
        self.assertEqual(len(w["34"]), 1)
        self.assertEqual(len(w["34"][0][0]), 361)

    def test_wind_extent_names_only_thresholds(self):
        doc = (b'<kml xmlns="http://earth.google.com/kml/2.1"><Placemark><name>99</name><Polygon>'
               b'<outerBoundaryIs><LinearRing><coordinates>0,0 1,0 1,1 0,0</coordinates>'
               b'</LinearRing></outerBoundaryIs></Polygon></Placemark></kml>')
        self.assertEqual(st.wind_extent(doc), {})

    def test_best_track(self):
        pts = st.best_track_points(kml("nhc_ep222026_besttrack.kmz"))
        self.assertEqual(len(pts), 34)
        self.assertEqual(pts[0], [-89.2, 10.6])

    def test_polygon_with_hole(self):
        doc = (b'<kml><Placemark><Polygon><innerBoundaryIs><LinearRing><coordinates>'
               b'0.2,0.2 0.4,0.2 0.4,0.4 0.2,0.2</coordinates></LinearRing></innerBoundaryIs>'
               b'<outerBoundaryIs><LinearRing><coordinates>0,0 1,0 1,1 0,0'
               b'</coordinates></LinearRing></outerBoundaryIs></Polygon></Placemark></kml>')
        rings = st.cone_polygons(doc)[0]
        self.assertEqual(rings[0][1], [1.0, 0.0])   # outer first
        self.assertEqual(rings[1][0], [0.2, 0.2])

    def test_kmz_variants(self):
        self.assertIsNone(st.kml_from_kmz(b""))
        self.assertIsNone(st.kml_from_kmz(b"PK not a zip"))
        self.assertEqual(st.kml_from_kmz(b"<kml/>"), b"<kml/>")
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w") as z:
            z.writestr("a.png", b"x")
        self.assertIsNone(st.kml_from_kmz(buf.getvalue()))


class TestEonet(unittest.TestCase):
    def test_fresh_storms_only(self):
        s = {x["key"]: x for x in eonet()}
        # Champi (37.9 h) and Agueda (85.9 h) are past 36 h
        self.assertEqual(sorted(s), ["cp032026", "ep222026", "io022026", "wp302026"])
        self.assertEqual((s["wp302026"]["name"], s["wp302026"]["kt"]), ("In-fa", 110))
        self.assertEqual(s["wp302026"]["track"][-1], [162.4, 14.3])
        self.assertEqual(len(s["wp302026"]["track"]), 14)
        self.assertEqual(s["ep222026"]["nhc_ref"], ("2026", "VANCE"))
        self.assertEqual(s["io022026"]["time"], "2026-10-27T00:00:00Z")

    def test_cutoff_moves_with_now(self):
        self.assertEqual(len(eonet(stale_h=100)), 6)
        self.assertEqual(len(eonet(stale_h=1)), 0)

    def test_closed_and_malformed(self):
        self.assertEqual(st.eonet_storms(None, NOW, 36), [])
        doc = {"features": [
            {"properties": {"id": "E1", "date": "2026-10-27T00:00:00Z", "closed": "2026-10-27T01:00:00Z"},
             "geometry": {"type": "Point", "coordinates": [1, 1]}},
            {"properties": {"id": "E2", "date": "nope"}, "geometry": {"type": "Point", "coordinates": [1, 1]}},
            {"properties": {"id": "E3", "date": "2026-10-27T00:00:00Z"}, "geometry": {"type": "Polygon", "coordinates": []}},
        ]}
        self.assertEqual(st.eonet_storms(doc, NOW, 36), [])


class TestMerge(unittest.TestCase):
    def test_nhc_wins(self):
        m = st.merge(nhc(), eonet())
        by = {s["key"]: s["source"] for s in m}
        self.assertEqual(by, {"cp032026": "nhc", "ep222026": "nhc", "io022026": "eonet", "wp302026": "eonet"})

    def test_join_by_id_alone(self):
        e = {"key": "ep222026", "nhc_ref": None, "source": "eonet"}
        self.assertEqual([s["source"] for s in st.merge(nhc(), [e])], ["nhc", "nhc"])

    def test_join_by_name_without_jtwc(self):
        e = {"key": "eonet_99999", "nhc_ref": ("2026", "VANCE"), "source": "eonet"}
        self.assertEqual([s["key"] for s in st.merge(nhc(), [e])], ["cp032026", "ep222026"])
        e2 = dict(e, nhc_ref=("2025", "VANCE"))
        self.assertIn("eonet_99999", [s["key"] for s in st.merge(nhc(), [e2])])


class TestOutput(unittest.TestCase):
    def rec(self, key):
        return st.entity_record(next(s for s in st.merge(nhc(), eonet()) if s["key"] == key))

    def test_nhc_record(self):
        r = self.rec("ep222026")
        self.assertEqual(r["name"], "Tropical Storm Vance")
        a = r["attrs"]
        self.assertEqual(a["identity"], "EP222026")
        self.assertEqual(a["marker_label"], "Vance")
        self.assertEqual(a["map_layer"], "weather")
        self.assertEqual(a["storm_category"], "TS")
        self.assertEqual(a["marker_color"], st.CATEGORY_COLOURS["TS"])
        self.assertEqual(a["max_wind_kmh"], 83.3)
        self.assertEqual(a["pressure_hpa"], 999)
        self.assertEqual((a["course_deg"], a["speed_kmh"]), (275.0, 8.0))
        self.assertEqual(a["advisory_number"], 23)
        self.assertEqual(a["storm_source"], "nhc")
        self.assertEqual(a["attribution"], st.ATTRIBUTION_NHC)
        self.assertNotIn("previous_latitude", a)

    def test_post_tropical_is_grey(self):
        a = self.rec("cp032026")["attrs"]
        self.assertEqual(a["storm_class"], "Post-Tropical Cyclone")
        self.assertEqual(a["storm_category"], "PT")
        self.assertEqual(a["marker_color"], "#BFBFBF")

    def test_eonet_record(self):
        r = self.rec("wp302026")
        self.assertEqual(r["name"], "Typhoon In-fa")
        a = r["attrs"]
        self.assertEqual(a["identity"], "WP302026")
        self.assertEqual(a["storm_category"], "H3")
        self.assertEqual(a["storm_source"], "jtwc_eonet")
        self.assertEqual(a["attribution"], st.ATTRIBUTION_EONET)
        for k in ("pressure_hpa", "course_deg", "speed_kmh", "advisory_number"):
            self.assertNotIn(k, a)

    def test_stationary_has_no_course(self):
        s = dict(nhc()[1], move_mph=0)
        self.assertNotIn("course_deg", st.entity_record(s)["attrs"])
        self.assertNotIn("speed_kmh", st.entity_record(s)["attrs"])

    def test_shapes(self):
        s = next(x for x in nhc() if x["key"] == "ep222026")
        products = {
            "cone": st.cone_polygons(kml("nhc_ep222026_023_cone.kmz")),
            "forecast": st.forecast_line(kml("nhc_ep222026_023_track.kmz")),
            "wind": st.wind_extent(kml("nhc_ep222026_023_initialradii.kmz")),
            "past": st.best_track_points(kml("nhc_ep222026_besttrack.kmz")),
        }
        shapes = st.shapes_for(s, products)
        self.assertEqual([x["event"] for x in shapes],
                         ["Forecast cone", "Tropical-storm-force winds", "Past track", "Forecast track"])
        self.assertEqual({x["type"] for x in shapes}, {"Polygon", "LineString"})
        for x in shapes:
            self.assertIn(x["event"], st.STYLES)
            self.assertEqual(x["storm"], "ep222026")
        self.assertEqual(len(json.dumps(shapes)) < 60000, True)

    def test_eonet_past_track_only(self):
        s = next(x for x in eonet() if x["key"] == "wp302026")
        shapes = st.shapes_for(s, {})
        self.assertEqual([x["event"] for x in shapes], ["Past track"])
        self.assertEqual(len(shapes[0]["coordinates"]), 14)

    def test_one_point_forecast_is_not_drawn(self):
        s = next(x for x in nhc() if x["key"] == "ep222026")
        self.assertEqual(st.shapes_for(s, {"forecast": [[1.0, 1.0]]}), [])

    def test_styles_priorities_unique(self):
        self.assertEqual(len({v["priority"] for v in st.STYLES.values()}), len(st.STYLES))


class TestUnwrap(unittest.TestCase):
    def test_across_antimeridian(self):
        self.assertEqual(st.unwrap([[179, 10], [-179, 11]], 179), [[179, 10], [181, 11]])
        self.assertEqual(st.unwrap([[179, 10], [-179, 11]], -179), [[-181, 10], [-179, 11]])

    def test_rounds(self):
        self.assertEqual(st.unwrap([[1.23456, 2.34567]], 0), [[1.235, 2.346]])


if __name__ == "__main__":
    unittest.main()
