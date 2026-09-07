from data_agent import data_agent_node

state = {
    "user_question": "Which categories are at highest SLA risk?",
    "route": "data_agent",
    "sql_result": None,
    "insight": None,
    "final_answer": None
}

result = data_agent_node(state)

print(result)