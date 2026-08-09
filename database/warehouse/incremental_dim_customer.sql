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
    c.customer_id,
    c.customer_unique_id,
    c.customer_zip_code_prefix,
    c.customer_city,
    c.customer_state
FROM dbo.Customers AS c
WHERE NOT EXISTS
(
    SELECT 1
    FROM dw.DimCustomer AS dc
    WHERE dc.CustomerID = c.customer_id
);
GO