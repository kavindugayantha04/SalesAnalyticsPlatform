USE SalesAnalytics_DB;
GO

CREATE TABLE dw.DimProduct
(
    ProductKey INT IDENTITY(1,1) PRIMARY KEY,
    ProductID VARCHAR(50) NOT NULL,
    ProductCategoryName VARCHAR(100) NULL,
    ProductCategoryEnglish VARCHAR(100) NULL,
    ProductNameLength INT NULL,
    ProductDescriptionLength INT NULL,
    ProductPhotosQty INT NULL,
    ProductWeightGrams INT NULL,
    ProductLengthCm INT NULL,
    ProductHeightCm INT NULL,
    ProductWidthCm INT NULL
);
GO