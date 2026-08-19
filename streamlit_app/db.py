"""
Database access layer for the Streamlit application.

Every connection is created by the existing shared helper
etl.db_connection.get_connection, so server, database, driver and
authentication settings remain defined in exactly one place.

This layer is read-only. It must never write to the operational
database, the data warehouse or dw.ForecastRevenue.
"""

import sys
import warnings

from contextlib import contextmanager
from pathlib import Path

import pandas as pd
import streamlit as st

# Streamlit adds this folder to sys.path, while package imports such as
# "from streamlit_app import db" require the repository root. Add the
# root first so config can be imported as a package in both cases.
# Importing config then keeps etl importable from that same root.
_project_root = str(Path(__file__).resolve().parent.parent)

if _project_root not in sys.path:

    sys.path.append(_project_root)

from streamlit_app import config


# ============================================================
# SHARED PROJECT CONNECTION HELPER
# ============================================================

# Imported defensively so a missing pyodbc driver surfaces as a readable
# Streamlit error instead of a crash on startup.

try:

    from etl import db_connection as project_db_connection

    IMPORT_ERROR = None

except Exception as error:

    project_db_connection = None

    IMPORT_ERROR = error


class DatabaseError(RuntimeError):
    """Raised when the Streamlit layer cannot reach SQL Server."""


# ============================================================
# CONNECTION
# ============================================================

def get_connection():
    """
    Open a new SQL Server connection using the shared project helper.

    The caller owns the connection and is responsible for closing it.
    Prefer connection_scope() unless a raw connection is required.
    """

    if project_db_connection is None:

        raise DatabaseError(
            "Could not import etl.db_connection. "
            f"Original error: {IMPORT_ERROR}"
        )

    connection = project_db_connection.get_connection()

    # The shared helper reports failures by returning None and printing
    # the driver error to the console.
    if connection is None:

        raise DatabaseError(
            "etl.db_connection.get_connection() did not return a "
            "connection. Check that SQL Server is running, that the "
            "ODBC driver is installed and that the current Windows "
            "user can access the database. The driver-level error is "
            "printed in the terminal running Streamlit."
        )

    return connection


@contextmanager
def connection_scope():
    """
    Provide a connection that is always closed when the block exits.
    """

    connection = get_connection()

    try:

        yield connection

    finally:

        connection.close()


def get_connection_info():
    """
    Report the connection settings owned by etl/db_connection.py.
    """

    if project_db_connection is None:

        return {}

    return {
        "Server": project_db_connection.SERVER,
        "Database": project_db_connection.DATABASE,
        "Driver": project_db_connection.DRIVER,
        "Authentication": "Windows Trusted Connection",
    }


# ============================================================
# QUERY EXECUTION
# ============================================================

@st.cache_data(ttl=config.QUERY_CACHE_TTL, show_spinner=False)
def run_query(sql, params=None):
    """
    Run a read-only query and return the result as a DataFrame.

    Results are cached so repeated page interactions do not re-query the
    warehouse. Pass parameters as a sequence of pyodbc placeholders
    rather than building SQL strings by concatenation.
    """

    with connection_scope() as connection:

        with warnings.catch_warnings():

            # pandas warns that pyodbc is not a SQLAlchemy connection.
            # The rest of the project reads through pyodbc the same way.
            warnings.simplefilter("ignore", UserWarning)

            return pd.read_sql(sql, connection, params=params)


# ============================================================
# CONNECTION TEST
# ============================================================

def test_connection():
    """
    Run a lightweight round trip against SQL Server.

    Returns a (connected, detail) pair. Failures are returned rather
    than raised so the interface can stay usable without a database.
    """

    try:

        with connection_scope() as connection:

            cursor = connection.cursor()

            try:

                cursor.execute("SELECT DB_NAME(), @@VERSION;")

                database_name, server_version = cursor.fetchone()

            finally:

                cursor.close()

    except Exception as error:

        return False, str(error)

    edition = server_version.splitlines()[0].strip()

    return True, f"{database_name} on {edition}"
