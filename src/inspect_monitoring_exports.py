from pathlib import Path
import pandas as pd

# ---------------------------------------------------------
# 1. Define project folders
# ---------------------------------------------------------

ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "data" / "raw"

# ---------------------------------------------------------
# 2. List the Monitoring des Quartiers raw files
# ---------------------------------------------------------

files = [
    "monitoring_brussels_vul_unemployment_2023.csv",
    "monitoring_brussels_vul_cpas_2023.csv",
    "monitoring_brussels_vul_bim_2024.csv",
]

# ---------------------------------------------------------
# 3. Inspect each CSV file
# ---------------------------------------------------------

for filename in files:

    file_path = RAW_DIR / filename

    print("\n" + "=" * 80)
    print(f"FILE: {filename}")
    print("=" * 80)

    # Check that the file actually exists
    if not file_path.exists():
        print(f"ERROR: File not found: {file_path}")
        continue

    try:
        # sep=None lets pandas try to detect the separator automatically.
        # engine="python" is required for this automatic detection.
        df = pd.read_csv(
            file_path,
            sep=None,
            engine="python",
            encoding="utf-8-sig"
        )

    except UnicodeDecodeError:
        # Fallback in case the CSV uses another common Windows encoding
        df = pd.read_csv(
            file_path,
            sep=None,
            engine="python",
            encoding="latin-1"
        )

    print("\nShape:")
    print(df.shape)

    print("\nColumns:")
    print(df.columns.tolist())

    print("\nData types:")
    print(df.dtypes)

    print("\nFirst five rows:")
    print(df.head())

    print("\nMissing values by column:")
    print(df.isna().sum())

    print("\nDuplicate rows:")
    print(df.duplicated().sum())