USE SalesAnalytics_DB;
GO

INSERT INTO dw.DimPayment
(
    PaymentType
)
SELECT DISTINCT
    p.payment_type
FROM dbo.Payments AS p
WHERE p.payment_type IS NOT NULL
AND NOT EXISTS
(
    SELECT 1
    FROM dw.DimPayment AS dp
    WHERE dp.PaymentType = p.payment_type
);
GO