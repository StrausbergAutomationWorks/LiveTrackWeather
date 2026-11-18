"""Storm and winter reports (Weather SSOT items 312 and 353, contract D21): lsr.py.

Fixtures are NWS's own answers of 2026-11-18 ~08:0xZ (bin\\ltw312_lsr_probe*.py): the build's query on layer 0
(lsr_last24h_kinds_20261118.json, 12 reports) and the whole 72-hour layer (lsr_last72h_all_20261118.json, 216 reports
of every type). Winter: the Snow reports in that 72-hour fixture are NWS's own; the other winter types are
CONSTRUCTED with feat(), their spellings as IEM's archive of the NWS products writes them (bin\\ltw353_probe.py).
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


T72 = datetime(2026, 11, 18, 7, 51, tzinfo=timezone.utc)


def wone(f, now=NOW):
    return lsr.points({"type": "FeatureCollection", "features": [f]}, now, lsr.WINTER)


class TestWinterReal(unittest.TestCase):
    def test_snow_of_the_last_24_hours(self):
        pts = lsr.points(ALL72, T72, lsr.WINTER)
        self.assertEqual({p[3] for p in pts}, {"Snow"}, "only snow fell in those 72 hours")
        snow72 = [f for f in ALL72["features"] if f["properties"]["descript"] == "Snow"]
        in24 = [f for f in snow72 if (T72.timestamp() * 1000 - f["properties"]["lsr_validtime"]) < 24 * 3600 * 1000]
        self.assertEqual(len(pts), len(in24))
        self.assertGreater(len(snow72), len(in24), "the 72-hour layer holds older snow, left out")
        for p in pts:
            self.assertIn(p[2], lsr.WINTER.styles)
            self.assertTrue(p[2].startswith("snow_"))

    def test_montana_row(self):
        mt = next(p for p in lsr.points(ALL72, T72, lsr.WINTER) if p[4] == "5.9 in (15 cm)")
        self.assertEqual(mt[2], "snow_new")
        self.assertEqual(mt[6], "2026-11-18 07:30")
        self.assertTrue(mt[8].startswith("5.9 Inches snowfall since 6 PM Tuesday evening."))

    def test_the_sets_do_not_overlap(self):
        self.assertFalse(set(lsr.STORM.kinds) & set(lsr.WINTER.kinds))
        storm = lsr.points(ALL72, T72)
        winter = lsr.points(ALL72, T72, lsr.WINTER)
        self.assertFalse({p[3] for p in storm} & {p[3] for p in winter})


class TestWinterRules(unittest.TestCase):
    def test_kinds_whatever_the_case(self):
        cases = {"SNOW": "snow_new", "Heavy Snow": "snow_new", "snow squall": "snow_new", "Blizzard": "blizzard_new",
                 "SLEET": "sleet_new", "Heavy Sleet": "sleet_new", "Freezing Rain": "ice_new",
                 "FREEZING DRIZZLE": "ice_new", "Snow/Ice Dmg": "damage_new", "Extreme Cold": "cold_new",
                 "WIND CHILL": "cold_new", "Extr Wind Chill": "cold_new", "Freeze": "cold_new",
                 "Avalanche": "avalanche_new", "Ice Jam": "ice_jam_new", "ICE JAM FLOODING": "ice_jam_new"}
        for d, style in cases.items():
            self.assertEqual(wone(feat(d, "", ""))[0][2], style, d)
        self.assertEqual(wone(feat("Ice Storm", "", ""))[0][2], "ice_sig_new", "any ice storm is significant")
        for d in ("Hail", "Tornado", "Flood", "Rain", "Non-Tstm Wnd Gst", "Fog"):
            self.assertEqual(wone(feat(d, "1", "Inch")), [], d)

    def test_significant(self):
        self.assertEqual(wone(feat("Snow", "12.0", "Inch"))[0][2], "snow_sig_new")
        self.assertEqual(wone(feat("Snow", "11.9", "INCH"))[0][2], "snow_new")
        self.assertEqual(wone(feat("Heavy Snow", "15", "inch"))[0][2], "snow_sig_new")
        self.assertEqual(wone(feat("Sleet", "0.50", "Inch"))[0][2], "sleet_sig_new")
        self.assertEqual(wone(feat("Sleet", "0.49", "Inch"))[0][2], "sleet_new")
        self.assertEqual(wone(feat("Freezing Rain", "0.25", "Inch"))[0][2], "ice_sig_new")
        self.assertEqual(wone(feat("Freezing Rain", "0.24", "Inch"))[0][2], "ice_new")
        self.assertEqual(wone(feat("Ice Storm", "0.10", "Inch"))[0][2], "ice_sig_new")
        self.assertEqual(wone(feat("Extreme Cold", "-60", "F"))[0][2], "cold_new", "cold has no significant form")
        self.assertEqual(lsr.WINTER.styles["snow_sig_new"]["outline"], "#212121")
        self.assertGreater(lsr.WINTER.styles["ice_sig_new"]["radius"], lsr.WINTER.styles["ice_new"]["radius"])

    def test_magnitudes(self):
        self.assertEqual(lsr.magnitude("snow", "5.0", "Inch"), ("5.0 in (13 cm)", False))
        self.assertEqual(lsr.magnitude("snow", " ", "TInch"), ("trace", False))
        self.assertEqual(lsr.magnitude("ice", "", "TInch"), ("trace", False))
        self.assertEqual(lsr.magnitude("sleet", "0.25", "INCH"), ("0.25 in (6 mm)", False))
        self.assertEqual(lsr.magnitude("ice", "0.30", "inch"), ("0.30 in (8 mm)", True))
        self.assertEqual(lsr.magnitude("cold", "-25", "F"), ("-25 \u00b0F (-32 \u00b0C)", False))
        self.assertEqual(lsr.magnitude("cold", "0", "F"), ("0 \u00b0F (-18 \u00b0C)", False))
        self.assertEqual(lsr.magnitude("cold", "", "F"), (None, False))
        self.assertEqual(lsr.magnitude("cold", "-30", ""), (None, False), "below zero with no unit: not shown")
        self.assertEqual(lsr.magnitude("snow", "0", "Inch"), (None, False))
        self.assertEqual(lsr.magnitude("blizzard", "", ""), (None, False))
        self.assertEqual(lsr.magnitude("avalanche", "3", "Ft"), ("3 Ft", False))
        self.assertEqual(lsr.magnitude("snow", "4", "cm"), ("4 cm", False))
        self.assertEqual(lsr.magnitude("hail", "1", "TInch"), ("1 TInch", False), "trace is a winter rule")

    def test_styles(self):
        self.assertEqual(len(lsr.WINTER.styles), 8 * 3 + 3 * 3, "significant forms for snow, sleet and ice only")
        self.assertEqual(lsr.WINTER.styles["snow_new"]["color"], "#7B68EE")
        self.assertEqual(lsr.WINTER.styles["blizzard_new"]["radius"], 5)
        self.assertEqual(lsr.WINTER.styles["cold_older"]["color"], lsr._mix("#0000FF", 0.65))
        self.assertEqual(lsr.WINTER.styles["ice_sig_recent"]["label"], "Freezing rain or ice report, significant")
        self.assertIs(lsr.STYLES, lsr.STORM.styles)
        for name, s in lsr.WINTER.styles.items():
            self.assertIn("outline", s, name)
            self.assertEqual(s["outline"], "#212121" if "_sig_" in name else "#424242", name)
        for name, s in lsr.STORM.styles.items():
            self.assertEqual("outline" in s, "_sig_" in name, name)
        self.assertEqual(lsr.WINTER.outline, "#424242")
        self.assertIsNone(lsr.STORM.outline)
        self.assertEqual(lsr._styles({"k": ("#000000", "K", 4, 4)}, "#ABCDEF")["k_older"]["outline"], "#ABCDEF")
        self.assertEqual(len(lsr.STYLES), 6 * 3 + 3 * 3)

    def test_ages(self):
        self.assertEqual(wone(feat("Snow", "2", "Inch", when=NOW - timedelta(hours=25))), [])
        self.assertEqual(wone(feat("Snow", "2", "Inch", when=NOW - timedelta(hours=2)))[0][2], "snow_recent")


class TestQueryAndPages(unittest.TestCase):
    def test_queries(self):
        for rs, other in ((lsr.STORM, "'SNOW'"), (lsr.WINTER, "'TORNADO'")):
            p = rs.params
            self.assertTrue(p["where"].startswith("UPPER(descript) IN ("))
            self.assertNotIn(other, p["where"])
            self.assertEqual(p["orderByFields"], "lsr_validtime DESC,objectid")
            self.assertEqual(p["resultRecordCount"], 2000)
            self.assertEqual(p["f"], "geojson")
        for k in ("'SNOW'", "'ICE STORM'", "'SNOW/ICE DMG'", "'EXTR WIND CHILL'", "'AVALANCHE'", "'ICE JAM FLOODING'"):
            self.assertIn(k, lsr.WINTER.params["where"])
        self.assertIs(lsr.PARAMS, lsr.STORM.params)
        self.assertEqual((lsr.STORM.key, lsr.WINTER.key), ("storm_reports", "winter_reports"))
        self.assertTrue(lsr.WINTER.attribution.startswith("Winter reports: NWS Local Storm Reports"))
        self.assertEqual(lsr.MAX_PAGES, 10)

    def test_more(self):
        self.assertTrue(lsr.more({"type": "FeatureCollection", "exceededTransferLimit": True, "features": []}))
        self.assertTrue(lsr.more({"properties": {"exceededTransferLimit": True}, "features": []}))
        self.assertFalse(lsr.more({"type": "FeatureCollection", "features": []}))
        self.assertFalse(lsr.more({"exceededTransferLimit": "true"}))
        self.assertFalse(lsr.more({"properties": "x"}))
        self.assertFalse(lsr.more(None))

    def test_merge(self):
        a, b = feat("Snow", "1", "Inch"), feat("Sleet", "0.1", "Inch")
        m = lsr.merge([{"features": [a]}, {"features": [b]}, {"features": "x"}, None])
        self.assertEqual(m, {"type": "FeatureCollection", "features": [a, b]})
        self.assertEqual(len(lsr.points(m, NOW, lsr.WINTER)), 2)


if __name__ == "__main__":
    unittest.main()
