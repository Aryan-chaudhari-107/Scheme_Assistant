"""
load_data.py

Reads every scheme JSON file from data/schemes/ into a single pandas
DataFrame, prints it for a manual eyeball-check, and saves a consolidated
schemes.json file for downstream use (Module 2 RAG pipeline).

Usage:
    python src/load_data.py
"""

import json
from pathlib import Path

import pandas as pd

# data/schemes/ lives two levels up from this file (src/load_data.py -> repo root -> data/schemes)
SCHEMES_DIR = Path(__file__).resolve().parent.parent / "data" / "schemes"
OUTPUT_JSON = Path(__file__).resolve().parent.parent / "data" / "schemes.json"


def load_schemes(schemes_dir: Path = SCHEMES_DIR) -> pd.DataFrame:
    """Read all scheme JSON files in schemes_dir into a DataFrame."""
    records = []
    for file_path in sorted(schemes_dir.glob("*.json")):
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            data["_source_file"] = file_path.name
            records.append(data)

    if not records:
        raise FileNotFoundError(f"No JSON scheme files found in {schemes_dir}")

    return pd.DataFrame(records)


def main():
    df = load_schemes()

    print(f"Loaded {len(df)} schemes from {SCHEMES_DIR}\n")
    print("Columns:", list(df.columns))
    print()
    print(df[["scheme_id", "name", "category", "state"]].to_string(index=False))

    # Save a consolidated dataset for reuse (drop internal helper column first)
    records = df.drop(columns=["_source_file"]).to_dict(orient="records")
    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=2, ensure_ascii=False)

    print(f"\nConsolidated dataset saved to: {OUTPUT_JSON}")


if __name__ == "__main__":
    main()