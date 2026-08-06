import os
import joblib
import pandas as pd

from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler

# Load Dataset

input_file = "ml/data/sales_features.csv"

df = pd.read_csv(input_file)

print("Dataset Loaded Successfully")

print(f"Rows : {len(df)}")


X = df[
    [
        "YearNumber",
        "MonthNumber",
        "Quarter",
        "TotalOrders",
        "AverageOrderValue",
        "PreviousMonthRevenue"
    ]
]

y = df["MonthlyRevenue"]


scaler = StandardScaler()

X_scaled = scaler.fit_transform(X)

print("Feature Standardization Completed")

model = LinearRegression()

model.fit(X_scaled, y)

print("Final Model Trained Successfully")

os.makedirs("ml/models", exist_ok=True)

joblib.dump(
    model,
    "ml/models/linear_regression_model.pkl"
)

joblib.dump(
    scaler,
    "ml/models/scaler.pkl"
)

print("Model Saved Successfully")