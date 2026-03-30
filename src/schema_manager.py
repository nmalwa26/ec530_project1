from typing import Any

def build_schema_object(table_name: str, columns: list[dict[str, str]]) -> dict[str, Any]:
    """
    Build a normalized internal schema representation.
    """
    pass


def get_existing_schemas(db_conn) -> list[dict[str, Any]]:
    """
    Read all existing table schemas from the database and return them
    in a normalized internal format.
    """
    pass


def normalize_schema_columns(columns: list[dict[str, str]]) -> list[dict[str, str]]:
    """
    Normalize column names/types for reliable comparison.
    """
    pass


def schemas_match(incoming_schema: dict[str, Any],existing_schema: dict[str, Any]) -> bool:
    """
    Return True if the incoming CSV schema matches an existing table schema.
    """
    pass


def find_matching_table(incoming_schema: dict[str, Any],existing_schemas: list[dict[str, Any]]) -> str | None:
    """
    Return the name of a matching table if one exists, otherwise None.
    """
    pass


def decide_table_action(incoming_schema: dict[str, Any],existing_schemas: list[dict[str, Any]]) -> dict[str, Any]:
    """
    Decide whether to append to an existing table or create a new one.
    """
    pass


def format_schema_for_prompt(existing_schemas: list[dict[str, Any]]) -> str:
    """
    Convert schema information into a readable text format for the LLM prompt.
    """
    pass