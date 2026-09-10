import streamlit as st
import pandas as pd

from db import get_connection, get_config
from langgraph_flow import graph


# =========================================================
# Page Configuration
# =========================================================

st.set_page_config(
    page_title="Snowflake Agentic Intelligence Platform",
    page_icon="❄️",
    layout="wide",
    initial_sidebar_state="expanded",
)


# =========================================================
# Styling
# =========================================================

st.markdown(
    """
    <style>

    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1500px;
    }

    .platform-title {
        font-size: 2.2rem;
        font-weight: 700;
        margin-bottom: 0.2rem;
    }

    .platform-subtitle {
        color: #6b7280;
        font-size: 1rem;
        margin-bottom: 1rem;
    }

    .section-title {
        font-size: 1.45rem;
        font-weight: 650;
        margin-top: 0.5rem;
        margin-bottom: 0.4rem;
    }

    .trace-item {
        border-left: 3px solid #9ca3af;
        padding: 0.45rem 0.9rem;
        margin-bottom: 0.5rem;
    }

    .small-muted {
        color: #6b7280;
        font-size: 0.9rem;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# Platform Configuration Check
# =========================================================

def check_platform_config():
    missing = []

    required = [
        "SNOWFLAKE_USER",
        "SNOWFLAKE_PASSWORD",
        "SNOWFLAKE_ACCOUNT",
        "GROQ_API_KEY",
    ]

    for name in required:
        if not get_config(name):
            missing.append(name)

    return missing


missing_config = check_platform_config()

if missing_config:
    st.error("Platform configuration is incomplete.")

    st.write(
        "Missing configuration:",
        ", ".join(missing_config),
    )

    st.info(
        "Configure these values in your local .env file "
        "or in Streamlit Cloud Secrets."
    )

    st.stop()


# =========================================================
# Sidebar
# =========================================================

with st.sidebar:
    st.markdown("## ❄️ Snowflake AI Platform")

    st.caption(
        "Governed Data + Agentic Intelligence"
    )

    st.markdown("---")

    page = st.radio(
        "Navigation",
        [
            "Ask the Agent",
            "Orchestrator",
            "Support Dashboard",
            "Data Health",
            "Architecture",
        ],
    )

    st.markdown("---")

    st.caption("Platform Stack")

    st.markdown(
        """
**Snowflake**  
Data & Analytics

**LangGraph**  
Agent Orchestration

**Groq**  
Hosted LLM Runtime

**Terraform**  
Infrastructure as Code

**Streamlit**  
Application Interface
"""
    )


# =========================================================
# Header
# =========================================================

st.markdown(
    """
    <div class="platform-title">
        Snowflake Agentic Intelligence Platform
    </div>

    <div class="platform-subtitle">
        Governed enterprise analytics with observable
        LangGraph orchestration and Snowflake-backed intelligence.
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown("---")


# =========================================================
# Snowflake Helpers
# =========================================================

def run_query(sql: str):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(sql)
        return cursor.fetchall()

    finally:
        cursor.close()
        conn.close()


def get_scalar(sql: str):
    rows = run_query(sql)

    if not rows:
        return None

    return rows[0][0]


# =========================================================
# Ask the Agent
# =========================================================

if page == "Ask the Agent":
    st.markdown(
        '<div class="section-title">'
        'Natural Language Analytics'
        '</div>',
        unsafe_allow_html=True,
    )

    st.write(
        "Ask analytical questions directly against governed Snowflake data."
    )

    question = st.text_input(
        "Question",
        placeholder=(
            "Which support channels have the worst "
            "average resolution time?"
        ),
        label_visibility="collapsed",
    )

    run_clicked = st.button(
        "Run Analysis",
        type="primary",
    )

    if run_clicked:
        if not question.strip():
            st.warning(
                "Please enter a question."
            )

        else:
            initial_state = {
                "user_question": question,

                "route": None,

                "generated_sql": None,
                "sql_validation_status": None,
                "sql_error": None,

                "sql_result": None,

                "insight": None,
                "final_answer": None,

                "current_node": None,
                "execution_trace": [],
            }

            try:
                with st.spinner(
                    "Running LangGraph agent workflow..."
                ):
                    result = graph.invoke(
                        initial_state
                    )

                st.session_state[
                    "latest_agent_result"
                ] = result

                st.session_state[
                    "latest_question"
                ] = question

                st.markdown(
                    "### Analysis Result"
                )

                final_answer = result.get(
                    "final_answer"
                )

                if final_answer:
                    st.markdown(
                        final_answer
                    )

                    st.success(
                        "Agent workflow completed successfully."
                    )

                else:
                    st.warning(
                        "The workflow completed but no final answer was generated."
                    )

                with st.expander(
                    "Technical Execution Trace"
                ):
                    st.write(
                        "Route:",
                        result.get("route"),
                    )

                    st.write(
                        "SQL Validation:",
                        result.get(
                            "sql_validation_status"
                        ),
                    )

                    st.markdown(
                        "#### Generated SQL"
                    )

                    st.code(
                        result.get(
                            "generated_sql"
                        )
                        or "No SQL generated",
                        language="sql",
                    )

                    st.markdown(
                        "#### Snowflake Result"
                    )

                    st.write(
                        result.get(
                            "sql_result"
                        )
                    )

                    st.markdown(
                        "#### Insight"
                    )

                    st.write(
                        result.get(
                            "insight"
                        )
                    )

            except Exception as exc:
                st.error(
                    "The agent workflow could not complete."
                )

                with st.expander(
                    "Error Details"
                ):
                    st.exception(exc)


# =========================================================
# LangGraph Orchestrator
# =========================================================

elif page == "Orchestrator":
    st.markdown(
        '<div class="section-title">'
        'LangGraph Orchestrator'
        '</div>',
        unsafe_allow_html=True,
    )

    st.write(
        "Inspect how the latest request moved through "
        "routing, SQL generation, validation, tools, "
        "Snowflake, and insight generation."
    )

    result = st.session_state.get(
        "latest_agent_result"
    )

    if not result:
        st.info(
            "Run a request from 'Ask the Agent' first."
        )

    else:
        sql_rows = result.get(
            "sql_result"
        )

        if isinstance(
            sql_rows,
            list,
        ):
            row_count = len(sql_rows)
        else:
            row_count = 0

        # -------------------------------------------------
        # Runtime Summary
        # -------------------------------------------------

        c1, c2, c3, c4 = st.columns(4)

        c1.metric(
            "Selected Route",
            result.get("route")
            or "N/A",
        )

        c2.metric(
            "SQL Validation",
            result.get(
                "sql_validation_status"
            )
            or "N/A",
        )

        c3.metric(
            "Rows Returned",
            row_count,
        )

        c4.metric(
            "Final Node",
            result.get(
                "current_node"
            )
            or "N/A",
        )

        st.markdown("---")

        # -------------------------------------------------
        # Execution Path
        # -------------------------------------------------

        st.markdown(
            "### Execution Path"
        )

        route = result.get(
            "route"
        )

        validation = result.get(
            "sql_validation_status"
        )

        flow = [
            "👤 User Request",
            "🧭 Supervisor Agent",
            f"🔀 Route → {route or 'N/A'}",
        ]

        if route == "data_agent":
            flow.extend(
                [
                    "🧠 Data Agent",
                    "📝 Text-to-SQL Generation",
                    "🛡️ SQL Policy Guard",
                    f"❄️ Snowflake Validation → {validation or 'N/A'}",
                    "🔧 Snowflake Query Tool",
                    "📊 Verified Query Result",
                    "🧠 Insight Agent",
                    "✅ Final Response",
                ]
            )

        else:
            flow.append(
                "✅ Final Response"
            )

        for item in flow:
            st.markdown(
                f"""
                <div class="trace-item">
                    {item}
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.markdown("---")

        # -------------------------------------------------
        # Actual Trace
        # -------------------------------------------------

        st.markdown(
            "### Actual Runtime Trace"
        )

        trace = result.get(
            "execution_trace",
            [],
        )

        if trace:
            for index, event in enumerate(
                trace,
                start=1,
            ):
                st.write(
                    f"**{index}.** ✅ {event}"
                )

        else:
            st.info(
                "No execution trace was recorded."
            )

        st.markdown("---")

        # -------------------------------------------------
        # SQL + Validation
        # -------------------------------------------------

        col_left, col_right = st.columns(
            [3, 2]
        )

        with col_left:
            st.markdown(
                "### Generated SQL"
            )

            sql = result.get(
                "generated_sql"
            )

            if sql:
                st.code(
                    sql,
                    language="sql",
                )

            else:
                st.info(
                    "No SQL was generated for this execution."
                )

        with col_right:
            st.markdown(
                "### Validation"
            )

            validation_status = (
                result.get(
                    "sql_validation_status"
                )
            )

            if validation_status == "PASSED":
                st.success(
                    "SQL validation passed."
                )

            elif validation_status:
                st.warning(
                    validation_status
                )

            else:
                st.info(
                    "No SQL validation was required."
                )

            error = result.get(
                "sql_error"
            )

            if error:
                st.error(
                    error
                )

        st.markdown("---")

        # -------------------------------------------------
        # Raw Output / Insight
        # -------------------------------------------------

        with st.expander(
            "Snowflake Query Result"
        ):
            st.write(
                result.get(
                    "sql_result"
                )
            )

        with st.expander(
            "Insight Agent Output"
        ):
            st.markdown(
                result.get(
                    "insight"
                )
                or "No insight generated."
            )

        with st.expander(
            "Complete AgentState"
        ):
            st.json(
                {
                    key: str(value)
                    for key, value
                    in result.items()
                }
            )


# =========================================================
# Support Dashboard
# =========================================================

elif page == "Support Dashboard":
    st.markdown(
        '<div class="section-title">'
        'Support Operations Dashboard'
        '</div>',
        unsafe_allow_html=True,
    )

    st.write(
        "Operational KPIs calculated directly inside Snowflake."
    )

    try:
        total_tickets = get_scalar(
            """
            SELECT COUNT(*)
            FROM AI_ENGINEERING_LAB.CURATED.CUSTOMER_SUPPORT_TICKETS
            """
        )

        avg_resolution = get_scalar(
            """
            SELECT AVG(RESOLUTION_TIME_HOURS)
            FROM AI_ENGINEERING_LAB.CURATED.CUSTOMER_SUPPORT_TICKETS
            """
        )

        avg_satisfaction = get_scalar(
            """
            SELECT AVG(SATISFACTION_SCORE)
            FROM AI_ENGINEERING_LAB.CURATED.CUSTOMER_SUPPORT_TICKETS
            """
        )

        high_risk = get_scalar(
            """
            SELECT COUNT(*)
            FROM AI_ENGINEERING_LAB.ANALYTICS.SUPPORT_SLA_RISK
            WHERE SLA_RISK_LEVEL = 'HIGH_RISK'
            """
        )

        k1, k2, k3, k4 = st.columns(4)

        k1.metric(
            "Total Tickets",
            f"{total_tickets:,}"
            if total_tickets is not None
            else "N/A",
        )

        k2.metric(
            "Avg Resolution",
            f"{float(avg_resolution):.2f} h"
            if avg_resolution is not None
            else "N/A",
        )

        k3.metric(
            "Avg Satisfaction",
            f"{float(avg_satisfaction):.2f}"
            if avg_satisfaction is not None
            else "N/A",
        )

        k4.metric(
            "High Risk Tickets",
            f"{high_risk:,}"
            if high_risk is not None
            else "N/A",
        )

        st.markdown("---")

        # -------------------------------------------------
        # Channel Performance
        # -------------------------------------------------

        channel_rows = run_query(
            """
            SELECT
                TICKET_CHANNEL,
                COUNT(*) AS TICKET_COUNT,
                AVG(RESOLUTION_TIME_HOURS) AS AVG_RESOLUTION_HOURS,
                AVG(SATISFACTION_SCORE) AS AVG_SATISFACTION
            FROM AI_ENGINEERING_LAB.CURATED.CUSTOMER_SUPPORT_TICKETS
            GROUP BY TICKET_CHANNEL
            ORDER BY AVG_RESOLUTION_HOURS DESC
            """
        )

        df_channels = pd.DataFrame(
            channel_rows,
            columns=[
                "Channel",
                "Ticket Count",
                "Avg Resolution Hours",
                "Avg Satisfaction",
            ],
        )

        left, right = st.columns(
            [3, 2]
        )

        with left:
            st.markdown(
                "### Channel Performance"
            )

            st.dataframe(
                df_channels,
                use_container_width=True,
                hide_index=True,
            )

        with right:
            st.markdown(
                "### Resolution Time"
            )

            st.bar_chart(
                df_channels.set_index(
                    "Channel"
                )[
                    "Avg Resolution Hours"
                ]
            )

        st.markdown("---")

        # -------------------------------------------------
        # SLA Risk
        # -------------------------------------------------

        risk_rows = run_query(
            """
            SELECT
                SLA_RISK_LEVEL,
                COUNT(*) AS TICKET_COUNT
            FROM AI_ENGINEERING_LAB.ANALYTICS.SUPPORT_SLA_RISK
            GROUP BY SLA_RISK_LEVEL
            ORDER BY TICKET_COUNT DESC
            """
        )

        risk_df = pd.DataFrame(
            risk_rows,
            columns=[
                "Risk Level",
                "Ticket Count",
            ],
        )

        st.markdown(
            "### SLA Risk Distribution"
        )

        st.bar_chart(
            risk_df.set_index(
                "Risk Level"
            )[
                "Ticket Count"
            ]
        )

    except Exception as exc:
        st.error(
            "Unable to load Snowflake dashboard."
        )

        with st.expander(
            "Error Details"
        ):
            st.exception(exc)


# =========================================================
# Data Health
# =========================================================

elif page == "Data Health":
    st.markdown(
        '<div class="section-title">'
        'Data Platform Health'
        '</div>',
        unsafe_allow_html=True,
    )

    st.write(
        "Quality and consistency checks across Snowflake data layers."
    )

    try:
        raw_count = get_scalar(
            """
            SELECT COUNT(*)
            FROM AI_ENGINEERING_LAB.RAW.CUSTOMER_SUPPORT_TICKETS
            """
        )

        curated_count = get_scalar(
            """
            SELECT COUNT(*)
            FROM AI_ENGINEERING_LAB.CURATED.CUSTOMER_SUPPORT_TICKETS
            """
        )

        duplicate_count = get_scalar(
            """
            SELECT COUNT(*)
            FROM (
                SELECT TICKET_ID
                FROM AI_ENGINEERING_LAB.CURATED.CUSTOMER_SUPPORT_TICKETS
                GROUP BY TICKET_ID
                HAVING COUNT(*) > 1
            )
            """
        )

        invalid_resolution = get_scalar(
            """
            SELECT COUNT(*)
            FROM AI_ENGINEERING_LAB.CURATED.CUSTOMER_SUPPORT_TICKETS
            WHERE RESOLUTION_TIME_HOURS < 0
            """
        )

        h1, h2, h3, h4 = st.columns(4)

        h1.metric(
            "RAW Records",
            f"{raw_count:,}"
            if raw_count is not None
            else "N/A",
        )

        h2.metric(
            "CURATED Records",
            f"{curated_count:,}"
            if curated_count is not None
            else "N/A",
        )

        h3.metric(
            "Duplicate IDs",
            f"{duplicate_count:,}"
            if duplicate_count is not None
            else "N/A",
        )

        h4.metric(
            "Invalid Resolution",
            f"{invalid_resolution:,}"
            if invalid_resolution is not None
            else "N/A",
        )

        st.markdown("---")

        if (
            raw_count == curated_count
            and duplicate_count == 0
            and invalid_resolution == 0
        ):
            st.success(
                "All monitored data-quality checks are healthy."
            )

        else:
            st.warning(
                "One or more data-quality checks require attention."
            )

        st.markdown(
            "### Data Pipeline"
        )

        st.code(
            """
Source
  ↓
Snowflake Internal Stage
  ↓
RAW
  ↓
Data Quality
  ↓
CURATED
  ↓
ANALYTICS
  ↓
Agent Consumption
            """
        )

    except Exception as exc:
        st.error(
            "Unable to retrieve data-health metrics."
        )

        with st.expander(
            "Error Details"
        ):
            st.exception(exc)


# =========================================================
# Architecture
# =========================================================

elif page == "Architecture":
    st.markdown(
        '<div class="section-title">'
        'Platform Architecture'
        '</div>',
        unsafe_allow_html=True,
    )

    st.write(
        "The platform separates application experience, "
        "agent orchestration, execution, data, and infrastructure."
    )

    a1, a2 = st.columns(2)

    with a1:
        st.markdown(
            "### Agent Runtime"
        )

        st.code(
            """
User
 ↓
Streamlit
 ↓
LangGraph Runtime
 ↓
Supervisor
 ↓
Conditional Edge
 ↓
Data Agent
 ↓
Groq-hosted LLM
 ↓
SQL Guard
 ↓
Snowflake EXPLAIN
 ↓
Snowflake Query Tool
 ↓
Insight Agent
 ↓
Final Response
            """
        )

    with a2:
        st.markdown(
            "### Data Platform"
        )

        st.code(
            """
Source
 ↓
Python Ingestion
 ↓
Snowflake Stage
 ↓
RAW
 ↓
Data Quality
 ↓
CURATED
 ↓
ANALYTICS
 ↓
AI Consumers
            """
        )

    st.markdown(
        "### Infrastructure Delivery"
    )

    st.code(
        """
Developer
 ↓
GitHub
 ↓
GitHub Actions
 ↓
OIDC
 ↓
GCP Workload Identity Federation
 ↓
GCS Terraform State
 ↓
Terraform
 ↓
Snowflake Infrastructure
        """
    )