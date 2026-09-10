from agent_state import AgentState
from llm_client import call_llm


ALLOWED_ROUTES = {
    "data_agent",
    "final",
}


DATA_KEYWORDS = {
    "ticket",
    "tickets",
    "category",
    "categories",
    "channel",
    "channels",
    "priority",
    "priorities",
    "resolution",
    "satisfaction",
    "agent",
    "agents",
    "sla",
    "risk",
    "average",
    "count",
    "highest",
    "lowest",
    "worst",
    "best",
    "metric",
    "metrics",
}


def supervisor_node(state: AgentState):
    question = state["user_question"]

    trace = state.get(
        "execution_trace",
        [],
    ).copy()

    question_lower = question.lower()

    # -----------------------------------------------------
    # 1. Deterministic routing for obvious analytics
    # -----------------------------------------------------

    if any(
        keyword in question_lower
        for keyword in DATA_KEYWORDS
    ):
        route = "data_agent"

        trace.append(
            "Supervisor selected route: data_agent "
            "(deterministic analytics routing)"
        )

        return {
            "route": route,
            "current_node": "supervisor",
            "execution_trace": trace,
        }

    # -----------------------------------------------------
    # 2. LLM routing for ambiguous requests
    # -----------------------------------------------------

    prompt = f"""
You are the routing supervisor for an enterprise
customer-support analytics platform.

Your ONLY responsibility is to select the next route.

User question:

{question}

Available routes:

data_agent
Use this whenever answering the question requires
looking at Snowflake data.

This includes questions involving:

- tickets
- issue categories
- support channels
- priorities
- assigned agents
- ticket counts
- resolution time
- satisfaction scores
- SLA metrics
- risk
- averages
- rankings
- comparisons
- highest / lowest
- best / worst
- trends or operational metrics

Examples:

"Which issue categories have the highest average resolution time?"
→ data_agent

"Which support channel has the lowest satisfaction?"
→ data_agent

"How many tickets are high priority?"
→ data_agent

"What is this application?"
→ final

Return ONLY:

data_agent

or

final
"""

    try:
        raw_route = call_llm(prompt)

        route = (
            raw_route
            .strip()
            .lower()
            .replace("`", "")
        )

        # Handle occasional extra model text
        if "data_agent" in route:
            route = "data_agent"
        elif "final" in route:
            route = "final"
        else:
            route = "data_agent"

    except Exception as exc:
        # For this analytics-focused application,
        # data_agent is the safer functional fallback.
        route = "data_agent"

        trace.append(
            f"Supervisor LLM routing failed: {exc}"
        )

    trace.append(
        f"Supervisor selected route: {route}"
    )

    return {
        "route": route,
        "current_node": "supervisor",
        "execution_trace": trace,
    }