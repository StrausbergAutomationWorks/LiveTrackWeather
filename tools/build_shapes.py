"""Build the NWS shape file that Live Track Weather ships.

Input: the five National Weather Service shapefile zips of ONE edition, as
published at https://www.weather.gov/gis/ :

    c_DDmmYY.zip   counties            -> county/<ST>C<nnn>
    z_DDmmYY.zip   public zones        -> forecast/<ST>Z<nnn>
    mzDDmmYY.zip   marine zones        -> forecast/<ID>
    ozDDmmYY.zip   offshore zones      -> forecast/<ID>
    fzDDmmYY.zip   fire weather zones  -> fire/<ST>Z<nnn>

Keys are the path after /zones/ in the API's affectedZones URLs, so an alert
names its shapes directly. Public, marine and offshore zones all live under
/zones/forecast/ in the API. Fire zones and public zones share codes; the
prefix is what tells them apart.

Records sharing a key are unioned. Each shape is simplified on its own to
0.005 degrees (about 500 m) with preserve_topology=True, and coordinates are
rounded to 3 decimals. Shape keys are sorted and the gzip header carries no
timestamp, so the same five zips always give the same bytes.

Output: {"meta": {...}, "shapes": {key: GeoJSON geometry}}, gzipped.
The data is a work of the US Government (public domain).

Usage:
    python tools/build_shapes.py --src <folder with the five zips> \
        [--out custom_components/live_track_weather/data/nws_zones.json.gz]
"""
from __future__ import annotations

import argparse
import datetime as dt
import gzip
import hashlib
import json
import re
import sys
import tempfile
import zipfile
from pathlib import Path

import shapefile  # pyshp
from shapely.geometry import mapping, shape
from shapely.ops import unary_union

TOLERANCE_DEG = 0.005
DECIMALS = 3
FORMAT_VERSION = 1

# prefix in the zip name -> (set name, key function on a record)
SETS = {
    "c_": ("counties", lambda r: f"county/{r['STATE']}C{r['FIPS'][2:]}"),
    "z_": ("public", lambda r: f"forecast/{r['STATE']}Z{r['ZONE']}"),
    "mz": ("marine", lambda r: f"forecast/{r['ID']}"),
    "oz": ("offshore", lambda r: f"forecast/{r['ID']}"),
    "fz": ("fire", lambda r: f"fire/{r['STATE']}Z{r['ZONE']}"),
}
# Public and marine/offshore zones share the forecast/ prefix; their codes must
# not collide. Fire shares codes with public, but has its own prefix.

# NWS stamps an edition as DDmmYY with a two-letter month. Only months seen in
# a real file name are listed; an unknown one stops the build rather than
# guessing, so add it here after reading the NWS page.
MONTHS = {"mr": 3, "ap": 4}

STAMP = re.compile(r"^(c_|z_|mz|oz|fz)(\d\d)([a-z]{2})(\d\d)\.zip$")


def find_zips(src: Path) -> tuple[dict[str, Path], str]:
    """The five zips of one edition, by prefix, and that edition's stamp."""
    found: dict[str, Path] = {}
    stamps: set[str] = set()
    for p in sorted(src.glob("*.zip")):
        m = STAMP.match(p.name)
        if not m:
            continue
        if m.group(1) in found:
            sys.exit(f"two {SETS[m.group(1)][0]} zips in {src}: keep one edition only")
        found[m.group(1)] = p
        stamps.add(m.group(2) + m.group(3) + m.group(4))
    missing = [SETS[k][0] for k in SETS if k not in found]
    if missing:
        sys.exit(f"missing in {src}: {', '.join(missing)}")
    if len(stamps) != 1:
        sys.exit(f"the five zips are from different editions: {sorted(stamps)}")
    return found, stamps.pop()


def edition_date(stamp: str) -> str:
    day, mon, yy = stamp[:2], stamp[2:4], stamp[4:]
    if mon not in MONTHS:
        sys.exit(f"unknown NWS month code {mon!r} in {stamp!r}: add it to MONTHS")
    return dt.date(2000 + int(yy), MONTHS[mon], int(day)).isoformat()


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def records(zpath: Path, tmp: Path):
    """(record dict, shapely geometry) for every shape in one zip."""
    out = tmp / zpath.stem
    with zipfile.ZipFile(zpath) as z:
        z.extractall(out)
    shp = next(out.rglob("*.shp"))
    with shapefile.Reader(str(shp)) as sf:
        names = [f[0] for f in sf.fields[1:]]
        for sr in sf.iterShapeRecords():
            yield dict(zip(names, sr.record)), shape(sr.shape.__geo_interface__)


def rnd(c, nd):
    if isinstance(c[0], (int, float)):
        return [round(c[0], nd), round(c[1], nd)]
    return [rnd(x, nd) for x in c]


def build(src: Path) -> dict:
    zips, stamp = find_zips(src)
    groups: dict[str, list] = {}
    origin: dict[str, str] = {}
    counts: dict[str, int] = {}
    with tempfile.TemporaryDirectory() as td:
        for prefix, (set_name, key_of) in SETS.items():
            n = 0
            for rec, geom in records(zips[prefix], Path(td)):
                key = key_of(rec)
                if origin.setdefault(key, set_name) != set_name:
                    sys.exit(f"key {key} is in both {origin[key]} and {set_name}")
                groups.setdefault(key, []).append(geom)
                n += 1
            counts[set_name] = n

    shapes = {}
    for key in sorted(groups):
        parts = groups[key]
        g = parts[0] if len(parts) == 1 else unary_union(parts)
        if not g.is_valid:
            g = g.buffer(0)
        gj = mapping(g.simplify(TOLERANCE_DEG, preserve_topology=True))
        shapes[key] = {"type": gj["type"], "coordinates": rnd(gj["coordinates"], DECIMALS)}

    per_set = {s: 0 for s, _ in SETS.values()}
    for key in shapes:
        per_set[origin[key]] += 1
    meta = {
        "format": FORMAT_VERSION,
        "source": "US National Weather Service county and zone shapefiles (public domain)",
        "source_page": "https://www.weather.gov/gis/",
        "edition": stamp,
        "edition_date": edition_date(stamp),
        "files": {zips[p].name: sha256(zips[p]) for p in SETS},
        "records": counts,
        "shapes": per_set,
        "keys": "the path after /zones/ in the NWS API's affectedZones URLs",
        "simplify_deg": TOLERANCE_DEG,
        "preserve_topology": True,
        "decimals": DECIMALS,
    }
    return {"meta": meta, "shapes": shapes}


def encode(doc: dict) -> bytes:
    raw = json.dumps(doc, separators=(",", ":"), ensure_ascii=True).encode("ascii")
    return gzip.compress(raw, compresslevel=9, mtime=0)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--src", type=Path, required=True, help="folder holding the five NWS zips")
    ap.add_argument(
        "--out",
        type=Path,
        default=Path(__file__).resolve().parent.parent
        / "custom_components" / "live_track_weather" / "data" / "nws_zones.json.gz",
    )
    a = ap.parse_args()
    doc = build(a.src)
    data = encode(doc)
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_bytes(data)
    m = doc["meta"]
    print(f"edition {m['edition']} ({m['edition_date']}): {len(doc['shapes'])} shapes "
          f"{m['shapes']}; {len(data)} bytes gzip; sha256 {hashlib.sha256(data).hexdigest()}")
    print(f"written {a.out}")


if __name__ == "__main__":
    main()
