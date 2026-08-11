from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient


STORAGE_ACCOUNT_NAME = "stdocclassdev001"


class BlobStorageClient:
    def __init__(self):
        account_url = (
            f"https://{STORAGE_ACCOUNT_NAME}.blob.core.windows.net"
        )

        credential = DefaultAzureCredential()

        self.client = BlobServiceClient(
            account_url=account_url,
            credential=credential,
        )

    def get_container(self, container_name: str):
        return self.client.get_container_client(container_name)

    def list_documents(self, container_name: str):
        container_client = self.get_container(container_name)

        return [
            blob.name
            for blob in container_client.list_blobs()
        ]
    