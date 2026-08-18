USE SalesAnalytics_DB;
GO

CREATE TABLE dw.MLExcludedOrders
(
    OrderID VARCHAR(50) NOT NULL,
    Reason VARCHAR(200) NOT NULL,

    CONSTRAINT PK_MLExcludedOrders
        PRIMARY KEY (OrderID)
);
GO