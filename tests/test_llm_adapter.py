import pytest

from src.llm_adapter import (
    build_prompt,
    extract_sql,
    generate_sql,
)


def test_build_prompt_includes_user_query_and_schema():
    user_query = "Show me all students older than 20"
    schema_text = """
Table: students
- name (TEXT)
- age (INTEGER)
- gpa (REAL)
""".strip()

    prompt = build_prompt(user_query, schema_text)

    assert "Show me all students older than 20" in prompt
    assert "Table: students" in prompt
    assert "- name (TEXT)" in prompt
    assert "SQLite" in prompt
    assert "SELECT" in prompt


def test_extract_sql_raw_sql():
    response = "SELECT name, age FROM students WHERE age > 20;"
    sql = extract_sql(response)

    assert sql == "SELECT name, age FROM students WHERE age > 20;"


def test_extract_sql_from_markdown_code_block():
    response = """```sql
SELECT name, age FROM students WHERE age > 20;
```"""
    sql = extract_sql(response)

    assert sql == "SELECT name, age FROM students WHERE age > 20;"


def test_extract_sql_with_sql_label():
    response = "SQL: SELECT name, age FROM students;"
    sql = extract_sql(response)

    assert sql == "SELECT name, age FROM students;"


def test_extract_sql_trims_extra_text_after_first_semicolon():
    response = "SELECT name FROM students; Explanation: this returns names."
    sql = extract_sql(response)

    assert sql == "SELECT name FROM students;"


def test_extract_sql_raises_for_empty_response():
    with pytest.raises(ValueError, match="LLM response is empty"):
        extract_sql("")


def test_generate_sql_uses_mocked_llm_response(monkeypatch):
    def mock_call_llm(prompt: str, model: str = "gpt-4.1-mini") -> str:
        return "SELECT name, age FROM students;"

    monkeypatch.setattr(
        "src.llm_adapter.call_llm",
        mock_call_llm
    )

    sql = generate_sql(
        user_query="Show me all students",
        schema_text="Table: students\n- name (TEXT)\n- age (INTEGER)"
    )

    assert sql == "SELECT name, age FROM students;"


def test_generate_sql_extracts_sql_from_mocked_code_block(monkeypatch):
    def mock_call_llm(prompt: str, model: str = "gpt-4.1-mini") -> str:
        return """```sql
SELECT gpa FROM students;
```"""

    monkeypatch.setattr(
        "src.llm_adapter.call_llm",
        mock_call_llm
    )

    sql = generate_sql(
        user_query="Show me all GPAs",
        schema_text="Table: students\n- gpa (REAL)"
    )

    assert sql == "SELECT gpa FROM students;"