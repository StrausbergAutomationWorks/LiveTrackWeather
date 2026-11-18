"""Elevation and depth worldwide (Weather SSOT item 352 step 4b): elevation.py.

Fixtures are the sources' own answers, saved by bin\\ltw352e_world_probe2.py, _probe3.py and bin\\ltw352b_probe4.py on
2026-11-18 (elev_*_20261118.*, epqs_*_20261118.json). Expected values are what those answers say (printed by
bin\\ltw352b_fixtures.py), and agree with 20_Research/REPORT_elevation_world_20261117.md.
"""

import json
import unittest

from _load import FIXTURES, load

el = load("elevation")
us = load("usgs")

P = {"chicago_loop": (41.8789, -87.6359), "toronto": (43.6532, -79.3832), "lake_michigan_mid": (42.5, -87.0),
     "gulf_offshore": (27.0, -90.0), "oslofjord": (59.85, 10.62), "north_sea": (56.0, 3.0),
     "atlantic_open": (40.0, -40.0), "jericho_land": (31.856, 35.46)}


def fx(kind, name):
    return json.loads((FIXTURES / f"elev_{kind}_{name}_20261118.json").read_text(encoding="utf-8"))


def noaa(name):
    return el.parse_noaa(fx("noaa", name))


def epqs(name):
    got = us.parse_elevation(json.loads((FIXTURES / f"epqs_{name}_20261118.json").read_text(encoding="utf-8")))
    return {**got, "source": el.SRC_3DEP}


def terrain(name):
    lat, lon = P[name]
    x, y, px, py = el.terrain_tile(lat, lon)
    return el.terrain_record(el.decode_terrarium((FIXTURES / f"elev_terrain15_{name}_20261118.png").read_bytes(), px, py))


class TestSources(unittest.TestCase):
    def test_nrcan(self):
        self.assertEqual(el.parse_nrcan(fx("nrcan", "toronto")), {"m": 90.0, "resolution_m": None, "source": "nrcan_cdem"})
        self.assertIsNone(el.parse_nrcan(fx("nrcan", "chicago_loop")), "null outside Canada")
        self.assertEqual(el.parse_nrcan(fx("nrcan", "halifax_harbour"))["m"], 0.0, "0 on the sea is a value")
        self.assertEqual(el.parse_nrcan(fx("nrcan", "lake_ontario"))["m"], 75.0, "a lake's surface")
        for bad in (None, [], {}, {"altitude": "x"}, {"altitude": True}, {"altitude": float("nan")}):
            self.assertIsNone(el.parse_nrcan(bad), bad)

    def test_kartverket(self):
        self.assertEqual(el.parse_kartverket(fx("kartverket", "oslo")),
                         {"m": 4.9, "resolution_m": 1.0, "source": "kartverket", "water": False})
        fjord = el.parse_kartverket(fx("kartverket", "oslofjord"))
        self.assertEqual((fjord["m"], fjord["water"], fjord["resolution_m"]), (-37.8, True, None))
        self.assertIsNone(el.parse_kartverket(fx("kartverket", "longyearbyen")), "Svalbard: null")
        self.assertIsNone(el.parse_kartverket(fx("kartverket", "stockholm")), "Sweden: null")
        self.assertEqual(el.parse_kartverket(fx("kartverket", "lindesnes"))["m"], 15.2)
        for bad in (None, {}, {"punkter": []}, {"punkter": [None]}, {"punkter": [{"z": None}]}):
            self.assertIsNone(el.parse_kartverket(bad), bad)
        # constructed: land just below sea level is not the sea; only `terreng` "Havflate" is
        low = el.parse_kartverket({"punkter": [{"datakilde": "dtm1", "terreng": "Myr", "z": -0.5}]})
        self.assertEqual((low["m"], low["water"]), (-0.5, False))

    def test_rounding_and_no_data(self):
        self.assertEqual(el.parse_nrcan({"altitude": 90.04321})["m"], 90.0)
        self.assertEqual(el.parse_kartverket({"punkter": [{"z": 4.94321}]})["m"], 4.9)
        self.assertEqual(el.parse_noaa({"value": "-153.6321"}), -153.6)
        # no-data markers (-32767, -32768, float32's lowest) are not elevations
        self.assertIsNone(el.parse_nrcan({"altitude": -32767}))
        self.assertIsNone(el.parse_kartverket({"punkter": [{"z": -32768}]}))
        self.assertIsNone(el.parse_noaa({"value": "-3.4028235e+38"}))
        self.assertEqual(el.parse_noaa({"value": "-10994"}), -10994.0, "the Challenger Deep is a value")

    def test_noaa(self):
        self.assertEqual(noaa("lake_michigan_mid"), -153.6, "depth below the lake")
        self.assertEqual(noaa("gulf_offshore"), -2416.7)
        self.assertEqual(noaa("chicago_loop"), 190.4)
        self.assertIsNone(el.parse_noaa({"error": {"code": 400}, "value": "1"}))
        self.assertIsNone(el.parse_noaa({"value": "NoData"}))
        self.assertIsNone(el.parse_noaa(None))

    def test_params(self):
        self.assertEqual(el.nrcan_params(43.65321, -79.38321), {"lat": "43.6532", "lon": "-79.3832"})
        self.assertEqual(el.kartverket_params(59.91391, 10.75221),
                         {"nord": "59.9139", "ost": "10.7522", "koordsys": "4258", "geojson": "false"})
        q = el.noaa_params(42.5, -87.0)
        self.assertEqual(json.loads(q["geometry"]), {"x": -87.0, "y": 42.5, "spatialReference": {"wkid": 4326}})
        self.assertEqual((q["geometryType"], q["returnCatalogItems"], q["f"]), ("esriGeometryPoint", "false", "json"))
        self.assertIn('"x":-87.0000', q["geometry"], "4 decimals")
        self.assertEqual(el.terrain_url(8407, 12178), "https://s3.amazonaws.com/elevation-tiles-prod/terrarium/15/8407/12178.png")

    def test_boxes(self):
        for lat, lon in ((57.983, 7.048), (71.17, 25.78), (70.37, 31.1), (59.306, 4.885), (59.9139, 10.7522)):
            self.assertTrue(el.in_kartverket_box(lat, lon), (lat, lon))
        for lat, lon in ((78.2232, 15.6267), (55.7, 12.6), (41.88, -87.64), (59.9, 3.9)):
            self.assertFalse(el.in_kartverket_box(lat, lon), (lat, lon))
        for lat, lon in ((43.6532, -79.3832), (60.7212, -135.0568), (63.7467, -68.517), (44.64, -63.55)):
            self.assertTrue(el.in_canada_box(lat, lon), (lat, lon))
        for lat, lon in ((59.9139, 10.7522), (51.5, -0.1), (27.0, -90.0), (21.3, -157.8)):
            self.assertFalse(el.in_canada_box(lat, lon), (lat, lon))


class TestTerrain(unittest.TestCase):
    def test_measured_places(self):
        want = {"chicago_loop": 181.1, "toronto": 89.8, "lake_michigan_mid": 175.9, "gulf_offshore": -2409.0,
                "oslofjord": 0.0, "north_sea": -74.0, "atlantic_open": 0.0, "jericho_land": -249.9}
        for name, m in want.items():
            self.assertEqual(terrain(name)["m"], m, name)
            self.assertEqual(terrain(name)["source"], "aws_terrain_tiles")

    def test_tile_and_pixel(self):
        self.assertEqual(el.terrain_tile(41.8789, -87.6359), (8407, 12178, 47, 219))
        self.assertEqual(el.terrain_tile(40.0, -40.0), (12743, 12405, 28, 72))
        x, y, px, py = el.terrain_tile(89.9, 180.0)
        self.assertTrue(0 <= x < 2 ** 15 and 0 <= y < 2 ** 15 and 0 <= px < 256 and 0 <= py < 256, "clamped")
        x, y, px, py = el.terrain_tile(-89.9, -180.0)
        self.assertTrue(0 <= x < 2 ** 15 and 0 <= y < 2 ** 15 and 0 <= px < 256 and 0 <= py < 256)

    def test_decode(self):
        import io
        from PIL import Image
        buf = io.BytesIO()
        Image.new("RGB", (256, 256), (128, 0, 0)).save(buf, "PNG")
        self.assertEqual(el.decode_terrarium(buf.getvalue(), 5, 5), 0.0, "R 128 is sea level")
        buf = io.BytesIO()
        Image.new("RGB", (256, 256), (128, 181, 25)).save(buf, "PNG")
        self.assertEqual(el.decode_terrarium(buf.getvalue(), 255, 255), 181.1, "B/256 is the decimals")
        small = io.BytesIO()
        Image.new("RGB", (512, 512), (128, 0, 0)).save(small, "PNG")
        self.assertIsNone(el.decode_terrarium(small.getvalue(), 5, 5), "not a 256-pixel tile")
        self.assertIsNone(el.decode_terrarium(b"<html>no</html>", 5, 5))
        self.assertIsNone(el.terrain_record(None))


def decide(land, noaa_m=None, noaa_ok=True, sea=None, sea_ok=False, gn=False):
    return el.decide(land, noaa_m, noaa_ok, sea, sea_ok, gn)


class TestDecide(unittest.TestCase):
    def test_us_land_and_great_lakes(self):
        d = decide(epqs("chicago_loop"), noaa("chicago_loop"))
        self.assertEqual((d["m"], d["on_water"], d["depth_m"], d["depth_reason"]), (181.2, False, None, "not on water"))
        lm = decide(epqs("lake_michigan_mid"), noaa("lake_michigan_mid"))
        self.assertEqual((lm["m"], lm["on_water"], lm["depth_m"], lm["depth_source"]), (175.9, True, 153.6, "noaa_ncei"),
                         "on a lake the elevation is its surface")

    def test_measured_us_and_canada(self):
        pac = decide(epqs("pacific_off_ca"), noaa("pacific_off_ca"))
        self.assertEqual((pac["m"], pac["on_water"], pac["depth_m"]), (0.0, True, 2007.0))
        dv = decide(epqs("death_valley"), noaa("death_valley"))
        self.assertEqual((dv["m"], dv["on_water"], dv["depth_m"]), (-84.7, False, None), "below sea level, still land")
        lo = decide(el.parse_nrcan(fx("nrcan", "lake_ontario")), noaa("lake_ontario"))
        self.assertEqual((lo["on_water"], lo["depth_m"], lo["source"]), (True, 149.6, "nrcan_cdem"))
        hx = decide(el.parse_nrcan(fx("nrcan", "halifax_harbour")), -21.0)   # NOAA's -21 at Halifax: the report's 4.4
        self.assertEqual((hx["m"], hx["on_water"], hx["depth_m"]), (0.0, True, 21.0))

    def test_rivers_read_as_land(self):
        # MEASURED limitation (bin\ltw352b_probe4.txt): NOAA has no depth on rivers, so they stay land.
        for name in ("mississippi_stl", "hudson_nyc"):
            self.assertFalse(decide(epqs(name), noaa(name))["on_water"], name)

    def test_margin(self):
        land = {"m": 0.0, "resolution_m": None, "source": "usgs_3dep"}
        self.assertTrue(decide(land, -5.0)["on_water"], "exactly 5 m below")
        self.assertFalse(decide(land, -4.9)["on_water"])
        self.assertFalse(decide({**land, "m": -100.0}, -1.0)["on_water"])
        self.assertFalse(decide({**land, "m": 10.0}, 2.0)["on_water"], "NOAA must be negative")
        self.assertTrue(el.water_by_noaa(3.0, -2.0))
        self.assertIsNone(el.water_by_noaa(None, -2.0))
        self.assertIsNone(el.water_by_noaa(3.0, None))

    def test_noaa_failed_after_3dep(self):
        d = decide({"m": 175.9, "resolution_m": None, "source": "usgs_3dep"}, None, noaa_ok=False)
        self.assertEqual((d["m"], d["on_water"], d["depth_m"]), (175.9, None, None))
        self.assertEqual(d["depth_reason"], "NOAA's depth service did not answer")
        self.assertEqual(decide({"m": 1.0, "resolution_m": None, "source": "nrcan_cdem"}, None)["depth_reason"],
                         "NOAA has no value here")

    def test_norway(self):
        fj = decide(el.parse_kartverket(fx("kartverket", "oslofjord")), sea="Skagerrak", sea_ok=True, gn=True)
        self.assertEqual((fj["m"], fj["on_water"], fj["depth_m"], fj["depth_source"], fj["sea"]),
                         (0.0, True, 37.8, "kartverket", "Skagerrak"), "Kartverket's z on the sea IS the depth")
        oslo = decide(el.parse_kartverket(fx("kartverket", "oslo")), noaa("oslofjord"))
        self.assertEqual((oslo["m"], oslo["on_water"], oslo["resolution_m"]), (4.9, False, 1.0), "NOAA not used")
        dry = decide({"m": 3.0, "resolution_m": None, "source": "kartverket", "water": True})
        self.assertEqual((dry["on_water"], dry["depth_m"], dry["depth_reason"]), (True, None, "Kartverket gives no depth here"))

    def test_terrain_only_needs_geonames(self):
        ns = terrain("north_sea")
        d = decide(ns, None)
        self.assertEqual((d["m"], d["on_water"], d["depth_m"]), (-74.0, None, None))
        self.assertIn("GeoNames username", d["depth_reason"])
        d = decide(ns, None, sea=None, sea_ok=False, gn=True)
        self.assertEqual((d["on_water"], d["depth_reason"]), (None, "GeoNames did not answer"))
        d = decide(ns, noaa("north_sea"), sea="North Sea", sea_ok=True, gn=True)
        self.assertEqual((d["m"], d["on_water"], d["depth_m"], d["depth_source"], d["sea"]),
                         (0.0, True, 73.0, "noaa_ncei", "North Sea"), "the sea floor is not the elevation")
        d = decide(ns, None, noaa_ok=False, sea="North Sea", sea_ok=True, gn=True)
        self.assertEqual((d["on_water"], d["depth_m"], d["depth_reason"]), (True, None, "NOAA's depth service did not answer"))
        d = decide(ns, 2.0, sea="North Sea", sea_ok=True, gn=True)
        self.assertEqual((d["on_water"], d["depth_m"], d["depth_reason"]), (True, None, "NOAA has no depth here"))

    def test_terrain_only_land_is_never_water_by_noaa(self):
        # MEASURED: the approved NOAA rule would call these water (Lee 2026-11-18: GeoNames decides here instead).
        jer = terrain("jericho_land")
        self.assertTrue(el.water_by_noaa(jer["m"], noaa("jericho_land")), "the rule's measured failure")
        self.assertIsNone(decide(jer, noaa("jericho_land"))["on_water"])
        d = decide(jer, None, sea=None, sea_ok=True, gn=True)
        self.assertEqual((d["m"], d["on_water"], d["depth_reason"]), (-249.9, False, "not on water"))
        kirkenes = {"m": 8.9, "resolution_m": None, "source": "aws_terrain_tiles"}
        self.assertTrue(el.water_by_noaa(8.9, noaa("kirkenes")))
        self.assertIsNone(decide(kirkenes, noaa("kirkenes"))["on_water"])
        self.assertFalse(el.needs_noaa(kirkenes), "NOAA is not asked after Terrain Tiles until GeoNames finds a sea")
        self.assertTrue(el.needs_noaa(epqs("pacific_off_ca")))
        self.assertTrue(el.needs_noaa({"m": 1.0, "resolution_m": None, "source": "nrcan_cdem"}))
        self.assertFalse(el.needs_noaa(el.parse_kartverket(fx("kartverket", "oslo"))))
        self.assertFalse(el.needs_noaa(None))

    def test_open_ocean_by_terrain(self):
        d = decide(terrain("atlantic_open"), noaa("atlantic_open"), sea="North Atlantic Ocean", sea_ok=True, gn=True)
        self.assertEqual((d["m"], d["depth_m"]), (0.0, 4644.0))

    def test_nothing_answered(self):
        d = decide(None)
        self.assertEqual((d["m"], d["on_water"], d["source"]), (None, None, None))
        self.assertEqual(d["reason"], "no elevation source answered here")
        self.assertEqual(set(d), {"m", "resolution_m", "source", "on_water", "reason", "depth_m", "depth_source",
                                  "depth_reason", "sea"})

    def test_attribution(self):
        for src in ("usgs_3dep", "nrcan_cdem", "kartverket", "aws_terrain_tiles"):
            self.assertTrue(el.ATTRIBUTION[src].startswith("Elevation: "), src)
        self.assertIn("Mapzen", el.ATTRIBUTION["aws_terrain_tiles"])
        self.assertEqual(set(el.DEPTH_ATTRIBUTION), {"noaa_ncei", "kartverket"})


class Fake:
    """Sources for run_chain: each name -> (answered, value); records what was asked, in order."""

    def __init__(self, **answers):
        self.answers = answers
        self.asked = []

    def __getattr__(self, name):
        async def ask(lat, lon):
            self.asked.append(name)
            return self.answers.get(name, (True, None))
        return ask

    def run(self, lat, lon, gn=False):
        import asyncio
        return asyncio.run(el.run_chain(lat, lon, epqs=self.epqs, nrcan=self.nrcan, kartverket=self.kartverket,
                                        terrain=self.terrain, noaa=self.noaa, sea=self.sea, has_geonames=gn))


OSLO, OSLOFJORD, TORONTO, CHICAGO, NORTH_SEA, JERICHO = ((59.9139, 10.7522), (59.85, 10.62), (43.6532, -79.3832),
                                                         (41.8789, -87.6359), (56.0, 3.0), (31.856, 35.46))


class TestChain(unittest.TestCase):
    def test_us_land(self):
        f = Fake(epqs=(True, epqs("chicago_loop")), noaa=(True, noaa("chicago_loop")))
        got, failed = f.run(*CHICAGO, gn=True)
        self.assertEqual(f.asked, ["epqs", "noaa"], "3DEP answered: nothing else, and GeoNames only on water")
        self.assertEqual((got["m"], got["source"], got["on_water"], failed), (181.2, "usgs_3dep", False, False))

    def test_great_lake_asks_the_sea_name_with_geonames(self):
        f = Fake(epqs=(True, epqs("lake_michigan_mid")), noaa=(True, noaa("lake_michigan_mid")), sea=(True, None))
        got, _ = f.run(42.5, -87.0, gn=True)
        self.assertEqual(f.asked, ["epqs", "noaa", "sea"])
        self.assertEqual((got["on_water"], got["depth_m"], got["sea"]), (True, 153.6, None))
        f = Fake(epqs=(True, epqs("lake_michigan_mid")), noaa=(True, noaa("lake_michigan_mid")))
        f.run(42.5, -87.0, gn=False)
        self.assertEqual(f.asked, ["epqs", "noaa"], "no username: GeoNames never asked")

    def test_canada(self):
        f = Fake(nrcan=(True, el.parse_nrcan(fx("nrcan", "toronto"))), noaa=(True, 80.0))
        got, failed = f.run(*TORONTO)
        self.assertEqual(f.asked, ["epqs", "nrcan", "noaa"])
        self.assertEqual((got["m"], got["source"], failed), (90.0, "nrcan_cdem", False))

    def test_norway(self):
        f = Fake(kartverket=(True, el.parse_kartverket(fx("kartverket", "oslofjord"))), sea=(True, "Skagerrak"))
        got, _ = f.run(*OSLOFJORD, gn=True)
        self.assertEqual(f.asked, ["epqs", "kartverket", "sea"], "Canada's box skipped, NOAA not asked in Norway")
        self.assertEqual((got["m"], got["depth_m"], got["depth_source"], got["sea"]), (0.0, 37.8, "kartverket", "Skagerrak"))
        f = Fake(kartverket=(True, el.parse_kartverket(fx("kartverket", "oslo"))))
        got, _ = f.run(*OSLO, gn=True)
        self.assertEqual(f.asked, ["epqs", "kartverket"])

    def test_elsewhere_terrain_and_geonames(self):
        f = Fake(terrain=(True, terrain("north_sea")), sea=(True, "North Sea"), noaa=(True, noaa("north_sea")))
        got, failed = f.run(*NORTH_SEA, gn=True)
        self.assertEqual(f.asked, ["epqs", "terrain", "sea", "noaa"], "neither box; NOAA only after GeoNames says sea")
        self.assertEqual((got["m"], got["on_water"], got["depth_m"], failed), (0.0, True, 73.0, False))
        f = Fake(terrain=(True, terrain("jericho_land")), sea=(True, None))
        got, _ = f.run(*JERICHO, gn=True)
        self.assertEqual(f.asked, ["epqs", "terrain", "sea"])
        self.assertEqual((got["m"], got["on_water"]), (-249.9, False))
        f = Fake(terrain=(True, terrain("north_sea")))
        got, failed = f.run(*NORTH_SEA, gn=False)
        self.assertEqual(f.asked, ["epqs", "terrain"])
        self.assertEqual((got["on_water"], failed), (None, False))

    def test_geonames_failure_does_not_fail_the_check(self):
        f = Fake(terrain=(True, terrain("north_sea")), sea=(False, None))
        got, failed = f.run(*NORTH_SEA, gn=True)
        self.assertEqual((got["on_water"], got["depth_reason"], failed), (None, "GeoNames did not answer", False))

    def test_failures(self):
        f = Fake(epqs=(False, None), terrain=(True, terrain("north_sea")))
        got, failed = f.run(*NORTH_SEA)
        self.assertEqual(f.asked, ["epqs", "terrain"], "3DEP down: the chain goes on")
        self.assertEqual((got["source"], failed), ("aws_terrain_tiles", True), "and asks again after the gap")
        f = Fake(epqs=(False, None), terrain=(False, None))
        self.assertEqual(f.run(*NORTH_SEA), (None, True), "nothing answered: keep what was shown")
        f = Fake(epqs=(True, None), terrain=(True, None))
        got, failed = f.run(*NORTH_SEA)
        self.assertEqual((got["reason"], failed), ("no elevation source answered here", False))
        f = Fake(epqs=(True, epqs("chicago_loop")), noaa=(False, None))
        got, failed = f.run(*CHICAGO)
        self.assertEqual((got["m"], got["on_water"], failed), (181.2, None, True), "NOAA down: asked again later")
        f = Fake(epqs=(True, None), nrcan=(False, None), terrain=(True, terrain("toronto")), noaa=(True, 80.0))
        got, failed = f.run(*TORONTO)
        self.assertEqual(f.asked, ["epqs", "nrcan", "terrain"])
        self.assertTrue(failed)
        f = Fake(epqs=(True, None), kartverket=(False, None), terrain=(True, terrain("oslofjord")))
        _got, failed = f.run(*OSLO)
        self.assertEqual(f.asked, ["epqs", "kartverket", "terrain"])
        self.assertTrue(failed)


if __name__ == "__main__":
    unittest.main()
