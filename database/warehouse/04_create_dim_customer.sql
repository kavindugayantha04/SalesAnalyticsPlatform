USE SalesAnalytics_DB;
GO

CREATE TABLE dw.DimCustomer
(
    CustomerKey INT IDENTITY(1,1) PRIMARY KEY,
    CustomerID VARCHAR(50) NOT NULL,
    CustomerUniqueID VARCHAR(50) NOT NULL,
    ZipCodePrefix INT NOT NULL,
    CustomerCity VARCHAR(100) NOT NULL,
    CustomerState CHAR(2) NOT NULL
);
GO