USE SalesAnalytics_DB;
GO

CREATE OR ALTER VIEW dw.vw_RevenueActualForecast
AS

-- Actual Revenue
SELECT
    YearNumber,
    MonthNumber,
    MonthName,
    YearMonth,
    MonthlyRevenue AS Revenue,
    'Actual' AS RevenueType
FROM dw.vw_MonthlyRevenueML

UNION ALL

-- Forecast Revenue
SELECT
    ForecastYear AS YearNumber,
    ForecastMonth AS MonthNumber,

    DATENAME(
        MONTH,
        DATEFROMPARTS(
            ForecastYear,
            ForecastMonth,
            1
        )
    ) AS MonthName,

    ForecastYearMonth AS YearMonth,

    PredictedRevenue AS Revenue,
    'Forecast' AS RevenueType

FROM dw.vw_RevenueForecast;
GO