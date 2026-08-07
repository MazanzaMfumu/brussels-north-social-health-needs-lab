from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd


# ============================================================
# 1. Project paths
# ============================================================

ROOT = Path(__file__).resolve().parents[1]

RAW_DIR = ROOT / "data" / "raw"
PROCESSED_DIR = ROOT / "data" / "processed"

PROCESSED_DIR.mkdir(
    parents=True,
    exist_ok=True
)

GML_FILE = (
    RAW_DIR
    / "geography"
    / "UrbAdm_StatisticalUnits.gml"
)

VULNERABILITY_FILE = (
    PROCESSED_DIR
    / "territorial_vulnerability_indicators.csv"
)


# ============================================================
# 2. Read source datasets
# ============================================================

geography = gpd.read_file(
    GML_FILE
)

vulnerability = pd.read_csv(
    VULNERABILITY_FILE
)


# ============================================================
# 3. Create common territory code
# ============================================================

THEMATIC_ID_COLUMN = (
    "thematicId|ThematicIdentifier|identifier"
)

geography["territory_code"] = pd.to_numeric(
    geography[THEMATIC_ID_COLUMN],
    errors="raise"
).astype(int)

vulnerability["territory_code"] = pd.to_numeric(
    vulnerability["territory_code"],
    errors="raise"
).astype(int)


# ============================================================
# 4. Extract French and Dutch geographic names
# ============================================================

def extract_names(value):
    """
    Extract French and Dutch Monitoring district names
    from the UrbIS multilingual 'text' field.
    """

    if isinstance(value, (list, tuple, np.ndarray)):
        values = list(value)

        name_fr = (
            str(values[0]).strip()
            if len(values) >= 1
            else None
        )

        name_nl = (
            str(values[1]).strip()
            if len(values) >= 2
            else None
        )

        return pd.Series(
            [name_fr, name_nl]
        )

    # Fallback if the value is not stored as a list-like object
    if pd.isna(value):
        return pd.Series(
            [None, None]
        )

    text = str(value).strip()

    return pd.Series(
        [text, None]
    )


geography[
    [
        "territory_name_urbis_fr",
        "territory_name_urbis_nl",
    ]
] = geography["text"].apply(
    extract_names
)


# ============================================================
# 5. Keep only useful geographic variables
# ============================================================

geography_clean = geography[
    [
        "territory_code",
        "territory_name_urbis_fr",
        "territory_name_urbis_nl",
        "geometry",
    ]
].copy()


# ============================================================
# 6. Geographic quality checks
# ============================================================

assert len(geography_clean) == 145

assert (
    geography_clean[
        "territory_code"
    ].is_unique
)

assert (
    geography_clean[
        "territory_code"
    ].notna().all()
)

assert (
    geography_clean.geometry.notna().all()
)

print(
    "Source CRS:",
    geography_clean.crs
)

print(
    "Invalid geometries:",
    (~geography_clean.geometry.is_valid).sum()
)


# ============================================================
# 7. Convert to WGS84 for web mapping
# ============================================================

geography_clean = (
    geography_clean
    .to_crs(epsg=4326)
)

print(
    "Output CRS:",
    geography_clean.crs
)


# ============================================================
# 8. Merge geography with Monitoring indicators
# ============================================================

geo_vulnerability = geography_clean.merge(
    vulnerability,
    on="territory_code",
    how="inner",
    validate="one_to_one",
)


# ============================================================
# 9. Final quality checks
# ============================================================

assert len(geo_vulnerability) == 145

assert (
    geo_vulnerability[
        "territory_code"
    ].is_unique
)

assert (
    geo_vulnerability.geometry.notna().all()
)


# ============================================================
# 10. Put analytical territory name first
# ============================================================

final_columns = [
    "territory_code",
    "territory",
    "territory_name_urbis_fr",
    "territory_name_urbis_nl",
    "territory_level",
    "unemployment_rate",
    "unemployment_year",
    "cpas_rate",
    "cpas_year",
    "bim_rate",
    "bim_year",
    "geometry",
]

geo_vulnerability = geo_vulnerability[
    final_columns
]


# ============================================================
# 11. Save clean geographic boundaries
# ============================================================

boundaries_file = (
    PROCESSED_DIR
    / "brussels_monitoring_boundaries.geojson"
)

geography_clean.to_file(
    boundaries_file,
    driver="GeoJSON"
)


# ============================================================
# 12. Save geographic vulnerability dataset
# ============================================================

output_file = (
    PROCESSED_DIR
    / "brussels_monitoring_vulnerability.geojson"
)

geo_vulnerability.to_file(
    output_file,
    driver="GeoJSON"
)


# ============================================================
# 13. Final report
# ============================================================

print("\n" + "=" * 80)
print("GEOGRAPHY PREPARATION COMPLETED")
print("=" * 80)

print(
    "Monitoring boundaries:",
    len(geography_clean)
)

print(
    "Merged territories:",
    len(geo_vulnerability)
)

print(
    "Final CRS:",
    geo_vulnerability.crs
)

print(
    "Geometry types:"
)

print(
    geo_vulnerability
    .geometry
    .geom_type
    .value_counts()
)

print(
    "\nFirst five territories:"
)

print(
    geo_vulnerability[
        [
            "territory_code",
            "territory",
            "territory_name_urbis_fr",
            "territory_name_urbis_nl",
        ]
    ]
    .head()
    .to_string(index=False)
)

print(
    "\nSaved boundaries to:"
)

print(boundaries_file)

print(
    "\nSaved vulnerability geography to:"
)

print(output_file)