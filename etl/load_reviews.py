import pandas as pd
from db_connection import get_connection


# Helper function
def sql_value(value):

    if pd.isna(value):
        return None

    return value


# Read reviews dataset
df = pd.read_csv(
    "data/raw/olist_order_reviews_dataset.csv",
    parse_dates=[
        "review_creation_date",
        "review_answer_timestamp"
    ]
)


# Connect to SQL Server
connection = get_connection()
cursor = connection.cursor()


# Development only
cursor.execute("DELETE FROM Reviews")
connection.commit()


# SQL insert statement
sql = """
INSERT INTO Reviews
(
    review_id,
    order_id,
    review_score,
    review_comment_title,
    review_comment_message,
    review_creation_date,
    review_answer_timestamp
)
VALUES (?, ?, ?, ?, ?, ?, ?)
"""


# Prepare rows
rows = [

    (
        row.review_id,
        row.order_id,
        int(row.review_score),
        sql_value(row.review_comment_title),
        sql_value(row.review_comment_message),
        row.review_creation_date,
        row.review_answer_timestamp
    )

    for row in df.itertuples(index=False)

]


# Bulk insert
cursor.fast_executemany = True

cursor.executemany(sql, rows)

connection.commit()

print(f"{len(rows)} reviews inserted successfully!")

cursor.close()
connection.close()