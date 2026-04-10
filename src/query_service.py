from __future__ import annotations

from typing import Any

from src.schema_manager import get_existing_schemas, format_schema_for_prompt
from src.sql_validator import validate_sql
from src.sqlite_manager import execute_select_query
from src.llm_adapter import generate_sql


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
    lines.append("-" * len(lines[0]))

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


def run_natural_language_query(user_query: str, conn) -> dict[str, Any]:
    """
    Convert a natural-language query into SQL using the LLM adapter,
    validate the generated SQL, execute it if valid, and return results.
    """
    schemas = get_existing_schemas(conn)
    schema_text = format_schema_for_prompt(schemas)

    try:
        generated_sql = generate_sql(user_query, schema_text)
    except Exception as e:
        return {
            "success": False,
            "mode": "natural_language",
            "user_query": user_query,
            "generated_sql": None,
            "message": "LLM generation failed.",
            "errors": [str(e)],
            "rows": [],
        }

    validation = validate_sql(generated_sql, schemas)

    if not validation["is_valid"]:
        return {
            "success": False,
            "mode": "natural_language",
            "user_query": user_query,
            "generated_sql": generated_sql,
            "message": "Generated SQL failed validation.",
            "errors": validation["errors"],
            "rows": [],
        }

    rows = execute_select_query(conn, generated_sql)

    return {
        "success": True,
        "mode": "natural_language",
        "user_query": user_query,
        "generated_sql": generated_sql,
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

    Supports:
    - raw SQL mode
    - natural-language mode
    """
    if input_mode == "sql":
        return run_sql_query(user_input, conn)

    if input_mode == "natural_language":
        return run_natural_language_query(user_input, conn)

    return {
        "success": False,
        "mode": input_mode,
        "message": f"Unsupported input mode: {input_mode}",
        "errors": [f"Unsupported input mode: {input_mode}"],
        "rows": [],
    }