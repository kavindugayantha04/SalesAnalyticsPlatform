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
| product_category_name | 610 | Missing product classification | Keep NULL|
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
| product_weight_g | Float | DECIMAL(10,2) |
| product_length_cm | Float | DECIMAL(10,2) |
| product_height_cm | Float | DECIMAL(10,2) |
| product_width_cm | Float | DECIMAL(10,2) |

---

## ETL Rules

- Preserve all product records.
- Preserve missing product categories as NULL to maintain data integrity.
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

---

# Dataset: olist_order_reviews_dataset.csv

## Business Purpose

Stores customer ratings and written reviews for completed orders.

---

## Primary Key

No reliable single primary key was identified during assessment.

`review_id` should uniquely identify reviews, but duplicate values exist and require investigation during ETL.

---

## Foreign Key

- order_id → Orders

---

## Data Quality Summary

| Metric | Value |
|--------|------:|
| Rows | 99,224 |
| Columns | 7 |
| Duplicate Rows | 0 |

---

## Missing Values Assessment

| Column | Missing | Business Reason | ETL Action |
|--------|---------:|----------------|------------|
| review_comment_title | 87,656 | Customer did not provide a title | Keep NULL |
| review_comment_message | 58,247 | Customer provided only a rating | Keep NULL |

---

## Data Type Conversion

| Column | Current Type | Target SQL Type |
|--------|--------------|-----------------|
| review_id | String | VARCHAR(50) |
| order_id | String | VARCHAR(50) |
| review_score | Integer | TINYINT |
| review_comment_title | String | NVARCHAR(255) |
| review_comment_message | String | NVARCHAR(MAX) |
| review_creation_date | String | DATETIME2 |
| review_answer_timestamp | String | DATETIME2 |

---

## ETL Rules

- Preserve all review records.
- Keep NULL values in review text fields.
- Convert review dates to DATETIME2.
- Investigate duplicate review_id values before loading into SQL Server.

---

# Dataset: olist_sellers_dataset.csv

## Business Purpose

Stores seller master data, including seller location information such as ZIP code, city, and state.

---

## Primary Key

- seller_id

---

## Data Quality Summary

| Metric | Value |
|--------|------:|
| Rows | 3,095 |
| Columns | 4 |
| Duplicate Rows | 0 |

---

## Missing Values Assessment

No missing values were found.

---

## Data Type Conversion

| Column | Current Type | Target SQL Type |
|--------|--------------|-----------------|
| seller_id | String | VARCHAR(50) |
| seller_zip_code_prefix | Integer | INT |
| seller_city | String | VARCHAR(100) |
| seller_state | String | CHAR(2) |

---

## ETL Rules

- Preserve all seller records.
- No missing values require cleaning.
- No duplicate rows require removal.
- Preserve seller_id as the primary key.

---

# Dataset: olist_geolocation_dataset.csv

## Business Purpose

Stores geographic information for Brazilian ZIP code prefixes, including latitude, longitude, city, and state.

---

## Primary Key

No reliable primary key exists.

The ZIP code prefix is not unique because multiple geographic coordinates can belong to the same postal area.

---

## Data Quality Summary

| Metric | Value |
|--------|------:|
| Rows | 1,000,163 |
| Columns | 5 |
| Duplicate Rows | 261,831 |

---

## Missing Values Assessment

No missing values were found.

---

## Duplicate Assessment

A large number of duplicate rows were identified.

Further investigation is required to determine whether these are:

- Exact duplicate records
- Multiple valid geographic coordinates within the same ZIP code prefix

Only exact duplicate rows should be removed during ETL.

---

## Data Type Conversion

| Column | Current Type | Target SQL Type |
|--------|--------------|-----------------|
| geolocation_zip_code_prefix | Integer | INT |
| geolocation_lat | Float | FLOAT |
| geolocation_lng | Float | FLOAT |
| geolocation_city | String | VARCHAR(100) |
| geolocation_state | String | CHAR(2) |

---

## ETL Rules

- Preserve all geographic information until duplicate analysis is completed.
- Remove only confirmed exact duplicate rows.
- Preserve multiple coordinates belonging to the same ZIP code prefix.

---

# Dataset: product_category_name_translation.csv

## Business Purpose

Stores the English translation for Portuguese product category names.

This lookup table is used to improve reporting and dashboard readability.

---

## Primary Key

- product_category_name

---

## Foreign Key Relationship

Referenced by:

- Products → product_category_name

---

## Data Quality Summary

| Metric | Value |
|--------|------:|
| Rows | 71 |
| Columns | 2 |
| Duplicate Rows | 0 |

---

## Missing Values Assessment

No missing values were found.

---

## Data Type Conversion

| Column | Current Type | Target SQL Type |
|--------|--------------|-----------------|
| product_category_name | String | VARCHAR(100) |
| product_category_name_english | String | VARCHAR(100) |

---

## ETL Rules

- Preserve all translation records.
- No missing values require cleaning.
- No duplicate rows require removal.
- Use English category names for reporting and Power BI dashboards.


## Data Quality Issue Identified During ETL

During ETL validation, two product categories found in the
`olist_products_dataset.csv` were missing from the original
`product_category_name_translation.csv` lookup table.

Missing categories:

- pc_gamer
- portateis_cozinha_e_preparadores_de_alimentos

Since the Products table enforces a foreign key relationship with
ProductCategoryTranslation, these missing lookup values would prevent
successful data loading.

To preserve referential integrity and avoid data loss, the missing
categories were added to the ProductCategoryTranslation table before
loading the Products dataset.

Original lookup records: **71**

Final lookup records: **73**