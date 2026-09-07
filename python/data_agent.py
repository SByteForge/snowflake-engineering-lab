from agent_state import AgentState
from snowflake_tool import run_snowflake_query


def data_agent_node(state: AgentState):
    question = state["user_question"].lower()

    if "sla" in question or "risk" in question:
        sql = """
        SELECT
            SLA_RISK_LEVEL,
            COUNT(*) AS TICKET_COUNT
        FROM AI_ENGINEERING_LAB.ANALYTICS.SUPPORT_SLA_RISK
        GROUP BY SLA_RISK_LEVEL
        ORDER BY TICKET_COUNT DESC
        """
    else:
        sql = """
        SELECT
            ISSUE_CATEGORY,
            COUNT(*) AS TICKET_COUNT
        FROM AI_ENGINEERING_LAB.CURATED.CUSTOMER_SUPPORT_TICKETS
        GROUP BY ISSUE_CATEGORY
        ORDER BY TICKET_COUNT DESC
        LIMIT 10
        """

    result = run_snowflake_query(sql)

    return {
        "sql_result": result
    }