import os
import joblib
import pandas as pd

from etl.db_connection import get_connection

from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler



# Connect to SQL Server


connection = get_connection()

if connection is None:
    raise Exception("Failed to connect to SQL Server.")

print("Connected to SQL Server Successfully")



# Read Monthly Revenue View


query = """
SELECT *
FROM dw.vw_MonthlyRevenueML
ORDER BY YearNumber, MonthNumber;
"""

df = pd.read_sql(query, connection)

connection.close()

print("\nMonthly Revenue Loaded Successfully")
print(f"Rows Before Filtering : {len(df)}")



# Remove Known Incomplete Historical Data


df = df[
    ~(
        (df["YearNumber"] == 2016)
        |
        (
            (df["YearNumber"] == 2018)
            & (df["MonthNumber"] == 9)
            & (df["TotalOrders"] == 1)
        )
    )
].copy()

print("\nKnown Incomplete Historical Data Removed")

print(f"Rows After Filtering : {len(df)}")

print("\nRemaining Months")

print(df[["YearMonth", "TotalOrders"]])



# Feature Engineering


df["Quarter"] = ((df["MonthNumber"] - 1) // 3) + 1

df["PreviousMonthRevenue"] = df["MonthlyRevenue"].shift(1)

# Remove first row because it has no previous month
df = df.dropna().reset_index(drop=True)

print("\nFeature Engineering Completed")

print(df.head())

print(f"\nTraining Rows : {len(df)}")



# Prepare Training Data


X = df[
    [
        "YearNumber",
        "MonthNumber",
        "Quarter",
        "PreviousMonthRevenue"
    ]
]

y = df["MonthlyRevenue"]

print("\nTraining Features Ready")

print(X.head())



# Standardize Features


scaler = StandardScaler()

X_scaled = scaler.fit_transform(X)

print("\nFeature Standardization Completed")


# Train Linear Regression Model


model = LinearRegression()

model.fit(X_scaled, y)

print("Final Model Trained Successfully")



# Save Model and Scaler


os.makedirs("ml/models", exist_ok=True)

joblib.dump(
    model,
    "ml/models/linear_regression_model.pkl"
)

joblib.dump(
    scaler,
    "ml/models/scaler.pkl"
)

print("\nModel Saved Successfully")
print("Scaler Saved Successfully")