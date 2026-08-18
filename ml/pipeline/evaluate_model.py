import pandas as pd
import numpy as np

from etl.db_connection import get_connection

from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score
)


# ============================================================
# CONNECT TO SQL SERVER
# ============================================================

connection = get_connection()

if connection is None:
    raise Exception("Failed to connect to SQL Server.")

print("Connected to SQL Server Successfully")


# ============================================================
# LOAD VALID ML DATA
# ============================================================

query = """
SELECT *
FROM dw.vw_MonthlyRevenueML
ORDER BY YearNumber, MonthNumber;
"""

df = pd.read_sql(query, connection)

connection.close()

print("\nMonthly Revenue Loaded Successfully")
print(f"Valid ML Months : {len(df)}")


# ============================================================
# FEATURE ENGINEERING
# ============================================================

df["Quarter"] = (
    (df["MonthNumber"] - 1) // 3
) + 1

df["PreviousMonthRevenue"] = (
    df["MonthlyRevenue"].shift(1)
)

# First month has no previous-month revenue
df = df.dropna().reset_index(drop=True)

print("\nFeature Engineering Completed")
print(f"Total Usable Rows : {len(df)}")


# ============================================================
# PREPARE FEATURES
# ============================================================

features = [
    "YearNumber",
    "MonthNumber",
    "Quarter",
    "PreviousMonthRevenue"
]

X = df[features]
y = df["MonthlyRevenue"]


# ============================================================
# TIME-BASED TRAIN / TEST SPLIT
# ============================================================

# Use the final 4 months as the test period.
# This simulates forecasting future months.

test_size = 4

train = df.iloc[:-test_size].copy()
test = df.iloc[-test_size:].copy()

X_train = train[features]
y_train = train["MonthlyRevenue"]

X_test = test[features]
y_test = test["MonthlyRevenue"]

print("\nTime-Based Train/Test Split")

print(f"Training Rows : {len(train)}")
print(f"Testing Rows  : {len(test)}")

print("\nTesting Months")
print(
    test[
        [
            "YearMonth",
            "MonthlyRevenue"
        ]
    ]
)


# ============================================================
# STANDARDIZATION
# ============================================================

scaler = StandardScaler()

X_train_scaled = scaler.fit_transform(X_train)

X_test_scaled = scaler.transform(X_test)

print("\nFeature Standardization Completed")


# ============================================================
# TRAIN MODEL
# ============================================================

model = LinearRegression()

model.fit(
    X_train_scaled,
    y_train
)

print("Model Trained Successfully")


# ============================================================
# PREDICTIONS
# ============================================================

predictions = model.predict(
    X_test_scaled
)

test["PredictedRevenue"] = predictions


# ============================================================
# DISPLAY PREDICTIONS
# ============================================================

print("\n========== MODEL PREDICTIONS ==========")

print(
    test[
        [
            "YearMonth",
            "MonthlyRevenue",
            "PredictedRevenue"
        ]
    ]
)


# ============================================================
# MODEL METRICS
# ============================================================

mae = mean_absolute_error(
    y_test,
    predictions
)

rmse = np.sqrt(
    mean_squared_error(
        y_test,
        predictions
    )
)

r2 = r2_score(
    y_test,
    predictions
)

# Avoid division by zero
non_zero_actuals = y_test != 0

mape = (
    np.mean(
        np.abs(
            (
                y_test[non_zero_actuals]
                - predictions[non_zero_actuals]
            )
            /
            y_test[non_zero_actuals]
        )
    )
    * 100
)


# ============================================================
# DISPLAY METRICS
# ============================================================

print("\n========== MODEL EVALUATION ==========")

print(
    f"MAE  : {mae:,.2f}"
)

print(
    f"RMSE : {rmse:,.2f}"
)

print(
    f"MAPE : {mape:.2f}%"
)

print(
    f"R²   : {r2:.4f}"
)


print("\nModel evaluation completed successfully.")