# Data Quality Assessment

---

# Dataset: olist_orders_dataset.csv

## Business Purpose

Stores the complete lifecycle of customer orders from purchase to delivery.

---

## Primary Key

- order_id

---

## Foreign Key

- customer_id

---

## Data Quality Summary

| Metric | Value |
|--------|------:|
| Rows | 99,441 |
| Columns | 8 |
| Duplicate Rows | 0 |

---

## Missing Values Assessment

| Column | Missing | Business Reason | ETL Action |
|--------|---------:|----------------|------------|
| order_approved_at | 160 | Mostly cancelled orders | Keep NULL |
| order_delivered_carrier_date | 1,783 | Orders not shipped | Keep NULL |
| order_delivered_customer_date | 2,965 | Orders not delivered or cancelled | Keep NULL |

---

## Data Type Conversion

| Column | Current Type | Target SQL Type |
|--------|--------------|-----------------|
| order_purchase_timestamp | String | DATETIME2 |
| order_approved_at | String | DATETIME2 |
| order_delivered_carrier_date | String | DATETIME2 |
| order_delivered_customer_date | String | DATETIME2 |
| order_estimated_delivery_date | String | DATETIME2 |

---

## ETL Rules

- Convert all timestamp columns to DATETIME2.
- Preserve NULL values for cancelled and undelivered orders.
- Do not remove rows with missing delivery dates.
- Validate delivery dates against the order status.

---

# Dataset: olist_customers_dataset.csv

## Business Purpose

Stores customer information and customer location details.

---

## Primary Key

- customer_id

---

## Business Key

- customer_unique_id

> A single customer may place multiple orders. Therefore, customer_unique_id can appear multiple times.

---

## Data Quality Summary

| Metric | Value |
|--------|------:|
| Rows | 99,441 |
| Columns | 5 |
| Duplicate Rows | 0 |

---

## Missing Values Assessment

No missing values were found.

---

## Data Type Conversion

| Column | Current Type | Target SQL Type |
|--------|--------------|-----------------|
| customer_id | String | VARCHAR(50) |
| customer_unique_id | String | VARCHAR(50) |
| customer_zip_code_prefix | Integer | INT |
| customer_city | String | VARCHAR(100) |
| customer_state | String | CHAR(2) |

---

## ETL Rules

- No missing values require cleaning.
- No duplicate rows require removal.
- Preserve customer_id as the primary key.
- Preserve customer_unique_id for customer-level analysis.


---

# Dataset: olist_order_items_dataset.csv

## Business Purpose

Stores the individual products included in each customer order.

Each row represents one product within an order.

---

## Primary Key

Composite Primary Key

- order_id
- order_item_id

---

## Foreign Keys

- order_id → Orders
- product_id → Products
- seller_id → Sellers

---

## Data Quality Summary

| Metric | Value |
|--------|------:|
| Rows | 112,650 |
| Columns | 7 |
| Duplicate Rows | 0 |

---

## Missing Values Assessment

No missing values were found.

---

## Data Type Conversion

| Column | Current Type | Target SQL Type |
|--------|--------------|-----------------|
| order_id | String | VARCHAR(50) |
| order_item_id | Integer | INT |
| product_id | String | VARCHAR(50) |
| seller_id | String | VARCHAR(50) |
| shipping_limit_date | String | DATETIME2 |
| price | Float | DECIMAL(10,2) |
| freight_value | Float | DECIMAL(10,2) |

---

## ETL Rules

- Convert shipping_limit_date to DATETIME2.
- Preserve the composite primary key.
- No duplicate rows require removal.
- No missing values require cleaning.
- Preserve price and freight values without modification.

---

# Dataset: olist_products_dataset.csv

## Business Purpose

Stores product master data including category, dimensions, weight, and descriptive attributes.

---

## Primary Key

- product_id

---

## Data Quality Summary

| Metric | Value |
|--------|------:|
| Rows | 32,951 |
| Columns | 9 |
| Duplicate Rows | 0 |

---

## Missing Values Assessment

| Column | Missing | Business Reason | ETL Action |
|--------|---------:|----------------|------------|
| product_category_name | 610 | Missing product classification | Fill with "Unknown Category" |
| product_name_lenght | 610 | Missing metadata | Keep NULL |
| product_description_lenght | 610 | Missing metadata | Keep NULL |
| product_photos_qty | 610 | Missing metadata | Keep NULL |
| product_weight_g | 2 | Missing physical measurement | Investigate during ETL |
| product_length_cm | 2 | Missing physical measurement | Investigate during ETL |
| product_height_cm | 2 | Missing physical measurement | Investigate during ETL |
| product_width_cm | 2 | Missing physical measurement | Investigate during ETL |

---

## Data Type Conversion

| Column | Current Type | Target SQL Type |
|--------|--------------|-----------------|
| product_id | String | VARCHAR(50) |
| product_category_name | String | VARCHAR(100) |
| product_name_lenght | Float | INT |
| product_description_lenght | Float | INT |
| product_photos_qty | Float | INT |
| product_weight_g | Float | FLOAT |
| product_length_cm | Float | FLOAT |
| product_height_cm | Float | FLOAT |
| product_width_cm | Float | FLOAT |

---

## ETL Rules

- Preserve all product records.
- Replace missing product categories with **"Unknown Category"**.
- Convert numeric metadata columns to INTEGER where appropriate.
- Investigate products missing physical dimensions before applying imputation.

---

# Dataset: olist_order_payments_dataset.csv

## Business Purpose

Stores payment information for customer orders, including payment method, number of installments, and payment amount.

---

## Primary Key

Composite Primary Key

- order_id
- payment_sequential

---

## Foreign Key

- order_id → Orders

---

## Data Quality Summary

| Metric | Value |
|--------|------:|
| Rows | 103,886 |
| Columns | 5 |
| Duplicate Rows | 0 |

---

## Missing Values Assessment

No missing values were found.

---

## Data Type Conversion

| Column | Current Type | Target SQL Type |
|--------|--------------|-----------------|
| order_id | String | VARCHAR(50) |
| payment_sequential | Integer | INT |
| payment_type | String | VARCHAR(30) |
| payment_installments | Integer | INT |
| payment_value | Float | DECIMAL(10,2) |

---

## ETL Rules

- Preserve all payment records.
- Preserve composite primary key.
- Do not remove multiple payment records for a single order.
- Convert payment_value to DECIMAL(10,2).
- Retain "not_defined" payment types for further analysis.