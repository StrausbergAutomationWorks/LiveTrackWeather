"""What ships: manifest, translations, the two data files, no BOM anywhere."""

import gzip
import json
import re
import unittest

from _load import COMP, ROOT


class TestPackage(unittest.TestCase):
    def test_manifest(self):
        m = json.loads((COMP / "manifest.json").read_text(encoding="utf-8"))
        const = (COMP / "const.py").read_text(encoding="utf-8")
        self.assertEqual(m["domain"], "live_track_weather")
        self.assertIn('DOMAIN = "live_track_weather"', const)
        self.assertIn(f'VERSION = "{m["version"]}"', const)
        self.assertEqual(m["iot_class"], "cloud_polling")
        self.assertIn("http", m["dependencies"])

    def test_no_bom_anywhere(self):
        for p in ROOT.rglob("*"):
            if p.is_file() and ".git" not in p.parts and p.suffix in (".py", ".json", ".md", ".txt"):
                self.assertFalse(p.read_bytes().startswith(b"\xef\xbb\xbf"), p)

    def test_translations_match_strings(self):
        self.assertEqual((COMP / "strings.json").read_bytes(),
                         (COMP / "translations" / "en.json").read_bytes())

    def test_shape_file(self):
        raw = (COMP / "www" / "nws_zones.json.gz").read_bytes()
        self.assertEqual(raw[:2], b"\x1f\x8b")
        self.assertEqual(raw[4:8], b"\x00\x00\x00\x00", "gzip header carries a timestamp")
        doc = json.loads(gzip.decompress(raw))
        meta, shapes = doc["meta"], doc["shapes"]
        self.assertEqual(meta["simplify_deg"], 0.005)
        self.assertEqual(len(shapes), sum(meta["shapes"].values()))
        self.assertEqual(list(shapes), sorted(shapes))
        key = re.compile(r"^(county/[A-Z]{2}C\d{3}|forecast/[A-Z]{2}Z\d{3}|fire/[A-Z]{2}Z\d{3})$")
        bad = [k for k in shapes if not key.match(k)]
        self.assertEqual(bad, [])
        # The plain file must NOT ship: the .gz answers requests for it.
        self.assertFalse((COMP / "www" / "nws_zones.json").exists())

    def test_colour_table(self):
        doc = json.loads((COMP / "data" / "nws_hazard_colours.json").read_text(encoding="utf-8"))
        ev = doc["events"]
        self.assertGreaterEqual(len(ev), 100)
        self.assertEqual(ev["Tornado Warning"], {"color": "#FF0000", "priority": 2})
        self.assertEqual(len({e["priority"] for e in ev.values()}), len(ev))
        for e in ev.values():
            self.assertRegex(e["color"], r"^#[0-9A-F]{6}$")


if __name__ == "__main__":
    unittest.main()
