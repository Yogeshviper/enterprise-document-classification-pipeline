
import joblib

MODEL_PATH = "models/document_classifier.pk2"

# Load trained model
try:
    model = joblib.load(MODEL_PATH)
    print("Model loaded successfully.")

except FileNotFoundError:
    print(f"Model file not found: {MODEL_PATH}")
    exit(1)


# Test documents covering all 7 categories
test_documents = [
    "Invoice No INV-2026-999. Bill To Contoso Ltd. Amount 4500. Payment due within 30 days.",

    "Purchase Order PO-2026-999. Supplier TechSource Ltd. Buyer Northwind Services. Quantity 25.",

    "Candidate Resume. Professional experience, education, technical skills, Python, Azure and employment history.",

    "This agreement is entered into between the supplier and customer for providing consulting services.",

    "Meeting minutes. Project discussion, attendees, action items and next meeting schedule.",

    "Employee Identity Card. Employee ID EMP-1001. Name Rahul Sharma. Department IT. Valid until 2027.",

    "Payment Receipt. Receipt No RCPT-2026-999. Amount paid 2500. Payment mode UPI. Status Paid."
]


# Predict document categories
predictions = model.predict(test_documents)

# Predict confidence if supported by the model
probabilities = None

if hasattr(model, "predict_proba"):
    probabilities = model.predict_proba(test_documents)


print("\n====================================")
print("DOCUMENT CLASSIFICATION RESULTS")
print("====================================")

for i, (document, prediction) in enumerate(
    zip(test_documents, predictions)
):

    print("\nDocument:")
    print(document)

    print(f"Predicted Category: {prediction}")

    if probabilities is not None:
        confidence = max(probabilities[i]) * 100
        print(f"Confidence: {confidence:.2f}%")

    print("------------------------------------")
