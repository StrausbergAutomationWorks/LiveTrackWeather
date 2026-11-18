# Live Track Weather

[English](README.md) · [Deutsch](README.de.md) · [Français](README.fr.md) · [Nederlands](README.nl.md) · [简体中文](README.zh-Hans.md) · [Español](README.es.md) · [Italiano](README.it.md) · **Dansk** · [Kalaallisut](README.kl.md) · [Alle sprog](#sprog)

**Vejrvarsler, storme, jordskælv, oversvømmelser, skovbrande, radar og
aktuelt vejr til Home Assistant, på ét kort.** Live Track Weather sætter
varsler fra den amerikanske National Weather Service, orkaner og tyfoner,
udsigter for kraftige tordenbyger, jordskælv, vulkaner, oversvømmede floder,
storm- og snerapporter, data om skovbrande og røg, MET Norways farevarsler og
vejrstationer på Svalbard på dit Home Assistant-kort, og holder øje med fare
for dit hjem, din families telefoner og din autocamper.

> **Live Track Weather er ét modul i Live Track**, en familie af Home
> Assistant-integrationer, der tegner alt, hvad der bevæger sig, og det vejr,
> det bevæger sig igennem, på ét fælles kort: fly, skibe, tog og nu vejret.
> Installer det alene eller sammen med de andre moduler
> ([listen nedenfor](#en-del-af-live-track-de-andre-moduler)).

**Status: 0.1.0, den første udgivelse.** Tilføjes til Marketplace via et link
([se nedenfor](#installation-trin-for-trin)); den er endnu ikke i Marketplaces katalog.

Eget værk af StrausbergAutomationWorks. Ikke tilknyttet eller godkendt af
National Weather Service, NOAA, National Hurricane Center, Storm Prediction
Center, Joint Typhoon Warning Center, NASA, US Geological Survey, EPA, MET
Norway, KNMI eller GeoNames.

> ⚠ **Ikke et nødvarslingssystem.** Det viser offentlige data, i bedste fald
> et par minutter forsinket. Brug din telefons nødvarsler, en vejrradio (i USA
> NOAA Weather Radio) og dine lokale myndigheder til varsler, der redder liv,
> og følg evakueringsordrer.

---

## Indhold

1. [Alt, hvad den gør](#alt-hvad-den-gør)
2. [En del af Live Track: de andre moduler](#en-del-af-live-track-de-andre-moduler)
3. [Før du begynder](#før-du-begynder)
4. [Installation, trin for trin](#installation-trin-for-trin)
5. [Opsætning, trin for trin](#opsætning-trin-for-trin)
6. [Gratis nøgler, der slår mere til, trin for trin](#gratis-nøgler-der-slår-mere-til-trin-for-trin)
7. [Sæt kortet på et dashboard](#sæt-kortet-på-et-dashboard)
8. [Brug den i automatiseringer](#brug-den-i-automatiseringer)
9. [Alt på kortet i detaljer](#alt-på-kortet-i-detaljer)
10. [Alt ved dine steder i detaljer](#alt-ved-dine-steder-i-detaljer)
11. [Alle entiteter, den opretter](#alle-entiteter-den-opretter)
12. [Hvad den sender og henter](#hvad-den-sender-og-henter)
13. [Sprog](#sprog)
14. [Tak og licenser](#tak-og-licenser)
15. [Nøgleord](#nøgleord)

---

## Alt, hvad den gør

### På kortet, uden opsætning

| Hvad | Hvor | Kilde |
|---|---|---|
| **Vejrvarsler**: varsler, skærpet opmærksomhed, meddelelser og orienteringer, udfyldt gennemsigtigt i vejrtjenestens egne farver | hele USA, kyster og farvande | National Weather Service |
| **Varsler om tornado, kraftig tordenbyge, pludselig oversvømmelse og andre stormbaserede varsler**, tegnet med deres eget polygon | USA | National Weather Service |
| **Orkaner, tropiske storme, tyfoner og cykloner**: en markør pr. storm, prognosekeglen, den forventede bane, vindfeltet og den tilbagelagte bane | hele verden | National Hurricane Center; Joint Typhoon Warning Center via NASA EONET |
| **Dagens udsigt for kraftigt uvejr**: risiko for kraftige tordenbyger fra Marginal til High | USA | NOAA Storm Prediction Center |
| **Jordskælv** fra de seneste 24 timer: markører for de store og de mærkede, prikker for resten, rystelseslinjer for de kraftigste | hele verden | US Geological Survey |
| **Vulkaner med forhøjet varsling**, i deres farvekode for luftfarten | vulkaner i USA | USGS Volcano Hazards Program |
| **Floder, der går over deres bredder eller ventes at gøre det**, let, moderat eller alvorlig | flod- og tidevandsmålere i USA | NOAA National Water Prediction Service |
| **Stormrapporter**: tornadoer, tragtskyer, hagl, skadelig vind, oversvømmelser | USA | NWS Local Storm Reports |
| **Vinterrapporter**: snemængder, snestorme, iskorn, isslag og isstorme, ekstrem kulde, laviner, isskruninger | USA | NWS Local Storm Reports |
| **MET Norways farevarsler**, ved siden af de amerikanske | Norge, havene og Svalbard | MET Norway |
| **Havudsigter** for 56 havområder og 39 kystområder, klik for at læse | fra Nordsøen til Nordpolen | MET Norway |
| **En prognoseprik i Longyearbyen**, Svalbard, klik for udsigten | Svalbard | MET Norway |
| **Vejrradar** og **lyn**: den skarpeste radar for det, der er på skærmen | verden | tegnet af Live Track-kortkortet |

### Ved dine steder, uden opsætning

"Dine steder" er dit hjem og enhver person, telefon, enhedstracker eller zone,
du vælger at overvåge. Hvert sted får (entiteternes navne er på engelsk):

* **Alert at …**: tændt, mens stedet ligger inden for et vejrvarsel, nær et
  kraftigt jordskælv eller i fareområdet for en vulkan i udbrud. Klar til
  automatiseringer: tænd lyset, send en notifikation til telefonen, luk
  garagen.
* **Forecast at …**: en fuld vejrudsigt, der følger stedet, når det flytter
  sig, til hvert vejrkort på dit dashboard. National Weather Services udsigter
  på land i USA; MET Norways alle andre steder og på alt vand.
* **Wind at …**, **Wind gust at …**, **Wind direction at …** og
  **Temperature at …**: hvad den nærmeste vejrstation har målt. Rul markisen
  ind, når det blæser op.
* **Elevation at …** og **Depth at …**: terrænets højde og vanddybden under
  en båd.

### Slået til med din egen gratis nøgle eller konto

| Gratis nøgle eller konto | Hvad den tilføjer |
|---|---|
| **NASA FIRMS**-kortnøgle | skovbrandsvarsler nær dine steder; hver satellitdetekteret brand på kortet |
| **AirNow** API-nøgle | varsler om skovbrandsrøg og luftkvalitet (PM2.5-AQI) ved dine steder i USA; hver luftkvalitetsmåler på kortet |
| **KNMI** API-nøgle | skarpere radar over Nederlandene |
| **GeoNames**-brugernavn | målt vind og temperatur uden for USA fra den nærmeste lufthavn; havets navn og vand eller land til dybden |
| **MET Norway Frost** klient-ID | hver vejrstation på Svalbard og Jan Mayen på kortet; målt vind og temperatur ved dine steder i Norge og på Svalbard |

Hver tager få minutter at få: [trin for trin nedenfor](#gratis-nøgler-der-slår-mere-til-trin-for-trin).

---

## En del af Live Track: de andre moduler

Live Track er en række Home Assistant-integrationer, én for hver slags ting,
der bevæger sig, alle tegnet på det samme kortkort. Hver virker alene; sammen
giver de ét levende billede. De deler kortkortet og et Python-bibliotek
([saw-livetrack](https://github.com/StrausbergAutomationWorks/LiveTrackCore)),
så en ekstra integration ikke sender flere forespørgsler til en kilde, som en
anden allerede læser.

| Modul | Hvad det sætter på kortet | Status |
|---|---|---|
| [Live Track Aircraft](https://github.com/StrausbergAutomationWorks/LiveTrackAircraft) | fly over dig via ADS-B, med ruter og typeikoner | udgivet |
| [Live Track Ships](https://github.com/StrausbergAutomationWorks/LiveTrackShips) | skibe og både via AIS, nær dig eller hvor som helst | udgivet |
| [Live Track Commuter Rail](https://github.com/StrausbergAutomationWorks/LiveTrackCommuterRail) | nærbaner i Nordamerika, Europa og Australien | udgivet |
| [Live Track Intercity Rail](https://github.com/StrausbergAutomationWorks/LiveTrackIntercityRail) | intercity- og fjerntog i Nordamerika, Europa og Australien | udgivet |
| [Live Track SALT](https://github.com/StrausbergAutomationWorks/LiveTrackSALT) | fly og fartøjer fra immigrations- og føderale ordensmyndigheder, ud fra offentlige lister | udgivet |
| **Live Track Weather** | vejr, storme og naturfarer (dette modul) | udgivet |
| Live Track Stations | afgangstavler og "tid til at gå"-påmindelser for hver station | planlagt |
| Live Track Satellites | satellitter, der passerer over dig | planlagt |
| Live Track Freight Trains | gods- og arbejdstog, hvor jernbanerne offentliggør dem | planlagt |
| Live Track Transit | bybusser, sporvogne, færger og metro | planlagt |
| Live Track Intercity Buses | fjern- og regionalbusser | planlagt |
| Live Track Commuter Buses | pendlerbusser | planlagt |
| [LiveTrackMapCard](https://github.com/StrausbergAutomationWorks/LiveTrackMapCard) | det fælles kortkort, som hvert modul tegner på | udgivet, installeres med hvert modul |

Alt er gratis og open source. Intet holdes tilbage til sponsorer.

---

## Før du begynder

* **Home Assistant** 2026.11 eller nyere.
* **Marketplace** (HACS) i din Home Assistant, så den er nem at installere og
  opdatere. Uden den kan du kopiere filerne i hånden.
* **Internetadgang** for Home Assistant: alt kommer fra offentlige
  vejrtjenester.
* **Valgfrit: auto-entities** fra Marketplace, så markørerne for storme,
  jordskælv og stationer kommer på kortet (se
  [Sæt kortet på et dashboard](#sæt-kortet-på-et-dashboard)). Varslerne og
  områderne vises også uden.
* Intet at betale og ingen konto nødvendig til det grundlæggende. De gratis
  nøgler ovenfor er valgfrie.

---

## Installation, trin for trin

### Fra Marketplace (anbefalet)

Live Track Weather er endnu ikke i Marketplaces katalog. Tilføj den via dens
link:

1. Åbn **Indstillinger → Marketplace** (HACS) i Home Assistant.
2. Vælg **Tilføj via link** (eller menuen med de tre prikker →
   **Brugerdefinerede repositories**).
3. Skriv `StrausbergAutomationWorks/LiveTrackWeather`. Bliver du spurgt om
   typen, så vælg **Integration**.
4. Find **Live Track Weather** på listen, og vælg **Download** eller
   **Installer**.
5. **Genstart Home Assistant**: **Indstillinger → System → Reparationer**
   tilbyder genstarten, eller brug **Indstillinger → System → Genstart**.

### I hånden

1. Hent kildekoden til den
   [nyeste udgivelse](https://github.com/StrausbergAutomationWorks/LiveTrackWeather/releases/latest).
2. Kopier dens mappe `custom_components/live_track_weather` til mappen
   `custom_components` i din Home Assistant-konfigurationsmappe (opret
   `custom_components`, hvis den ikke findes).
3. Genstart Home Assistant.

---

## Opsætning, trin for trin

1. Åbn **Indstillinger → Enheder og tjenester**.
2. Vælg **Tilføj integration** (nederst til højre), og søg efter
   **Live Track Weather**.
3. Vælg **Indsend**. Der er intet at skrive: én Live Track Weather dækker hele
   verden.

Det er det hele. Varsler, storme, jordskælv, vulkaner, oversvømmelser,
stormrapporter og MET Norways farevarsler begynder at dukke op inden for få
minutter, og dit hjem bliver overvåget: **Alert at Home**, **Forecast at
Home**, **Wind at Home**, **Temperature at Home**, **Elevation at Home** og
**Depth at Home**.

### Ændr, hvad den overvåger: indstillingerne

Åbn **Indstillinger → Enheder og tjenester → Live Track Weather →
Konfigurer** (tandhjulet). Hver indstilling med almindelige ord:

| Indstilling | Hvad den gør | Standard |
|---|---|---|
| **Sekunder mellem hentninger** | hvor ofte listen over amerikanske varsler hentes, 60 til 900 sekunder | 180 |
| **Overvåg hjemmet** | dit hjem får sensorerne "… at Home" og udsigten; slå fra for at fjerne dem | til |
| **Overvåg også disse personer, enhedstrackere eller zoner** | hver får sin egen "Alert at …", "Forecast at …", vind, temperatur, højde og dybde, som følger den, når den flytter sig. Vælg et familiemedlems telefon, en autocampers tracker, en zone for et sommerhus | ingen |
| **Varsler, der tænder et sted** | ethvert varsel (også meddelelser og orienteringer) eller kun moderate, alvorlige eller ekstreme. Alle varsler står stadig i sensoren | ethvert varsel |
| **Målt vind og temperatur kun fra lufthavnsstationer** | fra: den nærmeste station af enhver art (ofte tættere på en campingplads); til: kun lufthavne | fra |
| **NASA FIRMS MAP_KEY** | brandvarsler og branddetektioner (se [gratis nøgler](#gratis-nøgler-der-slår-mere-til-trin-for-trin)) | tom |
| **En brand tæller inden for** | hvor tæt en brand skal være for at tænde et sted, 5 til 150 km | 50 km |
| **AirNow API-nøgle** | røgvarsler og luftkvalitetsstationer | tom |
| **Røg tæller fra PM2.5-AQI** | det luftkvalitetsindeks, der tænder et sted | 90 |
| **Branddetektioner og luftkvalitetsstationer på kortet** | hvilke regioner der tegnes: de 48 sammenhængende stater og Hawaii, Alaska, Canada, hele verden (kun brande) | ingen |
| **Mindste jordskælv på kortets punktlag** | udelader de små jordskælvsprikker under en størrelse; markørerne bliver | tom: alle skælv |
| **KNMI API-nøgle** | skarpere radar over Nederlandene | tom |
| **GeoNames-brugernavn** | vejr uden for USA, havnavne | tom |
| **MET Norway Frost klient-ID** | stationer på Svalbard og Jan Mayen; målt vejr i Norge | tom |

Hver nøgle kontrolleres én gang, når du skriver den, og du får besked, hvis
den ikke virker. Lad et felt stå tomt for at slå den del fra.

---

## Gratis nøgler, der slår mere til, trin for trin

De er alle gratis og personlige: hver person, der installerer Live Track
Weather, skaffer sine egne. Indsæt hver af dem under **Indstillinger →
Enheder og tjenester → Live Track Weather → Konfigurer**.

### NASA FIRMS (skovbrande)

1. Åbn <https://firms.modaps.eosdis.nasa.gov/api/map_key/>.
2. Skriv din e-mailadresse, og bed om en **MAP_KEY**. Den kommer med e-mail.
3. Indsæt den i **NASA FIRMS MAP_KEY**, og indstil **En brand tæller inden
   for**, hvis 50 km ikke passer dig.
4. For at se brande på kortet skal du også sætte flueben ved en region under
   **Branddetektioner og luftkvalitetsstationer på kortet**.

### AirNow (røg og luftkvalitet, USA)

1. Åbn <https://docs.airnowapi.org/>, og vælg **Request an AirNow API
   Account**.
2. Bekræft e-mailen, log ind, og kopier din **API key** fra din kontoside.
3. Indsæt den i **AirNow API-nøgle**.

### KNMI (radar over Nederlandene)

1. Registrer dig på KNMI Data Platform, <https://developer.dataplatform.knmi.nl/>.
2. Bed om en nøgle til **WMS**-API'et. (En nøgle til Open Data-API'et virker
   ikke her.)
3. Indsæt den i **KNMI API-nøgle**. Kortet bruger så KNMI's radar over
   Nederlandene; uden den RainViewers.

### GeoNames (vejr uden for USA)

1. Opret en gratis konto på <https://www.geonames.org/login>.
2. Åbn bekræftelsesmailen fra GeoNames, og bekræft.
3. Log ind, åbn din kontoside, og **slå de gratis webtjenester til**.
4. Skriv dit **brugernavn** (ikke din adgangskode) i **GeoNames-brugernavn**.

### MET Norway Frost (stationer på Svalbard, vejr i Norge)

1. Åbn <https://frost.met.no/auth/requestCredentials.html>.
2. Skriv din e-mailadresse. Du får et **klient-ID** og en klienthemmelighed.
3. Indsæt **klient-ID'et** i **MET Norway Frost klient-ID**. Hemmeligheden er
   ikke nødvendig.

---

## Sæt kortet på et dashboard

Kortet er [LiveTrackMapCard](https://github.com/StrausbergAutomationWorks/LiveTrackMapCard),
det kort, som hvert Live Track-modul tegner på. **Det installeres med Live
Track Weather**: intet at hente, intet at kopiere til `www`, ingen ressource at
tilføje.

1. Åbn et dashboard, vælg blyanten (**Rediger dashboard**), og derefter
   **Tilføj kort**.
2. Rul ned til bunden, og vælg **Manuelt**.
3. Indsæt dette, og vælg **Gem**:

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

Vejrvarslerne, uvejrsudsigten, MET Norways områder, stormenes kegler og baner,
jordskælvenes rystelseslinjer og prik-lagene dukker op af sig selv. Markørerne
(storme, jordskælv, vulkaner, flodmålere, udsigten for Longyearbyen og
stationerne på Svalbard) kommer gennem filteret ovenfor, som kræver
[auto-entities](https://github.com/thomasloven/lovelace-auto-entities) fra
Marketplace. Er andre Live Track-moduler installeret, så tilføj ét filter mere
`- domain: geo_location` for hver af deres kilder (`live_track_aircraft`,
`live_track_ships` og så videre).

**På kortet:**

* **Lagvælgeren** øverst til højre har et afkrydsningsfelt for hvert lag: de
  amerikanske varsler, uvejrsudsigten, tropiske cykloner, MET Norways
  farevarsler og havudsigter, jordskælv, jordskælvsrystelser, stormrapporter,
  vinterrapporter, branddetektioner, luftkvalitetsstationer, vejrradar,
  radarbevægelse, lyn og skyer. Hver seers valg gemmes i vedkommendes egen
  browser.
* **Klik** på en markør, et område, en linje eller en prik for at læse om
  den.
* **Filterkortet** (`custom:live-track-map-filter-card`) kan skjule
  stationerne på Svalbard, som **Observed weather (MET Norway)**.
* Hver kildes kreditering står i kortets attributionslinje, så længe dens data
  vises.

Er dine dashboards' ressourcer sat op i YAML (`lovelace: resource_mode: yaml`),
kan intet registreres for dig: et punkt under **Reparationer** giver så den
præcise linje, der skal tilføjes. Ethvert andet kortkort, der viser
`geo_location`-entiteter, viser markørerne, men ikke varslerne, områderne
eller prikkerne.

---

## Brug den i automatiseringer

Alt er almindelige Home Assistant-entiteter, så automatiseringseditoren
virker med dem, helt uden kode.

**En notifikation til telefonen, når hjemmet ligger inden for et varsel:**

1. **Indstillinger → Automatiseringer og scener → Opret automatisering →
   Opret ny automatisering**.
2. **Når**: *Entitet → Tilstand*, entitet **Alert at Home**, til **Usikker**
   (til).
3. **Så gør**: *Notifikationer → Send en notifikation via mobile_app_…*, med
   en besked som `Vejrvarsel derhjemme: {{ state_attr('binary_sensor.live_track_weather_alert_at_home', 'highest') }}`.
4. Gem.

**Rul markisen ind ved et vindstød:** *Når* **Wind gust at Home** er over
50 km/t (eller 30 mph), *så* luk markisens afdækning.

**Andre idéer:** lad en lampe blinke, når **Severe weather outlook** når 3
(Enhanced); advar autocamperens ejer, når **Alert at Camper** tænder på grund
af en skovbrand inden for 50 km; send besked, når **Temperature at Cabin**
falder under frysepunktet; vis **Forecast at Boat** på et vejrkort, mens den
er på havet.

---

## Alt på kortet i detaljer

### Amerikanske vejrvarsler

Hvert aktivt varsel fra National Weather Service: varsler, skærpet
opmærksomhed, meddelelser og orienteringer for counties, landzoner og zoner
for kyst, åbent hav og brandvejr, udfyldt gennemsigtigt i den farve,
vejrtjenesten giver hver hændelse (den med højest prioritet, hvor varsler
overlapper). Stormbaserede varsler som tornado-, tordenbyge- og
oversvømmelsesvarsler tegnes med deres eget polygon, ikke som hele countyet.
Der vælges intet sted: kortet viser det, der er på skærmen. Zonernes omrids
(11.651, forenklet til omkring 500 m, omkring 3,6 MB) følger med hver udgivelse
og hentes én gang pr. udgivelse af hver browser.

**Sensor `US alerts`**: antallet af aktive varsler; dens attributter
indeholder den liste, kortet tegner (`zones`, `polygons`, `styles`, `updated`,
`shapes_url`), som skifter ved næsten hver hentning og ikke gemmes i
historikken.

### Tropiske cykloner: orkaner, tyfoner, cykloner

Hver aktiv tropisk cyklon i verden, en markør pr. storm mærket med dens navn
og farvet efter kategori: lavtryk blå, tropisk storm blågrøn, kategori 1 til 5
guld, orange, mørkeorange, rød og magenta, posttropisk grå. Hold musen over
for klasse, vind, lufttryk og bevægelse.

* Storme fra **National Hurricane Center** (Atlanterhavet, det østlige og
  centrale Stillehav): prognosekeglen (blå), den forventede bane (rød), de
  aktuelle vinde på 34, 50 og 64 knob (gul, orange, rød) og den tilbagelagte
  bane (sort).
* **Alle andre havområder**, fra Joint Typhoon Warning Center via NASA's
  EONET: markøren og den tilbagelagte bane. En storm, hvis seneste position er
  over 24 timer gammel, vises ikke.

Markørerne er `geo_location.storm_<id>` (`geo_location.storm_ep222026`), med
attributterne `storm_class`, `storm_category` (TD, TS, H1-H5, PT),
`max_wind_kmh`, `pressure_hpa`, `course_deg`, `speed_kmh`, `last_seen`,
`advisory_number` og `storm_source`. De kommer og går med stormene og har
intet unikt ID, så de kan ikke omdøbes i brugerfladen. **Sensor `Tropical
cyclones`**: antallet af storme.

### Udsigt for kraftigt uvejr

Storm Prediction Centers kategoriske udsigt for dag 1: hvor der kan komme
kraftige tordenbyger i dag, fra 1 Marginal, 2 Slight, 3 Enhanced, 4 Moderate
til 5 High, i centrets egne farver, under varslerne. **Sensor `Severe weather
outlook`**: den højeste risiko nogen steder i USA i dag, 0 til 5, gemt, så den
kan styre en automatisering; attributter `risk`, `issued`, `valid_from`,
`valid_to`. Området med almindelige tordenbyger tegnes ikke.

### Jordskælv

Hvert jordskælv, US Geological Survey lister for de seneste 24 timer, i hele
verden (omkring 240 om dagen):

* **Markører** fra styrke 4,5 og for ethvert skælv, folk har meldt at have
  mærket, mærket med styrken (`geo_location.quake_<USGS id>`). Klik for tid,
  dybde, meldinger fra folk, der mærkede det, de kraftigste rystelser,
  PAGER-varslingsniveauet og USGS' side om hændelsen. "Tsunamiflaget" er ikke
  et varsel; tsunamivarsler kommer fra NOAA (tsunami.gov).
* **Prikker** for alle andre skælv (og sprængninger i stenbrud og
  eksplosioner i gråt), på deres eget lag: **sensor `Earthquakes`**.
  Indstillingen **Mindste jordskælv på kortets punktlag** udelader de små.
* **Rystelseslinjer** (USGS ShakeMap) for dagens største skælv, styrke 6 og
  derover eller kraftige rystelser, højst fem:
  **sensor `Earthquake shaking`**.

### Vulkaner med forhøjet varsling

Hver vulkan i USA på varslingsniveau Advisory eller luftfartens farvekode
Yellow og derover, en markør i dens farvekode mærket med dens navn
(`geo_location.volcano_<number>`). Klik for varslingsniveauet, farvekoden,
siden hvornår, observatoriets sammenfatning og links til meddelelsen og
vulkanens side.

### Floder, der går over deres bredder nu eller ventes at gøre det

Hver flod- eller tidevandsmåler i USA med **let oversvømmelse eller værre
nu**, eller som ventes at nå det, mærket Minor, Moderate eller Major i
vejrtjenestens oversvømmelsesfarver (`geo_location.river_<gauge id>`). **En
mørk ring betyder, at den oversvømmer nu**; uden ringen er det en prognose.
Klik for den aktuelle vandstand, den forventede vandstand,
oversvømmelsesniveauerne, vandføringen og målerens side. ⚠ Nogle få målere har
oversvømmelsesniveauer, der ligner pladsholdere, og viser derfor Major (Devils
Lake, North Dakota).

### Stormrapporter

Hver NWS Local Storm Report fra de seneste 24 timer om en tornado eller
skypumpe, en tragtsky, hagl, tordenbygevind eller -skader, en pludselig
oversvømmelse eller en oversvømmelse: rød for tornadoer, blå for vind, grøn
for hagl, blågrøn for oversvømmelser. En betydelig rapport (enhver tornado,
hagl på 2 tommer eller mere, vind på 65 knob eller mere) er større med en
mørk ring. Rapporterne blegner med alderen: under en time, 1 til 6 timer, 6 til
24 timer. Klik for typen, størrelsen eller hastigheden, stedet, tiden,
NWS-kontoret og bemærkningerne. **Sensor `Storm reports`**: antallet af
prikker. ⚠ Det er rapporter, sådan som folk sender dem, før vejrtjenesten har
kontrolleret dem, og de kan være 30 minutter om at dukke op.

### Vinterrapporter

Fra de samme rapporter, på deres eget lag under stormrapporterne: sne, kraftigt
snefald og snebyger (skiferblå), snestorme (orangerød), iskorn (orkidé),
isslag, frysende støvregn og isstorme (mørk magenta), skader fra sne og is
(grå), ekstrem kulde og vindafkøling (blå), laviner (brun) og isskruninger
(mørk blågrøn), hver med en tynd mørk ring. Betydelige rapporter (12 tommer
sne, en halv tomme iskorn, en kvart tomme is, enhver isstorm) er større. Klik
for mængden i tommer og cm eller mm, eller temperaturen i °F og °C.
**Sensor `Winter reports`**. ⚠ En stor storm giver tusindvis af rapporter;
hvor to ville overlappe, tegnes én, så zoom ind.

### MET Norway: farevarsler, havudsigter, udsigten for Longyearbyen

* **Farevarsler** for Norges land, kyst og have og havene op til Nordpolen, i
  METs gul, orange eller rød, ved siden af de amerikanske varsler. Klik på et
  for, hvad der ventes, følgerne, rådene og hvornår (på engelsk). **Sensor
  `MET Norway warnings`**.
* **Havudsigter** for 56 havområder og 39 kystområder, også Svalbards, under
  farevarslerne. Klik på et for udsigten og eventuelle varsler om vind, is
  eller polare lavtryk. **Sensor `MET Norway marine forecasts`**.
* **En prognoseprik i Longyearbyen**, mærket med temperaturen; klik på den for
  udsigten hver sjette time for et døgn
  (`geo_location.met_forecast_longyearbyen`).

### Målt vejr på Svalbard og Jan Mayen (Frost klient-ID)

En blågrøn prik for hver vejrstation på Svalbard, Bjørnøya, Hopen og Jan Mayen,
hvis temperatur og vind begge er under to timer gamle (omkring 30), mærket med
temperaturen (`geo_location.frost_sn99840` for Svalbard Lufthavn og så
videre). Klik på en for temperatur, vind og retning, det kraftigste vindstød i
den seneste time, luftfugtighed, lufttryk, snedybde og tiden. Stationer, der
kun melder temperatur, tegnes ikke; af to stationer, der ligger tættere end
1 km på hinanden, tegnes én. Værdier, som Frost markerer som meget usikre
eller fejlagtige, bruges ikke; værdier, der indtil videre kun er kontrolleret
automatisk (det er METs nyeste time som regel), vises, og pop op-vinduet
siger "Automatic check only".

### Skovbrande og luftkvalitet (FIRMS- og AirNow-nøgler)

Vælg regioner under **Branddetektioner og luftkvalitetsstationer på kortet**:

* **Branddetektioner** (kræver FIRMS-nøglen): hver satellitdetekteret brand
  fra de seneste 24 timer (NOAA-20 og NOAA-21 VIIRS) som små røde prikker.
  Fabrikker, raffinaderier, gasfakler og andre faste varmekilder, NASA har
  klassificeret, er udeladt. Klik for hvornår, hvilken satellit, brandens
  udstrålede effekt og NASA's sikkerhed. **Sensor `Fire detections`**.
* **Luftkvalitetsstationer** (kræver AirNow-nøglen; USA og Canada): hver
  finpartikelmåler (PM2.5), farvet efter sin AQI i EPA's farver, hver time.
  **Sensor `Air quality sites`**.

### Vejrradar, lyn og skyer

Tegnet af selve kortkortet, uden opsætning: ét radarlag, der vælger den
skarpeste kilde for det, der er på skærmen (RainViewer, NOAA nowCOAST og
Canadas GeoMet i Nordamerika; Finlands FMI og Tysklands DWD i Europa; Japans
JMA; KNMI over Nederlandene med din nøgle), radarbevægelse, lyn fra nowCOAST og
skyer fra satellitterne GOES og EUMETSAT.

---

## Alt ved dine steder i detaljer

### Alert at …

**`Alert at Home`** (`binary_sensor.live_track_weather_alert_at_home`,
enhedsklasse *safety*: til betyder usikker), og én for hver person, tracker
eller zone, du overvåger. Den tænder, når stedet ligger:

* inden for et **amerikansk vejrvarsel** eller et **farevarsel fra MET
  Norway** (efter vejrtjenestens egen regel: et tornado- eller
  oversvømmelsesvarsel tæller inden for sit polygon, ikke i hele countyet;
  zonerne kommer fra vejrtjenesten selv, så et sted ved en kyst eller på en
  countygrænse får det rigtige svar);
* nær et kraftigt **jordskælv** i de seneste 24 timer: styrke 4 inden for
  50 km, 5 inden for 150 km, 6 inden for 300 km, 7 inden for 600 km;
* inden for fareområdet for en **vulkan** på Watch eller Orange og derover
  (USGS' National Volcanic Threat Layer, som følger med integrationen);
* med FIRMS-nøglen nær en **skovbrand** (inden for den afstand, du har
  indstillet, som standard 50 km; detektioner når Home Assistant 2 til 4 timer
  efter satellittens passage);
* med AirNow-nøglen i **skovbrandsrøg**: den nærmeste PM2.5-måler inden for
  50 miles på eller over den AQI, du har indstillet, som standard 90 (steder i
  USA).

Attributter: `alerts` (hvert varsel ved stedet, det værste først, med `event`,
`severity`, `headline`, `onset`, `ends`, `source` og et link), `highest`,
`zones`; med nøglerne `fires_near`, `nearest_fire_km`, `pm25_aqi`, `pm25_site`
og flere. En tracker i bevægelse får sine zoner slået op igen, når den har
flyttet sig mere end 1 km. NASA fraråder at bruge branddetektioner alene til
beslutninger på stedet: følg evakueringsordrer.

### Forecast at …

**`Forecast at Home`** (`weather.live_track_weather_forecast_at_home`), og én
for hvert overvåget sted, til hvert vejrkort og `weather.get_forecasts`:
daglig, dag og nat, og time for time.

* **På land i USA**: National Weather Services udsigt for stedets 2,5 km-felt,
  syv døgn med dag og nat og den skrevne udsigt, og time for time i seks og et
  halvt døgn.
* **Alle andre steder og på alt vand**: MET Norways udsigt, time for time i
  omkring to et halvt døgn, derefter hver sjette time op til omkring ti døgn.

Den skifter kilde, når stedet flytter sig (en båd, der forlader havnen, en
autocamper, der kører ind i Canada).

### Wind at …, Wind gust at …, Wind direction at …, Temperature at …

Hvad den nærmeste vejrstation har målt, for hvert overvåget sted
(`sensor.live_track_weather_wind_at_home` og så videre).

* **I USA**: den nærmeste station i National Weather Service fra ethvert
  netværk (lufthavne, brandvejrs- og vejstationer, frivilliges stationer),
  eller kun lufthavne efter valg; den næste, op til tre, når én ikke har noget
  nyt.
* **I Norge og på Svalbard**, med et Frost klient-ID: den nærmeste af MET
  Norways egne stationer (målt på 22 steder i Norge: 0,4 til 11 km væk).
  Vindstødet er det kraftigste i den seneste time.
* **Andre steder**, med et GeoNames-brugernavn: den nærmeste lufthavns
  vejrmelding (METAR) inden for omkring 100 km.
* En sensor er **utilgængelig**, når ingen melding under to timer gammel har
  dens værdi. Et vindstød er ukendt, når intet er meldt. Attributter:
  `station`, `station_name`, `provider`, `distance_km`, `observed`, `age_min`.

### Elevation at … og Depth at …

**`Elevation at Home`** og **`Depth at Home`**, og én af hver for hvert
overvåget sted, kontrolleret ved opstart og efter en flytning på mere end
500 m.

* **Højde** fra den første kilde med en værdi: USGS 3DEP (USA og
  grænseområder, på 1 m), Natural Resources Canada, Kartverket (det norske
  fastland), og derefter Mapzens Terrain Tiles for resten af verden.
* **På vand** er højden overfladen, og **Depth** er dybden under stedet, fra
  Kartverket i Norge eller NOAA NCEI andre steder (De Store Søer medregnet);
  ukendt på land. Med et GeoNames-brugernavn giver `sea` havets navn.
* ⚠ Kendte begrænsninger: højden på Svalbard er omkring 35 m for høj (ingen
  bedre kilde fundet); floder, havne og reservoirer har ingen dybde; i
  lavvandede have uden GeoNames er højden havbunden; en sø under havets
  overflade, som kun nås af terrain tiles, viser 0.

---

## Alle entiteter, den opretter

| Entitet | Hvad den er |
|---|---|
| `sensor.live_track_weather_us_alerts` | antal aktive amerikanske varsler; den liste, kortet tegner |
| `sensor.live_track_weather_tropical_cyclones` | antal tropiske cykloner |
| `sensor.live_track_weather_severe_weather_outlook` | højeste risiko for kraftigt uvejr i dag, 0 til 5 |
| `sensor.live_track_weather_met_norway_warnings` | tegnede farevarsler fra MET Norway |
| `sensor.live_track_weather_met_norway_marine_forecasts` | MET Norways havudsigtsområder |
| `sensor.live_track_weather_earthquakes` | jordskælvsprikker på kortet |
| `sensor.live_track_weather_earthquake_shaking` | tegnede ShakeMaps |
| `sensor.live_track_weather_storm_reports` | tegnede stormrapporter |
| `sensor.live_track_weather_winter_reports` | tegnede vinterrapporter |
| `sensor.live_track_weather_fire_detections` | branddetektioner (FIRMS-nøgle og en region) |
| `sensor.live_track_weather_air_quality_sites` | luftkvalitetsstationer (AirNow-nøgle og en region) |
| `sensor.live_track_weather_knmi_radar` | nyeste radarbillede fra KNMI (KNMI-nøgle) |
| `geo_location.storm_…`, `quake_…`, `volcano_…`, `river_…`, `met_forecast_…`, `frost_…` | markørerne; de kommer og går og har intet unikt ID |
| `binary_sensor.live_track_weather_alert_at_home` | Alert at Home (og én pr. overvåget sted) |
| `weather.live_track_weather_forecast_at_home` | Forecast at Home (og én pr. overvåget sted) |
| `sensor.live_track_weather_wind_at_home`, `…_wind_gust_at_home`, `…_wind_direction_at_home`, `…_temperature_at_home` | målt vejr derhjemme (og pr. sted) |
| `sensor.live_track_weather_elevation_at_home`, `…_depth_at_home` | højde og dybde derhjemme (og pr. sted) |

Attributter, der skifter ved hver hentning (lister, former, pop op-vinduer),
holdes ude af Home Assistants historik, så din database ikke vokser af dem.

---

## Hvad den sender og henter

**Om din placering.** Placeringen af dit hjem og hvert overvåget sted sendes,
afrundet til omkring 11 m, kun dertil, hvor en tjeneste har brug for den: til
National Weather Service for at finde stedets zoner, prognosefelt og
stationer; uden for USA's prognoseområde til MET Norway for dets udsigt; til
USGS (og, hvor USGS intet har, til Natural Resources Canada, Kartverket og NOAA
NCEI) for højde og dybde, ved opstart og efter en flytning på mere end 500 m;
med dine nøgler til NASA FIRMS (en firkant omkring stedet), AirNow, GeoNames og
MET Norways Frost. Slå **Overvåg hjemmet** fra, og overvåg intet andet, så
sendes ingen placering. Intet andet om dig sendes nogen steder hen.

**Hvor meget.** Listen over amerikanske varsler omkring 100 KB hvert 3.
minut (kan justeres); de andre spørger kun efter en ændret fil, hvor tjenesten
tillader det: orkanmeddelelser hvert 5. minut, EONET hvert 30., uvejrsudsigten
hvert 5., MET Norways farevarsler hvert 5., havudsigter hvert 15.-30. og
punktudsigter hvert 30. (hver gang et tilfældigt minut senere, som MET beder
om, og intet i 30 minutter efter en afvisning); USGS' jordskælv hvert 5. minut
(omkring 170 KB), vulkaner hvert 10., floder hvert 30., stormrapporter hvert
10.; Frost hvert 10. minut (omkring 80 KB); GeoNames inden for halvdelen af
dets 10.000 gratis point om dagen; KNMI højst omkring 24 forespørgsler i
timen, og kun mens et kort viser det. Efter en fejl får hver tjeneste lov at
være i fred et stykke tid, før den spørges igen.

---

## Sprog

Denne README: [English](README.md), [Deutsch](README.de.md),
[Français](README.fr.md), [Nederlands](README.nl.md),
[简体中文](README.zh-Hans.md), [Español](README.es.md),
[Italiano](README.it.md), **Dansk** og [Kalaallisut](README.kl.md) (en kort
kladde; indtil en modersmålstaler har læst den, er den danske side den
pålidelige). Hver oversat README er komplet.

Opsætningsdialogen og indstillingerne vises på din Home Assistants sprog, når
det er et af disse: English, Dansk, Deutsch, Español, Français, Gaeilge,
Íslenska, Italiano, Nederlands, Norsk Bokmål, Polski, Português, Português
(BR), Suomi, Svenska og 简体中文. Alle andre sprog viser engelsk. Entiteternes
navne (**Alert at Home** og så videre) og kortkortets etiketter er på engelsk
på alle sprog.

Har du fundet en fejl i en oversættelse, eller mangler du et andet sprog? Sig
det til os på <https://github.com/StrausbergAutomationWorks/LiveTrackWeather/issues>.

---

## Tak og licenser

* National Weather Service, National Hurricane Center, Storm Prediction
  Center, National Water Prediction Service, Joint Typhoon Warning Center,
  NASA og US Geological Survey er myndigheder under den amerikanske regering;
  deres data er værker fra den amerikanske regering. AirNow-data er
  foreløbige og ikke efterprøvede (US EPA og partnere).
* **MET Norway**: data under Norwegian Licence for Open Government Data (NLOD)
  2.0 og Creative Commons Attribution 4.0; Frosts observationer under Creative
  Commons Attribution 3.0 Norway. Denne integration afrunder områderne,
  omfarver farevarslerne og omregner enheder.
* **KNMI**: radar under Creative Commons Attribution 4.0, beskåret og skaleret
  til kortfliser.
* **GeoNames**: METAR-meldinger og havnavne under Creative Commons Attribution
  4.0.
* **Højde**: Natural Resources Canadas CDEM, Open Government Licence - Canada;
  Kartverket, Creative Commons Attribution 4.0; NOAA NCEI, den amerikanske
  regering. **Terrain Tiles**: Mapzen og kilderne i Mapzens Joerd-attribution
  (`tilezen/joerd`, `docs/attribution.md`), gengivet her ordret: ArcticDEM
  terrain data DEM(s) were created from DigitalGlobe, Inc., imagery and funded
  under National Science Foundation awards 1043681, 1559691, and 1542736;
  Australia terrain data © Commonwealth of Australia (Geoscience Australia)
  2017; Austria terrain data © offene Daten Österreichs – Digitales
  Geländemodell (DGM) Österreich; Canada terrain data contains information
  licensed under the Open Government Licence – Canada; Europe terrain data
  produced using Copernicus data and information funded by the European
  Union - EU-DEM layers; Global ETOPO1 terrain data U.S. National Oceanic and
  Atmospheric Administration; Mexico terrain data source: INEGI, Continental
  relief, 2016; New Zealand terrain data Copyright 2011 Crown copyright (c)
  Land Information New Zealand and the New Zealand Government (All rights
  reserved); Norway terrain data © Kartverket; United Kingdom terrain data ©
  Environment Agency copyright and/or database right 2015. All rights
  reserved; United States 3DEP (formerly NED) and global GMTED2010 and SRTM
  terrain data courtesy of the U.S. Geological Survey.
* **Vulkanske fareområder**: USGS National Volcanic Threat Layer (2024, CC0).

Ingen af disse organisationer har lavet eller godkendt denne integration.

**Kode**: MIT, i [LICENSE](LICENSE).

**For udviklere:** `tools/build_shapes.py` genopbygger filen med varselszoner
ud fra NWS' shapefiler (<https://www.weather.gov/gis/>) og
`tools/build_colours.py` farvetabellen ud fra NWS' side med farekortet;
testene køres med `python -m unittest discover -s tests`.

---

## Nøgleord

Home Assistant vejr · Home Assistant vejrvarsler · NWS-varsler · National
Weather Service · kort over vejrvarsler · tornadovarsel · varsel om kraftig
tordenbyge · pludselig oversvømmelse · vinterstorm · orkansporing · tropisk
storm · tyfon · cyklon · orkankegle · NHC · JTWC · SPC outlook · udsigt for
kraftigt uvejr · jordskælvskort · jordskælvsvarsel · USGS jordskælv · ShakeMap
· vulkanvarsel · oversvømmelseskort · vandstandsmåler · NWPS · stormrapporter ·
hagl · snemængde · snestorm · isstorm · skovbrandskort · skovbrandsvarsel ·
branddetektion · NASA FIRMS · VIIRS · røgvarsel · luftkvalitet · AQI · PM2.5 ·
AirNow · vejrradar · regnradar · lynkort · MET Norway · yr · vejret på
Svalbard · Longyearbyen · Jan Mayen · Frost API · havudsigt · KNMI radar ·
GeoNames · METAR · vejrstation · vindstødssensor · temperatursensor · udsigt
for en enhedstracker · vejr til autocamperen · vejr til båden ·
højdesensor · vanddybde · geo_location · binary_sensor · weather entity ·
kortkort · Lovelace · HACS · Marketplace · Live Track · LiveTrack ·
StrausbergAutomationWorks
