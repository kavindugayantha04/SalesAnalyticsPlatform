import pandas as pd

from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt
import os

from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score
)

# Load Feature Dataset

input_file = "ml/data/sales_features.csv"
df=pd.read_csv(input_file)

print(df.head())

print(df.shape)

# Select Input Features (X)

X = df[
    [
        "YearNumber",
        "MonthNumber",
        "Quarter",
        "PreviousMonthRevenue",
       
    ]
]

# Select Target Variable (y)

y = df["MonthlyRevenue"]

print("\nInput Features (X)")

print(X.head())

print("\nTarget Variable (y)")

print(y.head())

# Split Data into Training and Testing Sets

X_train, X_test, y_train, y_test=train_test_split(X,y, test_size=0.2, shuffle=False)

print(f"X_train : {X_train.shape}")
print(f"y_train : {y_train.shape}")

print(f"X_test : {X_test.shape}")
print(f"y_test : {y_test.shape}")

# Standardize Input Features

scaler = StandardScaler()

X_train = scaler.fit_transform(X_train)

X_test = scaler.transform(X_test)

# Train Linear Regression Model

model = LinearRegression()

model.fit(X_train, y_train)


# Predict Monthly Revenue

y_pred = model.predict(X_test)

print("\nPredicted Revenue")

print(y_pred)


# Evaluate Model Performance

mae = mean_absolute_error(y_test, y_pred)

mse = mean_squared_error(y_test, y_pred)

rmse = mse ** 0.5

r2 = r2_score(y_test, y_pred)

print("\nModel Evaluation ")

print(f"Mean Absolute Error (MAE) : {mae:,.2f}")

print(f"Root Mean Squared Error (RMSE) : {rmse:,.2f}")

print(f"R² Score : {r2:.4f}")

# Actual vs Predicted Revenue

results = pd.DataFrame({
    "Actual Revenue": y_test.values,
    "Predicted Revenue": y_pred
})

results["Difference"] = (
    results["Predicted Revenue"] -
    results["Actual Revenue"]
)

print("\n========== Actual vs Predicted ==========")

print(results)

# Create output folder if it doesn't exist

os.makedirs("ml/output", exist_ok=True)

results.to_csv(
    "ml/output/predictions.csv",
    index=False
)



plt.figure(figsize=(8,5))

plt.plot(
    y_test.values,
    marker="o",
    linewidth=2,
    label="Actual"
)

plt.plot(
    y_pred,
    marker="s",
    linewidth=2,
    label="Predicted"
)

plt.title("Actual vs Predicted Revenue")

plt.xlabel("Test Months")

plt.ylabel("Revenue")

plt.legend()

plt.grid(True)

plt.show()



