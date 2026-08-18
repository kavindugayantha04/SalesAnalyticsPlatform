import os

import joblib
import pandas as pd

from etl.db_connection import get_connection

from sklearn.ensemble import GradientBoostingRegressor


MODEL_DIR = "ml/models"

MODEL_PATH = os.path.join(MODEL_DIR, "gradient_boosting_model.pkl")

METADATA_PATH = os.path.join(MODEL_DIR, "gradient_boosting_metadata.pkl")

MODEL_VERSION = "GradientBoosting-v1"

FEATURES = [
    "YearNumber",
    "MonthNumber",
    "Quarter",
    "PreviousMonthRevenue",
    "Previous2MonthRevenue",
    "Previous3MonthRevenue",
    "Rolling3MonthAverage",
]

TARGET = "MonthlyRevenue"


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

# The view already excludes incomplete historical months through
# dw.MLExcludedOrders, so every returned month is treated as valid.

total_valid_months = len(df)

print("\n========== DATA LOADED ==========")
print(f"Total Valid Months : {total_valid_months}")


# ============================================================
# FEATURE ENGINEERING
# ============================================================

df = df.sort_values(["YearNumber", "MonthNumber"]).reset_index(drop=True)

df["Quarter"] = ((df["MonthNumber"] - 1) // 3) + 1

df["PreviousMonthRevenue"] = df[TARGET].shift(1)
df["Previous2MonthRevenue"] = df[TARGET].shift(2)
df["Previous3MonthRevenue"] = df[TARGET].shift(3)

# Shift before rolling so the current month's revenue never enters its
# own feature window.
df["Rolling3MonthAverage"] = df[TARGET].shift(1).rolling(window=3).mean()

# The earliest months lack enough history for the 3-month lags.
df = df.dropna(subset=FEATURES).reset_index(drop=True)

print("\n========== FEATURE ENGINEERING ==========")
print(f"Total Usable Rows : {len(df)}")
print("\nEngineered Features (first rows)")
print(
    df[["YearMonth", TARGET] + FEATURES]
    .head()
    .to_string(index=False)
)


# ============================================================
# TRAINING DATA
# ============================================================

# Production training uses every usable month. Validation of this
# configuration was performed separately in the experiment scripts.

X = df[FEATURES]
y = df[TARGET]

if len(df) == 0:
    raise Exception(
        "No usable training rows remain after feature engineering."
    )

print("\n========== TRAINING DATA ==========")
print(f"Total Valid Months   : {total_valid_months}")
print(f"Total Training Rows  : {len(X)}")
print(f"Training Period      : {df['YearMonth'].iloc[0]} .. {df['YearMonth'].iloc[-1]}")
print("\nTraining Features")

for feature in FEATURES:
    print(f"  - {feature}")


# ============================================================
# MODEL TRAINING
# ============================================================

# n_estimators matches the experimental runs that selected this
# configuration; no tuning is performed here.
model = GradientBoostingRegressor(
    n_estimators=200,
    random_state=42,
)

model.fit(X, y)

print("\n========== MODEL TRAINING ==========")
print("Training Completed")


# ============================================================
# MODEL SAVED
# ============================================================

os.makedirs(MODEL_DIR, exist_ok=True)

metadata = {
    "model_type": "GradientBoostingRegressor",
    "model_version": MODEL_VERSION,
    "features": FEATURES,
}

joblib.dump(model, MODEL_PATH)

joblib.dump(metadata, METADATA_PATH)

print("\n========== MODEL SAVED ==========")
print(f"Model    : {MODEL_PATH}")
print(f"Metadata : {METADATA_PATH}")


# ============================================================
# TRAINING COMPLETED
# ============================================================

print("\n========== TRAINING COMPLETED ==========")
print(f"Model Type              : {metadata['model_type']}")
print(f"Model Version           : {metadata['model_version']}")
print(f"Number of Training Rows : {len(X)}")
print("Feature Names           :")

for feature in metadata["features"]:
    print(f"  - {feature}")

print("\nGradient Boosting production candidate trained successfully.")
print("Existing Linear Regression model was not modified.")
print("No database records were modified.")
