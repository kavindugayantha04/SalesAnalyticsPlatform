import pandas as pd
from db_connection import get_connection


# Helper function
def sql_value(value, data_type):

    if pd.isna(value):
        return None

    if data_type == "int":
        return int(value)

    if data_type == "decimal":
        return float(value)

    return value


# Read payments dataset
df = pd.read_csv("data/raw/olist_order_payments_dataset.csv")


# Connect to SQL Server
connection = get_connection()
cursor = connection.cursor()


# Development only
cursor.execute("DELETE FROM Payments")
connection.commit()


# SQL insert statement
sql = """
INSERT INTO Payments
(
    order_id,
    payment_sequential,
    payment_type,
    payment_installments,
    payment_value
)
VALUES (?, ?, ?, ?, ?)
"""


# Prepare rows
rows = [

    (
        sql_value(row.order_id, "str"),
        sql_value(row.payment_sequential, "int"),
        sql_value(row.payment_type, "str"),
        sql_value(row.payment_installments, "int"),
        sql_value(row.payment_value, "decimal")
    )

    for row in df.itertuples(index=False)

]


# Bulk insert
cursor.fast_executemany = True

cursor.executemany(sql, rows)

connection.commit()

print(f"{len(rows)} payments inserted successfully!")


# Close connection
cursor.close()
connection.close()