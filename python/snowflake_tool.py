from db import get_connection


def run_snowflake_query(sql: str):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(sql)
        rows = cursor.fetchall()
        return rows

    finally:
        cursor.close()
        conn.close()