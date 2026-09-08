from agent_state import AgentState
from llm_client import call_llm


ALLOWED_ROUTES = {
    "data_agent",
    "final",
}


def supervisor_node(state: AgentState):
    """
    Decide which path the LangGraph workflow should take.
    """

    question = state["user_question"]

    prompt = f"""
You are the supervisor agent for an enterprise support analytics platform.

Your responsibility is ONLY to decide which route should handle the request.

User question:

{question}

Available routes:

data_agent
- Use when answering the question requires querying Snowflake data.
- Examples include tickets, SLA risk, channels, issue categories,
  resolution time, satisfaction, priority, workload, or support metrics.

final
- Use when the request does not require querying enterprise support data.

Return ONLY one value:

data_agent

or

final
"""

    try:
        route = call_llm(prompt).strip().lower()

    except Exception as exc:
        # Safe deterministic fallback
        route = "final"

        trace = state.get("execution_trace", []) + [
            f"Supervisor LLM failed; fallback route selected: final ({exc})"
        ]

        return {
            "route": route,
            "current_node": "supervisor",
            "execution_trace": trace,
        }

    if route not in ALLOWED_ROUTES:
        route = "final"

    trace = state.get("execution_trace", []) + [
        f"Supervisor selected route: {route}"
    ]

    return {
        "route": route,
        "current_node": "supervisor",
        "execution_trace": trace,
    }