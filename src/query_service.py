from typing import Any

def run_natural_language_query(user_query: str, db_conn) -> dict[str, Any]:
    """
    Convert a natural-language query into SQL, validate it,
    execute it safely, and return results.
    """
    pass


def run_sql_query(sql: str, db_conn) -> dict[str, Any]:
    """
    Validate a raw SQL query, execute it safely, and return results.
    """
    pass


def process_query(user_input: str, db_conn, input_mode: str = "natural_language") -> dict[str, Any]:
    """
    Main entry point for query handling. Routes input based on mode.
    """
    pass


def format_query_result(rows: list[dict[str, Any]]) -> str:
    """
    Convert raw query result rows into a user-friendly string.
    """
    pass