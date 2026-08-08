# Sources de données

Ce document décrit la provenance, la période de référence, le niveau territorial,
le rôle dans le projet ainsi que les principales limites des sources de données
externes utilisées ou prévues dans le projet
**Brussels North Social-Health Needs & Network Lab**.

Les fichiers sources bruts sont conservés localement dans `data/raw/`.
Ils sont distingués des données intermédiaires et des fichiers produits par
les traitements du projet.

---

## 1. Projections démographiques communales de l'IBSA

- **Nom de la source :** Projections démographiques communales bruxelloises 2026-2035
- **Institution :** Institut Bruxellois de Statistique et d'Analyse (IBSA)
- **Sources sous-jacentes :** Bureau fédéral du Plan (BFP), Statbel et IBSA
- **Fichier utilisé :** fichier original de projections de l'IBSA conservé localement dans `data/raw/`
- **Période de référence :** 2026-2035, population au 1er janvier
- **Niveau territorial :** commune
- **Principales variables :** commune, âge, sexe et population projetée
- **Rôle dans le projet :** fournir le contexte démographique et analyser les évolutions attendues de la population dans les communes pertinentes pour le Bassin Nord
- **Fichier produit :** `data/processed/population_projection_core_municipalities.csv`
- **Licence :** CC BY 4.0
- **Limites éventuelles :**
  - les projections constituent des estimations de populations futures et ne doivent pas être interprétées comme des effectifs futurs observés ;
  - la source est disponible au niveau communal ;
  - les données de la Ville de Bruxelles ne permettent pas d'isoler directement Laeken, Neder-Over-Heembeek et Haren ;
  - la géographie des projections démographiques ne coïncide donc pas parfaitement avec le périmètre opérationnel final du Bassin Nord.

---

## 2. Monitoring des Quartiers — Indicateurs de vulnérabilité territoriale

- **Nom de la source :** Monitoring des Quartiers
- **Institution :** IBSA / perspective.brussels
- **Date de téléchargement :** 7 août 2026
- **Fichiers utilisés :**
  - `data/raw/monitoring_brussels_vul_unemployment_2023.csv`
  - `data/raw/monitoring_brussels_vul_cpas_2023.csv`
  - `data/raw/monitoring_brussels_vul_bim_2024.csv`
- **Niveau territorial :** quartiers du Monitoring
- **Couverture territoriale :** ensemble des 145 quartiers du Monitoring de la Région de Bruxelles-Capitale
- **Rôle dans le projet :** construire un profil de vulnérabilité territoriale permettant d'identifier des signaux sociaux et socio-économiques nécessitant une analyse complémentaire

### Indicateurs utilisés

| Indicateur | Année de référence | Unité |
|---|---:|---:|
| Taux de chômage | 2023 | % |
| Part des bénéficiaires d'un revenu du CPAS (RIS ou équivalent) | 2023 | % |
| Part des bénéficiaires de l'intervention majorée (BIM) | 2024 | % |

### Fichiers produits

Les fichiers bruts sont nettoyés à l'aide du script :

`src/prepare_vulnerability.py`

Fichiers intermédiaires :

- `data/interim/monitoring_unemployment_2023_clean.csv`
- `data/interim/monitoring_cpas_2023_clean.csv`
- `data/interim/monitoring_bim_2024_clean.csv`

Fichier principal produit :

- `data/processed/territorial_vulnerability_indicators.csv`

### Limites éventuelles

- les trois indicateurs ne se rapportent pas tous à la même année : le chômage et le CPAS se rapportent à 2023, tandis que le BIM se rapporte à 2024 ;
- les années de référence sont conservées dans le pipeline plutôt que d'être artificiellement harmonisées ;
- les données manquantes restent enregistrées comme valeurs manquantes et ne sont jamais remplacées par zéro ;
- 117 des 145 quartiers du Monitoring disposent actuellement des trois indicateurs ;
- 28 quartiers présentent au moins un indicateur manquant ;
- 22 quartiers ne disposent d'aucun des trois indicateurs ;
- les quartiers du Monitoring ne correspondent pas aux quartiers social-santé officiels (QSS) ;
- aucun indice composite de vulnérabilité n'est actuellement construit, car la couverture des indicateurs, leurs années de référence et leurs relations statistiques doivent d'abord être examinées.

---

## 3. UrbIS Vector — Géographie administrative et statistique

- **Nom de la source :** UrbIS — Unités administratives / UrbIS Vector
- **Institution :** Paradigm.brussels
- **Fichier utilisé :** `data/raw/geography/UrbISVector_04000.gpkg`
- **Format :** GeoPackage
- **Système de coordonnées de la source :** Belgian Lambert 1972 — EPSG:31370
- **Principales couches utilisées :**
  - `MonitoringDistricts`
  - `StatisticalSectors`
- **Niveau territorial :** quartiers du Monitoring et secteurs statistiques
- **Rôle dans le projet :**
  - fournir les limites géographiques officielles utilisées dans les analyses spatiales ;
  - relier les 145 quartiers du Monitoring aux indicateurs de vulnérabilité ;
  - utiliser `MDZONE` comme identifiant géographique correspondant à `territory_code` ;
  - utiliser `NISCODE` et `MONITORINGDISTRICT_ID` des secteurs statistiques pour construire une passerelle géographique plus fine destinée à l'analyse préliminaire du périmètre du Bassin Nord.

### Couche `MonitoringDistricts`

Caractéristiques validées :

- 145 entités géographiques ;
- 145 valeurs uniques de `MDZONE` ;
- type de géométrie : `MultiPolygon` ;
- aucune géométrie manquante ;
- aucune géométrie vide ;
- aucune géométrie invalide ;
- correspondance exacte de type un-à-un entre `MDZONE` et les 145 valeurs de `territory_code` du Monitoring.

Les fichiers géographiques destinés à la cartographie web sont transformés en
EPSG:4326.

### Couche `StatisticalSectors`

Cette couche est utilisée comme passerelle géographique fine entre :

`NISCODE`
→ commune
→ `MONITORINGDISTRICT_ID`
→ quartier du Monitoring.

Elle est notamment exploitée par :

`src/derive_north_scope_candidates.py`

### Limites éventuelles

- les quartiers du Monitoring UrbIS et les quartiers social-santé officiels (QSS) constituent deux systèmes territoriaux différents ;
- UrbIS ne permet donc pas, à lui seul, d'établir définitivement la limite officielle du Bassin Nord ;
- la couche `StatisticalSectors` contient 750 objets géométriques mais 749 valeurs uniques de `NISCODE`, car un code de secteur statistique est représenté par deux polygones distincts ;
- cette particularité géométrique n'affecte pas la classification actuelle des quartiers du Monitoring, puisque celle-ci repose sur les identifiants territoriaux et ne considère pas les 750 polygones comme 750 codes statistiques distincts.

---

## 4. Quartiers social-santé et bassins d'aide et de soins

- **Nom de la source :** Arrêté conjoint d'exécution du 4 avril 2024 relatif à l'organisation de l'ambulatoire et de la première ligne social-santé en Région de Bruxelles-Capitale
- **Institutions :** autorités conjointes de la Commission communautaire commune (COCOM) et de la Commission communautaire française (COCOF)
- **Publication officielle :** Moniteur belge, 30 avril 2024
- **Fichier utilisé :** document juridique officiel consulté comme référence institutionnelle ; aucun référentiel QSS exploitable automatiquement n'a encore été intégré au projet
- **Année de référence :** 2024
- **Niveau territorial :** quartiers social-santé (QSS) et bassins d'aide et de soins
- **Structure officielle :** 56 quartiers social-santé et 5 bassins d'aide et de soins
- **Rôle dans le projet :** fournir la référence institutionnelle pour la définition finale du périmètre Brussels North / Bassin Nord

### État actuel des données

Un référentiel exploitable permettant de relier :

`secteur statistique NISCODE`
→ `QSS`
→ `bassin d'aide et de soins`

a été demandé à Vivalis / à l'Observatoire de la Santé et du Social,
avec une éventuelle orientation complémentaire via Brusano.

Le crosswalk final du Bassin Nord est donc volontairement considéré comme :

**en attente du référentiel officiel**.

### Limites éventuelles

- la source juridique définit le système territorial, mais le projet ne dispose pas encore d'une table officielle exploitable automatiquement reliant chaque secteur statistique à son QSS et à son bassin ;
- les quartiers du Monitoring ne peuvent donc pas être assimilés automatiquement aux QSS officiels ;
- les cas géographiques ambigus sont maintenus dans des catégories `REVIEW` ou `PARTIAL` plutôt que d'être attribués à partir de noms, d'une interprétation visuelle ou d'un seuil arbitraire.

---

## 5. Brusano — Référence opérationnelle du Bassin Nord

- **Nom de la source :** Informations territoriales et opérationnelles du Bassin Nord
- **Institution :** Brusano
- **Fichier utilisé :** documentation institutionnelle en ligne ; aucun fichier de données analytique brut
- **Période de référence :** documentation opérationnelle actuelle consultée en 2026
- **Niveau territorial :** bassin d'aide et de soins
- **Définition territoriale utilisée pour l'orientation :** Berchem-Sainte-Agathe, Ganshoren, Jette et Koekelberg, ainsi que les parties de la Ville de Bruxelles correspondant à Laeken, Neder-Over-Heembeek et Haren
- **Rôle dans le projet :**
  - fournir l'interprétation opérationnelle du territoire cible du Bassin Nord ;
  - soutenir la classification préliminaire des territoires à partir des communes ;
  - fournir des éléments de contexte pour les futures analyses des besoins et de l'offre social-santé.

### Limite éventuelle

Cette définition territoriale descriptive n'est pas suffisamment fine, à elle seule,
pour attribuer chaque quartier du Monitoring au Bassin Nord.

En effet, certains quartiers du Monitoring traversent des limites communales ou
des limites infra-communales.

Cette source est donc utilisée conjointement avec les secteurs statistiques
UrbIS et devra être complétée par le référentiel officiel des QSS.

---

## 6. Classification préliminaire du périmètre Brussels North

Cette section décrit un **fichier dérivé du projet** et non une source externe.

- **Fichier dérivé :** `data/interim/north_scope_candidates.csv`
- **Script :** `src/derive_north_scope_candidates.py`
- **Sources d'entrée :** couches UrbIS `StatisticalSectors` et `MonitoringDistricts`
- **Niveau territorial :** quartier du Monitoring
- **Rôle dans le projet :** identifier les quartiers pouvant déjà être classés avec un degré élevé de certitude à partir de la composition communale des secteurs statistiques et isoler les cas nécessitant une validation plus fine à partir des QSS officiels.

### Catégories actuellement utilisées

- `CERTAIN_YES`
- `CERTAIN_NO`
- `REVIEW_BRUSSELS_CITY`
- `REVIEW_BRUSSELS_CITY_MIXED`
- `PARTIAL_MUNICIPAL_BOUNDARY`

Ces catégories constituent des **résultats diagnostiques intermédiaires**.

Elles ne doivent pas être interprétées comme le crosswalk officiel et définitif
du Bassin Nord.

---

## 7. Bruxelles Social — Source prévue pour l'analyse de l'offre social-santé

- **Nom de la source :** Bruxelles Social / Sociaal Brussel
- **Institution :** Observatoire de la Santé et du Social / Vivalis
- **Fichier utilisé :** aucun à ce stade — source pas encore intégrée
- **Période de référence :** répertoire actualisé en continu ; la date exacte d'extraction sera enregistrée lors du téléchargement
- **Niveau territorial :** organisations, implantations de services et zones d'action dans la Région de Bruxelles-Capitale
- **Rôle dans le projet :** future source destinée à l'analyse de l'offre social-santé et de son accessibilité
- **Variables potentielles :** nom de l'organisation, adresse, activités, publics bénéficiaires, zone d'action, offre linguistique et informations de contact
- **État d'implémentation :** prévu / non encore intégré

### Limites éventuelles

- le répertoire est régulièrement actualisé ;
- la plateforme est actuellement en évolution ;
- toute future extraction devra donc mentionner explicitement sa date ;
- le nombre d'organisations ou de services recensés ne doit pas être interprété comme une mesure de la capacité réelle de prise en charge, de la disponibilité, de la qualité ou de l'accessibilité effective des services ;
- aucun résultat provenant de Bruxelles Social n'est actuellement inclus dans les résultats analytiques du projet.

---

## Principes de traçabilité et de gestion des données

Le projet applique les principes suivants :

1. Les fichiers sources bruts sont conservés séparément des données nettoyées et transformées.
2. Les années de référence des indicateurs sont conservées explicitement.
3. Les jointures géographiques utilisent autant que possible des identifiants territoriaux stables plutôt que des noms.
4. Les valeurs manquantes sont conservées sauf lorsqu'une règle analytique documentée justifie un autre traitement.
5. Les définitions territoriales officielles sont distinguées des classifications analytiques préliminaires.
6. Les fichiers dérivés produits par le projet sont clairement distingués des données institutionnelles originales.
7. Les incertitudes et les cas territoriaux non résolus sont documentés plutôt que corrigés ou attribués arbitrairement.