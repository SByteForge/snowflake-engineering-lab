import os

import snowflake.connector
from dotenv import load_dotenv


load_dotenv()


def get_config(name: str, default=None):
    """
    Read configuration from:
    1. Local environment / .env
    2. Streamlit Cloud secrets
    """

    value = os.getenv(name)

    if value:
        return value

    try:
        import streamlit as st

        if name in st.secrets:
            return st.secrets[name]

    except Exception:
        pass

    return default


def get_connection():
    user = get_config("SNOWFLAKE_USER")
    password = get_config("SNOWFLAKE_PASSWORD")
    account = get_config("SNOWFLAKE_ACCOUNT")

    warehouse = get_config(
        "SNOWFLAKE_WAREHOUSE",
        "COMPUTE_WH",
    )

    database = get_config(
        "SNOWFLAKE_DATABASE",
        "AI_ENGINEERING_LAB",
    )

    role = get_config(
        "SNOWFLAKE_ROLE",
        "ACCOUNTADMIN",
    )

    required = {
        "SNOWFLAKE_USER": user,
        "SNOWFLAKE_PASSWORD": password,
        "SNOWFLAKE_ACCOUNT": account,
    }

    missing = [
        key
        for key, value in required.items()
        if not value
    ]

    if missing:
        raise RuntimeError(
            "Missing Snowflake configuration: "
            + ", ".join(missing)
        )

    return snowflake.connector.connect(
        user=user,
        password=password,
        account=account,
        warehouse=warehouse,
        database=database,
        role=role,
    )