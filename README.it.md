# Live Track Weather

[English](README.md) · [Deutsch](README.de.md) · [Français](README.fr.md) · [Nederlands](README.nl.md) · [简体中文](README.zh-Hans.md) · [Español](README.es.md) · **Italiano** · [Dansk](README.da.md) · [Kalaallisut](README.kl.md) · [Tutte le lingue](#lingue)

**Allerte meteo, tempeste, terremoti, alluvioni, incendi boschivi, radar e
meteo in tempo reale per Home Assistant, su un'unica mappa.** Live Track
Weather porta sulla tua mappa di Home Assistant allerte meteo ufficiali,
uragani e tifoni, terremoti, vulcani, piene dei fiumi, segnalazioni di
tempeste e di neve, dati su incendi boschivi e fumo, previsioni marine e
stazioni meteo, e sorveglia i pericoli per la tua casa, i telefoni della tua
famiglia e il tuo camper. Tempeste, terremoti, radar e previsioni coprono
tutto il mondo; Stati Uniti, Norvegia e Svalbard sono coperti con più
dettaglio ([dove funziona](#dove-funziona)).

> **Live Track Weather è un modulo di Live Track**, una famiglia di
> integrazioni di Home Assistant che disegnano tutto ciò che si muove, e il
> tempo che attraversa, su una mappa condivisa: aerei, navi, treni, e ora il
> meteo. Installalo da solo o accanto agli altri moduli
> ([elenco più sotto](#parte-di-live-track-gli-altri-moduli)).

> **In crescita, e aperto alle idee.** Oggi Live Track Weather copre
> tempeste, terremoti, radar e previsioni in tutto il mondo, e allerte per
> Stati Uniti, Norvegia e Svalbard. Stiamo aggiungendo altri paesi, servizi
> meteo e pericoli. Manca il tuo? [Suggeriscilo](#aiutaci-a-farlo-crescere),
> o aggiungilo tu: ti aiuteremo a farlo.

**Stato: 0.1.2, pubblicato.** Nel catalogo del Marketplace ([installalo più
sotto](#installazione-passo-dopo-passo)).

Opera originale di StrausbergAutomationWorks. Non affiliato a, né approvato
da, alcuna delle organizzazioni di cui mostra i dati: negli Stati Uniti il
National Weather Service, la NOAA, il National Hurricane Center, lo Storm
Prediction Center, il Joint Typhoon Warning Center, la NASA, l'US Geological
Survey e l'EPA; MET Norway (Norvegia); il KNMI (Paesi Bassi); o GeoNames.

> ⚠ **Non è un sistema di allerta di emergenza.** Mostra dati pubblici, nel
> migliore dei casi con qualche minuto di ritardo. Per le allerte che
> proteggono vite, usa le allerte di emergenza del tuo telefono, il tuo
> servizio meteorologico nazionale, una radio meteo dove il tuo paese ne ha
> una e le autorità locali, e segui gli ordini di evacuazione.

---

## Indice

1. [Tutto quello che fa](#tutto-quello-che-fa)
2. [Dove funziona](#dove-funziona)
3. [Parte di Live Track: gli altri moduli](#parte-di-live-track-gli-altri-moduli)
4. [Prima di iniziare](#prima-di-iniziare)
5. [Installazione, passo dopo passo](#installazione-passo-dopo-passo)
6. [Configurazione, passo dopo passo](#configurazione-passo-dopo-passo)
7. [Chiavi gratuite che attivano di più, passo dopo passo](#chiavi-gratuite-che-attivano-di-più-passo-dopo-passo)
8. [Mettere la mappa su una plancia](#mettere-la-mappa-su-una-plancia)
9. [Usarlo nelle automazioni](#usarlo-nelle-automazioni)
10. [Tutto sulla mappa, nel dettaglio](#tutto-sulla-mappa-nel-dettaglio)
11. [Tutto nei tuoi luoghi, nel dettaglio](#tutto-nei-tuoi-luoghi-nel-dettaglio)
12. [Tutte le entità che crea](#tutte-le-entità-che-crea)
13. [Cosa invia e scarica](#cosa-invia-e-scarica)
14. [Aiutaci a farlo crescere](#aiutaci-a-farlo-crescere)
15. [Lingue](#lingue)
16. [Riconoscimenti e licenze](#riconoscimenti-e-licenze)
17. [Parole chiave](#parole-chiave)

---

## Tutto quello che fa

### Sulla mappa, senza configurare nulla

| Cosa | Dove | Fonte |
|---|---|---|
| **Allerte meteo**: avvisi, allerte preventive, avvertenze e comunicati, riempiti in trasparenza con i colori propri del Weather Service | tutti gli Stati Uniti, le loro coste e acque | National Weather Service (Stati Uniti) |
| **Avvisi di tornado, temporale violento, piena improvvisa e altri avvisi legati alle tempeste**, disegnati con il proprio poligono | Stati Uniti | National Weather Service |
| **Uragani, tempeste tropicali, tifoni e cicloni**: un indicatore per tempesta, il cono di previsione, la traiettoria prevista, il campo di vento e la traiettoria passata | tutto il mondo | National Hurricane Center (Stati Uniti); Joint Typhoon Warning Center (Stati Uniti) tramite NASA EONET |
| **La previsione di maltempo severo di oggi**: rischio di temporali violenti da Marginal a High | Stati Uniti | NOAA Storm Prediction Center |
| **Terremoti** delle ultime 24 ore: indicatori per i forti e per quelli avvertiti, punti per gli altri, linee di scuotimento per i più forti | tutto il mondo | US Geological Survey |
| **Vulcani in allerta**, con il loro codice colore per l'aviazione | vulcani degli Stati Uniti | USGS Volcano Hazards Program |
| **Fiumi in piena o con piena prevista**, lieve, moderata o grave | idrometri e mareografi degli Stati Uniti | NOAA National Water Prediction Service |
| **Segnalazioni di tempeste**: tornado, nubi a imbuto, grandine, vento dannoso, inondazioni | Stati Uniti | NWS Local Storm Reports |
| **Segnalazioni invernali**: altezze della neve, bufere di neve, nevischio, pioggia gelata e tempeste di ghiaccio, freddo estremo, valanghe, ingorghi di ghiaccio | Stati Uniti | NWS Local Storm Reports |
| **Le allerte meteo di MET Norway**, accanto a quelle statunitensi | Norvegia, i suoi mari, Svalbard | MET Norway |
| **Previsioni marine** per 56 zone di mare e 39 zone costiere, clicca per leggerle | dal Mare del Nord al Polo Nord | MET Norway |
| **Un punto di previsione a Longyearbyen**, Svalbard, clicca per la previsione | Svalbard | MET Norway |
| **Radar meteo** e **fulmini**: il radar più nitido per ciò che è sullo schermo | il mondo | disegnati dalla scheda mappa di Live Track |

### Nei tuoi luoghi, senza configurare nulla

"I tuoi luoghi" sono la tua casa, e qualsiasi persona, telefono, tracker di
dispositivo o zona che scegli di sorvegliare. Ogni luogo riceve (i nomi delle
entità sono in inglese):

* **Alert at …**: acceso mentre il luogo è dentro un'allerta meteo, vicino a
  un terremoto forte o nella zona di pericolo di un vulcano in eruzione. Pronto
  per le automazioni: accendere le luci, inviare una notifica al telefono,
  chiudere il garage.
* **Forecast at …**: una previsione meteo completa che segue il luogo quando
  si sposta, per ogni scheda meteo della tua plancia. Le previsioni del
  National Weather Service sulla terraferma degli Stati Uniti; quelle di MET
  Norway ovunque altrove, e su tutte le acque.
* **Wind at …**, **Wind gust at …**, **Wind direction at …** e
  **Temperature at …**: ciò che ha misurato la stazione meteo più vicina.
  Ritira la tenda quando arrivano le raffiche.
* **Elevation at …** e **Depth at …**: l'altitudine del terreno e la
  profondità dell'acqua sotto una barca.

### Attivato dalla tua chiave o dal tuo account gratuito

| Chiave o account gratuito | Cosa aggiunge |
|---|---|
| Chiave mappa **NASA FIRMS** | allerte per incendi boschivi vicino ai tuoi luoghi; ogni rilevamento satellitare di incendio sulla mappa |
| Chiave API **AirNow** (Stati Uniti) | allerte per fumo da incendi e qualità dell'aria (AQI PM2.5) nei tuoi luoghi negli Stati Uniti; ogni monitor della qualità dell'aria sulla mappa |
| Chiave API **KNMI** (Paesi Bassi) | radar più nitido sui Paesi Bassi |
| Nome utente **GeoNames** | vento e temperatura misurati fuori dagli Stati Uniti, dall'aeroporto più vicino; il nome del mare e acqua o terra per la profondità |
| ID client **MET Norway Frost** | ogni stazione meteo delle Svalbard e di Jan Mayen sulla mappa; vento e temperatura misurati nei tuoi luoghi in Norvegia e alle Svalbard |

Ognuna si ottiene in pochi minuti: [passo dopo passo più sotto](#chiavi-gratuite-che-attivano-di-più-passo-dopo-passo).

---

## Dove funziona

| Regione | Cosa ottieni | Fonte | Serve |
|---|---|---|---|
| **Tutto il mondo** | uragani, tifoni e cicloni; terremoti; radar meteo, fulmini e nuvole; una previsione in ciascuno dei tuoi luoghi; altitudine e profondità del mare nei tuoi luoghi | National Hurricane Center, Joint Typhoon Warning Center e NASA (Stati Uniti); US Geological Survey; le fonti radar della scheda mappa; MET Norway; Mapzen Terrain Tiles; NOAA NCEI | niente |
| **Tutto il mondo** | rilevamenti satellitari di incendi sulla mappa e allerte per incendi boschivi nei tuoi luoghi | NASA FIRMS (Stati Uniti) | una chiave mappa FIRMS gratuita |
| **Tutto il mondo**, fuori dagli Stati Uniti | vento e temperatura misurati nei tuoi luoghi, dall'aeroporto più vicino; il nome del mare | GeoNames | un nome utente GeoNames gratuito |
| **America del Nord**: Canada | radar più nitido; altitudine nei tuoi luoghi | Environment and Climate Change Canada (GeoMet); Natural Resources Canada | niente |
| **America del Nord**: Canada | stazioni di qualità dell'aria sulla mappa | AirNow (Stati Uniti) e partner | una chiave AirNow gratuita |
| **America del Nord**: Stati Uniti | allerte meteo e avvisi legati alle tempeste; la previsione di maltempo severo; vulcani; fiumi in piena; segnalazioni di tempeste e invernali; la previsione e il meteo misurato del Weather Service nei tuoi luoghi; altitudine | National Weather Service, NOAA, US Geological Survey | niente |
| **America del Nord**: Stati Uniti | allerte per fumo da incendi nei tuoi luoghi; stazioni di qualità dell'aria sulla mappa | AirNow | una chiave AirNow gratuita |
| **Asia**: Giappone | radar più nitido | Japan Meteorological Agency | niente |
| **Europa**: Finlandia | radar più nitido | Finnish Meteorological Institute | niente |
| **Europa**: Germania | radar più nitido | Deutscher Wetterdienst | niente |
| **Europa**: Norvegia, Svalbard e Jan Mayen | allerte meteo; previsioni marine dal Mare del Nord al Polo Nord; una previsione a Longyearbyen; altitudine e profondità del mare in Norvegia | MET Norway; Kartverket | niente |
| **Europa**: Norvegia, Svalbard e Jan Mayen | meteo misurato nei tuoi luoghi; ogni stazione meteo delle Svalbard e di Jan Mayen sulla mappa | MET Norway Frost | un client ID Frost gratuito |
| **Europa**: Paesi Bassi | radar più nitido | KNMI | una chiave KNMI gratuita |

⚠ Per ora le allerte meteo arrivano solo da Stati Uniti e Norvegia. Ovunque
altrove hai i livelli mondiali qui sopra, una previsione e il meteo misurato
nei tuoi luoghi, e allerte per forti terremoti vicini e (con una chiave) per
incendi boschivi.

Non è nell'elenco? [Diccelo](#aiutaci-a-farlo-crescere). Dove un servizio
meteo pubblica apertamente le sue allerte o i suoi dati, valuteremo di
aggiungerlo.

---

## Parte di Live Track: gli altri moduli

Live Track è un insieme di integrazioni di Home Assistant, una per ogni tipo
di cosa che si muove, tutte disegnate sulla stessa scheda mappa. Ognuna
funziona da sola; insieme formano un'unica immagine dal vivo. Condividono la
scheda mappa e una libreria Python
([saw-livetrack](https://github.com/StrausbergAutomationWorks/LiveTrackCore)),
quindi installarne un'altra non aggiunge richieste a una fonte che un'altra
già legge.

| Modulo | Cosa mette sulla mappa | Stato |
|---|---|---|
| [Live Track Aircraft](https://github.com/StrausbergAutomationWorks/LiveTrackAircraft) | aerei sopra di te tramite ADS-B, con rotte e icone per tipo | pubblicato |
| [Live Track Ships](https://github.com/StrausbergAutomationWorks/LiveTrackShips) | navi e imbarcazioni tramite AIS, vicino a te o ovunque | pubblicato |
| [Live Track Commuter Rail](https://github.com/StrausbergAutomationWorks/LiveTrackCommuterRail) | treni suburbani in Nord America, Europa e Australia | pubblicato |
| [Live Track Intercity Rail](https://github.com/StrausbergAutomationWorks/LiveTrackIntercityRail) | treni intercity e a lunga percorrenza in Nord America, Europa e Australia | pubblicato |
| [Live Track SALT](https://github.com/StrausbergAutomationWorks/LiveTrackSALT) | aerei e imbarcazioni dell'immigrazione e delle forze dell'ordine federali, da elenchi pubblici | pubblicato |
| **Live Track Weather** | meteo, tempeste e rischi naturali (questo modulo) | pubblicato |
| [Live Track Internet](https://github.com/StrausbergAutomationWorks/LiveTrackInternet) | interruzioni di internet, cavi sottomarini e collegamenti terrestri | pubblicato |
| Live Track Stations | tabelloni delle partenze e avvisi "è ora di andare" per ogni stazione | previsto |
| Live Track Satellites | satelliti che passano sopra di te | previsto |
| Live Track Freight Trains | treni merci e di servizio dove le ferrovie li pubblicano | previsto |
| Live Track Transit | autobus urbani, tram, traghetti e metropolitana | previsto |
| Live Track Intercity Buses | autobus interurbani e regionali | previsto |
| Live Track Commuter Buses | autobus per pendolari | previsto |
| [LiveTrackMapCard](https://github.com/StrausbergAutomationWorks/LiveTrackMapCard) | la scheda mappa condivisa su cui disegna ogni modulo | pubblicata, installata con ogni modulo |

Tutto è gratuito e open source. Niente è riservato agli sponsor.

---

## Prima di iniziare

* **Home Assistant** 2026.11 o successivo.
* **Il Marketplace** (HACS) nel tuo Home Assistant, per installarlo e
  aggiornarlo comodamente. Senza, puoi copiare i file a mano.
* **Accesso a Internet** per Home Assistant: tutto viene da servizi meteo
  pubblici.
* Niente da pagare e nessun account necessario per le funzioni di base. Le
  chiavi gratuite qui sopra sono facoltative.

---

## Installazione, passo dopo passo

### Dal Marketplace (consigliato)

1. In Home Assistant, apri **Impostazioni → Marketplace** (HACS).
2. Cerca **Live Track Weather** e aprilo.
3. Scegli **Scarica** (o **Installa**).
4. **Riavvia Home Assistant**: **Impostazioni → Sistema → Riparazioni** offre
   il riavvio, oppure usa **Impostazioni → Sistema → Riavvia**.

Se la ricerca non lo trova, aggiungilo tramite il suo link: scegli **Aggiungi da
link** (oppure il menu a tre puntini → **Repository personalizzati**), inserisci
`StrausbergAutomationWorks/LiveTrackWeather`, scegli **Integrazione** se viene
chiesto il tipo, poi prosegui dal passo 3.

Il Marketplace offre poi ogni nuova versione come aggiornamento.

### A mano

1. Scarica il codice sorgente dell'[ultima versione](https://github.com/StrausbergAutomationWorks/LiveTrackWeather/releases/latest).
2. Copia la sua cartella `custom_components/live_track_weather` nella cartella
   `custom_components` della cartella di configurazione di Home Assistant
   (crea `custom_components` se non c'è).
3. Riavvia Home Assistant.

---

## Configurazione, passo dopo passo

1. Apri **Impostazioni → Dispositivi e servizi**.
2. Scegli **Aggiungi integrazione** (in basso a destra) e cerca
   **Live Track Weather**.
3. Scegli **Invia**. Non c'è niente da scrivere: un solo Live Track Weather
   copre tutto il mondo.

Tutto qui. Allerte, tempeste, terremoti, vulcani, piene, segnalazioni di
tempeste e le allerte di MET Norway iniziano a comparire in pochi minuti, e la
tua casa è sorvegliata: **Alert at Home**, **Forecast at Home**, **Wind at
Home**, **Temperature at Home**, **Elevation at Home** e **Depth at Home**.

### Cambiare cosa sorveglia: le opzioni

Apri **Impostazioni → Dispositivi e servizi → Live Track Weather →
Configura** (l'ingranaggio). Ogni opzione, in parole semplici:

| Opzione | Cosa fa | Predefinito |
|---|---|---|
| **Secondi tra un'interrogazione e l'altra** | ogni quanto viene scaricato l'elenco delle allerte statunitensi, da 60 a 900 secondi | 180 |
| **Sorveglia la casa** | la tua casa riceve i sensori "… at Home" e la previsione; disattiva per eliminarli | attivo |
| **Sorveglia anche queste persone, tracker di dispositivi o zone** | ognuno riceve il proprio "Alert at …", "Forecast at …", vento, temperatura, altitudine e profondità, che lo seguono quando si sposta. Scegli il telefono di un familiare, il tracker di un camper, la zona di una casa vacanze | nessuno |
| **Allerte che accendono un luogo** | qualsiasi allerta (avvisi e comunicati compresi), oppure solo quelle moderate, gravi o estreme. Ogni allerta resta elencata nel sensore | qualsiasi allerta |
| **Vento e temperatura misurati solo da stazioni aeroportuali** | disattivo: la stazione più vicina di qualsiasi tipo (spesso più vicina a un campeggio); attivo: solo aeroporti | disattivo |
| **MAP_KEY NASA FIRMS** | allerte incendi e rilevamenti di incendi (vedi [chiavi gratuite](#chiavi-gratuite-che-attivano-di-più-passo-dopo-passo)) | vuoto |
| **Un incendio conta entro** | quanto vicino deve essere un incendio per accendere un luogo, da 5 a 150 km (da 3 a 93 miglia) | 50 km (31 miglia) |
| **Chiave API AirNow** | allerte fumo e stazioni di qualità dell'aria | vuoto |
| **Il fumo conta da un AQI PM2.5 di** | l'indice di qualità dell'aria che accende un luogo | 90 |
| **Rilevamenti di incendi e stazioni di qualità dell'aria sulla mappa** | quali regioni disegnare: i 48 stati contigui e le Hawaii, l'Alaska, il Canada, il mondo intero (solo incendi) | nessuna |
| **Terremoto più piccolo sullo strato di punti della mappa** | esclude i piccoli punti dei terremoti sotto una magnitudo; gli indicatori restano | vuoto: tutti i terremoti |
| **Chiave API KNMI** | radar più nitido sui Paesi Bassi | vuoto |
| **Nome utente GeoNames** | meteo fuori dagli Stati Uniti, nomi dei mari | vuoto |
| **ID client MET Norway Frost** | stazioni delle Svalbard e di Jan Mayen; meteo misurato in Norvegia | vuoto |

Ogni chiave viene controllata una volta quando la inserisci, e ti viene detto
se non funziona. Lascia un campo vuoto per disattivare quella parte.

---

## Chiavi gratuite che attivano di più, passo dopo passo

Sono tutte gratuite e personali: ogni persona che installa Live Track Weather
ottiene le proprie. Incolla ciascuna in **Impostazioni → Dispositivi e
servizi → Live Track Weather → Configura**.

### NASA FIRMS (incendi boschivi)

1. Apri <https://firms.modaps.eosdis.nasa.gov/api/map_key/>.
2. Inserisci il tuo indirizzo email e richiedi una **MAP_KEY**. Arriva per
   email.
3. Incollala in **MAP_KEY NASA FIRMS**, e regola **Un incendio conta entro**
   se 50 km (31 miglia) non vanno bene per te.
4. Per vedere gli incendi sulla mappa, spunta anche una regione in
   **Rilevamenti di incendi e stazioni di qualità dell'aria sulla mappa**.

### AirNow (fumo e qualità dell'aria, Stati Uniti)

1. Apri <https://docs.airnowapi.org/> e scegli **Request an AirNow API
   Account**.
2. Conferma l'email, accedi e copia la tua **API key** dalla pagina del tuo
   account.
3. Incollala in **Chiave API AirNow**.

### KNMI (radar sui Paesi Bassi)

1. Registrati sulla KNMI Data Platform, <https://developer.dataplatform.knmi.nl/>.
2. Richiedi una chiave per l'API **WMS**. (Una chiave per l'API Open Data qui
   non funziona.)
3. Incollala in **Chiave API KNMI**. La mappa usa allora il radar del KNMI sui
   Paesi Bassi; senza, quello di RainViewer.

### GeoNames (meteo fuori dagli Stati Uniti)

1. Crea un account gratuito su <https://www.geonames.org/login>.
2. Apri l'email di conferma che invia GeoNames e conferma.
3. Accedi, apri la pagina del tuo account e **attiva i servizi web
   gratuiti**.
4. Inserisci il tuo **nome utente** (non la password) in
   **Nome utente GeoNames**.

### MET Norway Frost (stazioni delle Svalbard, meteo in Norvegia)

1. Apri <https://frost.met.no/auth/requestCredentials.html>.
2. Inserisci il tuo indirizzo email. Ricevi un **ID client** e un segreto
   client.
3. Incolla l'**ID client** in **ID client MET Norway Frost**. Il segreto non
   serve.

---

## Mettere la mappa su una plancia

La mappa è [LiveTrackMapCard](https://github.com/StrausbergAutomationWorks/LiveTrackMapCard),
la scheda su cui disegna ogni modulo di Live Track. **Viene installata con
Live Track Weather**: niente da scaricare, niente da copiare in `www`, nessuna
risorsa da aggiungere.

1. Apri una plancia, scegli la matita (**Modifica plancia**), poi
   **Aggiungi scheda**.
2. Scorri fino in fondo e scegli **Manuale**.
3. Incolla questo e scegli **Salva**:

```yaml
type: custom:live-track-map-card
entity_filter:
  include:
    - domain: geo_location
      attributes:
        source: live_track_weather
```

Le allerte meteo, la previsione di maltempo, le zone di MET Norway, i coni e le
traiettorie delle tempeste, le linee di scuotimento dei terremoti e gli strati
di punti compaiono da soli. Gli indicatori (tempeste, terremoti, vulcani,
idrometri, la previsione di Longyearbyen e le stazioni delle Svalbard) arrivano
tramite il filtro qui sopra.

Gli altri moduli di Live Track vanno in `entity_filter` allo stesso modo: una
regola `- domain: geo_location` in più per ogni fonte.

**Sulla mappa:**

* Il **controllo degli strati** in alto a destra ha una casella per ogni
  strato: le allerte statunitensi, la previsione di maltempo, i cicloni
  tropicali, le allerte e le previsioni marine di MET Norway, i terremoti, lo
  scuotimento sismico, le segnalazioni di tempeste, le segnalazioni invernali,
  i rilevamenti di incendi, le stazioni di qualità dell'aria, il radar meteo,
  il movimento del radar, i fulmini e le nuvole. La scelta di ogni spettatore
  viene conservata nel suo browser.
* **Clicca** su un indicatore, un'area, una linea o un punto per saperne di
  più.
* La **scheda filtro** (`custom:live-track-map-filter-card`) può nascondere le
  stazioni delle Svalbard, come **Observed weather (MET Norway)**.
* Il riconoscimento di ogni fonte compare nella riga di attribuzione della
  mappa finché i suoi dati sono mostrati.

Se le risorse delle tue plance sono definite in YAML
(`lovelace: resource_mode: yaml`), non si può registrare nulla per te: un
problema in **Riparazioni** indica allora la riga esatta da aggiungere.
Qualsiasi altra scheda mappa che mostra entità `geo_location` mostra gli
indicatori, ma non le allerte, le aree o i punti.

---

## Usarlo nelle automazioni

Tutto è una normale entità di Home Assistant, quindi l'editor delle
automazioni funziona con esso, senza codice.

**Una notifica sul telefono quando la casa è dentro un'allerta:**

1. **Impostazioni → Automazioni e scenari → Crea automazione → Crea una
   nuova automazione**.
2. **Quando**: *Entità → Stato*, entità **Alert at Home**, a **Non sicuro**
   (acceso).
3. **Allora esegui**: *Notifiche → Invia una notifica tramite mobile_app_…*,
   con un messaggio come `Allerta meteo a casa: {{ state_attr('binary_sensor.live_track_weather_alert_at_home', 'highest') }}`.
4. Salva.

**Ritirare la tenda con una raffica:** *Quando* **Wind gust at Home** supera
50 km/h (o 30 mph), *allora* chiudi la copertura della tenda.

**Altre idee:** far lampeggiare una luce quando **Severe weather outlook**
raggiunge 3 (Enhanced); avvisare il proprietario del camper quando **Alert at
Camper** si accende per un incendio entro 50 km; inviare una notifica quando
**Temperature at Cabin** scende sotto zero; mostrare **Forecast at Boat** su
una scheda meteo mentre è in mare; avvisare la famiglia quando **Alert at
Cabin**, in Norvegia, si accende per un'allerta di MET Norway.

---

## Tutto sulla mappa, nel dettaglio

### Allerte meteo statunitensi

Ogni allerta attiva del National Weather Service: avvisi, allerte preventive,
avvertenze e comunicati per contee, zone terrestri, marine, d'altura e di
meteo antincendio, riempiti in trasparenza con il colore che il Weather
Service dà a ogni evento (quello di priorità più alta dove le allerte si
sovrappongono). Gli avvisi legati alle tempeste, come quelli di tornado,
temporale violento e piena improvvisa, sono disegnati con il proprio poligono,
non l'intera contea. Non si imposta alcuna posizione: la mappa mostra ciò che
è sullo schermo. I contorni delle zone (11.651, semplificati a circa 500 m,
circa 3,6 MB) arrivano con ogni versione e ogni browser li scarica una volta
per versione.

**Sensore `US alerts`**: il numero di allerte attive; i suoi attributi portano
l'elenco che la mappa disegna (`zones`, `polygons`, `styles`, `updated`,
`shapes_url`), che cambia quasi a ogni interrogazione e non viene registrato
nello storico.

### Cicloni tropicali: uragani, tifoni, cicloni

Ogni ciclone tropicale attivo nel mondo, un indicatore per tempesta con il suo
nome come etichetta e colorato per categoria: depressione blu, tempesta
tropicale verde acqua, categorie da 1 a 5 oro, arancione, arancione scuro,
rosso e magenta, post-tropicale grigio. Passaci sopra con il mouse per la
classe, il vento, la pressione e il movimento.

* Tempeste del **National Hurricane Center** (Atlantico, Pacifico orientale e
  centrale): il cono di previsione (blu), la traiettoria prevista (rosso), i
  venti attuali di 34, 50 e 64 nodi (63, 93 e 119 km/h; 39, 58 e 74 mph)
  (giallo, arancione, rosso) e la
  traiettoria passata (nero).
* **Ogni altro bacino**, dal Joint Typhoon Warning Center tramite EONET della
  NASA: l'indicatore e la traiettoria passata. Una tempesta la cui ultima
  posizione ha più di 24 ore non viene mostrata.

Gli indicatori sono `geo_location.storm_<id>` (`geo_location.storm_ep222026`),
con gli attributi `storm_class`, `storm_category` (TD, TS, H1-H5, PT),
`max_wind_kmh`, `pressure_hpa`, `course_deg`, `speed_kmh`, `last_seen`,
`advisory_number` e `storm_source`. Vanno e vengono con le tempeste e non
hanno un ID univoco, quindi non si possono rinominare dall'interfaccia.
**Sensore `Tropical cyclones`**: il numero di tempeste.

### Previsione di maltempo severo

La previsione categorica del giorno 1 dello Storm Prediction Center: dove oggi
possono verificarsi temporali violenti, da 1 Marginal, 2 Slight, 3 Enhanced,
4 Moderate a 5 High, con i colori propri del Center, sotto le allerte.
**Sensore `Severe weather outlook`**: il rischio più alto in qualsiasi punto
degli Stati Uniti oggi, da 0 a 5, registrato perché possa guidare
un'automazione; attributi `risk`, `issued`, `valid_from`, `valid_to`. L'area
dei temporali ordinari non viene disegnata.

### Terremoti

Ogni terremoto che l'US Geological Survey elenca per le ultime 24 ore, in
tutto il mondo (circa 240 al giorno):

* **Indicatori** da magnitudo 4,5 in su, e per ogni terremoto che le persone
  hanno segnalato di aver avvertito, con la magnitudo come etichetta
  (`geo_location.quake_<USGS id>`). Clicca per l'ora, la profondità, le
  segnalazioni di chi l'ha avvertito, lo scuotimento più forte, il livello di
  allerta PAGER e la pagina dell'evento dell'USGS. La "bandiera tsunami" non è
  un'allerta; le allerte tsunami vengono dalla NOAA (tsunami.gov).
* **Punti** per ogni altro terremoto (e brillamenti di cava ed esplosioni in
  grigio), su uno strato a sé: **sensore `Earthquakes`**. L'opzione
  **Terremoto più piccolo sullo strato di punti della mappa** esclude quelli
  piccoli.
* **Linee di scuotimento** (USGS ShakeMap) per i terremoti più forti del
  giorno, magnitudo 6 e oltre o scuotimento forte, al massimo cinque:
  **sensore `Earthquake shaking`**.

### Vulcani in allerta

Ogni vulcano degli Stati Uniti a livello di allerta Advisory o codice colore
per l'aviazione Yellow e oltre, un indicatore nel suo codice colore con il suo
nome come etichetta (`geo_location.volcano_<number>`). Clicca per il livello
di allerta, il codice colore, da quando, la sintesi dell'osservatorio e i link
al bollettino e alla pagina del vulcano.

### Fiumi in piena ora o con piena prevista

Ogni idrometro o mareografo degli Stati Uniti **in piena lieve o peggio
adesso**, o per cui è prevista, etichettato Minor, Moderate o Major nei colori
di piena del Weather Service (`geo_location.river_<gauge id>`). **Un anello
scuro significa che è in piena adesso**; senza l'anello è una previsione.
Clicca per il livello attuale, il livello previsto, le soglie di piena, la
portata e la pagina dell'idrometro. ⚠ Alcuni idrometri hanno soglie di piena
che sembrano valori provvisori e mostrano quindi Major (Devils Lake, Dakota
del Nord).

### Segnalazioni di tempeste

Ogni NWS Local Storm Report delle ultime 24 ore di un tornado o di una tromba
marina, di una nube a imbuto, di grandine, di vento temporalesco o danni, di
una piena improvvisa o di un'inondazione: rosso per i tornado, blu per il
vento, verde per la grandine, verde acqua per le inondazioni. Una segnalazione
significativa è più grande e ha un anello scuro: qualsiasi tornado, grandine
di 5 cm (2 pollici) o più, o vento di 120 km/h (65 nodi) o più. Le segnalazioni sbiadiscono con
il tempo: meno di un'ora, da 1 a 6 ore, da 6 a 24 ore. Clicca per il tipo, la
dimensione o la velocità, il luogo, l'ora, l'ufficio del NWS e le note.
**Sensore `Storm reports`**: il numero di punti. ⚠ Sono segnalazioni così come
le inviano le persone, prima che il Weather Service le verifichi, e possono
impiegare 30 minuti a comparire.

### Segnalazioni invernali

Dalle stesse segnalazioni, su uno strato a sé sotto le segnalazioni di
tempeste: neve, forti nevicate e rovesci di neve (blu ardesia), bufere di neve
(rosso arancio), nevischio (orchidea), pioggia gelata, pioviggine gelata e
tempeste di ghiaccio (magenta scuro), danni da neve e ghiaccio (grigio), freddo
estremo e temperatura percepita (blu), valanghe (marrone) e ingorghi di
ghiaccio (verde acqua scuro), ciascuno con un sottile anello scuro. Quelle
significative sono più grandi: 30 cm di neve (12 pollici), 1,3 cm di
nevischio (mezzo pollice), 6 mm di ghiaccio (un quarto di pollice) o qualsiasi
tempesta di ghiaccio. Clicca
per la quantità in pollici e cm o mm, o la temperatura in °F e °C.
**Sensore `Winter reports`**. ⚠ Una grande tempesta porta migliaia di
segnalazioni; dove due si sovrapporrebbero ne viene disegnata una, quindi
ingrandisci.

### MET Norway: allerte, previsioni marine, la previsione di Longyearbyen

* **Allerte** per la terraferma, la costa e i mari della Norvegia e i mari fino
  al Polo Nord, nel giallo, arancione o rosso di MET, accanto alle allerte
  statunitensi. Cliccane una per ciò che è previsto, le conseguenze, i
  consigli e quando (in inglese). **Sensore `MET Norway warnings`**.
* **Previsioni marine** per 56 zone di mare e 39 zone costiere, comprese
  quelle delle Svalbard, sotto le allerte. Cliccane una per la sua previsione
  e ogni allerta per vento, ghiaccio o bassa polare.
  **Sensore `MET Norway marine forecasts`**.
* **Un punto di previsione a Longyearbyen**, con la temperatura come
  etichetta; cliccalo per la previsione ogni sei ore per un giorno
  (`geo_location.met_forecast_longyearbyen`).

### Meteo misurato alle Svalbard e a Jan Mayen (ID client Frost)

Un punto verde acqua per ogni stazione meteo delle Svalbard, dell'Isola degli
Orsi, di Hopen e di Jan Mayen la cui temperatura e il cui vento hanno entrambi
meno di due ore (circa 30), con la temperatura come etichetta
(`geo_location.frost_sn99840` per Svalbard Lufthavn, e così via). Cliccane uno
per la temperatura, il vento e la direzione, la raffica più forte dell'ultima
ora, l'umidità, la pressione, l'altezza della neve e l'ora. Le stazioni che
trasmettono solo la temperatura non vengono disegnate; di due stazioni a meno
di 1 km ne viene disegnata una. I valori che Frost segna come molto incerti o
errati non vengono usati; i valori finora controllati solo automaticamente (di
solito l'ora più recente di MET) vengono mostrati, e il popup dice "Automatic
check only".

### Incendi boschivi e qualità dell'aria (chiavi FIRMS e AirNow)

Scegli le regioni in **Rilevamenti di incendi e stazioni di qualità dell'aria
sulla mappa**:

* **Rilevamenti di incendi** (serve la chiave FIRMS): ogni rilevamento
  satellitare di incendio delle ultime 24 ore (NOAA-20 e NOAA-21 VIIRS) come
  piccoli punti rossi. Stabilimenti, raffinerie, torce e altre fonti di calore
  fisse classificate dalla NASA sono escluse. Clicca per quando, quale
  satellite, la potenza radiativa dell'incendio e l'affidabilità secondo la
  NASA. **Sensore `Fire detections`**.
* **Stazioni di qualità dell'aria** (serve la chiave AirNow; Stati Uniti e
  Canada): ogni monitor di particolato fine (PM2.5), colorato secondo il suo
  AQI nei colori dell'EPA, ogni ora. **Sensore `Air quality sites`**.

### Radar meteo, fulmini e nuvole

Disegnati dalla scheda mappa stessa, senza configurare nulla: uno strato radar
che sceglie la fonte più nitida per ciò che è sullo schermo (RainViewer, NOAA
nowCOAST e GeoMet del Canada in Nord America; l'FMI della Finlandia e il DWD
della Germania in Europa; la JMA del Giappone; il KNMI sui Paesi Bassi con la
tua chiave), il movimento del radar, i fulmini da nowCOAST e le nuvole dai
satelliti GOES ed EUMETSAT.

---

## Tutto nei tuoi luoghi, nel dettaglio

### Alert at …

**`Alert at Home`** (`binary_sensor.live_track_weather_alert_at_home`, classe
di dispositivo *safety*: acceso significa non sicuro), e uno per ogni persona,
tracker o zona che sorvegli. Si accende quando il luogo è:

* dentro un'**allerta meteo statunitense** o un'**allerta di MET Norway**
  (secondo la regola propria del Weather Service: un avviso di tornado o di
  inondazione conta dentro il suo poligono, non in tutta la contea; le zone
  vengono dal Weather Service stesso, quindi un luogo su una costa o su un
  confine di contea ottiene la risposta giusta);
* vicino a un **terremoto** forte nelle ultime 24 ore: magnitudo 4 entro 50 km
  (31 miglia), 5 entro 150 km (93 miglia), 6 entro 300 km (186 miglia), 7 entro
  600 km (373 miglia);
* dentro la zona di pericolo di un **vulcano** a livello Watch o Orange e
  oltre (il National Volcanic Threat Layer dell'USGS, fornito con
  l'integrazione);
* con la chiave FIRMS, vicino a un **incendio boschivo** (entro la distanza
  che imposti, 50 km (31 miglia) per impostazione predefinita; i rilevamenti arrivano in
  Home Assistant da 2 a 4 ore dopo il passaggio del satellite);
* con la chiave AirNow, nel **fumo di un incendio**: il monitor PM2.5 più
  vicino entro 80 km (50 miglia) all'AQI che imposti o sopra, 90 per impostazione
  predefinita (luoghi negli Stati Uniti).

Attributi: `alerts` (ogni allerta nel luogo, la peggiore per prima, con
`event`, `severity`, `headline`, `onset`, `ends`, `source` e un link),
`highest`, `zones`; con le chiavi, `fires_near`, `nearest_fire_km`,
`pm25_aqi`, `pm25_site` e altro. Le zone di un tracker in movimento vengono
richieste di nuovo dopo uno spostamento di oltre 1 km. La NASA sconsiglia di
usare i soli rilevamenti di incendi per decisioni sul campo: segui gli ordini
di evacuazione.

### Forecast at …

**`Forecast at Home`** (`weather.live_track_weather_forecast_at_home`), e una
per ogni luogo sorvegliato, per ogni scheda meteo e `weather.get_forecasts`:
giornaliera, giorno e notte, e oraria.

* **Sulla terraferma degli Stati Uniti**: la previsione del National Weather
  Service per la griglia di 2,5 km del luogo, sette giorni di giorno e di
  notte con il testo della previsione, e oraria per sei giorni e mezzo.
* **Ovunque altrove, e su tutte le acque**: la previsione di MET Norway,
  oraria per circa due giorni e mezzo, poi ogni sei ore fino a circa dieci
  giorni.

Cambia fonte quando il luogo si sposta (una barca che lascia il porto, un
camper che entra in Canada).

### Wind at …, Wind gust at …, Wind direction at …, Temperature at …

Ciò che ha misurato la stazione meteo più vicina, per ogni luogo sorvegliato
(`sensor.live_track_weather_wind_at_home` e così via).

* **Negli Stati Uniti**: la stazione del National Weather Service più vicina
  di qualsiasi rete (aeroporti, stazioni meteo antincendio e stradali,
  stazioni di volontari), o solo aeroporti con l'opzione; la successiva, fino
  a tre, quando una non ha nulla di recente.
* **In Norvegia e alle Svalbard**, con un ID client Frost: la più vicina delle
  stazioni proprie di MET Norway (misurato in 22 luoghi della Norvegia: da 0,4
  a 11 km). La raffica è la più forte dell'ultima ora.
* **Altrove**, con un nome utente GeoNames: il bollettino meteo (METAR)
  dell'aeroporto più vicino, entro circa 100 km (60 miglia).
* Un sensore è **non disponibile** quando nessun bollettino con meno di due
  ore contiene il suo valore. Una raffica è sconosciuta quando non ne è stata
  segnalata alcuna. Attributi: `station`, `station_name`, `provider`,
  `distance_km`, `observed`, `age_min`.

### Elevation at … e Depth at …

**`Elevation at Home`** e **`Depth at Home`**, e uno di ciascuno per ogni
luogo sorvegliato, controllati all'avvio e dopo uno spostamento di oltre
500 m.

* **Altitudine** dalla prima fonte con un valore: USGS 3DEP (Stati Uniti e
  regioni di confine, al metro), Natural Resources Canada, Kartverket
  (Norvegia continentale), poi i Terrain Tiles di Mapzen per il resto del
  mondo.
* **Sull'acqua** l'altitudine è la superficie e **Depth** è la profondità
  sotto il luogo, da Kartverket in Norvegia o da NOAA NCEI altrove (Grandi
  Laghi compresi); sconosciuta sulla terraferma. Con un nome utente GeoNames,
  `sea` indica il nome del mare.
* ⚠ Limiti noti: l'altitudine alle Svalbard è circa 35 m troppo alta (nessuna
  fonte migliore trovata); fiumi, porti e bacini artificiali non hanno
  profondità; nei mari poco profondi senza GeoNames l'altitudine è il fondale;
  un lago sotto il livello del mare raggiunto solo dai terrain tiles mostra 0.

---

## Tutte le entità che crea

| Entità | Cos'è |
|---|---|
| `sensor.live_track_weather_us_alerts` | numero di allerte statunitensi attive; l'elenco che la mappa disegna |
| `sensor.live_track_weather_tropical_cyclones` | numero di cicloni tropicali |
| `sensor.live_track_weather_severe_weather_outlook` | rischio più alto di temporali violenti oggi, da 0 a 5 |
| `sensor.live_track_weather_met_norway_warnings` | allerte di MET Norway disegnate |
| `sensor.live_track_weather_met_norway_marine_forecasts` | zone di previsione marina di MET Norway |
| `sensor.live_track_weather_earthquakes` | punti dei terremoti sulla mappa |
| `sensor.live_track_weather_earthquake_shaking` | ShakeMap disegnate |
| `sensor.live_track_weather_storm_reports` | segnalazioni di tempeste disegnate |
| `sensor.live_track_weather_winter_reports` | segnalazioni invernali disegnate |
| `sensor.live_track_weather_fire_detections` | rilevamenti di incendi (chiave FIRMS e una regione) |
| `sensor.live_track_weather_air_quality_sites` | stazioni di qualità dell'aria (chiave AirNow e una regione) |
| `sensor.live_track_weather_knmi_radar` | immagine radar KNMI più recente (chiave KNMI) |
| `geo_location.storm_…`, `quake_…`, `volcano_…`, `river_…`, `met_forecast_…`, `frost_…` | gli indicatori; vanno e vengono e non hanno un ID univoco |
| `binary_sensor.live_track_weather_alert_at_home` | Alert at Home (e uno per ogni luogo sorvegliato) |
| `weather.live_track_weather_forecast_at_home` | Forecast at Home (e una per ogni luogo sorvegliato) |
| `sensor.live_track_weather_wind_at_home`, `…_wind_gust_at_home`, `…_wind_direction_at_home`, `…_temperature_at_home` | meteo misurato a casa (e per luogo) |
| `sensor.live_track_weather_elevation_at_home`, `…_depth_at_home` | altitudine e profondità a casa (e per luogo) |

Gli attributi che cambiano a ogni interrogazione (elenchi, forme, popup) sono
tenuti fuori dallo storico di Home Assistant, così il tuo database non cresce
con essi.

---

## Cosa invia e scarica

**Sulla tua posizione.** La posizione della tua casa e di ogni luogo
sorvegliato viene inviata, arrotondata a circa 11 m, solo dove un servizio ne
ha bisogno: al National Weather Service per conoscere le zone, la griglia di
previsione e le stazioni del luogo; fuori dall'area di previsione
statunitense, a MET Norway per la sua previsione; all'USGS (e, dove l'USGS non
ha nulla, a Natural Resources Canada, Kartverket e NOAA NCEI) per altitudine e
profondità, all'avvio e dopo uno spostamento di oltre 500 m; con le tue
chiavi, a NASA FIRMS (un riquadro attorno al luogo), AirNow, GeoNames e Frost
di MET Norway. Disattiva **Sorveglia la casa** e non sorvegliare nient'altro, e
nessuna posizione viene inviata. Nient'altro su di te viene inviato da
nessuna parte.

**Quanto.** L'elenco delle allerte statunitensi circa 100 KB ogni 3 minuti
(regolabile); gli altri chiedono un file solo se è cambiato, dove il servizio
lo consente: bollettini degli uragani ogni 5 minuti, EONET ogni 30, la
previsione di maltempo ogni 5, le allerte di MET Norway ogni 5, le previsioni
marine ogni 15-30 e le previsioni puntuali ogni 30 (ciascuna un minuto dopo a
caso, come chiede MET, e niente per 30 minuti dopo un rifiuto); i terremoti
dell'USGS ogni 5 minuti (circa 170 KB), i vulcani ogni 10, i fiumi ogni 30, le
segnalazioni di tempeste ogni 10; Frost ogni 10 minuti (circa 80 KB); GeoNames
entro la metà dei suoi 10.000 crediti gratuiti al giorno; il KNMI al massimo
circa 24 richieste all'ora, e solo mentre una mappa lo mostra. Dopo un errore,
ogni servizio viene lasciato in pace per un po' prima di essere interrogato di
nuovo.

---

## Aiutaci a farlo crescere

Live Track Weather sta ancora crescendo. Aggiungiamo paesi, servizi meteo e
pericoli man mano che li troviamo, e vogliamo sapere cosa ti piacerebbe dopo.

### Suggerisci qualcosa

Manca il tuo servizio meteo? Qualcosa è sbagliato o difficile da capire?
Diccelo nel modo più facile per te:

* [**Compila un breve modulo**](https://github.com/StrausbergAutomationWorks/LiveTrackWeather/issues/new?template=it.yml)
  in italiano. Ti serve un account GitHub gratuito.
* **Scrivi un'email** a
  [StrausbergAutomationWorks@recordwise.org](mailto:StrausbergAutomationWorks@recordwise.org).
  Non serve un account.

In entrambi i casi, ci aiuta se ci dici:

* cosa ti piacerebbe vedere, e dove nel mondo;
* un link a dove vengono pubblicati i dati, se ne conosci uno (una pagina di
  open data, un feed pubblico, il sito di un servizio meteo): non è
  necessario, ma aiuta;
* la lingua del tuo Home Assistant, se il problema riguarda il testo o una
  traduzione.

Scrivi in inglese o nella tua lingua, come ti è più facile.

### Aggiungilo tu, con il nostro aiuto

Se vuoi aggiungere qualcosa tu stesso, ti aiuteremo a farlo, dalla prima
domanda fino alla versione finita. Non devi essere uno sviluppatore per
iniziare:

* **Una traduzione.** I testi della finestra di configurazione sono un breve
  elenco di frasi in un unico file di testo. Ti mostreremo quale file e quali
  righe.
* **Un nuovo paese o un nuovo servizio meteo.** Dicci dove vengono pubblicati
  i dati. Possiamo scrivere il codice insieme, o rivedere il tuo.
* **Provarlo dove vivi.** Installalo, guarda la tua parte della mappa e dicci
  cosa è giusto e cosa no.
* **Una correzione a questo README.** Se un passaggio non corrispondeva a
  quello che hai visto, dicci cosa hai visto.

[**Raccontaci cosa hai in mente**](https://github.com/StrausbergAutomationWorks/LiveTrackWeather/issues/new?template=it.yml)
o scrivi a
[StrausbergAutomationWorks@recordwise.org](mailto:StrausbergAutomationWorks@recordwise.org),
e ti risponderemo con i passi successivi.

---

## Lingue

Questo README: [English](README.md), [Deutsch](README.de.md),
[Français](README.fr.md), [Nederlands](README.nl.md),
[简体中文](README.zh-Hans.md), [Español](README.es.md), **Italiano**,
[Dansk](README.da.md) e [Kalaallisut](README.kl.md) (una breve bozza; finché
un madrelingua non l'avrà letta, la pagina danese è quella affidabile). Ogni
README tradotto è completo.

La finestra di configurazione e le opzioni compaiono nella lingua del tuo Home
Assistant quando è una di queste: English, Dansk, Deutsch, Español,
Français, Gaeilge, Íslenska, Italiano, Nederlands, Norsk Bokmål, Polski,
Português, Português (BR), Suomi, Svenska e 简体中文. Qualsiasi altra lingua
mostra l'inglese. I nomi delle entità (**Alert at Home** e così via) e le
etichette della scheda mappa sono in inglese in tutte le lingue.

Hai trovato un errore in una traduzione, o ti serve un'altra lingua? Diccelo
su <https://github.com/StrausbergAutomationWorks/LiveTrackWeather/issues>, o
[traducilo con il nostro aiuto](#aggiungilo-tu-con-il-nostro-aiuto).

---

## Riconoscimenti e licenze

* Il National Weather Service, il National Hurricane Center, lo Storm
  Prediction Center, il National Water Prediction Service, il Joint Typhoon
  Warning Center, la NASA e l'US Geological Survey sono agenzie del governo
  degli Stati Uniti; i loro dati sono opere del governo degli Stati Uniti. I
  dati di AirNow sono preliminari e non verificati (US EPA e partner).
* **MET Norway**: dati sotto la Norwegian Licence for Open Government Data
  (NLOD) 2.0 e Creative Commons Attribution 4.0; le osservazioni di Frost
  sotto Creative Commons Attribution 3.0 Norway. Questa integrazione
  arrotonda le aree, ricolora le allerte e converte le unità.
* **KNMI**: radar sotto Creative Commons Attribution 4.0, ritagliato e
  ridimensionato in tessere di mappa.
* **GeoNames**: bollettini METAR e nomi dei mari sotto Creative Commons
  Attribution 4.0.
* **Altitudine**: il CDEM di Natural Resources Canada, Open Government
  Licence - Canada; Kartverket, Creative Commons Attribution 4.0; NOAA NCEI, governo
  degli Stati Uniti. **Terrain Tiles**: Mapzen, e le fonti elencate
  nell'attribuzione Joerd di Mapzen (`tilezen/joerd`, `docs/attribution.md`),
  riportate qui alla lettera: ArcticDEM terrain data DEM(s) were created from
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
* **Zone di pericolo vulcanico**: USGS National Volcanic Threat Layer (2024,
  CC0).

Nessuna di queste organizzazioni ha realizzato o approvato questa
integrazione.

**Codice**: MIT, in [LICENSE](LICENSE).

**Per gli sviluppatori:** `tools/build_shapes.py` ricostruisce il file delle
zone di allerta dagli shapefile del NWS (<https://www.weather.gov/gis/>) e
`tools/build_colours.py` la tabella dei colori dalla pagina della mappa dei
pericoli del NWS; i test si eseguono con `python -m unittest discover -s tests`.

---

## Parole chiave

Home Assistant meteo · Home Assistant allerte meteo · allerte NWS · National
Weather Service · mappa delle allerte meteo · avviso di tornado · temporale
violento · piena improvvisa · tempesta invernale · tracciamento uragani ·
tempesta tropicale · tifone · ciclone · cono dell'uragano · NHC · JTWC · SPC
outlook · previsione di maltempo · mappa dei terremoti · allerta terremoto ·
terremoti USGS · ShakeMap · allerta vulcano · mappa delle piene · idrometro ·
NWPS · segnalazioni di tempeste · grandine · altezza della neve · bufera di
neve · tempesta di ghiaccio · mappa degli incendi boschivi · allerta incendi ·
rilevamento incendi · NASA FIRMS · VIIRS · allerta fumo · qualità dell'aria ·
AQI · PM2.5 · AirNow · radar meteo · radar pioggia · mappa dei fulmini · MET
Norway · yr · meteo Svalbard · Longyearbyen · Jan Mayen · Frost API ·
previsione marina · radar KNMI · GeoNames · METAR · stazione meteo · sensore
raffiche · sensore di temperatura · previsione per un tracker · meteo camper ·
meteo barca · sensore di altitudine · profondità dell'acqua · geo_location ·
binary_sensor · weather entity · scheda mappa · Lovelace · HACS · Marketplace ·
Live Track · LiveTrack · weather warning · vejrvarsel · Unwetterwarnung ·
weerwaarschuwing · alerte météo · alerta meteorológica · farevarsel · 天气预警 ·
StrausbergAutomationWorks

---

**Riconoscimento.** StrausbergAutomationWorks riconosce i popoli indigeni di
tutte le terre e le acque di questa mappa, in tutto il mondo, e rende omaggio ai
loro Anziani del passato e del presente.
