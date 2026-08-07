from pathlib import Path

import geopandas as gpd


ROOT = Path(__file__).resolve().parents[1]

PROCESSED_DIR = ROOT / "data" / "processed"

INPUT_FILE = (
    PROCESSED_DIR
    / "brussels_monitoring_vulnerability.geojson"
)

OUTPUT_FILE = (
    PROCESSED_DIR
    / "brussels_north_monitoring_crosswalk.csv"
)


if not INPUT_FILE.exists():
    raise FileNotFoundError(
        f"Input file not found: {INPUT_FILE}"
    )


if OUTPUT_FILE.exists():
    raise FileExistsError(
        f"{OUTPUT_FILE.name} already exists. "
        "It was not overwritten to protect manual validation work."
    )


gdf = gpd.read_file(INPUT_FILE)

required_columns = {
    "territory_code",
    "territory",
    "geometry",
}

missing_columns = required_columns - set(gdf.columns)

if missing_columns:
    raise ValueError(
        "Required columns are missing: "
        f"{sorted(missing_columns)}"
    )


if len(gdf) != 145:
    raise ValueError(
        "Expected 145 validated Monitoring territories, "
        f"but found {len(gdf)}."
    )


if gdf["territory_code"].duplicated().any():
    raise ValueError(
        "Duplicate territory codes detected."
    )


crosswalk = (
    gdf[
        [
            "territory_code",
            "territory",
        ]
    ]
    .sort_values("territory_code")
    .reset_index(drop=True)
    .copy()
)


crosswalk["in_bassin_nord"] = "TO_VALIDATE"

crosswalk["target_basin"] = "Bassin Nord"

crosswalk["mapping_method"] = "TO_VALIDATE"

crosswalk["mapping_note"] = ""


crosswalk.to_csv(
    OUTPUT_FILE,
    index=False,
    encoding="utf-8-sig",
)


print(
    "Crosswalk template created:"
)

print(
    OUTPUT_FILE
)

print(
    "Rows:",
    len(crosswalk),
)

print(
    crosswalk.head()
)