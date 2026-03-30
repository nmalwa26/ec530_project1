from __future__ import annotations

from pathlib import Path
import re
from typing import Any

import pandas as pd


def normalize_column_name(column_name: str) -> str:
    """
    Convert a CSV column name into a SQLite-friendly format
    """
    normalized = column_name.strip().lower()

    # Remove punctuation/special characters 
    normalized = re.sub(r"[^\w\s]", "", normalized)

    # Replace spaces with underscores
    normalized = re.sub(r"\s+", "_", normalized)

    return normalized


def infer_sqlite_type(values: list[Any]) -> str:
    """
    Infer an appropriate SQLite column type from a list of values.
    """
    # Remove null values 
    non_null_values = [v for v in values if pd.notna(v)]

    # If column is empty or all null, default to TEXT
    if not non_null_values:
        return "TEXT"

    all_integers = True
    all_numeric = True

    for value in non_null_values:
        # Boolean values should not be treated as numbers here
        if isinstance(value, bool):
            all_numeric = False
            all_integers = False
            break

        # If already an integer, continue checking
        if isinstance(value, int):
            continue

        # If float continue, but not if has a decimal (3.5)
        if isinstance(value, float):
            if not value.is_integer():
                all_integers = False
            continue

        # If it's a string, try converting to float (if "20")
        try:
            numeric_value = float(value)

            # If it has decimals, not an integer
            if not numeric_value.is_integer():
                all_integers = False

        except (ValueError, TypeError):
            # If conversion fails, it's text ("hello")
            all_numeric = False
            all_integers = False
            break

    # Final decision based on flags
    if all_integers:
        return "INTEGER"
    if all_numeric:
        return "REAL"

    return "TEXT"


def load_csv(file_path: str) -> dict[str, Any]:
    """
    Load a CSV file and convert it into structured data for the system
    """

    # Convert string path to Path object 
    path = Path(file_path)

    # Check that file exists
    if not path.exists():
        raise FileNotFoundError(f"CSV file not found: {file_path}")

    # Ensure file is actually a CSV
    if path.suffix.lower() != ".csv":
        raise ValueError(f"Expected a .csv file, got: {path.suffix}")

    # Load CSV into pandas DataFrame
    df = pd.read_csv(path)

    # Reject empty CSV files 
    if df.empty:
        raise ValueError("CSV file is empty.")

    # Store original column names
    original_columns = list(df.columns)

    # Normalize column names for database use
    normalized_columns = [normalize_column_name(col) for col in original_columns]

    # Check for duplicate columns after normalization
    if len(normalized_columns) != len(set(normalized_columns)):
        raise ValueError("CSV contains duplicate column names after normalization.")

    # Replace DataFrame column names with normalized versions
    df.columns = normalized_columns

    # Build column schema (name + inferred SQLite type)
    columns = []
    for col in df.columns:
        sqlite_type = infer_sqlite_type(df[col].tolist())

        columns.append({
            "name": col,
            "sqlite_type": sqlite_type
        })

    # Convert DataFrame rows into list of dictionaries (replace NaN with None for SQLite)
    rows = df.where(pd.notna(df), None).to_dict(orient="records")

    # Return structured result 
    return {
        "table_name": path.stem.lower(),  # file name without extension
        "columns": columns,
        "rows": rows,
        "row_count": len(rows)
    }