USE SalesAnalytics_DB;
GO

CREATE OR ALTER VIEW vw_MonthlySales AS

SELECT

    YEAR(order_purchase_timestamp) AS sales_year,

    MONTH(order_purchase_timestamp) AS month_number,

    DATENAME(MONTH, order_purchase_timestamp) AS month_name,

    FORMAT(order_purchase_timestamp, 'yyyy-MM') AS year_month,

    COUNT(order_id) AS total_orders,

    ROUND(SUM(total_order_value), 2) AS total_revenue,

    ROUND(AVG(total_order_value), 2) AS average_order_value

FROM vw_SalesSummary

GROUP BY

    YEAR(order_purchase_timestamp),
    MONTH(order_purchase_timestamp),
    DATENAME(MONTH, order_purchase_timestamp),
    FORMAT(order_purchase_timestamp, 'yyyy-MM');
GO