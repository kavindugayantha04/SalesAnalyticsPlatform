USE SalesAnalytics_DB;
GO

CREATE TABLE dw.DimDate
(
    DateKey INT NOT NULL PRIMARY KEY,       -- Format: YYYYMMDD
    FullDate DATE NOT NULL,
    DayNumber TINYINT NOT NULL,
    MonthNumber TINYINT NOT NULL,
    MonthName VARCHAR(20) NOT NULL,
    QuarterNumber TINYINT NOT NULL,
    QuarterName VARCHAR(2) NOT NULL,
    YearNumber SMALLINT NOT NULL,
    WeekdayNumber TINYINT NOT NULL,
    WeekdayName VARCHAR(20) NOT NULL,
    IsWeekend BIT NOT NULL
);
GO