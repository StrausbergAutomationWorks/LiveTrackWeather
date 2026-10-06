"""Turn an NWS /alerts/active document into the live list the map draws.

Pure Python, no Home Assistant import, so it is tested offline.

The live list is small on purpose. The shapes themselves ship once per
release in a static file; this names which of them to fill and how:

    zones     {shape key: event}   e.g. {"forecast/LMZ740": "Gale Warning"}
    polygons  [{"event": ..., "coordinates": [...]}]
    styles    {event: {"color": "#RRGGBB", "priority": n}} for the events
              drawn only: the NWS's own colour and priority, nothing added
              (Lee, 2026-10-05)
    count     every live alert, drawn or outranked

A shape key is the path after /zones/ in the alert's affectedZones URL, the
same key the shape file uses. Where several alerts name one zone, the zone
takes the event NWS ranks highest (the lowest priority number in its hazard
colour table). An alert that carries its own polygon (a storm-based warning)
is drawn as that polygon only: its zones are the counties it touches, and
filling them would overstate it.
"""

from __future__ import annotations

from typing import Any

# Used for an event missing from the NWS colour table. Last in priority, so a
# known event always draws over it.
FALLBACK_STYLE = {"color": "#808080", "priority": 999}

_ZONES_MARKER = "/zones/"


def zone_key(url: str) -> str | None:
    """'https://api.weather.gov/zones/forecast/ILZ014' -> 'forecast/ILZ014'."""
    i = url.find(_ZONES_MARKER)
    return url[i + len(_ZONES_MARKER):] if i >= 0 else None


def wanted(props: dict[str, Any]) -> bool:
    """Real alerts only. Test and exercise messages are never drawn."""
    return props.get("status") == "Actual" and props.get("event") != "Test Message"


def style_of(event: str, colours: dict[str, dict[str, Any]]) -> dict[str, Any]:
    s = colours.get(event, FALLBACK_STYLE)
    return {"color": s["color"], "priority": s["priority"]}


def round_coords(c, nd: int = 3):
    if isinstance(c[0], (int, float)):
        return [round(c[0], nd), round(c[1], nd)]
    return [round_coords(x, nd) for x in c]


def live_list(doc: dict[str, Any], colours: dict[str, dict[str, Any]]) -> dict[str, Any]:
    """The live list for one /alerts/active document.

    `colours` maps event name -> {"color": "#RRGGBB", "priority": int}.
    """
    zones: dict[str, str] = {}
    polygons: list[dict[str, Any]] = []
    styles: dict[str, dict[str, Any]] = {}
    count = 0
    unknown: set[str] = set()

    for feat in doc.get("features", []):
        props = feat.get("properties") or {}
        if not wanted(props):
            continue
        event = props.get("event") or "Unknown"
        if event not in colours:
            unknown.add(event)
        style = styles.setdefault(event, style_of(event, colours))
        count += 1
        geom = feat.get("geometry")
        if geom and geom.get("type") in ("Polygon", "MultiPolygon"):
            polygons.append({
                "event": event,
                "type": geom["type"],
                "coordinates": round_coords(geom["coordinates"]),
            })
            continue
        for url in props.get("affectedZones") or []:
            key = zone_key(url)
            if key is None:
                continue
            held = zones.get(key)
            if held is None or style["priority"] < styles[held]["priority"]:
                zones[key] = event

    # Highest priority last, so a card painting in list order draws it on top.
    polygons.sort(key=lambda p: -styles[p["event"]]["priority"])
    # Styles for what is DRAWN: an event outranked on every zone it named
    # (a Gale Watch under a Gale Warning) has nothing on the map.
    drawn = set(zones.values()) | {p["event"] for p in polygons}
    return {
        "count": count,
        "zones": dict(sorted(zones.items())),
        "polygons": polygons,
        "styles": {e: s for e, s in sorted(styles.items()) if e in drawn},
        "unknown_events": sorted(unknown),
        "updated": doc.get("updated"),
    }
