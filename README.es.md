# Live Track Weather

[English](README.md) · [Deutsch](README.de.md) · [Français](README.fr.md) · [Nederlands](README.nl.md) · [简体中文](README.zh-Hans.md) · **Español** · [Italiano](README.it.md) · [Dansk](README.da.md) · [Kalaallisut](README.kl.md) · [Todos los idiomas](#idiomas)

**Avisos meteorológicos, tormentas, terremotos, inundaciones, incendios
forestales, radar y tiempo en directo para Home Assistant, en un solo mapa.**
Live Track Weather pone en tu mapa de Home Assistant avisos meteorológicos
oficiales, huracanes y tifones, terremotos, volcanes, crecidas de ríos,
informes de tormentas y de nieve, datos de incendios forestales y humo,
previsiones marítimas y estaciones meteorológicas, y vigila los peligros para
tu casa, los teléfonos de tu familia y tu autocaravana. Las tormentas, los
terremotos, el radar y las previsiones cubren todo el mundo; EE. UU., Noruega
y Svalbard son los que tienen más detalle ([dónde funciona](#dónde-funciona)).

> **Live Track Weather es un módulo de Live Track**, una familia de
> integraciones de Home Assistant que dibujan todo lo que se mueve, y el tiempo
> que atraviesa, en un mapa compartido: aviones, barcos, trenes y ahora el
> tiempo. Instálalo solo o junto a los demás módulos
> ([lista más abajo](#parte-de-live-track-los-demás-módulos)).

> **En crecimiento, y abierto a ideas.** Hoy Live Track Weather cubre
> tormentas, terremotos, radar y previsiones en todo el mundo, y avisos para
> EE. UU., Noruega y Svalbard. Estamos añadiendo más países, servicios
> meteorológicos y peligros. ¿Falta el tuyo? [Sugiérelo](#ayúdanos-a-hacerlo-crecer),
> o añádelo tú mismo: te ayudaremos a hacerlo.

**Estado: 0.1.0, la primera versión.** Se añade al Marketplace por enlace
([ver más abajo](#instalación-paso-a-paso)); aún no está en el catálogo del Marketplace.

Obra original de StrausbergAutomationWorks. Sin relación con, ni respaldo de,
ninguna organización cuyos datos muestra: en EE. UU. el National Weather
Service, la NOAA, el National Hurricane Center, el Storm Prediction Center, el
Joint Typhoon Warning Center, la NASA, el US Geological Survey y la EPA; MET
Norway (Noruega); el KNMI (Países Bajos); o GeoNames.

> ⚠ **No es un sistema de alertas de emergencia.** Muestra datos públicos,
> con unos minutos de retraso en el mejor de los casos. Para los avisos que
> protegen vidas, usa las alertas de emergencia de tu teléfono, tu servicio
> meteorológico nacional, una radio meteorológica donde tu país la tenga y a
> tus autoridades locales, y sigue las órdenes de evacuación.

---

## Contenido

1. [Todo lo que hace](#todo-lo-que-hace)
2. [Dónde funciona](#dónde-funciona)
3. [Parte de Live Track: los demás módulos](#parte-de-live-track-los-demás-módulos)
4. [Antes de empezar](#antes-de-empezar)
5. [Instalación, paso a paso](#instalación-paso-a-paso)
6. [Configuración, paso a paso](#configuración-paso-a-paso)
7. [Claves gratuitas que activan más, paso a paso](#claves-gratuitas-que-activan-más-paso-a-paso)
8. [Poner el mapa en un panel](#poner-el-mapa-en-un-panel)
9. [Usarlo en automatizaciones](#usarlo-en-automatizaciones)
10. [Todo lo que hay en el mapa, en detalle](#todo-lo-que-hay-en-el-mapa-en-detalle)
11. [Todo en tus lugares, en detalle](#todo-en-tus-lugares-en-detalle)
12. [Todas las entidades que crea](#todas-las-entidades-que-crea)
13. [Qué envía y descarga](#qué-envía-y-descarga)
14. [Ayúdanos a hacerlo crecer](#ayúdanos-a-hacerlo-crecer)
15. [Idiomas](#idiomas)
16. [Créditos y licencias](#créditos-y-licencias)
17. [Palabras clave](#palabras-clave)

---

## Todo lo que hace

### En el mapa, sin configurar nada

| Qué | Dónde | Fuente |
|---|---|---|
| **Avisos meteorológicos**: avisos, vigilancias, advertencias y comunicados, rellenos en transparencia con los colores propios del Weather Service | todo EE. UU., sus costas y aguas | National Weather Service (EE. UU.) |
| **Avisos de tornado, tormenta severa, crecida repentina y otros avisos por tormenta**, dibujados con su propio polígono | EE. UU. | National Weather Service |
| **Huracanes, tormentas tropicales, tifones y ciclones**: un marcador por tormenta, el cono de previsión, la trayectoria prevista, el campo de viento y la trayectoria pasada | todo el mundo | National Hurricane Center (EE. UU.); Joint Typhoon Warning Center (EE. UU.) a través de NASA EONET |
| **La previsión de tiempo severo de hoy**: riesgo de tormentas severas de Marginal a High | EE. UU. | NOAA Storm Prediction Center |
| **Terremotos** de las últimas 24 horas: marcadores para los grandes y los sentidos, puntos para el resto, líneas de sacudida para los más fuertes | todo el mundo | US Geological Survey |
| **Volcanes en alerta**, con su código de color de aviación | volcanes de EE. UU. | USGS Volcano Hazards Program |
| **Ríos desbordados o con crecida prevista**, leve, moderada o grave | estaciones fluviales y mareógrafos de EE. UU. | NOAA National Water Prediction Service |
| **Informes de tormentas**: tornados, nubes embudo, granizo, viento dañino, inundaciones | EE. UU. | NWS Local Storm Reports |
| **Informes invernales**: espesores de nieve, ventiscas, aguanieve, lluvia helada y tormentas de hielo, frío extremo, aludes, atascos de hielo | EE. UU. | NWS Local Storm Reports |
| **Los avisos meteorológicos de MET Norway**, junto a los de EE. UU. | Noruega, sus mares, Svalbard | MET Norway |
| **Previsiones marítimas** para 56 zonas marítimas y 39 zonas costeras, haz clic para leer | del mar del Norte al Polo Norte | MET Norway |
| **Un punto de previsión en Longyearbyen**, Svalbard, haz clic para la previsión | Svalbard | MET Norway |
| **Radar meteorológico** y **rayos**: el radar más nítido para lo que hay en pantalla | el mundo | dibujados por la tarjeta de mapa de Live Track |

### En tus lugares, sin configurar nada

"Tus lugares" son tu casa, y cualquier persona, teléfono, rastreador de
dispositivo o zona que elijas vigilar. Cada lugar recibe (los nombres de las
entidades están en inglés):

* **Alert at …**: encendido mientras el lugar está dentro de un aviso
  meteorológico, cerca de un terremoto fuerte o en la zona de peligro de un
  volcán en erupción. Listo para automatizaciones: encender las luces, enviar
  una notificación al teléfono, cerrar el garaje.
* **Forecast at …**: una previsión meteorológica completa que sigue al lugar
  cuando se mueve, para cada tarjeta meteorológica de tu panel. Previsiones del
  National Weather Service en tierra de EE. UU.; las de MET Norway en todas las
  demás partes y en todas las aguas.
* **Wind at …**, **Wind gust at …**, **Wind direction at …** y
  **Temperature at …**: lo que midió la estación meteorológica más cercana.
  Recoge el toldo cuando haya rachas.
* **Elevation at …** y **Depth at …**: la altura del terreno, y la
  profundidad del agua bajo un barco.

### Activado con tu propia clave o cuenta gratuita

| Clave o cuenta gratuita | Lo que añade |
|---|---|
| Clave de mapa de **NASA FIRMS** | avisos de incendios forestales cerca de tus lugares; cada detección de incendio por satélite en el mapa |
| Clave API de **AirNow** (EE. UU.) | avisos de humo de incendios y calidad del aire (AQI PM2.5) en tus lugares de EE. UU.; cada monitor de calidad del aire en el mapa |
| Clave API de **KNMI** (Países Bajos) | radar más nítido sobre los Países Bajos |
| Usuario de **GeoNames** | viento y temperatura medidos fuera de EE. UU., del aeropuerto más cercano; el nombre del mar y agua o tierra para la profundidad |
| ID de cliente de **MET Norway Frost** | cada estación meteorológica de Svalbard y Jan Mayen en el mapa; viento y temperatura medidos en tus lugares de Noruega y Svalbard |

Cada una se consigue en pocos minutos: [paso a paso más abajo](#claves-gratuitas-que-activan-más-paso-a-paso).

---

## Dónde funciona

| Región | Qué obtienes | Fuente | Necesita |
|---|---|---|---|
| **Todo el mundo** | huracanes, tifones y ciclones; terremotos; radar meteorológico, rayos y nubes; una previsión en cada uno de tus lugares; altitud y profundidad del mar en tus lugares | National Hurricane Center, Joint Typhoon Warning Center y NASA (EE. UU.); US Geological Survey; las fuentes de radar de la tarjeta de mapa; MET Norway; Mapzen Terrain Tiles; NOAA NCEI | nada |
| **Todo el mundo** | detecciones de incendios por satélite en el mapa y avisos de incendios forestales en tus lugares | NASA FIRMS (EE. UU.) | una clave de mapa de FIRMS gratuita |
| **Todo el mundo**, fuera de EE. UU. | viento y temperatura medidos en tus lugares, del aeropuerto más cercano; el nombre del mar | GeoNames | un usuario de GeoNames gratuito |
| **América del Norte**: Canadá | radar más nítido; altitud en tus lugares | Environment and Climate Change Canada (GeoMet); Natural Resources Canada | nada |
| **América del Norte**: Canadá | estaciones de calidad del aire en el mapa | AirNow (EE. UU.) y socios | una clave de AirNow gratuita |
| **América del Norte**: Estados Unidos | avisos meteorológicos y avisos por tormenta; la previsión de tiempo severo; volcanes; ríos en crecida; informes de tormentas y de invierno; la previsión y el tiempo medido del Weather Service en tus lugares; altitud | National Weather Service, NOAA, US Geological Survey | nada |
| **América del Norte**: Estados Unidos | avisos de humo de incendios en tus lugares; estaciones de calidad del aire en el mapa | AirNow | una clave de AirNow gratuita |
| **Asia**: Japón | radar más nítido | Japan Meteorological Agency | nada |
| **Europa**: Alemania | radar más nítido | Deutscher Wetterdienst | nada |
| **Europa**: Finlandia | radar más nítido | Finnish Meteorological Institute | nada |
| **Europa**: Noruega, Svalbard y Jan Mayen | avisos meteorológicos; previsiones marítimas desde el mar del Norte hasta el Polo Norte; una previsión en Longyearbyen; altitud y profundidad del mar en Noruega | MET Norway; Kartverket | nada |
| **Europa**: Noruega, Svalbard y Jan Mayen | tiempo medido en tus lugares; cada estación meteorológica de Svalbard y Jan Mayen en el mapa | MET Norway Frost | un ID de cliente de Frost gratuito |
| **Europa**: Países Bajos | radar más nítido | KNMI | una clave de KNMI gratuita |

⚠ Por ahora los avisos meteorológicos solo llegan de EE. UU. y Noruega. En
el resto del mundo tienes las capas mundiales de arriba, una previsión y el
tiempo medido en tus lugares, y avisos de terremotos fuertes cercanos y (con
una clave) de incendios forestales.

¿No está en la lista? [Dínoslo](#ayúdanos-a-hacerlo-crecer). Donde un servicio
meteorológico publique sus avisos o datos de forma abierta, estudiaremos
añadirlo.

---

## Parte de Live Track: los demás módulos

Live Track es un conjunto de integraciones de Home Assistant, una por cada tipo
de cosa que se mueve, todas dibujadas en la misma tarjeta de mapa. Cada una
funciona por sí sola; juntas forman una imagen en directo. Comparten la tarjeta
de mapa y una biblioteca de Python
([saw-livetrack](https://github.com/StrausbergAutomationWorks/LiveTrackCore)),
así que instalar otra no añade peticiones a una fuente que otra ya lee.

| Módulo | Lo que pone en el mapa | Estado |
|---|---|---|
| [Live Track Aircraft](https://github.com/StrausbergAutomationWorks/LiveTrackAircraft) | aviones sobre ti por ADS-B, con rutas e iconos por tipo | publicado |
| [Live Track Ships](https://github.com/StrausbergAutomationWorks/LiveTrackShips) | barcos y embarcaciones por AIS, cerca de ti o en cualquier parte | publicado |
| [Live Track Commuter Rail](https://github.com/StrausbergAutomationWorks/LiveTrackCommuterRail) | trenes de cercanías en Norteamérica, Europa y Australia | publicado |
| [Live Track Intercity Rail](https://github.com/StrausbergAutomationWorks/LiveTrackIntercityRail) | trenes interurbanos y de larga distancia en Norteamérica, Europa y Australia | publicado |
| [Live Track SALT](https://github.com/StrausbergAutomationWorks/LiveTrackSALT) | aviones y barcos de inmigración y de las fuerzas federales del orden, según listas públicas | publicado |
| **Live Track Weather** | tiempo, tormentas y riesgos naturales (este módulo) | publicado |
| Live Track Stations | paneles de salidas y avisos de "hora de salir" para cada estación | previsto |
| Live Track Satellites | satélites que pasan sobre ti | previsto |
| Live Track Freight Trains | trenes de mercancías y de obras donde los ferrocarriles los publican | previsto |
| Live Track Transit | autobuses urbanos, tranvías, transbordadores y metro | previsto |
| Live Track Intercity Buses | autocares interurbanos y regionales | previsto |
| Live Track Commuter Buses | autobuses de cercanías | previsto |
| [LiveTrackMapCard](https://github.com/StrausbergAutomationWorks/LiveTrackMapCard) | la tarjeta de mapa compartida en la que dibuja cada módulo | publicada, instalada con cada módulo |

Todo es gratuito y de código abierto. No se reserva nada para patrocinadores.

---

## Antes de empezar

* **Home Assistant** 2026.11 o posterior.
* **El Marketplace** (HACS) en tu Home Assistant, para instalarlo y
  actualizarlo de forma sencilla. Sin él puedes copiar los archivos a mano.
* **Acceso a Internet** para Home Assistant: todo viene de servicios
  meteorológicos públicos.
* **Opcional: auto-entities** del Marketplace, para poner en el mapa los
  marcadores de tormentas, terremotos y estaciones (ver
  [Poner el mapa en un panel](#poner-el-mapa-en-un-panel)). Los avisos y las
  formas aparecen sin él.
* Nada que pagar y ninguna cuenta necesaria para lo básico. Las claves
  gratuitas de arriba son opcionales.

---

## Instalación, paso a paso

### Desde el Marketplace (recomendado)

Live Track Weather aún no está en el catálogo del Marketplace. Añádelo por su
enlace:

1. En Home Assistant, abre **Configuración → Marketplace** (HACS).
2. Elige **Añadir desde un enlace** (o el menú de tres puntos →
   **Repositorios personalizados**).
3. Escribe `StrausbergAutomationWorks/LiveTrackWeather`. Si te pregunta el
   tipo, elige **Integración**.
4. Busca **Live Track Weather** en la lista y elige **Descargar** o
   **Instalar**.
5. **Reinicia Home Assistant**: **Configuración → Sistema → Reparaciones** ofrece el
   reinicio, o usa **Configuración → Sistema → Reiniciar**.

### A mano

1. Descarga el código fuente de la
   [última versión](https://github.com/StrausbergAutomationWorks/LiveTrackWeather/releases/latest).
2. Copia su carpeta `custom_components/live_track_weather` en la carpeta
   `custom_components` de tu carpeta de configuración de Home Assistant (crea
   `custom_components` si no existe).
3. Reinicia Home Assistant.

---

## Configuración, paso a paso

1. Abre **Configuración → Dispositivos y servicios**.
2. Elige **Añadir integración** (abajo a la derecha) y busca
   **Live Track Weather**.
3. Elige **Enviar**. No hay que escribir nada: un solo Live Track Weather
   cubre todo el mundo.

Eso es todo. Los avisos, tormentas, terremotos, volcanes, inundaciones,
informes de tormentas y avisos de MET Norway empiezan a aparecer en pocos
minutos, y tu casa queda vigilada: **Alert at Home**, **Forecast at Home**,
**Wind at Home**, **Temperature at Home**, **Elevation at Home** y
**Depth at Home**.

### Cambiar lo que vigila: las opciones

Abre **Configuración → Dispositivos y servicios → Live Track Weather → Configurar**
(la rueda dentada). Cada opción, en palabras sencillas:

| Opción | Lo que hace | Por defecto |
|---|---|---|
| **Segundos entre consultas** | cada cuánto se descarga la lista de avisos de EE. UU., de 60 a 900 segundos | 180 |
| **Vigilar la casa** | tu casa recibe los sensores "… at Home" y la previsión; desactívalo para quitarlos | activado |
| **Vigilar también estas personas, rastreadores de dispositivos o zonas** | cada uno recibe su propio "Alert at …", "Forecast at …", viento, temperatura, altitud y profundidad, que lo siguen cuando se mueve. Elige el teléfono de un familiar, el rastreador de una autocaravana, la zona de una casa de vacaciones | ninguno |
| **Avisos que encienden un lugar** | cualquier aviso (incluidos avisos menores y comunicados), o solo los moderados, graves o extremos. Todos los avisos siguen listados en el sensor | cualquier aviso |
| **Viento y temperatura medidos solo en estaciones de aeropuerto** | desactivado: la estación más cercana de cualquier tipo (a menudo más cerca de un camping); activado: solo aeropuertos | desactivado |
| **MAP_KEY de NASA FIRMS** | avisos de incendios y detecciones de incendios (ver [claves gratuitas](#claves-gratuitas-que-activan-más-paso-a-paso)) | vacía |
| **Un incendio cuenta a menos de** | lo cerca que debe estar un incendio para encender un lugar, de 5 a 150 km (de 3 a 93 millas) | 50 km (31 millas) |
| **Clave API de AirNow** | avisos de humo y estaciones de calidad del aire | vacía |
| **El humo cuenta desde un AQI PM2.5 de** | el índice de calidad del aire que enciende un lugar | 90 |
| **Detecciones de incendios y estaciones de calidad del aire en el mapa** | qué regiones dibujar: los 48 estados contiguos y Hawái, Alaska, Canadá, todo el mundo (solo incendios) | ninguna |
| **Terremoto más pequeño en la capa de puntos del mapa** | deja fuera los pequeños puntos de terremoto por debajo de una magnitud; los marcadores se quedan | vacío: todos los terremotos |
| **Clave API de KNMI** | radar más nítido sobre los Países Bajos | vacía |
| **Usuario de GeoNames** | tiempo fuera de EE. UU., nombres de mares | vacío |
| **ID de cliente de MET Norway Frost** | estaciones de Svalbard y Jan Mayen; tiempo medido en Noruega | vacío |

Cada clave se comprueba una vez al introducirla, y se te avisa si no funciona.
Deja un campo vacío para desactivar esa parte.

---

## Claves gratuitas que activan más, paso a paso

Todas son gratuitas y personales: cada persona que instala Live Track Weather
consigue las suyas. Pega cada una en **Configuración → Dispositivos y servicios →
Live Track Weather → Configurar**.

### NASA FIRMS (incendios forestales)

1. Abre <https://firms.modaps.eosdis.nasa.gov/api/map_key/>.
2. Escribe tu dirección de correo y solicita una **MAP_KEY**. Llega por
   correo.
3. Pégala en **MAP_KEY de NASA FIRMS**, y ajusta **Un incendio cuenta a menos
   de** si 50 km (31 millas) no te van bien.
4. Para ver incendios en el mapa, marca también una región en
   **Detecciones de incendios y estaciones de calidad del aire en el mapa**.

### AirNow (humo y calidad del aire, EE. UU.)

1. Abre <https://docs.airnowapi.org/> y elige **Request an AirNow API
   Account**.
2. Confirma el correo, inicia sesión y copia tu **API key** desde la página de
   tu cuenta.
3. Pégala en **Clave API de AirNow**.

### KNMI (radar sobre los Países Bajos)

1. Regístrate en la KNMI Data Platform, <https://developer.dataplatform.knmi.nl/>.
2. Solicita una clave para la API **WMS**. (Una clave de la API Open Data no
   sirve aquí.)
3. Pégala en **Clave API de KNMI**. El mapa usa entonces el radar de KNMI sobre
   los Países Bajos; sin ella, el de RainViewer.

### GeoNames (tiempo fuera de EE. UU.)

1. Crea una cuenta gratuita en <https://www.geonames.org/login>.
2. Abre el correo de confirmación que envía GeoNames y confirma.
3. Inicia sesión, abre la página de tu cuenta y **activa los servicios web
   gratuitos**.
4. Escribe tu **nombre de usuario** (no tu contraseña) en
   **Usuario de GeoNames**.

### MET Norway Frost (estaciones de Svalbard, tiempo en Noruega)

1. Abre <https://frost.met.no/auth/requestCredentials.html>.
2. Escribe tu dirección de correo. Recibes un **ID de cliente** y un secreto de
   cliente.
3. Pega el **ID de cliente** en **ID de cliente de MET Norway Frost**. El
   secreto no hace falta.

---

## Poner el mapa en un panel

El mapa es [LiveTrackMapCard](https://github.com/StrausbergAutomationWorks/LiveTrackMapCard),
la tarjeta en la que dibuja cada módulo de Live Track. **Se instala con Live
Track Weather**: nada que descargar, nada que copiar en `www`, ningún recurso
que añadir.

1. Abre un panel, elige el lápiz (**Editar panel**) y luego **Añadir
   tarjeta**.
2. Desplázate hasta abajo y elige **Manual**.
3. Pega esto y elige **Guardar**:

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

Los avisos meteorológicos, la previsión de tiempo severo, las zonas de MET
Norway, los conos y trayectorias de las tormentas, las líneas de sacudida de
los terremotos y las capas de puntos aparecen solos. Los marcadores (tormentas,
terremotos, volcanes, estaciones fluviales, la previsión de Longyearbyen y las
estaciones de Svalbard) llegan por el filtro de arriba, que necesita
[auto-entities](https://github.com/thomasloven/lovelace-auto-entities) del
Marketplace. Con otros módulos de Live Track instalados, añade un filtro
`- domain: geo_location` más para cada una de sus fuentes
(`live_track_aircraft`, `live_track_ships`, etcétera).

**En el mapa:**

* El **control de capas** de arriba a la derecha tiene una casilla para cada
  capa: los avisos de EE. UU., la previsión de tiempo severo, los ciclones
  tropicales, los avisos y previsiones marítimas de MET Norway, los terremotos,
  la sacudida sísmica, los informes de tormentas, los informes invernales, las
  detecciones de incendios, las estaciones de calidad del aire, el radar
  meteorológico, el movimiento del radar, los rayos y las nubes. La elección de
  cada espectador se guarda en su propio navegador.
* **Haz clic** en un marcador, una zona, una línea o un punto para leer sobre
  él.
* La **tarjeta de filtro** (`custom:live-track-map-filter-card`) puede ocultar
  las estaciones de Svalbard, como **Observed weather (MET Norway)**.
* El crédito de cada fuente aparece en la línea de atribución del mapa
  mientras se muestran sus datos.

Si los recursos de tus paneles están definidos en YAML
(`lovelace: resource_mode: yaml`), no se puede registrar nada por ti: un
problema en **Reparaciones** te da entonces la línea exacta que añadir.
Cualquier otra tarjeta de mapa que muestre entidades `geo_location` muestra
los marcadores, pero no los avisos, las zonas ni los puntos.

---

## Usarlo en automatizaciones

Todo es una entidad normal de Home Assistant, así que el editor de
automatizaciones funciona con ello, sin código.

**Una notificación al teléfono cuando la casa está dentro de un aviso:**

1. **Configuración → Automatizaciones y escenas → Crear automatización → Crear
   nueva automatización**.
2. **Cuando**: *Entidad → Estado*, entidad **Alert at Home**, a **Inseguro**
   (encendido).
3. **Entonces hacer**: *Notificaciones → Enviar una notificación a través de
   mobile_app_…*, con un mensaje como `Aviso meteorológico en casa: {{ state_attr('binary_sensor.live_track_weather_alert_at_home', 'highest') }}`.
4. Guarda.

**Recoger el toldo con una racha:** *Cuando* **Wind gust at Home** supere
50 km/h (o 30 mph), *entonces* cierra la cubierta del toldo.

**Otras ideas:** hacer parpadear una luz cuando **Severe weather outlook**
llegue a 3 (Enhanced); avisar al dueño de la autocaravana cuando **Alert at
Camper** se encienda por un incendio a menos de 50 km; notificar cuando
**Temperature at Cabin** baje de cero; mostrar **Forecast at Boat** en una
tarjeta meteorológica mientras está en el mar; avisar a la familia cuando
**Alert at Cabin**, en Noruega, se encienda por un aviso de MET Norway.

---

## Todo lo que hay en el mapa, en detalle

### Avisos meteorológicos de EE. UU.

Cada aviso activo del National Weather Service: avisos, vigilancias,
advertencias y comunicados para condados, zonas terrestres, marítimas, de alta
mar y de meteorología de incendios, rellenos en transparencia con el color que
el Weather Service da a cada fenómeno (el de mayor prioridad donde se solapan
avisos). Los avisos por tormenta, como los de tornado, tormenta severa y crecida
repentina, se dibujan con su propio polígono, no el condado entero. No se fija
ninguna ubicación: el mapa muestra lo que hay en pantalla. Los contornos de las
zonas (11.651, simplificados a unos 500 m, unos 3,6 MB) vienen con cada versión
y cada navegador los descarga una vez por versión.

**Sensor `US alerts`**: el número de avisos activos; sus atributos llevan la
lista que dibuja el mapa (`zones`, `polygons`, `styles`, `updated`,
`shapes_url`), que cambia en casi cada consulta y no se guarda en el
historial.

### Ciclones tropicales: huracanes, tifones, ciclones

Cada ciclón tropical activo del mundo, un marcador por tormenta rotulado con
su nombre y coloreado por categoría: depresión azul, tormenta tropical verde
azulado, categorías 1 a 5 dorado, naranja, naranja oscuro, rojo y magenta,
postropical gris. Pasa el ratón por encima para ver su clase, viento, presión y
movimiento.

* Tormentas del **National Hurricane Center** (Atlántico, Pacífico oriental y
  central): el cono de previsión (azul), la trayectoria prevista (rojo), los
  vientos actuales de 34, 50 y 64 nudos (63, 93 y 119 km/h; 39, 58 y 74 mph)
  (amarillo, naranja, rojo) y la
  trayectoria pasada (negro).
* **Todas las demás cuencas**, del Joint Typhoon Warning Center a través de
  EONET de la NASA: el marcador y la trayectoria pasada. No se muestra una
  tormenta cuya última posición tenga más de 24 horas.

Los marcadores son `geo_location.storm_<id>` (`geo_location.storm_ep222026`),
con los atributos `storm_class`, `storm_category` (TD, TS, H1-H5, PT),
`max_wind_kmh`, `pressure_hpa`, `course_deg`, `speed_kmh`, `last_seen`,
`advisory_number` y `storm_source`. Van y vienen con las tormentas y no tienen
ID único, así que no se pueden renombrar en la interfaz. **Sensor `Tropical
cyclones`**: el número de tormentas.

### Previsión de tiempo severo

La previsión categórica del día 1 del Storm Prediction Center: dónde pueden
darse tormentas severas hoy, de 1 Marginal, 2 Slight, 3 Enhanced, 4 Moderate a
5 High, con los colores propios del Center, bajo los avisos. **Sensor `Severe
weather outlook`**: el riesgo más alto en cualquier parte de EE. UU. hoy, de 0
a 5, registrado para que pueda activar una automatización; atributos `risk`,
`issued`, `valid_from`, `valid_to`. No se dibuja la zona de tormentas
ordinarias.

### Terremotos

Cada terremoto que el US Geological Survey lista en las últimas 24 horas, en
todo el mundo (unos 240 al día):

* **Marcadores** desde magnitud 4,5, y para cualquier terremoto que la gente
  haya notado, rotulados con la magnitud (`geo_location.quake_<USGS id>`). Haz
  clic para ver la hora, la profundidad, los informes de quienes lo sintieron,
  la sacudida más fuerte, el nivel de alerta PAGER y la página del evento del
  USGS. La "bandera de tsunami" no es un aviso; los avisos de tsunami vienen de
  la NOAA (tsunami.gov).
* **Puntos** para todos los demás terremotos (y voladuras de cantera y
  explosiones en gris), en su propia capa: **sensor `Earthquakes`**. La opción
  **Terremoto más pequeño en la capa de puntos del mapa** deja fuera los
  pequeños.
* **Líneas de sacudida** (USGS ShakeMap) para los mayores terremotos del día,
  magnitud 6 o más o sacudida fuerte, como mucho cinco:
  **sensor `Earthquake shaking`**.

### Volcanes en alerta

Cada volcán de EE. UU. en nivel de alerta Advisory o código de color de
aviación Yellow o superior, un marcador con su código de color rotulado con su
nombre (`geo_location.volcano_<number>`). Haz clic para ver el nivel de alerta,
el código de color, desde cuándo, el resumen del observatorio y enlaces al
aviso y a la página del volcán.

### Ríos desbordados ahora o con crecida prevista

Cada estación fluvial o mareógrafo de EE. UU. con **inundación leve o peor
ahora**, o con previsión de alcanzarla, rotulado Minor, Moderate o Major con
los colores de inundación del Weather Service (`geo_location.river_<gauge id>`).
**Un anillo oscuro significa que se está desbordando ahora**; sin el anillo es
una previsión. Haz clic para ver el nivel actual, el nivel previsto, los
umbrales de inundación, el caudal y la página de la estación. ⚠ Algunas
estaciones tienen umbrales de inundación que parecen provisionales y por eso
muestran Major (Devils Lake, Dakota del Norte).

### Informes de tormentas

Cada NWS Local Storm Report de las últimas 24 horas sobre un tornado o una
tromba marina, una nube embudo, granizo, viento de tormenta o daños, una
crecida repentina o una inundación: rojo para tornados, azul para viento, verde
para granizo, verde azulado para inundaciones. Un informe significativo
es más grande y tiene un anillo oscuro: cualquier tornado, granizo de 5 cm
(2 pulgadas) o más, o viento de 120 km/h (65 nudos) o más. Los informes se desvanecen con el tiempo:
menos de una hora, de 1 a 6 horas, de 6 a 24 horas. Haz clic para ver el tipo,
el tamaño o la velocidad, el lugar, la hora, la oficina del NWS y las
observaciones. **Sensor `Storm reports`**: el número de puntos. ⚠ Son
informes tal como los envía la gente, antes de que el Weather Service los
revise, y pueden tardar 30 minutos en aparecer.

### Informes invernales

De los mismos informes, en su propia capa bajo los informes de tormentas:
nieve, nevadas intensas y chubascos de nieve (azul pizarra), ventiscas (rojo
anaranjado), aguanieve (orquídea), lluvia helada, llovizna helada y tormentas
de hielo (magenta oscuro), daños por nieve y hielo (gris), frío extremo y
sensación térmica (azul), aludes (marrón) y atascos de hielo (verde azulado
oscuro), cada uno con un fino anillo oscuro. Los significativos son más
grandes: 30 cm de nieve (12 pulgadas), 1,3 cm de aguanieve (media pulgada),
6 mm de hielo (un cuarto de pulgada) o cualquier tormenta de hielo. Haz clic para ver la cantidad en pulgadas y
cm o mm, o la temperatura en °F y °C. **Sensor `Winter reports`**. ⚠ Una gran
tormenta trae miles de informes; donde dos se solaparían se dibuja uno, así que
acércate.

### MET Norway: avisos, previsiones marítimas, la previsión de Longyearbyen

* **Avisos** para la tierra, la costa y los mares de Noruega y los mares hasta
  el Polo Norte, en el amarillo, naranja o rojo de MET, junto a los avisos de
  EE. UU. Haz clic en uno para ver lo que se espera, las consecuencias, los
  consejos y cuándo (en inglés). **Sensor `MET Norway warnings`**.
* **Previsiones marítimas** para 56 zonas marítimas y 39 zonas costeras,
  incluidas las de Svalbard, bajo los avisos. Haz clic en una para ver su
  previsión y cualquier aviso de viento, hielo o baja polar. **Sensor `MET
  Norway marine forecasts`**.
* **Un punto de previsión en Longyearbyen**, rotulado con la temperatura; haz
  clic para ver la previsión cada seis horas durante un día
  (`geo_location.met_forecast_longyearbyen`).

### Tiempo medido en Svalbard y Jan Mayen (ID de cliente de Frost)

Un punto verde azulado por cada estación meteorológica de Svalbard, la isla de
los Osos, Hopen y Jan Mayen cuya temperatura y viento tengan ambos menos de dos
horas (unas 30), rotulado con la temperatura (`geo_location.frost_sn99840` para
Svalbard Lufthavn, etcétera). Haz clic en uno para ver la temperatura, el viento
y su dirección, la racha más fuerte de la última hora, la humedad, la presión,
el espesor de nieve y la hora. Las estaciones que solo dan temperatura no se
dibujan; de dos estaciones a menos de 1 km se dibuja una. No se usan los
valores que Frost marca como muy inciertos o erróneos; los valores que hasta
ahora solo se han comprobado automáticamente (suele ser el caso de la hora más
reciente de MET) se muestran, y la ventana dice "Automatic check only".

### Incendios forestales y calidad del aire (claves de FIRMS y AirNow)

Elige regiones en **Detecciones de incendios y estaciones de calidad del aire
en el mapa**:

* **Detecciones de incendios** (necesita la clave de FIRMS): cada detección
  de incendio por satélite de las últimas 24 horas (NOAA-20 y NOAA-21 VIIRS)
  como pequeños puntos rojos. Se dejan fuera fábricas, refinerías, antorchas de
  gas y otras fuentes de calor fijas que la NASA ha clasificado. Haz clic para
  ver cuándo, qué satélite, su potencia radiativa del fuego y la confianza de
  la NASA. **Sensor `Fire detections`**.
* **Estaciones de calidad del aire** (necesita la clave de AirNow; EE. UU. y
  Canadá): cada monitor de partículas finas (PM2.5), coloreado según su AQI con
  los colores de la EPA, cada hora. **Sensor `Air quality sites`**.

### Radar meteorológico, rayos y nubes

Dibujados por la propia tarjeta de mapa, sin configurar nada: una capa de radar
que elige la fuente más nítida para lo que hay en pantalla (RainViewer, NOAA
nowCOAST y GeoMet de Canadá en Norteamérica; el FMI de Finlandia y el DWD de
Alemania en Europa; la JMA de Japón; el KNMI sobre los Países Bajos con tu
clave), el movimiento del radar, los rayos de nowCOAST y las nubes de los
satélites GOES y EUMETSAT.

---

## Todo en tus lugares, en detalle

### Alert at …

**`Alert at Home`** (`binary_sensor.live_track_weather_alert_at_home`, clase
de dispositivo *safety*: encendido significa inseguro), y uno por cada
persona, rastreador o zona que vigiles. Se enciende cuando el lugar está:

* dentro de un **aviso meteorológico de EE. UU.** o un **aviso de MET Norway**
  (según la propia regla del Weather Service: un aviso de tornado o de
  inundación cuenta dentro de su polígono, no en todo el condado; las zonas
  vienen del propio Weather Service, así que un lugar en la costa o en el
  límite de un condado obtiene la respuesta correcta);
* cerca de un **terremoto** fuerte en las últimas 24 horas: magnitud 4 a menos
  de 50 km (31 millas), 5 a menos de 150 km (93 millas), 6 a menos de 300 km
  (186 millas), 7 a menos de 600 km (373 millas);
* dentro de la zona de peligro de un **volcán** en Watch u Orange o superior
  (la National Volcanic Threat Layer del USGS, incluida con la integración);
* con la clave de FIRMS, cerca de un **incendio forestal** (dentro de la
  distancia que fijes, 50 km (31 millas) por defecto; las detecciones llegan a Home
  Assistant de 2 a 4 horas después del paso del satélite);
* con la clave de AirNow, en **humo de incendio**: el monitor PM2.5 más cercano
  en 80 km (50 millas) en el AQI que fijes o por encima, 90 por defecto (lugares de
  EE. UU.).

Atributos: `alerts` (cada aviso en el lugar, el peor primero, con `event`,
`severity`, `headline`, `onset`, `ends`, `source` y un enlace), `highest`,
`zones`; con las claves, `fires_near`, `nearest_fire_km`, `pm25_aqi`,
`pm25_site` y más. Las zonas de un rastreador en movimiento se vuelven a
consultar cuando se mueve más de 1 km. La NASA desaconseja usar solo las
detecciones de incendios para decidir sobre el terreno: sigue las órdenes de
evacuación.

### Forecast at …

**`Forecast at Home`** (`weather.live_track_weather_forecast_at_home`), y una
por cada lugar vigilado, para cada tarjeta meteorológica y
`weather.get_forecasts`: diaria, de día y de noche, y por horas.

* **En tierra de EE. UU.**: la previsión del National Weather Service para la
  cuadrícula de 2,5 km del lugar, siete días de día y de noche con el texto de
  la previsión, y por horas durante seis días y medio.
* **En todas las demás partes, y en todas las aguas**: la previsión de MET
  Norway, por horas durante unos dos días y medio, y luego cada seis horas
  hasta unos diez días.

Cambia de fuente cuando el lugar se mueve (un barco que sale del puerto, una
autocaravana que entra en Canadá).

### Wind at …, Wind gust at …, Wind direction at …, Temperature at …

Lo que midió la estación meteorológica más cercana, para cada lugar vigilado
(`sensor.live_track_weather_wind_at_home`, etcétera).

* **En EE. UU.**: la estación del National Weather Service más cercana de
  cualquier red (aeropuertos, estaciones de meteorología de incendios y de
  carreteras, estaciones de voluntarios), o solo aeropuertos con la opción; la
  siguiente, hasta tres, cuando una no tiene nada reciente.
* **En Noruega y Svalbard**, con un ID de cliente de Frost: la más cercana de
  las estaciones propias de MET Norway (medido en 22 lugares de Noruega: de 0,4
  a 11 km). La racha es la más fuerte de la última hora.
* **En otras partes**, con un usuario de GeoNames: el informe meteorológico
  (METAR) del aeropuerto más cercano, en un radio de unos 100 km (60 millas).
* Un sensor está **no disponible** cuando ningún informe de menos de dos horas
  tiene su valor. Una racha es desconocida cuando no se ha informado ninguna.
  Atributos: `station`, `station_name`, `provider`, `distance_km`, `observed`,
  `age_min`.

### Elevation at … y Depth at …

**`Elevation at Home`** y **`Depth at Home`**, y uno de cada por lugar
vigilado, comprobados al arrancar y tras un desplazamiento de más de 500 m.

* **Altitud** de la primera fuente con un valor: USGS 3DEP (EE. UU. y regiones
  fronterizas, al metro), Natural Resources Canada, Kartverket (Noruega
  continental), y después los Terrain Tiles de Mapzen para el resto del mundo.
* **Sobre el agua** la altitud es la superficie y **Depth** es la profundidad
  bajo el lugar, de Kartverket en Noruega o de NOAA NCEI en otras partes
  (incluidos los Grandes Lagos); desconocida en tierra. Con un usuario de
  GeoNames, `sea` da el nombre del mar.
* ⚠ Límites conocidos: la altitud en Svalbard es unos 35 m demasiado alta (no
  se ha encontrado una fuente mejor); los ríos, puertos y embalses no tienen
  profundidad; en mares poco profundos sin GeoNames la altitud es el fondo del
  mar; un lago bajo el nivel del mar al que solo llegan los terrain tiles
  muestra 0.

---

## Todas las entidades que crea

| Entidad | Qué es |
|---|---|
| `sensor.live_track_weather_us_alerts` | número de avisos activos de EE. UU.; la lista que dibuja el mapa |
| `sensor.live_track_weather_tropical_cyclones` | número de ciclones tropicales |
| `sensor.live_track_weather_severe_weather_outlook` | riesgo más alto de tormentas severas hoy, de 0 a 5 |
| `sensor.live_track_weather_met_norway_warnings` | avisos de MET Norway dibujados |
| `sensor.live_track_weather_met_norway_marine_forecasts` | zonas de previsión marítima de MET Norway |
| `sensor.live_track_weather_earthquakes` | puntos de terremoto en el mapa |
| `sensor.live_track_weather_earthquake_shaking` | ShakeMaps dibujados |
| `sensor.live_track_weather_storm_reports` | informes de tormentas dibujados |
| `sensor.live_track_weather_winter_reports` | informes invernales dibujados |
| `sensor.live_track_weather_fire_detections` | detecciones de incendios (clave de FIRMS y una región) |
| `sensor.live_track_weather_air_quality_sites` | estaciones de calidad del aire (clave de AirNow y una región) |
| `sensor.live_track_weather_knmi_radar` | imagen de radar de KNMI más reciente (clave de KNMI) |
| `geo_location.storm_…`, `quake_…`, `volcano_…`, `river_…`, `met_forecast_…`, `frost_…` | los marcadores; van y vienen y no tienen ID único |
| `binary_sensor.live_track_weather_alert_at_home` | Alert at Home (y uno por lugar vigilado) |
| `weather.live_track_weather_forecast_at_home` | Forecast at Home (y una por lugar vigilado) |
| `sensor.live_track_weather_wind_at_home`, `…_wind_gust_at_home`, `…_wind_direction_at_home`, `…_temperature_at_home` | tiempo medido en casa (y por lugar) |
| `sensor.live_track_weather_elevation_at_home`, `…_depth_at_home` | altitud y profundidad en casa (y por lugar) |

Los atributos que cambian en cada consulta (listas, formas, ventanas) se
mantienen fuera del historial de Home Assistant, para que tu base de datos no
crezca con ellos.

---

## Qué envía y descarga

**Sobre tu ubicación.** La ubicación de tu casa y de cada lugar vigilado se
envía, redondeada a unos 11 m, solo donde un servicio la necesita: al National
Weather Service para conocer las zonas, la cuadrícula de previsión y las
estaciones del lugar; fuera de la zona de previsión de EE. UU., a MET Norway
para su previsión; al USGS (y, donde el USGS no tiene nada, a Natural Resources
Canada, Kartverket y NOAA NCEI) para la altitud y la profundidad, al arrancar y
tras un desplazamiento de más de 500 m; con tus claves, a NASA FIRMS (un
recuadro alrededor del lugar), AirNow, GeoNames y Frost de MET Norway.
Desactiva **Vigilar la casa** y no vigiles nada más, y no se envía ninguna
ubicación. No se envía nada más sobre ti a ninguna parte.

**Cuánto.** La lista de avisos de EE. UU., unos 100 KB cada 3 minutos
(ajustable); las demás solo piden un archivo si ha cambiado, donde el servicio
lo permite: boletines de huracanes cada 5 minutos, EONET cada 30, la previsión
de tiempo severo cada 5, los avisos de MET Norway cada 5, las previsiones
marítimas cada 15-30 y las previsiones puntuales cada 30 (cada una un minuto
más tarde al azar, como pide MET, y nada durante 30 minutos tras un rechazo);
los terremotos del USGS cada 5 minutos (unos 170 KB), los volcanes cada 10, los
ríos cada 30, los informes de tormentas cada 10; Frost cada 10 minutos (unos
80 KB); GeoNames dentro de la mitad de sus 10.000 créditos gratuitos diarios;
KNMI como mucho unas 24 peticiones por hora, y solo mientras un mapa lo
muestra. Tras un error, cada servicio se deja tranquilo un rato antes de
volver a consultarlo.

---

## Ayúdanos a hacerlo crecer

Live Track Weather sigue creciendo. Añadimos países, servicios meteorológicos
y peligros a medida que los encontramos, y queremos saber qué te gustaría
después.

### Sugiere algo

¿Falta tu servicio meteorológico? ¿Hay algo mal o difícil de entender?
Dínoslo como te resulte más fácil:

* [**Rellena un formulario corto**](https://github.com/StrausbergAutomationWorks/LiveTrackWeather/issues/new?template=es.yml)
  en español. Necesitas una cuenta gratuita de GitHub.
* **Escribe un correo** a
  [StrausbergAutomationWorks@recordwise.org](mailto:StrausbergAutomationWorks@recordwise.org).
  No hace falta cuenta.

En cualquier caso, nos ayuda que nos digas:

* qué te gustaría ver, y en qué lugar del mundo;
* un enlace a donde se publican los datos, si conoces alguno (una página de
  datos abiertos, un feed público, la web de un servicio meteorológico): no es
  necesario, pero ayuda;
* el idioma de tu Home Assistant, si el problema es la redacción o una
  traducción.

Escribe en inglés o en tu propio idioma, lo que te resulte más fácil.

### Añádelo tú mismo, con nuestra ayuda

Si quieres añadir algo tú mismo, te ayudaremos a hacerlo, desde la primera
pregunta hasta la versión terminada. No necesitas ser desarrollador para
empezar:

* **Una traducción.** Los textos del diálogo de configuración son una lista
  corta de frases en un solo archivo de texto. Te mostraremos qué archivo y
  qué líneas.
* **Un país o un servicio meteorológico nuevo.** Dinos dónde se publican los
  datos. Podemos escribir el código juntos o revisar el tuyo.
* **Probarlo donde vives.** Instálalo, mira tu parte del mapa y dinos qué
  está bien y qué no.
* **Una corrección de este README.** Si un paso no coincidía con lo que
  viste, dinos qué viste.

[**Cuéntanos qué tienes en mente**](https://github.com/StrausbergAutomationWorks/LiveTrackWeather/issues/new?template=es.yml)
o escribe a
[StrausbergAutomationWorks@recordwise.org](mailto:StrausbergAutomationWorks@recordwise.org),
y te responderemos con los siguientes pasos.

---

## Idiomas

Este README: [English](README.md), [Deutsch](README.de.md),
[Français](README.fr.md), [Nederlands](README.nl.md),
[简体中文](README.zh-Hans.md), **Español**, [Italiano](README.it.md),
[Dansk](README.da.md) y [Kalaallisut](README.kl.md) (un borrador breve; hasta
que lo lea un hablante nativo, la página danesa es la fiable). Cada README
traducido está completo.

El diálogo de configuración y las opciones aparecen en el idioma de tu Home
Assistant cuando es uno de estos: English, Dansk, Deutsch, Español,
Français, Gaeilge, Íslenska, Italiano, Nederlands, Norsk Bokmål, Polski,
Português, Português (BR), Suomi, Svenska y 简体中文. Cualquier otro idioma
muestra inglés. Los nombres de las entidades (**Alert at Home**, etcétera) y
las etiquetas de la tarjeta de mapa están en inglés en todos los idiomas.

¿Has encontrado un error en una traducción, o necesitas otro idioma? Dínoslo
en <https://github.com/StrausbergAutomationWorks/LiveTrackWeather/issues>, o
[tradúcelo con nuestra ayuda](#añádelo-tú-mismo-con-nuestra-ayuda).

---

## Créditos y licencias

* El National Weather Service, el National Hurricane Center, el Storm
  Prediction Center, el National Water Prediction Service, el Joint Typhoon
  Warning Center, la NASA y el US Geological Survey son agencias del Gobierno
  de EE. UU.; sus datos son obras del Gobierno de EE. UU. Los datos de AirNow
  son preliminares y no verificados (US EPA y socios).
* **MET Norway**: datos bajo la Norwegian Licence for Open Government Data
  (NLOD) 2.0 y Creative Commons Attribution 4.0; las observaciones de Frost
  bajo Creative Commons Attribution 3.0 Norway. Esta integración redondea las
  zonas, cambia el color de los avisos y convierte unidades.
* **KNMI**: radar bajo Creative Commons Attribution 4.0, recortado y
  redimensionado en teselas de mapa.
* **GeoNames**: informes METAR y nombres de mares bajo Creative Commons
  Attribution 4.0.
* **Altitud**: el CDEM de Natural Resources Canada, Open Government Licence -
  Canada; Kartverket, Creative Commons Attribution 4.0; NOAA NCEI, Gobierno de
  EE. UU. **Terrain Tiles**: Mapzen, y las fuentes citadas en la atribución
  Joerd de Mapzen (`tilezen/joerd`, `docs/attribution.md`), reproducidas aquí
  literalmente: ArcticDEM terrain data DEM(s) were created from DigitalGlobe,
  Inc., imagery and funded under National Science Foundation awards 1043681,
  1559691, and 1542736; Australia terrain data © Commonwealth of Australia
  (Geoscience Australia) 2017; Austria terrain data © offene Daten Österreichs
  – Digitales Geländemodell (DGM) Österreich; Canada terrain data contains
  information licensed under the Open Government Licence – Canada; Europe
  terrain data produced using Copernicus data and information funded by the
  European Union - EU-DEM layers; Global ETOPO1 terrain data U.S. National
  Oceanic and Atmospheric Administration; Mexico terrain data source: INEGI,
  Continental relief, 2016; New Zealand terrain data Copyright 2011 Crown
  copyright (c) Land Information New Zealand and the New Zealand Government
  (All rights reserved); Norway terrain data © Kartverket; United Kingdom
  terrain data © Environment Agency copyright and/or database right 2015. All
  rights reserved; United States 3DEP (formerly NED) and global GMTED2010 and
  SRTM terrain data courtesy of the U.S. Geological Survey.
* **Zonas de peligro volcánico**: USGS National Volcanic Threat Layer (2024,
  CC0).

Ninguna de estas organizaciones ha creado ni respaldado esta integración.

**Código**: MIT, en [LICENSE](LICENSE).

**Para desarrolladores:** `tools/build_shapes.py` reconstruye el archivo de
zonas de aviso a partir de los shapefiles del NWS
(<https://www.weather.gov/gis/>) y `tools/build_colours.py` la tabla de colores
a partir de la página del mapa de peligros del NWS; las pruebas se ejecutan con
`python -m unittest discover -s tests`.

---

## Palabras clave

Home Assistant tiempo · Home Assistant avisos meteorológicos · avisos NWS ·
National Weather Service · mapa de avisos meteorológicos · aviso de tornado ·
aviso de tormenta severa · crecida repentina · tormenta invernal · seguimiento
de huracanes · tormenta tropical · tifón · ciclón · cono del huracán · NHC ·
JTWC · SPC outlook · previsión de tiempo severo · mapa de terremotos · alerta
de terremoto · terremotos USGS · ShakeMap · alerta volcánica · mapa de
inundaciones · estación fluvial · NWPS · informes de tormentas · granizo ·
espesor de nieve · ventisca · tormenta de hielo · mapa de incendios forestales
· alerta de incendio · detección de incendios · NASA FIRMS · VIIRS · alerta de
humo · calidad del aire · AQI · PM2.5 · AirNow · radar meteorológico · radar de
lluvia · mapa de rayos · MET Norway · yr · tiempo en Svalbard · Longyearbyen ·
Jan Mayen · Frost API · previsión marítima · radar KNMI · GeoNames · METAR ·
estación meteorológica · sensor de rachas · sensor de temperatura · previsión
para un rastreador · tiempo para autocaravanas · tiempo para barcos · sensor
de altitud · profundidad del agua · geo_location · binary_sensor · weather
entity · tarjeta de mapa · Lovelace · HACS · Marketplace · Live Track ·
LiveTrack · weather warning · vejrvarsel · Unwetterwarnung · weerwaarschuwing ·
alerte météo · allerta meteo · farevarsel · 天气预警 ·
StrausbergAutomationWorks

---

**Reconocimiento.** StrausbergAutomationWorks reconoce a los pueblos indígenas
de todas las tierras y aguas de este mapa, en todo el mundo, y presenta sus
respetos a sus Mayores del pasado y del presente.
