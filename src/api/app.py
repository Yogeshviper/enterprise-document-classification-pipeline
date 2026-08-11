from fastapi import FastAPI
from pydantic import BaseModel
import joblib


app = FastAPI(
    title="Enterprise Document Classification API",
    version="1.0"
)


# Load trained model
MODEL_PATH = "models/document_classifier.pkl"

model = joblib.load(MODEL_PATH)


class DocumentRequest(BaseModel):
    document_text: str


@app.get("/")
def health_check():
    return {
        "status": "healthy",
        "service": "document-classification-api"
    }


@app.post("/predict")
def predict(request: DocumentRequest):

    prediction = model.predict([request.document_text])[0]

    return {
        "document_text": request.document_text,
        "predicted_class": prediction
    }