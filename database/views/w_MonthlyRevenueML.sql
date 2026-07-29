USE SalesAnalytics_DB;
GO

CREATE OR ALTER VIEW dw.vw_MonthlyRevenueML
AS

SELECT

    d.YearNumber,

    d.MonthNumber,

    d.MonthName,

    CONCAT(
        d.YearNumber,
        '-',
        RIGHT('0' + CAST(d.MonthNumber AS VARCHAR(2)), 2)
    ) AS YearMonth,

    SUM(f.SalesAmount) AS MonthlyRevenue,

    COUNT(DISTINCT f.OrderID) AS TotalOrders,

    AVG(f.SalesAmount) AS AverageOrderValue

FROM dw.FactSales AS f

INNER JOIN dw.DimDate AS d
    ON f.DateKey = d.DateKey

GROUP BY
    d.YearNumber,
    d.MonthNumber,
    d.MonthName;
GO