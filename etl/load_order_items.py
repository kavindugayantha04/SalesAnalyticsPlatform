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


# Read Order Items Dataset

df = pd.read_csv(
    "data/raw/olist_order_items_dataset.csv",
    parse_dates=["shipping_limit_date"]
)


# Connect to SQL Server

connection = get_connection()
cursor = connection.cursor()


# Development Only

cursor.execute("DELETE FROM OrderItems")
connection.commit()


# SQL INSERT Statement

sql = """
INSERT INTO OrderItems
(
    order_id,
    order_item_id,
    product_id,
    seller_id,
    shipping_limit_date,
    price,
    freight_value
)
VALUES (?, ?, ?, ?, ?, ?, ?)
"""



# Prepare Data

rows = [

    (
        sql_value(row.order_id, "str"),
        sql_value(row.order_item_id, "int"),
        sql_value(row.product_id, "str"),
        sql_value(row.seller_id, "str"),
        sql_value(row.shipping_limit_date, "datetime"),
        sql_value(row.price, "decimal"),
        sql_value(row.freight_value, "decimal")
    )

    for row in df.itertuples(index=False)

]


# Bulk Insert

cursor.fast_executemany = True

cursor.executemany(sql, rows)

connection.commit()

print(f"{len(rows)} order items inserted successfully!")



# Close Connection

cursor.close()
connection.close()

