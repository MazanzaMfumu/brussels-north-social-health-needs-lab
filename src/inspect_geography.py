from pathlib import Path
import geopandas as gpd

ROOT = Path(__file__).resolve().parents[1]

file_path = (
    ROOT
    / "data"
    / "raw"
    / "geography"
    / "UrbAdm_StatisticalUnits.gml"
)

print("File exists:", file_path.exists())
print("File:", file_path)

gdf = gpd.read_file(file_path)

print("\nRows:")
print(len(gdf))

print("\nCRS:")
print(gdf.crs)

print("\nColumns:")
print(gdf.columns.tolist())

print("\nFirst five rows:")
print(gdf.head())

print("\nGeometry types:")
print(gdf.geometry.geom_type.value_counts())

print("\n" + "=" * 80)
print("KEY IDENTIFIER FIELDS")
print("=" * 80)

columns_to_inspect = [
    "gml_id",
    "identifier",
    "localId",
    "thematicId|ThematicIdentifier|identifier",
    "text",
]

available_columns = [
    col for col in columns_to_inspect
    if col in gdf.columns
]

print(
    gdf[available_columns]
    .head(20)
    .to_string(index=False)
)