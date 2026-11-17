"""hazards: fire (NASA FIRMS, keyed) and smoke (AirNow) at a watched place, on "Alert at X" (Weather SSOT item 351).

Fixtures are the services' own answers of 2026-11-17 at public places (bin\\ltw351_fixtures.py): FIRMS's standard
product around Indiana Dunes, 2026-07-27..31 (the mills, types 2 and 3); its NRT NOAA-20 and NOAA-21 answers for the
same 35 km box, day range 2 (156 detections, all the mills); AirNow's ziplatlong answer at Glacier (three pollutants),
its no-observations envelope (Oslo) and its wrong-key envelope.
"""

import json
import unittest
from datetime import datetime, timedelta, timezone

from _load import FIXTURES, load

hz = load("hazards")
pl = load("places")
DUNES = (41.6590, -87.0470)


def text(name):
    return (FIXTURES / name).read_text(encoding="utf-8")


SP = hz.parse_firms(text("firms_sp_noaa20_indiana_dunes_20260727.csv"), "VIIRS_NOAA20_SP")
NRT = (hz.parse_firms(text("firms_nrt_noaa21_indiana_dunes_20261117.csv"), "VIIRS_NOAA21_NRT")
       + hz.parse_firms(text("firms_nrt_noaa20_indiana_dunes_20261117.csv"), "VIIRS_NOAA20_NRT"))
NEWEST = max(datetime.fromisoformat(d["time"]) for d in NRT)
AVAIL = ("data_id,min_date,max_date\nMODIS_NRT,2026-09-01,2026-11-17\nMODIS_SP,2000-11-01,2026-08-31\n"
         "VIIRS_NOAA20_NRT,2026-08-01,2026-11-17\nVIIRS_NOAA20_SP,2018-04-01,2026-07-31\n"
         "VIIRS_NOAA21_SP,2023-03-01,2026-07-31\nVIIRS_SNPP_SP,2012-01-20,2026-07-31\n")


def det(lat, lon, hours_ago=1.0, typ=None, source="VIIRS_NOAA21_NRT"):
    t = (NEWEST - timedelta(hours=hours_ago)).isoformat()
    return {"lat": lat, "lon": lon, "time": t, "source": source, "satellite": "N21", "confidence": "n", "frp": 3.0,
            "version": "2.0URT", "type": typ}


class TestBox(unittest.TestCase):
    def test_box_holds_the_circle(self):
        w, s, e, n = map(float, hz.box(*DUNES, 35).split(","))
        self.assertAlmostEqual(n - DUNES[0], 35 / 111, places=2)
        self.assertAlmostEqual(DUNES[0] - s, 35 / 111, places=2)
        self.assertGreater(e - DUNES[1], 35 / 111)          # longitude degrees are shorter at 41.7 N
        self.assertAlmostEqual(e - DUNES[1], DUNES[1] - w, places=3)

    def test_box_clamped(self):
        w, s, e, n = map(float, hz.box(89.9, 179.9, 50).split(","))
        self.assertLessEqual(n, 90.0)
        self.assertLessEqual(e, 180.0)
        self.assertGreaterEqual(w, -180.0)


class TestParse(unittest.TestCase):
    def test_sp_rows_and_types(self):
        self.assertEqual(len(SP), len(text("firms_sp_noaa20_indiana_dunes_20260727.csv").splitlines()) - 1)
        self.assertEqual(len(SP), 207)
        self.assertEqual({d["type"] for d in SP}, {"2", "3"})
        self.assertTrue(all(d["time"].endswith("+00:00") for d in SP))

    def test_nrt_rows(self):
        lines = sum(len(text(f).splitlines()) - 1 for f in ("firms_nrt_noaa21_indiana_dunes_20261117.csv",
                                                            "firms_nrt_noaa20_indiana_dunes_20261117.csv"))
        self.assertEqual(len(NRT), lines)
        self.assertEqual(len(NRT), 156)
        self.assertTrue({d["version"] for d in NRT} <= {"2.0NRT", "2.0URT"})
        self.assertTrue(all(isinstance(d["frp"], float) for d in NRT))
        self.assertTrue(all(d["type"] is None for d in NRT))   # the NRT product has no type

    def test_not_firms(self):
        self.assertIsNone(hz.parse_firms("Invalid MAP_KEY.", "X"))
        self.assertIsNone(hz.parse_firms(None, "X"))
        self.assertIsNone(hz.parse_firms("Invalid day range. Expects [1..5].", "X"))
        self.assertEqual(hz.parse_firms("latitude,longitude,path,row,scan,track,acq_date,acq_time,satellite,"
                                        "confidence,daynight\n", "LANDSAT_NRT"), [])

    def test_landsat_without_frp_and_bad_rows(self):
        t = ("latitude,longitude,path,row,scan,track,acq_date,acq_time,satellite,confidence,daynight\n"
             "41.5,-87.1,22,31,0.03,0.03,2026-11-17,1640,L8,medium,D\n"
             "x,-87.1,22,31,0.03,0.03,2026-11-17,1640,L8,medium,D\n"
             "41.5,-87.1,22,31,0.03,0.03,2026-11-17,noon,L8,medium,D\n")
        rows = hz.parse_firms(t, "LANDSAT_NRT")
        self.assertEqual(len(rows), 1)
        self.assertIsNone(rows[0]["frp"])
        self.assertEqual(rows[0]["time"], "2026-11-17T16:40:00+00:00")


class TestStaticList(unittest.TestCase):
    def test_static_cells_from_types(self):
        cells = hz.static_cells(SP)
        self.assertGreater(len(cells), 5)
        mixed = [det(41.6, -87.1, typ="0"), det(41.7, -87.2, typ="2"), det(41.8, -87.3, typ="1"),
                 det(41.9, -87.4, typ="3"), det(42.0, -87.5, typ=None)]
        self.assertEqual(hz.static_cells(mixed), {hz.cell(41.7, -87.2), hz.cell(41.8, -87.3), hz.cell(41.9, -87.4)})

    def test_the_mills_are_left_out(self):
        now = NEWEST + timedelta(hours=1)
        without = hz.fires_near(NRT, *DUNES, 35, set(), now, max_age_h=48)
        withl = hz.fires_near(NRT, *DUNES, 35, hz.static_cells(SP), now, max_age_h=48)
        self.assertEqual(len(without), len(NRT))
        self.assertEqual(withl, [])

    def test_neighbour_cell_counts_two_away_does_not(self):
        cells = {hz.cell(41.70, -87.20)}
        self.assertTrue(hz.standing(det(41.70, -87.20), cells))
        self.assertTrue(hz.standing(det(41.72, -87.18), cells))      # next cell, diagonal
        self.assertFalse(hz.standing(det(41.74, -87.20), cells))     # two cells away

    def test_a_fire_beside_nothing_static_counts(self):
        f = hz.fires_near([det(41.80, -87.05)], *DUNES, 35, hz.static_cells(SP), NEWEST + timedelta(hours=1))
        self.assertEqual(len(f), 1)

    def test_sp_dates_and_windows(self):
        d = hz.sp_max_dates(AVAIL)
        self.assertEqual(d, {"VIIRS_NOAA20_SP": "2026-07-31", "VIIRS_NOAA21_SP": "2026-07-31"})
        self.assertEqual(hz.sp_max_dates("Invalid MAP_KEY."), {})
        self.assertEqual(hz.sp_max_dates("data_id,min_date,max_date\nVIIRS_NOAA20_SP,2018-04-01,soon\n"), {})
        w = hz.static_windows("2026-07-31")
        self.assertEqual(w, ["2026-07-27", "2026-07-22", "2026-07-17", "2026-07-12", "2026-07-07", "2026-07-02"])
        self.assertEqual(len(w), hz.STATIC_WINDOWS)


class TestFiresNear(unittest.TestCase):
    def test_distance_age_order_bearing(self):
        now = NEWEST
        dets = [det(41.66 + 0.3, -87.047, 2),          # ~33 km N
                det(41.659, -87.047 + 0.1, 3),         # ~8 km E
                det(41.66 - 0.6, -87.047, 1),          # ~67 km S: beyond 50
                det(41.66, -87.047 - 0.2, 30)]         # 30 h old
        f = hz.fires_near(dets, *DUNES, 50, set(), now)
        self.assertEqual([x["bearing"] for x in f], ["E", "N"])
        self.assertLess(f[0]["km"], f[1]["km"])
        self.assertAlmostEqual(f[0]["km"], 8.3, delta=0.3)
        self.assertEqual(hz.fires_near(dets[3:], *DUNES, 50, set(), now, max_age_h=31)[0]["bearing"], "W")

    def test_bearings(self):
        self.assertEqual(hz.bearing(0, 0, 1, 0), "N")
        self.assertEqual(hz.bearing(0, 0, 0, 1), "E")
        self.assertEqual(hz.bearing(0, 0, -1, 0), "S")
        self.assertEqual(hz.bearing(0, 0, -1, -1), "SW")
        self.assertEqual(hz.bearing(0, 0, 1, -1), "NW")

    def test_fire_record(self):
        self.assertIsNone(hz.fire_record([]))
        f = hz.fires_near([det(41.659, -86.947, 2), det(41.96, -87.047, 1)], *DUNES, 50, set(), NEWEST)
        r = hz.fire_record(f)
        self.assertEqual(r["event"], "Fire detected 8 km E")
        self.assertTrue(r["always"])
        self.assertEqual(r["severity"], "Severe")
        self.assertIn("and 1 more", r["headline"])
        self.assertEqual(r["km"], f[0]["km"])
        self.assertEqual(r["source"], "NASA FIRMS")


class TestSmoke(unittest.TestCase):
    def test_glacier_reading(self):
        r = hz.parse_airnow(json.loads(text("airnow_ziplatlong_glacier_20261117.json")))
        self.assertEqual(r["aqi"], 52)
        self.assertEqual(r["category"], "Moderate")
        self.assertEqual(r["site"], "Columbia Falls")
        self.assertEqual(r["agency"], "Montana DEQ")
        self.assertTrue(r["observed"].startswith("2026-11-17 03:00 MST"))

    def test_none_and_errors(self):
        oslo = json.loads(text("airnow_ziplatlong_oslo_none_20261117.json"))
        self.assertIsNone(hz.parse_airnow(oslo))
        self.assertIn("No observations", hz.airnow_error(oslo))
        self.assertEqual(hz.airnow_error(json.loads(text("airnow_wrong_key_20261117.json"))), "Invalid API key")
        self.assertIsNone(hz.airnow_error([]))
        self.assertIsNone(hz.parse_airnow([{"parameterName": "OZONE", "nowcastAQI": 30}]))
        for bad in (None, -1, True, "52"):
            self.assertIsNone(hz.parse_airnow([{"parameterName": "PM2.5", "nowcastAQI": bad}]))

    def test_threshold(self):
        r = {"aqi": 90, "category": "Moderate", "site": "S", "agency": "A", "observed": "2026-11-17 03:00 MST"}
        rec = hz.smoke_record(r, 90)
        self.assertEqual(rec["event"], "Smoke: PM2.5 AQI 90")
        self.assertTrue(rec["always"])
        self.assertIsNone(hz.smoke_record({**r, "aqi": 89}, 90))
        self.assertIsNone(hz.smoke_record(None, 90))


class TestOnAlertAtX(unittest.TestCase):
    def test_counts_whatever_the_threshold(self):
        fire = hz.fire_record(hz.fires_near([det(41.659, -86.947)], *DUNES, 50, set(), NEWEST))
        s = pl.summary([fire], "extreme")
        self.assertTrue(s["on"])
        self.assertEqual(s["alerts"][0]["km"], fire["km"])
        self.assertTrue(s["alerts"][0]["always"])
        nws = {"source": "NWS", "id": "x", "event": "Frost Advisory", "severity": "Minor", "priority": 50}
        s = pl.summary([nws], "extreme")
        self.assertFalse(s["on"])
        self.assertNotIn("always", s["alerts"][0])
        smoke = hz.smoke_record({"aqi": 120, "category": "USG", "site": "S", "agency": "A", "observed": "o"}, 90)
        s = pl.summary([nws, smoke], "severe")
        self.assertEqual(s["highest"], "Smoke: PM2.5 AQI 120")
        self.assertEqual(s["alerts"][0]["aqi"], 120)


if __name__ == "__main__":
    unittest.main()
