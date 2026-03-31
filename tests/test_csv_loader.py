import pytest

from src.csv_loader import (
    load_csv,
    normalize_column_name,
    infer_sqlite_type,
)

# Tests normalize_column_name function 
# if spaces become underscores + lowercase conversion
def test_normalize_column_name_basic():
    assert normalize_column_name("First Name") == "first_name"

# Tests for infer_sqlite_type function
# for integers 
def test_infer_sqlite_type_integer():
    values = [1, 2, 3, 4]
    assert infer_sqlite_type(values) == "INTEGER"

# for real numbers (floats)
def test_infer_sqlite_type_real():
    values = [1.5, 2.3, 3.0]
    assert infer_sqlite_type(values) == "REAL"

# for text
def test_infer_sqlite_type_text():
    values = ["Alice", "Bob", "Charlie"]
    assert infer_sqlite_type(values) == "TEXT"

# Test for load_csv function with a valid CSV file
# checks if file reading works, table name comes from file name, headers normalize correctly, type infer correctly, rows are returned correctly 
def test_load_csv_success(tmp_path):
    csv_file = tmp_path / "students.csv"
    csv_file.write_text("First Name,Age,GPA\nAlice,20,3.8\nBob,21,3.5\n")

    result = load_csv(str(csv_file))

    assert result["table_name"] == "students"
    assert result["row_count"] == 2
    assert result["columns"] == [
        {"name": "first_name", "sqlite_type": "TEXT"},
        {"name": "age", "sqlite_type": "INTEGER"},
        {"name": "gpa", "sqlite_type": "REAL"},
    ]
    assert result["rows"] == [
        {"first_name": "Alice", "age": 20, "gpa": 3.8},
        {"first_name": "Bob", "age": 21, "gpa": 3.5},
    ]

# test if file missing 
def test_load_csv_missing_file():
    with pytest.raises(FileNotFoundError):
        load_csv("does_not_exist.csv")

# test if same normalized column name 
def test_load_csv_duplicate_normalized_columns(tmp_path):
    csv_file = tmp_path / "bad.csv"
    csv_file.write_text("First Name,First_Name\nAlice,Bob\n")

    with pytest.raises(ValueError, match="duplicate column names"):
        load_csv(str(csv_file))