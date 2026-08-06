import pandas as pd

# Load Prepared Dataset
input_file = "ml/data/monthly_sales_ml.csv"

df=pd.read_csv(input_file)

print("Dataset Loaded Successfully!\n")

print(df.head())

print("\nDataset Shape")

print(df.shape)

print("\nColumns")
print(df.columns)


# Create Quarter Feature

df["Quarter"] = ((df["MonthNumber"] - 1) // 3) + 1

print(df[["YearMonth", "Quarter"]].head())

# Create Lag Features


# Previous Month Revenue (Lag 1)
df["PreviousMonthRevenue"] = df["MonthlyRevenue"].shift(1)

print(
    df[
        [
            "YearMonth",
            "MonthlyRevenue",
            "PreviousMonthRevenue"
        ]
    ].head()
)



# Check Missing Values After Feature Engineering

print(df.isnull().sum())

# Remove rows without previous month information

df = df.dropna().reset_index(drop=True)

print("\nFinal Dataset Shape")
print(df.shape)

print("\nTraining Period")
print(f"Start : {df.iloc[0]['YearMonth']}")
print(f"End   : {df.iloc[-1]['YearMonth']}")

print("\nFinal Dataset Preview")
print(df.head())

print("\nFinal Dataset Columns")
print(df.columns)

# Save Feature Dataset

output_file = "ml/data/sales_features.csv"

df.to_csv(output_file, index=False)

print("\nFeature Engineering Completed Successfully!")
print(f"Dataset saved to: {output_file}")