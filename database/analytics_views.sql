USE SalesAnalytics_DB;
GO

CREATE VIEW vw_SalesSummary AS

SELECT

    o.order_id,
    o.order_purchase_timestamp,
    o.order_status,

    c.customer_id,
    c.customer_city,
    c.customer_state,

    SUM(oi.price) AS total_product_value,
    SUM(oi.freight_value) AS total_freight,

    SUM(oi.price + oi.freight_value) AS total_order_value,

    COUNT(oi.order_item_id) AS total_items

FROM Orders o

JOIN Customers c
    ON o.customer_id = c.customer_id

JOIN OrderItems oi
    ON o.order_id = oi.order_id

GROUP BY

    o.order_id,
    o.order_purchase_timestamp,
    o.order_status,

    c.customer_id,
    c.customer_city,
    c.customer_state;
GO