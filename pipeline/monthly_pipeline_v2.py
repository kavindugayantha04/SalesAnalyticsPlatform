import os
import re
import subprocess
import sys

from etl.db_connection import get_connection


# ============================================================
# PROJECT PATHS
# ============================================================

PROJECT_ROOT = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

WAREHOUSE_PATH = os.path.join(
    PROJECT_ROOT,
    "database",
    "warehouse"
)


# ============================================================
# HELPER — RUN PYTHON MODULE
# ============================================================

def run_python_module(module_name):

    print("\n======================================")
    print(f"RUNNING: {module_name}")
    print("======================================")

    result = subprocess.run(
        [sys.executable, "-m", module_name],
        cwd=PROJECT_ROOT
    )

    if result.returncode != 0:

        raise Exception(
            f"{module_name} failed."
        )

    print(
        f"{module_name} completed successfully."
    )


# ============================================================
# HELPER — EXECUTE SQL FILE
# ============================================================

def run_sql_file(file_name):

    file_path = os.path.join(
        WAREHOUSE_PATH,
        file_name
    )

    print("\n======================================")
    print(f"RUNNING SQL: {file_name}")
    print("======================================")

    if not os.path.exists(file_path):

        raise FileNotFoundError(
            f"SQL file not found: {file_path}"
        )

    connection = get_connection()

    if connection is None:

        raise Exception(
            "Failed to connect to SQL Server."
        )

    cursor = connection.cursor()

    try:

        with open(
            file_path,
            "r",
            encoding="utf-8"
        ) as file:

            sql_script = file.read()

        # ----------------------------------------------------
        # Split SQL script at GO batch separators
        # ----------------------------------------------------

        batches = [
            batch.strip()
            for batch in re.split(
                r"^\s*GO\s*$",
                sql_script,
                flags=re.MULTILINE | re.IGNORECASE
            )
            if batch.strip()
        ]

        # ----------------------------------------------------
        # Execute each SQL batch
        # ----------------------------------------------------

        for batch in batches:

            cursor.execute(batch)

        connection.commit()

        print(
            f"{file_name} completed successfully."
        )

    except Exception as error:

        connection.rollback()

        print(
            f"{file_name} failed."
        )

        raise error

    finally:

        cursor.close()
        connection.close()


# ============================================================
# MAIN PIPELINE
# ============================================================

def main():

    print("\n")
    print("==============================================")
    print("   MONTHLY SALES ANALYTICS PIPELINE V2")
    print("==============================================")

    try:

        # ----------------------------------------------------
        # STEP 1 — MONTHLY UPLOAD ETL
        # ----------------------------------------------------

        run_python_module(
            "etl.monthly_upload_etl"
        )


        # ----------------------------------------------------
        # STEP 2 — INCREMENTAL DIMENSIONS
        # ----------------------------------------------------

        run_sql_file(
            "incremental_dim_customer.sql"
        )

        run_sql_file(
            "incremental_dim_product.sql"
        )

        run_sql_file(
            "incremental_dim_seller.sql"
        )

        run_sql_file(
            "incremental_dim_payment.sql"
        )


        # ----------------------------------------------------
        # STEP 3 — INCREMENTAL FACT TABLE
        # ----------------------------------------------------

        run_sql_file(
            "incremental_fact_sales.sql"
        )


        # ----------------------------------------------------
        # STEP 4 — RETRAIN GRADIENT BOOSTING MODEL
        # ----------------------------------------------------

        run_python_module(
            "ml.pipeline.retrain_model_v2"
        )


        # ----------------------------------------------------
        # STEP 5 — GENERATE NEXT-MONTH FORECAST
        # ----------------------------------------------------

        run_python_module(
            "ml.pipeline.predict_next_month_v2"
        )


        # ----------------------------------------------------
        # PIPELINE SUCCESS
        # ----------------------------------------------------

        print("\n")
        print("==============================================")
        print("      MONTHLY PIPELINE V2 COMPLETED")
        print("==============================================")

        print("\nAll stages completed successfully.")

        print("\nPipeline:")
        print("Upload")
        print("  ↓")
        print("Operational Database")
        print("  ↓")
        print("Incremental Dimensions")
        print("  ↓")
        print("FactSales")
        print("  ↓")
        print("Gradient Boosting Model Retraining")
        print("  ↓")
        print("Gradient Boosting Next Month Forecast")
        print("  ↓")
        print("ForecastRevenue")


    except Exception as error:

        print("\n")
        print("==============================================")
        print("      MONTHLY PIPELINE V2 FAILED")
        print("==============================================")

        print(
            f"\nError: {error}"
        )

        sys.exit(1)


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":

    main()
