"""
Entry point for the Sales Analytics Platform Streamlit application.

Start with:

    streamlit run streamlit_app/app.py

This application is an additional user-interface layer over the existing
platform. It reads from the data warehouse and never modifies the ETL
pipeline, the warehouse data or the machine-learning artefacts.
"""

import streamlit as st

import config
import db
from components.kpis import render_kpi_cards
from pages.power_bi import render as render_power_bi_page
from pages.revenue_forecast import render as render_revenue_forecast_page
from pages.monthly_upload import render as render_monthly_upload_page
from utils.formatting import format_compact_number, format_currency


# set_page_config must be the first Streamlit call in the script.

st.set_page_config(
    page_title=config.APP_TITLE,
    layout=config.LAYOUT,
    initial_sidebar_state="expanded",
)


# ============================================================
# SIDEBAR
# ============================================================

def render_sidebar(connected):
    """
    Draw the navigation sidebar and return the selected page name.
    """

    with st.sidebar:

        st.header(config.APP_TITLE)

        page_names = list(config.NAV_PAGES)

        if config.NAV_PAGE_KEY not in st.session_state:

            st.session_state[config.NAV_PAGE_KEY] = page_names[0]

        selected_page = st.radio(
            "Navigation",
            page_names,
            key=config.NAV_PAGE_KEY,
            label_visibility="collapsed",
        )

        st.divider()

        if connected:
            st.caption("Database: connected")
        else:
            st.caption("Database: unavailable")

    return selected_page


# ============================================================
# CONNECTION STATUS
# ============================================================

def render_connection_status(connected, detail):
    """
    Report the outcome of the SQL Server connection test.
    """

    if connected:

        st.success("SQL Server Connected")

        with st.expander("Connection details"):

            st.write(detail)

            for setting, value in db.get_connection_info().items():

                st.write(f"{setting}: {value}")

        return

    st.error("SQL Server connection failed.")

    st.code(detail, language="text")

    st.info(
        "The interface is running, but warehouse data is unavailable. "
        "Check that SQL Server is running and that the ODBC driver is "
        "installed, then reload this page."
    )


# ============================================================
# OVERVIEW
# ============================================================

# Match the Power BI Executive Dashboard star-schema measures:
# revenue is product sales only (not freight), orders are distinct
# OrderID values, and customers are distinct unique customer identities.

OVERVIEW_KPIS_SQL = """
SELECT
    SUM(SalesAmount) AS TotalRevenue,
    COUNT(DISTINCT OrderID) AS TotalOrders
FROM dw.FactSales;
"""

TOTAL_CUSTOMERS_SQL = """
SELECT COUNT(DISTINCT CustomerUniqueID) AS TotalCustomers
FROM dw.DimCustomer;
"""

LATEST_FORECAST_SQL = """
SELECT TOP 1
    PredictedRevenue
FROM dw.vw_RevenueForecast
ORDER BY ForecastYear DESC, ForecastMonth DESC;
"""


def _load_overview_kpis():
    """
    Read warehouse KPI values for the Overview page.
    """

    sales_frame = db.run_query(OVERVIEW_KPIS_SQL)
    customer_frame = db.run_query(TOTAL_CUSTOMERS_SQL)
    forecast_frame = db.run_query(LATEST_FORECAST_SQL)

    total_revenue = None
    total_orders = None
    total_customers = None
    latest_forecast = None

    if sales_frame is not None and not sales_frame.empty:

        row = sales_frame.iloc[0]

        total_revenue = row["TotalRevenue"]
        total_orders = row["TotalOrders"]

    if customer_frame is not None and not customer_frame.empty:

        total_customers = customer_frame.iloc[0]["TotalCustomers"]

    if forecast_frame is not None and not forecast_frame.empty:

        latest_forecast = forecast_frame.iloc[0]["PredictedRevenue"]

    return {
        "total_revenue": total_revenue,
        "total_orders": total_orders,
        "total_customers": total_customers,
        "latest_forecast": latest_forecast,
    }


def render_overview(connected, detail):
    """
    Simple platform overview with read-only warehouse KPIs.
    """

    st.title(config.APP_TITLE)

    st.write(config.APP_DESCRIPTION)

    render_connection_status(connected, detail)

    st.subheader("Platform Overview")

    if not connected:

        render_kpi_cards(
            [
                {"label": "Total Revenue", "value": "—"},
                {"label": "Total Orders", "value": "—"},
                {"label": "Total Customers", "value": "—"},
                {"label": "Latest Forecast", "value": "—"},
            ]
        )

        return

    try:

        kpis = _load_overview_kpis()

    except db.DatabaseError as error:

        st.error("Warehouse KPIs could not be loaded.")
        st.code(str(error), language="text")

        render_kpi_cards(
            [
                {"label": "Total Revenue", "value": "—"},
                {"label": "Total Orders", "value": "—"},
                {"label": "Total Customers", "value": "—"},
                {"label": "Latest Forecast", "value": "—"},
            ]
        )

        return

    render_kpi_cards(
        [
            {
                "label": "Total Revenue",
                "value": format_currency(kpis["total_revenue"]),
            },
            {
                "label": "Total Orders",
                "value": format_compact_number(kpis["total_orders"]),
            },
            {
                "label": "Total Customers",
                "value": format_compact_number(kpis["total_customers"]),
            },
            {
                "label": "Latest Forecast",
                "value": format_currency(kpis["latest_forecast"]),
            },
        ]
    )


# ============================================================
# PAGE PLACEHOLDER
# ============================================================

def render_page_placeholder(page_name):
    """
    Show a placeholder for a page that has not been built yet.
    """

    st.subheader(page_name)

    st.write(config.NAV_PAGES[page_name])

    st.info("This page has not been implemented yet.")


# ============================================================
# MAIN
# ============================================================

def main():

    connected, detail = db.test_connection()

    selected_page = render_sidebar(connected)

    if selected_page == "Overview":

        render_overview(connected, detail)

        return

    if selected_page == "Power BI Dashboards":

        render_power_bi_page()

        return

    if selected_page == "Revenue Forecast":

        render_revenue_forecast_page()

        return

    if selected_page == "Monthly Upload":

        render_monthly_upload_page()

        return

    render_page_placeholder(selected_page)


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":

    main()
