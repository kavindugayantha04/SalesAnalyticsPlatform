"""
Power BI Dashboards page.

Detailed BI reporting remains in the existing local Power BI Desktop
report. This page explains that report and helps the user locate or
open the PBIX file. The report itself is never modified here.
"""

import os
import subprocess
import sys

import streamlit as st

import config


def render():
    """
    Render the Power BI Dashboards page.
    """

    st.subheader("Power BI Desktop Report")

    report_path = config.POWER_BI_REPORT_PATH
    report_exists = report_path.is_file()

    if report_exists:

        st.success("Available locally")

    else:

        st.warning("Report file not found at the expected project path.")

    st.markdown("**Report**")

    st.code(str(report_path), language=None)

    st.markdown("")

    if report_exists:

        if st.button("Open / Locate Report", type="primary"):

            _attempt_open_report(report_path)

    else:

        st.button("Open / Locate Report", type="primary", disabled=True)

    st.caption(
        "Open the report in Power BI Desktop on this machine. "
        "The PBIX file is not published to Power BI Service."
    )

    st.markdown("")

    st.subheader("Available Dashboards")

    for dashboard in config.POWER_BI_DASHBOARDS:

        st.markdown(f"**{dashboard['name']}**")

        st.write(dashboard["description"])

        st.markdown("")


def _attempt_open_report(report_path):
    """
    Try to open the PBIX with the operating system's default application.
    """

    resolved_path = str(report_path.resolve())

    try:

        if sys.platform == "win32":

            os.startfile(resolved_path)  # noqa: S606 — local desktop report

            st.success(
                "Opening the report with the default application on this "
                "machine."
            )

            return

        if sys.platform == "darwin":

            subprocess.run(
                ["open", resolved_path],
                check=True,
            )

            st.success("Opening the report with the default application.")

            return

        subprocess.run(
            ["xdg-open", resolved_path],
            check=True,
        )

        st.success("Opening the report with the default application.")

    except Exception as error:

        st.info(
            "Automatic opening is not available from this Streamlit session. "
            "Open the file manually in Power BI Desktop using the path above."
        )

        st.caption(str(error))
