from pathlib import Path
from typing import Any

def load_csv(file_path: str) -> dict[str, Any]:
    """
    Read a CSV file and return structured data needed for schema creation
    and database insertion.
    """
    pass


def normalize_column_name(column_name: str) -> str:
    """
    Normalize a CSV column name into a database-friendly format.
    Example: 'First Name' -> 'first_name'
    """
    pass


def infer_sqlite_type(values: list[Any]) -> str:
    """
    Infer an SQLite type from a column's values.
    Returns one of: TEXT, INTEGER, REAL
    """
    pass

