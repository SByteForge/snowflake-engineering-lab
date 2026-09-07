from agent_state import AgentState


def supervisor_node(state: AgentState):
    question = state["user_question"].lower()

    if "sla" in question or "risk" in question:
        route = "data_agent"
    else:
        route = "final"

    return {
        "route": route
    }