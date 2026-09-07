from langgraph.graph import StateGraph, START, END

from agent_state import AgentState
from supervisor_node import supervisor_node
from data_agent import data_agent_node
from insight_agent import insight_agent_node
from final_response import final_response_node


builder = StateGraph(AgentState)

builder.add_node("supervisor", supervisor_node)
builder.add_node("data_agent", data_agent_node)
builder.add_node("insight_agent", insight_agent_node)
builder.add_node("final_response", final_response_node)

builder.add_edge(START, "supervisor")


def route_from_supervisor(state: AgentState):
    return state["route"]


builder.add_conditional_edges(
    "supervisor",
    route_from_supervisor,
    {
        "data_agent": "data_agent",
        "final": END,
    },
)

builder.add_edge("data_agent", "insight_agent")
builder.add_edge("insight_agent", "final_response")
builder.add_edge("final_response", END)


graph = builder.compile()


if __name__ == "__main__":
    initial_state = {
        "user_question": "Which support channels have the worst average resolution time?",
        "route": None,
        "sql_result": None,
        "insight": None,
        "final_answer": None,
    }

    result = graph.invoke(initial_state)

    print(result)