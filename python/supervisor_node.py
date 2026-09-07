from agent_state import AgentState
from llm_client import call_llm


def supervisor_node(state: AgentState):
    question = state["user_question"]

    prompt = f"""
You are a routing supervisor for a support analytics system.

User question:
{question}

Available routes:

1. data_agent
   Use when the question requires querying support data, SLA risk,
   ticket counts, categories, channels, agents, satisfaction,
   resolution time, or operational metrics.

2. final
   Use when the question does not require querying support data.

Return ONLY one value:

data_agent

or

final
"""

    route = call_llm(prompt).strip().lower()

    if route not in {"data_agent", "final"}:
        route = "final"

    return {
        "route": route
    }