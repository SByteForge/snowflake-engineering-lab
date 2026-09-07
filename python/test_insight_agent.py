from insight_agent import insight_agent_node

state = {
    "user_question": "Which categories are at highest SLA risk?",
    "route": "data_agent",
    "sql_result": [
        ("LOW_RISK", 12447),
        ("MEDIUM_RISK", 5795),
        ("HIGH_RISK", 1758)
    ],
    "insight": None,
    "final_answer": None
}

result = insight_agent_node(state)

print(result)