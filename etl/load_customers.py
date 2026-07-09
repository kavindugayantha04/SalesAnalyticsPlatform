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

# Prepare all rows for insertion
rows = []

for _, row in df.iterrows():
    rows.append((
        row["customer_id"],
        row["customer_unique_id"],
        int(row["customer_zip_code_prefix"]),
        row["customer_city"],
        row["customer_state"]
    ))

# Insert all customers
cursor.executemany("""
INSERT INTO Customers
(
    customer_id,
    customer_unique_id,
    customer_zip_code_prefix,
    customer_city,
    customer_state
)
VALUES (?, ?, ?, ?, ?)
""", rows)

# Save changes
connection.commit()

print(f"{len(rows)} customers inserted successfully!")

cursor.close()
connection.close()