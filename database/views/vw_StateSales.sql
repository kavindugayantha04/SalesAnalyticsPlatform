USE SalesAnalytics_DB;
GO

CREATE VIEW vw_StateSales AS

SELECT

    c.customer_state,

    COUNT(DISTINCT o.order_id) AS total_orders,

    COUNT(oi.order_item_id) AS total_items_sold,

    ROUND(SUM(oi.price), 2) AS total_product_value,
 
    ROUND(SUM(oi.freight_value), 2) AS total_freight,

    ROUND(SUM(oi.price + oi.freight_value), 2) AS total_revenue,

    ROUND(
        SUM(oi.price + oi.freight_value)
        / COUNT(DISTINCT o.order_id),
        2
    ) AS average_order_value

FROM Customers c

INNER JOIN Orders o
    ON c.customer_id = o.customer_id

INNER JOIN OrderItems oi
    ON o.order_id = oi.order_id

GROUP BY

    c.customer_state;
GO