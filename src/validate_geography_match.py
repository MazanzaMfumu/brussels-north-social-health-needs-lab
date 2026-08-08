from pathlib import Path

import geopandas as gpd
import pandas as pd


# ============================================================
# 1. Project paths
# ============================================================

ROOT = Path(__file__).resolve().parents[1]

URBIS_FILE = (
    ROOT
    / "data"
    / "raw"
    / "geography"
    / "UrbISVector_04000.gpkg"
)

VULNERABILITY_FILE = (
    ROOT
    / "data"
    / "processed"
    / "territorial_vulnerability_indicators.csv"
)


# ============================================================
# 2. Check input files
# ============================================================

if not URBIS_FILE.exists():
    raise FileNotFoundError(
        f"UrbIS GeoPackage not found: {URBIS_FILE}"
    )

if not VULNERABILITY_FILE.exists():
    raise FileNotFoundError(
        f"Vulnerability file not found: {VULNERABILITY_FILE}"
    )


# ============================================================
# 3. Read datasets
# ============================================================

geography = gpd.read_file(
    URBIS_FILE,
    layer="MonitoringDistricts",
)

vulnerability = pd.read_csv(
    VULNERABILITY_FILE
)


# ============================================================
# 4. Basic row counts
# ============================================================

print("\n" + "=" * 80)
print("ROW COUNT COMPARISON")
print("=" * 80)

print("Geographic units:", len(geography))
print("Monitoring territories:", len(vulnerability))


# ============================================================
# 5. Check expected UrbIS columns
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
        "Missing expected UrbIS columns: "
        f"{sorted(missing_columns)}"
    )


# ============================================================
# 6. Standardise geographic territory code
# ============================================================

geography["territory_code"] = (
    pd.to_numeric(
        geography["MDZONE"],
        errors="raise",
    )
    .astype(int)
)

vulnerability["territory_code"] = (
    pd.to_numeric(
        vulnerability["territory_code"],
        errors="raise",
    )
    .astype(int)
)


# ============================================================
# 7. Geographic quality checks
# ============================================================

print("\n" + "=" * 80)
print("GEOGRAPHIC CODE QUALITY")
print("=" * 80)

print(
    "Unique geographic codes:",
    geography["territory_code"].nunique()
)

print(
    "Missing geographic codes:",
    geography["territory_code"].isna().sum()
)

print(
    "Duplicated geographic codes:",
    geography["territory_code"].duplicated().sum()
)

print(
    "Invalid geometries:",
    (~geography.geometry.is_valid).sum()
)

print(
    "Empty geometries:",
    geography.geometry.is_empty.sum()
)

print(
    "CRS:",
    geography.crs
)

print("\nFirst geographic codes:")

print(
    geography[
        [
            "territory_code",
            "NAMEFRE",
            "NAMEDUT",
        ]
    ]
    .head(20)
    .to_string(index=False)
)


# ============================================================
# 8. Monitoring data quality checks
# ============================================================

print("\n" + "=" * 80)
print("MONITORING CODE QUALITY")
print("=" * 80)

print(
    "Unique Monitoring codes:",
    vulnerability["territory_code"].nunique()
)

print(
    "Missing Monitoring codes:",
    vulnerability["territory_code"].isna().sum()
)

print(
    "Duplicated Monitoring codes:",
    vulnerability["territory_code"].duplicated().sum()
)


# ============================================================
# 9. Compare exact code sets
# ============================================================

geo_codes = set(
    geography["territory_code"]
)

monitoring_codes = set(
    vulnerability["territory_code"]
)

only_in_geography = (
    geo_codes - monitoring_codes
)

only_in_monitoring = (
    monitoring_codes - geo_codes
)


print("\n" + "=" * 80)
print("CODE SET COMPARISON")
print("=" * 80)

print(
    "Codes in geography:",
    len(geo_codes)
)

print(
    "Codes in Monitoring data:",
    len(monitoring_codes)
)

print(
    "Codes only in geography:",
    sorted(only_in_geography)
)

print(
    "Codes only in Monitoring data:",
    sorted(only_in_monitoring)
)

print(
    "Exact code-set match:",
    geo_codes == monitoring_codes
)


# ============================================================
# 10. Hard validation
# ============================================================

EXPECTED_TERRITORIES = 145

if len(geography) != EXPECTED_TERRITORIES:
    raise ValueError(
        f"Expected {EXPECTED_TERRITORIES} geographic units, "
        f"found {len(geography)}."
    )

if len(vulnerability) != EXPECTED_TERRITORIES:
    raise ValueError(
        f"Expected {EXPECTED_TERRITORIES} Monitoring territories, "
        f"found {len(vulnerability)}."
    )

if geography["territory_code"].duplicated().any():
    raise ValueError(
        "Duplicated geographic territory codes detected."
    )

if vulnerability["territory_code"].duplicated().any():
    raise ValueError(
        "Duplicated Monitoring territory codes detected."
    )

if only_in_geography or only_in_monitoring:
    raise ValueError(
        "Geographic and Monitoring territory codes "
        "do not correspond exactly."
    )

if geography.geometry.isna().any():
    raise ValueError(
        "Missing geographic geometries detected."
    )

if geography.geometry.is_empty.any():
    raise ValueError(
        "Empty geographic geometries detected."
    )

if (~geography.geometry.is_valid).any():
    raise ValueError(
        "Invalid geographic geometries detected."
    )


# ============================================================
# 11. Test one-to-one merge
# ============================================================

test_merge = vulnerability.merge(
    geography[
        [
            "territory_code",
            "NAMEFRE",
            "NAMEDUT",
        ]
    ],
    on="territory_code",
    how="outer",
    indicator=True,
    validate="one_to_one",
)


print("\n" + "=" * 80)
print("MERGE VALIDATION")
print("=" * 80)

print(
    test_merge["_merge"].value_counts()
)


if not (
    test_merge["_merge"] == "both"
).all():
    raise ValueError(
        "Some territories failed the one-to-one merge."
    )


# ============================================================
# 12. Show first matched rows
# ============================================================

print("\nFirst matched rows:")

print(
    test_merge[
        [
            "territory_code",
            "territory",
            "NAMEFRE",
            "NAMEDUT",
            "_merge",
        ]
    ]
    .head(20)
    .to_string(index=False)
)


print("\n" + "=" * 80)
print("GEOGRAPHY MATCH VALIDATION PASSED")
print("=" * 80)