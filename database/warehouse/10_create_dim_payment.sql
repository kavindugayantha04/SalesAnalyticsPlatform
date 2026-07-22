USE SalesAnalytics_DB;
GO

CREATE TABLE dw.DimPayment
(
    PaymentKey INT IDENTITY(1,1) PRIMARY KEY,
    PaymentType VARCHAR(50) NOT NULL
);
GO