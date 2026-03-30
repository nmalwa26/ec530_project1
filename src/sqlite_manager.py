import sqlite3
from typing import Any

def connect_db(db_path: str) -> sqlite3.Connection:
    """
    Create and return a connection to the SQLite database.
    """
    pass


def create_table(conn: sqlite3.Connection, table_name: str, columns: list[dict[str, str]]) -> None:
    """
    Create a table with an auto-incrementing primary key and the provided columns.
    """
    pass


def insert_rows(conn: sqlite3.Connection, table_name: str, rows: list[dict[str, Any]]) -> None:
    """
    Insert multiple rows into a table.
    """
    pass


def execute_select_query(conn: sqlite3.Connection, sql: str) -> list[dict[str, Any]]:
    """
    Execute a validated SELECT query and return results as a list of dictionaries.
    """
    pass


def list_tables(conn: sqlite3.Connection) -> list[str]:
    """
    Return a list of all user tables in the database.
    """
    pass


def get_table_info(conn: sqlite3.Connection, table_name: str) -> list[dict[str, Any]]:
    """
    Return schema metadata for a table using PRAGMA table_info().
    """
    pass