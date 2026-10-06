"""Build the hazard colour table that Live Track Weather ships.

Source: the National Weather Service's own table of watch, warning and
advisory colours and priorities, https://www.weather.gov/help-map . Each row
names an event, its priority (1 = drawn on top: Tsunami Warning) and its hex
colour. Live Track Weather uses those values unchanged.

Output: {"meta": {...}, "events": {event: {"color": "#RRGGBB", "priority": n}}},
events sorted by priority. The data is a work of the US Government.

Usage:
    python tools/build_colours.py --fetch
    python tools/build_colours.py --html saved_page.html --retrieved 2026-10-05
        [--out custom_components/live_track_weather/data/nws_hazard_colours.json]
"""
from __future__ import annotations

import argparse
import datetime as dt
import email.utils
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

SOURCE = "https://www.weather.gov/help-map"
USER_AGENT = "LiveTrackWeather build tool (+https://github.com/StrausbergAutomationWorks/LiveTrackWeather)"
HEX = re.compile(r"#?([0-9A-Fa-f]{6})")


class _Rows(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.rows: list[list[str]] = []
        self._row: list[str] | None = None
        self._cell: list[str] | None = None

    def handle_starttag(self, tag, attrs):
        if tag == "tr":
            self._row = []
        elif tag in ("td", "th") and self._row is not None:
            self._cell = []

    def handle_endtag(self, tag):
        if tag in ("td", "th") and self._cell is not None:
            self._row.append(" ".join("".join(self._cell).split()))
            self._cell = None
        elif tag == "tr" and self._row is not None:
            if self._row:
                self.rows.append(self._row)
            self._row = None

    def handle_data(self, data):
        if self._cell is not None:
            self._cell.append(data)


def parse(html: str) -> dict[str, dict]:
    p = _Rows()
    p.feed(html)
    events: dict[str, dict] = {}
    for row in p.rows:
        if len(row) < 6 or not row[1].isdigit():
            continue  # header and any other table
        m = HEX.fullmatch(row[-1].strip())
        if not m:
            sys.exit(f"row without a hex colour: {row}")
        if row[0] in events:
            sys.exit(f"event listed twice: {row[0]}")
        events[row[0]] = {"color": "#" + m.group(1).upper(), "priority": int(row[1])}
    if len(events) < 50:
        sys.exit(f"only {len(events)} events parsed: has the page changed shape?")
    prios = [e["priority"] for e in events.values()]
    if len(set(prios)) != len(prios):
        sys.exit("two events share a priority: the page has changed meaning")
    return dict(sorted(events.items(), key=lambda kv: kv[1]["priority"]))


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--fetch", action="store_true", help=f"download {SOURCE}")
    g.add_argument("--html", type=Path, help="a saved copy of the page")
    ap.add_argument("--retrieved", help="YYYY-MM-DD the saved copy was taken (with --html)")
    ap.add_argument(
        "--out",
        type=Path,
        default=Path(__file__).resolve().parent.parent
        / "custom_components" / "live_track_weather" / "data" / "nws_hazard_colours.json",
    )
    a = ap.parse_args()
    if a.fetch:
        import requests

        r = requests.get(SOURCE, headers={"User-Agent": USER_AGENT}, timeout=30)
        r.raise_for_status()
        html = r.text
        retrieved = email.utils.parsedate_to_datetime(r.headers["Date"]).date().isoformat()
    else:
        if not a.retrieved:
            sys.exit("--retrieved is required with --html")
        html = a.html.read_text(encoding="utf-8")
        retrieved = dt.date.fromisoformat(a.retrieved).isoformat()
    events = parse(html)
    doc = {
        "meta": {
            "source": "US National Weather Service hazard map colours and priorities",
            "source_page": SOURCE,
            "retrieved": retrieved,
            "events": len(events),
            "priority": "1 is drawn on top",
        },
        "events": events,
    }
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(doc, indent=1, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(f"{len(events)} events, retrieved {retrieved}; written {a.out}")


if __name__ == "__main__":
    main()
