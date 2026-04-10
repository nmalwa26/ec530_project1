from __future__ import annotations

import re
from typing import Any


DISALLOWED_KEYWORDS = {
    "insert",
    "update",
    "delete",
    "drop",
    "alter",
    "create",
    "replace",
    "truncate",
}


def is_select_query(sql: str) -> bool:
    """
    Return True only if the query starts with SELECT.
    """
    if not sql or not sql.strip():
        return False

    return sql.strip().lower().startswith("select")


def contains_disallowed_keyword(sql: str) -> bool:
    """
    Return True if the query contains obvious write/DDL keywords.
    """
    sql_lower = sql.lower()

    for keyword in DISALLOWED_KEYWORDS:
        if re.search(rf"\b{keyword}\b", sql_lower):
            return True

    return False


def contains_multiple_statements(sql: str) -> bool:
    """
    Reject queries that appear to contain multiple SQL statements.

    Allows at most one trailing semicolon.
    """
    stripped = sql.strip()

    if not stripped:
        return False

    semicolon_count = stripped.count(";")

    if semicolon_count == 0:
        return False

    if semicolon_count == 1 and stripped.endswith(";"):
        return False

    return True


def get_allowed_schema_map(schemas: list[dict[str, Any]]) -> dict[str, set[str]]:
    """
    Convert schema objects into a lookup map:
        {
            "students": {"name", "age", "gpa"}
        }
    """
    schema_map = {}

    for schema in schemas:
        table_name = schema["table_name"]
        columns = schema["columns"]

        schema_map[table_name] = {column["name"] for column in columns}

    return schema_map


def extract_table_names(sql: str) -> list[str]:
    """
    Extract table names from FROM and JOIN clauses.

    Example:
        SELECT * FROM students JOIN courses ...
        -> ["students", "courses"]
    """
    pattern = r"\b(?:from|join)\s+([a-zA-Z_][a-zA-Z0-9_]*)"
    return re.findall(pattern, sql, flags=re.IGNORECASE)

def extract_column_names(sql: str) -> list[str]:
    """
    Extract column names from the SELECT clause.

    Supports:
    - simple columns: name, age
    - table-qualified columns: students.name
    - aggregate functions: SUM(s.revenue), COUNT(*)
    - aliases: SUM(s.revenue) AS total_revenue

    Returns cleaned base column names.
    """
    match = re.search(
        r"select\s+(.*?)\s+from\s",
        sql,
        flags=re.IGNORECASE | re.DOTALL,
    )

    if not match:
        return []

    select_part = match.group(1).strip()

    if select_part == "*":
        return ["*"]

    raw_columns = [col.strip() for col in select_part.split(",")]
    cleaned_columns = []

    for column in raw_columns:
        # Remove alias: "SUM(s.revenue) AS total_revenue" -> "SUM(s.revenue)"
        column = re.split(r"\s+as\s+", column, flags=re.IGNORECASE)[0].strip()

        # Handle aggregate/function calls like SUM(...), AVG(...), COUNT(...)
        func_match = re.match(r"[a-zA-Z_][a-zA-Z0-9_]*\((.*?)\)", column)
        if func_match:
            inner = func_match.group(1).strip()

            # COUNT(*) or similar
            if inner == "*":
                cleaned_columns.append("*")
                continue

            column = inner

        # Handle table-qualified names: s.revenue -> revenue
        if "." in column:
            column = column.split(".")[-1].strip()

        # Remove stray parentheses or spaces
        column = column.strip("() ")

        cleaned_columns.append(column)

    return cleaned_columns


def validate_sql(sql: str, schemas: list[dict[str, Any]]) -> dict[str, Any]:
    """
    Validate a SQL query against project rules.

    Rules:
    - only SELECT queries allowed
    - reject unknown tables
    - reject unknown columns
    - reject obvious unsafe keywords
    - reject multiple statements
    """
    result = {
        "is_valid": False,
        "errors": [],
        "tables": [],
        "columns": [],
    }

    if not sql or not sql.strip():
        result["errors"].append("SQL query is empty.")
        return result

    if not is_select_query(sql):
        result["errors"].append("Only SELECT queries are allowed.")
        return result

    if contains_multiple_statements(sql):
        result["errors"].append("Multiple SQL statements are not allowed.")
        return result

    if contains_disallowed_keyword(sql):
        result["errors"].append("Query contains disallowed SQL keywords.")
        return result

    schema_map = get_allowed_schema_map(schemas)

    table_names = extract_table_names(sql)
    column_names = extract_column_names(sql)

    result["tables"] = table_names
    result["columns"] = column_names

    if not table_names:
        result["errors"].append("No table name found in query.")
        return result

    # Check all referenced tables exist
    for table in table_names:
        if table not in schema_map:
            result["errors"].append(f"Unknown table: {table}")

    if result["errors"]:
        return result

    # SELECT * is allowed as long as tables are valid
    if column_names == ["*"]:
        result["is_valid"] = True
        return result

    # For version 1, combine columns from all referenced tables
    allowed_columns = set()
    for table in table_names:
        allowed_columns.update(schema_map[table])

    for column in column_names:
        if column not in allowed_columns:
            result["errors"].append(f"Unknown column: {column}")

    if result["errors"]:
        return result

    result["is_valid"] = True
    return result