"""
Monthly Upload page.

This page is a user interface around the existing production pipeline:

    python -m pipeline.monthly_pipeline_v2

It does not reimplement ETL, warehouse loads, model retraining or
prediction. Those steps remain in pipeline/monthly_pipeline_v2.py.

Streamlit only:

- inspects the uploaded ZIP in memory
- saves it to the path already expected by etl.monthly_upload_etl
- starts the existing pipeline module
- reads the latest forecast with SELECT after success
"""

import io
import os
import re
import subprocess
import sys
import zipfile

from pathlib import Path, PurePosixPath

import pandas as pd
import streamlit as st

import config
import db
from utils.formatting import (
    format_currency_full,
    format_month_year,
    format_percent,
)


LATEST_FORECAST_SQL = """
SELECT TOP 1
    ForecastYear,
    ForecastMonth,
    ForecastYearMonth,
    PredictedRevenue,
    ModelVersion,
    PredictionDate
FROM dw.vw_RevenueForecast
ORDER BY ForecastYear DESC, ForecastMonth DESC;
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

EXISTING_MONTH_SQL = """
SELECT
    YearMonth,
    MonthlyRevenue,
    TotalOrders
FROM dw.vw_MonthlyRevenueML
WHERE YearMonth = ?;
"""


# ============================================================
# PAGE
# ============================================================

def render():
    """
    Render the Monthly Upload page.
    """

    st.subheader("Monthly Upload")

    st.write("Upload monthly sales data and run the automated analytics pipeline.")

    uploaded_file = st.file_uploader(
        "Upload Monthly Sales ZIP",
        type=["zip"],
        accept_multiple_files=False,
    )

    if uploaded_file is None:

        _render_previous_result()
        return

    file_bytes = uploaded_file.getvalue()
    file_name = Path(uploaded_file.name).name
    file_size = uploaded_file.size if uploaded_file.size else len(file_bytes)

    st.write(f"**File name:** {file_name}")
    st.write(f"**File size:** {_format_file_size(file_size)}")

    inspection = inspect_zip(file_bytes, original_name=file_name)

    _render_validation(inspection)

    if not inspection["ok"]:

        _render_previous_result()
        return

    executed = _render_confirmation(inspection, file_bytes)

    if not executed:

        _render_previous_result()


# ============================================================
# ZIP INSPECTION
# ============================================================

def inspect_zip(file_bytes, original_name="upload.zip"):
    """
    Basic in-memory ZIP checks. This does not replace ETL validation and
    does not write to disk or the database.
    """

    result = {
        "ok": False,
        "original_name": original_name,
        "required": {name: False for name in config.REQUIRED_UPLOAD_FILES},
        "missing": list(config.REQUIRED_UPLOAD_FILES),
        "unsafe_entries": [],
        "csv_files": [],
        "detected_months": [],
        "detected_month": None,
        "errors": [],
    }

    if not file_bytes:

        result["errors"].append("The uploaded file is empty.")
        return result

    if not zipfile.is_zipfile(io.BytesIO(file_bytes)):

        result["errors"].append("The selected file is not a valid ZIP archive.")
        return result

    try:

        with zipfile.ZipFile(io.BytesIO(file_bytes)) as archive:

            entries = archive.infolist()

            if not entries:

                result["errors"].append("The ZIP archive is empty.")
                return result

            for info in entries:

                if _is_unsafe_zip_entry(info.filename):

                    result["unsafe_entries"].append(info.filename)

            if result["unsafe_entries"]:

                result["errors"].append(
                    "The ZIP contains unsafe paths and will not be processed."
                )
                return result

            present = set()

            for info in entries:

                if info.is_dir():

                    continue

                base_name = Path(info.filename.replace("\\", "/")).name.lower()

                if base_name.endswith(".csv"):

                    result["csv_files"].append(base_name)
                    present.add(base_name)

            result["required"] = {
                name: name in present
                for name in config.REQUIRED_UPLOAD_FILES
            }
            result["missing"] = [
                name
                for name, found in result["required"].items()
                if not found
            ]

            if result["missing"]:

                result["errors"].append("Required CSV files are missing.")
                return result

            result["detected_months"] = _detect_upload_months(archive)

    except zipfile.BadZipFile:

        result["errors"].append("The selected file is not a valid ZIP archive.")
        return result

    except Exception as error:

        result["errors"].append(f"The ZIP could not be read: {error}")
        return result

    if len(result["detected_months"]) == 1:

        result["detected_month"] = result["detected_months"][0]

    result["ok"] = True
    return result


def _is_unsafe_zip_entry(name):
    """
    Reject absolute paths and parent-directory traversal inside the ZIP.
    """

    if not name:

        return True

    normalised = name.replace("\\", "/")

    if normalised.startswith("/") or normalised.startswith("//"):

        return True

    path = PurePosixPath(normalised)

    if path.is_absolute():

        return True

    if any(part == ".." for part in path.parts):

        return True

    first = path.parts[0] if path.parts else ""

    if re.match(r"^[A-Za-z]:$", first):

        return True

    if ":" in first:

        return True

    return False


def _detect_upload_months(archive):
    """
    Read order_purchase_timestamp from orders.csv when present.
    """

    orders_member = None

    for info in archive.infolist():

        if info.is_dir():

            continue

        base_name = Path(info.filename.replace("\\", "/")).name.lower()

        if base_name == "orders.csv":

            orders_member = info.filename
            break

    if orders_member is None:

        return []

    try:

        with archive.open(orders_member) as handle:

            orders = pd.read_csv(handle)

    except Exception:

        return []

    if "order_purchase_timestamp" not in orders.columns:

        return []

    timestamps = pd.to_datetime(
        orders["order_purchase_timestamp"],
        errors="coerce",
    )

    months = (
        timestamps.dt.to_period("M")
        .dropna()
        .astype(str)
        .unique()
        .tolist()
    )

    months.sort()
    return months


# ============================================================
# VALIDATION UI
# ============================================================

def _render_validation(inspection):

    st.markdown("### Upload Validation")

    st.write(f"**File:** {inspection['original_name']}")

    st.markdown("**Required files:**")

    for name in config.REQUIRED_UPLOAD_FILES:

        marker = "✓" if inspection["required"].get(name) else "✗"
        st.write(f"{marker} {name}")

    if inspection["unsafe_entries"]:

        st.error("Unsafe ZIP entries were found. The pipeline will not be started.")

        with st.expander("Unsafe entries"):

            for entry in inspection["unsafe_entries"]:

                st.code(entry, language="text")

        return

    if inspection["missing"]:

        st.error("Basic ZIP validation failed. Missing required files:")

        for name in inspection["missing"]:

            st.write(f"- {name}")

        return

    for message in inspection["errors"]:

        st.error(message)
        return

    st.success("Basic ZIP validation passed.")

    detected = inspection.get("detected_month")
    months = inspection.get("detected_months") or []

    if detected:

        year, month = detected.split("-")
        st.write(f"**Detected upload month:** {format_month_year(year, month)} (`{detected}`)")

    elif not months:

        st.info("The upload month could not be detected from orders.csv.")

    else:

        st.warning(
            "The ZIP does not contain a single upload month. "
            "The existing pipeline requires exactly one month and may reject this file."
        )
        st.write("Detected months: " + ", ".join(months))


def _render_confirmation(inspection, file_bytes):

    st.markdown("### Ready to process upload")

    st.write(f"**File name:** {inspection['original_name']}")
    st.caption(
        "The existing pipeline reads "
        f"`data/uploads/{config.PIPELINE_UPLOAD_FILENAME}`. "
        "The selected ZIP will be saved to that path when you run the pipeline."
    )

    already_processed = False
    detected = inspection.get("detected_month")

    if detected:

        already_processed = _month_already_processed(detected)

        if already_processed:

            st.warning(
                "This upload may already have been processed. "
                "Please verify before continuing."
            )

    if st.button("Run Monthly Pipeline", type="primary", key="run_monthly_pipeline"):

        _execute_pipeline(file_bytes, inspection)
        return True

    return False


# ============================================================
# DUPLICATE CHECK
# ============================================================

def _month_already_processed(year_month):
    """
    Read-only check against the warehouse monthly revenue view.
    """

    try:

        frame = db.run_query(EXISTING_MONTH_SQL, params=(year_month,))

    except Exception:

        return False

    return frame is not None and not frame.empty


# ============================================================
# PIPELINE EXECUTION
# ============================================================

def _execute_pipeline(file_bytes, inspection):

    try:

        saved_path = _save_upload(file_bytes)

    except Exception as error:

        st.error("The uploaded ZIP could not be saved.")
        st.code(str(error), language="text")
        return

    st.write(f"Saved upload to `{saved_path}`.")

    st.markdown("### Pipeline Status")

    step_placeholder = st.empty()
    log_placeholder = st.empty()

    completed_steps = set()
    active_step = 0
    logs = []

    _render_status_steps(step_placeholder, completed_steps, active_step)

    try:

        process = subprocess.Popen(
            [sys.executable, "-u", "-m", config.PIPELINE_MODULE],
            cwd=str(config.PROJECT_ROOT),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
            env=_unbuffered_env(),
        )

    except Exception as error:

        st.error("Monthly pipeline failed.")
        st.code(str(error), language="text")
        return

    assert process.stdout is not None

    for line in process.stdout:

        logs.append(line.rstrip())
        active_step, newly_completed = _progress_from_line(
            line,
            active_step,
            completed_steps,
        )
        completed_steps.update(newly_completed)
        _render_status_steps(step_placeholder, completed_steps, active_step)
        log_placeholder.code("\n".join(logs[-80:]), language="text")

    return_code = process.wait()

    result = {
        "return_code": return_code,
        "ok": return_code == 0,
        "logs": "\n".join(logs),
        "file_name": inspection["original_name"],
        "detected_month": inspection.get("detected_month"),
        "forecast": None,
    }

    if return_code == 0:

        completed_steps = set(range(len(config.PIPELINE_STATUS_STEPS)))
        _render_status_steps(step_placeholder, completed_steps, None)
        _clear_query_cache()
        result["forecast"] = _load_forecast_summary()
        st.success("Monthly pipeline completed successfully.")

    else:

        _render_status_steps(
            step_placeholder,
            completed_steps,
            active_step,
            failed=True,
        )
        st.error("Monthly pipeline failed.")

    st.session_state["pipeline_result"] = result

    with st.expander("Pipeline Logs", expanded=return_code != 0):

        st.code(result["logs"] or "(no output)", language="text")

    if result["ok"]:

        _render_forecast_result(result["forecast"])


def _save_upload(file_bytes):
    """
    Write the ZIP to the filename already expected by etl.monthly_upload_etl.
    """

    config.UPLOAD_DIRECTORY.mkdir(parents=True, exist_ok=True)

    target = config.PIPELINE_UPLOAD_PATH
    partial = target.with_name(target.name + ".partial")

    partial.write_bytes(file_bytes)
    os.replace(partial, target)

    return target


def _unbuffered_env():

    env = os.environ.copy()
    env["PYTHONUNBUFFERED"] = "1"
    env["PYTHONIOENCODING"] = "utf-8"
    return env


def _progress_from_line(line, active_step, completed_steps):
    """
    Map existing pipeline stdout onto the six status steps.
    """

    text = line.lower()
    completed = set()

    markers = [
        (0, "running: etl.monthly_upload_etl"),
        (0, "upload validation successful"),
        (1, "starting database load"),
        (1, "database load successful"),
        (2, "running sql: incremental_dim_"),
        (3, "running sql: incremental_fact_sales.sql"),
        (4, "running: ml.pipeline.retrain_model_v2"),
        (5, "running: ml.pipeline.predict_next_month_v2"),
        (5, "monthly pipeline v2 completed"),
    ]

    for step_index, marker in markers:

        if marker not in text:

            continue

        if step_index > 0:

            completed.update(range(step_index))

        if "successful" in marker or "completed" in marker:

            completed.add(step_index)

        active_step = max(active_step, step_index)

    return active_step, completed


def _render_status_steps(placeholder, completed_steps, active_step, failed=False):

    lines = []

    for index, label in enumerate(config.PIPELINE_STATUS_STEPS):

        if index in completed_steps:

            mark = "✓"
        elif failed and index == active_step:

            mark = "✗"
        elif index == active_step:

            mark = "…"
        else:

            mark = "○"

        lines.append(f"{mark}  {label}")

    placeholder.markdown("\n\n".join(lines))


# ============================================================
# FORECAST RESULT
# ============================================================

def _load_forecast_summary():
    """
    Read-only latest forecast, using the same sources as Revenue Forecast.
    """

    try:

        forecast_frame = db.run_query(LATEST_FORECAST_SQL)
        monthly_frame = db.run_query(MONTHLY_REVENUE_SQL)

    except Exception:

        return None

    if forecast_frame is None or forecast_frame.empty:

        return None

    forecast = forecast_frame.iloc[0]
    forecast_year = int(forecast["ForecastYear"])
    forecast_month = int(forecast["ForecastMonth"])
    forecast_revenue = float(forecast["PredictedRevenue"])

    previous_year, previous_month = (
        (forecast_year - 1, 12)
        if forecast_month == 1
        else (forecast_year, forecast_month - 1)
    )

    previous_revenue = None

    if monthly_frame is not None and not monthly_frame.empty:

        matched = monthly_frame[
            (monthly_frame["YearNumber"] == previous_year)
            & (monthly_frame["MonthNumber"] == previous_month)
        ]

        if not matched.empty:

            previous_revenue = float(matched.iloc[0]["MonthlyRevenue"])

    change_pct = None

    if previous_revenue not in (None, 0):

        change_pct = ((forecast_revenue - previous_revenue) / previous_revenue) * 100

    return {
        "label": format_month_year(forecast_year, forecast_month),
        "forecast_revenue": forecast_revenue,
        "previous_revenue": previous_revenue,
        "change_pct": change_pct,
        "model_version": forecast.get("ModelVersion"),
    }


def _render_forecast_result(summary):

    st.markdown("### Latest Forecast")

    if not summary:

        st.info("The pipeline finished, but no revenue forecast is currently available.")
        return

    one, two, three = st.columns(3)

    with one:

        st.write("Forecast Month")
        st.write(summary["label"])

    with two:

        st.write("Forecast Revenue")
        st.write(format_currency_full(summary["forecast_revenue"]))

    with three:

        st.write("Previous Month Revenue")
        st.write(format_currency_full(summary["previous_revenue"]))

    st.write("Forecast Change %")
    st.write(format_percent(summary["change_pct"]))

    if st.button("View Revenue Forecast", key="view_revenue_forecast"):

        st.session_state[config.NAV_PAGE_KEY] = "Revenue Forecast"
        st.rerun()


def _render_previous_result():

    result = st.session_state.get("pipeline_result")

    if not result:

        return

    st.divider()
    st.markdown("### Last pipeline run")

    if result.get("ok"):

        st.success("Monthly pipeline completed successfully.")
        _render_forecast_result(result.get("forecast"))

    else:

        st.error("Monthly pipeline failed.")

    with st.expander("Pipeline Logs"):

        st.code(result.get("logs") or "(no output)", language="text")


def _clear_query_cache():

    try:

        db.run_query.clear()

    except Exception:

        pass


def _format_file_size(size_bytes):

    size = int(size_bytes or 0)

    if size < 1024:

        return f"{size} bytes"

    if size < 1024 * 1024:

        return f"{size / 1024:.1f} KB"

    return f"{size / (1024 * 1024):.2f} MB"
