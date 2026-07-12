USE SalesAnalytics_DB;
GO

CREATE VIEW vw_PaymentAnalysis AS

SELECT

    payment_type,

    COUNT(*) AS total_payments,

    COUNT(DISTINCT order_id) AS total_orders,

    SUM(payment_installments) AS total_installments,

    ROUND(AVG(payment_installments), 2) AS average_installments,

    ROUND(SUM(payment_value), 2) AS total_payment_value,

    ROUND(AVG(payment_value), 2) AS average_payment_value

FROM Payments

GROUP BY

    payment_type;
GO