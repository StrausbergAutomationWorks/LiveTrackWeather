# Live Track Weather

[English](README.md) · **Deutsch** · [Français](README.fr.md) · [Nederlands](README.nl.md) · [简体中文](README.zh-Hans.md) · [Español](README.es.md) · [Italiano](README.it.md) · [Dansk](README.da.md) · [Kalaallisut](README.kl.md) · [Alle Sprachen](#sprachen)

**Wetterwarnungen, Stürme, Erdbeben, Hochwasser, Waldbrände, Radar und
aktuelles Wetter für Home Assistant, auf einer Karte.** Live Track Weather
bringt Warnungen des US National Weather Service, Hurrikane und Taifune,
Unwetterprognosen, Erdbeben, Vulkane, Flusshochwasser, Sturm- und
Schneeberichte, Waldbrand- und Rauchdaten, Warnungen von MET Norway und
Wetterstationen auf Svalbard auf Ihre Home-Assistant-Karte und überwacht Ihr
Zuhause, die Handys Ihrer Familie und Ihr Wohnmobil auf Gefahren.

> **Live Track Weather ist ein Modul von Live Track**, einer Familie von
> Home-Assistant-Integrationen, die alles, was sich bewegt, und das Wetter,
> durch das es sich bewegt, auf einer gemeinsamen Karte zeigen: Flugzeuge,
> Schiffe, Züge und jetzt das Wetter. Installieren Sie es allein oder neben
> den anderen Modulen ([Liste unten](#teil-von-live-track-die-anderen-module)).

**Status: in Entwicklung, noch nicht veröffentlicht.** Das Repository bleibt
bis zur ersten Veröffentlichung privat.

Eigenes Werk von StrausbergAutomationWorks. Nicht verbunden mit oder
unterstützt von National Weather Service, NOAA, National Hurricane Center,
Storm Prediction Center, Joint Typhoon Warning Center, NASA, US Geological
Survey, EPA, MET Norway, KNMI oder GeoNames.

> ⚠ **Kein Notfallwarnsystem.** Es zeigt öffentliche Daten, bestenfalls ein
> paar Minuten verspätet. Für Warnungen, die Leben schützen, nutzen Sie die
> Notfallwarnungen Ihres Handys, ein Wetterradio (in den USA NOAA Weather
> Radio) und Ihre örtlichen Behörden, und folgen Sie Evakuierungsanordnungen.

---

## Inhalt

1. [Alles, was es kann](#alles-was-es-kann)
2. [Teil von Live Track: die anderen Module](#teil-von-live-track-die-anderen-module)
3. [Bevor Sie beginnen](#bevor-sie-beginnen)
4. [Installation, Schritt für Schritt](#installation-schritt-für-schritt)
5. [Einrichtung, Schritt für Schritt](#einrichtung-schritt-für-schritt)
6. [Kostenlose Schlüssel, die mehr freischalten, Schritt für Schritt](#kostenlose-schlüssel-die-mehr-freischalten-schritt-für-schritt)
7. [Die Karte auf ein Dashboard bringen](#die-karte-auf-ein-dashboard-bringen)
8. [In Automationen verwenden](#in-automationen-verwenden)
9. [Alles auf der Karte im Detail](#alles-auf-der-karte-im-detail)
10. [Alles an Ihren Orten im Detail](#alles-an-ihren-orten-im-detail)
11. [Alle Entitäten, die es anlegt](#alle-entitäten-die-es-anlegt)
12. [Was es sendet und herunterlädt](#was-es-sendet-und-herunterlädt)
13. [Sprachen](#sprachen)
14. [Danksagungen und Lizenzen](#danksagungen-und-lizenzen)
15. [Stichwörter](#stichwörter)

---

## Alles, was es kann

### Auf der Karte, ohne Einrichtung

| Was | Wo | Quelle |
|---|---|---|
| **Wetterwarnungen**: Warnungen, Vorwarnungen, Hinweise und Mitteilungen, durchscheinend gefüllt in den eigenen Farben des Wetterdienstes | die gesamten USA, ihre Küsten und Gewässer | National Weather Service |
| **Tornado-, Gewitter-, Sturzflut- und andere unwetterbezogene Warnungen**, mit ihrem eigenen Polygon gezeichnet | USA | National Weather Service |
| **Hurrikane, tropische Stürme, Taifune und Zyklone**: eine Markierung pro Sturm, der Vorhersagekegel, die vorhergesagte Zugbahn, das Windfeld und die bisherige Zugbahn | die ganze Welt | National Hurricane Center; Joint Typhoon Warning Center über NASA EONET |
| **Die heutige Unwetterprognose**: Gewitterrisiko von Marginal bis High | USA | NOAA Storm Prediction Center |
| **Erdbeben** der letzten 24 Stunden: Markierungen für die starken und die gespürten, Punkte für den Rest, Erschütterungslinien für die stärksten | die ganze Welt | US Geological Survey |
| **Vulkane mit erhöhter Warnstufe**, in ihrem Luftfahrt-Farbcode | Vulkane der USA | USGS Volcano Hazards Program |
| **Flüsse im Hochwasser oder mit vorhergesagtem Hochwasser**, gering, mäßig oder stark | Fluss- und Pegelmessstellen der USA | NOAA National Water Prediction Service |
| **Sturmberichte**: Tornados, Trichterwolken, Hagel, schädlicher Wind, Überflutungen | USA | NWS Local Storm Reports |
| **Winterberichte**: Schneehöhen, Blizzards, Graupel, gefrierender Regen und Eisstürme, extreme Kälte, Lawinen, Eisstau | USA | NWS Local Storm Reports |
| **Wetterwarnungen von MET Norway**, neben den US-Warnungen | Norwegen, seine Meere, Svalbard | MET Norway |
| **Seewetterberichte** für 56 Seegebiete und 39 Küstengebiete, zum Lesen anklicken | von der Nordsee bis zum Nordpol | MET Norway |
| **Ein Vorhersagepunkt in Longyearbyen**, Svalbard, anklicken für die Vorhersage | Svalbard | MET Norway |
| **Wetterradar** und **Blitze**: das schärfste Radar für das, was auf dem Bildschirm ist | die Welt | gezeichnet von der Live-Track-Kartenkarte |

### An Ihren Orten, ohne Einrichtung

„Ihre Orte“ sind Ihr Zuhause und jede Person, jedes Handy, jeder Gerätetracker
und jede Zone, die Sie überwachen lassen. Jeder Ort erhält (die Namen der
Entitäten sind englisch):

* **Alert at …**: eingeschaltet, solange der Ort in einer Wetterwarnung, nahe
  einem starken Erdbeben oder in der Gefahrenzone eines ausbrechenden Vulkans
  liegt. Bereit für Automationen: Licht einschalten, eine Benachrichtigung
  aufs Handy schicken, das Garagentor schließen.
* **Forecast at …**: eine vollständige Wettervorhersage, die dem Ort folgt,
  wenn er sich bewegt, für jede Wetterkarte auf Ihrem Dashboard. Vorhersagen
  des National Weather Service auf dem Festland der USA; die von MET Norway
  überall sonst und auf allen Gewässern.
* **Wind at …**, **Wind gust at …**, **Wind direction at …** und
  **Temperature at …**: was die nächste Wetterstation gemessen hat. Fahren
  Sie die Markise ein, wenn es böig wird.
* **Elevation at …** und **Depth at …**: die Höhe des Geländes und die
  Wassertiefe unter einem Boot.

### Mit Ihrem eigenen kostenlosen Schlüssel oder Konto

| Kostenloser Schlüssel oder Konto | Was es hinzufügt |
|---|---|
| **NASA FIRMS** Map-Key | Waldbrandwarnungen nahe Ihren Orten; jede Satelliten-Branderkennung auf der Karte |
| **AirNow** API-Schlüssel | Warnungen vor Waldbrandrauch und Luftqualität (PM2.5-AQI) an Ihren Orten in den USA; jede Luftqualitätsmessstelle auf der Karte |
| **KNMI** API-Schlüssel | schärferes Radar über den Niederlanden |
| **GeoNames** Benutzername | gemessener Wind und gemessene Temperatur außerhalb der USA, vom nächsten Flughafen; Name des Meeres und Wasser oder Land für die Tiefe |
| **MET Norway Frost** Client-ID | jede Wetterstation auf Svalbard und Jan Mayen auf der Karte; gemessener Wind und gemessene Temperatur an Ihren Orten in Norwegen und auf Svalbard |

Jeder ist in wenigen Minuten beschafft: [Schritt für Schritt unten](#kostenlose-schlüssel-die-mehr-freischalten-schritt-für-schritt).

---

## Teil von Live Track: die anderen Module

Live Track ist eine Reihe von Home-Assistant-Integrationen, eine für jede Art
von beweglichem Ding, alle auf derselben Kartenkarte gezeichnet. Jede
funktioniert allein; zusammen ergeben sie ein lebendiges Bild. Sie teilen sich
die Kartenkarte und eine Python-Bibliothek
([saw-livetrack](https://github.com/StrausbergAutomationWorks/LiveTrackCore)),
sodass eine weitere installierte Integration keine zusätzlichen Anfragen an
eine Quelle stellt, die eine andere bereits liest.

| Modul | Was es auf die Karte bringt | Status |
|---|---|---|
| [Live Track Aircraft](https://github.com/StrausbergAutomationWorks/LiveTrackAircraft) | Flugzeuge über Ihnen per ADS-B, mit Routen und Typsymbolen | veröffentlicht |
| [Live Track Ships](https://github.com/StrausbergAutomationWorks/LiveTrackShips) | Schiffe und Boote per AIS, in Ihrer Nähe oder irgendwo | veröffentlicht |
| [Live Track Commuter Rail](https://github.com/StrausbergAutomationWorks/LiveTrackCommuterRail) | Nahverkehrszüge in Nordamerika, Europa und Australien | veröffentlicht |
| [Live Track Intercity Rail](https://github.com/StrausbergAutomationWorks/LiveTrackIntercityRail) | Intercity- und Fernzüge in Nordamerika, Europa und Australien | veröffentlicht |
| [Live Track SALT](https://github.com/StrausbergAutomationWorks/LiveTrackSALT) | Flugzeuge und Schiffe der Einwanderungs- und Bundespolizeibehörden, aus öffentlichen Listen | veröffentlicht |
| **Live Track Weather** | Wetter, Stürme und Naturgefahren (dieses Modul) | in Entwicklung |
| Live Track Stations | Abfahrtstafeln und „Zeit zu gehen“-Hinweise für jeden Bahnhof | geplant |
| Live Track Satellites | Satelliten, die über Sie hinwegziehen | geplant |
| Live Track Freight Trains | Güter- und Arbeitszüge, wo Bahnen sie veröffentlichen | geplant |
| Live Track Transit | Stadtbusse, Straßenbahnen, Fähren und U-Bahnen | geplant |
| Live Track Intercity Buses | Fernbusse und Regionalbusse | geplant |
| Live Track Commuter Buses | Pendlerbusse | geplant |
| [LiveTrackMapCard](https://github.com/StrausbergAutomationWorks/LiveTrackMapCard) | die gemeinsame Kartenkarte, auf der jedes Modul zeichnet | veröffentlicht, mit jedem Modul installiert |

Alles ist kostenlos und quelloffen. Nichts wird für Sponsoren zurückgehalten.

---

## Bevor Sie beginnen

* **Home Assistant** 2025.1 oder neuer (entwickelt und getestet auf 2026.11).
* **Der Marketplace** (HACS) in Ihrem Home Assistant, um es bequem zu
  installieren und zu aktualisieren. Ohne ihn können Sie die Dateien von Hand
  kopieren.
* **Internetzugang** für Home Assistant: alles kommt von öffentlichen
  Wetterdiensten.
* **Optional: auto-entities** aus dem Marketplace, um die Markierungen für
  Stürme, Erdbeben und Stationen auf die Karte zu bringen (siehe
  [Die Karte auf ein Dashboard bringen](#die-karte-auf-ein-dashboard-bringen)).
  Die Warnungen und Flächen erscheinen auch ohne.
* Für die Grundfunktionen nichts zu bezahlen und kein Konto nötig. Die
  kostenlosen Schlüssel oben sind optional.

---

## Installation, Schritt für Schritt

### Über den Marketplace (empfohlen)

Live Track Weather ist noch nicht im Katalog des Marketplace. Fügen Sie es per
Link hinzu:

1. Öffnen Sie in Home Assistant **Einstellungen → Marketplace** (HACS).
2. Wählen Sie **Per Link hinzufügen** (oder das Dreipunktmenü →
   **Benutzerdefinierte Repositories**).
3. Geben Sie `StrausbergAutomationWorks/LiveTrackWeather` ein. Wenn nach dem
   Typ gefragt wird, wählen Sie **Integration**.
4. Suchen Sie **Live Track Weather** in der Liste und wählen Sie
   **Herunterladen** oder **Installieren**.
5. **Starten Sie Home Assistant neu**: **Einstellungen → System → Reparaturen**
   bietet den Neustart an, oder nutzen Sie **Einstellungen → System → Neu
   starten**.

### Von Hand

1. Laden Sie den Quellcode der
   [neuesten Veröffentlichung](https://github.com/StrausbergAutomationWorks/LiveTrackWeather/releases/latest)
   herunter.
2. Kopieren Sie dessen Ordner `custom_components/live_track_weather` in den
   Ordner `custom_components` Ihres Home-Assistant-Konfigurationsordners
   (legen Sie `custom_components` an, falls es ihn nicht gibt).
3. Starten Sie Home Assistant neu.

---

## Einrichtung, Schritt für Schritt

1. Öffnen Sie **Einstellungen → Geräte & Dienste**.
2. Wählen Sie **Integration hinzufügen** (unten rechts) und suchen Sie nach
   **Live Track Weather**.
3. Wählen Sie **Senden**. Es gibt nichts einzugeben: ein Live Track Weather
   deckt die ganze Welt ab.

Das ist alles. Warnungen, Stürme, Erdbeben, Vulkane, Hochwasser,
Sturmberichte und die Warnungen von MET Norway erscheinen innerhalb weniger
Minuten, und Ihr Zuhause wird überwacht: **Alert at Home**, **Forecast at
Home**, **Wind at Home**, **Temperature at Home**, **Elevation at Home** und
**Depth at Home**.

### Ändern, was überwacht wird: die Optionen

Öffnen Sie **Einstellungen → Geräte & Dienste → Live Track Weather →
Konfigurieren** (das Zahnrad). Jede Option in einfachen Worten:

| Option | Was sie tut | Standard |
|---|---|---|
| **Sekunden zwischen Abfragen** | wie oft die Liste der US-Warnungen abgerufen wird, 60 bis 900 Sekunden | 180 |
| **Zuhause überwachen** | Ihr Zuhause erhält die Sensoren „… at Home“ und die Vorhersage; ausschalten, um sie zu entfernen | ein |
| **Auch diese Personen, Gerätetracker oder Zonen überwachen** | jede erhält ihr eigenes „Alert at …“, „Forecast at …“, Wind, Temperatur, Höhe und Tiefe, die ihr folgen, wenn sie sich bewegt. Wählen Sie das Handy eines Familienmitglieds, den Tracker eines Wohnmobils, eine Zone für ein Ferienhaus | keine |
| **Warnungen, die einen Ort einschalten** | jede Warnung (auch Hinweise und Mitteilungen) oder nur mäßige, schwere oder extreme. Jede Warnung bleibt im Sensor aufgelistet | jede Warnung |
| **Gemessener Wind und Temperatur nur von Flughafenstationen** | aus: die nächste Station jeder Art (oft näher an einem Campingplatz); ein: nur Flughäfen | aus |
| **NASA FIRMS MAP_KEY** | Brandwarnungen und Branderkennungen (siehe [kostenlose Schlüssel](#kostenlose-schlüssel-die-mehr-freischalten-schritt-für-schritt)) | leer |
| **Ein Brand zählt im Umkreis von** | wie nah ein Brand sein muss, um einen Ort einzuschalten, 5 bis 150 km | 50 km |
| **AirNow-API-Schlüssel** | Rauchwarnungen und Luftqualitätsstationen | leer |
| **Rauch zählt ab PM2.5-AQI** | der Luftqualitätsindex, der einen Ort einschaltet | 90 |
| **Branderkennungen und Luftqualitätsstationen auf der Karte** | welche Regionen gezeichnet werden: die 48 zusammenhängenden Bundesstaaten und Hawaii, Alaska, Kanada, die ganze Welt (nur Brände) | keine |
| **Kleinstes Erdbeben auf der Punktebene der Karte** | lässt die kleinen Erdbebenpunkte unter einer Magnitude weg; die Markierungen bleiben | leer: jedes Beben |
| **KNMI-API-Schlüssel** | schärferes Radar über den Niederlanden | leer |
| **GeoNames-Benutzername** | Wetter außerhalb der USA, Meeresnamen | leer |
| **MET Norway Frost Client-ID** | Stationen auf Svalbard und Jan Mayen; gemessenes Wetter in Norwegen | leer |

Jeder Schlüssel wird einmal bei der Eingabe geprüft, und Sie erfahren, wenn
er nicht funktioniert. Lassen Sie ein Feld leer, um diesen Teil abzuschalten.

---

## Kostenlose Schlüssel, die mehr freischalten, Schritt für Schritt

Alle sind kostenlos und persönlich: Jede Person, die Live Track Weather
installiert, holt sich ihre eigenen. Fügen Sie jeden unter **Einstellungen →
Geräte & Dienste → Live Track Weather → Konfigurieren** ein.

### NASA FIRMS (Waldbrände)

1. Öffnen Sie <https://firms.modaps.eosdis.nasa.gov/api/map_key/>.
2. Geben Sie Ihre E-Mail-Adresse ein und fordern Sie einen **MAP_KEY** an. Er
   kommt per E-Mail.
3. Fügen Sie ihn in **NASA FIRMS MAP_KEY** ein, und stellen Sie **Ein Brand
   zählt im Umkreis von** ein, wenn 50 km für Sie nicht passen.
4. Um Brände auf der Karte zu sehen, kreuzen Sie außerdem eine Region unter
   **Branderkennungen und Luftqualitätsstationen auf der Karte** an.

### AirNow (Rauch und Luftqualität, USA)

1. Öffnen Sie <https://docs.airnowapi.org/> und wählen Sie **Request an
   AirNow API Account**.
2. Bestätigen Sie die E-Mail, melden Sie sich an und kopieren Sie Ihren
   **API key** von Ihrer Kontoseite.
3. Fügen Sie ihn in **AirNow-API-Schlüssel** ein.

### KNMI (Radar über den Niederlanden)

1. Registrieren Sie sich bei der KNMI Data Platform, <https://developer.dataplatform.knmi.nl/>.
2. Fordern Sie einen Schlüssel für die **WMS**-API an. (Ein Schlüssel für die
   Open-Data-API funktioniert hier nicht.)
3. Fügen Sie ihn in **KNMI-API-Schlüssel** ein. Die Karte verwendet dann über
   den Niederlanden das Radar des KNMI; ohne ihn das von RainViewer.

### GeoNames (Wetter außerhalb der USA)

1. Legen Sie ein kostenloses Konto an unter <https://www.geonames.org/login>.
2. Öffnen Sie die Bestätigungs-E-Mail von GeoNames und bestätigen Sie.
3. Melden Sie sich an, öffnen Sie Ihre Kontoseite und **aktivieren Sie die
   kostenlosen Webdienste**.
4. Geben Sie Ihren **Benutzernamen** (nicht Ihr Passwort) in
   **GeoNames-Benutzername** ein.

### MET Norway Frost (Stationen auf Svalbard, Wetter in Norwegen)

1. Öffnen Sie <https://frost.met.no/auth/requestCredentials.html>.
2. Geben Sie Ihre E-Mail-Adresse ein. Sie erhalten eine **Client-ID** und ein
   Client-Secret.
3. Fügen Sie die **Client-ID** in **MET Norway Frost Client-ID** ein. Das
   Secret wird nicht gebraucht.

---

## Die Karte auf ein Dashboard bringen

Die Karte ist [LiveTrackMapCard](https://github.com/StrausbergAutomationWorks/LiveTrackMapCard),
die Karte, auf der jedes Live-Track-Modul zeichnet. **Sie wird mit Live Track
Weather installiert**: nichts herunterzuladen, nichts nach `www` zu kopieren,
keine Ressource hinzuzufügen.

1. Öffnen Sie ein Dashboard, wählen Sie den Stift (**Dashboard bearbeiten**),
   dann **Karte hinzufügen**.
2. Scrollen Sie nach unten und wählen Sie **Manuell**.
3. Fügen Sie dies ein und wählen Sie **Speichern**:

```yaml
type: custom:auto-entities
card:
  type: custom:live-track-map-card
filter:
  include:
    - domain: geo_location
      attributes:
        source: live_track_weather
```

Die Wetterwarnungen, die Unwetterprognose, die Gebiete von MET Norway, die
Kegel und Zugbahnen der Stürme, die Erschütterungslinien der Erdbeben und die
Punktebenen erscheinen von selbst. Die Markierungen (Stürme, Erdbeben, Vulkane,
Pegel, die Vorhersage von Longyearbyen und die Stationen auf Svalbard) kommen
über den Filter oben, der
[auto-entities](https://github.com/thomasloven/lovelace-auto-entities) aus dem
Marketplace braucht. Sind andere Live-Track-Module installiert, fügen Sie für
jede ihrer Quellen einen weiteren Filter `- domain: geo_location` hinzu
(`live_track_aircraft`, `live_track_ships` und so weiter).

**Auf der Karte:**

* Die **Ebenensteuerung** oben rechts hat für jede Ebene ein Kästchen: die
  US-Warnungen, die Unwetterprognose, tropische Wirbelstürme, die Warnungen
  und Seewetterberichte von MET Norway, Erdbeben, Erdbebenerschütterung,
  Sturmberichte, Winterberichte, Branderkennungen, Luftqualitätsstationen,
  Wetterradar, Radarbewegung, Blitze und Wolken. Die Wahl jedes Betrachters
  wird in seinem eigenen Browser gespeichert.
* **Klicken** Sie auf eine Markierung, eine Fläche, eine Linie oder einen
  Punkt, um mehr darüber zu lesen.
* Die **Filterkarte** (`custom:live-track-map-filter-card`) kann die Stationen
  auf Svalbard ausblenden, als **Observed weather (MET Norway)**.
* Der Nachweis jeder Quelle erscheint in der Attributionszeile der Karte,
  solange ihre Daten angezeigt werden.

Sind die Ressourcen Ihrer Dashboards in YAML festgelegt
(`lovelace: resource_mode: yaml`), kann nichts für Sie registriert werden: Ein
Eintrag unter **Reparaturen** nennt dann die genaue Zeile, die Sie hinzufügen
müssen. Jede andere Kartenkarte, die `geo_location`-Entitäten zeigt, zeigt die
Markierungen, aber nicht die Warnungen, Gebiete oder Punkte.

---

## In Automationen verwenden

Alles ist eine gewöhnliche Home-Assistant-Entität, also funktioniert der
Automationseditor damit, ganz ohne Code.

**Eine Benachrichtigung aufs Handy, wenn das Zuhause in einer Warnung liegt:**

1. **Einstellungen → Automationen & Szenen → Automation erstellen → Neue
   Automation erstellen**.
2. **Wenn**: *Entität → Zustand*, Entität **Alert at Home**, nach **Unsicher**
   (ein).
3. **Dann tue**: *Benachrichtigungen → Benachrichtigung über mobile_app_…
   senden*, mit einer Nachricht wie `Wetterwarnung zu Hause: {{ state_attr('binary_sensor.live_track_weather_alert_at_home', 'highest') }}`.
4. Speichern.

**Die Markise bei einer Böe einfahren:** *Wenn* **Wind gust at Home** über
50 km/h (oder 30 mph) liegt, *dann* die Abdeckung der Markise schließen.

**Weitere Ideen:** ein Licht blinken lassen, wenn **Severe weather outlook**
3 (Enhanced) erreicht; den Besitzer des Wohnmobils warnen, wenn **Alert at
Camper** wegen eines Waldbrands im Umkreis von 50 km einschaltet;
benachrichtigen, wenn **Temperature at Cabin** unter den Gefrierpunkt fällt;
**Forecast at Boat** auf einer Wetterkarte zeigen, solange es auf See ist.

---

## Alles auf der Karte im Detail

### US-Wetterwarnungen

Jede aktive Warnung des National Weather Service: Warnungen, Vorwarnungen,
Hinweise und Mitteilungen für Countys, Landzonen sowie Küsten-, Hochsee- und
Waldbrandwetterzonen, durchscheinend gefüllt in der Farbe, die der
Wetterdienst jedem Ereignis gibt (die mit der höchsten Priorität, wo sich
Warnungen überlagern). Unwetterbezogene Warnungen wie Tornado-, Gewitter- und
Sturzflutwarnungen werden mit ihrem eigenen Polygon gezeichnet, nicht als
ganzes County. Es wird kein Standort festgelegt: Die Karte zeigt, was auf dem
Bildschirm ist. Die Zonenumrisse (11.651, auf etwa 500 m vereinfacht, etwa
3,6 MB) werden mit jeder Veröffentlichung ausgeliefert und von jedem Browser
einmal pro Veröffentlichung heruntergeladen.

**Sensor `US alerts`**: die Zahl der aktiven Warnungen; seine Attribute
enthalten die Liste, die die Karte zeichnet (`zones`, `polygons`, `styles`,
`updated`, `shapes_url`), die sich bei fast jeder Abfrage ändert und nicht im
Verlauf gespeichert wird.

### Tropische Wirbelstürme: Hurrikane, Taifune, Zyklone

Jeder aktive tropische Wirbelsturm der Welt, eine Markierung pro Sturm,
beschriftet mit seinem Namen und nach Kategorie eingefärbt: Tiefdruckgebiet
blau, tropischer Sturm blaugrün, Kategorien 1 bis 5 gold, orange,
dunkelorange, rot und magenta, posttropisch grau. Mit der Maus darüber sehen
Sie Klasse, Wind, Luftdruck und Zugrichtung.

* Stürme des **National Hurricane Center** (Atlantik, östlicher und zentraler
  Pazifik): der Vorhersagekegel (blau), die vorhergesagte Zugbahn (rot), die
  aktuellen Winde von 34, 50 und 64 Knoten (gelb, orange, rot) und die
  bisherige Zugbahn (schwarz).
* **Jedes andere Becken**, vom Joint Typhoon Warning Center über EONET der
  NASA: die Markierung und die bisherige Zugbahn. Ein Sturm, dessen letzte
  Position älter als 24 Stunden ist, wird nicht gezeigt.

Die Markierungen sind `geo_location.storm_<id>` (`geo_location.storm_ep222026`),
mit den Attributen `storm_class`, `storm_category` (TD, TS, H1-H5, PT),
`max_wind_kmh`, `pressure_hpa`, `course_deg`, `speed_kmh`, `last_seen`,
`advisory_number` und `storm_source`. Sie kommen und gehen mit den Stürmen und
haben keine eindeutige ID, daher können sie in der Oberfläche nicht umbenannt
werden. **Sensor `Tropical cyclones`**: die Zahl der Stürme.

### Unwetterprognose

Die kategorische Prognose für Tag 1 des Storm Prediction Center: wo heute
schwere Gewitter auftreten können, von 1 Marginal, 2 Slight, 3 Enhanced,
4 Moderate bis 5 High, in den eigenen Farben des Centers, unter den Warnungen.
**Sensor `Severe weather outlook`**: das höchste Risiko irgendwo in den USA
heute, 0 bis 5, aufgezeichnet, damit es eine Automation auslösen kann;
Attribute `risk`, `issued`, `valid_from`, `valid_to`. Das Gebiet allgemeiner
Gewitter wird nicht gezeichnet.

### Erdbeben

Jedes Erdbeben, das der US Geological Survey für die letzten 24 Stunden führt,
weltweit (etwa 240 am Tag):

* **Markierungen** ab Magnitude 4,5 und für jedes Beben, das Menschen gespürt
  haben, beschriftet mit der Magnitude (`geo_location.quake_<USGS id>`).
  Anklicken für Zeit, Tiefe, Spürmeldungen, die stärkste Erschütterung, die
  PAGER-Warnstufe und die Ereignisseite des USGS. Das „Tsunami-Kennzeichen“
  ist keine Warnung; Tsunamiwarnungen kommen von der NOAA (tsunami.gov).
* **Punkte** für jedes andere Beben (und Steinbruchsprengungen und Explosionen
  in Grau), auf einer eigenen Ebene: **Sensor `Earthquakes`**. Die Option
  **Kleinstes Erdbeben auf der Punktebene der Karte** lässt die kleinen weg.
* **Erschütterungslinien** (USGS ShakeMap) für die stärksten Beben des Tages,
  ab Magnitude 6 oder bei starker Erschütterung, höchstens fünf:
  **Sensor `Earthquake shaking`**.

### Vulkane mit erhöhter Warnstufe

Jeder US-Vulkan ab Warnstufe Advisory oder Luftfahrt-Farbcode Yellow, eine
Markierung in seinem Farbcode, beschriftet mit seinem Namen
(`geo_location.volcano_<number>`). Anklicken für Warnstufe, Farbcode, seit
wann, die Zusammenfassung des Observatoriums und Links zur Meldung und zur
Seite des Vulkans.

### Flüsse mit aktuellem oder vorhergesagtem Hochwasser

Jede Fluss- oder Pegelmessstelle der USA, die **jetzt mindestens geringes
Hochwasser** hat oder für die es vorhergesagt ist, beschriftet mit Minor,
Moderate oder Major in den Hochwasserfarben des Wetterdienstes
(`geo_location.river_<gauge id>`). **Ein dunkler Ring bedeutet, dass jetzt
Hochwasser ist**; ohne Ring ist es eine Vorhersage. Anklicken für den
aktuellen Pegelstand, den vorhergesagten Stand, die Hochwassermarken, den
Abfluss und die Seite der Messstelle. ⚠ Einige Messstellen haben Hochwassermarken,
die wie Platzhalter aussehen, und zeigen daher Major (Devils Lake, North
Dakota).

### Sturmberichte

Jeder NWS Local Storm Report der letzten 24 Stunden über einen Tornado oder
eine Wasserhose, eine Trichterwolke, Hagel, Gewitterwind oder -schäden, eine
Sturzflut oder eine Überflutung: rot für Tornados, blau für Wind, grün für
Hagel, blaugrün für Überflutungen. Ein bedeutender Bericht (jeder Tornado,
Hagel ab 2 Zoll, Wind ab 65 Knoten) ist größer und hat einen dunklen Ring.
Berichte verblassen mit dem Alter: unter einer Stunde, 1 bis 6 Stunden, 6 bis
24 Stunden. Anklicken für Art, Größe oder Geschwindigkeit, Ort, Zeit, das
NWS-Büro und die Bemerkungen. **Sensor `Storm reports`**: die Zahl der Punkte.
⚠ Das sind Berichte, wie Menschen sie senden, bevor der Wetterdienst sie
prüft, und sie können 30 Minuten bis zum Erscheinen brauchen.

### Winterberichte

Aus denselben Berichten, auf einer eigenen Ebene unter den Sturmberichten:
Schnee, starker Schneefall und Schneeschauer (schieferblau), Blizzards
(orangerot), Graupel (orchideenfarben), gefrierender Regen, gefrierender
Sprühregen und Eisstürme (dunkles Magenta), Schäden durch Schnee und Eis
(grau), extreme Kälte und Windchill (blau), Lawinen (braun) und Eisstau
(dunkles Blaugrün), jeweils mit einem dünnen dunklen Ring. Bedeutende Berichte
(12 Zoll Schnee, ein halber Zoll Graupel, ein Viertelzoll Eis, jeder Eissturm)
sind größer. Anklicken für die Menge in Zoll und cm oder mm, oder die
Temperatur in °F und °C. **Sensor `Winter reports`**. ⚠ Ein großer Sturm
bringt Tausende von Berichten; wo sich zwei überdecken würden, wird einer
gezeichnet, also hineinzoomen.

### MET Norway: Warnungen, Seewetterberichte, die Vorhersage von Longyearbyen

* **Warnungen** für Norwegens Land, Küste und Meere und die Meere bis zum
  Nordpol, im Gelb, Orange oder Rot von MET, neben den US-Warnungen. Anklicken
  für das Erwartete, die Folgen, die Ratschläge und den Zeitraum (auf
  Englisch). **Sensor `MET Norway warnings`**.
* **Seewetterberichte** für 56 Seegebiete und 39 Küstengebiete, die von
  Svalbard eingeschlossen, unter den Warnungen. Anklicken für die Vorhersage
  und jede Wind-, Eis- oder Polartief-Warnung.
  **Sensor `MET Norway marine forecasts`**.
* **Ein Vorhersagepunkt in Longyearbyen**, beschriftet mit der Temperatur;
  anklicken für die Vorhersage alle sechs Stunden für einen Tag
  (`geo_location.met_forecast_longyearbyen`).

### Gemessenes Wetter auf Svalbard und Jan Mayen (Frost-Client-ID)

Ein blaugrüner Punkt für jede Wetterstation auf Svalbard, der Bäreninsel, Hopen
und Jan Mayen, deren Temperatur und Wind beide weniger als zwei Stunden alt
sind (etwa 30), beschriftet mit der Temperatur (`geo_location.frost_sn99840`
für Svalbard Lufthavn und so weiter). Anklicken für Temperatur, Wind und
Richtung, die stärkste Böe der letzten Stunde, Luftfeuchtigkeit, Luftdruck,
Schneehöhe und die Zeit. Stationen, die nur die Temperatur melden, werden nicht
gezeichnet; von zwei Stationen, die näher als 1 km beieinander liegen, wird
eine gezeichnet. Werte, die Frost als sehr unsicher oder fehlerhaft markiert,
werden nicht verwendet; Werte, die bisher nur automatisch geprüft wurden (die
neueste Stunde von MET meist), werden gezeigt, und das Popup sagt „Automatic
check only“.

### Waldbrände und Luftqualität (FIRMS- und AirNow-Schlüssel)

Wählen Sie Regionen unter **Branderkennungen und Luftqualitätsstationen auf der
Karte**:

* **Branderkennungen** (braucht den FIRMS-Schlüssel): jede
  Satelliten-Branderkennung der letzten 24 Stunden (NOAA-20 und NOAA-21 VIIRS)
  als kleine rote Punkte. Werke, Raffinerien, Gasfackeln und andere ortsfeste
  Wärmequellen, die die NASA eingestuft hat, werden ausgelassen. Anklicken für
  den Zeitpunkt, den Satelliten, seine Feuerstrahlungsleistung und die
  Konfidenz der NASA. **Sensor `Fire detections`**.
* **Luftqualitätsstationen** (braucht den AirNow-Schlüssel; USA und Kanada):
  jede Feinstaubmessstelle (PM2.5), eingefärbt nach ihrem AQI in den Farben der
  EPA, stündlich. **Sensor `Air quality sites`**.

### Wetterradar, Blitze und Wolken

Von der Kartenkarte selbst gezeichnet, ohne Einrichtung: eine Radarebene, die
die schärfste Quelle für das wählt, was auf dem Bildschirm ist (RainViewer,
NOAA nowCOAST und GeoMet aus Kanada in Nordamerika; FMI aus Finnland und DWD
aus Deutschland in Europa; JMA aus Japan; KNMI über den Niederlanden mit Ihrem
Schlüssel), Radarbewegung, Blitze von nowCOAST und Wolken von den Satelliten
GOES und EUMETSAT.

---

## Alles an Ihren Orten im Detail

### Alert at …

**`Alert at Home`** (`binary_sensor.live_track_weather_alert_at_home`,
Geräteklasse *safety*: ein bedeutet unsicher), und einer für jede Person, jeden
Tracker und jede Zone, die Sie überwachen. Er schaltet sich ein, wenn der Ort:

* in einer **US-Wetterwarnung** oder einer **Warnung von MET Norway** liegt
  (nach der eigenen Regel des Wetterdienstes: eine Tornado- oder
  Hochwasserwarnung zählt innerhalb ihres Polygons, nicht im ganzen County;
  die Zonen kommen vom Wetterdienst selbst, sodass ein Ort an einer Küste oder
  einer County-Grenze die richtige Antwort erhält);
* in den letzten 24 Stunden nahe einem starken **Erdbeben** liegt: Magnitude 4
  im Umkreis von 50 km, 5 im Umkreis von 150 km, 6 im Umkreis von 300 km,
  7 im Umkreis von 600 km;
* in der Gefahrenzone eines **Vulkans** ab Watch oder Orange liegt (der
  National Volcanic Threat Layer des USGS, mit der Integration ausgeliefert);
* mit dem FIRMS-Schlüssel nahe einem **Waldbrand** liegt (innerhalb der von
  Ihnen eingestellten Entfernung, standardmäßig 50 km; Erkennungen erreichen
  Home Assistant 2 bis 4 Stunden nach dem Überflug des Satelliten);
* mit dem AirNow-Schlüssel im **Waldbrandrauch** liegt: die nächste
  PM2.5-Messstelle im Umkreis von 50 Meilen bei oder über dem von Ihnen
  eingestellten AQI, standardmäßig 90 (Orte in den USA).

Attribute: `alerts` (jede Warnung am Ort, die schlimmste zuerst, mit `event`,
`severity`, `headline`, `onset`, `ends`, `source` und einem Link), `highest`,
`zones`; mit den Schlüsseln `fires_near`, `nearest_fire_km`, `pm25_aqi`,
`pm25_site` und mehr. Die Zonen eines beweglichen Trackers werden erneut
abgefragt, nachdem er sich mehr als 1 km bewegt hat. Die NASA rät davon ab,
Branderkennungen allein für Entscheidungen vor Ort zu verwenden: Folgen Sie
Evakuierungsanordnungen.

### Forecast at …

**`Forecast at Home`** (`weather.live_track_weather_forecast_at_home`), und
eine für jeden überwachten Ort, für jede Wetterkarte und
`weather.get_forecasts`: täglich, Tag und Nacht, und stündlich.

* **Auf dem Festland der USA**: die Vorhersage des National Weather Service
  für das 2,5-km-Gitter des Orts, sieben Tage mit Tag und Nacht und dem
  Vorhersagetext, und stündlich für sechseinhalb Tage.
* **Überall sonst und auf allen Gewässern**: die Vorhersage von MET Norway,
  stündlich für etwa zweieinhalb Tage, dann sechsstündlich bis etwa zehn Tage.

Sie wechselt die Quelle, wenn der Ort sich bewegt (ein Boot verlässt den
Hafen, ein Wohnmobil fährt nach Kanada).

### Wind at …, Wind gust at …, Wind direction at …, Temperature at …

Was die nächste Wetterstation gemessen hat, für jeden überwachten Ort
(`sensor.live_track_weather_wind_at_home` und so weiter).

* **In den USA**: die nächste Station des National Weather Service aus jedem
  Netz (Flughäfen, Waldbrandwetter- und Straßenwetterstationen, Stationen von
  Freiwilligen) oder per Option nur Flughäfen; die nächste, bis zu drei, wenn
  eine nichts Aktuelles hat.
* **In Norwegen und auf Svalbard**, mit einer Frost-Client-ID: die nächste der
  eigenen Stationen von MET Norway (gemessen an 22 Orten in ganz Norwegen:
  0,4 bis 11 km entfernt). Die Böe ist die stärkste der letzten Stunde.
* **Anderswo**, mit einem GeoNames-Benutzernamen: der Wetterbericht (METAR)
  des nächsten Flughafens, im Umkreis von etwa 100 km.
* Ein Sensor ist **nicht verfügbar**, wenn kein Bericht, der jünger als zwei
  Stunden ist, seinen Wert enthält. Eine Böe ist unbekannt, wenn keine
  gemeldet wurde. Attribute: `station`, `station_name`, `provider`,
  `distance_km`, `observed`, `age_min`.

### Elevation at … und Depth at …

**`Elevation at Home`** und **`Depth at Home`**, und je einer für jeden
überwachten Ort, geprüft beim Start und nach einer Bewegung um mehr als 500 m.

* **Höhe** aus der ersten Quelle mit einem Wert: USGS 3DEP (USA und
  Grenzregionen, auf 1 m), Natural Resources Canada, Kartverket (norwegisches
  Festland), dann die Terrain Tiles von Mapzen für den Rest der Welt.
* **Auf dem Wasser** ist die Höhe die Wasseroberfläche und **Depth** die
  Tiefe unter dem Ort, von Kartverket in Norwegen oder NOAA NCEI anderswo (die
  Großen Seen eingeschlossen); auf dem Land unbekannt. Mit einem
  GeoNames-Benutzernamen nennt `sea` das Meer.
* ⚠ Bekannte Grenzen: Die Höhe auf Svalbard ist etwa 35 m zu hoch (keine
  bessere Quelle gefunden); Flüsse, Häfen und Stauseen haben keine Tiefe; in
  flachen Meeren ohne GeoNames ist die Höhe der Meeresboden; ein See unter dem
  Meeresspiegel, der nur über die Terrain Tiles erreicht wird, zeigt 0.

---

## Alle Entitäten, die es anlegt

| Entität | Was sie ist |
|---|---|
| `sensor.live_track_weather_us_alerts` | Zahl der aktiven US-Warnungen; die Liste, die die Karte zeichnet |
| `sensor.live_track_weather_tropical_cyclones` | Zahl der tropischen Wirbelstürme |
| `sensor.live_track_weather_severe_weather_outlook` | höchstes Unwetterrisiko heute, 0 bis 5 |
| `sensor.live_track_weather_met_norway_warnings` | gezeichnete Warnungen von MET Norway |
| `sensor.live_track_weather_met_norway_marine_forecasts` | Seewettergebiete von MET Norway |
| `sensor.live_track_weather_earthquakes` | Erdbebenpunkte auf der Karte |
| `sensor.live_track_weather_earthquake_shaking` | gezeichnete ShakeMaps |
| `sensor.live_track_weather_storm_reports` | gezeichnete Sturmberichte |
| `sensor.live_track_weather_winter_reports` | gezeichnete Winterberichte |
| `sensor.live_track_weather_fire_detections` | Branderkennungen (FIRMS-Schlüssel und eine Region) |
| `sensor.live_track_weather_air_quality_sites` | Luftqualitätsstationen (AirNow-Schlüssel und eine Region) |
| `sensor.live_track_weather_knmi_radar` | neuestes Radarbild des KNMI (KNMI-Schlüssel) |
| `geo_location.storm_…`, `quake_…`, `volcano_…`, `river_…`, `met_forecast_…`, `frost_…` | die Markierungen; sie kommen und gehen und haben keine eindeutige ID |
| `binary_sensor.live_track_weather_alert_at_home` | Alert at Home (und einer pro überwachtem Ort) |
| `weather.live_track_weather_forecast_at_home` | Forecast at Home (und eine pro überwachtem Ort) |
| `sensor.live_track_weather_wind_at_home`, `…_wind_gust_at_home`, `…_wind_direction_at_home`, `…_temperature_at_home` | gemessenes Wetter zu Hause (und pro Ort) |
| `sensor.live_track_weather_elevation_at_home`, `…_depth_at_home` | Höhe und Tiefe zu Hause (und pro Ort) |

Attribute, die sich bei jeder Abfrage ändern (Listen, Formen, Popups), werden
aus dem Verlauf von Home Assistant herausgehalten, damit Ihre Datenbank nicht
mit ihnen wächst.

---

## Was es sendet und herunterlädt

**Zu Ihrem Standort.** Der Standort Ihres Zuhauses und jedes überwachten Orts
wird, auf etwa 11 m gerundet, nur dorthin gesendet, wo ein Dienst ihn braucht:
an den National Weather Service, um die Zonen, das Vorhersagegitter und die
Stationen des Orts zu ermitteln; außerhalb des US-Vorhersagegebiets an MET
Norway für dessen Vorhersage; an den USGS (und, wo der USGS nichts hat, an
Natural Resources Canada, Kartverket und NOAA NCEI) für Höhe und Tiefe, beim
Start und nach einer Bewegung um mehr als 500 m; mit Ihren Schlüsseln an NASA
FIRMS (ein Rechteck um den Ort), AirNow, GeoNames und Frost von MET Norway.
Schalten Sie **Zuhause überwachen** aus und überwachen Sie nichts anderes, dann
wird kein Standort gesendet. Sonst wird nichts über Sie irgendwohin gesendet.

**Wie viel.** Die Liste der US-Warnungen etwa 100 KB alle 3 Minuten
(einstellbar); die anderen fragen, wo der Dienst es erlaubt, nur nach einer
geänderten Datei: Hurrikanmeldungen alle 5 Minuten, EONET alle 30, die
Unwetterprognose alle 5, die Warnungen von MET Norway alle 5, Seewetterberichte
alle 15-30 und Punktvorhersagen alle 30 (jeweils zufällig eine Minute später,
wie MET es verlangt, und nach einer Ablehnung 30 Minuten lang nichts); USGS-Erdbeben
alle 5 Minuten (etwa 170 KB), Vulkane alle 10, Flüsse alle 30, Sturmberichte
alle 10; Frost alle 10 Minuten (etwa 80 KB); GeoNames innerhalb der Hälfte
seiner 10.000 kostenlosen Credits pro Tag; KNMI höchstens etwa 24 Anfragen pro
Stunde und nur, solange eine Karte es zeigt. Nach einem Fehler wird jeder
Dienst eine Weile in Ruhe gelassen, bevor er wieder gefragt wird.

---

## Sprachen

Diese README: [English](README.md), **Deutsch**, [Français](README.fr.md),
[Nederlands](README.nl.md), [简体中文](README.zh-Hans.md),
[Español](README.es.md), [Italiano](README.it.md), [Dansk](README.da.md) und
[Kalaallisut](README.kl.md) (ein kurzer Entwurf; bis ein Muttersprachler ihn
gelesen hat, ist die dänische Seite die verlässliche). Jede übersetzte README
ist vollständig.

Der Einrichtungsdialog und die Optionen erscheinen in der Sprache Ihres Home
Assistant, wenn es eine dieser ist: English, Dansk, Deutsch, Español,
Français, Gaeilge, Íslenska, Italiano, Nederlands, Norsk Bokmål, Polski,
Português, Português (BR), Suomi, Svenska und 简体中文. Jede andere Sprache
zeigt Englisch. Die Namen der Entitäten (**Alert at Home** und so weiter) und
die Beschriftungen der Kartenkarte sind in jeder Sprache englisch.

Einen Fehler in einer Übersetzung gefunden, oder eine andere Sprache nötig?
Sagen Sie es uns unter
<https://github.com/StrausbergAutomationWorks/LiveTrackWeather/issues>.

---

## Danksagungen und Lizenzen

* Der National Weather Service, das National Hurricane Center, das Storm
  Prediction Center, der National Water Prediction Service, das Joint Typhoon
  Warning Center, die NASA und der US Geological Survey sind Behörden der
  US-Regierung; ihre Daten sind Werke der US-Regierung. AirNow-Daten sind
  vorläufig und nicht geprüft (US EPA und Partner).
* **MET Norway**: Daten unter der Norwegian Licence for Open Government Data
  (NLOD) 2.0 und Creative Commons Attribution 4.0; die Beobachtungen von Frost
  unter Creative Commons Attribution 3.0 Norway. Diese Integration rundet die
  Gebiete, färbt die Warnungen neu ein und rechnet Einheiten um.
* **KNMI**: Radar unter Creative Commons Attribution 4.0, zu Kartenkacheln
  zugeschnitten und skaliert.
* **GeoNames**: METAR-Berichte und Meeresnamen unter Creative Commons
  Attribution 4.0.
* **Höhe**: CDEM von Natural Resources Canada, Open Government Licence -
  Canada; Kartverket, Creative Commons Attribution 4.0; NOAA NCEI,
  US-Regierung. **Terrain Tiles**: Mapzen und die in der Joerd-Attribution von
  Mapzen genannten Quellen (`tilezen/joerd`, `docs/attribution.md`), hier im
  Wortlaut: ArcticDEM terrain data DEM(s) were created from DigitalGlobe, Inc.,
  imagery and funded under National Science Foundation awards 1043681, 1559691,
  and 1542736; Australia terrain data © Commonwealth of Australia (Geoscience
  Australia) 2017; Austria terrain data © offene Daten Österreichs – Digitales
  Geländemodell (DGM) Österreich; Canada terrain data contains information
  licensed under the Open Government Licence – Canada; Europe terrain data
  produced using Copernicus data and information funded by the European Union -
  EU-DEM layers; Global ETOPO1 terrain data U.S. National Oceanic and
  Atmospheric Administration; Mexico terrain data source: INEGI, Continental
  relief, 2016; New Zealand terrain data Copyright 2011 Crown copyright (c) Land
  Information New Zealand and the New Zealand Government (All rights reserved);
  Norway terrain data © Kartverket; United Kingdom terrain data © Environment
  Agency copyright and/or database right 2015. All rights reserved; United
  States 3DEP (formerly NED) and global GMTED2010 and SRTM terrain data courtesy
  of the U.S. Geological Survey.
* **Vulkan-Gefahrenzonen**: USGS National Volcanic Threat Layer (2024, CC0).

Keine dieser Organisationen hat diese Integration erstellt oder unterstützt.

**Code**: MIT, in [LICENSE](LICENSE).

**Für Entwickler:** `tools/build_shapes.py` erstellt die Datei der
Warnzonen aus den NWS-Shapefiles neu (<https://www.weather.gov/gis/>) und
`tools/build_colours.py` die Farbtabelle aus der Gefahrenkartenseite des NWS;
die Tests laufen mit `python -m unittest discover -s tests`.

---

## Stichwörter

Home Assistant Wetter · Home Assistant Wetterwarnungen · Unwetterwarnung ·
NWS alerts · National Weather Service · Wetterwarnkarte · Tornadowarnung ·
Gewitterwarnung · Sturzflutwarnung · Wintersturmwarnung · Hurrikan-Tracker ·
Tropensturm · Taifun · Zyklon · Hurrikankegel · NHC · JTWC · SPC outlook ·
Unwetterprognose · Erdbebenkarte · Erdbebenwarnung · USGS Erdbeben · ShakeMap ·
Vulkanwarnung · Hochwasserkarte · Pegel · NWPS · Sturmberichte · Hagel ·
Schneehöhe · Blizzard · Eissturm · Waldbrandkarte · Waldbrandwarnung ·
Branderkennung · NASA FIRMS · VIIRS · Rauchwarnung · Luftqualität · AQI ·
PM2.5 · AirNow · Wetterradar · Regenradar · Blitzkarte · MET Norway · yr ·
Svalbard Wetter · Longyearbyen · Jan Mayen · Frost API · Seewetterbericht ·
KNMI Radar · GeoNames · METAR · Wetterstation · Windböen-Sensor ·
Temperatursensor · Vorhersage für einen Gerätetracker · Wohnmobil Wetter ·
Boot Wetter · Höhensensor · Wassertiefe · geo_location · binary_sensor ·
weather entity · Kartenkarte · Lovelace · HACS · Marketplace · Live Track ·
LiveTrack · StrausbergAutomationWorks
