import json
import os
from datetime import datetime, timezone
from pathlib import Path

import joblib
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse
from azure.core.credentials import AzureKeyCredential
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient


# ============================================================
# CONFIGURATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[2]

MODEL_PATH = BASE_DIR / "models" / "document_classifier.pkl"

STORAGE_ACCOUNT_NAME = "stdocclassdev001"

RAW_CONTAINER = "raw-documents"
CLASSIFIED_CONTAINER = "classified-documents"

DOCUMENT_INTELLIGENCE_ENDPOINT = os.getenv(
    "DOCUMENT_INTELLIGENCE_ENDPOINT",
    "https://docclass-di-dev-001.cognitiveservices.azure.com/",
)

DOCUMENT_INTELLIGENCE_KEY = os.getenv(
    "DOCUMENT_INTELLIGENCE_KEY"
)


# ============================================================
# FASTAPI
# ============================================================

app = FastAPI(
    title="Enterprise Document Classification",
    version="1.0",
)


# ============================================================
# LOAD ML MODEL
# ============================================================

try:

    model = joblib.load(MODEL_PATH)

    print("ML model loaded successfully.")
    print(f"Model path: {MODEL_PATH}")

except Exception as e:

    model = None

    print("WARNING: ML model could not be loaded.")
    print(f"Model error: {e}")


# ============================================================
# AZURE BLOB STORAGE
# ============================================================

try:

    storage_account_url = (
        f"https://{STORAGE_ACCOUNT_NAME}.blob.core.windows.net"
    )

    storage_credential = DefaultAzureCredential()

    blob_service_client = BlobServiceClient(
        account_url=storage_account_url,
        credential=storage_credential,
    )

    print("Blob Storage client initialized.")

except Exception as e:

    blob_service_client = None

    print("WARNING: Blob Storage client could not be initialized.")
    print(f"Storage error: {e}")


# ============================================================
# DOCUMENT INTELLIGENCE
# ============================================================

document_intelligence_client = None

if DOCUMENT_INTELLIGENCE_KEY:

    try:

        document_intelligence_client = DocumentIntelligenceClient(
            endpoint=DOCUMENT_INTELLIGENCE_ENDPOINT,
            credential=AzureKeyCredential(
                DOCUMENT_INTELLIGENCE_KEY
            ),
        )

        print("Document Intelligence client initialized.")

    except Exception as e:

        print(
            "WARNING: Document Intelligence initialization failed."
        )

        print(f"Document Intelligence error: {e}")

else:

    print(
        "WARNING: DOCUMENT_INTELLIGENCE_KEY environment variable "
        "is not configured."
    )


# ============================================================
# SUPPORTED FILE TYPES
# ============================================================

SUPPORTED_EXTENSIONS = {
    ".pdf": "application/pdf",

    ".docx": (
        "application/vnd.openxmlformats-officedocument."
        "wordprocessingml.document"
    ),

    ".doc": "application/msword",

    ".png": "image/png",

    ".jpg": "image/jpeg",

    ".jpeg": "image/jpeg",

    ".tif": "image/tiff",

    ".tiff": "image/tiff",
}


# ============================================================
# HELPER - GET BLOB CONTAINER
# ============================================================

def get_container(container_name: str):

    if blob_service_client is None:

        raise HTTPException(
            status_code=500,
            detail="Blob Storage is not configured.",
        )

    return blob_service_client.get_container_client(
        container_name
    )


# ============================================================
# HELPER - UPLOAD TO BLOB STORAGE
# ============================================================

def upload_to_blob(
    container_name: str,
    blob_name: str,
    data: bytes,
):

    container_client = get_container(
        container_name
    )

    blob_client = container_client.get_blob_client(
        blob_name
    )

    blob_client.upload_blob(
        data,
        overwrite=True,
    )

    return blob_client


# ============================================================
# HELPER - SAVE CLASSIFICATION RESULT
# ============================================================

def save_classification_result(
    document_name: str,
    predicted_type: str,
):

    result = {

        "document_name": document_name,

        "predicted_type": predicted_type,

        "status": "classified",

        "processed_at": datetime.now(
            timezone.utc
        ).isoformat(),

    }

    json_name = (
        Path(document_name).stem
        + ".json"
    )

    json_data = json.dumps(
        result,
        indent=2,
    ).encode("utf-8")

    upload_to_blob(
        CLASSIFIED_CONTAINER,
        json_name,
        json_data,
    )

    return result


# ============================================================
# HELPER - DOCUMENT INTELLIGENCE TEXT EXTRACTION
# ============================================================

def extract_text(
    document_bytes: bytes,
    content_type: str,
):

    if document_intelligence_client is None:

        raise HTTPException(
            status_code=500,
            detail=(
                "Document Intelligence is not configured. "
                "Set the DOCUMENT_INTELLIGENCE_KEY "
                "environment variable."
            ),
        )

    try:

        print(
            "Starting Document Intelligence analysis..."
        )

        poller = (
            document_intelligence_client
            .begin_analyze_document(
                model_id="prebuilt-read",
                body=document_bytes,
                content_type=content_type,
            )
        )

        result = poller.result()

        print(
            "Document Intelligence analysis completed."
        )

    except Exception as e:

        print(
            "Document Intelligence analysis failed."
        )

        print(str(e))

        raise HTTPException(
            status_code=500,
            detail=(
                "Document Intelligence failed: "
                + str(e)
            ),
        )

    # --------------------------------------------------------
    # Primary method
    # --------------------------------------------------------

    extracted_text = ""

    try:

        extracted_text = result.content or ""

    except AttributeError:

        extracted_text = ""

    # --------------------------------------------------------
    # Fallback method
    # --------------------------------------------------------

    if not extracted_text.strip():

        text_parts = []

        try:

            for page in result.pages:

                try:

                    for line in page.lines:

                        if line.content:

                            text_parts.append(
                                line.content
                            )

                except AttributeError:

                    continue

        except AttributeError:

            pass

        extracted_text = "\n".join(
            text_parts
        )

    extracted_text = extracted_text.strip()

    print(
        f"Extracted text length: "
        f"{len(extracted_text)} characters"
    )

    if not extracted_text:

        raise HTTPException(
            status_code=400,
            detail=(
                "No readable text was found "
                "in the uploaded document."
            ),
        )

    return extracted_text


# ============================================================
# HELPER - CLASSIFY TEXT
# ============================================================

def classify_text(text: str):

    if model is None:

        raise HTTPException(
            status_code=500,
            detail="ML model is not loaded.",
        )

    try:

        prediction = model.predict(
            [text]
        )[0]

        return str(prediction)

    except Exception as e:

        print(
            "ML classification failed."
        )

        print(str(e))

        raise HTTPException(
            status_code=500,
            detail=(
                "ML classification failed: "
                + str(e)
            ),
        )


# ============================================================
# HOME PAGE
# ============================================================

@app.get(
    "/",
    response_class=HTMLResponse,
)
async def home():

    return """
<!DOCTYPE html>

<html>

<head>

<meta charset="UTF-8">

<title>
Enterprise Document Classification
</title>

<style>

* {
    box-sizing: border-box;
}

body {

    margin: 0;

    font-family:
        Arial,
        Helvetica,
        sans-serif;

    background:
        #f3f6fa;

    color:
        #111827;
}

.header {

    background:
        linear-gradient(
            135deg,
            #0078d4,
            #005a9e
        );

    color:
        white;

    padding:
        55px 20px;

    text-align:
        center;
}

.header h1 {

    margin:
        0 0 12px 0;

    font-size:
        42px;
}

.header p {

    margin:
        0;

    font-size:
        20px;
}

.container {

    max-width:
        1100px;

    margin:
        50px auto;

    padding:
        0 20px;
}

.card {

    background:
        white;

    border-radius:
        16px;

    padding:
        40px;

    box-shadow:
        0 8px 30px
        rgba(
            0,
            0,
            0,
            0.08
        );
}

.upload-area {

    border:
        2px dashed
        #0078d4;

    background:
        #f7fbff;

    border-radius:
        12px;

    padding:
        55px 30px;

    text-align:
        center;
}

.upload-area input {

    margin:
        20px 0;

    font-size:
        16px;
}

button {

    display:
        block;

    margin:
        15px auto;

    background:
        #0078d4;

    color:
        white;

    border:
        none;

    border-radius:
        8px;

    padding:
        16px 35px;

    font-size:
        18px;

    font-weight:
        bold;

    cursor:
        pointer;
}

button:hover {

    background:
        #005a9e;
}

.supported {

    color:
        #6b7280;

    margin-top:
        15px;

    font-size:
        14px;
}

.result {

    margin-top:
        30px;

    padding:
        30px;

    background:
        #f0fff4;

    border:
        1px solid
        #b7ebc6;

    border-radius:
        12px;

}

.result h2 {

    margin-top:
        0;
}

.document-type {

    font-size:
        36px;

    font-weight:
        bold;

    color:
        #15803d;

    margin:
        15px 0;
}

.status {

    color:
        #15803d;

    font-weight:
        bold;
}

.error {

    margin-top:
        25px;

    padding:
        20px;

    background:
        #fff1f2;

    border:
        1px solid
        #fecdd3;

    border-radius:
        10px;

    color:
        #be123c;

}

.loading {

    display:
        none;

    margin-top:
        20px;

    text-align:
        center;

    color:
        #0078d4;

    font-weight:
        bold;

}

.footer {

    text-align:
        center;

    color:
        #6b7280;

    margin:
        30px 0;

}

</style>

</head>


<body>


<div class="header">

<h1>
Enterprise Document Classification
</h1>

<p>
AI-powered document classification
</p>

</div>


<div class="container">


<div class="card">


<h2>
Upload Document
</h2>


<p>
Upload a document and the system will
automatically identify its type.
</p>


<form
    id="uploadForm"
>


<div class="upload-area">


<input
    type="file"
    id="file"
    name="file"
    accept=".pdf,.docx,.doc,.png,.jpg,.jpeg,.tif,.tiff"
    required
>


<button
    type="submit"
>
Classify Document
</button>


<div class="supported">

Supported formats:
PDF, DOCX, DOC, PNG, JPG, JPEG, TIFF

</div>


</div>


</form>


<div
    id="loading"
    class="loading"
>
Analyzing document...
</div>


<div
    id="result"
>
</div>


</div>


<div class="footer">

Enterprise Document Classification POC

</div>


</div>


<script>


const form =
    document.getElementById(
        "uploadForm"
    );


const resultDiv =
    document.getElementById(
        "result"
    );


const loading =
    document.getElementById(
        "loading"
    );


form.addEventListener(
    "submit",
    async function(event) {

        event.preventDefault();


        const fileInput =
            document.getElementById(
                "file"
            );


        if (
            !fileInput.files.length
        ) {

            return;

        }


        const file =
            fileInput.files[0];


        const formData =
            new FormData();


        formData.append(
            "file",
            file
        );


        resultDiv.innerHTML =
            "";


        loading.style.display =
            "block";


        try {

            const response =
                await fetch(
                    "/upload",
                    {
                        method:
                            "POST",

                        body:
                            formData
                    }
                );


            const data =
                await response.json();


            loading.style.display =
                "none";


            if (!response.ok) {

                resultDiv.innerHTML = `
                    <div class="error">
                        <strong>Error:</strong>
                        ${data.detail || data.error || "Classification failed."}
                    </div>
                `;

                return;

            }


            resultDiv.innerHTML = `

                <div class="result">

                    <h2>
                        Classification Result
                    </h2>

                    <p>
                        <strong>
                            Document:
                        </strong>
                        ${data.document_name}
                    </p>

                    <p>
                        <strong>
                            Document Type:
                        </strong>
                    </p>

                    <div class="document-type">
                        ${data.predicted_type}
                    </div>

                    <p class="status">
                        Status:
                        Classified Successfully
                    </p>

                </div>

            `;


        }

        catch (error) {

            loading.style.display =
                "none";


            resultDiv.innerHTML = `

                <div class="error">

                    <strong>
                        Error:
                    </strong>

                    ${error.message}

                </div>

            `;

        }

    }

);

</script>


</body>

</html>
"""


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/health")
def health_check():

    return {

        "status": "healthy",

        "service":
            "document-classification-api",

        "model_loaded":
            model is not None,

        "document_intelligence_configured":
            document_intelligence_client is not None,

    }


# ============================================================
# PREDICT FROM TEXT
# ============================================================

@app.post("/predict")
async def predict(document_text: str):

    if not document_text.strip():

        raise HTTPException(
            status_code=400,
            detail="Document text cannot be empty.",
        )

    prediction = classify_text(
        document_text
    )

    return {

        "document_text":
            document_text,

        "predicted_class":
            prediction,

    }


# ============================================================
# UPLOAD AND CLASSIFY DOCUMENT
# ============================================================

@app.post("/upload")
async def upload_document(
    file: UploadFile = File(...)
):

    # --------------------------------------------------------
    # Validate filename
    # --------------------------------------------------------

    if not file.filename:

        raise HTTPException(
            status_code=400,
            detail="No filename provided.",
        )


    filename = Path(
        file.filename
    ).name


    extension = Path(
        filename
    ).suffix.lower()


    # --------------------------------------------------------
    # Validate file type
    # --------------------------------------------------------

    if extension not in SUPPORTED_EXTENSIONS:

        raise HTTPException(
            status_code=400,
            detail=(
                "Unsupported file type. "
                "Supported formats: "
                "PDF, DOCX, DOC, PNG, JPG, JPEG, TIFF."
            ),
        )


    content_type = (
        SUPPORTED_EXTENSIONS[
            extension
        ]
    )


    # --------------------------------------------------------
    # Read uploaded document
    # --------------------------------------------------------

    try:

        document_bytes = await file.read()

    except Exception as e:

        raise HTTPException(
            status_code=400,
            detail=(
                "Unable to read uploaded file: "
                + str(e)
            ),
        )


    if not document_bytes:

        raise HTTPException(
            status_code=400,
            detail="Uploaded file is empty.",
        )


    print(
        f"Received document: {filename}"
    )

    print(
        f"Document size: "
        f"{len(document_bytes)} bytes"
    )


    # --------------------------------------------------------
    # Upload original document to raw-documents
    # --------------------------------------------------------

    try:

        upload_to_blob(
            RAW_CONTAINER,
            filename,
            document_bytes,
        )

        print(
            f"Uploaded to Blob Storage: "
            f"{RAW_CONTAINER}/{filename}"
        )

    except Exception as e:

        print(
            "Raw document upload failed."
        )

        print(str(e))

        raise HTTPException(
            status_code=500,
            detail=(
                "Failed to upload document "
                "to Blob Storage: "
                + str(e)
            ),
        )


    # --------------------------------------------------------
    # Extract text using Azure Document Intelligence
    # --------------------------------------------------------

    print(
        "Extracting text using "
        "Document Intelligence..."
    )


    extracted_text = extract_text(
        document_bytes,
        content_type,
    )


    # --------------------------------------------------------
    # Run ML classification
    # --------------------------------------------------------

    print(
        "Running ML classification..."
    )


    predicted_type = classify_text(
        extracted_text
    )


    print(
        "============================================"
    )

    print(
        "DOCUMENT CLASSIFICATION RESULT"
    )

    print(
        "============================================"
    )

    print(
        f"Document       : {filename}"
    )

    print(
        f"Predicted Type : {predicted_type}"
    )

    print(
        "============================================"
    )


    # --------------------------------------------------------
    # Save classification result to Blob Storage
    # --------------------------------------------------------

    try:

        result = save_classification_result(
            filename,
            predicted_type,
        )

        print(
            "Classification result saved to "
            f"{CLASSIFIED_CONTAINER}"
        )

    except Exception as e:

        print(
            "Failed to save classification result."
        )

        print(str(e))

        raise HTTPException(
            status_code=500,
            detail=(
                "Document was classified, "
                "but the result could not be saved: "
                + str(e)
            ),
        )


    # --------------------------------------------------------
    # Return result to UI
    # --------------------------------------------------------

    return JSONResponse(

        content={

            "document_name":
                filename,

            "predicted_type":
                predicted_type,

            "status":
                "classified",

            "processed_at":
                result["processed_at"],

            "message":
                "Document classified successfully.",

        }

    )