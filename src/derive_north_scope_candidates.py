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

OUTPUT_FILE = (
    ROOT
    / "data"
    / "interim"
    / "north_scope_candidates.csv"
)

OUTPUT_FILE.parent.mkdir(
    parents=True,
    exist_ok=True,
)


# ============================================================
# 2. Official territorial references
# ============================================================

# Municipalities entirely included in Bassin Nord.
NORTH_FULL_COMMUNES = {
    "21003",  # Berchem-Sainte-Agathe
    "21008",  # Ganshoren
    "21010",  # Jette
    "21011",  # Koekelberg
}

# Bruxelles-Ville is only PARTLY included in Bassin Nord:
# Laeken, Neder-Over-Heembeek and Haren.
BRUSSELS_CITY = "21004"


# ============================================================
# 3. Read official UrbIS layers
# ============================================================

sectors = gpd.read_file(
    URBIS_FILE,
    layer="StatisticalSectors",
)

districts = gpd.read_file(
    URBIS_FILE,
    layer="MonitoringDistricts",
)


# ============================================================
# 4. Check required columns
# ============================================================

required_sector_columns = {
    "NISCODE",
    "MONITORINGDISTRICT_ID",
}

missing = (
    required_sector_columns
    - set(sectors.columns)
)

if missing:
    raise ValueError(
        f"Missing StatisticalSectors columns: {sorted(missing)}"
    )

required_district_columns = {
    "MDZONE",
    "NAMEFRE",
}

missing = (
    required_district_columns
    - set(districts.columns)
)

if missing:
    raise ValueError(
        f"Missing MonitoringDistricts columns: {sorted(missing)}"
    )


# ============================================================
# 5. Create geographic bridge
# ============================================================

sectors["niscode"] = (
    sectors["NISCODE"]
    .astype("string")
    .str.strip()
)

# First five characters of NISCODE = municipality NIS code.
sectors["municipality_nis"] = (
    sectors["niscode"]
    .str[:5]
)

sectors["territory_code"] = (
    pd.to_numeric(
        sectors["MONITORINGDISTRICT_ID"],
        errors="raise",
    )
    .astype(int)
)

districts["territory_code"] = (
    pd.to_numeric(
        districts["MDZONE"],
        errors="raise",
    )
    .astype(int)
)


# ============================================================
# 6. Summarise municipalities inside each Monitoring district
# ============================================================

summary = (
    sectors
    .groupby("territory_code", as_index=False)
    .agg(
        municipality_nis_codes=(
            "municipality_nis",
            lambda x: "|".join(
                sorted(set(x.dropna()))
            ),
        ),
        n_statistical_sectors=(
            "niscode",
            "nunique",
        ),
    )
)


# ============================================================
# 7. Candidate classification
# ============================================================

def classify_candidate(code_string):

    codes = set(
        code_string.split("|")
    )

    north_codes = (
        codes & NORTH_FULL_COMMUNES
    )

    outside_codes = (
        codes
        - NORTH_FULL_COMMUNES
        - {BRUSSELS_CITY}
    )

    has_brussels_city = (
        BRUSSELS_CITY in codes
    )

    # Entirely inside one or more whole Bassin Nord communes.
    if codes and codes <= NORTH_FULL_COMMUNES:
        return "CERTAIN_YES"

    # Completely outside the four whole North communes
    # and outside Bruxelles-Ville.
    if (
        not north_codes
        and not has_brussels_city
    ):
        return "CERTAIN_NO"

    # Bruxelles-Ville requires finer QSS validation.
    if has_brussels_city:

        if outside_codes:
            return "REVIEW_BRUSSELS_CITY_MIXED"

        return "REVIEW_BRUSSELS_CITY"

    # Monitoring district crosses a municipal boundary
    # between Bassin Nord and another basin.
    return "PARTIAL_MUNICIPAL_BOUNDARY"


summary["candidate_status"] = (
    summary["municipality_nis_codes"]
    .apply(classify_candidate)
)


# ============================================================
# 8. Add official Monitoring district names
# ============================================================

district_names = (
    districts[
        [
            "territory_code",
            "NAMEFRE",
        ]
    ]
    .rename(
        columns={
            "NAMEFRE": "territory_urbis_fr",
        }
    )
)


result = district_names.merge(
    summary,
    on="territory_code",
    how="left",
    validate="one_to_one",
)


# ============================================================
# 9. Integrity checks
# ============================================================

if len(result) != 145:
    raise ValueError(
        f"Expected 145 Monitoring districts, found {len(result)}."
    )

if result["territory_code"].duplicated().any():
    raise ValueError(
        "Duplicate Monitoring territory codes detected."
    )

if result["municipality_nis_codes"].isna().any():
    raise ValueError(
        "Some Monitoring districts have no StatisticalSector mapping."
    )


# ============================================================
# 10. Save diagnostic table
# ============================================================

result.to_csv(
    OUTPUT_FILE,
    index=False,
    encoding="utf-8-sig",
)


# ============================================================
# 11. Report
# ============================================================

print("\n" + "=" * 80)
print("BASSIN NORD CANDIDATE CLASSIFICATION")
print("=" * 80)

print("\nRows:")
print(len(result))

print("\nCandidate status:")
print(
    result["candidate_status"]
    .value_counts()
)

review = result[
    result["candidate_status"].isin(
        [
            "REVIEW_BRUSSELS_CITY",
            "REVIEW_BRUSSELS_CITY_MIXED",
            "PARTIAL_MUNICIPAL_BOUNDARY",
        ]
    )
]

print("\nTerritories requiring finer validation:")
print(
    review[
        [
            "territory_code",
            "territory_urbis_fr",
            "municipality_nis_codes",
            "candidate_status",
        ]
    ]
    .sort_values("territory_code")
    .to_string(index=False)
)

print("\nSaved to:")
print(OUTPUT_FILE)