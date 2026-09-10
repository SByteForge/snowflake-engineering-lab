from agent_state import AgentState


def final_response_node(state: AgentState):

    trace = state.get(
        "execution_trace",
        [],
    ).copy()

    insight = state.get("insight")

    if insight:
        final_answer = insight
    else:
        final_answer = (
            "This request did not require a Snowflake analytical query."
        )

    trace.append(
        "Final response generated"
    )

    return {
        "final_answer": final_answer,
        "current_node": "final_response",
        "execution_trace": trace,
    }