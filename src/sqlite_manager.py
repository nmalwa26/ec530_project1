from __future__ import annotations

import sqlite3
from typing import Any


def connect_db(db_path: str) -> sqlite3.Connection:
    """
    Connect to a SQLite database and return the connection object.
    """
    return sqlite3.connect(db_path)


def create_table(conn: sqlite3.Connection, create_table_sql: str) -> None:
    """
    Execute a CREATE TABLE statement.
    """
    cursor = conn.cursor()
    cursor.execute(create_table_sql)
    conn.commit()


def insert_rows(conn: sqlite3.Connection, table_name: str,rows: list[dict[str, Any]]) -> None:
    """
    Insert multiple rows into a table.

    Assumes each row is a dictionary with the same keys.
    """
    if not rows:
        return

    columns = list(rows[0].keys())
    column_names_sql = ", ".join(columns)
    placeholders = ", ".join(["?"] * len(columns))

    sql = f"INSERT INTO {table_name} ({column_names_sql}) VALUES ({placeholders})"

    values = []
    for row in rows:
        values.append(tuple(row[column] for column in columns))

    cursor = conn.cursor()
    cursor.executemany(sql, values)
    conn.commit()


def list_tables(conn: sqlite3.Connection) -> list[str]:
    """
    Return a list of all user-defined tables in the database.
    """
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT name
        FROM sqlite_master
        WHERE type='table' AND name NOT LIKE 'sqlite_%'
        ORDER BY name;
        """
    )
    return [row[0] for row in cursor.fetchall()]


def get_table_info(conn: sqlite3.Connection, table_name: str) -> list[dict[str, Any]]:
    """
    Return schema information for a table using PRAGMA table_info().
    """
    cursor = conn.cursor()
    cursor.execute(f"PRAGMA table_info({table_name});")

    rows = cursor.fetchall()

    result = []
    for row in rows:
        result.append({
            "cid": row[0],
            "name": row[1],
            "sqlite_type": row[2],
            "notnull": row[3],
            "default_value": row[4],
            "is_primary_key": row[5],
        })

    return result


def execute_select_query(conn: sqlite3.Connection, sql: str) -> list[dict[str, Any]]:
    """
    Execute a validated SELECT query and return results as dictionaries.
    """
    cursor = conn.cursor()
    cursor.execute(sql)

    column_names = [description[0] for description in cursor.description]
    rows = cursor.fetchall()

    results = []
    for row in rows:
        results.append(dict(zip(column_names, row)))

    return results