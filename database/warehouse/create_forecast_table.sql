CREATE TABLE dw.ForecastRevenue
(
    ForecastID INT IDENTITY(1,1) PRIMARY KEY,

    ForecastYear INT NOT NULL,

    ForecastMonth INT NOT NULL,

    PredictedRevenue DECIMAL(18,2) NOT NULL,

    ModelVersion VARCHAR(50) NOT NULL,

    PredictionDate DATETIME NOT NULL DEFAULT GETDATE()
);