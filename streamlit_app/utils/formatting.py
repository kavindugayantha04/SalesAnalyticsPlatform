"""
Display formatting for the Streamlit application.

These helpers only format values already loaded from the warehouse.
They never query or write to SQL Server.
"""

import calendar


def format_compact_number(value):
    """
    Compact count for KPI cards: 99K, 1.25M, or 1,234.
    """

    if value is None:

        return "—"

    number = float(value)
    sign = "-" if number < 0 else ""
    amount = abs(number)

    if amount >= 1_000_000:

        return f"{sign}{amount / 1_000_000:.2f}M"

    if amount >= 1_000:

        return f"{sign}{amount / 1_000:.0f}K"

    return f"{sign}{int(amount):,}"


def format_currency(value):
    """
    Compact currency for KPI cards: R1.00M, R974.53K, or R123.45.
    """

    if value is None:

        return "—"

    number = float(value)
    sign = "-" if number < 0 else ""
    amount = abs(number)

    if amount >= 1_000_000:

        return f"{sign}R{amount / 1_000_000:.2f}M"

    if amount >= 1_000:

        return f"{sign}R{amount / 1_000:.2f}K"

    return f"{sign}R{amount:,.2f}"


def format_currency_full(value):
    """Full currency with thousands separators, for detail rows."""

    if value is None:

        return "—"

    return f"R{float(value):,.2f}"


def format_percent(value):
    """Percentage with two decimal places, for example 14.02%."""

    if value is None:

        return "—"

    return f"{float(value):.2f}%"


def format_month_year(year, month):
    """Calendar label such as September 2018."""

    month_name = calendar.month_name[int(month)]

    return f"{month_name} {int(year)}"
