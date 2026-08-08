from pathlib import Path

import geopandas as gpd
import pandas as pd


# ============================================================
# 1. Project paths
# ============================================================

ROOT = Path(__file__).resolve().parents[1]

RAW_DIR = ROOT / "data" / "raw"
PROCESSED_DIR = ROOT / "data" / "processed"

PROCESSED_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


URBIS_FILE = (
    RAW_DIR
    / "geography"
    / "UrbISVector_04000.gpkg"
)

VULNERABILITY_FILE = (
    PROCESSED_DIR
    / "territorial_vulnerability_indicators.csv"
)


# ============================================================
# 2. Required inputs
# ============================================================

if not URBIS_FILE.exists():
    raise FileNotFoundError(
        f"UrbIS GeoPackage not found: {URBIS_FILE}"
    )

if not VULNERABILITY_FILE.exists():
    raise FileNotFoundError(
        f"Vulnerability table not found: {VULNERABILITY_FILE}"
    )


# ============================================================
# 3. Read official Monitoring district geography
# ============================================================

geography = gpd.read_file(
    URBIS_FILE,
    layer="MonitoringDistricts",
)

print("\nMonitoringDistricts loaded.")
print("Rows:", len(geography))
print("Source CRS:", geography.crs)
print("Columns:", geography.columns.tolist())


# ============================================================
# 4. Check expected UrbIS structure
# ============================================================

required_columns = {
    "MDZONE",
    "NAMEFRE",
    "NAMEDUT",
    "geometry",
}

missing_columns = (
    required_columns
    - set(geography.columns)
)

if missing_columns:
    raise ValueError(
        "Missing expected columns in MonitoringDistricts: "
        f"{sorted(missing_columns)}"
    )


# ============================================================
# 5. Keep and standardise geographic variables
# ============================================================

geography_clean = geography[
    [
        "MDZONE",
        "NAMEFRE",
        "NAMEDUT",
        "geometry",
    ]
].copy()

geography_clean = geography_clean.rename(
    columns={
        "MDZONE": "territory_code",
        "NAMEFRE": "territory_name_urbis_fr",
        "NAMEDUT": "territory_name_urbis_nl",
    }
)


# ============================================================
# 6. Standardise territory code
# ============================================================

geography_clean["territory_code"] = (
    pd.to_numeric(
        geography_clean["territory_code"],
        errors="raise",
    )
    .astype(int)
)


# ============================================================
# 7. Geographic quality controls
# ============================================================

EXPECTED_TERRITORIES = 145

if len(geography_clean) != EXPECTED_TERRITORIES:
    raise ValueError(
        f"Expected {EXPECTED_TERRITORIES} Monitoring districts, "
        f"but found {len(geography_clean)}."
    )

if not geography_clean["territory_code"].is_unique:
    raise ValueError(
        "Duplicate MDZONE / territory_code values detected."
    )

if geography_clean["territory_code"].isna().any():
    raise ValueError(
        "Missing territory_code values detected."
    )

if geography_clean.geometry.isna().any():
    raise ValueError(
        "Missing Monitoring district geometries detected."
    )

if geography_clean.geometry.is_empty.any():
    raise ValueError(
        "Empty Monitoring district geometries detected."
    )

invalid_count = (
    ~geography_clean.geometry.is_valid
).sum()

if invalid_count != 0:
    raise ValueError(
        f"{invalid_count} invalid geometries detected."
    )

if (
    geography_clean.crs is None
    or geography_clean.crs.to_epsg() != 31370
):
    raise ValueError(
        "Unexpected source CRS. "
        f"Expected EPSG:31370, got {geography_clean.crs}."
    )

print("Unique territory codes:",
      geography_clean["territory_code"].nunique())

print("Invalid geometries:", invalid_count)


# ============================================================
# 8. Read territorial vulnerability indicators
# ============================================================

vulnerability = pd.read_csv(
    VULNERABILITY_FILE
)

if len(vulnerability) != EXPECTED_TERRITORIES:
    raise ValueError(
        f"Expected {EXPECTED_TERRITORIES} vulnerability rows, "
        f"but found {len(vulnerability)}."
    )

vulnerability["territory_code"] = (
    pd.to_numeric(
        vulnerability["territory_code"],
        errors="raise",
    )
    .astype(int)
)

if not vulnerability["territory_code"].is_unique:
    raise ValueError(
        "Duplicate territory_code values "
        "in vulnerability table."
    )


# ============================================================
# 9. Prove exact geographic correspondence
# ============================================================

geo_codes = set(
    geography_clean["territory_code"]
)

vulnerability_codes = set(
    vulnerability["territory_code"]
)

missing_in_geography = sorted(
    vulnerability_codes - geo_codes
)

missing_in_vulnerability = sorted(
    geo_codes - vulnerability_codes
)

print(
    "\nCodes missing from geography:",
    missing_in_geography,
)

print(
    "Codes missing from vulnerability:",
    missing_in_vulnerability,
)


if missing_in_geography or missing_in_vulnerability:
    raise ValueError(
        "Territorial codes do not correspond exactly "
        "between UrbIS and vulnerability data."
    )

print(
    "Territorial correspondence: PERFECT MATCH"
)


# ============================================================
# 10. Merge geography and vulnerability
# ============================================================

geo_vulnerability = geography_clean.merge(
    vulnerability,
    on="territory_code",
    how="left",
    validate="one_to_one",
)


# ============================================================
# 11. Final merge checks
# ============================================================

if len(geo_vulnerability) != EXPECTED_TERRITORIES:
    raise ValueError(
        "Unexpected number of territories after merge."
    )

if not geo_vulnerability["territory_code"].is_unique:
    raise ValueError(
        "territory_code is not unique after merge."
    )

if geo_vulnerability.geometry.isna().any():
    raise ValueError(
        "Missing geometries after merge."
    )


# ============================================================
# 12. Convert to WGS84 for web mapping
# ============================================================

geography_web = geography_clean.to_crs(
    epsg=4326
)

geo_vulnerability_web = geo_vulnerability.to_crs(
    epsg=4326
)

print(
    "\nWeb output CRS:",
    geo_vulnerability_web.crs,
)


# ============================================================
# 13. Final analytical column order
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

geo_vulnerability_web = (
    geo_vulnerability_web[
        final_columns
    ]
)


# ============================================================
# 14. Save Monitoring boundaries
# ============================================================

boundaries_file = (
    PROCESSED_DIR
    / "brussels_monitoring_boundaries.geojson"
)

geography_web.to_file(
    boundaries_file,
    driver="GeoJSON",
)


# ============================================================
# 15. Save vulnerability geography
# ============================================================

output_file = (
    PROCESSED_DIR
    / "brussels_monitoring_vulnerability.geojson"
)

geo_vulnerability_web.to_file(
    output_file,
    driver="GeoJSON",
)


# ============================================================
# 16. Final report
# ============================================================

print("\n" + "=" * 72)
print("GEOGRAPHY PREPARATION COMPLETED")
print("=" * 72)

print(
    "Monitoring boundaries:",
    len(geography_web),
)

print(
    "Merged territories:",
    len(geo_vulnerability_web),
)

print(
    "Final CRS:",
    geo_vulnerability_web.crs,
)

print("\nGeometry types:")

print(
    geo_vulnerability_web
    .geometry
    .geom_type
    .value_counts()
)

print("\nFirst five territories:")

print(
    geo_vulnerability_web[
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