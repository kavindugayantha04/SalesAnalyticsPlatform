USE SalesAnalytics_DB;
GO

CREATE VIEW vw_CategorySales AS

SELECT

    pct.product_category_name_english AS category_name,

    COUNT(DISTINCT oi.order_id) AS total_orders,

    SUM(oi.price) AS total_product_sales,

    SUM(oi.freight_value) AS total_freight,

    SUM(oi.price + oi.freight_value) AS total_revenue,

    COUNT(*) AS total_items_sold,

    AVG(oi.price) AS average_product_price

FROM OrderItems oi

INNER JOIN Products p
    ON oi.product_id = p.product_id

INNER JOIN ProductCategoryTranslation pct
    ON p.product_category_name = pct.product_category_name

GROUP BY
    pct.product_category_name_english;
GO