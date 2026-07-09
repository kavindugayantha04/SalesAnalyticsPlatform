import pandas as pd
from db_connection import get_connection

# Read sellers dataset
df = pd.read_csv("data/raw/olist_sellers_dataset.csv")

# Connect to SQL Server
connection = get_connection()
cursor = connection.cursor()

# Development only: clear existing records
cursor.execute("DELETE FROM Sellers")
connection.commit()

# SQL Insert statement
sql = """
INSERT INTO Sellers
(
    seller_id,
    seller_zip_code_prefix,
    seller_city,
    seller_state
)
VALUES (?, ?, ?, ?)
"""

# Prepare data
rows = [
    (
        row.seller_id,
        int(row.seller_zip_code_prefix),
        row.seller_city,
        row.seller_state
    )
    for row in df.itertuples(index=False)
]

# Faster bulk insert
cursor.fast_executemany = True
cursor.executemany(sql, rows)

connection.commit()

print(f"{len(rows)} sellers inserted successfully!")

cursor.close()
connection.close()