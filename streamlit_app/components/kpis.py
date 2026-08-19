"""
KPI card layout used by analytical Streamlit pages.
"""

import streamlit as st


def render_kpi_cards(cards):
    """
    Render a row of metric cards.

    Each card is a mapping with label, value and optional help text.
    """

    columns = st.columns(len(cards))

    for column, card in zip(columns, cards):

        with column:

            with st.container(border=True):

                st.metric(
                    label=card["label"],
                    value=card["value"],
                    help=card.get("help"),
                )
