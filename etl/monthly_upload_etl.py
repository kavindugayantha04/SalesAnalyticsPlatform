import os
import zipfile
import shutil
import pandas as pd


# ============================================================
# CONFIGURATION
# ============================================================

UPLOAD_FILE = "data/uploads/2018-09.zip"

EXTRACT_FOLDER = "data/uploads/extracted"


REQUIRED_FILES = [
    "customers.csv",
    "orders.csv",
    "order_items.csv",
    "products.csv",
    "sellers.csv",
    "payments.csv",
    "reviews.csv"
]


# ============================================================
# HELPER FUNCTION
# ============================================================

def sql_value(value):
    """
    Convert Pandas missing values into Python None.

    Python None will become SQL NULL when inserted
    into SQL Server.
    """

    if pd.isna(value):
        return None

    return value


# ============================================================
# STEP 1 — CHECK UPLOAD
# ============================================================

if not os.path.exists(UPLOAD_FILE):

    raise FileNotFoundError(
        f"Upload file not found: {UPLOAD_FILE}"
    )

print("Upload file found successfully.")
print(f"Upload : {UPLOAD_FILE}")


# ============================================================
# STEP 2 — PREPARE EXTRACTION FOLDER
# ============================================================

if os.path.exists(EXTRACT_FOLDER):

    shutil.rmtree(EXTRACT_FOLDER)


os.makedirs(
    EXTRACT_FOLDER,
    exist_ok=True
)


# ============================================================
# STEP 3 — EXTRACT ZIP
# ============================================================

print("\nExtracting upload...")

with zipfile.ZipFile(
    UPLOAD_FILE,
    "r"
) as zip_ref:

    zip_ref.extractall(
        EXTRACT_FOLDER
    )


print("ZIP extracted successfully.")


# ============================================================
# STEP 4 — FIND CSV FILES
# ============================================================

csv_files = {}


for root, directories, files in os.walk(
    EXTRACT_FOLDER
):

    for file in files:

        if file.lower().endswith(".csv"):

            csv_files[
                file.lower()
            ] = os.path.join(
                root,
                file
            )


print("\nCSV files found:")

for file in csv_files:

    print(
        f" - {file}"
    )


# ============================================================
# STEP 5 — CHECK REQUIRED FILES
# ============================================================

print("\nChecking required files...")


missing_files = []


for required_file in REQUIRED_FILES:

    if required_file not in csv_files:

        missing_files.append(
            required_file
        )


if missing_files:

    print("\nERROR: Missing files:")

    for file in missing_files:

        print(
            f" - {file}"
        )

    raise Exception(
        "Upload validation failed."
    )


print(
    "All required CSV files are present."
)


# ============================================================
# STEP 6 — LOAD CSV FILES
# ============================================================

dataframes = {}


for file in REQUIRED_FILES:

    path = csv_files[file]

    print(
        f"\nLoading {file}..."
    )

    df = pd.read_csv(path)

    dataframes[file] = df

    print(
        f"Rows : {len(df)}"
    )


# ============================================================
# STEP 7 — PREPARE DATA TYPES
# ============================================================

print("\nPreparing data types...")


# -------------------------
# Customers
# -------------------------

customers = dataframes[
    "customers.csv"
].copy()


customers[
    "customer_zip_code_prefix"
] = pd.to_numeric(
    customers[
        "customer_zip_code_prefix"
    ],
    errors="coerce"
)


# -------------------------
# Orders
# -------------------------

orders = dataframes[
    "orders.csv"
].copy()


order_date_columns = [
    "order_purchase_timestamp",
    "order_approved_at",
    "order_delivered_carrier_date",
    "order_delivered_customer_date",
    "order_estimated_delivery_date"
]


for column in order_date_columns:

    orders[column] = pd.to_datetime(
        orders[column],
        errors="coerce"
    )


# -------------------------
# Order Items
# -------------------------

order_items = dataframes[
    "order_items.csv"
].copy()


order_items[
    "order_item_id"
] = pd.to_numeric(
    order_items[
        "order_item_id"
    ],
    errors="coerce"
)


order_items[
    "shipping_limit_date"
] = pd.to_datetime(
    order_items[
        "shipping_limit_date"
    ],
    errors="coerce"
)


order_items[
    "price"
] = pd.to_numeric(
    order_items[
        "price"
    ],
    errors="coerce"
)


order_items[
    "freight_value"
] = pd.to_numeric(
    order_items[
        "freight_value"
    ],
    errors="coerce"
)


# -------------------------
# Products
# -------------------------

products = dataframes[
    "products.csv"
].copy()


# Normalize original Olist column names
# Olist uses "lenght" in the source dataset.

products = products.rename(
    columns={
        "product_name_lenght": "product_name_length",
        "product_description_lenght": "product_description_length"
    }
)

print(
    "Product column names normalized."
)

# Update the main dataframe collection
dataframes["products.csv"] = products


product_numeric_columns = [
    "product_name_length",
    "product_description_length",
    "product_photos_qty",
    "product_weight_g",
    "product_length_cm",
    "product_height_cm",
    "product_width_cm"
]


for column in product_numeric_columns:

    products[column] = pd.to_numeric(
        products[column],
        errors="coerce"
    )


# -------------------------
# Sellers
# -------------------------

sellers = dataframes[
    "sellers.csv"
].copy()


sellers[
    "seller_zip_code_prefix"
] = pd.to_numeric(
    sellers[
        "seller_zip_code_prefix"
    ],
    errors="coerce"
)


# -------------------------
# Payments
# -------------------------

payments = dataframes[
    "payments.csv"
].copy()


payments[
    "payment_sequential"
] = pd.to_numeric(
    payments[
        "payment_sequential"
    ],
    errors="coerce"
)


payments[
    "payment_installments"
] = pd.to_numeric(
    payments[
        "payment_installments"
    ],
    errors="coerce"
)


payments[
    "payment_value"
] = pd.to_numeric(
    payments[
        "payment_value"
    ],
    errors="coerce"
)


# -------------------------
# Reviews
# -------------------------

reviews = dataframes[
    "reviews.csv"
].copy()


reviews[
    "review_score"
] = pd.to_numeric(
    reviews[
        "review_score"
    ],
    errors="coerce"
)


reviews[
    "review_creation_date"
] = pd.to_datetime(
    reviews[
        "review_creation_date"
    ],
    errors="coerce"
)


reviews[
    "review_answer_timestamp"
] = pd.to_datetime(
    reviews[
        "review_answer_timestamp"
    ],
    errors="coerce"
)


print(
    "Data type preparation completed."
)


# ============================================================
# STEP 8 — CHECK REQUIRED COLUMNS
# ============================================================

print("\nChecking required columns...")


REQUIRED_COLUMNS = {

    "customers.csv": [
        "customer_id",
        "customer_unique_id",
        "customer_zip_code_prefix",
        "customer_city",
        "customer_state"
    ],

    "orders.csv": [
        "order_id",
        "customer_id",
        "order_status",
        "order_purchase_timestamp",
        "order_approved_at",
        "order_delivered_carrier_date",
        "order_delivered_customer_date",
        "order_estimated_delivery_date"
    ],

    "order_items.csv": [
        "order_id",
        "order_item_id",
        "product_id",
        "seller_id",
        "shipping_limit_date",
        "price",
        "freight_value"
    ],

    "products.csv": [
        "product_id",
        "product_category_name",
        "product_name_length",
        "product_description_length",
        "product_photos_qty",
        "product_weight_g",
        "product_length_cm",
        "product_height_cm",
        "product_width_cm"
    ],

    "sellers.csv": [
        "seller_id",
        "seller_zip_code_prefix",
        "seller_city",
        "seller_state"
    ],

    "payments.csv": [
        "order_id",
        "payment_sequential",
        "payment_type",
        "payment_installments",
        "payment_value"
    ],

    "reviews.csv": [
        "review_id",
        "order_id",
        "review_score",
        "review_comment_title",
        "review_comment_message",
        "review_creation_date",
        "review_answer_timestamp"
    ]
}


for file in REQUIRED_FILES:

    df = dataframes[file]

    missing_columns = [
        column
        for column in REQUIRED_COLUMNS[file]
        if column not in df.columns
    ]

    if missing_columns:

        print(
            f"\nERROR in {file}"
        )

        print(
            "Missing columns:"
        )

        for column in missing_columns:

            print(
                f" - {column}"
            )

        raise Exception(
            f"Column validation failed for {file}."
        )

    print(
        f"{file} : OK"
    )


# ============================================================
# STEP 9 — CHECK REQUIRED VALUES
# ============================================================

print("\nChecking required values...")


def check_required_values(
    df,
    columns,
    file
):

    for column in columns:

        if df[column].isna().any():

            missing_count = (
                df[column].isna().sum()
            )

            raise Exception(
                f"{file}: "
                f"{column} contains "
                f"{missing_count} missing values."
            )


# Customers

check_required_values(
    customers,
    [
        "customer_id",
        "customer_unique_id",
        "customer_zip_code_prefix",
        "customer_city",
        "customer_state"
    ],
    "customers.csv"
)


# Orders

check_required_values(
    orders,
    [
        "order_id",
        "customer_id",
        "order_status",
        "order_purchase_timestamp",
        "order_estimated_delivery_date"
    ],
    "orders.csv"
)


# Order Items

check_required_values(
    order_items,
    [
        "order_id",
        "order_item_id",
        "product_id",
        "seller_id",
        "shipping_limit_date",
        "price",
        "freight_value"
    ],
    "order_items.csv"
)


# Products

check_required_values(
    products,
    [
        "product_id"
    ],
    "products.csv"
)


# Sellers

check_required_values(
    sellers,
    [
        "seller_id",
        "seller_zip_code_prefix",
        "seller_city",
        "seller_state"
    ],
    "sellers.csv"
)


# Payments

check_required_values(
    payments,
    [
        "order_id",
        "payment_sequential",
        "payment_type",
        "payment_installments",
        "payment_value"
    ],
    "payments.csv"
)


# Reviews

check_required_values(
    reviews,
    [
        "review_id",
        "order_id",
        "review_score",
        "review_creation_date",
        "review_answer_timestamp"
    ],
    "reviews.csv"
)


print(
    "Required-value validation passed."
)


# ============================================================
# STEP 10 — CHECK DUPLICATE KEYS
# ============================================================

print("\nChecking duplicate keys...")


if customers[
    "customer_id"
].duplicated().any():

    raise Exception(
        "Duplicate customer_id found."
    )


if orders[
    "order_id"
].duplicated().any():

    raise Exception(
        "Duplicate order_id found."
    )


if order_items.duplicated(
    subset=[
        "order_id",
        "order_item_id"
    ]
).any():

    raise Exception(
        "Duplicate OrderItems key found."
    )


if products[
    "product_id"
].duplicated().any():

    raise Exception(
        "Duplicate product_id found."
    )


if sellers[
    "seller_id"
].duplicated().any():

    raise Exception(
        "Duplicate seller_id found."
    )


if payments.duplicated(
    subset=[
        "order_id",
        "payment_sequential"
    ]
).any():

    raise Exception(
        "Duplicate payment key found."
    )


print(
    "Duplicate-key validation passed."
)


# ============================================================
# STEP 11 — DETECT UPLOAD MONTH
# ============================================================

orders["YearMonth"] = (
    orders[
        "order_purchase_timestamp"
    ]
    .dt
    .to_period("M")
    .astype(str)
)


unique_months = (
    orders["YearMonth"]
    .dropna()
    .unique()
)


print("\nDetected Months")

for month in unique_months:

    print(
        f" - {month}"
    )


if len(unique_months) != 1:

    raise Exception(
        "Upload must contain exactly one month."
    )


upload_month = unique_months[0]


print("\nUpload Month")
print(
    f"Month : {upload_month}"
)


# ============================================================
# STEP 12 — FINAL SUMMARY
# ============================================================

print("\n======================================")
print("UPLOAD VALIDATION SUCCESSFUL")
print("======================================")


print(
    f"Upload Month : {upload_month}"
)


print("\nRecords:")


for file, df in dataframes.items():

    print(
        f"{file:<25} {len(df):>8} rows"
    )


# ============================================================
# STEP 13 — LOAD DATA INTO SQL SERVER
# ============================================================

from etl.db_connection import get_connection


print("\n======================================")
print("STARTING DATABASE LOAD")
print("======================================")


connection = get_connection()

if connection is None:
    raise Exception(
        "Failed to connect to SQL Server."
    )


cursor = connection.cursor()

print("Connected to SQL Server successfully.")


try:

    # ========================================================
    # BEGIN TRANSACTION
    # ========================================================

    print("\nStarting database transaction...")

    # ========================================================
    # 1. CUSTOMERS
    # ========================================================

    print("\nLoading Customers...")


    customer_sql = """
    INSERT INTO dbo.Customers
    (
        customer_id,
        customer_unique_id,
        customer_zip_code_prefix,
        customer_city,
        customer_state
    )
    SELECT ?, ?, ?, ?, ?
    WHERE NOT EXISTS
    (
        SELECT 1
        FROM dbo.Customers
        WHERE customer_id = ?
    );
    """


    customer_rows = [

        (
            row.customer_id,
            row.customer_unique_id,
            int(row.customer_zip_code_prefix),
            row.customer_city,
            row.customer_state,
            row.customer_id
        )

        for row in customers.itertuples(
            index=False
        )
    ]


    cursor.fast_executemany = True

    cursor.executemany(
        customer_sql,
        customer_rows
    )


    print(
        f"Customers processed : {len(customer_rows)}"
    )


    # ========================================================
    # 2. PRODUCTS
    # ========================================================

    print("\nLoading Products...")


    product_sql = """
    INSERT INTO dbo.Products
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
    SELECT ?, ?, ?, ?, ?, ?, ?, ?, ?
    WHERE NOT EXISTS
    (
        SELECT 1
        FROM dbo.Products
        WHERE product_id = ?
    );
    """


    product_rows = [

        (
            sql_value(row.product_id),
            sql_value(row.product_category_name),
            sql_value(row.product_name_length),
            sql_value(row.product_description_length),
            sql_value(row.product_photos_qty),
            sql_value(row.product_weight_g),
            sql_value(row.product_length_cm),
            sql_value(row.product_height_cm),
            sql_value(row.product_width_cm),
            row.product_id
        )

        for row in products.itertuples(
            index=False
        )
    ]


    cursor.fast_executemany = True

    cursor.executemany(
        product_sql,
        product_rows
    )


    print(
        f"Products processed : {len(product_rows)}"
    )


    # ========================================================
    # 3. SELLERS
    # ========================================================

    print("\nLoading Sellers...")


    seller_sql = """
    INSERT INTO dbo.Sellers
    (
        seller_id,
        seller_zip_code_prefix,
        seller_city,
        seller_state
    )
    SELECT ?, ?, ?, ?
    WHERE NOT EXISTS
    (
        SELECT 1
        FROM dbo.Sellers
        WHERE seller_id = ?
    );
    """


    seller_rows = [

        (
            row.seller_id,
            int(row.seller_zip_code_prefix),
            row.seller_city,
            row.seller_state,
            row.seller_id
        )

        for row in sellers.itertuples(
            index=False
        )
    ]


    cursor.fast_executemany = True

    cursor.executemany(
        seller_sql,
        seller_rows
    )


    print(
        f"Sellers processed : {len(seller_rows)}"
    )


    # ========================================================
    # 4. ORDERS
    # ========================================================

    print("\nLoading Orders...")


    order_sql = """
    INSERT INTO dbo.Orders
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
    SELECT ?, ?, ?, ?, ?, ?, ?, ?
    WHERE NOT EXISTS
    (
        SELECT 1
        FROM dbo.Orders
        WHERE order_id = ?
    );
    """


    order_rows = [

        (
            row.order_id,
            row.customer_id,
            row.order_status,
            sql_value(
                row.order_purchase_timestamp
            ),
            sql_value(
                row.order_approved_at
            ),
            sql_value(
                row.order_delivered_carrier_date
            ),
            sql_value(
                row.order_delivered_customer_date
            ),
            sql_value(
                row.order_estimated_delivery_date
            ),
            row.order_id
        )

        for row in orders.itertuples(
            index=False
        )
    ]


    cursor.fast_executemany = True

    cursor.executemany(
        order_sql,
        order_rows
    )


    print(
        f"Orders processed : {len(order_rows)}"
    )


    # ========================================================
    # 5. ORDER ITEMS
    # ========================================================

    print("\nLoading OrderItems...")


    order_item_sql = """
    INSERT INTO dbo.OrderItems
    (
        order_id,
        order_item_id,
        product_id,
        seller_id,
        shipping_limit_date,
        price,
        freight_value
    )
    SELECT ?, ?, ?, ?, ?, ?, ?
    WHERE NOT EXISTS
    (
        SELECT 1
        FROM dbo.OrderItems
        WHERE order_id = ?
          AND order_item_id = ?
    );
    """


    order_item_rows = [

        (
            row.order_id,
            int(row.order_item_id),
            row.product_id,
            row.seller_id,
            row.shipping_limit_date,
            float(row.price),
            float(row.freight_value),
            row.order_id,
            int(row.order_item_id)
        )

        for row in order_items.itertuples(
            index=False
        )
    ]


    cursor.fast_executemany = True

    cursor.executemany(
        order_item_sql,
        order_item_rows
    )


    print(
        f"OrderItems processed : "
        f"{len(order_item_rows)}"
    )


    # ========================================================
    # 6. PAYMENTS
    # ========================================================

    print("\nLoading Payments...")


    payment_sql = """
    INSERT INTO dbo.Payments
    (
        order_id,
        payment_sequential,
        payment_type,
        payment_installments,
        payment_value
    )
    SELECT ?, ?, ?, ?, ?
    WHERE NOT EXISTS
    (
        SELECT 1
        FROM dbo.Payments
        WHERE order_id = ?
          AND payment_sequential = ?
    );
    """


    payment_rows = [

        (
            row.order_id,
            int(row.payment_sequential),
            row.payment_type,
            int(row.payment_installments),
            float(row.payment_value),
            row.order_id,
            int(row.payment_sequential)
        )

        for row in payments.itertuples(
            index=False
        )
    ]


    cursor.fast_executemany = True

    cursor.executemany(
        payment_sql,
        payment_rows
    )


    print(
        f"Payments processed : "
        f"{len(payment_rows)}"
    )


    # ========================================================
    # 7. REVIEWS
    # ========================================================

    print("\nLoading Reviews...")


    review_sql = """
    INSERT INTO dbo.Reviews
    (
        review_id,
        order_id,
        review_score,
        review_comment_title,
        review_comment_message,
        review_creation_date,
        review_answer_timestamp
    )
    SELECT ?, ?, ?, ?, ?, ?, ?
    WHERE NOT EXISTS
    (
        SELECT 1
        FROM dbo.Reviews
        WHERE review_id = ?
          AND order_id = ?
    );
    """


    review_rows = [

        (
            row.review_id,
            row.order_id,
            int(row.review_score),
            sql_value(
                row.review_comment_title
            ),
            sql_value(
                row.review_comment_message
            ),
            row.review_creation_date,
            row.review_answer_timestamp,
            row.review_id,
            row.order_id
        )

        for row in reviews.itertuples(
            index=False
        )
    ]


    cursor.fast_executemany = True

    cursor.executemany(
        review_sql,
        review_rows
    )


    print(
        f"Reviews processed : "
        f"{len(review_rows)}"
    )


    # ========================================================
    # COMMIT
    # ========================================================

    connection.commit()

    print("\n======================================")
    print("DATABASE LOAD SUCCESSFUL")
    print("======================================")

    print(
        f"Uploaded Month : {upload_month}"
    )

    print(
        "Transaction committed successfully."
    )


except Exception as error:

    # ========================================================
    # ROLLBACK
    # ========================================================

    connection.rollback()

    print("\n======================================")
    print("DATABASE LOAD FAILED")
    print("======================================")

    print(
        f"Error : {error}"
    )

    print(
        "\nTransaction rolled back."
    )

    print(
        "No partial database changes were committed."
    )

    raise


finally:

    cursor.close()

    connection.close()

    print(
        "\nSQL Server connection closed."
    )