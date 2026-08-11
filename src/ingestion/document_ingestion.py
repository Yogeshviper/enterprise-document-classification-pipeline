from src.storage.blob_client import BlobStorageClient


RAW_CONTAINER = "raw-documents"


def get_documents():
    storage_client = BlobStorageClient()

    documents = storage_client.list_documents(
        RAW_CONTAINER
    )

    return documents


if __name__ == "__main__":
    documents = get_documents()

    print("Documents available for processing:")

    for document in documents:
        print(f"- {document}")