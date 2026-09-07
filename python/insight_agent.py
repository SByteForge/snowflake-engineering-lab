from agent_state import AgentState
from llm_client import call_llm


def insight_agent_node(state: AgentState):
    rows = state["sql_result"]

    total = sum(count for _, count in rows)

    formatted_rows = []
    for risk_level, count in rows:
        percentage = round((count / total) * 100, 2)
        formatted_rows.append(
            f"{risk_level}: {count} tickets ({percentage}%)"
        )

    facts = "\n".join(formatted_rows)

    prompt = f"""
You are a support operations analyst.

These are verified facts calculated by Python:

{facts}

Important:
- Do not recalculate totals.
- Do not change the numbers.
- Treat HIGH_RISK as highest severity even if it has fewer tickets.

Explain:
1. What this distribution means
2. What needs operational attention
3. One practical recommendation

Keep the answer concise.
"""

    insight = call_llm(prompt)

    return {
        "insight": insight
    }