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
 
------------------------------------------------

## vw_MonthlySales

### Purpose

Provides monthly sales performance, including total revenue, total orders, and average order value.

### Source View

- vw_SalesSummary

### Primary Use

- Power BI monthly sales dashboard
- Sales forecasting (Machine Learning)
- Chatbot monthly sales queries