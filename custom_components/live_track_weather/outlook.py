"""The SPC Day 1 categorical outlook as D12 `polygons` (contract D16). No Home Assistant import.

Decided by Lee 2026-10-28 14:12: Day 1 categorical only, Marginal and up, its own checkbox,
drawn under the alerts, on by default. SPC's file carries every category from general
thunderstorms (`TSTM`) up; `TSTM` is not severe and on 2026-10-28 covered most of the country,
so it is not drawn. A quiet day draws nothing.

The file (MEASURED 2026-10-28, `day1otlk_cat.lyr.geojson`): one feature per category, a
`MultiPolygon` with `LABEL` (`MRGL`), `LABEL2` (`Marginal Risk`), `DN`, SPC's own `fill` and
`stroke`, and `ISSUE`, `VALID`, `EXPIRE` as `YYYYMMDDhhmm` UTC. An outlook past its `EXPIRE`
is not drawn.
"""

from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Any

# category -> (event, risk level 1-5, D12 priority: 1 on top)
CATEGORIES = {
    "MRGL": ("Marginal Risk", 1, 5),
    "SLGT": ("Slight Risk", 2, 4),
    "ENH": ("Enhanced Risk", 3, 3),
    "MDT": ("Moderate Risk", 4, 2),
    "HIGH": ("High Risk", 5, 1),
}
# Used only when a feature carries no usable `fill`. MRGL and SLGT MEASURED from SPC's file
# 2026-10-28; ENH, MDT and HIGH are SPC's usual colours, NOT seen in a file yet.
FALLBACK_COLOURS = {
    "MRGL": "#66A366",
    "SLGT": "#FFE066",
    "ENH": "#FFA366",
    "MDT": "#E06666",
    "HIGH": "#EE99EE",
}
_HEX = re.compile(r"^#[0-9A-Fa-f]{6}$")
_AREA = ("Polygon", "MultiPolygon")


def spc_time(s: Any) -> datetime | None:
    """`202610281630` -> 2026-10-28 16:30 UTC; anything else None."""
    if not isinstance(s, str) or not re.fullmatch(r"\d{12}", s):
        return None
    try:
        return datetime.strptime(s, "%Y%m%d%H%M").replace(tzinfo=timezone.utc)
    except ValueError:
        return None


def _iso(t: datetime | None) -> str | None:
    return t.strftime("%Y-%m-%dT%H:%M:%SZ") if t else None


def _round(c: Any) -> Any:
    if isinstance(c, list):
        if len(c) >= 2 and all(isinstance(x, (int, float)) and not isinstance(x, bool) for x in c[:2]):
            return [round(float(c[0]), 3), round(float(c[1]), 3)]
        return [_round(x) for x in c]
    return c


def empty() -> dict[str, Any]:
    return {"polygons": [], "styles": {}, "level": 0, "risk": None,
            "issued": None, "valid_from": None, "valid_to": None}


def parse(doc: Any, now: datetime) -> dict[str, Any]:
    """The polygons, styles and highest risk level to draw now from one Day 1 categorical file."""
    out = empty()
    if not isinstance(doc, dict) or not isinstance(doc.get("features"), list):
        return out
    feats = [f for f in doc["features"] if isinstance(f, dict) and isinstance(f.get("properties"), dict)]
    times = next(((spc_time(f["properties"].get("ISSUE")), spc_time(f["properties"].get("VALID")),
                   spc_time(f["properties"].get("EXPIRE"))) for f in feats), (None, None, None))
    issued, valid, expire = times
    if expire is not None and now >= expire:
        return out
    out.update(issued=_iso(issued), valid_from=_iso(valid), valid_to=_iso(expire))
    for f in feats:
        p = f["properties"]
        cat = p.get("LABEL")
        g = f.get("geometry")
        if cat not in CATEGORIES or not isinstance(g, dict) or g.get("type") not in _AREA \
                or not isinstance(g.get("coordinates"), list) or not g["coordinates"]:
            continue
        event, level, priority = CATEGORIES[cat]
        fill = p.get("fill")
        colour = fill.upper() if isinstance(fill, str) and _HEX.match(fill) else FALLBACK_COLOURS[cat]
        out["polygons"].append({"event": event, "type": g["type"], "coordinates": _round(g["coordinates"])})
        out["styles"][event] = {"color": colour, "priority": priority}
        if level > out["level"]:
            out["level"], out["risk"] = level, event
    return out
