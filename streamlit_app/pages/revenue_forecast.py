"""
Revenue Forecast page.

Reads the existing warehouse forecast and monthly revenue views. This
page never writes to SQL Server, never retrains the model and never
runs the monthly prediction pipeline.
"""

import calendar

import altair as alt
import pandas as pd
import streamlit as st

import config
import db
from components.kpis import render_kpi_cards
from utils.formatting import (
    format_currency,
    format_currency_full,
    format_month_year,
    format_percent,
)


# Number of completed months required to rebuild the lag features used
# by the existing Gradient Boosting prediction module.
REQUIRED_HISTORY_MONTHS = config.REQUIRED_FORECAST_HISTORY_MONTHS


LATEST_FORECAST_SQL = """
SELECT TOP 1
    ForecastID,
    ForecastYear,
    ForecastMonth,
    ForecastYearMonth,
    PredictedRevenue,
    ModelVersion,
    PredictionDate
FROM dw.vw_RevenueForecast
ORDER BY ForecastYear DESC, ForecastMonth DESC;
"""

ACTUAL_VS_FORECAST_SQL = """
SELECT
    YearNumber,
    MonthNumber,
    MonthName,
    YearMonth,
    Revenue,
    RevenueType
FROM dw.vw_RevenueActualForecast;
"""

MONTHLY_REVENUE_SQL = """
SELECT
    YearNumber,
    MonthNumber,
    MonthName,
    YearMonth,
    MonthlyRevenue
FROM dw.vw_MonthlyRevenueML
ORDER BY YearNumber, MonthNumber;
"""


def render():
    """
    Render the Revenue Forecast page.
    """

    st.subheader("Revenue Forecast")

    st.write("Machine-learning based next-month revenue forecasting.")

    try:

        forecast = _load_latest_forecast()
        actual_vs_forecast = _load_actual_vs_forecast()
        monthly_revenue = _load_monthly_revenue()

    except db.DatabaseError as error:

        st.error("SQL Server is unavailable. Revenue forecast data cannot be loaded.")
        st.code(str(error), language="text")
        return

    except Exception as error:

        st.error("SQL Server is unavailable. Revenue forecast data cannot be loaded.")
        st.code(str(error), language="text")
        return

    if forecast is None:

        st.warning("No revenue forecast is currently available.")
        _render_model_information(model_version=None)
        return

    previous_month = _previous_calendar_month_revenue(
        monthly_revenue,
        int(forecast["ForecastYear"]),
        int(forecast["ForecastMonth"]),
    )

    forecast_revenue = float(forecast["PredictedRevenue"])
    previous_revenue = (
        None if previous_month is None else float(previous_month["MonthlyRevenue"])
    )

    change_pct, variance = _forecast_change(forecast_revenue, previous_revenue)

    _render_kpi_section(
        forecast_revenue,
        previous_revenue,
        change_pct,
        variance,
    )

    st.markdown("")

    _render_forecast_month_section(
        forecast,
        forecast_revenue,
        previous_month,
        previous_revenue,
        change_pct,
    )

    st.markdown("")

    _render_actual_vs_forecast_chart(actual_vs_forecast)

    st.markdown("")

    model_column, inputs_column = st.columns(2)

    with model_column:

        _render_model_information(forecast.get("ModelVersion"))

    with inputs_column:

        _render_forecast_inputs(forecast, monthly_revenue)

    st.markdown("")

    _render_interpretation(change_pct)


# ============================================================
# DATA LOADING
# ============================================================

def _load_latest_forecast():

    frame = db.run_query(LATEST_FORECAST_SQL)

    if frame is None or frame.empty:

        return None

    return frame.iloc[0].to_dict()


def _load_actual_vs_forecast():

    frame = db.run_query(ACTUAL_VS_FORECAST_SQL)

    if frame is None or frame.empty:

        return pd.DataFrame(
            columns=[
                "YearNumber",
                "MonthNumber",
                "MonthName",
                "YearMonth",
                "Revenue",
                "RevenueType",
            ]
        )

    return frame


def _load_monthly_revenue():

    frame = db.run_query(MONTHLY_REVENUE_SQL)

    if frame is None or frame.empty:

        return pd.DataFrame(
            columns=[
                "YearNumber",
                "MonthNumber",
                "MonthName",
                "YearMonth",
                "MonthlyRevenue",
            ]
        )

    return frame.sort_values(["YearNumber", "MonthNumber"]).reset_index(drop=True)


# ============================================================
# DERIVED VALUES
# ============================================================

def _previous_calendar_month(year, month):

    if month == 1:

        return year - 1, 12

    return year, month - 1


def _previous_calendar_month_revenue(monthly_revenue, forecast_year, forecast_month):

    previous_year, previous_month = _previous_calendar_month(
        forecast_year,
        forecast_month,
    )

    matched = monthly_revenue[
        (monthly_revenue["YearNumber"] == previous_year)
        & (monthly_revenue["MonthNumber"] == previous_month)
    ]

    if matched.empty:

        return None

    return matched.iloc[0]


def _forecast_change(forecast_revenue, previous_revenue):

    if previous_revenue is None:

        return None, None

    variance = forecast_revenue - previous_revenue

    if previous_revenue == 0:

        return None, variance

    change_pct = (variance / previous_revenue) * 100

    return change_pct, variance


def _lag_features(forecast, monthly_revenue):
    """
    Rebuild the lag inputs used by predict_next_month_v2.py from the
    completed months already stored in dw.vw_MonthlyRevenueML.
    """

    forecast_year = int(forecast["ForecastYear"])
    forecast_month = int(forecast["ForecastMonth"])

    history = monthly_revenue[
        (monthly_revenue["YearNumber"] < forecast_year)
        | (
            (monthly_revenue["YearNumber"] == forecast_year)
            & (monthly_revenue["MonthNumber"] < forecast_month)
        )
    ].sort_values(["YearNumber", "MonthNumber"])

    if len(history) < REQUIRED_HISTORY_MONTHS:

        return None

    recent = history.tail(REQUIRED_HISTORY_MONTHS)

    return {
        "PreviousMonthRevenue": float(history["MonthlyRevenue"].iloc[-1]),
        "Previous2MonthRevenue": float(history["MonthlyRevenue"].iloc[-2]),
        "Previous3MonthRevenue": float(history["MonthlyRevenue"].iloc[-3]),
        "Rolling3MonthAverage": float(recent["MonthlyRevenue"].mean()),
        "ForecastYear": forecast_year,
        "ForecastMonth": forecast_month,
        "Quarter": ((forecast_month - 1) // 3) + 1,
        "History": recent,
    }


# ============================================================
# SECTIONS
# ============================================================

def _render_kpi_section(
    forecast_revenue,
    previous_revenue,
    change_pct,
    variance,
):

    render_kpi_cards(
        [
            {
                "label": "Forecast Revenue",
                "value": format_currency(forecast_revenue),
                "help": format_currency_full(forecast_revenue),
            },
            {
                "label": "Previous Month Revenue",
                "value": format_currency(previous_revenue),
                "help": (
                    format_currency_full(previous_revenue)
                    if previous_revenue is not None
                    else "No completed month immediately before the forecast."
                ),
            },
            {
                "label": "Forecast Change %",
                "value": format_percent(change_pct),
                "help": "((Forecast - Previous Month) / Previous Month) x 100",
            },
            {
                "label": "Forecast Variance",
                "value": format_currency(variance),
                "help": (
                    format_currency_full(variance)
                    if variance is not None
                    else "Forecast Revenue - Previous Month Revenue"
                ),
            },
        ]
    )


def _render_forecast_month_section(
    forecast,
    forecast_revenue,
    previous_month,
    previous_revenue,
    change_pct,
):

    forecast_label = format_month_year(
        forecast["ForecastYear"],
        forecast["ForecastMonth"],
    )

    with st.container(border=True):

        st.markdown(f"### {forecast_label}")

        st.caption("Latest stored forecast")

        detail_one, detail_two, detail_three = st.columns(3)

        with detail_one:

            st.write("Forecast Revenue")
            st.write(format_currency_full(forecast_revenue))

        with detail_two:

            st.write("Previous Month Revenue")

            if previous_month is None:

                st.write("Insufficient historical data")

            else:

                previous_label = format_month_year(
                    previous_month["YearNumber"],
                    previous_month["MonthNumber"],
                )
                st.write(f"{format_currency_full(previous_revenue)} ({previous_label})")

        with detail_three:

            st.write("Forecast Change %")
            st.write(format_percent(change_pct))

        prediction_date = forecast.get("PredictionDate")

        if pd.notna(prediction_date):

            st.caption(f"Stored on {pd.to_datetime(prediction_date):%Y-%m-%d %H:%M}")


def _render_actual_vs_forecast_chart(actual_vs_forecast):

    st.markdown("### Actual Revenue vs Forecast")

    if actual_vs_forecast.empty:

        st.info("No actual or forecast revenue is available to chart.")
        return

    chart_data = actual_vs_forecast.copy()

    chart_data["YearNumber"] = chart_data["YearNumber"].astype(int)
    chart_data["MonthNumber"] = chart_data["MonthNumber"].astype(int)
    chart_data["YearMonthSort"] = (
        chart_data["YearNumber"] * 100 + chart_data["MonthNumber"]
    )
    chart_data["Revenue"] = chart_data["Revenue"].astype(float)

    chart_data = chart_data.sort_values(
        ["YearMonthSort", "RevenueType"]
    ).reset_index(drop=True)

    month_order = (
        chart_data.sort_values("YearMonthSort")["YearMonth"]
        .drop_duplicates()
        .tolist()
    )

    colour_scale = alt.Scale(
        domain=["Actual", "Forecast"],
        range=["#4C78A8", "#F58518"],
    )

    x_axis = alt.X(
        "YearMonth:N",
        title="YearMonth",
        sort=month_order,
    )
    y_axis = alt.Y(
        "Revenue:Q",
        title="Revenue",
        axis=alt.Axis(format="~s"),
    )
    colour = alt.Color(
        "RevenueType:N",
        title="RevenueType",
        scale=colour_scale,
        legend=alt.Legend(orient="top"),
    )
    tooltips = [
        alt.Tooltip("YearMonth:N"),
        alt.Tooltip("RevenueType:N"),
        alt.Tooltip("Revenue:Q", format=",.2f"),
    ]

    actual_line = (
        alt.Chart(chart_data)
        .transform_filter("datum.RevenueType == 'Actual'")
        .mark_line(point=True)
        .encode(x=x_axis, y=y_axis, color=colour, tooltip=tooltips)
    )

    forecast_points = (
        alt.Chart(chart_data)
        .transform_filter("datum.RevenueType == 'Forecast'")
        .mark_point(filled=True, size=140, shape="diamond")
        .encode(x=x_axis, y=y_axis, color=colour, tooltip=tooltips)
    )

    chart = (actual_line + forecast_points).properties(height=360)

    st.altair_chart(chart, width="stretch")


def _render_model_information(model_version):

    st.markdown("### Forecast Model")

    displayed_version = model_version or config.PRODUCTION_MODEL_VERSION

    st.write(f"**Model:** {config.PRODUCTION_MODEL_TYPE}")
    st.write(f"**Model Version:** {displayed_version}")
    st.write(f"**Model file:** `{config.PRODUCTION_MODEL_PATH}`")

    st.write("**Training Features:**")

    for feature in config.PRODUCTION_FEATURES:

        st.markdown(f"- {feature}")

    st.caption(
        "This page reads the stored forecast only. It does not retrain "
        "the model or run the prediction pipeline."
    )


def _render_forecast_inputs(forecast, monthly_revenue):

    st.markdown("### Forecast Input Information")

    lags = _lag_features(forecast, monthly_revenue)

    if lags is None:

        st.warning(
            "Insufficient historical data is available to reconstruct "
            "the forecast input features. At least "
            f"{REQUIRED_HISTORY_MONTHS} completed months before the "
            "forecast month are required."
        )
        return

    rows = [
        ("Previous Month Revenue", format_currency_full(lags["PreviousMonthRevenue"])),
        ("Previous 2 Month Revenue", format_currency_full(lags["Previous2MonthRevenue"])),
        ("Previous 3 Month Revenue", format_currency_full(lags["Previous3MonthRevenue"])),
        ("Rolling 3 Month Average", format_currency_full(lags["Rolling3MonthAverage"])),
        ("Forecast Year", str(lags["ForecastYear"])),
        ("Forecast Month", f"{lags['ForecastMonth']} ({calendar.month_name[lags['ForecastMonth']]})"),
        ("Quarter", str(lags["Quarter"])),
    ]

    st.dataframe(
        pd.DataFrame(rows, columns=["Input", "Value"]),
        hide_index=True,
        width="stretch",
    )


def _render_interpretation(change_pct):

    st.markdown("### Forecast Interpretation")

    if change_pct is None:

        st.info(
            "Insufficient historical data is available to compare the "
            "forecast with the previous month."
        )
        return

    displayed_change = round(float(change_pct), 2)

    if displayed_change > 0:

        st.success(
            "Revenue is forecast to increase compared with the previous month."
        )

    elif displayed_change < 0:

        st.warning(
            "Revenue is forecast to decrease compared with the previous month."
        )

    else:

        st.info(
            "Revenue is forecast to remain approximately unchanged."
        )
