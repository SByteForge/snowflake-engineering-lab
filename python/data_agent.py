from agent_state import AgentState
from llm_client import call_llm
from sql_guard import validate_sql
from snowflake_tool import (
    validate_snowflake_query,
    run_snowflake_query,
)


def clean_sql(text: str) -> str:
    """
    Extract a single SQL SELECT statement from LLM output.
    """

    text = (
        text
        .replace("```sql", "")
        .replace("```SQL", "")
        .replace("```", "")
        .strip()
    )

    start = text.upper().find("SELECT")

    if start == -1:
        return text.strip()

    sql = text[start:]

    semicolon = sql.find(";")

    if semicolon != -1:
        sql = sql[: semicolon + 1]

    return sql.strip()


def generate_sql(question: str) -> str:
    """
    Generate constrained Snowflake SQL from a natural-language question.
    """

    prompt = f"""
You are a Snowflake analytics agent.

Your responsibility is to convert the user's analytical question
into exactly one safe Snowflake SELECT query.

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

Rules:

- Return SQL only.
- Do not return explanations.
- Do not return markdown.
- Generate exactly one SELECT query.
- Never use INSERT, UPDATE, DELETE, DROP, ALTER, CREATE, MERGE, or TRUNCATE.
- Use only the table and columns listed above.
- Always use the fully qualified table name.
- Avoid joins.
- Prefer the simplest query that answers the question.
- Perform calculations and aggregations inside Snowflake.
- RESOLUTION_TIME_HOURS is measured in hours.
- If the user asks for the "worst" resolution time, higher values are worse,
  therefore sort the relevant resolution metric descending.
"""

    raw_output = call_llm(prompt)

    return clean_sql(raw_output)


def repair_sql(
    question: str,
    sql: str,
    error: str,
) -> str:
    """
    Allow exactly one controlled LLM repair attempt.
    """

    prompt = f"""
You are repairing a Snowflake SELECT query.

Original user question:

{question}

Original SQL:

{sql}

Snowflake compilation error:

{error}

Allowed table:

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

Rules:

- Return SQL only.
- Generate exactly one SELECT query.
- Do not return markdown.
- Do not return explanations.
- Do not invent columns.
- Do not use joins.
- Use only the allowed table.
- Use the fully qualified table name.
- Preserve the original business question.
- Prefer the simplest valid query.
"""

    repaired_output = call_llm(prompt)

    return clean_sql(repaired_output)


def data_agent_node(state: AgentState):
    """
    Convert the user question into governed Snowflake SQL,
    validate it, optionally repair it once, execute it,
    and return verified query results.
    """

    question = state["user_question"]

    trace = state.get("execution_trace", []).copy()

    # ---------------------------------------------------------
    # 1. Generate SQL
    # ---------------------------------------------------------

    try:
        generated_sql = generate_sql(question)

    except Exception as exc:
        trace.append(
            f"Data Agent SQL generation failed: {exc}"
        )

        return {
            "generated_sql": None,
            "sql_validation_status": "GENERATION_FAILED",
            "sql_error": str(exc),
            "sql_result": [
                (
                    "ERROR",
                    f"SQL generation failed: {exc}",
                )
            ],
            "current_node": "data_agent",
            "execution_trace": trace,
        }

    print("Generated SQL:")
    print(generated_sql)

    trace.append("Data Agent generated SQL")

    # ---------------------------------------------------------
    # 2. Application SQL Policy Guard
    # ---------------------------------------------------------

    if not validate_sql(generated_sql):

        trace.append(
            "SQL Guard rejected generated query"
        )

        return {
            "generated_sql": generated_sql,
            "sql_validation_status": "FAILED_POLICY",
            "sql_error": (
                "Generated SQL failed application safety validation."
            ),
            "sql_result": [
                (
                    "ERROR",
                    "Generated SQL failed application safety validation.",
                )
            ],
            "current_node": "data_agent",
            "execution_trace": trace,
        }

    trace.append("SQL Guard passed")

    # ---------------------------------------------------------
    # 3. Snowflake Compilation Validation
    # ---------------------------------------------------------

    is_valid, validation_error = (
        validate_snowflake_query(generated_sql)
    )

    # ---------------------------------------------------------
    # 4. One Bounded Repair Attempt
    # ---------------------------------------------------------

    if not is_valid:

        trace.append(
            "Snowflake EXPLAIN validation failed"
        )

        trace.append(
            "Bounded SQL repair attempted"
        )

        try:
            repaired_sql = repair_sql(
                question=question,
                sql=generated_sql,
                error=validation_error or "Unknown Snowflake error",
            )

        except Exception as exc:

            trace.append(
                f"SQL repair failed: {exc}"
            )

            return {
                "generated_sql": generated_sql,
                "sql_validation_status": "REPAIR_FAILED",
                "sql_error": str(exc),
                "sql_result": [
                    (
                        "ERROR",
                        f"SQL repair failed: {exc}",
                    )
                ],
                "current_node": "data_agent",
                "execution_trace": trace,
            }

        # Treat repaired SQL as new untrusted SQL
        generated_sql = repaired_sql

        trace.append(
            "Data Agent generated repaired SQL"
        )

        # Re-run application safety guard
        if not validate_sql(generated_sql):

            trace.append(
                "SQL Guard rejected repaired query"
            )

            return {
                "generated_sql": generated_sql,
                "sql_validation_status": "REPAIR_POLICY_FAILED",
                "sql_error": (
                    "Repaired SQL failed application safety validation."
                ),
                "sql_result": [
                    (
                        "ERROR",
                        "Repaired SQL failed application safety validation.",
                    )
                ],
                "current_node": "data_agent",
                "execution_trace": trace,
            }

        trace.append(
            "Repaired SQL passed SQL Guard"
        )

        # Re-run Snowflake compilation validation
        is_valid, validation_error = (
            validate_snowflake_query(generated_sql)
        )

        if not is_valid:

            trace.append(
                "Repaired SQL failed Snowflake EXPLAIN validation"
            )

            return {
                "generated_sql": generated_sql,
                "sql_validation_status": "REPAIR_VALIDATION_FAILED",
                "sql_error": validation_error,
                "sql_result": [
                    (
                        "ERROR",
                        validation_error
                        or "Repaired SQL failed Snowflake validation.",
                    )
                ],
                "current_node": "data_agent",
                "execution_trace": trace,
            }

        trace.append(
            "Repaired SQL passed Snowflake EXPLAIN validation"
        )

    else:

        trace.append(
            "Snowflake EXPLAIN validation passed"
        )

    # ---------------------------------------------------------
    # 5. Execute Verified Query
    # ---------------------------------------------------------

    try:
        result = run_snowflake_query(
            generated_sql
        )

    except Exception as exc:

        trace.append(
            f"Snowflake query execution failed: {exc}"
        )

        return {
            "generated_sql": generated_sql,
            "sql_validation_status": "EXECUTION_FAILED",
            "sql_error": str(exc),
            "sql_result": [
                (
                    "ERROR",
                    f"Snowflake query execution failed: {exc}",
                )
            ],
            "current_node": "data_agent",
            "execution_trace": trace,
        }

    trace.append(
        f"Snowflake query executed successfully: "
        f"{len(result)} rows returned"
    )

    return {
        "generated_sql": generated_sql,
        "sql_validation_status": "PASSED",
        "sql_error": None,
        "sql_result": result,
        "current_node": "data_agent",
        "execution_trace": trace,
    }