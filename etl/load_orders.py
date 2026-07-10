import pandas as pd
from db_connection import get_connection



# Helper Function

def sql_value(value):
    """
    Converts Pandas NaN values into SQL NULL.
    """
    if pd.isna(value):
        return None
    return value


# Read Orders Dataset

df = pd.read_csv(
    "data/raw/olist_orders_dataset.csv",
    parse_dates=[
        "order_purchase_timestamp",
        "order_approved_at",
        "order_delivered_carrier_date",
        "order_delivered_customer_date",
        "order_estimated_delivery_date"
    ]
)


# Connect to SQL Server

connection = get_connection()
cursor = connection.cursor()



# Development Only

cursor.execute("DELETE FROM Orders")
connection.commit()



# SQL INSERT Statement

sql = """
INSERT INTO Orders
(
    order_id,
    customer_id,
    order_status,
    order_purchase_timestamp,
    order_approved_at,
    order_delivered_carrier_date,
    order_delivered_customer_date,
    order_estimated_delivery_date
)
VALUES (?, ?, ?, ?, ?, ?, ?, ?)
"""



# Prepare Data

rows = [

    (
        row.order_id,
        row.customer_id,
        row.order_status,
        sql_value(row.order_purchase_timestamp),
        sql_value(row.order_approved_at),
        sql_value(row.order_delivered_carrier_date),
        sql_value(row.order_delivered_customer_date),
        sql_value(row.order_estimated_delivery_date)
    )

    for row in df.itertuples(index=False)

]


# Bulk Insert

cursor.fast_executemany = True

cursor.executemany(sql, rows)

connection.commit()

print(f"{len(rows)} orders inserted successfully!")



# Close Connection

cursor.close()
connection.close()