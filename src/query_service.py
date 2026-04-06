from __future__ import annotations

from typing import Any

from src.schema_manager import get_existing_schemas
from src.sql_validator import validate_sql
from src.sqlite_manager import execute_select_query


def format_query_result(rows: list[dict[str, Any]]) -> str:
    """
    Convert query results into a readable string for the CLI.

    If no rows are returned, provide a helpful message.
    """
    if not rows:
        return "No results found."

    headers = list(rows[0].keys())
    lines = []

    # Header row
    lines.append(" | ".join(headers))
    lines.append("-" * (len(lines[0])))

    # Data rows
    for row in rows:
        values = [str(row.get(header, "")) for header in headers]
        lines.append(" | ".join(values))

    return "\n".join(lines)


def run_sql_query(sql: str, conn) -> dict[str, Any]:
    """
    Validate a raw SQL query against the current schema, execute it if valid,
    and return a structured result.
    """
    schemas = get_existing_schemas(conn)
    validation = validate_sql(sql, schemas)

    if not validation["is_valid"]:
        return {
            "success": False,
            "mode": "sql",
            "sql": sql,
            "message": "Validation failed.",
            "errors": validation["errors"],
            "rows": [],
        }

    rows = execute_select_query(conn, sql)

    return {
        "success": True,
        "mode": "sql",
        "sql": sql,
        "message": f"Returned {len(rows)} row(s).",
        "errors": [],
        "rows": rows,
        "formatted_result": format_query_result(rows),
    }


def process_query(
    user_input: str,
    conn,
    input_mode: str = "sql",
) -> dict[str, Any]:
    """
    Main query entry point.

    Version 1:
    - supports raw SQL mode
    Future version:
    - can route natural-language queries to the LLM adapter
    """
    if input_mode == "sql":
        return run_sql_query(user_input, conn)

    return {
        "success": False,
        "mode": input_mode,
        "message": f"Unsupported input mode: {input_mode}",
        "errors": [f"Unsupported input mode: {input_mode}"],
        "rows": [],
    }