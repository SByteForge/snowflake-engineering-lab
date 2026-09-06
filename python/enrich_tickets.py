import json
import requests
from db import get_connection

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "mistral:latest"


def get_tickets(conn):
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            TICKET_ID,
            SUBJECT,
            MESSAGE
        FROM RAW.SUPPORT_TICKETS
        ORDER BY TICKET_ID
    """)

    return cursor.fetchall()


def enrich_with_ollama(subject, message):
    prompt = f"""
You are a customer support analyst.

Analyze this support ticket.

Subject: {subject}
Message: {message}

Return ONLY valid JSON in this format:

{{
    "category": "Billing|Authentication|Performance|Feature Request|Other",
    "urgency": "Low|Medium|High",
    "sentiment": "Positive|Neutral|Negative",
    "summary": "short summary"
}}
"""

    response = requests.post(
        OLLAMA_URL,
        json={
            "model": MODEL,
            "prompt": prompt,
            "stream": False
        },
        timeout=60
    )

    response.raise_for_status()

    result = response.json()["response"]

    return json.loads(result)


def save_result(conn, ticket_id, result):
    cursor = conn.cursor()

    cursor.execute(
        """
        MERGE INTO AI.TICKET_ENRICHMENT target
        USING (
            SELECT
                %s AS TICKET_ID,
                %s AS CATEGORY,
                %s AS URGENCY,
                %s AS SENTIMENT,
                %s AS SUMMARY,
                %s AS MODEL_USED
        ) source

        ON target.TICKET_ID = source.TICKET_ID

        WHEN MATCHED THEN UPDATE SET
            CATEGORY = source.CATEGORY,
            URGENCY = source.URGENCY,
            SENTIMENT = source.SENTIMENT,
            SUMMARY = source.SUMMARY,
            MODEL_USED = source.MODEL_USED,
            PROCESSED_AT = CURRENT_TIMESTAMP()

        WHEN NOT MATCHED THEN INSERT (
            TICKET_ID,
            CATEGORY,
            URGENCY,
            SENTIMENT,
            SUMMARY,
            MODEL_USED
        )
        VALUES (
            source.TICKET_ID,
            source.CATEGORY,
            source.URGENCY,
            source.SENTIMENT,
            source.SUMMARY,
            source.MODEL_USED
        )
        """,
        (
            ticket_id,
            result["category"],
            result["urgency"],
            result["sentiment"],
            result["summary"],
            MODEL,
        ),
    )


def main():
    conn = get_connection()

    try:
        tickets = get_tickets(conn)

        for ticket_id, subject, message in tickets:
            print(f"Processing ticket {ticket_id}...")

            result = enrich_with_ollama(subject, message)

            save_result(conn, ticket_id, result)

            print(result)

    finally:
        conn.close()


if __name__ == "__main__":
    main()