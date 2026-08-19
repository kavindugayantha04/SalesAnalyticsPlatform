"""
AI Assistant page.

Natural-language questions are answered from the SQL Server data
warehouse through Gemini Flash. Conversation history is kept in
Streamlit session state only. The page never writes to SQL Server and
never retrains the forecasting model.
"""

import streamlit as st

import config
from ai.assistant import AssistantError, answer_question
from ai.gemini_client import get_gemini_api_key


def render():
    """
    Render the AI Assistant page.
    """

    st.subheader("AI Assistant")

    st.write(
        "Ask questions about sales, customers, products, sellers, "
        "payments and revenue forecasts."
    )

    if not get_gemini_api_key():

        st.info(config.MISSING_GEMINI_KEY_MESSAGE)

    _ensure_history()

    st.markdown("**Example questions**")

    for example in config.AI_EXAMPLE_QUESTIONS:

        if st.button(f"• {example}", key=f"ai_example_{example}"):

            st.session_state["ai_pending_question"] = example

    st.markdown("")

    _render_history()

    with st.form("ai_assistant_form", clear_on_submit=True):

        question = st.text_input(
            "Question",
            placeholder="Ask a question about the Sales Analytics Platform",
        )

        ask_clicked = st.form_submit_button("Ask / Send", type="primary")

    if st.button("Clear conversation"):

        st.session_state[config.AI_CHAT_HISTORY_KEY] = []
        st.session_state[config.AI_ANSWER_CACHE_KEY] = {}
        st.session_state.pop("ai_pending_question", None)
        st.rerun()

    pending = st.session_state.pop("ai_pending_question", None)

    if pending:

        _handle_question(pending)

        return

    if ask_clicked:

        _handle_question(question)


def _ensure_history():
    """Create the session-state chat list and answer cache on first visit."""

    if config.AI_CHAT_HISTORY_KEY not in st.session_state:

        st.session_state[config.AI_CHAT_HISTORY_KEY] = []

    if config.AI_ANSWER_CACHE_KEY not in st.session_state:

        st.session_state[config.AI_ANSWER_CACHE_KEY] = {}


def _render_history():
    """Draw the current-session conversation."""

    for message in st.session_state[config.AI_CHAT_HISTORY_KEY]:

        with st.chat_message(message["role"]):

            st.write(message["content"])

            table = message.get("table")

            if table is not None and not table.empty:

                st.dataframe(table, hide_index=True, use_container_width=True)

            sql = message.get("sql")

            if sql:

                with st.expander("View SQL Query"):

                    st.code(sql, language="sql")

            sources = message.get("sources") or []

            if sources:

                with st.expander("Data Source"):

                    for source in sources:

                        st.write(source)


def _handle_question(question):
    """Append the user turn, call the assistant, and store the reply."""

    cleaned = (question or "").strip()

    if not cleaned:

        st.warning("Please enter a business question.")
        return

    history = st.session_state[config.AI_CHAT_HISTORY_KEY]

    history.append({"role": "user", "content": cleaned})

    cache = st.session_state[config.AI_ANSWER_CACHE_KEY]
    cache_key = cleaned.casefold()

    if cache_key in cache:

        history.append(dict(cache[cache_key]))
        st.rerun()

        return

    try:

        with st.spinner("Looking up warehouse data..."):

            result = answer_question(cleaned, history)

        reply = {
            "role": "assistant",
            "content": result["text"],
            "sql": result.get("sql"),
            "sources": result.get("sources") or [],
            "table": result.get("table"),
        }

        cache[cache_key] = dict(reply)

    except AssistantError as error:

        reply = {
            "role": "assistant",
            "content": str(error),
            "sql": error.sql,
            "sources": error.sources,
            "table": None,
        }

    except Exception:

        reply = {
            "role": "assistant",
            "content": (
                "The AI Assistant could not complete that request. "
                "Please try again."
            ),
            "sql": None,
            "sources": [],
            "table": None,
        }

    history.append(reply)
    st.rerun()
