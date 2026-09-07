ALLOWED_TABLES = {
    "AI_ENGINEERING_LAB.CURATED.CUSTOMER_SUPPORT_TICKETS",
    "AI_ENGINEERING_LAB.ANALYTICS.SUPPORT_OPERATION_METRICS",
    "AI_ENGINEERING_LAB.ANALYTICS.SUPPORT_SLA_RISK",
}


def validate_sql(sql: str) -> bool:
    normalized = sql.strip().upper()

    if not normalized.startswith("SELECT"):
        return False

    forbidden = [
        "INSERT",
        "UPDATE",
        "DELETE",
        "DROP",
        "ALTER",
        "TRUNCATE",
        "CREATE",
        "MERGE",
    ]

    if any(keyword in normalized for keyword in forbidden):
        return False

    if not any(table in normalized for table in ALLOWED_TABLES):
        return False

    return True