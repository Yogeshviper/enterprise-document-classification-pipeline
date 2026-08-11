from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.core.credentials import AzureKeyCredential

from src.storage.blob_client import BlobStorageClient
import joblib
import os
import json
from datetime import datetime, timezone


# ============================================================
# CONFIGURATION
# ============================================================

DI_ENDPOINT = "https://docclass-di-dev-001.cognitiveservices.azure.com/"
DI_KEY = os.environ["DOCUMENT_INTELLIGENCE_KEY"]

RAW_CONTAINER = "raw-documents"
DOCUMENT_NAME = "test-doc.pdf"

MODEL_PATH = "models/document_classifier.pkl"


# ============================================================
# LOAD ML MODEL
# ============================================================

print("Loading ML model...")

model = joblib.load(MODEL_PATH)

print("ML model loaded successfully.")


# ============================================================
# CONNECT TO DOCUMENT INTELLIGENCE
# ============================================================

document_client = DocumentIntelligenceClient(
    endpoint=DI_ENDPOINT,
    credential=AzureKeyCredential(DI_KEY),
)


# ============================================================
# DOWNLOAD DOCUMENT FROM BLOB
# ============================================================

print("\nDownloading document from Blob Storage...")

storage = BlobStorageClient()

pdf_bytes = storage.download_document(
    RAW_CONTAINER,
    DOCUMENT_NAME,
)

print(f"Downloaded: {DOCUMENT_NAME}")
print(f"Document size: {len(pdf_bytes)} bytes")


# ============================================================
# EXTRACT TEXT USING DOCUMENT INTELLIGENCE
# ============================================================

print("\nExtracting text using Document Intelligence...")

poller = document_client.begin_analyze_document(
    "prebuilt-read",
    body=pdf_bytes,
)

result = poller.result()


extracted_text = ""

for page in result.pages:

    for line in page.lines:

        extracted_text += line.content + "\n"


extracted_text = extracted_text.strip()


print("Text extraction completed.")

print("\nExtracted text length:")
print(len(extracted_text))


# ============================================================
# CLASSIFY DOCUMENT
# ============================================================

print("\nRunning ML classification...")

prediction = model.predict(
    [extracted_text]
)[0]

# ============================================================
# SAVE CLASSIFICATION RESULT
# ============================================================

RESULT_CONTAINER = "classified-documents"

result_data = {
    "document_name": DOCUMENT_NAME,
    "predicted_type": str(prediction),
    "status": "classified",
    "processed_at": datetime.now(timezone.utc).isoformat(),
}

result_json = json.dumps(
    result_data,
    indent=2
)

result_blob_name = (
    DOCUMENT_NAME.rsplit(".", 1)[0] + ".json"
)

storage.upload_document(
    RESULT_CONTAINER,
    result_blob_name,
    result_json.encode("utf-8"),
)

print("\nClassification result saved successfully.")
print(f"Result container : {RESULT_CONTAINER}")
print(f"Result file      : {result_blob_name}")


# ============================================================
# FINAL RESULT
# ============================================================

print("\n============================================")
print("DOCUMENT CLASSIFICATION RESULT")
print("============================================")

print(f"Document       : {DOCUMENT_NAME}")
print(f"Predicted Type : {prediction}")

print("============================================")