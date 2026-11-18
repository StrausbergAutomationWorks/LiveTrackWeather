"""Storm reports (Weather SSOT item 312, contract D21): lsr.py.

Fixtures are NWS's own answers of 2026-11-18 ~08:0xZ (bin\\ltw312_lsr_probe*.py): the build's query on layer 0
(lsr_last24h_kinds_20261118.json, 12 reports) and the whole 72-hour layer (lsr_last72h_all_20261118.json, 216 reports
of every type).
"""

import copy
import json
import unittest
from datetime import datetime, timedelta, timezone

from _load import FIXTURES, load

lsr = load("lsr")
KINDS = json.loads((FIXTURES / "lsr_last24h_kinds_20261118.json").read_text(encoding="utf-8"))
ALL72 = json.loads((FIXTURES / "lsr_last72h_all_20261118.json").read_text(encoding="utf-8"))
NOW = datetime(2026, 11, 18, 8, 5, tzinfo=timezone.utc)


def feat(descript="Hail", mag="1.00", units="Inch", when=NOW - timedelta(minutes=30), lon=-90.0, lat=40.0, **p):
    props = {"descript": descript, "magnitude": mag, "units": units, "lsr_validtime": when.timestamp() * 1000,
             "loc_desc": "2 W Town", "state": "IL", "wfo": "Chicago IL", "wfo_id": "LOT", "remarks": " "}
    props.update(p)
    return {"type": "Feature", "geometry": {"type": "Point", "coordinates": [lon, lat]}, "properties": props}


def one(f, now=NOW):
    return lsr.points({"type": "FeatureCollection", "features": [f]}, now)


class TestReal(unittest.TestCase):
    def test_the_build_query(self):
        pts = lsr.points(KINDS, NOW)
        self.assertEqual(len(pts), 12)
        styles = sorted(p[2] for p in pts)
        self.assertEqual(styles.count("flash_flood_recent"), 5)
        self.assertEqual(styles.count("flash_flood_older"), 2)
        self.assertEqual(styles.count("flood_recent"), 1)
        self.assertEqual(styles.count("flood_older"), 2)
        self.assertIn("hail_recent", styles)
        self.assertIn("wind_older", styles)
        for p in pts:
            self.assertIn(p[2], lsr.STYLES)

    def test_hollywood_hail_row(self):
        hail = next(p for p in lsr.points(KINDS, NOW) if p[3] == "Hail")
        self.assertEqual(hail, [-80.19, 26.03, "hail_recent", "Hail", "1.00 in (25 mm)", "2 W Hollywood, FL",
                                "2026-11-18 04:10", "Miami FL", hail[8]])
        wind = next(p for p in lsr.points(KINDS, NOW) if p[3] == "Tstm Wnd Gst")
        self.assertEqual((wind[4], wind[5], wind[6]), ("60 mph (97 km/h)", "1 S Allison, NM", "2026-11-17 23:42"))
        self.assertEqual(wind[8], "Peak wind gust from passing thunderstorm.")

    def test_every_type_of_72_hours(self):
        # snow, non-thunderstorm wind, fog, rain, landslide ... are not drawn; the kinds are
        pts = lsr.points(ALL72, datetime(2026, 11, 18, 7, 51, tzinfo=timezone.utc))
        kinds = {p[3] for p in pts}
        self.assertEqual(kinds, {"Hail", "Tstm Wnd Gst", "Flash Flood", "Flood"})
        self.assertTrue(all(p[2].rsplit("_", 1)[1] in ("new", "recent", "older") for p in pts))

    def test_query(self):
        self.assertIn("UPPER(descript) IN (", lsr.PARAMS["where"])
        for k in ("'TORNADO'", "'HAIL'", "'TSTM WND GST'", "'FLASH FLOOD'", "'FLOOD'", "'FUNNEL CLOUD'"):
            self.assertIn(k, lsr.PARAMS["where"])
        self.assertNotIn("SNOW", lsr.PARAMS["where"])
        self.assertEqual(lsr.PARAMS["f"], "geojson")
        self.assertTrue(lsr.URL.endswith("/nws_local_storm_reports/MapServer/0/query"))


class TestRules(unittest.TestCase):
    def test_kinds_whatever_the_case(self):
        self.assertEqual(one(feat("TORNADO", "", ""))[0][2], "tornado_sig_new")
        self.assertEqual(one(feat("Waterspout", "", ""))[0][2], "tornado_sig_new")
        self.assertEqual(one(feat("funnel cloud", "", ""))[0][2], "funnel_new")
        self.assertEqual(one(feat("Marine Hail"))[0][2], "hail_new")
        self.assertEqual(one(feat("Tstm Wnd Dmg", "", ""))[0][2], "wind_new")
        self.assertEqual(one(feat("Marine Tstm Wind", "50", "KTS"))[0][4], "58 mph (93 km/h)")
        self.assertEqual(one(feat("Snow", "3", "Inch")), [])
        self.assertEqual(one(feat("Non-Tstm Wnd Gst", "70", "MPH")), [])

    def test_significant(self):
        self.assertEqual(one(feat("Hail", "2.00"))[0][2], "hail_sig_new")
        self.assertEqual(one(feat("Hail", "1.99"))[0][2], "hail_new")
        self.assertEqual(one(feat("Tstm Wnd Gst", "75", "MPH"))[0][2], "wind_sig_new")
        self.assertEqual(one(feat("Tstm Wnd Gst", "74", "mph"))[0][2], "wind_new")
        self.assertEqual(one(feat("Tstm Wnd Gst", "65", "KTS"))[0][2], "wind_sig_new", "65 kt is 75 mph")
        self.assertEqual(one(feat("Tstm Wnd Gst", "64", "KT"))[0][2], "wind_new")
        self.assertEqual(one(feat("Flash Flood", "", " "))[0][2], "flash_flood_new")
        self.assertEqual(lsr.STYLES["tornado_sig_new"]["outline"], "#212121")
        self.assertGreater(lsr.STYLES["hail_sig_new"]["radius"], lsr.STYLES["hail_new"]["radius"])

    def test_magnitudes(self):
        self.assertEqual(lsr.magnitude("hail", "1.75", "Inch"), ("1.75 in (44 mm)", False))
        self.assertEqual(lsr.magnitude("hail", "", "Inch"), (None, False))
        self.assertEqual(lsr.magnitude("hail", "0", "Inch"), (None, False))
        self.assertEqual(lsr.magnitude("wind", "UNK", "MPH"), (None, False))
        self.assertEqual(lsr.magnitude("tornado", "", ""), (None, True))
        self.assertEqual(lsr.magnitude("flood", "2", "Ft"), ("2 Ft", False))
        self.assertEqual(lsr.magnitude("wind", "60", "furlongs"), ("60 furlongs", False))

    def test_ages(self):
        self.assertEqual(lsr.age_name(0), "new")
        self.assertEqual(lsr.age_name(3599), "new")
        self.assertEqual(lsr.age_name(3600), "recent")
        self.assertEqual(lsr.age_name(6 * 3600), "older")
        self.assertEqual(lsr.age_name(24 * 3600 - 1), "older")
        self.assertIsNone(lsr.age_name(24 * 3600))
        self.assertEqual(lsr.age_name(-599), "new", "a clock a little ahead")
        self.assertIsNone(lsr.age_name(-601))
        self.assertEqual(one(feat(when=NOW - timedelta(hours=25))), [])
        self.assertEqual(one(feat(when=NOW - timedelta(hours=7)))[0][2], "hail_older")

    def test_paler_with_age(self):
        self.assertEqual(lsr.STYLES["tornado_sig_new"]["color"], "#D50000")
        self.assertEqual(lsr.STYLES["tornado_sig_recent"]["color"], lsr._mix("#D50000", 0.4))
        self.assertEqual(lsr._mix("#000000", 0.5), "#808080")
        self.assertEqual(lsr._mix("#2E7D32", 0.0), "#2E7D32")
        labels = {s["label"] for s in lsr.STYLES.values()}
        self.assertIn("Tornado report, significant", labels)
        self.assertEqual(len(lsr.STYLES), 6 * 3 + 3 * 3, "significant forms for tornado, hail and wind only")

    def test_row_fields(self):
        r = one(feat(remarks="  Big hail.  ", loc_desc="", state="IL", wfo="", wfo_id="LOT", lon=-87.123456, lat=41.987654))[0]
        self.assertEqual((r[0], r[1], r[5], r[7], r[8]), (-87.1235, 41.9877, "IL", "LOT", "Big hail."))
        r = one(feat(remarks=" ", loc_desc="", state=""))[0]
        self.assertEqual((r[5], r[8]), (None, None))
        self.assertEqual(len(one(feat(remarks="x" * 900))[0][8]), 500)

    def test_bad_input(self):
        self.assertIsNone(lsr.points(None, NOW))
        self.assertIsNone(lsr.points({"features": "x"}, NOW))
        bad = [feat(lat=95), feat(lon=float("nan")), {"properties": {}}, "x", feat(), feat(lon=200)]
        bad[2]["geometry"] = None
        del bad[4]["properties"]["lsr_validtime"]
        self.assertEqual(lsr.points({"features": bad}, NOW), [])
        g = copy.deepcopy(feat())
        g["geometry"]["coordinates"] = []
        self.assertEqual(one(g), [])
        self.assertEqual([c["key"] for c in lsr.COLUMNS], ["type", "magnitude", "place", "time", "office", "remarks"])


if __name__ == "__main__":
    unittest.main()
