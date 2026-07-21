USE SalesAnalytics_DB;
GO

INSERT INTO dw.DimProduct
(
    ProductID,
    ProductCategoryName,
    ProductCategoryEnglish,
    ProductNameLength,
    ProductDescriptionLength,
    ProductPhotosQty,
    ProductWeightGrams,
    ProductLengthCm,
    ProductHeightCm,
    ProductWidthCm
)
SELECT
    p.product_id,
    p.product_category_name,
    pct.product_category_name_english,
    p.product_name_length,
    p.product_description_length,
    p.product_photos_qty,
    p.product_weight_g,
    p.product_length_cm,
    p.product_height_cm,
    p.product_width_cm
FROM dbo.Products AS p
LEFT JOIN dbo.ProductCategoryTranslation AS pct
    ON p.product_category_name = pct.product_category_name;
GO