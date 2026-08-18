import pandas as pd
import numpy as np

from etl.db_connection import get_connection

from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score,
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

# The view already excludes incomplete historical months through
# dw.MLExcludedOrders, so every returned month is treated as valid.

print("\n========== DATA LOADED ==========")
print(f"Total Valid Months Loaded : {len(df)}")


# ============================================================
# FEATURE ENGINEERING
# ============================================================

df = df.sort_values(["YearNumber", "MonthNumber"]).reset_index(drop=True)

df["Quarter"] = ((df["MonthNumber"] - 1) // 3) + 1

df["PreviousMonthRevenue"] = df["MonthlyRevenue"].shift(1)
df["Previous2MonthRevenue"] = df["MonthlyRevenue"].shift(2)
df["Previous3MonthRevenue"] = df["MonthlyRevenue"].shift(3)

# Shift before rolling so the current month's revenue never enters its
# own feature window.
df["Rolling3MonthAverage"] = (
    df["MonthlyRevenue"].shift(1).rolling(window=3).mean()
)

features = [
    "YearNumber",
    "MonthNumber",
    "Quarter",
    "PreviousMonthRevenue",
    "Previous2MonthRevenue",
    "Previous3MonthRevenue",
    "Rolling3MonthAverage",
]

# The earliest months lack enough history for the 3-month lags.
df = df.dropna(subset=features).reset_index(drop=True)

print("\n========== FEATURE ENGINEERING ==========")
print(f"Total Usable Rows : {len(df)}")
print("\nEngineered Features (first rows)")
print(df[["YearMonth", "MonthlyRevenue"] + features].head().to_string(index=False))


# ============================================================
# TIME-BASED TRAIN / TEST SPLIT
# ============================================================

test_size = 4

train = df.iloc[:-test_size].copy()
test = df.iloc[-test_size:].copy()

X_train = train[features]
y_train = train["MonthlyRevenue"]

X_test = test[features]
y_test = test["MonthlyRevenue"]

print("\n========== TRAIN / TEST SPLIT ==========")
print(f"Training Rows : {len(train)}")
print(f"Testing Rows  : {len(test)}")

print("\n========== TESTING MONTHS ==========")
print(test[["YearMonth", "MonthlyRevenue"]].to_string(index=False))


# ============================================================
# MODEL DEFINITIONS
# ============================================================

models = {
    "LinearRegression": {
        "estimator": LinearRegression(),
        "use_scaler": True,
    },
    "RandomForestRegressor": {
        "estimator": RandomForestRegressor(
            n_estimators=200,
            random_state=42,
        ),
        "use_scaler": False,
    },
    "GradientBoostingRegressor": {
        "estimator": GradientBoostingRegressor(
            n_estimators=200,
            random_state=42,
        ),
        "use_scaler": False,
    },
}


# ============================================================
# TRAIN, PREDICT, AND EVALUATE
# ============================================================

results = []
predictions_by_model = {}

for name, config in models.items():
    estimator = config["estimator"]

    if config["use_scaler"]:
        scaler = StandardScaler()
        X_train_fit = scaler.fit_transform(X_train)
        X_test_fit = scaler.transform(X_test)
    else:
        X_train_fit = X_train
        X_test_fit = X_test

    estimator.fit(X_train_fit, y_train)
    predictions = estimator.predict(X_test_fit)

    predictions_by_model[name] = predictions

    mae = mean_absolute_error(y_test, predictions)
    rmse = np.sqrt(mean_squared_error(y_test, predictions))
    r2 = r2_score(y_test, predictions)

    non_zero_actuals = y_test != 0

    if non_zero_actuals.any():
        mape = (
            np.mean(
                np.abs(
                    (y_test[non_zero_actuals] - predictions[non_zero_actuals])
                    / y_test[non_zero_actuals]
                )
            )
            * 100
        )
    else:
        mape = np.nan

    results.append(
        {
            "Model": name,
            "MAE": mae,
            "RMSE": rmse,
            "MAPE": mape,
            "R2": r2,
        }
    )


# ============================================================
# ACTUAL VS PREDICTED
# ============================================================

comparison_df = test[["YearMonth", "MonthlyRevenue"]].copy()

for name, predictions in predictions_by_model.items():
    comparison_df[f"{name}_Predicted"] = predictions

print("\n========== ACTUAL VS PREDICTED REVENUE ==========")
print(
    comparison_df.to_string(
        index=False,
        formatters={
            column: (lambda x: f"{x:,.2f}")
            for column in comparison_df.columns
            if column != "YearMonth"
        },
    )
)


# ============================================================
# FINAL MODEL COMPARISON TABLE
# ============================================================

results_df = pd.DataFrame(results)

print("\n========== MODEL COMPARISON ==========")
print(
    results_df.to_string(
        index=False,
        formatters={
            "MAE": lambda x: f"{x:,.2f}",
            "RMSE": lambda x: f"{x:,.2f}",
            "MAPE": lambda x: f"{x:.2f}%",
            "R2": lambda x: f"{x:.4f}",
        },
    )
)


# ============================================================
# BEST MODEL
# ============================================================

best_row = results_df.loc[results_df["RMSE"].idxmin()]

print("\n========== BEST MODEL ==========")
print(f"Best model by RMSE: {best_row['Model']}")
print(f"RMSE : {best_row['RMSE']:,.2f}")
print(f"MAPE : {best_row['MAPE']:.2f}%")

print("\n========== EXPERIMENT COMPLETED ==========")
print("No models, scalers, or database records were modified.")
