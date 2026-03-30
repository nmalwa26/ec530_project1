from typing import Any

def build_prompt(user_query: str, schema_text: str) -> str:
    """
    Build the prompt sent to the LLM using the user query and database schema.
    """
    pass


def generate_sql(user_query: str, schema_text: str) -> str:
    """
    Generate candidate SQL from a natural-language user query.
    """
    pass


def call_llm(prompt: str) -> str:
    """
    Send the prompt to the LLM and return the raw text response.
    """
    pass


def extract_sql(llm_response: str) -> str:
    """
    Extract SQL text from the raw LLM response.
    """
    pass