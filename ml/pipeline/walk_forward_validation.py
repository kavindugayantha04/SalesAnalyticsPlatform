import pandas as pd
import numpy as np

from etl.db_connection import get_connection

from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score,
)


# Number of most recent months to validate one step at a time.
VALIDATION_MONTHS = 4

# Never let the expanding window start with fewer rows than this.
MIN_TRAINING_ROWS = 6


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
print(f"Total Valid Months : {len(df)}")


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
print(
    df[["YearMonth", "MonthlyRevenue"] + features]
    .head()
    .to_string(index=False)
)


# ============================================================
# WALK-FORWARD VALIDATION SETUP
# ============================================================

usable_rows = len(df)

max_validations = usable_rows - MIN_TRAINING_ROWS

if max_validations < 1:
    raise Exception(
        "Not enough usable months for walk-forward validation. "
        f"Usable rows: {usable_rows}, "
        f"minimum training rows required: {MIN_TRAINING_ROWS}."
    )

validation_count = min(VALIDATION_MONTHS, max_validations)

# Index of the first month that gets predicted.
first_validation_index = usable_rows - validation_count

validation_months = df["YearMonth"].iloc[first_validation_index:].tolist()

print("\n========== WALK-FORWARD VALIDATION ==========")
print(f"Total Usable Rows                  : {usable_rows}")
print(f"First Validation Month             : {validation_months[0]}")
print(f"Last Validation Month              : {validation_months[-1]}")
print(f"Number of Walk-Forward Predictions : {validation_count}")

print("\nTesting Months")
print(
    df[["YearMonth", "MonthlyRevenue"]]
    .iloc[first_validation_index:]
    .to_string(index=False)
)


# ============================================================
# MODEL DEFINITIONS
# ============================================================

# Factories so every walk-forward step trains a brand new estimator
# rather than reusing fitted state from the previous step.
model_factories = {
    "RandomForestRegressor": lambda: RandomForestRegressor(
        n_estimators=200,
        random_state=42,
    ),
    "GradientBoostingRegressor": lambda: GradientBoostingRegressor(
        n_estimators=200,
        random_state=42,
    ),
}


# ============================================================
# EXPANDING-WINDOW WALK-FORWARD LOOP
# ============================================================

records = []

for position in range(first_validation_index, usable_rows):
    train = df.iloc[:position]
    target_row = df.iloc[[position]]

    X_train = train[features]
    y_train = train["MonthlyRevenue"]

    X_target = target_row[features]

    record = {
        "YearMonth": target_row["YearMonth"].iloc[0],
        "ActualRevenue": target_row["MonthlyRevenue"].iloc[0],
    }

    for name, build_model in model_factories.items():
        model = build_model()
        model.fit(X_train, y_train)
        record[name] = model.predict(X_target)[0]

    records.append(record)

    print(
        f"Trained on {len(train)} months "
        f"({train['YearMonth'].iloc[0]} .. {train['YearMonth'].iloc[-1]}) "
        f"-> predicted {record['YearMonth']}"
    )


predictions_df = pd.DataFrame(records)


# ============================================================
# WALK-FORWARD PREDICTIONS
# ============================================================

display_df = predictions_df.rename(
    columns={
        "RandomForestRegressor": "RandomForestPrediction",
        "GradientBoostingRegressor": "GradientBoostingPrediction",
    }
)

print("\n========== WALK-FORWARD PREDICTIONS ==========")
print(
    display_df.to_string(
        index=False,
        formatters={
            column: (lambda x: f"{x:,.2f}")
            for column in display_df.columns
            if column != "YearMonth"
        },
    )
)


# ============================================================
# EVALUATION METRICS
# ============================================================

actuals = predictions_df["ActualRevenue"]

results = []

for name in model_factories:
    predictions = predictions_df[name]

    mae = mean_absolute_error(actuals, predictions)
    rmse = np.sqrt(mean_squared_error(actuals, predictions))

    # R2 is undefined for a single observation.
    if len(actuals) > 1:
        r2 = r2_score(actuals, predictions)
    else:
        r2 = np.nan

    non_zero_actuals = actuals != 0

    if non_zero_actuals.any():
        mape = (
            np.mean(
                np.abs(
                    (
                        actuals[non_zero_actuals]
                        - predictions[non_zero_actuals]
                    )
                    / actuals[non_zero_actuals]
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
print(f"Best model by RMSE : {best_row['Model']}")
print(f"Best model RMSE    : {best_row['RMSE']:,.2f}")
print(f"Best model MAPE    : {best_row['MAPE']:.2f}%")
print(f"Best model R2      : {best_row['R2']:.4f}")

print("\n========== EXPERIMENT COMPLETED ==========")
print("No models, scalers, or database records were modified.")
