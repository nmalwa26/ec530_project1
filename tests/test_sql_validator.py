from src.sql_validator import (
    is_select_query,
    contains_disallowed_keyword,
    contains_multiple_statements,
    get_allowed_schema_map,
    extract_table_names,
    extract_column_names,
    validate_sql,
)


def sample_schemas():
    return [
        {
            "table_name": "students",
            "columns": [
                {"name": "name", "sqlite_type": "TEXT"},
                {"name": "age", "sqlite_type": "INTEGER"},
                {"name": "gpa", "sqlite_type": "REAL"},
            ],
        },
        {
            "table_name": "courses",
            "columns": [
                {"name": "course_name", "sqlite_type": "TEXT"},
                {"name": "credits", "sqlite_type": "INTEGER"},
            ],
        },
    ]


def test_is_select_query_true():
    assert is_select_query("SELECT * FROM students") is True


def test_is_select_query_false():
    assert is_select_query("DELETE FROM students") is False


def test_contains_disallowed_keyword_true():
    assert contains_disallowed_keyword("SELECT * FROM students; DROP TABLE students;") is True


def test_contains_disallowed_keyword_false():
    assert contains_disallowed_keyword("SELECT name, age FROM students") is False


def test_contains_multiple_statements_true():
    sql = "SELECT * FROM students; DROP TABLE students;"
    assert contains_multiple_statements(sql) is True


def test_contains_multiple_statements_false_with_single_trailing_semicolon():
    sql = "SELECT * FROM students;"
    assert contains_multiple_statements(sql) is False


def test_get_allowed_schema_map():
    schema_map = get_allowed_schema_map(sample_schemas())

    assert schema_map == {
        "students": {"name", "age", "gpa"},
        "courses": {"course_name", "credits"},
    }


def test_extract_table_names_single_table():
    sql = "SELECT name, age FROM students"
    assert extract_table_names(sql) == ["students"]


def test_extract_table_names_with_join():
    sql = "SELECT name, course_name FROM students JOIN courses ON students.id = courses.id"
    assert extract_table_names(sql) == ["students", "courses"]


def test_extract_column_names_simple():
    sql = "SELECT name, age FROM students"
    assert extract_column_names(sql) == ["name", "age"]


def test_extract_column_names_star():
    sql = "SELECT * FROM students"
    assert extract_column_names(sql) == ["*"]


def test_extract_column_names_with_table_prefix():
    sql = "SELECT students.name, students.age FROM students"
    assert extract_column_names(sql) == ["name", "age"]


def test_validate_sql_valid_simple_select():
    sql = "SELECT name, age FROM students"

    result = validate_sql(sql, sample_schemas())

    assert result["is_valid"] is True
    assert result["errors"] == []
    assert result["tables"] == ["students"]
    assert result["columns"] == ["name", "age"]


def test_validate_sql_rejects_non_select():
    sql = "DELETE FROM students"

    result = validate_sql(sql, sample_schemas())

    assert result["is_valid"] is False
    assert "Only SELECT queries are allowed." in result["errors"]


def test_validate_sql_rejects_unknown_table():
    sql = "SELECT name FROM employees"

    result = validate_sql(sql, sample_schemas())

    assert result["is_valid"] is False
    assert "Unknown table: employees" in result["errors"]


def test_validate_sql_rejects_unknown_column():
    sql = "SELECT salary FROM students"

    result = validate_sql(sql, sample_schemas())

    assert result["is_valid"] is False
    assert "Unknown column: salary" in result["errors"]


def test_validate_sql_allows_select_star():
    sql = "SELECT * FROM students"

    result = validate_sql(sql, sample_schemas())

    assert result["is_valid"] is True
    assert result["errors"] == []


def test_validate_sql_rejects_multiple_statements():
    sql = "SELECT * FROM students; DROP TABLE students;"

    result = validate_sql(sql, sample_schemas())

    assert result["is_valid"] is False
    assert "Multiple SQL statements are not allowed." in result["errors"]


def test_validate_sql_valid_join():
    sql = "SELECT name, course_name FROM students JOIN courses ON students.id = courses.id"

    result = validate_sql(sql, sample_schemas())

    assert result["is_valid"] is True
    assert result["errors"] == []
    assert result["tables"] == ["students", "courses"]
    assert result["columns"] == ["name", "course_name"]


def test_validate_sql_rejects_join_with_unknown_table():
    sql = "SELECT name FROM students JOIN professors ON students.id = professors.id"

    result = validate_sql(sql, sample_schemas())

    assert result["is_valid"] is False
    assert "Unknown table: professors" in result["errors"]


def test_validate_sql_rejects_empty_query():
    result = validate_sql("", sample_schemas())

    assert result["is_valid"] is False
    assert "SQL query is empty." in result["errors"]