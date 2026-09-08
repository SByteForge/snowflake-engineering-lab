from agent_state import AgentState


def final_response_node(
    state: AgentState,
):
    """
    Convert internal insight into the user-facing response.
    """

    trace = state.get(
        "execution_trace",
        [],
    ).copy()

    final_answer = state.get(
        "insight"
    )

    if not final_answer:
        final_answer = (
            "The workflow completed but no final insight was generated."
        )

    trace.append(
        "Final response generated"
    )

    return {
        "final_answer": final_answer,
        "current_node": "final_response",
        "execution_trace": trace,
    }