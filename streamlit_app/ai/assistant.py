"""
Orchestrate Text-to-SQL and a business-friendly Gemini answer.

Flow: question -> Gemini SQL plan -> validate -> read-only SELECT ->
Gemini narrative. Numerical answers always come from the warehouse.
"""

import time

import pandas as pd

import config
import db

from . import gemini_client
from . import schema
from .sql_guard import UnsafeSQLError, validate_readonly_sql


class AssistantError(RuntimeError):
    """Raised for recoverable assistant failures shown in the chat UI."""

    def __init__(self, message, sql=None, sources=None):

        super().__init__(message)

        self.sql = sql
        self.sources = sources or []


def _log(message):
    """Write a diagnostic line to the Streamlit / console process."""

    print(f"[AI Assistant] {message}", flush=True)


def answer_question(question, history=None):
    """
    Answer a business question from warehouse data.

    Returns a dict with text, sql, sources and an optional DataFrame.
    """

    cleaned_question = (question or "").strip()

    if not cleaned_question:

        raise AssistantError("Please enter a business question.")

    _log("warehouse lookup start")

    if not gemini_client.get_gemini_api_key():

        raise AssistantError(config.MISSING_GEMINI_KEY_MESSAGE)

    plan = _plan_query(cleaned_question, history or [])

    if plan.get("unsupported"):

        return {
            "text": config.UNSUPPORTED_QUESTION_MESSAGE,
            "sql": None,
            "sources": [],
            "table": None,
        }

    _log("SQL query being prepared")

    try:

        sql = validate_readonly_sql(plan.get("sql"))

    except UnsafeSQLError as error:

        raise AssistantError(
            "The generated query was blocked because it is not a "
            "read-only SELECT against the allowed warehouse objects."
        ) from error

    _log(f"SQL prepared: {sql}")

    sources = _normalise_sources(plan.get("data_sources"), sql)

    try:

        frame = _run_readonly_query(sql)

    except db.DatabaseError as error:

        raise AssistantError(
            "SQL Server is unavailable. Warehouse data cannot be loaded.",
            sql=sql,
            sources=sources,
        ) from error

    except Exception as error:

        if _is_timeout_error(error):

            raise AssistantError(
                config.WAREHOUSE_TIMEOUT_MESSAGE,
                sql=sql,
                sources=sources,
            ) from error

        raise AssistantError(
            "The warehouse query could not be executed. "
            "Please rephrase the question.",
            sql=sql,
            sources=sources,
        ) from error

    display_frame = frame.head(config.AI_MAX_RESULT_ROWS)

    text = _narrate_results(cleaned_question, sql, display_frame)

    return {
        "text": text,
        "sql": sql,
        "sources": sources,
        "table": display_frame if _should_show_table(display_frame) else None,
    }


def _plan_query(question, history):
    """Ask Gemini for a JSON SQL plan."""

    prompt = _sql_prompt(question, history)

    try:

        raw = gemini_client.generate_text(
            prompt,
            system_instruction=schema.WAREHOUSE_CONTEXT,
            expect_json=True,
        )

        payload = gemini_client.parse_json_object(raw)

    except gemini_client.GeminiError as error:

        raise AssistantError(str(error)) from error

    return payload


def _sql_prompt(question, history):
    """Build the SQL-generation user prompt."""

    lines = ["User question:", question]

    recent = _recent_turns(history)

    if recent:

        lines.append("")
        lines.append("Recent conversation:")
        lines.extend(recent)

    lines.append("")
    lines.append("Return JSON only.")

    return "\n".join(lines)


def _narrate_results(question, sql, frame):
    """Ask Gemini to phrase the warehouse result for a business user."""

    if frame is None or frame.empty:

        result_payload = "[]"
        empty_note = "The query returned no rows."

    else:

        slim = frame.head(config.AI_MAX_MODEL_ROWS)
        result_payload = slim.to_json(
            orient="records",
            date_format="iso",
            default_handler=str,
        )
        empty_note = f"The query returned {len(frame)} row(s)."

    prompt = (
        f"User question:\n{question}\n\n"
        f"{empty_note}\n\n"
        f"Query results (JSON records):\n{result_payload}\n"
    )

    try:

        return gemini_client.generate_text(
            prompt,
            system_instruction=schema.ANSWER_CONTEXT,
            expect_json=False,
        )

    except gemini_client.GeminiError as error:

        raise AssistantError(str(error), sql=sql) from error


def _run_readonly_query(sql):
    """Execute validated SQL through the existing Streamlit db helper."""

    _log("SQL execution start")
    started = time.perf_counter()

    with db.connection_scope() as connection:

        connection.timeout = config.AI_SQL_TIMEOUT_SECONDS

        cursor = connection.cursor()

        try:

            cursor.execute(sql)

            columns = [
                column[0] for column in (cursor.description or [])
            ]
            rows = cursor.fetchmany(config.AI_MAX_RESULT_ROWS)

        finally:

            cursor.close()

    _log(
        "SQL execution completion in "
        f"{time.perf_counter() - started:.1f}s "
        f"({len(rows)} row(s))"
    )

    if not columns:

        return pd.DataFrame()

    return pd.DataFrame.from_records(rows, columns=columns)


def _is_timeout_error(error):
    """Return True when SQL Server reports a query timeout."""

    detail = str(error).lower()

    return "timeout" in detail or "timed out" in detail or "hyt00" in detail


def _normalise_sources(declared, sql):
    """Prefer model-declared sources, else objects mentioned in SQL."""

    cleaned = []

    for item in declared or []:

        name = str(item).strip()

        if name and name not in cleaned:

            cleaned.append(name)

    if cleaned:

        return cleaned

    from .sql_guard import _referenced_objects

    inferred = []

    for schema_name, object_name in _referenced_objects(sql):

        qualified = f"{schema_name}.{object_name}"

        if qualified not in inferred:

            inferred.append(qualified)

    return inferred


def _should_show_table(frame):
    """Show a table for rankings and multi-row comparisons."""

    return frame is not None and not frame.empty and len(frame) > 1


def _recent_turns(history, limit=4):
    """Return compact prior chat lines for follow-up questions."""

    lines = []

    for message in history[-limit:]:

        role = message.get("role", "")
        text = (message.get("content") or "").strip()

        if role not in {"user", "assistant"} or not text:

            continue

        label = "User" if role == "user" else "Assistant"
        lines.append(f"{label}: {text[:500]}")

    return lines
