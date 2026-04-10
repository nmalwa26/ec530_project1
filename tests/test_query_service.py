from src.sqlite_manager import connect_db, create_table, insert_rows
from src.query_service import (
    format_query_result,
    run_sql_query,
    run_natural_language_query,
    process_query,
)


def setup_students_db(tmp_path):
    """
    Helper function to create a temporary database with one students table.
    """
    db_file = tmp_path / "test.db"
    conn = connect_db(str(db_file))

    create_sql = (
        "CREATE TABLE students ("
        "id INTEGER PRIMARY KEY AUTOINCREMENT, "
        "name TEXT, "
        "age INTEGER, "
        "gpa REAL);"
    )
    create_table(conn, create_sql)

    insert_rows(conn, "students", [
        {"name": "Alice", "age": 20, "gpa": 3.8},
        {"name": "Bob", "age": 21, "gpa": 3.5},
    ])

    return conn


def test_format_query_result_with_rows():
    rows = [
        {"name": "Alice", "age": 20},
        {"name": "Bob", "age": 21},
    ]

    result = format_query_result(rows)

    assert "name | age" in result
    assert "Alice | 20" in result
    assert "Bob | 21" in result


def test_format_query_result_no_rows():
    result = format_query_result([])

    assert result == "No results found."


def test_run_sql_query_success(tmp_path):
    conn = setup_students_db(tmp_path)

    result = run_sql_query("SELECT name, age FROM students ORDER BY age;", conn)

    assert result["success"] is True
    assert result["mode"] == "sql"
    assert result["errors"] == []
    assert result["message"] == "Returned 2 row(s)."
    assert result["rows"] == [
        {"name": "Alice", "age": 20},
        {"name": "Bob", "age": 21},
    ]
    assert "Alice | 20" in result["formatted_result"]
    assert "Bob | 21" in result["formatted_result"]

    conn.close()


def test_run_sql_query_validation_failure(tmp_path):
    conn = setup_students_db(tmp_path)

    result = run_sql_query("DELETE FROM students;", conn)

    assert result["success"] is False
    assert result["mode"] == "sql"
    assert result["message"] == "Validation failed."
    assert "Only SELECT queries are allowed." in result["errors"]
    assert result["rows"] == []

    conn.close()


def test_run_sql_query_unknown_table(tmp_path):
    conn = setup_students_db(tmp_path)

    result = run_sql_query("SELECT name FROM employees;", conn)

    assert result["success"] is False
    assert result["mode"] == "sql"
    assert result["message"] == "Validation failed."
    assert "Unknown table: employees" in result["errors"]
    assert result["rows"] == []

    conn.close()


def test_run_sql_query_no_results(tmp_path):
    conn = setup_students_db(tmp_path)

    result = run_sql_query(
        "SELECT name, age FROM students WHERE age > 100;",
        conn
    )

    assert result["success"] is True
    assert result["message"] == "Returned 0 row(s)."
    assert result["rows"] == []
    assert result["formatted_result"] == "No results found."

    conn.close()


def test_run_natural_language_query_success(tmp_path, monkeypatch):
    conn = setup_students_db(tmp_path)

    def mock_generate_sql(user_query, schema_text):
        return "SELECT name, age FROM students ORDER BY age;"

    monkeypatch.setattr(
        "src.query_service.generate_sql",
        mock_generate_sql
    )

    result = run_natural_language_query("Show me all students", conn)

    assert result["success"] is True
    assert result["mode"] == "natural_language"
    assert result["generated_sql"] == "SELECT name, age FROM students ORDER BY age;"
    assert result["errors"] == []
    assert result["rows"] == [
        {"name": "Alice", "age": 20},
        {"name": "Bob", "age": 21},
    ]
    assert "Alice | 20" in result["formatted_result"]

    conn.close()


def test_run_natural_language_query_generated_sql_fails_validation(tmp_path, monkeypatch):
    conn = setup_students_db(tmp_path)

    def mock_generate_sql(user_query, schema_text):
        return "DELETE FROM students;"

    monkeypatch.setattr(
        "src.query_service.generate_sql",
        mock_generate_sql
    )

    result = run_natural_language_query("Delete all students", conn)

    assert result["success"] is False
    assert result["mode"] == "natural_language"
    assert result["generated_sql"] == "DELETE FROM students;"
    assert result["message"] == "Generated SQL failed validation."
    assert "Only SELECT queries are allowed." in result["errors"]
    assert result["rows"] == []

    conn.close()


def test_run_natural_language_query_generation_failure(tmp_path, monkeypatch):
    conn = setup_students_db(tmp_path)

    def mock_generate_sql(user_query, schema_text):
        raise ValueError("OPENAI_API_KEY is not set in the environment.")

    monkeypatch.setattr(
        "src.query_service.generate_sql",
        mock_generate_sql
    )

    result = run_natural_language_query("Show me all students", conn)

    assert result["success"] is False
    assert result["mode"] == "natural_language"
    assert result["generated_sql"] is None
    assert result["message"] == "LLM generation failed."
    assert "OPENAI_API_KEY is not set in the environment." in result["errors"]
    assert result["rows"] == []

    conn.close()


def test_process_query_sql_mode(tmp_path):
    conn = setup_students_db(tmp_path)

    result = process_query(
        "SELECT name FROM students ORDER BY name;",
        conn,
        input_mode="sql",
    )

    assert result["success"] is True
    assert result["rows"] == [
        {"name": "Alice"},
        {"name": "Bob"},
    ]

    conn.close()


def test_process_query_natural_language_mode(tmp_path, monkeypatch):
    conn = setup_students_db(tmp_path)

    def mock_generate_sql(user_query, schema_text):
        return "SELECT name FROM students ORDER BY name;"

    monkeypatch.setattr(
        "src.query_service.generate_sql",
        mock_generate_sql
    )

    result = process_query(
        "Show me student names",
        conn,
        input_mode="natural_language",
    )

    assert result["success"] is True
    assert result["mode"] == "natural_language"
    assert result["rows"] == [
        {"name": "Alice"},
        {"name": "Bob"},
    ]

    conn.close()


def test_process_query_unsupported_mode(tmp_path):
    conn = setup_students_db(tmp_path)

    result = process_query(
        "Show me all students",
        conn,
        input_mode="something_else",
    )

    assert result["success"] is False
    assert result["mode"] == "something_else"
    assert "Unsupported input mode: something_else" in result["errors"]
    assert result["rows"] == []

    conn.close()