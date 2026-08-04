import pandas as pd

from etl.db_connection import get_connection

# Connect to SQL Server


connection = get_connection()

if connection is None:
    raise Exception("Failed to connect to SQL Server.")


# Read Monthly Revenue View


query = """
SELECT *
FROM dw.vw_MonthlyRevenueML
ORDER BY YearNumber, MonthNumber;
"""

# Load data into DataFrame


df = pd.read_sql(query, connection)

connection.close()

# Dataset Information


print("\nMonthly Revenue Dataset Loaded Successfully!\n")

print(f"Rows    : {df.shape[0]}")
print(f"Columns : {df.shape[1]}")

print("\nFirst 5 Rows")
print(df.head())

print("\nLast 5 Rows")
print(df.tail())


# Missing Values


print("\nMissing Values")

print(df.isnull().sum())

# Keep only complete months:
# January 2017 to August 2018

df = df[
    (
        (df["YearNumber"] == 2017)
        |
        (
            (df["YearNumber"] == 2018)
            &
            (df["MonthNumber"] <= 8)
        )
    )
].copy()

print(f"\nRemaining Months : {len(df)}")

print("\nFiltered Dataset")

print(df)


print(f"Start Month : {df.iloc[0]['YearMonth']}")
print(f"End Month   : {df.iloc[-1]['YearMonth']}")

# Save Dataset

output_path = "ml/data/monthly_sales_ml.csv"
df.to_csv(output_path, index=False)
print("\nDataset saved successfully!")

print(f"Location : {output_path}")