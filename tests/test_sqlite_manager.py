import sqlite3

from src.sqlite_manager import (
    connect_db,
    create_table,
    insert_rows,
    list_tables,
    get_table_info,
    execute_select_query,
)


def test_connect_db(tmp_path):
    db_file = tmp_path / "test.db"

    conn = connect_db(str(db_file))

    assert isinstance(conn, sqlite3.Connection)
    conn.close()


def test_create_table_and_list_tables(tmp_path):
    db_file = tmp_path / "test.db"
    conn = connect_db(str(db_file))

    create_sql = (
        "CREATE TABLE students ("
        "id INTEGER PRIMARY KEY AUTOINCREMENT, "
        "name TEXT, "
        "age INTEGER);"
    )

    create_table(conn, create_sql)

    tables = list_tables(conn)

    assert "students" in tables
    conn.close()


def test_get_table_info(tmp_path):
    db_file = tmp_path / "test.db"
    conn = connect_db(str(db_file))

    create_sql = (
        "CREATE TABLE students ("
        "id INTEGER PRIMARY KEY AUTOINCREMENT, "
        "name TEXT, "
        "age INTEGER);"
    )

    create_table(conn, create_sql)

    info = get_table_info(conn, "students")

    assert info == [
        {
            "cid": 0,
            "name": "id",
            "sqlite_type": "INTEGER",
            "notnull": 0,
            "default_value": None,
            "is_primary_key": 1,
        },
        {
            "cid": 1,
            "name": "name",
            "sqlite_type": "TEXT",
            "notnull": 0,
            "default_value": None,
            "is_primary_key": 0,
        },
        {
            "cid": 2,
            "name": "age",
            "sqlite_type": "INTEGER",
            "notnull": 0,
            "default_value": None,
            "is_primary_key": 0,
        },
    ]

    conn.close()


def test_insert_rows_and_execute_select_query(tmp_path):
    db_file = tmp_path / "test.db"
    conn = connect_db(str(db_file))

    create_sql = (
        "CREATE TABLE students ("
        "id INTEGER PRIMARY KEY AUTOINCREMENT, "
        "name TEXT, "
        "age INTEGER);"
    )

    create_table(conn, create_sql)

    rows = [
        {"name": "Alice", "age": 20},
        {"name": "Bob", "age": 21},
    ]

    insert_rows(conn, "students", rows)

    results = execute_select_query(
        conn,
        "SELECT name, age FROM students ORDER BY age;"
    )

    assert results == [
        {"name": "Alice", "age": 20},
        {"name": "Bob", "age": 21},
    ]

    conn.close()


def test_insert_rows_empty_list_does_nothing(tmp_path):
    db_file = tmp_path / "test.db"
    conn = connect_db(str(db_file))

    create_sql = (
        "CREATE TABLE students ("
        "id INTEGER PRIMARY KEY AUTOINCREMENT, "
        "name TEXT, "
        "age INTEGER);"
    )

    create_table(conn, create_sql)

    insert_rows(conn, "students", [])

    results = execute_select_query(conn, "SELECT name, age FROM students;")

    assert results == []

    conn.close()


def test_execute_select_query_returns_dicts(tmp_path):
    db_file = tmp_path / "test.db"
    conn = connect_db(str(db_file))

    create_sql = (
        "CREATE TABLE courses ("
        "id INTEGER PRIMARY KEY AUTOINCREMENT, "
        "course_name TEXT, "
        "credits INTEGER);"
    )

    create_table(conn, create_sql)

    insert_rows(conn, "courses", [
        {"course_name": "EC530", "credits": 4},
    ])

    results = execute_select_query(
        conn,
        "SELECT course_name, credits FROM courses;"
    )

    assert isinstance(results, list)
    assert isinstance(results[0], dict)
    assert results[0]["course_name"] == "EC530"
    assert results[0]["credits"] == 4

    conn.close()