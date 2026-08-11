import joblib


MODEL_PATH = "models/document_classifier.pkl"


# Load trained model
model = joblib.load(MODEL_PATH)

print("Model loaded successfully.")


# Test documents
test_documents = [
    "Invoice No INV-2026-999. Bill To Contoso Ltd. Amount $4500. Payment due within 30 days.",

    "Purchase Order PO-2026-999. Supplier TechSource Ltd. Buyer Northwind Services. Quantity 25.",

    "This document contains information about the candidate's professional experience, education and technical skills.",

    "This agreement is entered into between the supplier and customer for providing consulting services."
]


# Predict
predictions = model.predict(test_documents)


print("\n====================================")
print("DOCUMENT CLASSIFICATION RESULTS")
print("====================================")

for document, prediction in zip(test_documents, predictions):

    print("\nDocument:")
    print(document)

    print("Predicted class:")
    print(prediction)