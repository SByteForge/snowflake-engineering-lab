from agent_state import AgentState
from llm_client import call_llm


def insight_agent_node(state: AgentState):
    rows = state["sql_result"]

    if not rows:
        return {
            "insight": "No data was returned for this question."
        }

    # Handle errors returned by Data Agent
    if rows[0][0] == "ERROR":
        return {
            "insight": f"Data retrieval failed: {rows[0][1]}"
        }

    prompt = f"""
You are a support operations analyst.

User question:
{state["user_question"]}

These are verified query results returned from Snowflake:

{rows}

Rules:
- Do not invent numbers.
- Do not recalculate values unless necessary.
- Base your answer only on the provided results.
- Explain the most important pattern.
- Give one practical operational recommendation.
- Keep the response concise.
- RESOLUTION_TIME_HOURS values are measured in hours, not days.
"""

    insight = call_llm(prompt)

    return {
        "insight": insight
    }