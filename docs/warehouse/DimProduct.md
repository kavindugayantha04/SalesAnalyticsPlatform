# Dimension: DimProduct

## Purpose

The `DimProduct` table stores descriptive product information for sales analysis.

It combines product attributes with translated product category names to provide business-friendly reporting.

---

## Source

- dbo.Products
- dbo.ProductCategoryTranslation

---

## Grain

One record represents one product.

---

## Primary Key

- ProductKey (Surrogate Key)

---

## Business Key

- ProductID

---

## ETL

The ETL process joins the `Products` table with the `ProductCategoryTranslation` table to enrich product records with English category names.

---

## Business Usage

Supports reporting such as:

- Sales by Product
- Sales by Category
- Revenue by Product Category
- Product Weight Analysis
- Product Size Analysis

---

## Status

Completed