import pytest

from src.schema_manager import (
    build_schema_object,
    generate_create_table_sql,
    schemas_match,
    find_matching_table,
    decide_table_action,
    get_existing_schemas,
    log_error,
)


def test_build_schema_object():
    columns = [
        {"name": "name", "sqlite_type": "TEXT"},
        {"name": "age", "sqlite_type": "INTEGER"},
    ]

    result = build_schema_object("students", columns)

    assert result == {
        "table_name": "students",
        "columns": columns,
    }


def test_generate_create_table_sql():
    schema = {
        "table_name": "students",
        "columns": [
            {"name": "name", "sqlite_type": "TEXT"},
            {"name": "age", "sqlite_type": "INTEGER"},
        ],
    }

    sql = generate_create_table_sql(schema)

    assert sql == (
        "CREATE TABLE students "
        "(id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, age INTEGER);"
    )


def test_schemas_match_true():
    incoming = {
        "table_name": "students",
        "columns": [
            {"name": "name", "sqlite_type": "TEXT"},
            {"name": "age", "sqlite_type": "INTEGER"},
        ],
    }

    existing = {
        "table_name": "students_old",
        "columns": [
            {"name": "name", "sqlite_type": "TEXT"},
            {"name": "age", "sqlite_type": "INTEGER"},
        ],
    }

    assert schemas_match(incoming, existing) is True


def test_schemas_match_false_different_names():
    incoming = {
        "table_name": "students",
        "columns": [
            {"name": "full_name", "sqlite_type": "TEXT"},
            {"name": "age", "sqlite_type": "INTEGER"},
        ],
    }

    existing = {
        "table_name": "students",
        "columns": [
            {"name": "name", "sqlite_type": "TEXT"},
            {"name": "age", "sqlite_type": "INTEGER"},
        ],
    }

    assert schemas_match(incoming, existing) is False


def test_schemas_match_false_different_types():
    incoming = {
        "table_name": "students",
        "columns": [
            {"name": "name", "sqlite_type": "TEXT"},
            {"name": "age", "sqlite_type": "REAL"},
        ],
    }

    existing = {
        "table_name": "students",
        "columns": [
            {"name": "name", "sqlite_type": "TEXT"},
            {"name": "age", "sqlite_type": "INTEGER"},
        ],
    }

    assert schemas_match(incoming, existing) is False


def test_schemas_match_false_different_column_count():
    incoming = {
        "table_name": "students",
        "columns": [
            {"name": "name", "sqlite_type": "TEXT"},
        ],
    }

    existing = {
        "table_name": "students",
        "columns": [
            {"name": "name", "sqlite_type": "TEXT"},
            {"name": "age", "sqlite_type": "INTEGER"},
        ],
    }

    assert schemas_match(incoming, existing) is False


def test_find_matching_table_returns_name():
    incoming = {
        "table_name": "students",
        "columns": [
            {"name": "name", "sqlite_type": "TEXT"},
            {"name": "age", "sqlite_type": "INTEGER"},
        ],
    }

    existing_schemas = [
        {
            "table_name": "courses",
            "columns": [
                {"name": "course_name", "sqlite_type": "TEXT"},
            ],
        },
        {
            "table_name": "students_archive",
            "columns": [
                {"name": "name", "sqlite_type": "TEXT"},
                {"name": "age", "sqlite_type": "INTEGER"},
            ],
        },
    ]

    assert find_matching_table(incoming, existing_schemas) == "students_archive"


def test_find_matching_table_returns_none():
    incoming = {
        "table_name": "students",
        "columns": [
            {"name": "name", "sqlite_type": "TEXT"},
        ],
    }

    existing_schemas = [
        {
            "table_name": "courses",
            "columns": [
                {"name": "course_name", "sqlite_type": "TEXT"},
            ],
        }
    ]

    assert find_matching_table(incoming, existing_schemas) is None


def test_decide_table_action_append():
    incoming = {
        "table_name": "students",
        "columns": [
            {"name": "name", "sqlite_type": "TEXT"},
            {"name": "age", "sqlite_type": "INTEGER"},
        ],
    }

    existing_schemas = [
        {
            "table_name": "students_existing",
            "columns": [
                {"name": "name", "sqlite_type": "TEXT"},
                {"name": "age", "sqlite_type": "INTEGER"},
            ],
        }
    ]

    result = decide_table_action(incoming, existing_schemas)

    assert result == {
        "action": "append",
        "table_name": "students_existing",
    }


def test_decide_table_action_conflict():
    incoming = {
        "table_name": "students",
        "columns": [
            {"name": "name", "sqlite_type": "TEXT"},
            {"name": "gpa", "sqlite_type": "REAL"},
        ],
    }

    existing_schemas = [
        {
            "table_name": "students",
            "columns": [
                {"name": "name", "sqlite_type": "TEXT"},
                {"name": "age", "sqlite_type": "INTEGER"},
            ],
        }
    ]

    result = decide_table_action(incoming, existing_schemas)

    assert result["action"] == "conflict"
    assert result["table_name"] == "students"
    assert result["options"] == ["overwrite", "rename", "skip"]


def test_decide_table_action_create():
    incoming = {
        "table_name": "students",
        "columns": [
            {"name": "name", "sqlite_type": "TEXT"},
        ],
    }

    existing_schemas = [
        {
            "table_name": "courses",
            "columns": [
                {"name": "course_name", "sqlite_type": "TEXT"},
            ],
        }
    ]

    result = decide_table_action(incoming, existing_schemas)

    assert result == {
        "action": "create",
        "table_name": "students",
    }


def test_get_existing_schemas(monkeypatch):
    def mock_list_tables(conn):
        return ["students"]

    def mock_get_table_info(conn, table_name):
        return [
            {"name": "id", "sqlite_type": "INTEGER"},
            {"name": "name", "sqlite_type": "TEXT"},
            {"name": "age", "sqlite_type": "INTEGER"},
        ]

    monkeypatch.setattr(
        "src.schema_manager.list_tables",
        mock_list_tables
    )
    monkeypatch.setattr(
        "src.schema_manager.get_table_info",
        mock_get_table_info
    )

    result = get_existing_schemas(conn=None)

    assert result == [
        {
            "table_name": "students",
            "columns": [
                {"name": "name", "sqlite_type": "TEXT"},
                {"name": "age", "sqlite_type": "INTEGER"},
            ],
        }
    ]


def test_log_error_creates_file_and_writes_message(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    log_error("Test error message")

    log_file = tmp_path / "error_log.txt"
    assert log_file.exists()
    assert "Test error message" in log_file.read_text()