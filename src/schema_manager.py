from __future__ import annotations

from typing import Any

from src.sqlite_manager import list_tables, get_table_info


def build_schema_object(table_name: str, columns: list[dict[str, str]]) -> dict[str, Any]:
    """
    Build a standardized internal schema representation.
    """
    return {
        "table_name": table_name,
        "columns": columns,
    }

def generate_create_table_sql(schema: dict[str, Any]) -> str:
    """
    Generate a CREATE TABLE SQL statement from a schema object.
    """
    table_name = schema["table_name"]
    columns = schema["columns"]

    # Start with the required primary key column
    column_definitions = ["id INTEGER PRIMARY KEY AUTOINCREMENT"]

    # Add each schema column as "name TYPE"
    for column in columns:
        column_name = column["name"]
        sqlite_type = column["sqlite_type"]
        column_definitions.append(f"{column_name} {sqlite_type}")

    # Join all column definitions into one CREATE TABLE statement
    columns_sql = ", ".join(column_definitions)

    return f"CREATE TABLE {table_name} ({columns_sql});"

def get_existing_schemas(conn) -> list[dict]:
    """
    Retrieve all existing table schemas from the database
    """
    schemas = []

    for table_name in list_tables(conn):
        table_info = get_table_info(conn, table_name)

        columns = []
        for col in table_info:
            if col["name"] == "id":
                continue

            columns.append({
                "name": col["name"],
                "sqlite_type": col["sqlite_type"],
            })

        schemas.append({
            "table_name": table_name,
            "columns": columns,
        })

    return schemas

def schemas_match(incoming: dict, existing: dict) -> bool:
    """
    Check if two schemas match exactly.
    """
    inc_cols = incoming["columns"]
    ex_cols = existing["columns"]

    if len(inc_cols) != len(ex_cols):
        return False

    for inc, ex in zip(inc_cols, ex_cols):
        if inc["name"] != ex["name"]:
            return False
        if inc["sqlite_type"] != ex["sqlite_type"]:
            return False

    return True

def find_matching_table(incoming_schema: dict, existing_schemas: list[dict]) -> str | None:
    """
    Return the name of a matching table if one exists.
    """
    for schema in existing_schemas:
        if schemas_match(incoming_schema, schema):
            return schema["table_name"]

    return None

def decide_table_action(incoming_schema: dict, existing_schemas: list[dict]) -> dict:
    """
    Decide what to do with incoming data.
    """
    matching_table = find_matching_table(incoming_schema, existing_schemas)

    # Perfect match thenappend
    if matching_table:
        return {
            "action": "append",
            "table_name": matching_table,
        }

    # Check if table name already exists (but schema differs)
    for schema in existing_schemas:
        if schema["table_name"] == incoming_schema["table_name"]:
            return {
                "action": "conflict",
                "table_name": incoming_schema["table_name"],
                "options": ["overwrite", "rename", "skip"],
            }

    # No conflict, then create new table
    return {
        "action": "create",
        "table_name": incoming_schema["table_name"],
    }

def log_error(message: str) -> None:
    """
    Log an error message to error_log.txt.
    """
    with open("error_log.txt", "a") as f:
        f.write(message + "\n")