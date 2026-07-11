USE SalesAnalytics_DB;
GO

CREATE VIEW vw_MonthlySales AS

SELECT

    YEAR(order_purchase_timestamp) AS sales_year,
    MONTH(order_purchase_timestamp) AS sales_month,

    COUNT(order_id) AS total_orders,

    SUM(total_order_value) AS total_revenue,

    AVG(total_order_value) AS average_order_value

FROM vw_SalesSummary

GROUP BY

    YEAR(order_purchase_timestamp),
    MONTH(order_purchase_timestamp);
GO