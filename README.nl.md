# Live Track Weather

[English](README.md) · [Deutsch](README.de.md) · [Français](README.fr.md) · **Nederlands** · [简体中文](README.zh-Hans.md) · [Español](README.es.md) · [Italiano](README.it.md) · [Dansk](README.da.md) · [Kalaallisut](README.kl.md) · [Alle talen](#talen)

**Weerwaarschuwingen, stormen, aardbevingen, overstromingen, natuurbranden,
radar en actueel weer voor Home Assistant, op één kaart.** Live Track Weather
zet officiële weerwaarschuwingen, orkanen en tyfoons, aardbevingen,
vulkanen, rivieroverstromingen, storm- en sneeuwmeldingen, gegevens over
natuurbranden en rook, zeeweerberichten en weerstations op je Home
Assistant-kaart, en bewaakt je huis, de telefoons van je gezin en je camper op
gevaar. Stormen, aardbevingen, radar en verwachtingen gelden voor de hele
wereld; de VS, Noorwegen en Spitsbergen zijn het meest gedetailleerd gedekt
([waar het werkt](#waar-het-werkt)).

> **Live Track Weather is één module van Live Track**, een familie van Home
> Assistant-integraties die alles wat beweegt, en het weer waar het doorheen
> beweegt, op één gedeelde kaart tekenen: vliegtuigen, schepen, treinen, en nu
> het weer. Installeer het los of naast de andere modules
> ([lijst hieronder](#onderdeel-van-live-track-de-andere-modules)).

> **Het groeit, en ideeën zijn welkom.** Live Track Weather dekt vandaag
> stormen, aardbevingen, radar en verwachtingen wereldwijd, en waarschuwingen
> voor de VS, Noorwegen en Spitsbergen. We voegen meer landen, weerdiensten en
> gevaren toe. Ontbreekt de jouwe? [Stel het voor](#help-het-groeien), of voeg
> het zelf toe: we helpen je daarbij.

**Status: 0.1.0, de eerste release.** Via een link aan de Marketplace toe te
voegen ([zie hieronder](#installeren-stap-voor-stap)); in de catalogus van de Marketplace staat het nog niet.

Eigen werk van StrausbergAutomationWorks. Niet verbonden met, of
onderschreven door, een van de organisaties waarvan het gegevens toont: in de
VS de National Weather Service, NOAA, het National Hurricane Center, het Storm
Prediction Center, het Joint Typhoon Warning Center, NASA, de US Geological
Survey en de EPA; MET Norway (Noorwegen); het KNMI (Nederland); of GeoNames.

> ⚠ **Geen noodwaarschuwingssysteem.** Het toont openbare gegevens, op zijn
> best een paar minuten vertraagd. Gebruik voor waarschuwingen die levens
> beschermen de noodmeldingen van je telefoon, je nationale weerdienst, een
> weerradio waar je land er een heeft, en je plaatselijke overheid, en volg
> evacuatiebevelen op.

---

## Inhoud

1. [Alles wat het doet](#alles-wat-het-doet)
2. [Waar het werkt](#waar-het-werkt)
3. [Onderdeel van Live Track: de andere modules](#onderdeel-van-live-track-de-andere-modules)
4. [Voordat je begint](#voordat-je-begint)
5. [Installeren, stap voor stap](#installeren-stap-voor-stap)
6. [Instellen, stap voor stap](#instellen-stap-voor-stap)
7. [Gratis sleutels die meer aanzetten, stap voor stap](#gratis-sleutels-die-meer-aanzetten-stap-voor-stap)
8. [De kaart op een dashboard zetten](#de-kaart-op-een-dashboard-zetten)
9. [Gebruiken in automatiseringen](#gebruiken-in-automatiseringen)
10. [Alles op de kaart, in detail](#alles-op-de-kaart-in-detail)
11. [Alles bij je plaatsen, in detail](#alles-bij-je-plaatsen-in-detail)
12. [Alle entiteiten die het aanmaakt](#alle-entiteiten-die-het-aanmaakt)
13. [Wat het verstuurt en downloadt](#wat-het-verstuurt-en-downloadt)
14. [Help het groeien](#help-het-groeien)
15. [Talen](#talen)
16. [Vermeldingen en licenties](#vermeldingen-en-licenties)
17. [Trefwoorden](#trefwoorden)

---

## Alles wat het doet

### Op de kaart, zonder iets in te stellen

| Wat | Waar | Bron |
|---|---|---|
| **Weerwaarschuwingen**: waarschuwingen, voorwaarschuwingen, adviezen en mededelingen, doorschijnend gevuld in de eigen kleuren van de Weather Service | de hele VS, de kusten en wateren | National Weather Service (VS) |
| **Waarschuwingen voor tornado's, zware onweersbuien, plotselinge overstromingen en andere stormgebonden waarschuwingen**, getekend met hun eigen polygoon | de VS | National Weather Service |
| **Orkanen, tropische stormen, tyfoons en cyclonen**: een markering per storm, de verwachtingskegel, de verwachte baan, het windveld en de afgelegde baan | de hele wereld | National Hurricane Center (VS); Joint Typhoon Warning Center (VS) via NASA EONET |
| **De verwachting voor zwaar onweer van vandaag**: risico op zware onweersbuien van Marginal tot High | de VS | NOAA Storm Prediction Center |
| **Aardbevingen** van de afgelopen 24 uur: markeringen voor de grote en de gevoelde, stippen voor de rest, schudlijnen voor de sterkste | de hele wereld | US Geological Survey |
| **Vulkanen met verhoogde status**, in hun kleurcode voor de luchtvaart | vulkanen in de VS | USGS Volcano Hazards Program |
| **Rivieren die overstromen of naar verwachting overstromen**, gering, matig of ernstig | rivier- en getijdenmeters in de VS | NOAA National Water Prediction Service |
| **Stormmeldingen**: tornado's, trechterwolken, hagel, schadelijke wind, overstromingen | de VS | NWS Local Storm Reports |
| **Wintermeldingen**: sneeuwhoogtes, sneeuwstormen, ijzel en natte sneeuw, ijsstormen, extreme kou, lawines, ijsdammen | de VS | NWS Local Storm Reports |
| **De weerwaarschuwingen van MET Norway**, naast die van de VS | Noorwegen, de zeeën, Spitsbergen | MET Norway |
| **Zeeweerberichten** voor 56 zeegebieden en 39 kustgebieden, klik om te lezen | van de Noordzee tot de Noordpool | MET Norway |
| **Een verwachtingsstip bij Longyearbyen**, Spitsbergen, klik voor de verwachting | Spitsbergen | MET Norway |
| **Weerradar** en **bliksem**: de scherpste radar voor wat er op het scherm staat | de wereld | getekend door de Live Track-kaartkaart |

### Bij je plaatsen, zonder iets in te stellen

"Je plaatsen" zijn je huis, en elke persoon, telefoon, apparaattracker of zone
die je laat bewaken. Elke plaats krijgt (de namen van de entiteiten zijn
Engels):

* **Alert at …**: aan zolang de plaats binnen een weerwaarschuwing ligt, bij
  een sterke aardbeving of in de gevarenzone van een uitbarstende vulkaan.
  Klaar voor automatiseringen: zet de lampen aan, stuur een melding naar de
  telefoon, sluit de garage.
* **Forecast at …**: een volledige weersverwachting die met de plaats
  meebeweegt, voor elke weerkaart op je dashboard. Verwachtingen van de
  National Weather Service op het vasteland van de VS; die van MET Norway
  overal elders, en op al het water.
* **Wind at …**, **Wind gust at …**, **Wind direction at …** en
  **Temperature at …**: wat het dichtstbijzijnde weerstation heeft gemeten.
  Haal de zonnekap in als het hard gaat waaien.
* **Elevation at …** en **Depth at …**: de hoogte van de grond, en de diepte
  van het water onder een boot.

### Aangezet met je eigen gratis sleutel of account

| Gratis sleutel of account | Wat het toevoegt |
|---|---|
| **NASA FIRMS**-kaartsleutel | natuurbrandwaarschuwingen bij je plaatsen; elke satellietdetectie van brand op de kaart |
| **AirNow** (VS) API-sleutel | waarschuwingen voor rook van natuurbranden en luchtkwaliteit (PM2.5-AQI) bij je plaatsen in de VS; elke luchtkwaliteitsmeter op de kaart |
| **KNMI** (Nederland) API-sleutel | scherpere radar boven Nederland |
| **GeoNames**-gebruikersnaam | gemeten wind en temperatuur buiten de VS, van de dichtstbijzijnde luchthaven; de naam van de zee en water of land voor de diepte |
| **MET Norway Frost**-client-ID | elk weerstation op Spitsbergen en Jan Mayen op de kaart; gemeten wind en temperatuur bij je plaatsen in Noorwegen en op Spitsbergen |

Elk is in een paar minuten te krijgen: [stap voor stap hieronder](#gratis-sleutels-die-meer-aanzetten-stap-voor-stap).

---

## Waar het werkt

| Regio | Wat je krijgt | Bron | Nodig |
|---|---|---|---|
| **De hele wereld** | orkanen, tyfoons en cyclonen; aardbevingen; weerradar, bliksem en wolken; een verwachting bij elk van je plaatsen; hoogte en zeediepte bij je plaatsen | National Hurricane Center, Joint Typhoon Warning Center en NASA (VS); US Geological Survey; de radarbronnen van de kaartkaart; MET Norway; Mapzen Terrain Tiles; NOAA NCEI | niets |
| **De hele wereld** | satellietdetecties van brand op de kaart, en natuurbrandwaarschuwingen bij je plaatsen | NASA FIRMS (VS) | een gratis FIRMS-kaartsleutel |
| **De hele wereld**, buiten de VS | gemeten wind en temperatuur bij je plaatsen, van de dichtstbijzijnde luchthaven; de naam van de zee | GeoNames | een gratis GeoNames-gebruikersnaam |
| **Azië**: Japan | scherpere radar | Japan Meteorological Agency | niets |
| **Europa**: Duitsland | scherpere radar | Deutscher Wetterdienst | niets |
| **Europa**: Finland | scherpere radar | Finnish Meteorological Institute | niets |
| **Europa**: Nederland | scherpere radar | KNMI | een gratis KNMI-sleutel |
| **Europa**: Noorwegen, Spitsbergen en Jan Mayen | weerwaarschuwingen; zeeweerberichten van de Noordzee tot de Noordpool; een verwachting voor Longyearbyen; hoogte en zeediepte in Noorwegen | MET Norway; Kartverket | niets |
| **Europa**: Noorwegen, Spitsbergen en Jan Mayen | gemeten weer bij je plaatsen; elk weerstation op Spitsbergen en Jan Mayen op de kaart | MET Norway Frost | een gratis Frost-client-ID |
| **Noord-Amerika**: Canada | scherpere radar; hoogte bij je plaatsen | Environment and Climate Change Canada (GeoMet); Natural Resources Canada | niets |
| **Noord-Amerika**: Canada | luchtkwaliteitsstations op de kaart | AirNow (VS) en partners | een gratis AirNow-sleutel |
| **Noord-Amerika**: de VS | weerwaarschuwingen en stormgebonden waarschuwingen; de verwachting voor zwaar onweer; vulkanen; rivieren die buiten hun oevers treden; storm- en wintermeldingen; de verwachting en het gemeten weer van de Weather Service bij je plaatsen; hoogte | National Weather Service, NOAA, US Geological Survey | niets |
| **Noord-Amerika**: de VS | waarschuwingen voor rook van natuurbranden bij je plaatsen; luchtkwaliteitsstations op de kaart | AirNow | een gratis AirNow-sleutel |

⚠ Weerwaarschuwingen komen tot nu toe alleen uit de VS en Noorwegen. Overal
elders krijg je de wereldwijde lagen hierboven, een verwachting en gemeten
weer bij je plaatsen, en waarschuwingen voor sterke aardbevingen in de buurt
en (met een sleutel) natuurbranden.

Staat het er niet bij? [Laat het ons weten](#help-het-groeien). Waar een
weerdienst zijn waarschuwingen of gegevens openlijk publiceert, kijken we of
we die kunnen toevoegen.

---

## Onderdeel van Live Track: de andere modules

Live Track is een reeks Home Assistant-integraties, één per soort bewegend
ding, allemaal getekend op dezelfde kaartkaart. Elk werkt op zichzelf; samen
vormen ze één levend beeld. Ze delen de kaartkaart en een Python-bibliotheek
([saw-livetrack](https://github.com/StrausbergAutomationWorks/LiveTrackCore)),
dus een extra integratie installeren voegt geen verzoeken toe aan een bron die
een andere al leest.

| Module | Wat het op de kaart zet | Status |
|---|---|---|
| [Live Track Aircraft](https://github.com/StrausbergAutomationWorks/LiveTrackAircraft) | vliegtuigen boven je via ADS-B, met routes en typepictogrammen | uitgebracht |
| [Live Track Ships](https://github.com/StrausbergAutomationWorks/LiveTrackShips) | schepen en boten via AIS, bij je in de buurt of waar dan ook | uitgebracht |
| [Live Track Commuter Rail](https://github.com/StrausbergAutomationWorks/LiveTrackCommuterRail) | forensentreinen in Noord-Amerika, Europa en Australië | uitgebracht |
| [Live Track Intercity Rail](https://github.com/StrausbergAutomationWorks/LiveTrackIntercityRail) | intercity- en langeafstandstreinen in Noord-Amerika, Europa en Australië | uitgebracht |
| [Live Track SALT](https://github.com/StrausbergAutomationWorks/LiveTrackSALT) | vliegtuigen en schepen van immigratie- en federale opsporingsdiensten, uit openbare lijsten | uitgebracht |
| **Live Track Weather** | weer, stormen en natuurgevaren (deze module) | uitgebracht |
| Live Track Stations | vertrekborden en "tijd om te gaan"-meldingen voor elk station | gepland |
| Live Track Satellites | satellieten die over je heen trekken | gepland |
| Live Track Freight Trains | goederen- en werktreinen waar spoorwegen ze publiceren | gepland |
| Live Track Transit | stadsbussen, trams, veerboten en metro | gepland |
| Live Track Intercity Buses | intercity- en streekbussen | gepland |
| Live Track Commuter Buses | forensenbussen | gepland |
| [LiveTrackMapCard](https://github.com/StrausbergAutomationWorks/LiveTrackMapCard) | de gedeelde kaartkaart waarop elke module tekent | uitgebracht, met elke module geïnstalleerd |

Alles is gratis en open source. Niets wordt achtergehouden voor sponsors.

---

## Voordat je begint

* **Home Assistant** 2026.11 of nieuwer.
* **De Marketplace** (HACS) in je Home Assistant, om het makkelijk te
  installeren en bij te werken. Zonder kun je de bestanden met de hand
  kopiëren.
* **Internettoegang** voor Home Assistant: alles komt van openbare
  weerdiensten.
* **Optioneel: auto-entities** uit de Marketplace, om de markeringen van
  stormen, aardbevingen en stations op de kaart te zetten (zie
  [De kaart op een dashboard zetten](#de-kaart-op-een-dashboard-zetten)). De
  waarschuwingen en vormen verschijnen ook zonder.
* Niets te betalen en geen account nodig voor de basis. De gratis sleutels
  hierboven zijn optioneel.

---

## Installeren, stap voor stap

### Via de Marketplace (aanbevolen)

Live Track Weather staat nog niet in de catalogus van de Marketplace. Voeg het
toe via de link:

1. Open in Home Assistant **Instellingen → Marketplace** (HACS).
2. Kies **Toevoegen via link** (of het menu met drie puntjes →
   **Aangepaste repositories**).
3. Vul `StrausbergAutomationWorks/LiveTrackWeather` in. Als om het type wordt
   gevraagd, kies **Integratie**.
4. Zoek **Live Track Weather** in de lijst en kies **Downloaden** of
   **Installeren**.
5. **Herstart Home Assistant**: **Instellingen → Systeem → Reparaties** biedt
   de herstart aan, of gebruik **Instellingen → Systeem → Herstart**.

### Met de hand

1. Download de broncode van de
   [nieuwste release](https://github.com/StrausbergAutomationWorks/LiveTrackWeather/releases/latest).
2. Kopieer de map `custom_components/live_track_weather` daarvan naar de map
   `custom_components` van je Home Assistant-configuratiemap (maak
   `custom_components` aan als die er niet is).
3. Herstart Home Assistant.

---

## Instellen, stap voor stap

1. Open **Instellingen → Apparaten en diensten**.
2. Kies **Integratie toevoegen** (rechtsonder) en zoek naar
   **Live Track Weather**.
3. Kies **Verzenden**. Er hoeft niets ingevuld te worden: één Live Track
   Weather dekt de hele wereld.

Dat is alles. Waarschuwingen, stormen, aardbevingen, vulkanen,
overstromingen, stormmeldingen en de waarschuwingen van MET Norway verschijnen
binnen een paar minuten, en je huis wordt bewaakt: **Alert at Home**,
**Forecast at Home**, **Wind at Home**, **Temperature at Home**, **Elevation
at Home** en **Depth at Home**.

### Wijzigen wat het bewaakt: de opties

Open **Instellingen → Apparaten en diensten → Live Track Weather →
Configureer** (het tandwiel). Elke optie in gewone woorden:

| Optie | Wat het doet | Standaard |
|---|---|---|
| **Seconden tussen opvragingen** | hoe vaak de lijst met Amerikaanse waarschuwingen wordt opgehaald, 60 tot 900 seconden | 180 |
| **Huis bewaken** | je huis krijgt de sensoren "… at Home" en de verwachting; zet uit om ze te verwijderen | aan |
| **Bewaak ook deze personen, apparaattrackers of zones** | elk krijgt een eigen "Alert at …", "Forecast at …", wind, temperatuur, hoogte en diepte, die meebewegen. Kies de telefoon van een familielid, de tracker van een camper, een zone voor een vakantiehuis | geen |
| **Waarschuwingen die een plaats aanzetten** | elke waarschuwing (ook adviezen en mededelingen), of alleen matige, ernstige of extreme. Elke waarschuwing blijft in de sensor vermeld | elke waarschuwing |
| **Gemeten wind en temperatuur alleen van luchthavenstations** | uit: het dichtstbijzijnde station van welke soort ook (vaak dichter bij een camping); aan: alleen luchthavens | uit |
| **NASA FIRMS MAP_KEY** | brandwaarschuwingen en branddetecties (zie [gratis sleutels](#gratis-sleutels-die-meer-aanzetten-stap-voor-stap)) | leeg |
| **Een brand telt binnen** | hoe dichtbij een brand moet zijn om een plaats aan te zetten, 5 tot 150 km (3 tot 93 mijl) | 50 km (31 mijl) |
| **AirNow-API-sleutel** | rookwaarschuwingen en luchtkwaliteitsstations | leeg |
| **Rook telt vanaf PM2.5-AQI** | de luchtkwaliteitsindex die een plaats aanzet | 90 |
| **Branddetecties en luchtkwaliteitsstations op de kaart** | welke regio's getekend worden: de 48 aaneengesloten staten en Hawaï, Alaska, Canada, de hele wereld (alleen branden) | geen |
| **Kleinste aardbeving op de puntenlaag van de kaart** | laat de kleine aardbevingsstippen onder een magnitude weg; de markeringen blijven | leeg: elke beving |
| **KNMI-API-sleutel** | scherpere radar boven Nederland | leeg |
| **GeoNames-gebruikersnaam** | weer buiten de VS, namen van zeeën | leeg |
| **MET Norway Frost-client-ID** | stations op Spitsbergen en Jan Mayen; gemeten weer in Noorwegen | leeg |

Elke sleutel wordt één keer gecontroleerd als je hem invult, en je hoort het
als hij niet werkt. Laat een veld leeg om dat deel uit te zetten.

---

## Gratis sleutels die meer aanzetten, stap voor stap

Ze zijn allemaal gratis en persoonlijk: iedereen die Live Track Weather
installeert, haalt er zelf een. Plak elke sleutel in **Instellingen →
Apparaten en diensten → Live Track Weather → Configureer**.

### NASA FIRMS (natuurbranden)

1. Open <https://firms.modaps.eosdis.nasa.gov/api/map_key/>.
2. Vul je e-mailadres in en vraag een **MAP_KEY** aan. Die komt per e-mail.
3. Plak hem in **NASA FIRMS MAP_KEY**, en stel **Een brand telt binnen** in
   als 50 km (31 mijl) niet bij je past.
4. Om branden op de kaart te zien, vink je ook een regio aan onder
   **Branddetecties en luchtkwaliteitsstations op de kaart**.

### AirNow (rook en luchtkwaliteit, VS)

1. Open <https://docs.airnowapi.org/> en kies **Request an AirNow API
   Account**.
2. Bevestig de e-mail, log in en kopieer je **API key** van je accountpagina.
3. Plak hem in **AirNow-API-sleutel**.

### KNMI (radar boven Nederland)

1. Registreer je bij het KNMI Data Platform, <https://developer.dataplatform.knmi.nl/>.
2. Vraag een sleutel aan voor de **WMS**-API. (Een sleutel voor de Open
   Data-API werkt hier niet.)
3. Plak hem in **KNMI-API-sleutel**. De kaart gebruikt dan boven Nederland de
   radar van het KNMI; zonder sleutel die van RainViewer.

### GeoNames (weer buiten de VS)

1. Maak een gratis account aan op <https://www.geonames.org/login>.
2. Open de bevestigingsmail die GeoNames stuurt, en bevestig.
3. Log in, open je accountpagina en **zet de gratis webdiensten aan**.
4. Vul je **gebruikersnaam** (niet je wachtwoord) in bij
   **GeoNames-gebruikersnaam**.

### MET Norway Frost (stations op Spitsbergen, weer in Noorwegen)

1. Open <https://frost.met.no/auth/requestCredentials.html>.
2. Vul je e-mailadres in. Je krijgt een **client-ID** en een client-secret.
3. Plak de **client-ID** in **MET Norway Frost-client-ID**. Het secret is
   niet nodig.

---

## De kaart op een dashboard zetten

De kaart is [LiveTrackMapCard](https://github.com/StrausbergAutomationWorks/LiveTrackMapCard),
de kaart waarop elke Live Track-module tekent. **Hij wordt met Live Track
Weather geïnstalleerd**: niets te downloaden, niets naar `www` te kopiëren,
geen bron toe te voegen.

1. Open een dashboard, kies het potlood (**Dashboard bewerken**), dan
   **Kaart toevoegen**.
2. Scrol naar beneden en kies **Handmatig**.
3. Plak dit en kies **Opslaan**:

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

De weerwaarschuwingen, de onweersverwachting, de gebieden van MET Norway, de
kegels en banen van stormen, de schudlijnen van aardbevingen en de stippenlagen
verschijnen vanzelf. De markeringen (stormen, aardbevingen, vulkanen,
rivierpeilmeters, de verwachting van Longyearbyen en de stations op
Spitsbergen) komen via het filter hierboven, dat
[auto-entities](https://github.com/thomasloven/lovelace-auto-entities) uit de
Marketplace nodig heeft. Met andere Live Track-modules geïnstalleerd voeg je
voor elk van hun bronnen nog een filter `- domain: geo_location` toe
(`live_track_aircraft`, `live_track_ships` enzovoort).

**Op de kaart:**

* De **laagkeuze** rechtsboven heeft een vakje voor elke laag: de
  Amerikaanse waarschuwingen, de onweersverwachting, tropische cyclonen, de
  waarschuwingen en zeeweerberichten van MET Norway, aardbevingen,
  aardbevingsschudden, stormmeldingen, wintermeldingen, branddetecties,
  luchtkwaliteitsstations, weerradar, radarbeweging, bliksem en wolken. De
  keuze van elke kijker wordt in zijn eigen browser bewaard.
* **Klik** op een markering, een gebied, een lijn of een stip om erover te
  lezen.
* De **filterkaart** (`custom:live-track-map-filter-card`) kan de stations op
  Spitsbergen verbergen, als **Observed weather (MET Norway)**.
* De bronvermelding van elke bron verschijnt in de attributieregel van de
  kaart zolang de gegevens ervan getoond worden.

Als de bronnen van je dashboards in YAML zijn ingesteld
(`lovelace: resource_mode: yaml`), kan er niets voor je worden geregistreerd:
een melding onder **Reparaties** geeft dan de precieze regel om toe te voegen.
Elke andere kaartkaart die `geo_location`-entiteiten toont, laat de
markeringen zien, maar niet de waarschuwingen, gebieden of stippen.

---

## Gebruiken in automatiseringen

Alles is een gewone Home Assistant-entiteit, dus de automatiseringseditor
werkt ermee, zonder code.

**Een melding op de telefoon als het huis binnen een waarschuwing ligt:**

1. **Instellingen → Automatiseringen en scènes → Maak automatisering aan →
   Voeg automatisering toe**.
2. **Wanneer**: *Entiteit → Status*, entiteit **Alert at Home**, naar
   **Onveilig** (aan).
3. **Dan doe**: *Meldingen → Stuur een melding via mobile_app_…*, met een
   bericht als `Weerwaarschuwing thuis: {{ state_attr('binary_sensor.live_track_weather_alert_at_home', 'highest') }}`.
4. Opslaan.

**De zonnekap inhalen bij een windstoot:** *Wanneer* **Wind gust at Home**
boven 50 km/u (of 30 mph) komt, *dan* de afdekking van de zonnekap sluiten.

**Andere ideeën:** laat een lamp knipperen als **Severe weather outlook** 3
(Enhanced) bereikt; waarschuw de eigenaar van de camper als **Alert at
Camper** aangaat vanwege een natuurbrand binnen 50 km; stuur een melding als
**Temperature at Cabin** onder het vriespunt zakt; toon **Forecast at Boat**
op een weerkaart zolang die op zee is; stuur het gezin een melding als
**Alert at Cabin**, in Noorwegen, aangaat voor een waarschuwing van MET
Norway.

---

## Alles op de kaart, in detail

### Amerikaanse weerwaarschuwingen

Elke actieve waarschuwing van de National Weather Service: waarschuwingen,
voorwaarschuwingen, adviezen en mededelingen voor county's, landzones en
zones voor de kust, open zee en brandweer, doorschijnend gevuld in de kleur die
de Weather Service aan elke gebeurtenis geeft (die met de hoogste prioriteit
waar waarschuwingen overlappen). Stormgebonden waarschuwingen zoals die voor
tornado's, zware onweersbuien en plotselinge overstromingen worden met hun
eigen polygoon getekend, niet als het hele county. Er wordt geen locatie
ingesteld: de kaart toont wat er op het scherm staat. De zonecontouren
(11.651, vereenvoudigd tot ongeveer 500 m, ongeveer 3,6 MB) worden met elke
release meegeleverd en door elke browser één keer per release gedownload.

**Sensor `US alerts`**: het aantal actieve waarschuwingen; de attributen
bevatten de lijst die de kaart tekent (`zones`, `polygons`, `styles`,
`updated`, `shapes_url`), die bij bijna elke opvraging verandert en niet in de
geschiedenis wordt opgeslagen.

### Tropische cyclonen: orkanen, tyfoons, cyclonen

Elke actieve tropische cycloon ter wereld, een markering per storm met zijn
naam als label en gekleurd naar categorie: depressie blauw, tropische storm
blauwgroen, categorieën 1 tot 5 goud, oranje, donkeroranje, rood en magenta,
posttropisch grijs. Beweeg erover voor klasse, wind, luchtdruk en beweging.

* Stormen van het **National Hurricane Center** (Atlantische Oceaan, oostelijke
  en centrale Stille Oceaan): de verwachtingskegel (blauw), de verwachte baan
  (rood), de huidige winden van 34, 50 en 64 knopen (63, 93 en 119 km/u; 39, 58 en
  74 mph) (geel, oranje, rood) en de
  afgelegde baan (zwart).
* **Elk ander bekken**, van het Joint Typhoon Warning Center via EONET van
  NASA: de markering en de afgelegde baan. Een storm waarvan de laatste positie
  ouder is dan 24 uur, wordt niet getoond.

Markeringen zijn `geo_location.storm_<id>` (`geo_location.storm_ep222026`),
met de attributen `storm_class`, `storm_category` (TD, TS, H1-H5, PT),
`max_wind_kmh`, `pressure_hpa`, `course_deg`, `speed_kmh`, `last_seen`,
`advisory_number` en `storm_source`. Ze komen en gaan met de stormen en hebben
geen unieke ID, dus ze kunnen in de interface niet worden hernoemd.
**Sensor `Tropical cyclones`**: het aantal stormen.

### Verwachting voor zwaar onweer

De categorische verwachting voor dag 1 van het Storm Prediction Center: waar
vandaag zware onweersbuien kunnen voorkomen, van 1 Marginal, 2 Slight,
3 Enhanced, 4 Moderate tot 5 High, in de eigen kleuren van het Center, onder
de waarschuwingen. **Sensor `Severe weather outlook`**: het hoogste risico
ergens in de VS vandaag, 0 tot 5, opgeslagen zodat het een automatisering kan
aansturen; attributen `risk`, `issued`, `valid_from`, `valid_to`. Het gebied
met gewoon onweer wordt niet getekend.

### Aardbevingen

Elke aardbeving die de US Geological Survey voor de afgelopen 24 uur vermeldt,
wereldwijd (ongeveer 240 per dag):

* **Markeringen** vanaf magnitude 4,5, en voor elke beving die mensen hebben
  gevoeld, met de magnitude als label (`geo_location.quake_<USGS id>`). Klik
  voor tijd, diepte, meldingen van mensen die het voelden, het sterkste
  schudden, het PAGER-waarschuwingsniveau en de gebeurtenispagina van de USGS.
  De "tsunamivlag" is geen waarschuwing; tsunamiwaarschuwingen komen van NOAA
  (tsunami.gov).
* **Stippen** voor elke andere beving (en steengroeveexplosies en explosies in
  grijs), op een eigen laag: **sensor `Earthquakes`**. De optie
  **Kleinste aardbeving op de puntenlaag van de kaart** laat de kleine weg.
* **Schudlijnen** (USGS ShakeMap) voor de grootste bevingen van de dag,
  magnitude 6 en hoger of sterk schudden, hooguit vijf:
  **sensor `Earthquake shaking`**.

### Vulkanen met verhoogde status

Elke Amerikaanse vulkaan op waarschuwingsniveau Advisory of kleurcode Yellow
voor de luchtvaart en hoger, een markering in zijn kleurcode met zijn naam als
label (`geo_location.volcano_<number>`). Klik voor het waarschuwingsniveau, de
kleurcode, sinds wanneer, de samenvatting van het observatorium en links naar
het bericht en de pagina van de vulkaan.

### Rivieren die nu overstromen of naar verwachting overstromen

Elke Amerikaanse rivier- of getijdenmeter met **nu een geringe overstroming of
erger**, of waarvoor die verwacht wordt, met Minor, Moderate of Major als label
in de overstromingskleuren van de Weather Service
(`geo_location.river_<gauge id>`). **Een donkere ring betekent dat het nu
overstroomt**; zonder ring is het een verwachting. Klik voor de huidige
waterstand, de verwachte waterstand, de overstromingsniveaus, het debiet en de
pagina van de meter. ⚠ Een paar meters hebben overstromingsniveaus die op
plaatshouders lijken en tonen daardoor Major (Devils Lake, North Dakota).

### Stormmeldingen

Elke NWS Local Storm Report van de afgelopen 24 uur over een tornado of
waterhoos, een trechterwolk, hagel, onweerswind of schade, een plotselinge
overstroming of een overstroming: rood voor tornado's, blauw voor wind, groen
voor hagel, blauwgroen voor overstromingen. Een belangrijke melding is groter
met een donkere ring: elke tornado, hagel van 5 cm (2 inch) of meer, of wind
van 120 km/u (65 knopen) of meer. Meldingen vervagen met de tijd: minder dan een uur, 1 tot
6 uur, 6 tot 24 uur. Klik voor het soort, de grootte of snelheid, de plaats, de
tijd, het NWS-kantoor en de opmerkingen. **Sensor `Storm reports`**: het
aantal stippen. ⚠ Dit zijn meldingen zoals mensen ze insturen, voordat de
Weather Service ze controleert, en het kan 30 minuten duren voor ze
verschijnen.

### Wintermeldingen

Uit dezelfde meldingen, op een eigen laag onder de stormmeldingen: sneeuw,
zware sneeuw en sneeuwbuien (leiblauw), sneeuwstormen (oranjerood), natte
sneeuw met ijskorrels (orchidee), ijzel, aanvriezende motregen en ijsstormen
(donkermagenta), schade door sneeuw en ijs (grijs), extreme kou en
gevoelstemperatuur (blauw), lawines (bruin) en ijsdammen (donkerblauwgroen),
elk met een dunne donkere ring. Belangrijke meldingen zijn groter: 30 cm
sneeuw (12 inch), 1,3 cm ijskorrels (een halve inch), 6 mm ijs (een kwart
inch) of elke ijsstorm. Klik
voor de hoeveelheid in inch en cm of mm, of de temperatuur in °F en °C.
**Sensor `Winter reports`**. ⚠ Een grote storm brengt duizenden meldingen;
waar twee zouden overlappen, wordt er één getekend, dus zoom in.

### MET Norway: waarschuwingen, zeeweerberichten, de verwachting voor Longyearbyen

* **Waarschuwingen** voor het land, de kust en de zeeën van Noorwegen en de
  zeeën tot de Noordpool, in het geel, oranje of rood van MET, naast de
  Amerikaanse waarschuwingen. Klik er een aan voor wat er verwacht wordt, de
  gevolgen, het advies en wanneer (in het Engels). **Sensor `MET Norway
  warnings`**.
* **Zeeweerberichten** voor 56 zeegebieden en 39 kustgebieden, die van
  Spitsbergen inbegrepen, onder de waarschuwingen. Klik er een aan voor de
  verwachting en elke waarschuwing voor wind, ijs of polaire depressies.
  **Sensor `MET Norway marine forecasts`**.
* **Een verwachtingsstip bij Longyearbyen**, met de temperatuur als label;
  klik erop voor de verwachting per zes uur voor een dag
  (`geo_location.met_forecast_longyearbyen`).

### Gemeten weer op Spitsbergen en Jan Mayen (Frost-client-ID)

Een blauwgroene stip voor elk weerstation op Spitsbergen, Bereneiland, Hopen
en Jan Mayen waarvan temperatuur en wind allebei minder dan twee uur oud zijn
(ongeveer 30), met de temperatuur als label (`geo_location.frost_sn99840` voor
Svalbard Lufthavn, enzovoort). Klik er een aan voor temperatuur, wind en
richting, de hardste windstoot van het afgelopen uur, luchtvochtigheid,
luchtdruk, sneeuwdiepte en de tijd. Stations die alleen temperatuur melden,
worden niet getekend; van twee stations die dichter dan 1 km bij elkaar
liggen, wordt er één getekend. Waarden die Frost als zeer onzeker of foutief
markeert, worden niet gebruikt; waarden die tot nu toe alleen automatisch zijn
gecontroleerd (meestal het nieuwste uur van MET), worden getoond, en de popup
zegt "Automatic check only".

### Natuurbranden en luchtkwaliteit (FIRMS- en AirNow-sleutels)

Kies regio's onder **Branddetecties en luchtkwaliteitsstations op de kaart**:

* **Branddetecties** (vereist de FIRMS-sleutel): elke satellietdetectie van
  brand van de afgelopen 24 uur (NOAA-20 en NOAA-21 VIIRS) als kleine rode
  stippen. Fabrieken, raffinaderijen, fakkels en andere vaste warmtebronnen die
  NASA heeft ingedeeld, worden weggelaten. Klik voor wanneer, welke satelliet,
  het stralingsvermogen van de brand en de betrouwbaarheid volgens NASA.
  **Sensor `Fire detections`**.
* **Luchtkwaliteitsstations** (vereist de AirNow-sleutel; de VS en Canada):
  elke fijnstofmeter (PM2.5), gekleurd naar zijn AQI in de kleuren van de EPA,
  elk uur. **Sensor `Air quality sites`**.

### Weerradar, bliksem en wolken

Door de kaartkaart zelf getekend, zonder iets in te stellen: één radarlaag die
de scherpste bron kiest voor wat er op het scherm staat (RainViewer, NOAA
nowCOAST en GeoMet van Canada in Noord-Amerika; FMI uit Finland en DWD uit
Duitsland in Europa; JMA uit Japan; het KNMI boven Nederland met je sleutel),
radarbeweging, bliksem van nowCOAST, en wolken van de satellieten GOES en
EUMETSAT.

---

## Alles bij je plaatsen, in detail

### Alert at …

**`Alert at Home`** (`binary_sensor.live_track_weather_alert_at_home`,
apparaatklasse *safety*: aan betekent onveilig), en één per persoon, tracker of
zone die je bewaakt. Hij gaat aan als de plaats:

* binnen een **Amerikaanse weerwaarschuwing** of een **waarschuwing van MET
  Norway** ligt (volgens de eigen regel van de Weather Service: een tornado- of
  overstromingswaarschuwing telt binnen haar polygoon, niet in het hele
  county; de zones komen van de Weather Service zelf, dus een plaats aan een
  kust of op een countygrens krijgt het juiste antwoord);
* in de afgelopen 24 uur bij een sterke **aardbeving** ligt: magnitude 4
  binnen 50 km (31 mijl), 5 binnen 150 km (93 mijl), 6 binnen 300 km
  (186 mijl), 7 binnen 600 km (373 mijl);
* in de gevarenzone van een **vulkaan** op Watch of Orange en hoger ligt (de
  National Volcanic Threat Layer van de USGS, met de integratie meegeleverd);
* met de FIRMS-sleutel bij een **natuurbrand** ligt (binnen de afstand die je
  instelt, standaard 50 km (31 mijl); detecties bereiken Home Assistant 2 tot 4 uur nadat
  de satelliet overkwam);
* met de AirNow-sleutel in **rook van een natuurbrand** ligt: de
  dichtstbijzijnde PM2.5-meter binnen 80 km (50 mijl) op of boven de AQI die je
  instelt, standaard 90 (plaatsen in de VS).

Attributen: `alerts` (elke waarschuwing bij de plaats, de ergste eerst, met
`event`, `severity`, `headline`, `onset`, `ends`, `source` en een link),
`highest`, `zones`; met de sleutels `fires_near`, `nearest_fire_km`,
`pm25_aqi`, `pm25_site` en meer. De zones van een bewegende tracker worden
opnieuw opgevraagd nadat hij meer dan 1 km is verplaatst. NASA raadt af om
branddetecties alleen te gebruiken voor beslissingen ter plaatse: volg
evacuatiebevelen op.

### Forecast at …

**`Forecast at Home`** (`weather.live_track_weather_forecast_at_home`), en één
per bewaakte plaats, voor elke weerkaart en `weather.get_forecasts`: per dag,
per dag en nacht, en per uur.

* **Op het vasteland van de VS**: de verwachting van de National Weather
  Service voor het rastervak van 2,5 km van de plaats, zeven dagen met dag en
  nacht en de verwachtingstekst, en per uur voor zes en een halve dag.
* **Overal elders, en op al het water**: de verwachting van MET Norway, per uur
  voor ongeveer twee en een halve dag, daarna per zes uur tot ongeveer tien
  dagen.

Hij wisselt van bron als de plaats beweegt (een boot die de haven verlaat, een
camper die Canada binnenrijdt).

### Wind at …, Wind gust at …, Wind direction at …, Temperature at …

Wat het dichtstbijzijnde weerstation heeft gemeten, voor elke bewaakte plaats
(`sensor.live_track_weather_wind_at_home` enzovoort).

* **In de VS**: het dichtstbijzijnde station van de National Weather Service
  uit elk netwerk (luchthavens, brandweer- en wegweerstations,
  vrijwilligersstations), of met de optie alleen luchthavens; het volgende, tot
  drie, als er een niets recents heeft.
* **In Noorwegen en op Spitsbergen**, met een Frost-client-ID: het
  dichtstbijzijnde van de eigen stations van MET Norway (gemeten op 22 plaatsen
  in Noorwegen: 0,4 tot 11 km ver). De windstoot is de hardste van het
  afgelopen uur.
* **Elders**, met een GeoNames-gebruikersnaam: het weerbericht (METAR) van de
  dichtstbijzijnde luchthaven, binnen ongeveer 100 km (60 mijl).
* Een sensor is **niet beschikbaar** als geen bericht jonger dan twee uur zijn
  waarde bevat. Een windstoot is onbekend als er geen is gemeld. Attributen:
  `station`, `station_name`, `provider`, `distance_km`, `observed`, `age_min`.

### Elevation at … en Depth at …

**`Elevation at Home`** en **`Depth at Home`**, en van elk één per bewaakte
plaats, gecontroleerd bij het opstarten en na een verplaatsing van meer dan
500 m.

* **Hoogte** uit de eerste bron met een waarde: USGS 3DEP (de VS en
  grensgebieden, tot op 1 m), Natural Resources Canada, Kartverket (het
  Noorse vasteland), daarna de Terrain Tiles van Mapzen voor de rest van de
  wereld.
* **Op het water** is de hoogte het oppervlak en is **Depth** de diepte onder
  de plaats, van Kartverket in Noorwegen of NOAA NCEI elders (de Grote Meren
  inbegrepen); onbekend op het land. Met een GeoNames-gebruikersnaam noemt
  `sea` de zee.
* ⚠ Bekende beperkingen: de hoogte op Spitsbergen is ongeveer 35 m te hoog
  (geen betere bron gevonden); rivieren, havens en stuwmeren hebben geen
  diepte; in ondiepe zeeën zonder GeoNames is de hoogte de zeebodem; een meer
  onder zeeniveau dat alleen via de terrain tiles bereikt wordt, toont 0.

---

## Alle entiteiten die het aanmaakt

| Entiteit | Wat het is |
|---|---|
| `sensor.live_track_weather_us_alerts` | aantal actieve Amerikaanse waarschuwingen; de lijst die de kaart tekent |
| `sensor.live_track_weather_tropical_cyclones` | aantal tropische cyclonen |
| `sensor.live_track_weather_severe_weather_outlook` | hoogste risico op zwaar onweer vandaag, 0 tot 5 |
| `sensor.live_track_weather_met_norway_warnings` | getekende waarschuwingen van MET Norway |
| `sensor.live_track_weather_met_norway_marine_forecasts` | zeeweergebieden van MET Norway |
| `sensor.live_track_weather_earthquakes` | aardbevingsstippen op de kaart |
| `sensor.live_track_weather_earthquake_shaking` | getekende ShakeMaps |
| `sensor.live_track_weather_storm_reports` | getekende stormmeldingen |
| `sensor.live_track_weather_winter_reports` | getekende wintermeldingen |
| `sensor.live_track_weather_fire_detections` | branddetecties (FIRMS-sleutel en een regio) |
| `sensor.live_track_weather_air_quality_sites` | luchtkwaliteitsstations (AirNow-sleutel en een regio) |
| `sensor.live_track_weather_knmi_radar` | nieuwste radarbeeld van het KNMI (KNMI-sleutel) |
| `geo_location.storm_…`, `quake_…`, `volcano_…`, `river_…`, `met_forecast_…`, `frost_…` | de markeringen; ze komen en gaan en hebben geen unieke ID |
| `binary_sensor.live_track_weather_alert_at_home` | Alert at Home (en één per bewaakte plaats) |
| `weather.live_track_weather_forecast_at_home` | Forecast at Home (en één per bewaakte plaats) |
| `sensor.live_track_weather_wind_at_home`, `…_wind_gust_at_home`, `…_wind_direction_at_home`, `…_temperature_at_home` | gemeten weer thuis (en per plaats) |
| `sensor.live_track_weather_elevation_at_home`, `…_depth_at_home` | hoogte en diepte thuis (en per plaats) |

Attributen die bij elke opvraging veranderen (lijsten, vormen, popups), worden
buiten de geschiedenis van Home Assistant gehouden, zodat je database er niet
door groeit.

---

## Wat het verstuurt en downloadt

**Over je locatie.** De locatie van je huis en van elke bewaakte plaats wordt,
afgerond op ongeveer 11 m, alleen verstuurd waar een dienst die nodig heeft:
naar de National Weather Service om de zones, het verwachtingsraster en de
stations van de plaats te bepalen; buiten het Amerikaanse verwachtingsgebied
naar MET Norway voor de verwachting; naar de USGS (en, waar de USGS niets
heeft, naar Natural Resources Canada, Kartverket en NOAA NCEI) voor hoogte en
diepte, bij het opstarten en na een verplaatsing van meer dan 500 m; met je
sleutels naar NASA FIRMS (een rechthoek rond de plaats), AirNow, GeoNames en
Frost van MET Norway. Zet **Huis bewaken** uit en bewaak niets anders, dan
wordt er geen locatie verstuurd. Verder wordt er niets over jou verstuurd.

**Hoeveel.** De lijst met Amerikaanse waarschuwingen ongeveer 100 KB per
3 minuten (instelbaar); de andere vragen alleen om een gewijzigd bestand waar
de dienst dat toelaat: orkaanberichten elke 5 minuten, EONET elke 30, de
onweersverwachting elke 5, de waarschuwingen van MET Norway elke 5,
zeeweerberichten elke 15-30 en puntverwachtingen elke 30 (telkens willekeurig
een minuut later, zoals MET vraagt, en 30 minuten niets na een weigering);
aardbevingen van de USGS elke 5 minuten (ongeveer 170 KB), vulkanen elke 10,
rivieren elke 30, stormmeldingen elke 10; Frost elke 10 minuten (ongeveer
80 KB); GeoNames binnen de helft van zijn 10.000 gratis credits per dag; het
KNMI hooguit ongeveer 24 verzoeken per uur, en alleen zolang een kaart het
toont. Na een fout wordt elke dienst een tijdje met rust gelaten voordat hij
weer wordt bevraagd.

---

## Help het groeien

Live Track Weather groeit nog. We voegen landen, weerdiensten en gevaren toe
zodra we ze vinden, en we willen weten wat je hierna graag zou zien.

### Stel iets voor

Ontbreekt je weerdienst? Klopt er iets niet, of is iets moeilijk te
begrijpen? Laat het ons weten op de manier die voor jou het makkelijkst is:

* [**Vul een kort formulier in**](https://github.com/StrausbergAutomationWorks/LiveTrackWeather/issues/new?template=nl.yml)
  in het Nederlands. Je hebt een gratis GitHub-account nodig.
* **Stuur een e-mail** naar
  [StrausbergAutomationWorks@recordwise.org](mailto:StrausbergAutomationWorks@recordwise.org).
  Geen account nodig.

Hoe je ons ook bereikt, het helpt als je vertelt:

* wat je graag zou zien, en waar ter wereld;
* een link naar waar de gegevens gepubliceerd worden, als je er een kent (een
  open-datapagina, een openbare feed, de website van een weerdienst): niet
  nodig, maar het helpt;
* de taal van je Home Assistant, als het probleem de tekst of een vertaling
  is.

Schrijf in het Engels of in je eigen taal, wat voor jou het makkelijkst is.

### Voeg het zelf toe, met onze hulp

Als je zelf iets wilt toevoegen, helpen we je daarbij, van de eerste vraag tot
de afgeronde release. Je hoeft geen ontwikkelaar te zijn om te beginnen:

* **Een vertaling.** De teksten in het instellingsvenster zijn een korte lijst
  zinnen in één tekstbestand. We laten je zien welk bestand en welke regels.
* **Een nieuw land of een nieuwe weerdienst.** Vertel ons waar de gegevens
  gepubliceerd worden. We kunnen de code samen schrijven, of die van jou
  nakijken.
* **Testen waar je woont.** Installeer het, bekijk jouw deel van de kaart, en
  vertel ons wat klopt en wat niet.
* **Een correctie op deze README.** Als een stap niet overeenkwam met wat je
  zag, vertel ons wat je zag.

[**Vertel ons wat je van plan bent**](https://github.com/StrausbergAutomationWorks/LiveTrackWeather/issues/new?template=nl.yml)
of schrijf naar
[StrausbergAutomationWorks@recordwise.org](mailto:StrausbergAutomationWorks@recordwise.org),
en we antwoorden met de volgende stappen.

---

## Talen

Deze README: [English](README.md), [Deutsch](README.de.md),
[Français](README.fr.md), **Nederlands**, [简体中文](README.zh-Hans.md),
[Español](README.es.md), [Italiano](README.it.md), [Dansk](README.da.md) en
[Kalaallisut](README.kl.md) (een kort concept; tot een moedertaalspreker het
heeft gelezen, is de Deense pagina de betrouwbare). Elke vertaalde README is
volledig.

Het instellingsvenster en de opties verschijnen in de taal van je Home
Assistant als het een van deze is: English, Dansk, Deutsch, Español,
Français, Gaeilge, Íslenska, Italiano, Nederlands, Norsk Bokmål, Polski,
Português, Português (BR), Suomi, Svenska en 简体中文. Elke andere taal toont
Engels. De namen van de entiteiten (**Alert at Home** enzovoort) en de labels
van de kaartkaart zijn in elke taal Engels.

Een fout gevonden in een vertaling, of een andere taal nodig? Laat het ons
weten op <https://github.com/StrausbergAutomationWorks/LiveTrackWeather/issues>, of
[vertaal het met onze hulp](#voeg-het-zelf-toe-met-onze-hulp).

---

## Vermeldingen en licenties

* De National Weather Service, het National Hurricane Center, het Storm
  Prediction Center, de National Water Prediction Service, het Joint Typhoon
  Warning Center, NASA en de US Geological Survey zijn diensten van de
  Amerikaanse overheid; hun gegevens zijn werken van de Amerikaanse overheid.
  AirNow-gegevens zijn voorlopig en niet geverifieerd (US EPA en partners).
* **MET Norway**: gegevens onder de Norwegian Licence for Open Government Data
  (NLOD) 2.0 en Creative Commons Attribution 4.0; de waarnemingen van Frost
  onder Creative Commons Attribution 3.0 Norway. Deze integratie rondt de
  gebieden af, kleurt de waarschuwingen opnieuw in en rekent eenheden om.
* **KNMI**: radar onder Creative Commons Attribution 4.0, versneden en
  geschaald tot kaarttegels.
* **GeoNames**: METAR-berichten en namen van zeeën onder Creative Commons
  Attribution 4.0.
* **Hoogte**: de CDEM van Natural Resources Canada, Open Government Licence -
  Canada; Kartverket, Creative Commons Attribution 4.0; NOAA NCEI,
  Amerikaanse overheid. **Terrain Tiles**: Mapzen, en de bronnen in de
  Joerd-attributie van Mapzen (`tilezen/joerd`, `docs/attribution.md`), hier
  letterlijk overgenomen: ArcticDEM terrain data DEM(s) were created from
  DigitalGlobe, Inc., imagery and funded under National Science Foundation
  awards 1043681, 1559691, and 1542736; Australia terrain data © Commonwealth
  of Australia (Geoscience Australia) 2017; Austria terrain data © offene Daten
  Österreichs – Digitales Geländemodell (DGM) Österreich; Canada terrain data
  contains information licensed under the Open Government Licence – Canada;
  Europe terrain data produced using Copernicus data and information funded by
  the European Union - EU-DEM layers; Global ETOPO1 terrain data U.S. National
  Oceanic and Atmospheric Administration; Mexico terrain data source: INEGI,
  Continental relief, 2016; New Zealand terrain data Copyright 2011 Crown
  copyright (c) Land Information New Zealand and the New Zealand Government
  (All rights reserved); Norway terrain data © Kartverket; United Kingdom
  terrain data © Environment Agency copyright and/or database right 2015. All
  rights reserved; United States 3DEP (formerly NED) and global GMTED2010 and
  SRTM terrain data courtesy of the U.S. Geological Survey.
* **Gevarenzones van vulkanen**: USGS National Volcanic Threat Layer (2024,
  CC0).

Geen van deze organisaties heeft deze integratie gemaakt of onderschreven.

**Code**: MIT, in [LICENSE](LICENSE).

**Voor ontwikkelaars:** `tools/build_shapes.py` bouwt het bestand met
waarschuwingszones opnieuw uit de shapefiles van de NWS
(<https://www.weather.gov/gis/>) en `tools/build_colours.py` de kleurentabel
uit de pagina met de gevarenkaart van de NWS; de tests draaien met
`python -m unittest discover -s tests`.

---

## Trefwoorden

Home Assistant weer · Home Assistant weerwaarschuwingen · NWS alerts ·
National Weather Service · weerwaarschuwingskaart · tornadowaarschuwing ·
onweerswaarschuwing · plotselinge overstroming · winterstorm · orkaantracker ·
tropische storm · tyfoon · cycloon · orkaankegel · NHC · JTWC · SPC outlook ·
onweersverwachting · aardbevingskaart · aardbevingsmelding · USGS
aardbevingen · ShakeMap · vulkaanwaarschuwing · overstromingskaart ·
peilmeter · NWPS · stormmeldingen · hagel · sneeuwhoogte · sneeuwstorm ·
ijsstorm · natuurbrandkaart · natuurbrandwaarschuwing · branddetectie · NASA
FIRMS · VIIRS · rookwaarschuwing · luchtkwaliteit · AQI · PM2.5 · AirNow ·
weerradar · buienradar · bliksemkaart · MET Norway · yr · weer Spitsbergen ·
Svalbard · Longyearbyen · Jan Mayen · Frost API · zeeweerbericht · KNMI radar ·
GeoNames · METAR · weerstation · windstootsensor · temperatuursensor ·
verwachting voor een apparaattracker · camperweer · bootweer · hoogtesensor ·
waterdiepte · geo_location · binary_sensor · weather entity · kaartkaart ·
Lovelace · HACS · Marketplace · Live Track · LiveTrack · weather warning ·
vejrvarsel · Unwetterwarnung · alerte météo · alerta meteorológica · allerta
meteo · farevarsel · 天气预警 ·
StrausbergAutomationWorks

---

**Erkenning.** StrausbergAutomationWorks erkent de inheemse volken van alle
landen en wateren op deze kaart, overal ter wereld, en betuigt zijn respect aan
hun Elders, van vroeger en nu.
