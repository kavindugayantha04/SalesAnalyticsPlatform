USE SalesAnalytics_DB;
GO

CREATE TABLE dw.DimSeller
(
    SellerKey INT IDENTITY(1,1) PRIMARY KEY,
    SellerID VARCHAR(50) NOT NULL,
    ZipCodePrefix INT NOT NULL,
    SellerCity VARCHAR(100) NOT NULL,
    SellerState CHAR(2) NOT NULL
);
GO