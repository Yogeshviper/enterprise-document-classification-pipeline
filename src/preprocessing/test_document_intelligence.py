import os

from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.core.credentials import AzureKeyCredential

from src.storage.blob_client import BlobStorageClient


ENDPOINT = "https://docclass-di-dev-001.cognitiveservices.azure.com/"
DI_KEY = os.environ["DOCUMENT_INTELLIGENCE_KEY"]

RAW_CONTAINER = "raw-documents"
DOCUMENT_NAME = "test-doc.pdf"


# Connect to Document Intelligence
client = DocumentIntelligenceClient(
    endpoint=ENDPOINT,
    credential=AzureKeyCredential(DI_KEY),
)

# Download document from Blob Storage
storage = BlobStorageClient()

pdf_bytes = storage.download_document(
    RAW_CONTAINER,
    DOCUMENT_NAME,
)

print("Document downloaded from Blob Storage.")
print(f"Document size: {len(pdf_bytes)} bytes")


# Send PDF to Document Intelligence
poller = client.begin_analyze_document(
    "prebuilt-read",
    body=pdf_bytes,
)

result = poller.result()


print("\n====================================")
print("DOCUMENT INTELLIGENCE RESULT")
print("====================================")

for page in result.pages:
    for line in page.lines:
        print(line.content)