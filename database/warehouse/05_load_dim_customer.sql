USE SalesAnalytics_DB;
GO

INSERT INTO dw.DimCustomer
(
    CustomerID,
    CustomerUniqueID,
    ZipCodePrefix,
    CustomerCity,
    CustomerState
)
SELECT
    customer_id,
    customer_unique_id,
    customer_zip_code_prefix,
    customer_city,
    customer_state
FROM dbo.Customers;
GO