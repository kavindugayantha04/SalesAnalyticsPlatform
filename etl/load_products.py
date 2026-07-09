import pandas as pd
from db_connection import get_connection



# Helper Function

def sql_value(value, data_type):
    """
    Converts Pandas values into SQL-friendly values.
    NaN -> None (SQL NULL)
    """

    if pd.isna(value):
        return None

    if data_type == "int":
        return int(value)

    if data_type == "decimal":
        return float(value)

    return value



# Read Products Dataset

df = pd.read_csv("data/raw/olist_products_dataset.csv")



# Connect to SQL Server

connection = get_connection()
cursor = connection.cursor()



# Development Only

cursor.execute("DELETE FROM Products")
connection.commit()



# SQL Insert Statement

sql = """
INSERT INTO Products
(
    product_id,
    product_category_name,
    product_name_length,
    product_description_length,
    product_photos_qty,
    product_weight_g,
    product_length_cm,
    product_height_cm,
    product_width_cm
)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
"""



# Prepare Data

rows = [

    (
        sql_value(row.product_id, "str"),
        sql_value(row.product_category_name, "str"),
        sql_value(row.product_name_lenght, "int"),
        sql_value(row.product_description_lenght, "int"),
        sql_value(row.product_photos_qty, "int"),
        sql_value(row.product_weight_g, "decimal"),
        sql_value(row.product_length_cm, "decimal"),
        sql_value(row.product_height_cm, "decimal"),
        sql_value(row.product_width_cm, "decimal")
    )

    for row in df.itertuples(index=False)

]



# Bulk Insert

cursor.fast_executemany = True

cursor.executemany(sql, rows)

connection.commit()

print(f"{len(rows)} products inserted successfully!")



# Close Connection

cursor.close()
connection.close()