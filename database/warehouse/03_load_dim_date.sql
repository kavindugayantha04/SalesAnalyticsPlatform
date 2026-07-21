USE SalesAnalytics_DB;
GO

DECLARE @StartDate DATE = '2016-01-01';
DECLARE @EndDate   DATE = '2019-12-31';

;WITH Numbers AS
(
    SELECT TOP (DATEDIFF(DAY, @StartDate, @EndDate) + 1)
           ROW_NUMBER() OVER (ORDER BY (SELECT NULL)) - 1 AS Number
    FROM sys.all_objects
)
INSERT INTO dw.DimDate
(
    DateKey,
    FullDate,
    DayNumber,
    MonthNumber,
    MonthName,
    QuarterNumber,
    QuarterName,
    YearNumber,
    WeekdayNumber,
    WeekdayName,
    IsWeekend
)
SELECT
    CONVERT(INT, CONVERT(CHAR(8), DATEADD(DAY, Number, @StartDate), 112)) AS DateKey,
    DATEADD(DAY, Number, @StartDate) AS FullDate,
    DAY(DATEADD(DAY, Number, @StartDate)) AS DayNumber,
    MONTH(DATEADD(DAY, Number, @StartDate)) AS MonthNumber,
    DATENAME(MONTH, DATEADD(DAY, Number, @StartDate)) AS MonthName,
    DATEPART(QUARTER, DATEADD(DAY, Number, @StartDate)) AS QuarterNumber,
    CONCAT('Q', DATEPART(QUARTER, DATEADD(DAY, Number, @StartDate))) AS QuarterName,
    YEAR(DATEADD(DAY, Number, @StartDate)) AS YearNumber,
    DATEPART(WEEKDAY, DATEADD(DAY, Number, @StartDate)) AS WeekdayNumber,
    DATENAME(WEEKDAY, DATEADD(DAY, Number, @StartDate)) AS WeekdayName,
    CASE
        WHEN DATENAME(WEEKDAY, DATEADD(DAY, Number, @StartDate)) IN ('Saturday','Sunday')
            THEN 1
        ELSE 0
    END AS IsWeekend
FROM Numbers;
GO