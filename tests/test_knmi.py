"""The KNMI relay's HA-free parts (Weather SSOT item 278, contract D13 "Relays").

Fixtures are KNMI's own answers of 2026-10-29 00:15Z (bin\\ltw278_fixtures.py): the capabilities and the
relay's picture in KNMI_STYLE. The cut was checked against KNMI's own zoom-9 tiles there: identical.
"""

import io
import math
import unittest

from PIL import Image

from _load import FIXTURES, load

knmi = load("knmi")
const = load("const")


def png(im):
    buf = io.BytesIO()
    im.save(buf, "PNG")
    return buf.getvalue()


class TestArea(unittest.TestCase):
    def test_tiles_per_zoom(self):
        self.assertEqual(len(knmi.tiles_at(9)), 80)
        self.assertEqual(len(knmi.tiles_at(8)), 12)
        self.assertEqual(len(knmi.tiles_at(7)), 2)
        self.assertEqual(knmi.tiles_at(6), [])
        self.assertEqual(knmi.tiles_at(10), [])
        self.assertEqual(knmi.tiles_at(7), [(65, 41), (65, 42)])
        self.assertIn((259, 163), knmi.tiles_at(9))
        self.assertIn((266, 172), knmi.tiles_at(9))
        self.assertNotIn((267, 172), knmi.tiles_at(9))
        self.assertNotIn((259, 173), knmi.tiles_at(9))

    def test_every_lower_tile_is_made_of_native_tiles(self):
        native = set(knmi.tiles_at(9))
        for z in (7, 8):
            f = 2 ** (9 - z)
            for x, y in knmi.tiles_at(z):
                for dx in range(f):
                    for dy in range(f):
                        self.assertIn((x * f + dx, y * f + dy), native)

    def test_bounds_are_the_native_tile_edges(self):
        w, s, e, n = knmi.bounds()
        self.assertAlmostEqual(w, 2.109375)
        self.assertAlmostEqual(e, 7.734375)
        # Web Mercator: the top edge of zoom-9 row 163, the bottom edge of row 172
        top = math.degrees(2 * math.atan(math.exp(math.pi * (1 - 2 * 163 / 512))) - math.pi / 2)
        bottom = math.degrees(2 * math.atan(math.exp(math.pi * (1 - 2 * 173 / 512))) - math.pi / 2)
        self.assertAlmostEqual(n, top, places=5)
        self.assertAlmostEqual(s, bottom, places=5)
        self.assertAlmostEqual(n, 54.572, places=3)
        self.assertAlmostEqual(s, 50.289, places=3)
        # inside the rectangle measured inside KNMI's radar disc (1.58-8.41 E, 50.05-54.87 N)
        self.assertTrue(1.58 <= w and e <= 8.41 and 50.05 <= s and n <= 54.87)

    def test_picture(self):
        self.assertEqual(knmi.picture_size(), (2048, 2560))
        minx, miny, maxx, maxy = map(float, knmi.picture_bbox().split(","))
        self.assertAlmostEqual(minx, 2.109375 * 20037508.342789244 / 180, places=2)
        self.assertAlmostEqual(maxx, 7.734375 * 20037508.342789244 / 180, places=2)
        w = 2 * 20037508.342789244 / 512
        self.assertAlmostEqual((maxx - minx) / w, 8, places=6)
        self.assertAlmostEqual((maxy - miny) / w, 10, places=6)
        p = knmi.picture_params("precipitation", "s/x", "2026-10-29T00:15:00Z")
        self.assertEqual((p["REQUEST"], p["CRS"], p["WIDTH"], p["HEIGHT"], p["TIME"], p["STYLES"], p["LAYERS"]),
                         ("GetMap", "EPSG:3857", "2048", "2560", "2026-10-29T00:15:00Z", "s/x", "precipitation"))
        self.assertEqual(p["FORMAT"], "image/png")
        self.assertEqual(p["TRANSPARENT"], "TRUE")


class TestCapabilities(unittest.TestCase):
    caps = (FIXTURES / "knmi_caps.xml").read_bytes()

    def test_newest(self):
        self.assertEqual(knmi.newest_frame(self.caps, "precipitation"), "2026-10-29T00:15:00Z")
        self.assertEqual(knmi.newest_frame(self.caps, "Reflectivity"), "2026-10-29T00:15:00Z")
        self.assertEqual(knmi.frame_key("2026-10-29T00:15:00Z"), "202610290015")
        self.assertTrue(knmi.FRAME_RE.match("202610290015"))
        self.assertFalse(knmi.FRAME_RE.match("20261029001"))
        self.assertFalse(knmi.FRAME_RE.match("2026102900155"))

    def test_missing_or_bad(self):
        self.assertIsNone(knmi.newest_frame(self.caps, "nope"))
        self.assertIsNone(knmi.newest_frame(None, "precipitation"))
        self.assertIsNone(knmi.newest_frame(b"", "precipitation"))
        self.assertIsNone(knmi.newest_frame(b"<not xml", "precipitation"))
        bad = self.caps.replace(b'default="2026-10-29T00:15:00Z"', b'default="soon"')
        self.assertIsNone(knmi.newest_frame(bad, "precipitation"))
        self.assertEqual(const.KNMI_LAYER, "precipitation")

    def test_only_the_time_dimension(self):
        other = (b'<Dimension name="reference_time" units="ISO8601" default="2026-10-28T12:00:00Z">'
                 b'2026-10-28T12:00:00Z</Dimension>\n')
        anchor = b'<Dimension name="time" units="ISO8601" default="2026-10-29T00:15:00Z"'
        self.assertEqual(self.caps.count(anchor), 2)
        doc = self.caps.replace(anchor, other + anchor)
        self.assertEqual(knmi.newest_frame(doc, "precipitation"), "2026-10-29T00:15:00Z")


class TestCut(unittest.TestCase):
    def test_real_picture(self):
        tiles = knmi.cut((FIXTURES / "knmi_picture.png").read_bytes())
        self.assertEqual(len(tiles), 94)
        self.assertEqual(sorted({k[0] for k in tiles}), [7, 8, 9])
        drawn = [k for k, v in tiles.items() if v is not knmi.EMPTY_PNG]
        self.assertEqual(len(drawn), 18)
        for k, v in tiles.items():
            im = Image.open(io.BytesIO(v))
            self.assertEqual(im.size, (256, 256), k)

    def test_where_a_pixel_lands(self):
        w, h = knmi.picture_size()
        im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        # one opaque 8x8 block at zoom-9 pixels (3 * 256 + 8 .. +15, 4 * 256 + 16 .. +23): tile 9/262/167
        for dx in range(8):
            for dy in range(8):
                im.putpixel((3 * 256 + 8 + dx, 4 * 256 + 16 + dy), (200, 30, 40, 255))
        tiles = knmi.cut(png(im))
        t9 = Image.open(io.BytesIO(tiles[(9, 262, 167)])).convert("RGBA")
        self.assertEqual(t9.getpixel((8, 16)), (200, 30, 40, 255))
        self.assertEqual(t9.getpixel((15, 23)), (200, 30, 40, 255))
        self.assertEqual(t9.getpixel((16, 16))[3], 0)
        self.assertEqual(t9.getpixel((8, 15))[3], 0)
        # zoom 8: 262/167 is the left, lower child of 131/83 -> local (8, 256 + 16) halved = (4, 136)
        t8 = Image.open(io.BytesIO(tiles[(8, 131, 83)])).convert("RGBA")
        self.assertEqual(t8.getpixel((4, 136)), (200, 30, 40, 255))
        self.assertEqual(t8.getpixel((7, 139)), (200, 30, 40, 255))
        self.assertEqual(t8.getpixel((8, 136))[3], 0)
        # zoom 7: 65/41 holds 9/260..263, 164..167 -> local (2*256 + 8, 3*256 + 16) quartered = (130, 196)
        t7 = Image.open(io.BytesIO(tiles[(7, 65, 41)])).convert("RGBA")
        self.assertEqual(t7.getpixel((130, 196)), (200, 30, 40, 255))
        self.assertEqual(t7.getpixel((131, 197)), (200, 30, 40, 255))
        self.assertEqual(t7.getpixel((132, 196))[3], 0)
        empty = [k for k, v in tiles.items() if v is knmi.EMPTY_PNG]
        self.assertEqual(len(empty), 91)

    def test_box_filter_keeps_faint_echo(self):
        w, h = knmi.picture_size()
        im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        im.putpixel((0, 0), (10, 20, 30, 255))
        tiles = knmi.cut(png(im))
        self.assertIsNot(tiles[(9, 259, 163)], knmi.EMPTY_PNG)
        self.assertIs(tiles[(8, 130, 82)], knmi.EMPTY_PNG)  # 259 is not in zoom 8's tiles' children
        # a pixel inside a zoom-8 tile's block survives as a faint pixel
        im.putpixel((256, 256), (10, 20, 30, 255))
        t8 = Image.open(io.BytesIO(knmi.cut(png(im))[(8, 130, 82)])).convert("RGBA")
        self.assertGreater(t8.getpixel((0, 0))[3], 0)
        self.assertLess(t8.getpixel((0, 0))[3], 255)

    def test_wrong_picture(self):
        with self.assertRaises(ValueError):
            knmi.cut(png(Image.new("RGBA", (2048, 2559))))
        with self.assertRaises(OSError):
            knmi.cut(b"<ServiceExceptionReport/>")

    def test_empty_png(self):
        im = Image.open(io.BytesIO(knmi.EMPTY_PNG)).convert("RGBA")
        self.assertEqual(im.size, (256, 256))
        self.assertIsNone(im.getchannel("A").getbbox())


class TestRelayAttribute(unittest.TestCase):
    def test_usable(self):
        a = knmi.relay_attribute("202610290015", "2026-10-29T00:15:00Z", True, "/api/x/knmi", "credit", "knmi")
        self.assertEqual(a, {"id": "knmi", "tiles": "/api/x/knmi/202610290015/{z}/{x}/{y}.png",
                             "bounds": knmi.bounds(), "max_native_zoom": 9, "attribution": "credit",
                             "time": "2026-10-29T00:15:00Z"})

    def test_unusable_drops_time_only(self):
        a = knmi.relay_attribute("202610290015", "2026-10-29T00:15:00Z", False, "/p", "c", "knmi")
        self.assertNotIn("time", a)
        self.assertEqual(a["tiles"], "/p/202610290015/{z}/{x}/{y}.png")

    def test_nothing_before_a_frame(self):
        self.assertIsNone(knmi.relay_attribute(None, None, True, "/p", "c", "knmi"))
        self.assertIsNone(knmi.relay_attribute("x", None, True, "/p", "c", "knmi"))

    def test_constants(self):
        self.assertEqual(const.KNMI_TILE_PATH, "/api/live_track_weather/radar/knmi")
        self.assertEqual(const.KNMI_ATTRIBUTION, "Radar: KNMI, CC BY 4.0, modified")
        self.assertEqual(const.KNMI_RELAY_ID, "knmi")


class Clock:
    def __init__(self):
        self.t = 1_000_000.0

    def __call__(self):
        return self.t


class TestBudget(unittest.TestCase):
    def test_own_fuse(self):
        c = Clock()
        b = knmi.Budget(3, 100, c)
        for _ in range(3):
            self.assertTrue(b.allowed())
            b.spend()
        self.assertFalse(b.allowed())
        c.t += 3599
        self.assertFalse(b.allowed())
        c.t += 1
        self.assertTrue(b.allowed())

    def test_429_waits_for_reset(self):
        c = Clock()
        b = knmi.Budget(100, 100, c)
        b.server(429, None, int(c.t) + 600)
        self.assertFalse(b.allowed())
        c.t += 599
        self.assertFalse(b.allowed())
        c.t += 1
        self.assertTrue(b.allowed())

    def test_low_remaining_pauses(self):
        c = Clock()
        b = knmi.Budget(100, 100, c)
        b.server(200, 100, int(c.t) + 600)
        self.assertTrue(b.allowed())
        b.server(200, 99, int(c.t) + 600)
        self.assertFalse(b.allowed())

    def test_no_or_odd_reset(self):
        c = Clock()
        b = knmi.Budget(100, 100, c)
        b.server(429, None, None)
        self.assertEqual(b.paused_until, c.t + 900)
        b2 = knmi.Budget(100, 100, c)
        b2.server(429, None, int(c.t) + 7200)  # beyond an hour: not believed
        self.assertEqual(b2.paused_until, c.t + 900)
        b3 = knmi.Budget(100, 100, c)
        b3.server(429, None, int(c.t) - 5)  # in the past
        self.assertEqual(b3.paused_until, c.t + 900)

    def test_a_later_answer_never_shortens_a_pause(self):
        c = Clock()
        b = knmi.Budget(100, 100, c)
        b.server(429, None, int(c.t) + 1800)
        b.server(200, 50, int(c.t) + 60)
        self.assertEqual(b.paused_until, c.t + 1800)

    def test_fine_answers_change_nothing(self):
        c = Clock()
        b = knmi.Budget(100, 100, c)
        b.server(200, 950, int(c.t) + 600)
        b.server(503, None, None)
        self.assertEqual(b.paused_until, 0.0)


if __name__ == "__main__":
    unittest.main()
