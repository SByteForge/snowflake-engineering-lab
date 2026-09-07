from agent_state import AgentState


def final_response_node(state: AgentState):
    return {
        "final_answer": state["insight"]
    }