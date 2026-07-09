import pandas as pd
from db_connection import get_connection

# Read category translation dataset
df = pd.read_csv("data/raw/product_category_name_translation.csv")

# Connect to SQL Server
connection = get_connection()
cursor = connection.cursor()

# Development only: clear existing records
cursor.execute("DELETE FROM ProductCategoryTranslation")
connection.commit()

# SQL Insert statement
sql = """
INSERT INTO ProductCategoryTranslation
(
    product_category_name,
    product_category_name_english
)
VALUES (?, ?)
"""

# Prepare data
rows = [
    (
        row.product_category_name,
        row.product_category_name_english
    )
    for row in df.itertuples(index=False)
]

# Faster bulk insert
cursor.fast_executemany = True
cursor.executemany(sql, rows)

connection.commit()

print(f"{len(rows)} product category translations inserted successfully!")

cursor.close()
connection.close()