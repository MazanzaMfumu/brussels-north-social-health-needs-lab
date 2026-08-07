# Data Sources

## 1. IBSA Population Projections

- Source: Institut Bruxellois de Statistique et d'Analyse (IBSA)
- Dataset: Projections démographiques communales bruxelloises 2026-2035
- Geographic level: municipality
- Period: 2025 baseline and 2026-2035 projections
- Variables: municipality, age, sex, population and projected population
- Licence: CC BY 4.0
- Raw data stored locally in: data/raw/
- Limitation: Brussels-City data cannot isolate Laeken, Neder-Over-Heembeek and Haren.

## 2. Monitoring des Quartiers

- Source: Monitoring des Quartiers – IBSA / perspective.brussels
- Download date: 7 August 2026
- Geographic level used in this project: neighbourhoods (Quartiers)
- Territorial coverage downloaded: all Brussels-Capital Region neighbourhoods
- Raw data stored locally in: data/raw/

### Indicators downloaded

1. Unemployment rate
   - Original indicator: Taux de chômage
   - Reference year: 2023
   - Unit: %
   - Raw file: data/raw/monitoring_unemployment_2023.csv

2. CPAS / RIS beneficiaries
   - Original indicator: Part des bénéficiaires d'un revenu du CPAS (RIS ou équivalent) dans la population
   - Reference year: 2023
   - Unit: %
   - Raw file: data/raw/monitoring_cpas_2023.csv

3. BIM beneficiaries
   - Original indicator: Part des bénéficiaires de l'intervention majorée dans la population totale
   - Reference year: 2024
   - Unit: %
   - Raw file: data/raw/monitoring_bim_2024.csv

### Methodological note

The indicators do not all refer to the same year:
unemployment and CPAS/RIS data refer to 2023, while BIM data refer to 2024.
The original reference year of each indicator is preserved in the analytical pipeline rather than artificially harmonised.

The complete set of Brussels neighbourhoods was downloaded.
The Brussels North study area will be defined later through a reproducible geographic filtering procedure rather than by manually selecting neighbourhoods during data extraction.

## 3. Statbel Statistical Sectors

- Source: Statbel
- Dataset: Statistical sectors 2025
- Format: GeoJSON
- Coordinate reference system: EPSG:3812
- Use: geographic boundaries and spatial analysis
- Raw data stored locally in: data/raw/

## 4. Bruxelles Social

- Source: Vivalis / Bruxelles Social
- Use: social-health organisations and services
- Implementation phase: phase 2