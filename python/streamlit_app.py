import streamlit as st

from db import get_connection
from langgraph_flow import graph


st.set_page_config(
    page_title="Snowflake Agentic Intelligence Platform",
    page_icon="❄️",
    layout="wide",
)


st.title("❄️ Snowflake Agentic Intelligence Platform")

st.caption(
    "Governed analytics and agentic intelligence powered by "
    "Snowflake + LangGraph."
)


page = st.sidebar.radio(
    "Navigation",
    [
        "Ask the Agent",
        "Support Dashboard",
        "Data Health",
        "Architecture",
    ],
)


if page == "Ask the Agent":
    st.header("Ask the Agent")

    st.write(
        "Ask a natural-language question about customer support operations."
    )

    question = st.text_input(
        "Question",
        placeholder="Which support channels have the worst average resolution time?",
    )

    if st.button("Run Agent"):
        if not question.strip():
            st.warning("Enter a question first.")

        else:
            initial_state = {
                "user_question": question,
                "route": None,
                "sql_result": None,
                "insight": None,
                "final_answer": None,
            }

            try:
                with st.spinner("Running agent workflow..."):
                    result = graph.invoke(initial_state)

                st.subheader("Answer")

                st.success(
                    result.get(
                        "final_answer",
                        "The workflow completed but returned no final answer.",
                    )
                )

                with st.expander("Agent Trace"):
                    st.write("Route:", result.get("route"))

                    st.write(
                        "Snowflake Result:",
                        result.get("sql_result"),
                    )

                    st.write(
                        "Insight:",
                        result.get("insight"),
                    )

            except Exception as exc:
                st.error(f"Agent execution failed: {exc}")


elif page == "Support Dashboard":
    st.header("Support Operations Dashboard")

    st.info(
        "We will connect this page to Snowflake analytics in the next step."
    )


elif page == "Data Health":
    st.header("Data Health")

    st.info(
        "We will add RAW, CURATED and data-quality monitoring here."
    )


elif page == "Architecture":
    st.header("Platform Architecture")

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
Data Agent
  ↓
SQL Guard
  ↓
Snowflake
  ↓
Insight Agent
  ↓
Final Response
        """
    )