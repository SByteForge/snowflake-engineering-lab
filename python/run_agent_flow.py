from supervisor_node import supervisor_node
from data_agent import data_agent_node
from insight_agent import insight_agent_node


state = {
    "user_question": "Which categories are at highest SLA risk?",
    "route": None,
    "sql_result": None,
    "insight": None,
    "final_answer": None
}


# 1. Supervisor decides where to route
supervisor_result = supervisor_node(state)
state.update(supervisor_result)

print("After supervisor:")
print(state)


# 2. Data Agent runs if selected
if state["route"] == "data_agent":
    data_result = data_agent_node(state)
    state.update(data_result)

print("\nAfter data agent:")
print(state)


# 3. Insight Agent interprets Snowflake result
insight_result = insight_agent_node(state)
state.update(insight_result)

print("\nFinal state:")
print(state)