import os
import pandas as pd

DATASET_PATH = (
    "/Users/shubhamtiwari/.cache/kagglehub/"
    "datasets/ajverse/customer-support-tickets-crm-dataset/versions/2"
)

files = [
    "customer_support_tickets.csv",
    "enhanced_customer_support_data.csv",
]

for file_name in files:
    file_path = os.path.join(DATASET_PATH, file_name)

    print("\n" + "=" * 100)
    print(f"FILE: {file_name}")
    print("=" * 100)

    df = pd.read_csv(file_path)

    print(f"\nRows: {len(df)}")
    print(f"Columns: {len(df.columns)}")

    print("\nColumn names:")
    for col in df.columns:
        print(f" - {col}")

    print("\nData types:")
    print(df.dtypes)

    print("\nMissing values:")
    print(df.isnull().sum())

    print("\nDuplicate rows:")
    print(df.duplicated().sum())

    print("\nSample:")
    print(df.head(3).to_string())