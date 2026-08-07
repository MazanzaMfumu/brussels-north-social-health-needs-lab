from pathlib import Path

import geopandas as gpd
import pandas as pd


# ============================================================
# 1. Project paths
# ============================================================

ROOT = Path(__file__).resolve().parents[1]

GML_FILE = (
    ROOT
    / "data"
    / "raw"
    / "geography"
    / "UrbAdm_StatisticalUnits.gml"
)

VULNERABILITY_FILE = (
    ROOT
    / "data"
    / "processed"
    / "territorial_vulnerability_indicators.csv"
)


# ============================================================
# 2. Read datasets
# ============================================================

geography = gpd.read_file(GML_FILE)

vulnerability = pd.read_csv(
    VULNERABILITY_FILE
)


# ============================================================
# 3. Basic row counts
# ============================================================

print("\n" + "=" * 80)
print("ROW COUNT COMPARISON")
print("=" * 80)

print("Geographic units:", len(geography))
print("Monitoring territories:", len(vulnerability))


# ============================================================
# 4. Build a clean geographic territory code
# ============================================================

THEMATIC_ID_COLUMN = (
    "thematicId|ThematicIdentifier|identifier"
)

geography["territory_code"] = pd.to_numeric(
    geography[THEMATIC_ID_COLUMN],
    errors="coerce"
).astype("Int64")


# ============================================================
# 5. Standardise Monitoring territory code
# ============================================================

vulnerability["territory_code"] = pd.to_numeric(
    vulnerability["territory_code"],
    errors="coerce"
).astype("Int64")


# ============================================================
# 6. Quality checks on geographic codes
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

print("\nFirst geographic codes:")

print(
    geography[
        [
            "gml_id",
            "territory_code",
            "text",
        ]
    ]
    .head(20)
    .to_string(index=False)
)


# ============================================================
# 7. Quality checks on Monitoring codes
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
# 8. Compare exact code sets
# ============================================================

geo_codes = set(
    geography["territory_code"]
    .dropna()
    .astype(int)
)

monitoring_codes = set(
    vulnerability["territory_code"]
    .dropna()
    .astype(int)
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
    "Exact code-set match:",
    geo_codes == monitoring_codes
)


# ============================================================
# 9. Show differences if any
# ============================================================

only_in_geography = (
    geo_codes - monitoring_codes
)

only_in_monitoring = (
    monitoring_codes - geo_codes
)

print("\nCodes only in geography:")
print(sorted(only_in_geography))

print("\nCodes only in Monitoring data:")
print(sorted(only_in_monitoring))


# ============================================================
# 10. Test one-to-one merge by territory code
# ============================================================

test_merge = vulnerability.merge(
    geography[
        [
            "territory_code",
            "gml_id",
            "text",
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


# ============================================================
# 11. Show first matched rows
# ============================================================

print("\nFirst matched rows:")

print(
    test_merge[
        [
            "territory_code",
            "territory",
            "text",
            "_merge",
        ]
    ]
    .head(20)
    .to_string(index=False)
)