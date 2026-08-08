# Brussels North Social-Health Needs & Network Lab

Analyse territoriale des besoins sociaux et de santé, de la vulnérabilité et du périmètre géographique du nord de Bruxelles, fondée sur un traitement reproductible de données ouvertes officielles bruxelloises.

**Résumé —** Projet portfolio indépendant visant à explorer comment des données territoriales ouvertes peuvent soutenir un état des lieux des besoins sociaux et de santé, la connaissance du territoire et, à terme, l’analyse de l’offre social-santé dans le Bassin Nord de Bruxelles.

> **Statut :** version portfolio v0.1 — vulnérabilité territoriale et géographie Monitoring validées ; validation définitive du périmètre du Bassin Nord en attente du référentiel officiel des Quartiers du Care / Quartiers Social-Santé (QSS).

## Objectif du projet

Le projet étudie comment les données territoriales peuvent contribuer à :

* évaluer les besoins territoriaux ;
* identifier les profils de vulnérabilité sociale ;
* définir de manière transparente un périmètre géographique opérationnel ;
* préparer de futures analyses de l’accessibilité de l’offre social-santé ;
* formuler des questions fondées sur les données pouvant alimenter la concertation professionnelle.

Le projet n’a pas vocation à remplacer la connaissance du terrain ni l’évaluation des professionnels.

Les indicateurs quantitatifs sont considérés comme des **signaux à investiguer**, et non comme des conclusions définitives sur les besoins locaux ou l’adéquation de l’offre de services.

## Contexte territorial

La zone cible est le **Brussels North / Bassin Nord**.

Les sources institutionnelles décrivent ce bassin comme couvrant Berchem-Sainte-Agathe, Ganshoren, Jette et Koekelberg, ainsi que Laeken, Neder-Over-Heembeek et Haren au sein de la Ville de Bruxelles.

Un enjeu méthodologique majeur réside dans le fait que les **quartiers Monitoring** et les **Quartiers Social-Santé officiels (QSS)** correspondent à deux systèmes territoriaux différents.

Le projet n’attribue donc pas les quartiers Monitoring ambigus au Bassin Nord uniquement sur la base de leur nom ou d’une interprétation visuelle.

## État actuel du projet

### Réalisé

* Nettoyage et harmonisation des exports Monitoring relatifs au chômage, au CPAS et au BIM.
* Validation de 145 codes territoriaux Monitoring.
* Intégration du GeoPackage officiel UrbIS Vector.
* Validation de 145 géométries `MonitoringDistrict`.
* Établissement d’une correspondance exacte un-à-un entre :

`MonitoringDistricts.MDZONE`

et

`territorial_vulnerability_indicators.territory_code`.

* Génération des sorties géographiques destinées au Web en EPSG:4326.
* Construction d’un premier pont entre secteurs statistiques et quartiers Monitoring.
* Production d’une classification candidate du Bassin Nord.

### Référentiel officiel encore attendu

La correspondance définitive avec le Bassin Nord n’est volontairement pas considérée comme terminée.

Un référentiel officiel permettant de relier les secteurs statistiques / QSS aux cinq bassins social-santé a été demandé aux institutions bruxelloises compétentes en matière de données.

En attendant ce référentiel, les territoires ambigus restent explicitement classés comme `REVIEW` ou `PARTIAL`, au lieu d’être attribués sur la base d’une règle arbitraire.

## Sources de données

| Source                   | Utilisation                                                               |
| ------------------------ | ------------------------------------------------------------------------- |
| Monitoring des Quartiers | Indicateurs de chômage, CPAS et BIM                                       |
| UrbIS Vector             | Géométries `MonitoringDistricts` et `StatisticalSectors`                  |
| Référentiel officiel QSS | Demandé / en attente pour la délimitation définitive du Bassin Nord       |
| Source de population     | Documentée dans le notebook population et dans la documentation du projet |

Les jeux de données bruts officiels ne sont pas présentés comme des données produites par l’auteur du projet.

La provenance des sources, les années de référence et les limites des données doivent être consultées dans la documentation associée.

## Indicateurs

La couche actuelle de vulnérabilité repose sur trois indicateurs :

| Indicateur                                             | Année de référence |
| ------------------------------------------------------ | -----------------: |
| Taux de chômage                                        |               2023 |
| Part de la population bénéficiant d’un revenu du CPAS  |               2023 |
| Part des bénéficiaires de l’intervention majorée — BIM |               2024 |

Les valeurs manquantes sont conservées comme valeurs manquantes.

Elles ne sont jamais remplacées par zéro.

Aucun score composite de vulnérabilité n’est produit à ce stade, car la couverture des indicateurs, leurs années de référence et leurs corrélations doivent être examinées avant de définir une règle d’agrégation.

## Qualité des données

La géographie Monitoring comprend **145 territoires validés**.

La jointure géographique est de type **un-à-un**.

Aucune géométrie Monitoring n’est manquante, vide ou invalide.

La disponibilité des indicateurs reste toutefois incomplète :

* 117 quartiers Monitoring disposent des trois indicateurs actuels de vulnérabilité ;
* 28 présentent au moins un indicateur manquant ;
* 22 ne disposent d’aucun des trois indicateurs.

Ces valeurs manquantes sont documentées et ne sont pas imputées.

## Classification préliminaire du périmètre Brussels North

La procédure préliminaire utilise les secteurs statistiques comme pont géographique entre les codes NIS communaux et les quartiers Monitoring.

Résultats candidats actuels :

| Statut candidat              | Nombre de quartiers Monitoring |
| ---------------------------- | -----------------------------: |
| `CERTAIN_YES`                |                             12 |
| `CERTAIN_NO`                 |                             96 |
| `REVIEW_BRUSSELS_CITY`       |                             21 |
| `REVIEW_BRUSSELS_CITY_MIXED` |                             14 |
| `PARTIAL_MUNICIPAL_BOUNDARY` |                              2 |

Ces statuts constituent des **sorties diagnostiques** et non la correspondance officielle définitive avec le Bassin Nord.

En particulier, les quartiers Monitoring comprenant certaines parties de la Ville de Bruxelles ou franchissant des limites communales sont volontairement laissés en attente d’une validation plus fine.

## Pipeline de traitement

```text
Exports bruts Monitoring
        |
        v
prepare_vulnerability.py
        |
        v
territorial_vulnerability_indicators.csv
        |
        +-----------------------------+
        |                             |
        v                             v
UrbIS MonitoringDistricts     UrbIS StatisticalSectors
        |                             |
        v                             v
validate_geography_match.py   derive_north_scope_candidates.py
        |                             |
        v                             v
prepare_geography.py          north_scope_candidates.csv
        |                             |
        v                             v
Vulnérabilité Monitoring      validation officielle QSS
GeoJSON                       en attente
                                      |
                                      v
                              périmètre final
                              Brussels North
```

## Reproductibilité

Créez et activez un environnement virtuel Python, installez les dépendances figurant dans `requirements.txt`, puis exécutez les scripts de traitement depuis la racine du dépôt.

Séquence principale :

```powershell
.\.venv\Scripts\python.exe src\prepare_vulnerability.py
```

```powershell
.\.venv\Scripts\python.exe src\inspect_geography.py
```

```powershell
.\.venv\Scripts\python.exe src\validate_geography_match.py
```

```powershell
.\.venv\Scripts\python.exe src\prepare_geography.py
```

```powershell
.\.venv\Scripts\python.exe src\derive_north_scope_candidates.py
```

L’utilitaire de création du modèle de correspondance est conçu comme un outil d’initialisation à exécuter une seule fois et ne remplace pas un travail de validation manuelle existant.

## Notebooks

### `01_population_profile.ipynb`

Explore le contexte démographique.

### `02_vulnerability_profile.ipynb`

Analyse les indicateurs de vulnérabilité sociale.

### `03_geographic_scope.ipynb`

Documente le raisonnement géographique et le processus de validation territoriale.

## Structure du dépôt

```text
app/              application interactive prévue
data/             données brutes, intermédiaires et traitées
docs/             documentation méthodologique et sources de données
notebooks/        notebooks d’exploration, d’analyse et de validation géographique
outputs/          figures, cartes et rapports générés
src/              scripts Python reproductibles de préparation et de validation
tests/            tests et contrôles automatisés de qualité
.gitignore        règles d’exclusion des fichiers locaux et temporaires
README.md         présentation générale et documentation principale du projet
requirements.txt  dépendances Python nécessaires à la reproductibilité
```

## Principes méthodologiques

* Le projet sépare les données `raw`, `interim` et `processed`.
* Les jointures utilisent des identifiants territoriaux stables plutôt que les noms des territoires.
* Les relations géographiques sont validées avant tout filtrage.
* Les valeurs manquantes des indicateurs sont conservées.
* Les attributions ambiguës au Bassin Nord restent explicitement identifiées.
* Les quartiers Monitoring ne sont pas présentés comme des QSS officiels.
* Les classifications préliminaires sont clairement séparées des sorties territoriales définitives.

## Limites actuelles

Le référentiel officiel permettant de relier les QSS au Bassin Nord est toujours en attente.

Les quartiers Monitoring et les QSS ne possèdent pas des limites territoriales identiques.

Les trois indicateurs de vulnérabilité utilisent deux années de référence différentes.

Certains territoires présentent des valeurs d’indicateurs indisponibles.

Les éléments suivants ne sont pas encore modélisés :

* le nombre actuel de services ;
* la capacité des services ;
* l’accessibilité linguistique ;
* la continuité des soins.

Le projet décrit donc actuellement la vulnérabilité territoriale et l’incertitude géographique.

Il **ne mesure pas encore l’adéquation ni la qualité de l’offre social-santé**.

## Prochaine phase

Une fois le référentiel officiel QSS disponible, le projet permettra de :

1. valider la correspondance définitive entre secteurs statistiques, QSS et bassins ;
2. classifier les quartiers Monitoring comme situés à l’intérieur, à l’extérieur ou partiellement à l’intérieur du Bassin Nord ;
3. générer le périmètre validé de Brussels North ;
4. produire un jeu de données de vulnérabilité spécifique au Bassin Nord ;
5. intégrer ensuite des données relatives à l’offre de services social-santé afin d’analyser l’accessibilité et la relation entre besoins et ressources.

## Avertissement

Il s’agit d’un **projet portfolio indépendant à visée méthodologique**.

Il n’est ni produit, ni commandité, ni validé par Brusano, Vivalis, Perspective.brussels ou par les institutions fournissant les jeux de données sources.

Toute classification géographique préliminaire présentée dans ce dépôt ne doit donc pas être interprétée comme une délimitation institutionnelle officielle.
