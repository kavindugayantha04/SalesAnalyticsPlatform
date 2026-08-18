import os

import joblib
import pandas as pd

from etl.db_connection import get_connection


MODEL_DIR = "ml/models"

MODEL_PATH = os.path.join(MODEL_DIR, "gradient_boosting_model.pkl")

METADATA_PATH = os.path.join(MODEL_DIR, "gradient_boosting_metadata.pkl")

EXPECTED_MODEL_TYPE = "GradientBoostingRegressor"

EXPECTED_FEATURES = [
    "YearNumber",
    "MonthNumber",
    "Quarter",
    "PreviousMonthRevenue",
    "Previous2MonthRevenue",
    "Previous3MonthRevenue",
    "Rolling3MonthAverage",
]

# Number of completed months required to build the lag features.
REQUIRED_HISTORY_MONTHS = 3


# ============================================================
# LOAD VALID ML DATA
# ============================================================

connection = get_connection()

if connection is None:
    raise Exception("Failed to connect to SQL Server.")

print("Connected to SQL Server Successfully")

query = """
SELECT *
FROM dw.vw_MonthlyRevenueML
ORDER BY YearNumber, MonthNumber;
"""

df = pd.read_sql(query, connection)

connection.close()

# The view already excludes incomplete historical months through
# dw.MLExcludedOrders, so every returned month is treated as valid.

df = df.sort_values(["YearNumber", "MonthNumber"]).reset_index(drop=True)

print("\n========== DATA LOADED ==========")
print(f"Valid ML Months Loaded : {len(df)}")


# ============================================================
# FEATURE VALIDATION
# ============================================================

if len(df) < REQUIRED_HISTORY_MONTHS:
    raise Exception("Insufficient historical data to generate forecast.")


# ============================================================
# LATEST VALID MONTH
# ============================================================

latest_month = df.iloc[-1]

latest_year = int(latest_month["YearNumber"])
latest_month_number = int(latest_month["MonthNumber"])

print("\n========== LATEST VALID MONTH ==========")
print(f"Latest Valid Month : {latest_year}-{latest_month_number:02d}")
print(f"Year               : {latest_year}")
print(f"Month              : {latest_month_number}")
print(f"Revenue            : {latest_month['MonthlyRevenue']:,.2f}")


# ============================================================
# FORECAST MONTH
# ============================================================

if latest_month_number == 12:
    forecast_year = latest_year + 1
    forecast_month = 1
else:
    forecast_year = latest_year
    forecast_month = latest_month_number + 1

forecast_quarter = ((forecast_month - 1) // 3) + 1

print("\n========== FORECAST MONTH ==========")
print(f"Forecast Month : {forecast_year}-{forecast_month:02d}")
print(f"Year           : {forecast_year}")
print(f"Month          : {forecast_month}")
print(f"Quarter        : {forecast_quarter}")


# ============================================================
# CREATE FUTURE FEATURES
# ============================================================

# Only completed historical months feed the lag features. The forecast
# month has no revenue yet, so nothing about it enters the input.
recent_history = df.iloc[-REQUIRED_HISTORY_MONTHS:]

previous_month_revenue = float(df["MonthlyRevenue"].iloc[-1])
previous_2_month_revenue = float(df["MonthlyRevenue"].iloc[-2])
previous_3_month_revenue = float(df["MonthlyRevenue"].iloc[-3])

rolling_3_month_average = float(recent_history["MonthlyRevenue"].mean())

lag_values = {
    "PreviousMonthRevenue": previous_month_revenue,
    "Previous2MonthRevenue": previous_2_month_revenue,
    "Previous3MonthRevenue": previous_3_month_revenue,
    "Rolling3MonthAverage": rolling_3_month_average,
}

if any(pd.isna(value) for value in lag_values.values()):
    raise Exception("Insufficient historical data to generate forecast.")

X_future = pd.DataFrame(
    {
        "YearNumber": [forecast_year],
        "MonthNumber": [forecast_month],
        "Quarter": [forecast_quarter],
        "PreviousMonthRevenue": [previous_month_revenue],
        "Previous2MonthRevenue": [previous_2_month_revenue],
        "Previous3MonthRevenue": [previous_3_month_revenue],
        "Rolling3MonthAverage": [rolling_3_month_average],
    }
)

print("\n========== PREDICTION INPUT ==========")
print("Historical Months Used")
print(
    recent_history[["YearMonth", "MonthlyRevenue"]].to_string(index=False)
)

print("\nPrediction Input")
print(f"YearNumber            : {forecast_year}")
print(f"MonthNumber           : {forecast_month}")
print(f"Quarter               : {forecast_quarter}")
print(f"PreviousMonthRevenue  : {previous_month_revenue:,.2f}")
print(f"Previous2MonthRevenue : {previous_2_month_revenue:,.2f}")
print(f"Previous3MonthRevenue : {previous_3_month_revenue:,.2f}")
print(f"Rolling3MonthAverage  : {rolling_3_month_average:,.2f}")


# ============================================================
# LOAD MODEL
# ============================================================

if not os.path.exists(MODEL_PATH):
    raise Exception(
        f"Gradient Boosting model not found at {MODEL_PATH}. "
        "Run ml/pipeline/retrain_model_v2.py first."
    )

if not os.path.exists(METADATA_PATH):
    raise Exception(
        f"Gradient Boosting metadata not found at {METADATA_PATH}. "
        "Run ml/pipeline/retrain_model_v2.py first."
    )

model = joblib.load(MODEL_PATH)

metadata = joblib.load(METADATA_PATH)

if metadata.get("model_type") != EXPECTED_MODEL_TYPE:
    raise Exception(
        "Model metadata mismatch. "
        f"Expected model_type '{EXPECTED_MODEL_TYPE}' "
        f"but found '{metadata.get('model_type')}'."
    )

if list(metadata.get("features", [])) != EXPECTED_FEATURES:
    raise Exception(
        "Model metadata mismatch. "
        f"Expected features {EXPECTED_FEATURES} "
        f"but found {metadata.get('features')}."
    )

# Gradient Boosting needs no scaling, so raw feature values are used.
# Column order follows the metadata to match training exactly.
X_future = X_future[list(metadata["features"])]

model_version = metadata["model_version"]

print("\n========== MODEL LOADED ==========")
print(f"Model File    : {MODEL_PATH}")
print(f"Metadata File : {METADATA_PATH}")
print(f"Model Type    : {metadata['model_type']}")
print(f"Model Version : {model_version}")
print("Metadata feature list verified successfully")


# ============================================================
# GENERATE FORECAST
# ============================================================

predicted_revenue = float(model.predict(X_future)[0])

print("\n========== REVENUE FORECAST ==========")
print(f"Forecast Month : {forecast_year}-{forecast_month:02d}")
print(f"Predicted Revenue : {predicted_revenue:,.2f}")


# ============================================================
# DATABASE FORECAST STORAGE
# ============================================================

connection = get_connection()

if connection is None:
    raise Exception("Failed to connect to SQL Server.")

cursor = connection.cursor()

print("\n========== DATABASE FORECAST STORAGE ==========")

check_query = """
SELECT ForecastID
FROM dw.ForecastRevenue
WHERE ForecastYear = ?
AND ForecastMonth = ?;
"""

cursor.execute(
    check_query,
    forecast_year,
    forecast_month,
)

existing_forecast = cursor.fetchone()

if existing_forecast:

    update_query = """
    UPDATE dw.ForecastRevenue
    SET
        PredictedRevenue = ?,
        ModelVersion = ?,
        PredictionDate = GETDATE()
    WHERE ForecastYear = ?
    AND ForecastMonth = ?;
    """

    cursor.execute(
        update_query,
        predicted_revenue,
        model_version,
        forecast_year,
        forecast_month,
    )

    print("Existing Forecast Updated Successfully")

else:

    insert_query = """
    INSERT INTO dw.ForecastRevenue
    (
        ForecastYear,
        ForecastMonth,
        PredictedRevenue,
        ModelVersion
    )
    VALUES (?, ?, ?, ?);
    """

    cursor.execute(
        insert_query,
        forecast_year,
        forecast_month,
        predicted_revenue,
        model_version,
    )

    print("New Forecast Inserted Successfully")

connection.commit()

cursor.close()
connection.close()

print(f"Forecast : {forecast_year}-{forecast_month:02d}")
print(f"Predicted Revenue : {predicted_revenue:,.2f}")


# ============================================================
# PREDICTION COMPLETED
# ============================================================

print("\n========== PREDICTION COMPLETED ==========")
print("Gradient Boosting next-month prediction completed successfully.")
print("Existing Linear Regression prediction files were not modified.")
print("No operational or warehouse data was modified.")
