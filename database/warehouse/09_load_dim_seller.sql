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
    seller_id,
    seller_zip_code_prefix,
    seller_city,
    seller_state
FROM dbo.Sellers;
GO