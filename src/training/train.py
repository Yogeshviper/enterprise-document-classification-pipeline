import os
import pandas as pd
import joblib

from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix
)


# ============================================================
# Paths
# ============================================================

TRAINING_DATA = "data/labeled/training_data.csv"
VALIDATION_DATA = "data/labeled/validation_data.csv"

MODEL_DIR = "models"
MODEL_PATH = os.path.join(MODEL_DIR, "document_classifier.pkl")


# ============================================================
# Load datasets
# ============================================================

print("============================================")
print("Loading datasets")
print("============================================")

train_df = pd.read_csv(TRAINING_DATA)
validation_df = pd.read_csv(VALIDATION_DATA)

print(f"Training records:   {len(train_df)}")
print(f"Validation records: {len(validation_df)}")

print("\nTraining columns:")
print(train_df.columns.tolist())

print("\nValidation columns:")
print(validation_df.columns.tolist())


# ============================================================
# Clean data
# ============================================================

train_df = train_df.dropna(subset=["document_text", "label"])
validation_df = validation_df.dropna(
    subset=["document_text", "label"]
)

print("\nAfter cleaning:")
print(f"Training records:   {len(train_df)}")
print(f"Validation records: {len(validation_df)}")


# ============================================================
# Show classes
# ============================================================

print("\nTraining label distribution:")
print(train_df["label"].value_counts())

print("\nValidation label distribution:")
print(validation_df["label"].value_counts())


# ============================================================
# Prepare training and validation data
# ============================================================

X_train = train_df["document_text"]
y_train = train_df["label"]

X_validation = validation_df["document_text"]
y_validation = validation_df["label"]


# ============================================================
# Create ML pipeline
# ============================================================

model = Pipeline([
    (
        "tfidf",
        TfidfVectorizer(
            lowercase=True,
            stop_words="english",
            max_features=10000
        )
    ),
    (
        "classifier",
        LogisticRegression(
            max_iter=1000
        )
    )
])


# ============================================================
# Train
# ============================================================

print("\n============================================")
print("Training model...")
print("============================================")

model.fit(X_train, y_train)

print("Training completed successfully.")


# ============================================================
# Validation
# ============================================================

print("\n============================================")
print("Evaluating model")
print("============================================")

predictions = model.predict(X_validation)

accuracy = accuracy_score(
    y_validation,
    predictions
)

print(f"\nValidation Accuracy: {accuracy:.4f}")

print("\nClassification Report:")
print(
    classification_report(
        y_validation,
        predictions,
        zero_division=0
    )
)

print("\nConfusion Matrix:")
print(
    confusion_matrix(
        y_validation,
        predictions
    )
)


# ============================================================
# Save model
# ============================================================

os.makedirs(MODEL_DIR, exist_ok=True)

joblib.dump(
    model,
    MODEL_PATH
)

print("\n============================================")
print("MODEL SAVED")
print("============================================")

print(f"Model location:")
print(MODEL_PATH)