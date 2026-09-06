import os
import snowflake.connector


def get_connection():
    return snowflake.connector.connect(
        user=os.environ["SNOWFLAKE_USER"],
        password=os.environ["SNOWFLAKE_PASSWORD"],
        account=os.environ["SNOWFLAKE_ACCOUNT"],
        warehouse=os.environ.get("SNOWFLAKE_WAREHOUSE", "COMPUTE_WH"),
        database=os.environ.get("SNOWFLAKE_DATABASE", "AI_ENGINEERING_LAB"),
        schema=os.environ.get("SNOWFLAKE_SCHEMA", "RAW"),
        role=os.environ.get("SNOWFLAKE_ROLE", "ACCOUNTADMIN"),
    )