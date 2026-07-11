USE SalesAnalytics_DB;
GO

CREATE VIEW vw_ProductPerformance AS

SELECT

    p.product_id,

    pct.product_category_name_english AS category_name,

    COUNT(DISTINCT oi.order_id) AS total_orders,

    COUNT(*) AS total_items_sold,

    ROUND(SUM(oi.price), 2) AS total_product_sales,

    ROUND(SUM(oi.freight_value), 2) AS total_freight,

    ROUND(SUM(oi.price + oi.freight_value), 2) AS total_revenue,

    ROUND(AVG(oi.price), 2) AS average_product_price

FROM Products p

INNER JOIN OrderItems oi
    ON p.product_id = oi.product_id

LEFT JOIN ProductCategoryTranslation pct
    ON p.product_category_name = pct.product_category_name

GROUP BY

    p.product_id,
    pct.product_category_name_english;
GO