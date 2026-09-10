import os
from dotenv import load_dotenv
from groq import Groq


load_dotenv()

MODEL = "openai/gpt-oss-20b"


def call_llm(prompt: str) -> str:
    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        raise RuntimeError(
            "GROQ_API_KEY is not configured."
        )

    client = Groq(api_key=api_key)

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are an AI component inside a governed "
                    "enterprise analytics platform. Follow the "
                    "instructions precisely and do not invent data."
                ),
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
        temperature=0,
    )

    return response.choices[0].message.content.strip()  