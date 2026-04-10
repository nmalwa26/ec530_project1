from __future__ import annotations

import os
import re
from typing import Optional

from openai import OpenAI

def build_prompt(user_query: str, schema_text: str) -> str:
    """
    Build the prompt sent to the LLM.

    The prompt includes:
    - the task definition
    - the available database schema
    - the user's natural-language request
    - strict rules for the output
    """
    return f"""
You are an AI assistant that converts natural-language questions into SQLite SQL queries.

Database schema:
{schema_text}

User query:
"{user_query}"

Rules:
- Generate exactly one SQLite-compatible SELECT query.
- Only use the tables and columns shown in the schema.
- Do not write INSERT, UPDATE, DELETE, DROP, ALTER, or CREATE statements.
- Do not include explanations.
- Return only the SQL query.

SQL:
""".strip()


def call_llm(prompt: str, model: str = "gpt-4.1-mini") -> str:
    """
    Send the prompt to the LLM and return the raw text response.

    Requires OPENAI_API_KEY to be set in the environment.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY is not set in the environment.")

    client = OpenAI(api_key=api_key)

    response = client.responses.create(
        model=model,
        input=prompt,
    )

    return response.output_text.strip()


def extract_sql(llm_response: str) -> str:
    """
    Extract a SQL query from the raw LLM response.

    Handles cases like:
    - raw SQL only
    - SQL wrapped in ```sql ... ```
    - SQL preceded by labels like 'SQL:'
    """
    if not llm_response or not llm_response.strip():
        raise ValueError("LLM response is empty.")

    text = llm_response.strip()

    # Remove markdown code fences if present
    code_block_match = re.search(r"```(?:sql)?\s*(.*?)```", text, flags=re.IGNORECASE | re.DOTALL)
    if code_block_match:
        text = code_block_match.group(1).strip()

    # Remove leading label like "SQL:"
    text = re.sub(r"^\s*sql\s*:\s*", "", text, flags=re.IGNORECASE)

    # Trim to the first semicolon if present, assuming one query
    semicolon_index = text.find(";")
    if semicolon_index != -1:
        text = text[:semicolon_index + 1]

    return text.strip()


def generate_sql(
    user_query: str,
    schema_text: str,
    model: str = "gpt-4.1-mini",
) -> str:
    """
    Full LLM adapter flow:
    1. Build prompt
    2. Call LLM
    3. Extract SQL from response
    """
    prompt = build_prompt(user_query, schema_text)
    raw_response = call_llm(prompt, model=model)
    return extract_sql(raw_response)