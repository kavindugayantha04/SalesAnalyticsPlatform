# ETL Setup

## Purpose

This module establishes a connection between Python and Microsoft SQL Server using the `pyodbc` library.

## Components

- `db_connection.py` – Creates a reusable SQL Server connection.
- `test_connection.py` – Verifies that Python can successfully connect to the database.

## Connection Details

- Database: SalesAnalytics_DB
- Authentication: Windows Authentication (Trusted Connection)
- Driver: ODBC Driver 17 for SQL Server

## Result

The connection was successfully established, confirming that the ETL pipeline is ready to begin loading data into SQL Server.