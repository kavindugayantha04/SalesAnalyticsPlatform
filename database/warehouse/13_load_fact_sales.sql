USE SalesAnalytics_DB;
GO

/*==============================================================
  Payment Summary
  - One row per order
==============================================================*/
WITH PaymentSummary AS
(
    SELECT
        order_id,
        SUM(payment_value) AS PaymentValue,
        MAX(payment_installments) AS PaymentInstallments
    FROM dbo.Payments
    GROUP BY order_id
),

/*==============================================================
  Primary Payment
  - First payment method for each order
==============================================================*/
PrimaryPayment AS
(
    SELECT
        order_id,
        payment_type
    FROM
    (
        SELECT
            order_id,
            payment_type,
            ROW_NUMBER() OVER
            (
                PARTITION BY order_id
                ORDER BY payment_sequential
            ) AS rn
        FROM dbo.Payments
    ) p
    WHERE rn = 1
),

/*==============================================================
  Latest Review
  - Keep only the latest review per order
==============================================================*/
ReviewSummary AS
(
    SELECT
        order_id,
        review_score
    FROM
    (
        SELECT
            order_id,
            review_score,
            ROW_NUMBER() OVER
            (
                PARTITION BY order_id
                ORDER BY review_creation_date DESC,
                         review_answer_timestamp DESC
            ) AS rn
        FROM dbo.Reviews
    ) r
    WHERE rn = 1
)

INSERT INTO dw.FactSales
(
    OrderID,
    OrderItemID,
    DateKey,
    CustomerKey,
    ProductKey,
    SellerKey,
    PaymentKey,
    SalesAmount,
    FreightAmount,
    PaymentValue,
    PaymentInstallments,
    ReviewScore
)

SELECT

    oi.order_id,

    oi.order_item_id,

    CONVERT
    (
        INT,
        CONVERT(CHAR(8), o.order_purchase_timestamp, 112)
    ) AS DateKey,

    dc.CustomerKey,

    dp.ProductKey,

    ds.SellerKey,

    paydim.PaymentKey,

    oi.price AS SalesAmount,

    oi.freight_value AS FreightAmount,

    ps.PaymentValue,

    ps.PaymentInstallments,

    rs.review_score

FROM dbo.OrderItems oi

INNER JOIN dbo.Orders o
    ON oi.order_id = o.order_id

INNER JOIN dw.DimCustomer dc
    ON o.customer_id = dc.CustomerID

INNER JOIN dw.DimProduct dp
    ON oi.product_id = dp.ProductID

INNER JOIN dw.DimSeller ds
    ON oi.seller_id = ds.SellerID

/* Exclude orders without payment records */
INNER JOIN PaymentSummary ps
    ON oi.order_id = ps.order_id

INNER JOIN PrimaryPayment pp
    ON oi.order_id = pp.order_id

INNER JOIN dw.DimPayment paydim
    ON pp.payment_type = paydim.PaymentType

/* Reviews are optional */
LEFT JOIN ReviewSummary rs
    ON oi.order_id = rs.order_id;

GO