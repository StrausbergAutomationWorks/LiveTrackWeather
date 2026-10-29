"""KNMI radar for the Netherlands, relayed with the user's own key: the parts that need no Home Assistant
(Weather SSOT item 278, contract D13 "Relays").

KNMI's keyed WMS allows 1,000 requests an hour per key. So the relay never passes a tile through: for each
5-minute frame it asks KNMI for ONE picture of the whole relayed area, at zoom 9 and aligned to zoom 9's tile
grid, and cuts every tile the card can ask for from it (zooms 7 to 9). A frame costs one request however many
browsers look at it; capabilities every 5 minutes cost twelve an hour.

The relayed area is the zoom-9 tiles wholly inside the largest rectangle that fits in KNMI's radar disc,
MEASURED 2026-10-28 (bin\\ltw278_cover.py: the disc 0.00-9.80 E, 49.12-55.84 N; the rectangle 1.58-8.41 E,
50.05-54.87 N). Its edges are tile edges, so a tile the card's whole-tile test sends here at any zoom is one this
relay has. Outside it the card uses its other sources.
"""

from __future__ import annotations

import io
import math
import re
import time
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from typing import Any, Callable

from PIL import Image

_WMS = "{http://www.opengis.net/wms}"
_R = 20037508.342789244
FRAME_RE = re.compile(r"^\d{12}$")

# Zoom-9 tiles relayed, inclusive (x0, x1, y0, y1). MEASURED 2026-10-28, see the module docstring.
NATIVE_ZOOM = 9
MIN_ZOOM = 7
TILES_NATIVE = (259, 266, 163, 172)
TILE_PX = 256


def _lat(y: float, z: int) -> float:
    return math.degrees(math.atan(math.sinh(math.pi * (1 - 2 * y / 2 ** z))))


def bounds() -> list[float]:
    """[W, S, E, N] in degrees: the relayed area's tile edges, rounded to 6 decimals."""
    x0, x1, y0, y1 = TILES_NATIVE
    n = 2 ** NATIVE_ZOOM
    return [round(x0 / n * 360 - 180, 6), round(_lat(y1 + 1, NATIVE_ZOOM), 6),
            round((x1 + 1) / n * 360 - 180, 6), round(_lat(y0, NATIVE_ZOOM), 6)]


def tiles_at(z: int) -> list[tuple[int, int]]:
    """Every (x, y) at zoom z wholly inside the relayed area; none below MIN_ZOOM or above NATIVE_ZOOM."""
    if z < MIN_ZOOM or z > NATIVE_ZOOM:
        return []
    f = 2 ** (NATIVE_ZOOM - z)
    x0, x1, y0, y1 = TILES_NATIVE
    xs = range(-(-x0 // f), (x1 + 1) // f)
    ys = range(-(-y0 // f), (y1 + 1) // f)
    return [(x, y) for x in xs for y in ys]


def picture_size() -> tuple[int, int]:
    """The picture asked of KNMI, in pixels: the relayed area at zoom 9."""
    x0, x1, y0, y1 = TILES_NATIVE
    return (x1 - x0 + 1) * TILE_PX, (y1 - y0 + 1) * TILE_PX


def picture_bbox() -> str:
    """The relayed area in EPSG:3857 metres, as WMS 1.3.0's BBOX wants it (minx,miny,maxx,maxy)."""
    x0, x1, y0, y1 = TILES_NATIVE
    w = 2 * _R / 2 ** NATIVE_ZOOM
    minx, maxx = -_R + x0 * w, -_R + (x1 + 1) * w
    maxy, miny = _R - y0 * w, _R - (y1 + 1) * w
    return ",".join(f"{v:.3f}" for v in (minx, miny, maxx, maxy))


def capabilities_params() -> dict[str, str]:
    return {"SERVICE": "WMS", "REQUEST": "GetCapabilities", "VERSION": "1.3.0"}


def picture_params(layer: str, style: str, when: str) -> dict[str, str]:
    """GetMap for one frame. Every request names its frame: KNMI answers max-age=3600 for a picture."""
    w, h = picture_size()
    return {"SERVICE": "WMS", "REQUEST": "GetMap", "VERSION": "1.3.0", "LAYERS": layer, "STYLES": style,
            "CRS": "EPSG:3857", "BBOX": picture_bbox(), "WIDTH": str(w), "HEIGHT": str(h),
            "FORMAT": "image/png", "TRANSPARENT": "TRUE", "TIME": when}


def newest_frame(caps: bytes | None, layer: str) -> str | None:
    """The newest frame of `layer` in a WMS 1.3.0 capabilities document: its time dimension's default, as KNMI
    writes it (`2026-10-29T00:05:00Z`). None when the document, the layer or a valid time is missing."""
    if not caps:
        return None
    try:
        root = ET.fromstring(caps)
    except ET.ParseError:
        return None
    for lyr in root.iter(f"{_WMS}Layer"):
        if lyr.findtext(f"{_WMS}Name") != layer:
            continue
        for dim in lyr.findall(f"{_WMS}Dimension"):
            if dim.get("name") != "time":
                continue
            value = (dim.get("default") or "").strip()
            try:
                datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ")
            except ValueError:
                return None
            return value
    return None


def frame_key(when: str) -> str:
    """`2026-10-29T00:05:00Z` -> `202610290005`, the frame's part of a tile's path."""
    return datetime.strptime(when, "%Y-%m-%dT%H:%M:%SZ").strftime("%Y%m%d%H%M")


def parse_time(when: str) -> datetime:
    return datetime.strptime(when, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)


def _empty_png() -> bytes:
    buf = io.BytesIO()
    Image.new("RGBA", (TILE_PX, TILE_PX), (0, 0, 0, 0)).save(buf, "PNG")
    return buf.getvalue()


EMPTY_PNG = _empty_png()


def cut(picture: bytes) -> dict[tuple[int, int, int], bytes]:
    """Every relayed tile, zooms MIN_ZOOM to NATIVE_ZOOM, cut from one frame's picture. A lower zoom's tile is its
    block of zoom-9 pixels averaged down (box filter). A tile with nothing drawn is EMPTY_PNG.
    Raises ValueError when the picture is not the size asked for, OSError when it is not an image."""
    with Image.open(io.BytesIO(picture)) as im:
        if im.size != picture_size():
            raise ValueError(f"picture is {im.size}, expected {picture_size()}")
        rgba = im.convert("RGBA")
    x0, _, y0, _ = TILES_NATIVE
    out: dict[tuple[int, int, int], bytes] = {}
    for z in range(MIN_ZOOM, NATIVE_ZOOM + 1):
        f = 2 ** (NATIVE_ZOOM - z)
        size = TILE_PX * f
        for x, y in tiles_at(z):
            px, py = (x * f - x0) * TILE_PX, (y * f - y0) * TILE_PX
            tile = rgba.crop((px, py, px + size, py + size))
            if f > 1:
                tile = tile.resize((TILE_PX, TILE_PX), Image.Resampling.BOX)
            if tile.getchannel("A").getbbox() is None:
                out[(z, x, y)] = EMPTY_PNG
                continue
            buf = io.BytesIO()
            tile.save(buf, "PNG")
            out[(z, x, y)] = buf.getvalue()
    return out


def relay_attribute(frame: str | None, when: str | None, usable: bool, tile_path: str, attribution: str,
                    relay_id: str) -> dict[str, Any] | None:
    """D13's `radar_relay` mapping. None before any frame is known (nothing for the card to read). A frame
    that cannot be served drops `time`, so the card falls back to its other sources (D13: never tile by tile)."""
    if not frame or not when:
        return None
    out: dict[str, Any] = {"id": relay_id, "tiles": f"{tile_path}/{frame}/{{z}}/{{x}}/{{y}}.png",
                           "bounds": bounds(), "max_native_zoom": NATIVE_ZOOM, "attribution": attribution}
    if usable:
        out["time"] = when
    return out


class Budget:
    """What this relay may still ask of KNMI. Two limits: its own count over the last hour (a fuse far above
    what it needs), and KNMI's: a 429, or fewer than `reserve` requests left on the key, stops every request
    until KNMI's reset time (at most an hour; 15 minutes when KNMI gives none)."""

    def __init__(self, per_hour: int, reserve: int, clock: Callable[[], float] = time.time) -> None:
        self.per_hour = per_hour
        self.reserve = reserve
        self._clock = clock
        self._sent: list[float] = []
        self.paused_until = 0.0

    def allowed(self) -> bool:
        now = self._clock()
        self._sent = [t for t in self._sent if now - t < 3600]
        return now >= self.paused_until and len(self._sent) < self.per_hour

    def spend(self) -> None:
        self._sent.append(self._clock())

    def server(self, status: int, remaining: int | None, reset: int | None) -> None:
        if status != 429 and (remaining is None or remaining >= self.reserve):
            return
        now = self._clock()
        until = reset if reset is not None and now < reset <= now + 3600 else now + 900
        self.paused_until = max(self.paused_until, until)
