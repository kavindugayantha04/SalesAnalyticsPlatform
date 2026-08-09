USE SalesAnalytics_DB;
GO

INSERT INTO dw.DimSeller
(
    SellerID,
    ZipCodePrefix,
    SellerCity,
    SellerState
)
SELECT
    s.seller_id,
    s.seller_zip_code_prefix,
    s.seller_city,
    s.seller_state
FROM dbo.Sellers AS s
WHERE NOT EXISTS
(
    SELECT 1
    FROM dw.DimSeller AS ds
    WHERE ds.SellerID = s.seller_id
);
GO