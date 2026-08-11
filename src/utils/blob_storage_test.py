from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient


STORAGE_ACCOUNT_NAME = "stdocclassdev001"
CONTAINER_NAME = "raw-documents"


def main():
    account_url = (
        f"https://{STORAGE_ACCOUNT_NAME}.blob.core.windows.net"
    )

    credential = DefaultAzureCredential()

    blob_service_client = BlobServiceClient(
        account_url=account_url,
        credential=credential,
    )

    container_client = blob_service_client.get_container_client(
        CONTAINER_NAME
    )

    print(f"Connected to container: {CONTAINER_NAME}")
    print("Documents:")

    for blob in container_client.list_blobs():
        print(f"- {blob.name}")


if __name__ == "__main__":
    main()