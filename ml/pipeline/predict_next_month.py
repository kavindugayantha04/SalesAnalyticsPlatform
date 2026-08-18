import joblib
import pandas as pd

from etl.db_connection import get_connection


# Connect to SQL Server
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

print("\nMonthly Revenue Loaded Successfully")
print(f"Valid ML Months Loaded : {len(df)}")

print("\nValid Monthly Data")

print(df[[
    "YearMonth",
    "MonthlyRevenue",
    "TotalOrders"
]])



# Identify Latest Valid Month

df = df.sort_values(
    ["YearNumber", "MonthNumber"]
).reset_index(drop=True)

latest_month = df.iloc[-1]

print("\nLatest Valid Month")

print(f"Year    : {latest_month['YearNumber']}")
print(f"Month   : {latest_month['MonthNumber']}")
print(f"Revenue : {latest_month['MonthlyRevenue']}")


# Determine Next Month

latest_year = int(latest_month["YearNumber"])
latest_month_number = int(latest_month["MonthNumber"])

if latest_month_number == 12:
    forecast_year = latest_year + 1
    forecast_month = 1
else:
    forecast_year = latest_year
    forecast_month = latest_month_number + 1

print("\nForecast Month")

print(f"Year  : {forecast_year}")
print(f"Month : {forecast_month}")

# Calculate Forecast Quarter

forecast_quarter = ((forecast_month - 1) // 3) + 1

print(f"Quarter : {forecast_quarter}")


# Prepare Prediction Input

X_future = pd.DataFrame({
    "YearNumber": [forecast_year],
    "MonthNumber": [forecast_month],
    "Quarter": [forecast_quarter],
    "PreviousMonthRevenue": [
        latest_month["MonthlyRevenue"]
    ]
})

print("\nPrediction Input")

print(X_future)

# Load Trained Model and Scaler
model = joblib.load(
    "ml/models/linear_regression_model.pkl"
)

scaler = joblib.load(
    "ml/models/scaler.pkl"
)

print("\nModel and Scaler Loaded Successfully")

# Standardize Prediction Input

X_future_scaled = scaler.transform(X_future)

print("Prediction Input Standardized")


# Predict Next Month Revenue

predicted_revenue = model.predict(X_future_scaled)[0]

print("\n========== Revenue Forecast ==========")

print(f"Forecast Month : {forecast_year}-{forecast_month:02d}")

print(f"Predicted Revenue : {predicted_revenue:,.2f}")



# Save / Update Forecast in SQL Server


connection = get_connection()

if connection is None:
    raise Exception("Failed to connect to SQL Server.")

cursor = connection.cursor()

model_version = "LinearRegression-v1"


# Check whether forecast already exists
check_query = """
SELECT ForecastID
FROM dw.ForecastRevenue
WHERE ForecastYear = ?
AND ForecastMonth = ?;
"""

cursor.execute(
    check_query,
    forecast_year,
    forecast_month
)

existing_forecast = cursor.fetchone()



# Update Existing Forecast


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
        float(predicted_revenue),
        model_version,
        forecast_year,
        forecast_month
    )

    print("\nExisting Forecast Updated Successfully")



# Insert New Forecast


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
        float(predicted_revenue),
        model_version
    )

    print("\nNew Forecast Inserted Successfully")


connection.commit()

cursor.close()
connection.close()


print(
    f"Forecast : "
    f"{forecast_year}-{forecast_month:02d}"
)

print(
    f"Predicted Revenue : "
    f"{predicted_revenue:,.2f}"
)


