# Data Warehouse Design

## Project

**Sales Analytics Platform with AI-Powered Business Intelligence**

---

# Purpose

The operational database is designed for Online Transaction Processing (OLTP), where the primary objective is to efficiently store and manage transactional data.

To support Business Intelligence, reporting, machine learning, and AI-driven analytics, a dimensional Data Warehouse is introduced. The warehouse is optimized for analytical queries rather than transactional operations and follows the Kimball Star Schema methodology.

The Data Warehouse serves as the primary data source for:

- Power BI Dashboards
- Machine Learning Models
- AI Chatbot
- Streamlit Analytics Application

---

# Source System

The Data Warehouse is populated from the operational database (**SalesAnalytics_DB**) through an ETL process.

### Operational Tables

- Customers
- Orders
- OrderItems
- Products
- Sellers
- Payments
- Reviews
- ProductCategoryTranslation

The operational database remains the **single source of truth**.

---

# Data Warehouse Schema

Schema Name:

```text
dw
```

The Data Warehouse objects are stored separately from the operational tables using the `dw` schema.

---

# Business Process

The warehouse is designed to support the following business process:

## Sales Analysis

The primary objective is to analyze sales performance across different business dimensions.

Typical business questions include:

- What is the total revenue?
- Which products generate the highest revenue?
- Which customer locations contribute the most sales?
- Which sellers perform best?
- Which payment methods are most frequently used?
- How does sales performance change over time?

---

# Fact Table

The Data Warehouse contains a single central fact table.

## FactSales

### Grain

**One record represents one product sold within one customer order (one order item).**

### Measures

- Sales Amount
- Freight Amount
- Total Revenue
- Quantity Sold
- Review Score

---

# Dimension Tables

The warehouse contains the following dimension tables.

| Dimension | Description |
|-----------|-------------|
| DimDate | Date and time analysis |
| DimCustomer | Customer information |
| DimProduct | Product information |
| DimSeller | Seller information |
| DimPayment | Payment method information |

---

# Star Schema

```
                  DimDate
                     │
                     │
                     │
DimCustomer ─── FactSales ─── DimProduct
                     │
                     │
                DimPayment
                     │
                     │
                 DimSeller
```

---

# ETL Flow

```
CSV Files
      │
      ▼
Python ETL Pipeline
      │
      ▼
Operational Database (OLTP)
      │
      ▼
Data Warehouse (Star Schema)
      │
      ▼
Power BI
      │
      ▼
Machine Learning
      │
      ▼
AI Chatbot
      │
      ▼
Streamlit Application
```

---

# Design Principles

The Data Warehouse is designed according to the following principles:

- Kimball Dimensional Modeling
- Star Schema Architecture
- Single Fact Table
- Shared Dimension Tables
- Optimized for analytical workloads
- Separation of OLTP and OLAP systems
- Business-oriented data model
- Scalable design for future enhancements

---

# Future Enhancements

The warehouse can be extended by adding additional fact tables such as:

- FactInventory
- FactDelivery
- FactMarketing

without redesigning the existing dimensions.


