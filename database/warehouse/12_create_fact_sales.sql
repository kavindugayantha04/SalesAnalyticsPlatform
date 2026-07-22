USE SalesAnalytics_DB;
GO

CREATE TABLE dw.FactSales
(
    SalesKey BIGINT IDENTITY(1,1) PRIMARY KEY,

    -- Degenerate Dimensions
    OrderID VARCHAR(50) NOT NULL,
    OrderItemID INT NOT NULL,

    -- Foreign Keys
    DateKey INT NOT NULL,
    CustomerKey INT NOT NULL,
    ProductKey INT NOT NULL,
    SellerKey INT NOT NULL,
    PaymentKey INT NOT NULL,

    -- Measures
    SalesAmount DECIMAL(10,2) NOT NULL,
    FreightAmount DECIMAL(10,2) NOT NULL,
    PaymentValue DECIMAL(10,2) NULL,
    PaymentInstallments INT NULL,
    ReviewScore TINYINT NULL,

    -- Foreign Key Constraints
    CONSTRAINT FK_FactSales_DimDate
        FOREIGN KEY (DateKey)
        REFERENCES dw.DimDate(DateKey),

    CONSTRAINT FK_FactSales_DimCustomer
        FOREIGN KEY (CustomerKey)
        REFERENCES dw.DimCustomer(CustomerKey),

    CONSTRAINT FK_FactSales_DimProduct
        FOREIGN KEY (ProductKey)
        REFERENCES dw.DimProduct(ProductKey),

    CONSTRAINT FK_FactSales_DimSeller
        FOREIGN KEY (SellerKey)
        REFERENCES dw.DimSeller(SellerKey),

    CONSTRAINT FK_FactSales_DimPayment
        FOREIGN KEY (PaymentKey)
        REFERENCES dw.DimPayment(PaymentKey)
);
GO