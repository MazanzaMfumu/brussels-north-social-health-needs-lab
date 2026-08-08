from pathlib import Path

import geopandas as gpd
import pyogrio


ROOT = Path(__file__).resolve().parents[1]

URBIS_FILE = (
    ROOT
    / "data"
    / "raw"
    / "geography"
    / "UrbISVector_04000.gpkg"
)


if not URBIS_FILE.exists():
    raise FileNotFoundError(
        f"UrbIS GeoPackage not found: {URBIS_FILE}"
    )


print("\n" + "=" * 80)
print("URBIS VECTOR GEOPACKAGE")
print("=" * 80)

print("File:")
print(URBIS_FILE)


print("\nRelevant layers:")

layers = pyogrio.list_layers(
    URBIS_FILE
)

for layer_name, geometry_type in layers:
    if layer_name in {
        "MonitoringDistricts",
        "StatisticalSectors",
    }:
        print(
            f"- {layer_name}: {geometry_type}"
        )


for layer_name in [
    "MonitoringDistricts",
    "StatisticalSectors",
]:

    print("\n" + "=" * 80)
    print(layer_name.upper())
    print("=" * 80)

    gdf = gpd.read_file(
        URBIS_FILE,
        layer=layer_name,
    )

    print("Rows:", len(gdf))
    print("CRS:", gdf.crs)

    print("Columns:")
    print(gdf.columns.tolist())

    print("Geometry types:")
    print(
        gdf.geometry
        .geom_type
        .value_counts(dropna=False)
    )

    print(
        "Missing geometries:",
        gdf.geometry.isna().sum()
    )

    print(
        "Invalid geometries:",
        (~gdf.geometry.is_valid).sum()
    )

    print("\nFirst five rows:")
    print(
        gdf.drop(
            columns="geometry"
        )
        .head()
        .to_string(index=False)
    )