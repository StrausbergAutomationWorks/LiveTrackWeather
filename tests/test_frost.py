"""MET Norway's Frost (Weather SSOT item 311, contract D22): frost.py.

Real answers, 2026-11-18 (bin\\ltw311_measure.py, ltw311_measure2.py, ltw311_fixtures.py): the Svalbard and Jan Mayen
station list (frost_sources_sj_*) and its latest readings (frost_latest_sj_*, created 09:56:36Z), and the nearest
stations and their readings at Oslo and Longyearbyen, and the nearest at Stockholm. Answers marked CONSTRUCTED are
copies of a real one with one field changed.
"""

import json
import unittest
from datetime import datetime, timedelta, timezone

from _load import FIXTURES, load

frost = load("frost")
observe = load("observe")


def fx(name):
    return json.loads((FIXTURES / f"frost_{name}_20261118.json").read_text(encoding="utf-8"))


def created(doc):
    return datetime.fromisoformat(doc["createdAt"].replace("Z", "+00:00"))


SJ_SOURCES = fx("sources_sj")
SJ_LATEST = fx("latest_sj")
SJ_NOW = created(SJ_LATEST)


class TestNames(unittest.TestCase):
    def test_title(self):
        self.assertEqual(frost.title_name("SVALBARD LUFTHAVN"), "Svalbard Lufthavn")
        self.assertEqual(frost.title_name("BJØRNØYA II"), "Bjørnøya II")
        self.assertEqual(frost.title_name("KARL XII-ØYA"), "Karl XII-Øya")
        self.assertEqual(frost.title_name("NY-ÅLESUND"), "Ny-Ålesund")
        self.assertEqual(frost.title_name("LONGYEARDALEN - CENTRAL"), "Longyeardalen - Central")
        self.assertEqual(frost.title_name("PLATÅBERGET III"), "Platåberget III")
        self.assertEqual(frost.title_name("CIVIL DIX"), "Civil Dix", "only I to XXXIX are numerals")
        self.assertIsNone(frost.title_name("  "))
        self.assertIsNone(frost.title_name(None))


class TestSources(unittest.TestCase):
    def test_svalbard(self):
        src = frost.parse_sources(SJ_SOURCES)
        self.assertEqual(len(src), 48)
        self.assertEqual({s["country"] for s in src}, {"SJ"})
        by = {s["id"]: s for s in src}
        self.assertEqual(by["SN99840"]["name"], "Svalbard Lufthavn")
        self.assertEqual(by["SN99840"]["holders"], ["AVINOR", "MET.NO"])
        self.assertAlmostEqual(by["SN99840"]["lat"], 78.2453, places=4)
        self.assertAlmostEqual(by["SN99840"]["lon"], 15.5015, places=4)
        self.assertEqual(by["SN99712"]["name"], "Bjørnøya II")
        self.assertEqual(by["SN99950"]["name"], "Jan Mayen")

    def test_nearest_order_and_area(self):
        oslo = frost.parse_sources(fx("nearest_oslo"))
        self.assertEqual(len(oslo), 10)
        self.assertEqual(oslo[0]["id"], "SN18317", "nearest first, as Frost answered")
        self.assertTrue(frost.in_area(oslo))
        self.assertTrue(frost.in_area(frost.parse_sources(fx("nearest_longyearbyen"))))
        stockholm = frost.parse_sources(fx("nearest_stockholm"))
        self.assertEqual(stockholm[0]["country"], "SE")
        self.assertFalse(frost.in_area(stockholm), "Frost lists Swedish SYNOP stations: GeoNames' place")
        self.assertFalse(frost.in_area([]))
        self.assertFalse(frost.in_area([{"country": "SE"}, {"country": "NO"}]), "the NEAREST station decides")
        self.assertTrue(frost.in_area([{"country": "NO"}, {"country": "SE"}]))

    def test_bad_sources(self):
        doc = {"data": [{"id": "SN1", "geometry": {"coordinates": [10, 60]}, "name": "A"},
                        {"id": "TR1", "geometry": {"coordinates": [10, 60]}},
                        {"id": "SN2"},
                        {"id": "SN3", "geometry": {"coordinates": ["x", 60]}},
                        {"id": "SN4", "geometry": {"coordinates": [10, 60]}, "name": None}]}
        self.assertEqual([(s["id"], s["name"]) for s in frost.parse_sources(doc)], [("SN1", "A"), ("SN4", "SN4")])
        self.assertEqual(frost.parse_sources(None), [])
        self.assertEqual(frost.parse_sources({"data": None}), [])


class TestLatest(unittest.TestCase):
    def test_newest_and_best(self):
        lat = frost.parse_latest(SJ_LATEST, SJ_NOW)
        # 09:50: a 10-minute series (-2.3, quality 0) and a METAR-like 30-minute one (-2, quality 2)
        self.assertEqual(lat["SN99840"][frost.T]["value"], -2.3)
        self.assertEqual(lat["SN99840"][frost.WS]["value"], 8.8)
        self.assertEqual(lat["SN99840"][frost.SNOW]["value"], 27)
        self.assertEqual(lat["SN99840"][frost.T]["q"], 0)
        # quality 6 ("automatic" control only) is used, and kept with the value (Lee 2026-11-18)
        self.assertEqual((lat["SN99811"][frost.T]["value"], lat["SN99811"][frost.T]["q"]), (0, 6))
        self.assertEqual(lat["SN99870"][frost.WS]["q"], 6)
        self.assertEqual(len(lat), 37, "37 answered")

    def test_quality_and_ahead(self):
        now = datetime(2026, 11, 18, 10, 0, tzinfo=timezone.utc)

        def doc(ref, q=0, v=1.5):
            return {"data": [{"sourceId": "SN1:0", "referenceTime": ref,
                              "observations": [{"elementId": frost.T, "value": v, "qualityCode": q}]}]}
        self.assertEqual(frost.parse_latest(doc("2026-11-18T10:15:00.000Z"), now)["SN1"][frost.T]["value"], 1.5,
                         "15 minutes ahead counts")
        self.assertEqual(frost.parse_latest(doc("2026-11-18T10:16:00.000Z"), now), {})
        self.assertEqual(frost.parse_latest(doc("2101-11-18T10:00:00.000Z"), now), {}, "seen offshore")
        for q in (5, 7):
            self.assertEqual(frost.parse_latest(doc("2026-11-18T09:00:00.000Z", q), now), {}, q)
        for q in (0, 1, 2, 3, 4, 6, None):
            self.assertIn("SN1", frost.parse_latest(doc("2026-11-18T09:00:00.000Z", q), now), q)
        self.assertEqual(frost.parse_latest(doc("2026-11-18T09:00:00", 0), now), {}, "no zone")
        self.assertEqual(frost.parse_latest(doc("2026-11-18T09:00:00Z", 0, True), now), {}, "a boolean is no value")
        self.assertEqual(frost.parse_latest(None, now), {})

    def test_tie_breaks(self):
        now = datetime(2026, 11, 18, 10, 0, tzinfo=timezone.utc)
        obs = [{"elementId": frost.WS, "value": 1.0, "qualityCode": 0, "level": {"value": 2}, "timeResolution": "PT10M"},
               {"elementId": frost.WS, "value": 2.0, "qualityCode": 0, "level": {"value": 10}, "timeResolution": "PT1H"},
               {"elementId": frost.WS, "value": 3.0, "qualityCode": 0, "level": {"value": 10}, "timeResolution": "PT10M"},
               {"elementId": frost.WS, "value": 4.0, "qualityCode": 4, "level": {"value": 10}, "timeResolution": "PT1M"}]
        d = {"data": [{"sourceId": "SN1:0", "referenceTime": "2026-11-18T09:50:00Z", "observations": obs},
                      {"sourceId": "SN1:0", "referenceTime": "2026-11-18T09:00:00Z",
                       "observations": [{"elementId": frost.WS, "value": 9.0, "qualityCode": 0}]}]}
        self.assertEqual(frost.parse_latest(d, now)["SN1"][frost.WS]["value"], 3.0,
                         "newest; then quality; then 10 m; then the finer resolution")


class TestMarkers(unittest.TestCase):
    def setUp(self):
        self.recs = frost.station_markers(frost.parse_sources(SJ_SOURCES), frost.parse_latest(SJ_LATEST, SJ_NOW), SJ_NOW)
        self.by = {r["attrs"]["identity"]: r for r in self.recs}

    def test_which(self):
        # 32 report both; Bjørnøya II stands 10 m from Bjørnøya
        self.assertEqual(len(self.recs), 31)
        self.assertNotIn("SN99712", self.by)
        for there in ("SN99710", "SN99840", "SN99857", "SN99950", "SN99910", "SN99754", "SN99720", "SN99811", "SN99870"):
            self.assertIn(there, self.by)
        self.assertNotIn("SN99861", self.by, "temperature only (UNIS)")
        self.assertEqual([r["attrs"]["identity"] for r in self.recs], sorted(self.by))

    def test_svalbard_lufthavn(self):
        r = self.by["SN99840"]
        a = r["attrs"]
        self.assertEqual((r["key"], r["name"]), ("sn99840", "Svalbard Lufthavn"))
        self.assertEqual((a["marker_label"], a["marker_color"], a["map_layer"]), ("-2°", "#00796B", "fixed"))
        self.assertEqual((a["marker_group"], a["marker_group_label"], a["marker_group_order"]),
                         ("observations", "Observed weather (MET Norway)", 0))
        self.assertEqual((a["temperature_c"], a["wind_speed_kmh"], a["wind_from_deg"]), (-2.3, 31.7, 109))
        self.assertEqual(a["snow_depth_cm"], 27)
        self.assertEqual(a["observed"], "2026-11-18T09:50:00+00:00")
        self.assertEqual(a["station_holders"], "AVINOR, MET.NO")
        self.assertEqual(a["attribution"], "Observations: MET Norway (frost.met.no), CC BY 3.0 NO, modified")
        info = a["marker_info"]
        self.assertEqual(info["title"], "Svalbard Lufthavn, measured")
        lines = info["text"].split("\n")
        self.assertEqual(lines[0], "Temperature -2.3 °C")
        self.assertEqual(lines[1], "Wind 32 km/h from E (109°), gusts 50 km/h in the hour to 09:00 UTC",
                         "the 10-minute wind at 09:50 carries no time; the hourly gust names its hour")
        self.assertIn("Snow depth 27 cm", lines)
        self.assertEqual(lines[-2], "Measured 09:50 UTC 18 Nov")
        self.assertEqual(lines[-1], "MET Norway (Frost); station: AVINOR, MET.NO")

    def test_automatic_check_only(self):
        a = self.by["SN99870"]["attrs"]   # Adventdalen: temperature, wind and humidity all quality 6 at 09:00
        self.assertEqual(a["automatic_check_only"], ["temperature", "wind", "humidity"])
        lines = a["marker_info"]["text"].split("\n")
        self.assertEqual(lines[-2], "Automatic check only: temperature, wind, humidity")
        self.assertTrue(lines[-3].startswith("Measured "))
        self.assertNotIn("automatic_check_only", self.by["SN99840"]["attrs"], "all quality 0 or 2")
        self.assertNotIn("Automatic check", self.by["SN99840"]["attrs"]["marker_info"]["text"])
        p = self.by["SN99811"]["attrs"]   # Inglefieldbukta: quality 6 on temperature, wind, humidity, pressure
        self.assertEqual(p["automatic_check_only"], ["temperature", "wind", "humidity", "pressure"])

    def test_bjornoya_kept_is_the_newer(self):
        self.assertEqual(self.by["SN99710"]["name"], "Bjørnøya")

    def test_partial_station(self):
        # UNIS' Daudmannsodden reports temperature, humidity, wind and direction only: no gust or pressure lines
        r = self.by["SN99887"]
        self.assertNotIn("pressure_hpa", r["attrs"])
        self.assertNotIn("wind_gust_kmh", r["attrs"])
        text = r["attrs"]["marker_info"]["text"]
        self.assertNotIn("gusts", text)
        self.assertNotIn("Pressure", text)
        self.assertEqual(text.split("\n")[-1], "MET Norway (Frost); station: UNIS")

    def test_stale_and_merge_rules(self):
        src = [{"id": "SN1", "name": "A", "lat": 78.0, "lon": 15.0, "country": "SJ", "holders": []},
               {"id": "SN2", "name": "B", "lat": 78.005, "lon": 15.0, "country": "SJ", "holders": []},
               {"id": "SN3", "name": "C", "lat": 79.0, "lon": 15.0, "country": "SJ", "holders": []}]
        now = datetime(2026, 11, 18, 12, 0, tzinfo=timezone.utc)

        def v(x, mins):
            return {"value": x, "time": now - timedelta(minutes=mins)}
        lat = {"SN1": {frost.T: v(1.0, 60), frost.WS: v(2.0, 60)},
               "SN2": {frost.T: v(1.0, 10), frost.WS: v(2.0, 10)},       # 556 m from SN1, newer: kept
               "SN3": {frost.T: v(1.0, 121), frost.WS: v(2.0, 10)}}      # temperature older than 2 hours
        self.assertEqual([r["attrs"]["identity"] for r in frost.station_markers(src, lat, now)], ["SN2"])
        lat["SN2"][frost.RH] = v(80, 130)
        lat["SN2"][frost.PRESSURE] = v(1000.0, 30)
        a = frost.station_markers(src, lat, now)[0]["attrs"]
        self.assertNotIn("humidity_pct", a, "a value older than 2 hours is not shown")
        self.assertEqual(a["pressure_hpa"], 1000.0)
        self.assertIn("Pressure 1000.0 hPa at sea level (11:30 UTC)", a["marker_info"]["text"])
        lat["SN3"][frost.T] = v(-0.4, 120)
        recs = frost.station_markers(src, lat, now)
        self.assertEqual([r["attrs"]["identity"] for r in recs], ["SN2", "SN3"], "exactly 2 hours is fresh")
        self.assertEqual(recs[1]["attrs"]["marker_label"], "0°")
        self.assertNotIn("station_holders", recs[0]["attrs"])
        self.assertEqual(recs[0]["attrs"]["marker_info"]["text"].split("\n")[-1], "MET Norway (Frost)")
        lat["SN2"][frost.T] = v(1.0, 60)
        self.assertEqual([r["attrs"]["identity"] for r in frost.station_markers(src, lat, now)][0], "SN1",
                         "a tie: the lower id")
        del lat["SN1"][frost.WS]
        self.assertEqual([r["attrs"]["identity"] for r in frost.station_markers(src, lat, now)], ["SN2", "SN3"],
                         "no wind: no marker, and it does not hide its neighbour")


class TestPlaces(unittest.TestCase):
    def test_oslo(self):
        doc = fx("latest_oslo")
        now = created(doc)
        near = frost.parse_sources(fx("nearest_oslo"))
        reps = frost.place_reports(near, frost.parse_latest(doc, now), 59.9139, 10.7522, now)
        p = observe.pick(reps, now)
        self.assertEqual((p["temperature"]["station"]["id"], p["temperature"]["obs"]["temperature"]), ("SN18690", 0.5))
        self.assertEqual(p["wind"]["station"]["id"], "SN18210")
        self.assertEqual(p["wind"]["station"]["provider"], "MET Norway (Frost)")
        self.assertEqual(p["wind"]["station"]["km"], 3.1)
        w = p["wind"]["obs"]
        self.assertEqual((w["wind_speed"], w["wind_direction"], w["wind_gust"]), (16.56, 20.0, 20.88))
        self.assertEqual([s["km"] for s, _ in reps], sorted(s["km"] for s, _ in reps))

    def test_longyearbyen(self):
        doc = fx("latest_longyearbyen")
        now = created(doc)
        near = frost.parse_sources(fx("nearest_longyearbyen"))
        p = observe.pick(frost.place_reports(near, frost.parse_latest(doc, now), 78.2232, 15.6267, now), now)
        self.assertEqual(p["temperature"]["station"]["id"], "SN99861", "UNIS' temperature-only site, 1.0 km")
        self.assertEqual(p["wind"]["station"]["id"], "SN99857", "Longyeardalen - Central, 1.2 km")
        self.assertTrue(observe.complete(p))

    def test_report_time_and_staleness(self):
        now = datetime(2026, 11, 18, 12, 0, tzinfo=timezone.utc)
        s = [{"id": "SN1", "name": "A", "lat": 60.0, "lon": 10.0, "country": "NO", "holders": []}]

        def v(x, mins):
            return {"value": x, "time": now - timedelta(minutes=mins)}
        lat = {"SN1": {frost.T: v(1.0, 50), frost.WS: v(5.0, 5), frost.GUST: v(9.0, 130), frost.WD: v(90, 5)}}
        (st, rep), = frost.place_reports(s, lat, 60.0, 10.0, now)
        self.assertEqual(rep, {"temperature": 1.0, "wind_speed": 18.0, "wind_gust": None, "wind_direction": 90,
                               "time": (now - timedelta(minutes=50)).isoformat()}, "stale gust dropped; oldest time")
        self.assertEqual(st, {"id": "SN1", "name": "A", "provider": "MET Norway (Frost)", "km": 0.0})
        lat["SN1"][frost.T] = v(1.0, 125)
        lat["SN1"][frost.WS] = v(5.0, 125)
        self.assertEqual(frost.place_reports(s, lat, 60.0, 10.0, now), [], "nothing fresh: no report")
        lat["SN1"][frost.T] = v(1.0, -10)
        (_, rep), = frost.place_reports(s, lat, 60.0, 10.0, now)
        self.assertEqual(rep["time"], now.isoformat(), "a value ahead counts as now")
        lat3 = {"SN1": {frost.T: v(1.0, 10), frost.WS: v(5.0, 10), frost.GUST: v(9.0, 70)}}
        (_, rep), = frost.place_reports(s, lat3, 60.0, 10.0, now)
        self.assertEqual(rep["time"], (now - timedelta(minutes=70)).isoformat(),
                         "the hourly gust's older time counts, so it is never shown past 2 hours")
        lat2 = {"SN1": {frost.GUST: v(9.0, 5), frost.WD: v(90, 5)}}
        self.assertEqual(frost.place_reports(s, lat2, 60.0, 10.0, now), [], "a gust without a wind speed is not wind")


class TestRequests(unittest.TestCase):
    def test_params(self):
        self.assertEqual(frost.nearest_params(59.913912, 10.752212),
                         {"types": "SensorSystem", "geometry": "nearest(POINT(10.7522 59.9139))", "nearestmaxcount": "10"})
        self.assertEqual(frost.sources_params(), {"types": "SensorSystem", "country": "SJ"})
        p = frost.latest_params(["SN1", "SN2"], frost.PLACE_ELEMENTS)
        self.assertEqual(p["sources"], "SN1,SN2")
        self.assertEqual((p["referencetime"], p["maxage"]), ("latest", "PT2H"))
        self.assertEqual(p["elements"], "air_temperature,wind_speed,wind_from_direction,max(wind_speed_of_gust PT1H)")
        self.assertTrue(frost.OBS_URL.startswith("https://frost.met.no/"))

    def test_retry_and_check(self):
        self.assertEqual(frost.retry_s({"Retry-After": "120"}), 120)
        self.assertEqual(frost.retry_s({"Retry-After": "5"}), 60)
        self.assertEqual(frost.retry_s({}), 600)
        self.assertEqual(frost.retry_s({"Retry-After": "Wed, 18 Nov 2026 10:00:00 GMT"}), 600)
        self.assertEqual(frost.retry_s(None), 600)
        self.assertIsNone(frost.check_error(200))
        self.assertEqual(frost.check_error(401), "frost_id_rejected")
        for http in (0, 403, 429, 500, 503):
            self.assertEqual(frost.check_error(http), "frost_cannot_connect", http)


if __name__ == "__main__":
    unittest.main()
