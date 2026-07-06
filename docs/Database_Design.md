# Database Design

## Purpose

This document defines the logical database design for the Sales Analytics Platform.

It describes the relationships between tables, primary keys, foreign keys, SQL data types, and database constraints used to build the SQL Server database.

## Relationships

### 1. Customers → Orders

Relationship: One-to-Many

Primary Key:
Customers.customer_id

Foreign Key:
Orders.customer_id

---

### 2. Orders → Order Items

Relationship: One-to-Many

Primary Key:
Orders.order_id

Foreign Key:
OrderItems.order_id

---

### 3. Products → Order Items

Relationship: One-to-Many

Primary Key:
Products.product_id

Foreign Key:
OrderItems.product_id

---

### 4. Sellers → Order Items

Relationship: One-to-Many

Primary Key:
Sellers.seller_id

Foreign Key:
OrderItems.seller_id

---

### 5. Orders → Payments

Relationship: One-to-Many

Primary Key:
Orders.order_id

Foreign Key:
Payments.order_id

---

### 6. Orders → Reviews

Relationship: One-to-One (Business Rule)

Primary Key:
Orders.order_id

Foreign Key:
Reviews.order_id

---

### 7. Category Translation → Products

Relationship: One-to-Many

Primary Key:
CategoryTranslation.product_category_name

Foreign Key:
Products.product_category_name