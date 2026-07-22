USE SalesAnalytics_DB;
GO

INSERT INTO dw.DimPayment (PaymentType)
SELECT DISTINCT payment_type
FROM dbo.Payments
ORDER BY payment_type;
GO