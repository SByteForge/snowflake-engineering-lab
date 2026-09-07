import os
import kagglehub

from db import get_connection


DATASET_SLUG = "ajverse/customer-support-tickets-crm-dataset"
FILE_NAME = "enhanced_customer_support_data.csv"

DATABASE = "AI_ENGINEERING_LAB"
SCHEMA = "RAW"
STAGE = "CUSTOMER_SUPPORT_STAGE"


def download_dataset():
    path = kagglehub.dataset_download(DATASET_SLUG)

    file_path = os.path.join(path, FILE_NAME)

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"{FILE_NAME} not found in {path}")

    print(f"Dataset ready at: {file_path}")
    return file_path


def upload_to_stage(file_path):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(f"USE DATABASE {DATABASE}")
        cursor.execute(f"USE SCHEMA {SCHEMA}")

        cursor.execute(f"""
            CREATE STAGE IF NOT EXISTS {STAGE}
        """)

        cursor.execute(
            f"PUT file://{file_path} @{STAGE} AUTO_COMPRESS=FALSE OVERWRITE=TRUE"
        )

        print(f"Uploaded to Snowflake stage: @{STAGE}")

    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    file_path = download_dataset()
    upload_to_stage(file_path)