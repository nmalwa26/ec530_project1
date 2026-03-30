from typing import Any

def validate_sql(sql: str,schemas: list[dict[str, Any]]) -> dict[str, Any]:
    """
    Validate a SQL query.
    """
    pass


def is_select_query(sql: str) -> bool:
    """
    Return True only if the query is a SELECT query.
    """
    pass


def extract_table_names(sql: str) -> list[str]:
    """
    Extract referenced table names from a SQL query.
    """
    pass


def extract_column_names(sql: str) -> list[str]:
    """
    Extract referenced column names from a SQL query.
    """
    pass


def get_allowed_schema_map(schemas: list[dict[str, Any]]) -> dict[str, set[str]]:
    """
    Convert schema objects into a lookup map of table -> allowed columns.
    """
    pass