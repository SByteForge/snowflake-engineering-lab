import streamlit as st
import pandas as pd

from db import get_connection
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

    .architecture-card {
        border: 1px solid #e5e7eb;
        border-radius: 12px;
        padding: 1rem;
        margin-bottom: 1rem;
    }

    .trace-item {
        border-left: 3px solid #9ca3af;
        padding: 0.45rem 0.9rem;
        margin-bottom: 0.5rem;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# Sidebar
# =========================================================

with st.sidebar:

    st.markdown(
        "## ❄️ Snowflake AI Platform"
    )

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
        LangGraph agent orchestration.
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

                # Save result between Streamlit pages
                st.session_state[
                    "latest_agent_result"
                ] = result

                st.session_state[
                    "latest_question"
                ] = question

                st.markdown(
                    "### Analysis Result"
                )

                st.markdown(
                    result.get(
                        "final_answer",
                        "No response generated.",
                    )
                )

                st.success(
                    "Agent workflow completed successfully."
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

                    st.code(
                        result.get(
                            "generated_sql"
                        )
                        or "No SQL generated",
                        language="sql",
                    )

                    st.write(
                        "Snowflake Result:"
                    )

                    st.write(
                        result.get("sql_result")
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
        "agents, validation layers, tools, and Snowflake."
    )

    result = st.session_state.get(
        "latest_agent_result"
    )

    if not result:

        st.info(
            "Run a request from 'Ask the Agent' first."
        )

    else:

        # -------------------------------------------------
        # Runtime Summary
        # -------------------------------------------------

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
        # Runtime Flow
        # -------------------------------------------------

        st.markdown(
            "### Execution Path"
        )

        flow = [
            "👤 User Request",
            "🧭 Supervisor Agent",
            f"🔀 Route → {result.get('route')}",
            "🧠 Data Agent",
            "📝 Text-to-SQL Generation",
            "🛡️ SQL Policy Guard",
            "❄️ Snowflake EXPLAIN Validation",
            "🔧 Snowflake Query Tool",
            "📊 Verified Query Result",
            "🧠 Insight Agent",
            "✅ Final Response",
        ]

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
        # Actual Execution Trace
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
        # Generated SQL
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
                    "No SQL was generated."
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

            error = result.get(
                "sql_error"
            )

            if error:

                st.error(error)

        # -------------------------------------------------
        # Data + Insight
        # -------------------------------------------------

        st.markdown("---")

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
            f"{total_tickets:,}",
        )

        k2.metric(
            "Avg Resolution",
            f"{float(avg_resolution):.2f} h",
        )

        k3.metric(
            "Avg Satisfaction",
            f"{float(avg_satisfaction):.2f}",
        )

        k4.metric(
            "High Risk Tickets",
            f"{high_risk:,}",
        )

        st.markdown("---")

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
                SELECT
                    TICKET_ID
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
            f"{raw_count:,}",
        )

        h2.metric(
            "CURATED Records",
            f"{curated_count:,}",
        )

        h3.metric(
            "Duplicate IDs",
            f"{duplicate_count:,}",
        )

        h4.metric(
            "Invalid Resolution",
            f"{invalid_resolution:,}",
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
        "The architecture separates application experience, "
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
LangGraph
 ↓
Supervisor
 ↓
Conditional Edge
 ↓
Data Agent
 ↓
Groq LLM
 ↓
SQL Guard
 ↓
Snowflake EXPLAIN
 ↓
Snowflake Tool
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
Kaggle / Source
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