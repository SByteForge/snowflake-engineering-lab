from db import get_connection


def validate_snowflake_query(sql: str):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(f"EXPLAIN USING TEXT {sql}")
        return True, None

    except Exception as e:
        return False, str(e)

    finally:
        cursor.close()
        conn.close()


def run_snowflake_query(sql: str):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(sql)
        return cursor.fetchall()

    finally:
        cursor.close()
        conn.close()