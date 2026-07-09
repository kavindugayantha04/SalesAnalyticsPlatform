import pandas as pd

# Read CSV
df = pd.read_csv("data/raw/olist_customers_dataset.csv")

print(df.head())

print("\nRows:", len(df))
print("Columns:", len(df.columns))

print("\nColumn Names")
print(df.columns)

print(df.isnull().sum())

from db_connection import get_connection

connection = get_connection()
cursor = connection.cursor()