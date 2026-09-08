from typing import TypedDict, Optional, Any, List


class AgentState(TypedDict):
    user_question: str
    route: Optional[str]

    generated_sql: Optional[str]
    sql_validation_status: Optional[str]
    sql_error: Optional[str]

    sql_result: Optional[Any]

    insight: Optional[str]
    final_answer: Optional[str]

    current_node: Optional[str]
    execution_trace: List[str]