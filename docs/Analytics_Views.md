# Analytics Views

## vw_SalesSummary

### Purpose

Provides one record per order with customer information, total product value, freight value, total order value, and total number of purchased items.

### Source Tables

- Customers
- Orders
- OrderItems

### Primary Use

- Power BI KPIs
- Executive dashboard
- Revenue reporting
- Machine learning features
 
-----

## vw_MonthlySales

### Purpose

Provides monthly sales performance, including total revenue, total orders, and average order value.

### Source View

- vw_SalesSummary

### Primary Use

- Power BI monthly sales dashboard
- Sales forecasting (Machine Learning)
- Chatbot monthly sales queries

------

## vw_CategorySales

### Purpose

Provides sales performance by product category, including revenue, sales volume, freight cost, and average product price for each category.

### Source Tables

- OrderItems
- Products
- ProductCategoryTranslation

### Primary Use

- Power BI Category Sales Dashboard
- Category performance analysis
- Product demand analysis
- AI chatbot category-related queries

### Key Metrics

- Total Orders
- Total Product Sales
- Total Freight
- Total Revenue
- Total Items Sold
- Average Product Price


---

## 4. vw_ProductPerformance

### Purpose

Provides sales performance for individual products, including revenue, sales volume, freight cost, and average selling price.

### Source Tables

- Products
- OrderItems
- ProductCategoryTranslation

### Primary Use

- Power BI Product Dashboard
- Top-selling product analysis
- Product demand analysis
- AI chatbot product-related queries

### Key Metrics

- Total Orders
- Total Items Sold
- Total Product Sales
- Total Freight
- Total Revenue
- Average Product Price