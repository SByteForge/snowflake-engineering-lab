from agent_state import AgentState
from llm_client import call_llm


def insight_agent_node(state: AgentState):
    rows = state["sql_result"]

    if not rows:
        return {
            "insight": "No data was returned for this question."
        }

    # Handle errors returned by Data Agent
    if rows[0][0] == "ERROR":
        return {
            "insight": f"Data retrieval failed: {rows[0][1]}"
        }

    prompt = f"""
You are a support operations analyst.

User question:
{state["user_question"]}

These are verified query results returned from Snowflake:

{rows}

Rules:

- Base your answer only on the provided Snowflake results.
- Do not invent numbers, facts, causes, or business context that are not present in the results.
- Do not recalculate values unless necessary.
- Preserve the exact meaning and units of the metrics.
- RESOLUTION_TIME_HOURS values are measured in hours, not days.
- Clearly separate:
  1. Observed fact — what the data directly shows.
  2. Interpretation — what pattern can reasonably be inferred from the data.
  3. Recommendation — what practical next step should be considered.
- Do not claim a root cause unless the query results directly prove it.
- If the data is insufficient to determine the cause, explicitly say that further analysis is required.
- Any possible cause must be labeled as a hypothesis, not a fact.
- Recommendations should be proportional to the available evidence.
- Prefer recommending the next useful analysis when root cause is not established.
- Do not introduce external knowledge or assumptions.
- Keep the response concise and business-focused.

Use this response structure:

Observed:
<what the verified data directly shows>

Interpretation:
<the most important supported pattern>

Recommendation:
<a practical action or next analysis justified by the evidence>
"""

    insight = call_llm(prompt)

    return {
        "insight": insight
    }