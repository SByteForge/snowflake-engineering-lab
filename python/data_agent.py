from agent_state import AgentState
from llm_client import call_llm
from sql_guard import validate_sql
from snowflake_tool import (
    run_snowflake_query,
    validate_snowflake_query,
)


def clean_sql(text: str) -> str:
    text = text.replace("```sql", "").replace("```", "").strip()

    start = text.upper().find("SELECT")

    if start == -1:
        return text

    sql = text[start:]

    semicolon = sql.find(";")

    if semicolon != -1:
        sql = sql[:semicolon + 1]

    return sql.strip()


def data_agent_node(state: AgentState):
    question = state["user_question"]

    prompt = f"""
You are a Snowflake analytics agent.

User question:

{question}

Use ONLY this table:

AI_ENGINEERING_LAB.CURATED.CUSTOMER_SUPPORT_TICKETS

Available columns:

TICKET_ID
CUSTOMER_NAME
CUSTOMER_EMAIL
TICKET_SUBJECT
TICKET_DESCRIPTION
ISSUE_CATEGORY
PRIORITY_LEVEL
TICKET_CHANNEL
SUBMISSION_DATE
RESOLUTION_TIME_HOURS
ASSIGNED_AGENT
SATISFACTION_SCORE

Generate exactly ONE SELECT query.

Rules:
- SQL only
- No explanation
- No markdown
- No joins
- Use only the columns above
- Use the fully qualified table name
- For "worst", sort the relevant metric descending
"""

    sql = clean_sql(call_llm(prompt))

    print("\nGenerated SQL:")
    print(sql)

    # Layer 1: deterministic safety validation
    if not validate_sql(sql):
        return {
            "sql_result": [
                ("ERROR", "Generated SQL failed safety validation")
            ]
        }

    # Layer 2: Snowflake compilation validation
    is_valid, error = validate_snowflake_query(sql)

    if not is_valid:
        repair_prompt = f"""
You are repairing a Snowflake SELECT query.

Original user question:

{question}

Generated SQL:

{sql}

Snowflake compilation error:

{error}

Fix the SQL.

Available tables and columns:

AI_ENGINEERING_LAB.CURATED.CUSTOMER_SUPPORT_TICKETS
- TICKET_ID
- CUSTOMER_NAME
- CUSTOMER_EMAIL
- TICKET_SUBJECT
- TICKET_DESCRIPTION
- ISSUE_CATEGORY
- PRIORITY_LEVEL
- TICKET_CHANNEL
- SUBMISSION_DATE
- RESOLUTION_TIME_HOURS
- ASSIGNED_AGENT
- SATISFACTION_SCORE

AI_ENGINEERING_LAB.ANALYTICS.SUPPORT_OPERATION_METRICS
- ISSUE_CATEGORY
- TICKET_CHANNEL
- PRIORITY_LEVEL
- TICKET_COUNT
- AVG_RESOLUTION_HOURS
- AVG_SATISFACTION_SCORE
- HIGH_PRIORITY_TICKETS

AI_ENGINEERING_LAB.ANALYTICS.SUPPORT_SLA_RISK
- TICKET_ID
- ISSUE_CATEGORY
- PRIORITY_LEVEL
- TICKET_CHANNEL
- RESOLUTION_TIME_HOURS
- SATISFACTION_SCORE
- SLA_RISK_LEVEL

Rules:
- Return SQL only.
- SELECT only.
- Do not use markdown.
- Do not invent columns.
- Avoid unnecessary joins.
- Prefer the simplest query.
- Use fully qualified table names.
"""

        repaired_sql = clean_sql(call_llm(repair_prompt))

        print("\nRepaired SQL:")
        print(repaired_sql)

        # Safety-check repaired SQL again
        if not validate_sql(repaired_sql):
            return {
                "sql_result": [
                    ("ERROR", "Repaired SQL failed safety validation")
                ]
            }

        # Compile-check repaired SQL again
        is_valid, error = validate_snowflake_query(repaired_sql)

        if not is_valid:
            return {
                "sql_result": [
                    ("ERROR", f"SQL repair failed: {error}")
                ]
            }

        sql = repaired_sql

    # Only execute once SQL passed both validation layers
    result = run_snowflake_query(sql)

    return {
        "sql_result": result
    }