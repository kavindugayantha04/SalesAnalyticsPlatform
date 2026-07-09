import pandas as pd
from db_connection import get_connection

# Read customer dataset
df = pd.read_csv("data/raw/olist_customers_dataset.csv")

# Connect to SQL Server
connection = get_connection()
cursor = connection.cursor()

# Development only: clear existing records
cursor.execute("DELETE FROM Customers")
connection.commit()

# SQL Insert statement
sql = """
INSERT INTO Customers
(
    customer_id,
    customer_unique_id,
    customer_zip_code_prefix,
    customer_city,
    customer_state
)
VALUES (?, ?, ?, ?, ?)
"""

# Prepare data
rows = [
    (
        row.customer_id,
        row.customer_unique_id,
        int(row.customer_zip_code_prefix),
        row.customer_city,
        row.customer_state
    )
    for row in df.itertuples(index=False)
]

# Faster bulk insert
cursor.fast_executemany = True
cursor.executemany(sql, rows)

connection.commit()

print(f"{len(rows)} customers inserted successfully!")

cursor.close()
connection.close()