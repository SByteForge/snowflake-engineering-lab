from typing import TypedDict, Optional, Any


class AgentState(TypedDict):
    user_question: str
    route: Optional[str]
    sql_result: Optional[Any]
    insight: Optional[str]
    final_answer: Optional[str]