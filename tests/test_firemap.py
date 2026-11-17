"""firemap: fire detections and air-quality sites for the shared map as D19 point files (Weather items 309/333).

Fixtures are the services' own answers of 2026-11-17 (bin\\ltw333map_fixtures.py): FIRMS's keyless 24-hour NOAA-20
file for the US cut to Lake Michigan's south end and Hawaii (134 of 2,445 rows, header as served, no `type` column),
and AirNow's data/ for Hawaii's box (10 sites); with item 351's standard product around Indiana Dunes (the mills).
"""

import gzip
import json
import unittest
from datetime import datetime, timedelta, timezone

from _load import FIXTURES, load

fm = load("firemap")
hz = load("hazards")


def text(name):
    return (FIXTURES / name).read_text(encoding="utf-8")


FILE = text("firms_file_j1_us_cut_20261117.csv")
SP = text("firms_sp_noaa20_indiana_dunes_20260727.csv")
AIR = json.loads(text("airnow_data_hawaii_20261117.json"))
ROWS = FILE.splitlines()[1:]
NEWEST = max(datetime.strptime(f"{r.split(',')[5]} {int(r.split(',')[6]):04d}", "%Y-%m-%d %H%M") for r in ROWS
             ).replace(tzinfo=timezone.utc)
NOW = NEWEST + timedelta(hours=1)


class TestRegions(unittest.TestCase):
    def test_known_regions_in_fixed_order(self):
        self.assertEqual(fm.regions_of(["world", "canada", "bogus", "us"]), ["us", "canada", "world"])
        self.assertEqual(fm.regions_of(None), [])
        self.assertEqual(fm.regions_of("us"), [])
        self.assertEqual(fm.regions_of({"us": True}), [], "only a list, tuple or set counts")

    def test_no_two_regions_share_an_airnow_box(self):
        boxes = [b for r in fm.REGION_ORDER for b in fm.REGIONS[r]["airnow"]]
        self.assertEqual(len(boxes), len(set(boxes)))

    def test_world_replaces_the_region_files(self):
        self.assertEqual(fm.file_regions(["us", "canada"]), ["USA_contiguous_and_Hawaii", "Canada"])
        self.assertEqual(fm.file_regions(["us", "world"]), ["Global"])
        self.assertEqual(fm.file_regions([]), [])

    def test_file_url(self):
        self.assertEqual(fm.file_url("noaa-20-viirs-c2", "J1_VIIRS_C2", "Canada"),
                         "https://firms.modaps.eosdis.nasa.gov/data/active_fire/noaa-20-viirs-c2/csv/"
                         "J1_VIIRS_C2_Canada_24h.csv")

    def test_airnow_boxes_us_and_canada_only(self):
        self.assertEqual(fm.airnow_boxes(["world"]), [])
        self.assertEqual(fm.airnow_boxes(["us", "world"]), ["-125,24,-66,50", "-161,18,-154,23"])
        self.assertEqual(len(fm.airnow_boxes(["us", "alaska", "canada"])), 4)

    def test_world_list_is_one_window_the_others_six(self):
        self.assertEqual(fm.REGIONS["world"]["windows"], 1)
        self.assertEqual({fm.REGIONS[r]["windows"] for r in ("us", "alaska", "canada")}, {6})

    def test_list_windows(self):
        self.assertEqual(fm.list_windows("2026-07-31", 1), ["2026-07-27"])
        self.assertEqual(fm.list_windows("2026-07-31", 3), ["2026-07-27", "2026-07-22", "2026-07-17"])


class TestStaticCells(unittest.TestCase):
    def test_same_cells_as_the_place_list(self):
        cells = fm.static_cells_csv(SP)
        self.assertEqual(cells, hz.static_cells(hz.parse_firms(SP, "VIIRS_NOAA20_SP")))
        self.assertTrue(cells)

    def test_type_zero_is_not_listed(self):
        t = "latitude,longitude,type\n41.0,-87.0,0\n41.1,-87.1,2\n41.2,-87.2,1\n41.3,-87.3,3\n41.4,-87.4,\n"
        self.assertEqual(fm.static_cells_csv(t), {hz.cell(41.1, -87.1), hz.cell(41.2, -87.2), hz.cell(41.3, -87.3)})

    def test_not_csv_is_none(self):
        self.assertIsNone(fm.static_cells_csv("Invalid MAP_KEY."))
        self.assertIsNone(fm.static_cells_csv(None))
        self.assertIsNone(fm.static_cells_csv(""))
        self.assertIsNone(fm.static_cells_csv("latitude,longitude,frp\n1,2,3\n"))

    def test_bad_row_skipped(self):
        self.assertEqual(fm.static_cells_csv("latitude,longitude,type\nx,1,2\n41.0,-87.0,2\n41.5\n"),
                         {hz.cell(41.0, -87.0)})


class TestFireFile(unittest.TestCase):
    def test_every_row_parsed_with_its_fields(self):
        # The "24h" file spans 28 h 53 min (2026-11-16 06:39 to 11-17 11:32, measured): an hour after its newest
        # row, 79 of its 134 rows are younger than 24 h (11-16 18:xx onward: 5 + 10 + 2 + 39 + 23).
        pts = fm.parse_fire_file(FILE, "NOAA-20", NOW)
        self.assertEqual(len(pts), 79)
        self.assertEqual(len(fm.parse_fire_file(FILE, "NOAA-20", NEWEST - timedelta(hours=5))), 134)
        p = pts[0]
        self.assertEqual(len(p), 7)
        self.assertEqual(p[2], "fire")
        self.assertEqual(p[4], "NOAA-20")
        self.assertIn(p[6], ("low", "nominal", "high"))
        self.assertTrue(all(-90 <= q[1] <= 90 and -180 <= q[0] <= 180 for q in pts))
        self.assertTrue(any(18 <= q[1] <= 23 for q in pts), "Hawaii kept")

    def test_lon_lat_order_and_rounding(self):
        t = ("latitude,longitude,acq_date,acq_time,frp,confidence\n"
             "41.123456,-87.654321,2026-11-17,0705,3.14159,h\n")
        self.assertEqual(fm.parse_fire_file(t, "NOAA-21", datetime(2026, 11, 17, 8, tzinfo=timezone.utc)),
                         [[-87.6543, 41.1235, "fire", "2026-11-17 07:05", "NOAA-21", 3.1, "high"]])

    def test_older_than_24_h_dropped(self):
        t = ("latitude,longitude,acq_date,acq_time\n41,-87,2026-11-16,0659\n41,-87,2026-11-16,0701\n")
        pts = fm.parse_fire_file(t, "x", datetime(2026, 11, 17, 7, 0, tzinfo=timezone.utc))
        self.assertEqual([p[3] for p in pts], ["2026-11-16 07:01"])

    def test_bad_rows_and_missing_fields(self):
        t = ("latitude,longitude,acq_date,acq_time,frp,confidence\n"
             "x,-87,2026-11-17,0700,1,n\n95,-87,2026-11-17,0700,1,n\n41,-87,2026-11-17,0700,,\n"
             "41,-87,2026-11-17,0700,bad,q\n41,-87\n")
        pts = fm.parse_fire_file(t, "s", datetime(2026, 11, 17, 8, tzinfo=timezone.utc))
        self.assertEqual([(p[5], p[6]) for p in pts], [(None, None), (None, "q")])

    def test_not_csv(self):
        self.assertIsNone(fm.parse_fire_file("<html>", "s", NOW))
        self.assertIsNone(fm.parse_fire_file("latitude,longitude,frp\n", "s", NOW))


class TestStanding(unittest.TestCase):
    def test_the_mills_are_dropped(self):
        pts = fm.parse_fire_file(FILE, "NOAA-20", NOW)
        cells = fm.static_cells_csv(SP)
        kept = fm.drop_standing(pts, cells)
        self.assertLess(len(kept), len(pts))
        self.assertTrue(all(not hz.standing({"lat": p[1], "lon": p[0]}, cells) for p in kept))
        gone = [p for p in pts if p not in kept]
        self.assertTrue(all(41.55 <= p[1] <= 41.75 and -87.5 <= p[0] <= -87.0 for p in gone), "only the Dunes mills")

    def test_neighbouring_cell_counts(self):
        c = hz.cell(41.6, -87.1)
        p = [-87.1 + hz.CELL_DEG, 41.6, "fire"]
        self.assertEqual(fm.drop_standing([p], {c}), [])
        far = [-87.1 + 2 * hz.CELL_DEG, 41.6, "fire"]
        self.assertEqual(fm.drop_standing([far], {c}), [far])


class TestAirNow(unittest.TestCase):
    def test_sites(self):
        pts = fm.parse_airnow_sites(AIR)
        self.assertEqual(len(pts), 10)
        p = pts[0]
        self.assertEqual(p[:3], [-157.8711, 21.3039, "good"])
        self.assertEqual(p[3:], ["SAND ISLAND 2 - ANUENUE FISHERIES", "Hawaii State Dept. of Health", 22,
                                 "2026-11-17 18:00"])

    def test_categories_and_rejects(self):
        rows = [{"Latitude": 40.0, "Longitude": -100.0, "AQI": a, "Category": c, "SiteName": "s", "AgencyName": ""}
                for a, c in ((10, 1), (60, 2), (120, 3), (160, 4), (210, 5), (310, 6), (-999, 1), (50, 9),
                             (50, None))]
        rows += [{"Latitude": True, "Longitude": -100.0, "AQI": 5, "Category": 1}, "x",
                 {"Latitude": 95.0, "Longitude": -100.0, "AQI": 5, "Category": 1}]
        pts = fm.parse_airnow_sites(rows)
        self.assertEqual([p[2] for p in pts], ["good", "moderate", "usg", "unhealthy", "very_unhealthy", "hazardous"])
        self.assertIsNone(pts[0][4], "empty agency is null")
        self.assertIsNone(pts[0][6])

    def test_not_a_list(self):
        self.assertIsNone(fm.parse_airnow_sites({"WebServiceError": []}))

    def test_dedupe_keeps_first(self):
        a, b, c = [1, 2, "good", "x"], [1, 2, "good", "y"], [1, 2, "moderate", "z"]
        self.assertEqual(fm.dedupe([a, b, c]), [a, c])

    def test_hour(self):
        self.assertEqual(fm.airnow_hour(datetime(2026, 11, 17, 19, 5, tzinfo=timezone.utc)), "2026-11-17T18")


class TestPointFile(unittest.TestCase):
    def test_shape_and_gzip(self):
        pts = [[2.0, 1.0, "fire", "t", "NOAA-20", 1.0, "low"], [1.0, 1.0, "fire", "t", "NOAA-21", None, None]]
        digest, gz = fm.point_file(pts, fm.FIRE_COLUMNS, {"source": "x"})
        doc = json.loads(gzip.decompress(gz))
        self.assertEqual(set(doc), {"meta", "columns", "points"})
        self.assertEqual(doc["points"][0][0], 1.0, "sorted")
        self.assertEqual(len(doc["columns"]) + 3, len(doc["points"][0]))
        self.assertRegex(digest, r"^[0-9a-f]{12}$")
        self.assertEqual(gz[4:8], b"\x00\x00\x00\x00", "no time in the gzip header: same points, same bytes")

    def test_digest_by_content_not_order(self):
        a = [[1.0, 1.0, "good", "a"], [2.0, 2.0, "good", "b"]]
        d1, g1 = fm.point_file(a, fm.AQI_COLUMNS, {})
        d2, g2 = fm.point_file(list(reversed(a)), fm.AQI_COLUMNS, {})
        self.assertEqual((d1, g1), (d2, g2))
        d3, _ = fm.point_file(a[:1], fm.AQI_COLUMNS, {})
        self.assertNotEqual(d1, d3)

    def test_styles_follow_d19(self):
        for styles in (fm.FIRE_STYLE, fm.AQI_STYLES):
            for s in styles.values():
                self.assertRegex(s["color"], r"^#[0-9A-F]{6}$")
                self.assertTrue(2 <= s["radius"] <= 10)
                self.assertRegex(s["outline"], r"^#[0-9A-F]{6}$")
                self.assertTrue(s["label"])
        self.assertEqual(set(fm.AQI_CATEGORY.values()), set(fm.AQI_STYLES))


if __name__ == "__main__":
    unittest.main()
