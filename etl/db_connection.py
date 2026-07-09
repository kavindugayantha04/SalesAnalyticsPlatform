import pyodbc

# SQL Server Configuration
SERVER = "localhost"
DATABASE = "SalesAnalytics_DB"
DRIVER = "ODBC Driver 17 for SQL Server"


def get_connection():
    """
    Creates and returns a SQL Server database connection.
    """

    try:
        connection = pyodbc.connect(
            f"DRIVER={{{DRIVER}}};"
            f"SERVER={SERVER};"
            f"DATABASE={DATABASE};"
            "Trusted_Connection=yes;"
        )

        print("Connected to SQL Server successfully.")

        return connection

    except Exception as e:
        print("Database Connection Failed!")
        print(e)
        return None