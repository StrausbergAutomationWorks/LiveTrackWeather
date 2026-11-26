# Live Track Weather

[English](README.md) · [Deutsch](README.de.md) · **Français** · [Nederlands](README.nl.md) · [简体中文](README.zh-Hans.md) · [Español](README.es.md) · [Italiano](README.it.md) · [Dansk](README.da.md) · [Kalaallisut](README.kl.md) · [Toutes les langues](#langues)

**Alertes météo, tempêtes, séismes, crues, feux de forêt, radar et météo en
direct pour Home Assistant, sur une seule carte.** Live Track Weather affiche
sur votre carte Home Assistant les alertes météo officielles, les ouragans et
typhons, les séismes, les volcans, les crues des rivières, les rapports d'orage
et de neige, les données sur les feux de forêt et la fumée, les prévisions
marines et les stations météo, et surveille les dangers autour de votre
domicile, des téléphones de votre famille et de votre camping-car. Les
tempêtes, les séismes, le radar et les prévisions couvrent le monde entier ;
les États-Unis, la Norvège et le Svalbard sont couverts avec le plus de détail
([où il fonctionne](#où-il-fonctionne)).

> **Live Track Weather est un module de Live Track**, une famille
> d'intégrations Home Assistant qui dessinent tout ce qui bouge, et la météo
> que cela traverse, sur une carte partagée : avions, navires, trains, et
> maintenant la météo. Installez-le seul ou à côté des autres modules
> ([liste ci-dessous](#les-autres-modules-de-live-track)).

> **En croissance, et ouvert aux idées.** Aujourd'hui, Live Track Weather
> couvre les tempêtes, les séismes, le radar et les prévisions dans le monde
> entier, et les alertes pour les États-Unis, la Norvège et le Svalbard. Nous
> ajoutons d'autres pays, services météo et dangers. Le vôtre manque ?
> [Proposez-le](#aidez-le-à-grandir), ou ajoutez-le vous-même : nous vous
> aiderons à le faire.

**État : 0.1.3, publié.** Dans le catalogue du Marketplace ([l'installer
ci-dessous](#installation-pas-à-pas)).

Œuvre originale de StrausbergAutomationWorks. Sans lien avec, ni approbation
de, aucune des organisations dont il affiche les données : aux États-Unis, le
National Weather Service, la NOAA, le National Hurricane Center, le Storm
Prediction Center, le Joint Typhoon Warning Center, la NASA, l'US Geological
Survey et l'EPA ; MET Norway (Norvège) ; le KNMI (Pays-Bas) ; ou GeoNames.

> ⚠ **Ce n'est pas un système d'alerte d'urgence.** Il affiche des données
> publiques, avec au mieux quelques minutes de retard. Pour les alertes qui
> protègent des vies, utilisez les alertes d'urgence de votre téléphone, votre
> service météorologique national, une radio météo là où votre pays en a une,
> et vos autorités locales, et suivez les ordres d'évacuation.

---

## Sommaire

1. [Tout ce qu'il fait](#tout-ce-quil-fait)
2. [Où il fonctionne](#où-il-fonctionne)
3. [Les autres modules de Live Track](#les-autres-modules-de-live-track)
4. [Avant de commencer](#avant-de-commencer)
5. [Installation, pas à pas](#installation-pas-à-pas)
6. [Configuration, pas à pas](#configuration-pas-à-pas)
7. [Clés gratuites qui activent davantage, pas à pas](#clés-gratuites-qui-activent-davantage-pas-à-pas)
8. [Mettre la carte sur un tableau de bord](#mettre-la-carte-sur-un-tableau-de-bord)
9. [L'utiliser dans des automatisations](#lutiliser-dans-des-automatisations)
10. [Tout ce qui est sur la carte, en détail](#tout-ce-qui-est-sur-la-carte-en-détail)
11. [Tout ce qui concerne vos lieux, en détail](#tout-ce-qui-concerne-vos-lieux-en-détail)
12. [Toutes les entités qu'il crée](#toutes-les-entités-quil-crée)
13. [Ce qu'il envoie et télécharge](#ce-quil-envoie-et-télécharge)
14. [Aidez-le à grandir](#aidez-le-à-grandir)
15. [Langues](#langues)
16. [Crédits et licences](#crédits-et-licences)
17. [Mots-clés](#mots-clés)

---

## Tout ce qu'il fait

### Sur la carte, sans rien configurer

| Quoi | Où | Source |
|---|---|---|
| **Alertes météo** : avertissements, veilles, avis et communiqués, remplis en transparence dans les couleurs propres du Weather Service | tous les États-Unis, leurs côtes et leurs eaux | National Weather Service (États-Unis) |
| **Avertissements de tornade, d'orage violent, de crue soudaine et autres avertissements d'orage**, dessinés selon leur propre polygone | États-Unis | National Weather Service |
| **Ouragans, tempêtes tropicales, typhons et cyclones** : un marqueur par tempête, le cône de prévision, la trajectoire prévue, le champ de vent et la trajectoire passée | le monde entier | National Hurricane Center (États-Unis) ; Joint Typhoon Warning Center (États-Unis) via NASA EONET |
| **La prévision d'orages violents du jour** : risque d'orages violents de Marginal à High | États-Unis | NOAA Storm Prediction Center |
| **Séismes** des dernières 24 heures : des marqueurs pour les forts et les ressentis, des points pour les autres, des lignes de secousse pour les plus forts | le monde entier | US Geological Survey |
| **Volcans en alerte**, dans leur code couleur aviation | volcans des États-Unis | USGS Volcano Hazards Program |
| **Rivières en crue ou dont la crue est prévue**, mineure, modérée ou majeure | stations hydrométriques et marégraphes des États-Unis | NOAA National Water Prediction Service |
| **Rapports d'orage** : tornades, nuages en entonnoir, grêle, vents destructeurs, inondations | États-Unis | NWS Local Storm Reports |
| **Rapports hivernaux** : hauteurs de neige, blizzards, grésil, pluie verglaçante et tempêtes de verglas, froid extrême, avalanches, embâcles | États-Unis | NWS Local Storm Reports |
| **Avertissements météo de MET Norway**, à côté de ceux des États-Unis | Norvège, ses mers, Svalbard | MET Norway |
| **Prévisions marines** pour 56 zones maritimes et 39 zones côtières, cliquez pour lire | de la mer du Nord au pôle Nord | MET Norway |
| **Un point de prévision à Longyearbyen**, au Svalbard, cliquez pour la prévision | Svalbard | MET Norway |
| **Radar météo** et **foudre** : le radar le plus net pour ce qui est à l'écran | le monde | dessinés par la carte Live Track |

### Pour vos lieux, sans rien configurer

« Vos lieux » sont votre domicile et toute personne, tout téléphone, traceur
d'appareil ou zone que vous choisissez de surveiller. Chaque lieu reçoit (les
noms des entités sont en anglais) :

* **Alert at …** : allumé tant que le lieu est dans une alerte météo, près
  d'un séisme fort ou dans la zone de danger d'un volcan en éruption. Prêt
  pour les automatisations : allumer les lumières, envoyer une notification
  sur le téléphone, fermer le garage.
* **Forecast at …** : une prévision météo complète qui suit le lieu quand il
  se déplace, pour chaque carte météo de votre tableau de bord. Les prévisions
  du National Weather Service sur le territoire terrestre des États-Unis ;
  celles de MET Norway partout ailleurs, et sur toutes les eaux.
* **Wind at …**, **Wind gust at …**, **Wind direction at …** et
  **Temperature at …** : ce qu'a mesuré la station météo la plus proche.
  Rentrez le store quand les rafales se lèvent.
* **Elevation at …** et **Depth at …** : l'altitude du sol, et la profondeur
  de l'eau sous un bateau.

### Activé par votre propre clé ou compte gratuit

| Clé ou compte gratuit | Ce qu'il ajoute |
|---|---|
| Clé de carte **NASA FIRMS** | alertes de feux de forêt près de vos lieux ; chaque détection de feu par satellite sur la carte |
| Clé API **AirNow** (États-Unis) | alertes de fumée de feux de forêt et de qualité de l'air (AQI PM2.5) pour vos lieux aux États-Unis ; chaque capteur de qualité de l'air sur la carte |
| Clé API **KNMI** (Pays-Bas) | un radar plus net sur les Pays-Bas |
| Nom d'utilisateur **GeoNames** | vent et température mesurés hors des États-Unis, depuis l'aéroport le plus proche ; le nom de la mer et l'eau ou la terre pour la profondeur |
| Identifiant client **MET Norway Frost** | chaque station météo du Svalbard et de Jan Mayen sur la carte ; vent et température mesurés pour vos lieux en Norvège et au Svalbard |

Chacun s'obtient en quelques minutes : [pas à pas ci-dessous](#clés-gratuites-qui-activent-davantage-pas-à-pas).

---

## Où il fonctionne

| Région | Ce que vous obtenez | Source | Il faut |
|---|---|---|---|
| **Le monde entier** | ouragans, typhons et cyclones ; séismes ; radar météo, foudre et nuages ; une prévision à chacun de vos lieux ; altitude et profondeur de la mer à vos lieux | National Hurricane Center, Joint Typhoon Warning Center et NASA (États-Unis) ; US Geological Survey ; les sources radar de la carte ; MET Norway ; Mapzen Terrain Tiles ; NOAA NCEI | rien |
| **Le monde entier** | détections de feux par satellite sur la carte, et alertes de feux de forêt à vos lieux | NASA FIRMS (États-Unis) | une clé de carte FIRMS gratuite |
| **Le monde entier**, hors des États-Unis | vent et température mesurés à vos lieux, depuis l'aéroport le plus proche ; le nom de la mer | GeoNames | un nom d'utilisateur GeoNames gratuit |
| **Amérique du Nord** : Canada | un radar plus net ; l'altitude à vos lieux | Environnement et Changement climatique Canada (GeoMet) ; Ressources naturelles Canada | rien |
| **Amérique du Nord** : Canada | stations de qualité de l'air sur la carte | AirNow (États-Unis) et partenaires | une clé AirNow gratuite |
| **Amérique du Nord** : États-Unis | alertes météo et avertissements d'orage ; la prévision d'orages violents ; volcans ; rivières en crue ; rapports d'orage et d'hiver ; la prévision et la météo mesurée du Weather Service à vos lieux ; altitude | National Weather Service, NOAA, US Geological Survey | rien |
| **Amérique du Nord** : États-Unis | alertes de fumée de feux de forêt à vos lieux ; stations de qualité de l'air sur la carte | AirNow | une clé AirNow gratuite |
| **Asie** : Japon | un radar plus net | Japan Meteorological Agency | rien |
| **Europe** : Allemagne | un radar plus net | Deutscher Wetterdienst | rien |
| **Europe** : Finlande | un radar plus net | Finnish Meteorological Institute | rien |
| **Europe** : Norvège, Svalbard et Jan Mayen | avertissements météo ; prévisions marines de la mer du Nord au pôle Nord ; une prévision à Longyearbyen ; altitude et profondeur de la mer en Norvège | MET Norway ; Kartverket | rien |
| **Europe** : Norvège, Svalbard et Jan Mayen | météo mesurée à vos lieux ; chaque station météo du Svalbard et de Jan Mayen sur la carte | MET Norway Frost | un identifiant client Frost gratuit |
| **Europe** : Pays-Bas | un radar plus net | KNMI | une clé KNMI gratuite |

⚠ Pour l'instant, les alertes météo ne viennent que des États-Unis et de la
Norvège. Partout ailleurs, vous avez les couches mondiales ci-dessus, une
prévision et la météo mesurée à vos lieux, et des alertes pour les séismes
forts à proximité et (avec une clé) les feux de forêt.

Pas dans la liste ? [Dites-le-nous](#aidez-le-à-grandir). Là où un service
météo publie ses alertes ou ses données ouvertement, nous étudierons son ajout.

---

## Les autres modules de Live Track

Live Track est un ensemble d'intégrations Home Assistant, une par type de
chose qui bouge, toutes dessinées sur la même carte. Chacune fonctionne seule ;
ensemble, elles forment une image en direct. Elles partagent la carte et une
bibliothèque Python
([saw-livetrack](https://github.com/StrausbergAutomationWorks/LiveTrackCore)),
si bien qu'en installer une de plus n'ajoute aucune requête vers une source
qu'une autre lit déjà.

| Module | Ce qu'il met sur la carte | État |
|---|---|---|
| [Live Track Aircraft](https://github.com/StrausbergAutomationWorks/LiveTrackAircraft) | les avions au-dessus de vous par ADS-B, avec routes et icônes de type | publié |
| [Live Track Ships](https://github.com/StrausbergAutomationWorks/LiveTrackShips) | navires et bateaux par AIS, près de vous ou n'importe où | publié |
| [Live Track Commuter Rail](https://github.com/StrausbergAutomationWorks/LiveTrackCommuterRail) | trains de banlieue en Amérique du Nord, en Europe et en Australie | publié |
| [Live Track Intercity Rail](https://github.com/StrausbergAutomationWorks/LiveTrackIntercityRail) | trains intercités et grandes lignes en Amérique du Nord, en Europe et en Australie | publié |
| [Live Track SALT](https://github.com/StrausbergAutomationWorks/LiveTrackSALT) | avions et navires des services d'immigration et des forces de l'ordre fédérales, d'après des listes publiques | publié |
| **Live Track Weather** | météo, tempêtes et risques naturels (ce module) | publié |
| [Live Track Internet](https://github.com/StrausbergAutomationWorks/LiveTrackInternet) | pannes d'internet, câbles sous-marins et liaisons terrestres | publié |
| Live Track Stations | tableaux des départs et rappels « il est temps de partir » pour chaque gare | prévu |
| Live Track Satellites | les satellites qui passent au-dessus de vous | prévu |
| Live Track Freight Trains | trains de marchandises et de travaux là où les chemins de fer les publient | prévu |
| Live Track Transit | bus urbains, tramways, ferries et métros | prévu |
| Live Track Intercity Buses | autocars interurbains et régionaux | prévu |
| Live Track Commuter Buses | bus de banlieue | prévu |
| [LiveTrackMapCard](https://github.com/StrausbergAutomationWorks/LiveTrackMapCard) | la carte partagée sur laquelle dessine chaque module | publiée, installée avec chaque module |

Tout est gratuit et libre. Rien n'est réservé aux sponsors.

---

## Avant de commencer

* **Home Assistant** 2026.11 ou plus récent.
* **Le Marketplace** (HACS) dans votre Home Assistant, pour l'installer et le
  mettre à jour facilement. Sans lui, vous pouvez copier les fichiers à la
  main.
* **Un accès à Internet** pour Home Assistant : tout vient de services météo
  publics.
* Rien à payer et aucun compte nécessaire pour l'essentiel. Les clés gratuites
  ci-dessus sont facultatives.

---

## Installation, pas à pas

### Depuis le Marketplace (recommandé)

1. Dans Home Assistant, ouvrez **Paramètres → Marketplace** (HACS).
2. Recherchez **Live Track Weather** et ouvrez-le.
3. Choisissez **Télécharger** (ou **Installer**).
4. **Redémarrez Home Assistant** : **Paramètres → Système → Corrections**
   propose le redémarrage, ou utilisez **Paramètres → Système → Redémarrer**.

Si la recherche ne le trouve pas, ajoutez-le par son lien : choisissez **Ajouter
depuis un lien** (ou le menu à trois points → **Dépôts personnalisés**),
saisissez `StrausbergAutomationWorks/LiveTrackWeather`, choisissez
**Intégration** si le type est demandé, puis reprenez à l'étape 3.

Le Marketplace propose ensuite chaque nouvelle version comme mise à jour.

### À la main

1. Téléchargez le code source de la
   [dernière version](https://github.com/StrausbergAutomationWorks/LiveTrackWeather/releases/latest).
2. Copiez son dossier `custom_components/live_track_weather` dans le dossier
   `custom_components` de votre dossier de configuration Home Assistant
   (créez `custom_components` s'il n'existe pas).
3. Redémarrez Home Assistant.

---

## Configuration, pas à pas

1. Ouvrez **Paramètres → Appareils et services**.
2. Choisissez **Ajouter une intégration** (en bas à droite) et cherchez
   **Live Track Weather**.
3. Choisissez **Valider**. Il n'y a rien à saisir : un seul Live Track Weather
   couvre le monde entier.

C'est tout. Les alertes, tempêtes, séismes, volcans, crues, rapports d'orage
et avertissements de MET Norway commencent à apparaître en quelques minutes,
et votre domicile est surveillé : **Alert at Home**, **Forecast at Home**,
**Wind at Home**, **Temperature at Home**, **Elevation at Home** et
**Depth at Home**.

### Changer ce qu'il surveille : les options

Ouvrez **Paramètres → Appareils et services → Live Track Weather →
Configurer** (la roue dentée). Chaque option, en termes simples :

| Option | Ce qu'elle fait | Par défaut |
|---|---|---|
| **Secondes entre deux interrogations** | à quelle fréquence la liste des alertes américaines est récupérée, de 60 à 900 secondes | 180 |
| **Surveiller le domicile** | votre domicile reçoit les capteurs « … at Home » et la prévision ; désactivez pour les supprimer | activé |
| **Surveiller aussi ces personnes, traceurs d'appareils ou zones** | chacun reçoit son propre « Alert at … », « Forecast at … », vent, température, altitude et profondeur, qui le suivent quand il se déplace. Choisissez le téléphone d'un proche, le traceur d'un camping-car, une zone de maison de vacances | aucun |
| **Alertes qui allument un lieu** | toute alerte (avis et communiqués compris), ou seulement les modérées, graves ou extrêmes. Chaque alerte reste listée dans le capteur | toute alerte |
| **Vent et température mesurés aux seules stations d'aéroport** | désactivé : la station la plus proche de n'importe quel type (souvent plus près d'un camping) ; activé : aéroports seulement | désactivé |
| **MAP_KEY NASA FIRMS** | alertes de feux et détections de feux (voir [clés gratuites](#clés-gratuites-qui-activent-davantage-pas-à-pas)) | vide |
| **Un feu compte dans un rayon de** | à quelle distance un feu doit se trouver pour allumer un lieu, de 5 à 150 km (3 à 93 miles) | 50 km (31 miles) |
| **Clé API AirNow** | alertes de fumée et stations de qualité de l'air | vide |
| **La fumée compte à partir d'un AQI PM2.5 de** | l'indice de qualité de l'air qui allume un lieu | 90 |
| **Détections de feux et stations de qualité de l'air sur la carte** | quelles régions dessiner : les 48 États contigus et Hawaï, l'Alaska, le Canada, le monde entier (feux seulement) | aucune |
| **Plus petit séisme sur la couche de points de la carte** | écarte les petits points de séisme sous une magnitude ; les marqueurs restent | vide : tous les séismes |
| **Clé API KNMI** | un radar plus net sur les Pays-Bas | vide |
| **Nom d'utilisateur GeoNames** | météo hors des États-Unis, noms des mers | vide |
| **Identifiant client MET Norway Frost** | stations du Svalbard et de Jan Mayen ; météo mesurée en Norvège | vide |

Chaque clé est vérifiée une fois à la saisie, et vous êtes prévenu si elle ne
fonctionne pas. Laissez un champ vide pour désactiver cette partie.

---

## Clés gratuites qui activent davantage, pas à pas

Toutes sont gratuites et personnelles : chaque personne qui installe Live
Track Weather obtient les siennes. Collez chacune dans **Paramètres →
Appareils et services → Live Track Weather → Configurer**.

### NASA FIRMS (feux de forêt)

1. Ouvrez <https://firms.modaps.eosdis.nasa.gov/api/map_key/>.
2. Saisissez votre adresse e-mail et demandez une **MAP_KEY**. Elle arrive par
   e-mail.
3. Collez-la dans **MAP_KEY NASA FIRMS**, et réglez **Un feu compte dans un
   rayon de** si 50 km (31 miles) ne vous conviennent pas.
4. Pour voir les feux sur la carte, cochez aussi une région sous
   **Détections de feux et stations de qualité de l'air sur la carte**.

### AirNow (fumée et qualité de l'air, États-Unis)

1. Ouvrez <https://docs.airnowapi.org/> et choisissez **Request an AirNow API
   Account**.
2. Confirmez l'e-mail, connectez-vous et copiez votre **API key** depuis la
   page de votre compte.
3. Collez-la dans **Clé API AirNow**.

### KNMI (radar sur les Pays-Bas)

1. Inscrivez-vous sur la KNMI Data Platform, <https://developer.dataplatform.knmi.nl/>.
2. Demandez une clé pour l'API **WMS**. (Une clé pour l'API Open Data ne
   fonctionne pas ici.)
3. Collez-la dans **Clé API KNMI**. La carte utilise alors le radar du KNMI
   sur les Pays-Bas ; sans elle, celui de RainViewer.

### GeoNames (météo hors des États-Unis)

1. Créez un compte gratuit sur <https://www.geonames.org/login>.
2. Ouvrez l'e-mail de confirmation envoyé par GeoNames, et confirmez.
3. Connectez-vous, ouvrez la page de votre compte et **activez les services
   web gratuits**.
4. Saisissez votre **nom d'utilisateur** (pas votre mot de passe) dans
   **Nom d'utilisateur GeoNames**.

### MET Norway Frost (stations du Svalbard, météo en Norvège)

1. Ouvrez <https://frost.met.no/auth/requestCredentials.html>.
2. Saisissez votre adresse e-mail. Vous recevez un **identifiant client** et
   un secret client.
3. Collez l'**identifiant client** dans **Identifiant client MET Norway
   Frost**. Le secret n'est pas nécessaire.

---

## Mettre la carte sur un tableau de bord

La carte est [LiveTrackMapCard](https://github.com/StrausbergAutomationWorks/LiveTrackMapCard),
la carte sur laquelle dessine chaque module Live Track. **Elle est installée
avec Live Track Weather** : rien à télécharger, rien à copier dans `www`,
aucune ressource à ajouter.

1. Ouvrez un tableau de bord, choisissez le crayon (**Modifier le tableau de
   bord**), puis **Ajouter une carte**.
2. Faites défiler jusqu'en bas et choisissez **Manuel**.
3. Collez ceci, et choisissez **Enregistrer** :

```yaml
type: custom:live-track-map-card
entity_filter:
  include:
    - domain: geo_location
      attributes:
        source: live_track_weather
```

Les alertes météo, la prévision d'orages, les zones de MET Norway, les cônes et
trajectoires des tempêtes, les lignes de secousse des séismes et les couches de
points apparaissent d'eux-mêmes. Les marqueurs (tempêtes, séismes, volcans,
stations hydrométriques, la prévision de Longyearbyen et les stations du
Svalbard) passent par le filtre ci-dessus.

Les autres modules Live Track vont dans `entity_filter` de la même façon : une
règle `- domain: geo_location` de plus pour chaque source.

**Sur la carte :**

* Le **sélecteur de couches** en haut à droite a une case pour chaque
  couche : les alertes américaines, la prévision d'orages, les cyclones
  tropicaux, les avertissements et prévisions marines de MET Norway, les
  séismes, les secousses sismiques, les rapports d'orage, les rapports
  hivernaux, les détections de feux, les stations de qualité de l'air, le
  radar météo, le mouvement du radar, la foudre et les nuages. Le choix de
  chaque spectateur est gardé dans son propre navigateur.
* **Cliquez** sur un marqueur, une zone, une ligne ou un point pour en savoir
  plus.
* La **carte de filtre** (`custom:live-track-map-filter-card`) peut masquer
  les stations du Svalbard, sous le nom **Observed weather (MET Norway)**.
* Le crédit de chaque source apparaît dans la ligne d'attribution de la carte
  tant que ses données sont affichées.

Si les ressources de vos tableaux de bord sont définies en YAML
(`lovelace: resource_mode: yaml`), rien ne peut être enregistré pour vous : un
problème dans **Corrections** donne alors la ligne exacte à ajouter. Toute
autre carte qui affiche les entités `geo_location` montre les marqueurs, mais
pas les alertes, les zones ni les points.

---

## L'utiliser dans des automatisations

Tout est une entité Home Assistant ordinaire, donc l'éditeur
d'automatisations fonctionne avec, sans code.

**Une notification sur le téléphone quand le domicile est dans une alerte :**

1. **Paramètres → Automatisations et scènes → Créer une automatisation →
   Créer une nouvelle automatisation**.
2. **Quand** : *Entité → État*, entité **Alert at Home**, vers **Dangereux**
   (activé).
3. **Alors faire** : *Notifications → Envoyer une notification via
   mobile_app_…*, avec un message comme `Alerte météo au domicile : {{ state_attr('binary_sensor.live_track_weather_alert_at_home', 'highest') }}`.
4. Enregistrez.

**Rentrer le store sur une rafale :** *Quand* **Wind gust at Home** dépasse
50 km/h (ou 30 mph), *alors* fermez la protection du store.

**Autres idées :** faire clignoter une lumière quand **Severe weather
outlook** atteint 3 (Enhanced) ; prévenir le propriétaire du camping-car
quand **Alert at Camper** s'allume à cause d'un feu de forêt à moins de
50 km ; notifier quand **Temperature at Cabin** passe sous zéro ; afficher
**Forecast at Boat** sur une carte météo pendant qu'il est en mer ; prévenir
la famille quand **Alert at Cabin**, en Norvège, s'allume pour un
avertissement de MET Norway.

---

## Tout ce qui est sur la carte, en détail

### Alertes météo des États-Unis

Chaque alerte active du National Weather Service : avertissements, veilles,
avis et communiqués pour les comtés, les zones terrestres, marines, du large
et de météo des feux, remplis en transparence dans la couleur que le Weather
Service donne à chaque événement (celle de plus haute priorité là où des
alertes se chevauchent). Les avertissements liés aux orages, comme ceux de
tornade, d'orage violent et de crue soudaine, sont dessinés selon leur propre
polygone, pas le comté entier. Aucun lieu n'est fixé : la carte montre ce qui
est à l'écran. Les contours des zones (11 651, simplifiés à environ 500 m,
environ 3,6 Mo) sont livrés avec chaque version et téléchargés une fois par
version par chaque navigateur.

**Capteur `US alerts`** : le nombre d'alertes actives ; ses attributs portent
la liste que dessine la carte (`zones`, `polygons`, `styles`, `updated`,
`shapes_url`), qui change à presque chaque interrogation et n'est pas
enregistrée dans l'historique.

### Cyclones tropicaux : ouragans, typhons, cyclones

Chaque cyclone tropical actif dans le monde, un marqueur par tempête étiqueté
de son nom et coloré selon sa catégorie : dépression bleue, tempête tropicale
bleu sarcelle, catégories 1 à 5 or, orange, orange foncé, rouge et magenta,
post-tropical gris. Survolez-le pour sa classe, son vent, sa pression et son
déplacement.

* Tempêtes du **National Hurricane Center** (Atlantique, Pacifique est et
  central) : le cône de prévision (bleu), la trajectoire prévue (rouge), les
  vents de 34, 50 et 64 nœuds actuels (63, 93 et 119 km/h ; 39, 58 et 74 mph)
  (jaune, orange, rouge) et la trajectoire
  passée (noir).
* **Tous les autres bassins**, du Joint Typhoon Warning Center via EONET de la
  NASA : le marqueur et la trajectoire passée. Une tempête dont la dernière
  position date de plus de 24 heures n'est pas affichée.

Les marqueurs sont `geo_location.storm_<id>` (`geo_location.storm_ep222026`),
avec les attributs `storm_class`, `storm_category` (TD, TS, H1-H5, PT),
`max_wind_kmh`, `pressure_hpa`, `course_deg`, `speed_kmh`, `last_seen`,
`advisory_number` et `storm_source`. Ils vont et viennent avec les tempêtes et
n'ont pas d'identifiant unique, ils ne peuvent donc pas être renommés dans
l'interface. **Capteur `Tropical cyclones`** : le nombre de tempêtes.

### Prévision d'orages violents

La prévision catégorielle du jour 1 du Storm Prediction Center : où des orages
violents peuvent se produire aujourd'hui, de 1 Marginal, 2 Slight, 3 Enhanced,
4 Moderate à 5 High, dans les couleurs propres du Center, sous les alertes.
**Capteur `Severe weather outlook`** : le risque le plus élevé aux États-Unis
aujourd'hui, de 0 à 5, enregistré pour pouvoir déclencher une automatisation ;
attributs `risk`, `issued`, `valid_from`, `valid_to`. La zone d'orages
ordinaires n'est pas dessinée.

### Séismes

Chaque séisme que l'US Geological Survey liste pour les dernières 24 heures,
dans le monde entier (environ 240 par jour) :

* Des **marqueurs** à partir de la magnitude 4,5, et pour tout séisme que des
  gens ont signalé avoir ressenti, étiquetés avec la magnitude
  (`geo_location.quake_<USGS id>`). Cliquez pour l'heure, la profondeur, les
  témoignages, la secousse la plus forte, le niveau d'alerte PAGER et la page
  de l'événement de l'USGS. Le « drapeau tsunami » n'est pas une alerte ; les
  alertes tsunami viennent de la NOAA (tsunami.gov).
* Des **points** pour tous les autres séismes (et les tirs de carrière et
  explosions en gris), sur leur propre couche : **capteur `Earthquakes`**.
  L'option **Plus petit séisme sur la couche de points de la carte** écarte
  les petits.
* Des **lignes de secousse** (USGS ShakeMap) pour les plus forts séismes du
  jour, magnitude 6 et plus ou forte secousse, cinq au maximum :
  **capteur `Earthquake shaking`**.

### Volcans en alerte

Chaque volcan des États-Unis au niveau d'alerte Advisory ou au code couleur
aviation Yellow et plus, un marqueur dans son code couleur étiqueté de son nom
(`geo_location.volcano_<number>`). Cliquez pour le niveau d'alerte, le code
couleur, depuis quand, le résumé de l'observatoire et des liens vers le
bulletin et la page du volcan.

### Rivières en crue ou dont la crue est prévue

Chaque station hydrométrique ou marégraphe des États-Unis **en crue mineure
ou pire actuellement**, ou dont on prévoit qu'elle l'atteindra, étiquetée
Minor, Moderate ou Major dans les couleurs de crue du Weather Service
(`geo_location.river_<gauge id>`). **Un anneau sombre signifie que la crue est
en cours** ; sans l'anneau, c'est une prévision. Cliquez pour la hauteur
actuelle, la hauteur prévue, les seuils de crue, le débit et la page de la
station. ⚠ Quelques stations portent des seuils de crue qui ressemblent à des
valeurs provisoires et affichent donc Major (Devils Lake, Dakota du Nord).

### Rapports d'orage

Chaque NWS Local Storm Report des dernières 24 heures concernant une tornade
ou une trombe marine, un nuage en entonnoir, de la grêle, du vent d'orage ou
des dégâts, une crue soudaine ou une inondation : rouge pour les tornades, bleu
pour le vent, vert pour la grêle, bleu sarcelle pour les inondations. Un
rapport important est plus grand avec un anneau sombre : toute tornade, grêle
de 5 cm (2 pouces) ou plus, ou vent de 120 km/h (65 nœuds) ou plus. Les rapports pâlissent en
vieillissant : moins d'une heure, 1 à 6 heures, 6 à 24 heures. Cliquez pour le
type, la taille ou la vitesse, le lieu, l'heure, le bureau du NWS et les
remarques. **Capteur `Storm reports`** : le nombre de points. ⚠ Ce sont des
rapports tels que les gens les envoient, avant que le Weather Service ne les
vérifie, et ils peuvent mettre 30 minutes à apparaître.

### Rapports hivernaux

À partir des mêmes rapports, sur leur propre couche sous les rapports
d'orage : neige, fortes chutes de neige et bourrasques de neige (bleu ardoise),
blizzards (rouge orangé), grésil (orchidée), pluie verglaçante, bruine
verglaçante et tempêtes de verglas (magenta foncé), dégâts de neige et de glace
(gris), froid extrême et refroidissement éolien (bleu), avalanches (brun) et
embâcles (bleu sarcelle foncé), chacun avec un fin anneau sombre. Les rapports
importants sont plus grands : 30 cm de neige (12 pouces), 1,3 cm de grésil (un
demi-pouce), 6 mm de glace (un quart de pouce) ou toute tempête de verglas. Cliquez pour la quantité en
pouces et en cm ou mm, ou la température en °F et °C. **Capteur `Winter
reports`**. ⚠ Une grosse tempête apporte des milliers de rapports ; là où deux
se chevaucheraient, un seul est dessiné, alors zoomez.

### MET Norway : avertissements, prévisions marines, la prévision de Longyearbyen

* **Avertissements** pour la terre, la côte et les mers de Norvège et les mers
  jusqu'au pôle Nord, dans le jaune, l'orange ou le rouge de MET, à côté des
  alertes américaines. Cliquez sur l'un d'eux pour ce qui est attendu, les
  conséquences, les conseils et la période (en anglais). **Capteur `MET Norway
  warnings`**.
* **Prévisions marines** pour 56 zones maritimes et 39 zones côtières, dont
  celles du Svalbard, sous les avertissements. Cliquez sur l'une d'elles pour
  sa prévision et tout avertissement de vent, de glace ou de dépression
  polaire. **Capteur `MET Norway marine forecasts`**.
* **Un point de prévision à Longyearbyen**, étiqueté avec la température ;
  cliquez dessus pour la prévision toutes les six heures sur une journée
  (`geo_location.met_forecast_longyearbyen`).

### Météo mesurée au Svalbard et à Jan Mayen (identifiant client Frost)

Un point bleu sarcelle pour chaque station météo du Svalbard, de l'île aux
Ours, de Hopen et de Jan Mayen dont la température et le vent datent tous deux
de moins de deux heures (une trentaine), étiqueté avec la température
(`geo_location.frost_sn99840` pour Svalbard Lufthavn, et ainsi de suite).
Cliquez sur l'un d'eux pour la température, le vent et sa direction, la plus
forte rafale de la dernière heure, l'humidité, la pression, la hauteur de neige
et l'heure. Les stations qui ne transmettent que la température ne sont pas
dessinées ; de deux stations distantes de moins de 1 km, une seule est
dessinée. Les valeurs que Frost marque comme très incertaines ou erronées ne
sont pas utilisées ; les valeurs vérifiées seulement automatiquement pour
l'instant (c'est généralement le cas de l'heure la plus récente de MET) sont
affichées, et la fenêtre indique « Automatic check only ».

### Feux de forêt et qualité de l'air (clés FIRMS et AirNow)

Choisissez des régions sous **Détections de feux et stations de qualité de
l'air sur la carte** :

* **Détections de feux** (nécessite la clé FIRMS) : chaque détection de feu
  par satellite des dernières 24 heures (NOAA-20 et NOAA-21 VIIRS) en petits
  points rouges. Les usines, raffineries, torchères et autres sources de
  chaleur fixes que la NASA a classées sont écartées. Cliquez pour le moment,
  le satellite, la puissance radiative du feu et la confiance de la NASA.
  **Capteur `Fire detections`**.
* **Stations de qualité de l'air** (nécessite la clé AirNow ; États-Unis et
  Canada) : chaque capteur de particules fines (PM2.5), coloré selon son AQI
  dans les couleurs de l'EPA, toutes les heures. **Capteur `Air quality
  sites`**.

### Radar météo, foudre et nuages

Dessinés par la carte elle-même, sans rien configurer : une couche radar qui
choisit la source la plus nette pour ce qui est à l'écran (RainViewer, NOAA
nowCOAST et GeoMet du Canada en Amérique du Nord ; le FMI de Finlande et le
DWD d'Allemagne en Europe ; la JMA du Japon ; le KNMI sur les Pays-Bas avec
votre clé), le mouvement du radar, la foudre de nowCOAST et les nuages des
satellites GOES et EUMETSAT.

---

## Tout ce qui concerne vos lieux, en détail

### Alert at …

**`Alert at Home`** (`binary_sensor.live_track_weather_alert_at_home`, classe
d'appareil *safety* : activé signifie dangereux), et un par personne, traceur
ou zone que vous surveillez. Il s'allume quand le lieu est :

* dans une **alerte météo américaine** ou un **avertissement de MET Norway**
  (selon la règle propre du Weather Service : un avertissement de tornade ou
  de crue compte à l'intérieur de son polygone, pas dans tout le comté ; les
  zones viennent du Weather Service lui-même, donc un lieu sur une côte ou à
  la limite d'un comté obtient la bonne réponse) ;
* près d'un **séisme** fort dans les dernières 24 heures : magnitude 4 à moins
  de 50 km (31 miles), 5 à moins de 150 km (93 miles), 6 à moins de 300 km
  (186 miles), 7 à moins de 600 km (373 miles) ;
* dans la zone de danger d'un **volcan** au niveau Watch ou Orange et plus (la
  National Volcanic Threat Layer de l'USGS, livrée avec l'intégration) ;
* avec la clé FIRMS, près d'un **feu de forêt** (dans la distance que vous
  avez réglée, 50 km (31 miles) par défaut ; les détections arrivent dans Home Assistant
  2 à 4 heures après le passage du satellite) ;
* avec la clé AirNow, dans la **fumée d'un feu de forêt** : le capteur PM2.5
  le plus proche dans un rayon de 80 km (50 miles) à l'AQI que vous avez réglé ou
  au-dessus, 90 par défaut (lieux aux États-Unis).

Attributs : `alerts` (chaque alerte au lieu, la pire d'abord, avec `event`,
`severity`, `headline`, `onset`, `ends`, `source` et un lien), `highest`,
`zones` ; avec les clés, `fires_near`, `nearest_fire_km`, `pm25_aqi`,
`pm25_site` et plus. Les zones d'un traceur mobile sont redemandées après un
déplacement de plus de 1 km. La NASA déconseille d'utiliser les seules
détections de feux pour des décisions sur le terrain : suivez les ordres
d'évacuation.

### Forecast at …

**`Forecast at Home`** (`weather.live_track_weather_forecast_at_home`), et une
par lieu surveillé, pour chaque carte météo et `weather.get_forecasts` :
quotidienne, jour et nuit, et horaire.

* **Sur le territoire terrestre des États-Unis** : la prévision du National
  Weather Service pour la maille de 2,5 km du lieu, sept jours de jour et de
  nuit avec le texte de prévision, et horaire sur six jours et demi.
* **Partout ailleurs, et sur toutes les eaux** : la prévision de MET Norway,
  horaire pendant environ deux jours et demi, puis toutes les six heures
  jusqu'à environ dix jours.

Elle change de source quand le lieu se déplace (un bateau qui quitte le port,
un camping-car qui passe au Canada).

### Wind at …, Wind gust at …, Wind direction at …, Temperature at …

Ce qu'a mesuré la station météo la plus proche, pour chaque lieu surveillé
(`sensor.live_track_weather_wind_at_home` et ainsi de suite).

* **Aux États-Unis** : la station du National Weather Service la plus proche
  de n'importe quel réseau (aéroports, stations météo des feux et routières,
  stations de bénévoles), ou seulement les aéroports en option ; la suivante,
  jusqu'à trois, quand l'une n'a rien de récent.
* **En Norvège et au Svalbard**, avec un identifiant client Frost : la plus
  proche des stations de MET Norway (mesuré en 22 lieux de Norvège : de 0,4 à
  11 km). La rafale est la plus forte de la dernière heure.
* **Ailleurs**, avec un nom d'utilisateur GeoNames : le bulletin météo
  (METAR) de l'aéroport le plus proche, dans un rayon d'environ 100 km (60 miles).
* Un capteur est **indisponible** quand aucun bulletin de moins de deux heures
  ne contient sa valeur. Une rafale est inconnue quand aucune n'a été
  signalée. Attributs : `station`, `station_name`, `provider`, `distance_km`,
  `observed`, `age_min`.

### Elevation at … et Depth at …

**`Elevation at Home`** et **`Depth at Home`**, et un de chaque par lieu
surveillé, vérifiés au démarrage et après un déplacement de plus de 500 m.

* **Altitude** depuis la première source qui a une valeur : USGS 3DEP
  (États-Unis et régions frontalières, au mètre près), Ressources naturelles
  Canada, Kartverket (Norvège continentale), puis les Terrain Tiles de Mapzen
  pour le reste du monde.
* **Sur l'eau**, l'altitude est la surface et **Depth** est la profondeur
  sous le lieu, d'après Kartverket en Norvège ou NOAA NCEI ailleurs (les
  Grands Lacs compris) ; inconnue sur la terre. Avec un nom d'utilisateur
  GeoNames, `sea` donne le nom de la mer.
* ⚠ Limites connues : l'altitude au Svalbard est trop haute d'environ 35 m
  (aucune meilleure source trouvée) ; les rivières, ports et réservoirs n'ont
  pas de profondeur ; dans les mers peu profondes sans GeoNames, l'altitude
  est le fond de la mer ; un lac sous le niveau de la mer atteint seulement
  par les terrain tiles affiche 0.

---

## Toutes les entités qu'il crée

| Entité | Ce que c'est |
|---|---|
| `sensor.live_track_weather_us_alerts` | nombre d'alertes américaines actives ; la liste que dessine la carte |
| `sensor.live_track_weather_tropical_cyclones` | nombre de cyclones tropicaux |
| `sensor.live_track_weather_severe_weather_outlook` | risque d'orages violents le plus élevé aujourd'hui, de 0 à 5 |
| `sensor.live_track_weather_met_norway_warnings` | avertissements de MET Norway dessinés |
| `sensor.live_track_weather_met_norway_marine_forecasts` | zones de prévision marine de MET Norway |
| `sensor.live_track_weather_earthquakes` | points de séisme sur la carte |
| `sensor.live_track_weather_earthquake_shaking` | ShakeMaps dessinées |
| `sensor.live_track_weather_storm_reports` | rapports d'orage dessinés |
| `sensor.live_track_weather_winter_reports` | rapports hivernaux dessinés |
| `sensor.live_track_weather_fire_detections` | détections de feux (clé FIRMS et une région) |
| `sensor.live_track_weather_air_quality_sites` | stations de qualité de l'air (clé AirNow et une région) |
| `sensor.live_track_weather_knmi_radar` | image radar KNMI la plus récente (clé KNMI) |
| `geo_location.storm_…`, `quake_…`, `volcano_…`, `river_…`, `met_forecast_…`, `frost_…` | les marqueurs ; ils vont et viennent et n'ont pas d'identifiant unique |
| `binary_sensor.live_track_weather_alert_at_home` | Alert at Home (et un par lieu surveillé) |
| `weather.live_track_weather_forecast_at_home` | Forecast at Home (et une par lieu surveillé) |
| `sensor.live_track_weather_wind_at_home`, `…_wind_gust_at_home`, `…_wind_direction_at_home`, `…_temperature_at_home` | météo mesurée au domicile (et par lieu) |
| `sensor.live_track_weather_elevation_at_home`, `…_depth_at_home` | altitude et profondeur au domicile (et par lieu) |

Les attributs qui changent à chaque interrogation (listes, formes, fenêtres)
sont tenus hors de l'historique de Home Assistant, pour que votre base de
données ne grossisse pas avec eux.

---

## Ce qu'il envoie et télécharge

**Votre position.** La position de votre domicile et de chaque lieu surveillé
est envoyée, arrondie à environ 11 m, seulement là où un service en a
besoin : au National Weather Service pour connaître les zones, la maille de
prévision et les stations du lieu ; hors de la zone de prévision américaine,
à MET Norway pour sa prévision ; à l'USGS (et, là où l'USGS n'a rien, à
Ressources naturelles Canada, Kartverket et NOAA NCEI) pour l'altitude et la
profondeur, au démarrage et après un déplacement de plus de 500 m ; avec vos
clés, à NASA FIRMS (un rectangle autour du lieu), AirNow, GeoNames et Frost de
MET Norway. Désactivez **Surveiller le domicile** et ne surveillez rien
d'autre, et aucune position n'est envoyée. Rien d'autre vous concernant n'est
envoyé nulle part.

**Combien.** La liste des alertes américaines environ 100 Ko toutes les
3 minutes (réglable) ; les autres ne demandent un fichier que s'il a changé,
là où le service le permet : bulletins d'ouragan toutes les 5 minutes, EONET
toutes les 30, la prévision d'orages toutes les 5, les avertissements de MET
Norway toutes les 5, les prévisions marines toutes les 15-30 et les prévisions
ponctuelles toutes les 30 (chacune une minute plus tard au hasard, comme le
demande MET, et rien pendant 30 minutes après un refus) ; les séismes de
l'USGS toutes les 5 minutes (environ 170 Ko), les volcans toutes les 10, les
rivières toutes les 30, les rapports d'orage toutes les 10 ; Frost toutes les
10 minutes (environ 80 Ko) ; GeoNames dans la limite de la moitié de ses
10 000 crédits gratuits quotidiens ; le KNMI au plus environ 24 requêtes par
heure, et seulement pendant qu'une carte l'affiche. Après une erreur, chaque
service est laissé tranquille un moment avant d'être sollicité de nouveau.

---

## Aidez-le à grandir

Live Track Weather continue de grandir. Nous ajoutons des pays, des services
météo et des dangers à mesure que nous les trouvons, et nous voulons savoir ce
que vous aimeriez ensuite.

### Proposer quelque chose

Votre service météo manque ? Quelque chose est faux, ou difficile à
comprendre ? Dites-le-nous de la façon la plus simple pour vous :

* [**Remplissez un court formulaire**](https://github.com/StrausbergAutomationWorks/LiveTrackWeather/issues/new?template=fr.yml)
  en français. Il vous faut un compte GitHub gratuit.
* **Écrivez un e-mail** à
  [StrausbergAutomationWorks@recordwise.org](mailto:StrausbergAutomationWorks@recordwise.org).
  Aucun compte n'est nécessaire.

Dans les deux cas, il nous aide que vous nous disiez :

* ce que vous aimeriez voir, et où dans le monde ;
* un lien vers l'endroit où les données sont publiées, si vous en connaissez
  un (une page de données ouvertes, un flux public, le site d'un service
  météo) : ce n'est pas nécessaire, mais cela aide ;
* la langue de votre Home Assistant, si le problème concerne la formulation ou
  une traduction.

Écrivez en anglais ou dans votre propre langue, ce qui est le plus simple pour
vous.

### L'ajouter vous-même, avec notre aide

Si vous souhaitez ajouter quelque chose vous-même, nous vous aiderons à le
faire, de la première question jusqu'à la version terminée. Vous n'avez pas
besoin d'être développeur pour commencer :

* **Une traduction.** Les textes de la boîte de dialogue de configuration sont
  une courte liste de phrases dans un seul fichier texte. Nous vous montrerons
  quel fichier et quelles lignes.
* **Un nouveau pays ou un nouveau service météo.** Dites-nous où les données
  sont publiées. Nous pouvons écrire le code ensemble, ou relire le vôtre.
* **Le tester là où vous habitez.** Installez-le, regardez votre partie de la
  carte, et dites-nous ce qui est juste et ce qui ne l'est pas.
* **Une correction de ce README.** Si une étape ne correspondait pas à ce que
  vous avez vu, dites-nous ce que vous avez vu.

[**Dites-nous ce que vous avez en tête**](https://github.com/StrausbergAutomationWorks/LiveTrackWeather/issues/new?template=fr.yml)
ou écrivez à
[StrausbergAutomationWorks@recordwise.org](mailto:StrausbergAutomationWorks@recordwise.org),
et nous vous répondrons avec les prochaines étapes.

---

## Langues

Ce README : [English](README.md), [Deutsch](README.de.md), **Français**,
[Nederlands](README.nl.md), [简体中文](README.zh-Hans.md),
[Español](README.es.md), [Italiano](README.it.md), [Dansk](README.da.md) et
[Kalaallisut](README.kl.md) (un court brouillon ; tant qu'un locuteur natif
ne l'a pas relu, la page danoise est la page fiable). Chaque README traduit
est complet.

La boîte de dialogue de configuration et les options s'affichent dans la
langue de votre Home Assistant quand c'est l'une de celles-ci : English,
Dansk, Deutsch, Español, Français, Gaeilge, Íslenska, Italiano, Nederlands,
Norsk Bokmål, Polski, Português, Português (BR), Suomi, Svenska et 简体中文.
Toute autre langue affiche l'anglais. Les noms des entités (**Alert at Home**
et ainsi de suite) et les libellés de la carte sont en anglais dans toutes les
langues.

Vous avez trouvé une erreur dans une traduction, ou il vous faut une autre
langue ? Dites-le-nous sur
<https://github.com/StrausbergAutomationWorks/LiveTrackWeather/issues>, ou
[traduisez-le avec notre aide](#lajouter-vous-même-avec-notre-aide).

---

## Crédits et licences

* Le National Weather Service, le National Hurricane Center, le Storm
  Prediction Center, le National Water Prediction Service, le Joint Typhoon
  Warning Center, la NASA et l'US Geological Survey sont des agences du
  gouvernement des États-Unis ; leurs données sont des œuvres du gouvernement
  des États-Unis. Les données d'AirNow sont provisoires et non vérifiées (US
  EPA et partenaires).
* **MET Norway** : données sous la Norwegian Licence for Open Government Data
  (NLOD) 2.0 et Creative Commons Attribution 4.0 ; les observations de Frost
  sous Creative Commons Attribution 3.0 Norway. Cette intégration arrondit les
  zones, recolore les avertissements et convertit les unités.
* **KNMI** : radar sous Creative Commons Attribution 4.0, découpé et
  redimensionné en tuiles de carte.
* **GeoNames** : bulletins METAR et noms des mers sous Creative Commons
  Attribution 4.0.
* **Altitude** : le CDEM de Ressources naturelles Canada, Open Government
  Licence - Canada ; Kartverket, Creative Commons Attribution 4.0 ; NOAA NCEI,
  gouvernement des États-Unis. **Terrain Tiles** : Mapzen, et les sources
  citées dans l'attribution Joerd de Mapzen (`tilezen/joerd`,
  `docs/attribution.md`), reproduites ici telles quelles : ArcticDEM terrain
  data DEM(s) were created from DigitalGlobe, Inc., imagery and funded under
  National Science Foundation awards 1043681, 1559691, and 1542736; Australia
  terrain data © Commonwealth of Australia (Geoscience Australia) 2017; Austria
  terrain data © offene Daten Österreichs – Digitales Geländemodell (DGM)
  Österreich; Canada terrain data contains information licensed under the Open
  Government Licence – Canada; Europe terrain data produced using Copernicus
  data and information funded by the European Union - EU-DEM layers; Global
  ETOPO1 terrain data U.S. National Oceanic and Atmospheric Administration;
  Mexico terrain data source: INEGI, Continental relief, 2016; New Zealand
  terrain data Copyright 2011 Crown copyright (c) Land Information New Zealand
  and the New Zealand Government (All rights reserved); Norway terrain data ©
  Kartverket; United Kingdom terrain data © Environment Agency copyright and/or
  database right 2015. All rights reserved; United States 3DEP (formerly NED)
  and global GMTED2010 and SRTM terrain data courtesy of the U.S. Geological
  Survey.
* **Zones de danger volcanique** : USGS National Volcanic Threat Layer (2024,
  CC0).

Aucune de ces organisations n'a créé ni approuvé cette intégration.

**Code** : MIT, dans [LICENSE](LICENSE).

**Pour les développeurs :** `tools/build_shapes.py` reconstruit le fichier des
zones d'alerte à partir des shapefiles du NWS (<https://www.weather.gov/gis/>)
et `tools/build_colours.py` la table des couleurs à partir de la page de la
carte des dangers du NWS ; les tests se lancent avec
`python -m unittest discover -s tests`.

---

## Mots-clés

Home Assistant météo · Home Assistant alertes météo · alertes NWS · National
Weather Service · carte des alertes météo · alerte tornade · alerte orage
violent · crue soudaine · tempête hivernale · suivi des ouragans · tempête
tropicale · typhon · cyclone · cône d'ouragan · NHC · JTWC · SPC outlook ·
prévision d'orages violents · carte des séismes · alerte séisme · séismes
USGS · ShakeMap · alerte volcan · carte des crues · station hydrométrique ·
NWPS · rapports d'orage · grêle · hauteur de neige · blizzard · tempête de
verglas · carte des feux de forêt · alerte feu de forêt · détection de feux ·
NASA FIRMS · VIIRS · alerte fumée · qualité de l'air · AQI · PM2.5 · AirNow ·
radar météo · radar de pluie · carte de la foudre · MET Norway · yr · météo
Svalbard · Longyearbyen · Jan Mayen · Frost API · prévision marine · KNMI
radar · GeoNames · METAR · station météo · capteur de rafales · capteur de
température · prévision pour un traceur · météo camping-car · météo bateau ·
capteur d'altitude · profondeur de l'eau · geo_location · binary_sensor ·
weather entity · carte · Lovelace · HACS · Marketplace · Live Track ·
LiveTrack · weather warning · vejrvarsel · Unwetterwarnung · weerwaarschuwing ·
alerta meteorológica · allerta meteo · farevarsel · 天气预警 ·
StrausbergAutomationWorks

---

**Reconnaissance.** StrausbergAutomationWorks reconnaît les peuples autochtones
de toutes les terres et de toutes les eaux de cette carte, partout dans le
monde, et rend hommage à leurs Aînés d'hier et d'aujourd'hui.
