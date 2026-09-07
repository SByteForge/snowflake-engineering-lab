from supervisor_node import supervisor_node

state = {
    "user_question": "Which categories are at highest SLA risk?",
    "route": None,
    "sql_result": None,
    "insight": None,
    "final_answer": None
}

result = supervisor_node(state)

print(result)