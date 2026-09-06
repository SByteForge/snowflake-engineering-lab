import os
import kagglehub

path = kagglehub.dataset_download(
    "ajverse/customer-support-tickets-crm-dataset"
)

print("Dataset downloaded to:")
print(path)

print("\nFiles:")
for file_name in os.listdir(path):
    print(file_name)