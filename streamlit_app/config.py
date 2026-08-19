"""
Configuration for the Streamlit application layer.

This module holds presentation settings only. Database credentials stay
in etl/db_connection.py and are never redefined here.
"""

import sys

from pathlib import Path


# ============================================================
# PROJECT PATHS
# ============================================================

APP_DIR = Path(__file__).resolve().parent

PROJECT_ROOT = APP_DIR.parent


def ensure_project_root_on_path():
    """
    Make top-level project packages such as etl importable.

    Running "streamlit run streamlit_app/app.py" places streamlit_app on
    sys.path but not the repository root. The root is appended rather than
    prepended so installed packages always win over same-named folders
    that exist in the repository root.
    """

    root_path = str(PROJECT_ROOT)

    if root_path not in sys.path:

        sys.path.append(root_path)


ensure_project_root_on_path()


# ============================================================
# APPLICATION IDENTITY
# ============================================================

APP_TITLE = "Sales Analytics Platform"

APP_DESCRIPTION = (
    "Sales analytics, business intelligence and machine-learning "
    "forecasting platform."
)

LAYOUT = "wide"


# ============================================================
# NAVIGATION
# ============================================================

# Streamlit is the application layer around the existing BI platform.
# Detailed reporting stays in the completed Power BI report; Streamlit
# owns overview, forecast interaction, monthly upload and the assistant.

NAV_PAGES = {

    "Overview":
        "Platform overview, architecture and connection status.",

    "Power BI Dashboards":
        "Interactive business intelligence dashboards for executive, "
        "sales, product, customer, seller and revenue analysis.",

    "Revenue Forecast":
        "Actual revenue against the Gradient Boosting forecast.",

    "Monthly Upload":
        "Interface for the existing monthly ZIP upload pipeline.",

    "AI Assistant":
        "Natural-language questions over the data warehouse.",
}


# ============================================================
# POWER BI REPORT
# ============================================================

# Local Power BI Desktop report shipped with the repository.

POWER_BI_REPORT_FILENAME = "Sales_Analytics_Platform.pbix"

POWER_BI_REPORT_PATH = PROJECT_ROOT / "powerbi" / POWER_BI_REPORT_FILENAME

# Dashboard pages already built inside the PBIX report (display only).

POWER_BI_DASHBOARDS = (
    {
        "name": "Executive Dashboard",
        "description": (
            "Company-wide revenue, orders and KPI overview."
        ),
    },
    {
        "name": "Sales Analysis",
        "description": (
            "Revenue, orders, freight and payment analysis."
        ),
    },
    {
        "name": "Product Analysis",
        "description": (
            "Product and category performance and revenue analysis."
        ),
    },
    {
        "name": "Customer Analysis",
        "description": (
            "Customer revenue and purchasing behaviour."
        ),
    },
    {
        "name": "Seller Analysis",
        "description": (
            "Seller performance and revenue contribution."
        ),
    },
    {
        "name": "Revenue Forecast",
        "description": (
            "Actual revenue versus ML-based forecast."
        ),
    },
)


# ============================================================
# DATA WAREHOUSE OBJECTS
# ============================================================

# Analytical pages read from the star schema, matching the source
# already used by the Power BI report.

FACT_TABLE = "dw.FactSales"

DIMENSION_TABLES = (
    "dw.DimDate",
    "dw.DimCustomer",
    "dw.DimProduct",
    "dw.DimSeller",
    "dw.DimPayment",
)

FORECAST_TABLE = "dw.ForecastRevenue"

FORECAST_VIEW = "dw.vw_RevenueForecast"

ACTUAL_FORECAST_VIEW = "dw.vw_RevenueActualForecast"

MONTHLY_REVENUE_ML_VIEW = "dw.vw_MonthlyRevenueML"


# ============================================================
# PRODUCTION FORECAST MODEL (display only)
# ============================================================

# These values describe the current production candidate. The Streamlit
# page reads them for display and never retrains or re-runs prediction.

PRODUCTION_MODEL_TYPE = "GradientBoostingRegressor"

PRODUCTION_MODEL_VERSION = "GradientBoosting-v1"

PRODUCTION_MODEL_PATH = "ml/models/gradient_boosting_model.pkl"

PRODUCTION_METADATA_PATH = "ml/models/gradient_boosting_metadata.pkl"

PRODUCTION_FEATURES = (
    "YearNumber",
    "MonthNumber",
    "Quarter",
    "PreviousMonthRevenue",
    "Previous2MonthRevenue",
    "Previous3MonthRevenue",
    "Rolling3MonthAverage",
)

REQUIRED_FORECAST_HISTORY_MONTHS = 3


# ============================================================
# MONTHLY UPLOAD
# ============================================================

# The existing ETL reads this exact path. Streamlit must save the chosen
# ZIP here before calling pipeline.monthly_pipeline_v2. Do not change the
# ETL to look elsewhere.

UPLOAD_DIRECTORY = PROJECT_ROOT / "data" / "uploads"

PIPELINE_UPLOAD_FILENAME = "2018-09.zip"

PIPELINE_UPLOAD_PATH = UPLOAD_DIRECTORY / PIPELINE_UPLOAD_FILENAME

PIPELINE_MODULE = "pipeline.monthly_pipeline_v2"

REQUIRED_UPLOAD_FILES = (
    "customers.csv",
    "orders.csv",
    "order_items.csv",
    "payments.csv",
    "products.csv",
    "reviews.csv",
    "sellers.csv",
)

PIPELINE_STATUS_STEPS = (
    "Upload & Validation",
    "Operational Database Load",
    "Incremental Dimensions",
    "FactSales",
    "Gradient Boosting Model Retraining",
    "Next-Month Forecast",
)

NAV_PAGE_KEY = "nav_page"


# ============================================================
# QUERY BEHAVIOUR
# ============================================================

# Warehouse data changes once per monthly pipeline run, so cached query
# results can be held for a long time. Value is in seconds.

QUERY_CACHE_TTL = 600
