IF NOT EXISTS (
    SELECT *
    FROM sys.databases
    WHERE name = 'SalesAnalytics_DB'
)
BEGIN
    CREATE DATABASE SalesAnalytics_DB;
END;
GO