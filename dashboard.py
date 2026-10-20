
import re
import sqlite3
import subprocess
import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


# =========================================================
# 1. PROJECT CONFIGURATION
# =========================================================

BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "data" / "retail_sales.csv"
DATABASE_FILE = BASE_DIR / "data" / "retail_sales.db"
REPORTS_DIR = BASE_DIR / "data" / "reports"
PIPELINE_FILE = BASE_DIR / "run_project.py"
LOG_FILE = BASE_DIR / "logs" / "pipeline.log"

BG = "#050505"
PANEL = "#101010"
BORDER = "#292929"
GREEN = "#39FF14"
TEXT = "#F5F5F5"
MUTED = "#929292"

st.set_page_config(
    page_title="Obsidian | Retail ETL",
    page_icon="🟢",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# =========================================================
# 2. OBSIDIAN TERMINAL THEME
# =========================================================

st.markdown(
    f"""
    <style>
    .stApp {{
        background: {BG};
        color: {TEXT};
    }}

    [data-testid="stHeader"] {{
        background: {BG};
    }}

    .block-container {{
        max-width: 1600px;
        padding-top: 1rem;
        padding-bottom: 1rem;
        padding-left: 2rem;
        padding-right: 2rem;
    }}

    h1, h2, h3 {{
        color: {TEXT} !important;
        letter-spacing: -0.4px;
    }}

    p, label, .stMarkdown {{
        color: {TEXT};
    }}

    [data-testid="stMetric"] {{
        background: {PANEL};
        border: 1px solid {BORDER};
        border-radius: 8px;
        padding: 12px 14px;
    }}

    [data-testid="stMetricLabel"] {{
        color: {MUTED} !important;
    }}

    [data-testid="stMetricValue"] {{
        color: {GREEN} !important;
        font-weight: 700;
    }}

    [data-testid="stMetricDelta"] {{
        color: {GREEN} !important;
    }}

    div.stButton > button,
    div.stDownloadButton > button {{
        background: {GREEN};
        color: #050505;
        border: 1px solid {GREEN};
        border-radius: 6px;
        font-weight: 700;
        min-height: 38px;
    }}

    div.stButton > button:hover,
    div.stDownloadButton > button:hover {{
        background: #B5FFAA;
        color: #050505;
        border-color: #B5FFAA;
    }}

    div[data-testid="stExpander"] {{
        background: {PANEL};
        border: 1px solid {BORDER};
        border-radius: 8px;
    }}

    [data-testid="stDataFrame"] {{
        border: 1px solid {BORDER};
        border-radius: 6px;
    }}

    hr {{
        border-color: {BORDER};
    }}

    .terminal-title {{
        color: {GREEN};
        font-family: monospace;
        font-size: 12px;
        letter-spacing: 2px;
        margin-bottom: 5px;
    }}

    .system-title {{
        font-size: 27px;
        font-weight: 800;
        color: {TEXT};
        line-height: 1.2;
    }}

    .system-subtitle {{
        color: {MUTED};
        font-size: 12px;
        margin-top: 6px;
    }}

    .status-pill {{
        display: inline-block;
        color: {GREEN};
        background: #101A0D;
        border: 1px solid #294D20;
        padding: 5px 10px;
        border-radius: 5px;
        font-family: monospace;
        font-size: 11px;
        white-space: nowrap;
    }}

    .stage-card {{
        background: {PANEL};
        border: 1px solid {BORDER};
        border-radius: 8px;
        padding: 12px;
        min-height: 76px;
    }}

    .stage-name {{
        color: {TEXT};
        font-size: 13px;
        font-weight: 600;
        margin-bottom: 6px;
    }}

    .stage-status {{
        color: {GREEN};
        font-size: 11px;
        font-family: monospace;
    }}

    .section-label {{
        color: {GREEN};
        font-family: monospace;
        font-size: 12px;
        letter-spacing: 1px;
    }}

    #MainMenu, footer {{
        visibility: hidden;
    }}

    @media (max-width: 768px) {{
        .block-container {{
            padding-left: 0.8rem;
            padding-right: 0.8rem;
        }}

        .system-title {{
            font-size: 21px;
        }}
    }}
    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# 3. HELPER FUNCTIONS
# =========================================================

def load_source_data():
    """Read the original CSV file."""
    if not DATA_FILE.exists():
        return None

    return pd.read_csv(DATA_FILE, encoding="cp1252")


def load_database_data():
    """Read processed records from SQLite."""
    if not DATABASE_FILE.exists():
        return None

    with sqlite3.connect(DATABASE_FILE) as connection:
        return pd.read_sql_query(
            "SELECT * FROM retail_sales",
            connection,
        )


def load_log():
    """Read the latest pipeline log."""
    if not LOG_FILE.exists():
        return "No pipeline log found yet."

    return LOG_FILE.read_text(
        encoding="utf-8",
        errors="replace",
    )


def clean_output(output):
    """Put known pipeline messages on separate lines."""
    labels = [
        "ETL pipeline completed successfully!",
        "Raw rows extracted:",
        "Rows validated:",
        "Rows loaded into SQLite:",
        "Database location:",
        "Reports generated successfully!",
        "Reports saved to:",
        "Category report rows:",
        "Region report rows:",
        "Loss-making subcategories:",
        "Running: pipeline.py",
        "Running: generate_reports.py",
        "Complete project workflow finished successfully!",
    ]

    for label in labels:
        output = re.sub(
            rf"\s*({re.escape(label)})",
            r"\n\1",
            output,
        )

    return output.strip()


def stage_card(title, detail, completed):
    """Display one compact pipeline stage."""
    status = "● COMPLETE" if completed else "○ PENDING"
    status_color = GREEN if completed else MUTED

    st.markdown(
        f"""
        <div class="stage-card">
            <div class="stage-name">{title}</div>
            <div style="color:{MUTED};font-size:11px;margin-bottom:6px;">
                {detail}
            </div>
            <div class="stage-status" style="color:{status_color};">
                {status}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# =========================================================
# 4. HEADER
# =========================================================

header_left, header_right = st.columns([4, 1])

with header_left:
    st.markdown(
        """
        <div class="terminal-title">SYSTEM / DATA ENGINEERING / 001</div>
        <div class="system-title">RETAIL ETL CONTROL CENTER</div>
        <div class="system-subtitle">
            EXTRACT &nbsp; / &nbsp; TRANSFORM &nbsp; / &nbsp;
            VALIDATE &nbsp; / &nbsp; LOAD
        </div>
        """,
        unsafe_allow_html=True,
    )

with header_right:
    st.markdown(
        f"""
        <div style="text-align:right;padding-top:8px;">
            <span class="status-pill">● OBSIDIAN MODE</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown("---")


# =========================================================
# 5. LOAD CURRENT DATA
# =========================================================

source_df = None
database_df = None
database_error = None

try:
    source_df = load_source_data()
except Exception as error:
    st.error(f"Could not read the source CSV: {error}")

try:
    database_df = load_database_data()
except Exception as error:
    database_error = str(error)


# =========================================================
# 6. PIPELINE EXECUTION
# =========================================================

st.markdown(
    '<div class="section-label">01 / PIPELINE EXECUTION</div>',
    unsafe_allow_html=True,
)

run_col, info_col = st.columns([1, 3])

with run_col:
    run_pipeline = st.button(
        "▶  RUN ETL PIPELINE",
        type="primary",
        use_container_width=True,
    )

with info_col:
    st.caption(
        "Runs run_project.py, loads the SQLite database, "
        "and regenerates the CSV reports."
    )

if run_pipeline:
    if not PIPELINE_FILE.exists():
        st.error("run_project.py was not found.")
    else:
        try:
            with st.spinner("Executing ETL pipeline..."):
                result = subprocess.run(
                    [sys.executable, str(PIPELINE_FILE)],
                    cwd=str(BASE_DIR),
                    capture_output=True,
                    text=True,
                    timeout=300,
                    encoding="utf-8",
                    errors="replace",
                )

            st.session_state["last_run_success"] = (
                result.returncode == 0
            )
            st.session_state["last_run_output"] = clean_output(
                result.stdout or ""
            )
            st.session_state["last_run_error"] = (
                result.stderr or ""
            )

            if result.returncode == 0:
                st.success("Pipeline completed successfully.")
            else:
                st.error(
                    f"Pipeline failed with exit code "
                    f"{result.returncode}."
                )

        except subprocess.TimeoutExpired:
            st.session_state["last_run_success"] = False
            st.session_state["last_run_output"] = ""
            st.session_state["last_run_error"] = (
                "Pipeline exceeded the 5-minute time limit."
            )
            st.error("Pipeline timed out.")
        except Exception as error:
            st.session_state["last_run_success"] = False
            st.session_state["last_run_output"] = ""
            st.session_state["last_run_error"] = str(error)
            st.error(f"Could not execute pipeline: {error}")

        # Reload files after execution so the dashboard shows
        # the latest database and reports.
        try:
            database_df = load_database_data()
            database_error = None
        except Exception as error:
            database_df = None
            database_error = str(error)

        try:
            source_df = load_source_data()
        except Exception:
            source_df = None


if "last_run_success" not in st.session_state:
    st.session_state["last_run_success"] = None

st.markdown("")


# =========================================================
# 7. COMPACT KPI METRICS
# =========================================================

source_rows = len(source_df) if source_df is not None else 0
loaded_rows = len(database_df) if database_df is not None else 0

report_files = (
    sorted(REPORTS_DIR.glob("*.csv"))
    if REPORTS_DIR.exists()
    else []
)

metric1, metric2, metric3, metric4 = st.columns(4)

metric1.metric("SOURCE RECORDS", f"{source_rows:,}")
metric2.metric("DATABASE RECORDS", f"{loaded_rows:,}")

if database_df is not None:
    rows_not_loaded = max(source_rows - loaded_rows, 0)
    metric3.metric("ROWS NOT LOADED", f"{rows_not_loaded:,}")
else:
    metric3.metric("ROWS NOT LOADED", "—")

metric4.metric("REPORTS AVAILABLE", f"{len(report_files):02d}")

if database_error:
    st.warning(f"Database could not be read: {database_error}")
elif database_df is None:
    st.info("Run the pipeline to create or load the database.")


# =========================================================
# 8. PIPELINE STAGE MONITOR
# =========================================================

st.markdown("")
st.markdown(
    '<div class="section-label">02 / PIPELINE STAGES</div>',
    unsafe_allow_html=True,
)

database_ready = database_df is not None and not database_df.empty
reports_ready = len(report_files) == 3

if st.session_state["last_run_success"] is True:
    validation_ready = True
elif st.session_state["last_run_success"] is False:
    validation_ready = False
else:
    # Before this dashboard runs the pipeline, show stages as
    # ready only when a previous database and reports exist.
    validation_ready = database_ready and reports_ready

stage1, stage2, stage3, stage4 = st.columns(4)

with stage1:
    stage_card(
        "01 / EXTRACT",
        "Source CSV",
        source_df is not None,
    )

with stage2:
    stage_card(
        "02 / VALIDATE",
        "Transform & checks",
        validation_ready,
    )

with stage3:
    stage_card(
        "03 / LOAD",
        "SQLite database",
        database_ready,
    )

with stage4:
    stage_card(
        "04 / REPORT",
        "CSV report generation",
        reports_ready,
    )


# =========================================================
# 9. DATA QUALITY
# =========================================================

st.markdown("")
st.markdown(
    '<div class="section-label">03 / DATA QUALITY</div>',
    unsafe_allow_html=True,
)

if source_df is not None:
    missing_values = int(source_df.isna().sum().sum())
    duplicate_rows = int(source_df.duplicated().sum())

    if "Row ID" in source_df.columns:
        duplicate_ids = int(source_df["Row ID"].duplicated().sum())
    else:
        duplicate_ids = 0

    if "Quantity" in source_df.columns:
        invalid_quantities = int((source_df["Quantity"] <= 0).sum())
    else:
        invalid_quantities = 0

    q1, q2, q3, q4 = st.columns(4)

    q1.metric("MISSING VALUES", f"{missing_values:,}")
    q2.metric("DUPLICATE ROWS", f"{duplicate_rows:,}")
    q3.metric("DUPLICATE ROW IDs", f"{duplicate_ids:,}")
    q4.metric("INVALID QUANTITIES", f"{invalid_quantities:,}")

    if (
        missing_values == 0
        and duplicate_rows == 0
        and duplicate_ids == 0
        and invalid_quantities == 0
    ):
        st.caption("🟢 Basic source data-quality checks passed.")
    else:
        st.warning("Some source data-quality issues were detected.")

    with st.expander("Inspect source data"):
        st.dataframe(
            source_df.head(50),
            use_container_width=True,
            hide_index=True,
        )
else:
    st.warning("Source CSV not found. Check data/retail_sales.csv.")


# =========================================================
# 10. BUSINESS INSIGHTS
# =========================================================

if database_ready:
    st.markdown("")
    st.markdown(
        '<div class="section-label">04 / BUSINESS INTELLIGENCE</div>',
        unsafe_allow_html=True,
    )

    required_columns = {"Category", "Sales", "Profit"}

    if required_columns.issubset(database_df.columns):
        category_summary = (
            database_df.groupby("Category", as_index=False)
            .agg(
                Sales=("Sales", "sum"),
                Profit=("Profit", "sum"),
            )
        )

        chart1, chart2 = st.columns(2)

        with chart1:
            st.markdown("**Sales by Category**")

            fig_sales = px.bar(
                category_summary.sort_values("Sales", ascending=False),
                x="Category",
                y="Sales",
                text_auto=".3s",
                color_discrete_sequence=[GREEN],
            )

            fig_sales.update_traces(
                textposition="outside",
                cliponaxis=False,
            )

            fig_sales.update_layout(
                template="plotly_dark",
                paper_bgcolor=BG,
                plot_bgcolor=PANEL,
                font=dict(color=TEXT, size=11),
                margin=dict(l=10, r=10, t=15, b=10),
                height=270,
                showlegend=False,
                xaxis_title=None,
                yaxis_title=None,
            )

            st.plotly_chart(
                fig_sales,
                use_container_width=True,
                config={"displayModeBar": False},
            )

        with chart2:
            st.markdown("**Profit by Category**")

            fig_profit = px.bar(
                category_summary.sort_values("Profit", ascending=False),
                x="Category",
                y="Profit",
                text_auto=".3s",
                color_discrete_sequence=[GREEN],
            )

            fig_profit.update_traces(
                textposition="outside",
                cliponaxis=False,
            )

            fig_profit.update_layout(
                template="plotly_dark",
                paper_bgcolor=BG,
                plot_bgcolor=PANEL,
                font=dict(color=TEXT, size=11),
                margin=dict(l=10, r=10, t=15, b=10),
                height=270,
                showlegend=False,
                xaxis_title=None,
                yaxis_title=None,
            )

            st.plotly_chart(
                fig_profit,
                use_container_width=True,
                config={"displayModeBar": False},
            )

    if {"Region", "Sales", "Profit"}.issubset(database_df.columns):
        region_summary = (
            database_df.groupby("Region", as_index=False)
            .agg(
                Sales=("Sales", "sum"),
                Profit=("Profit", "sum"),
            )
            .sort_values("Sales", ascending=False)
        )

        with st.expander("Regional performance details"):
            st.dataframe(
                region_summary,
                use_container_width=True,
                hide_index=True,
            )


# =========================================================
# 11. GENERATED REPORTS
# =========================================================

st.markdown("")
st.markdown(
    '<div class="section-label">05 / GENERATED REPORTS</div>',
    unsafe_allow_html=True,
)

report_names = {
    "category_report.csv": "Category Report",
    "region_report.csv": "Regional Report",
    "loss_making_subcategories.csv": "Loss-Making Subcategories",
}

with st.expander(
    f"View and download reports ({len(report_files)} available)"
):
    if not report_files:
        st.info("No CSV reports found. Run the ETL pipeline first.")

    for report_path in report_files:
        st.markdown(
            f"**{report_names.get(report_path.name, report_path.name)}**"
        )

        try:
            report_df = pd.read_csv(report_path)

            st.dataframe(
                report_df,
                use_container_width=True,
                hide_index=True,
            )

            st.download_button(
                label=f"Download {report_path.name}",
                data=report_path.read_bytes(),
                file_name=report_path.name,
                mime="text/csv",
                key=f"download_{report_path.name}",
            )
        except Exception as error:
            st.error(f"Could not read {report_path.name}: {error}")


# =========================================================
# 12. EXECUTION OUTPUT AND LOGS
# =========================================================

st.markdown("")
st.markdown(
    '<div class="section-label">06 / SYSTEM LOGS</div>',
    unsafe_allow_html=True,
)

with st.expander("Last execution output"):
    output = st.session_state.get("last_run_output", "")

    if output:
        st.code(output, language="text")
    else:
        st.caption(
            "No execution output stored in this session. "
            "Run the pipeline to view its output."
        )

    error_output = st.session_state.get("last_run_error", "")

    if error_output:
        st.markdown("**Error output / diagnostic messages**")
        st.code(error_output.strip(), language="text")

with st.expander("View pipeline log file"):
    st.code(load_log(), language="text")

with st.expander("Inspect database records"):
    if database_ready:
        st.dataframe(
            database_df.head(100),
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.info("No loaded database records are available yet.")

footer_left, footer_right = st.columns(2)

with footer_left:
    st.caption("OBSIDIAN TERMINAL  /  RETAIL ETL MONITOR")

with footer_right:
    st.caption("PYTHON · PANDAS · SQLITE · STREAMLIT · PLOTLY")
