from azure.ai.ml import MLClient
from azure.ai.ml.entities import Model
from azure.identity import AzureCliCredential


# ============================================================
# Azure configuration
# ============================================================

SUBSCRIPTION_ID = "96df72e2-2bf4-44c9-81b0-ef644cf462e5"
RESOURCE_GROUP = "rg-docclass-dev-001"
WORKSPACE_NAME = "enterprise-document-ml"


# ============================================================
# Connect to Azure ML
# ============================================================

print("Connecting to Azure ML...")

credential = AzureCliCredential()

ml_client = MLClient(
    credential=credential,
    subscription_id=SUBSCRIPTION_ID,
    resource_group_name=RESOURCE_GROUP,
    workspace_name=WORKSPACE_NAME
)

print("Connected successfully.")
print(f"Workspace: {WORKSPACE_NAME}")


# ============================================================
# Register model
# ============================================================

MODEL_PATH = "models/document_classifier.pkl"

model = Model(
    path=MODEL_PATH,
    name="document-classifier",
    description="CPU-based document classification model using TF-IDF and Logistic Regression",
    type="custom_model"
)


print("\nRegistering model...")

registered_model = ml_client.models.create_or_update(model)


# ============================================================
# Result
# ============================================================

print("\n============================================")
print("MODEL REGISTERED SUCCESSFULLY")
print("============================================")

print(f"Model name:    {registered_model.name}")
print(f"Model version: {registered_model.version}")
print(f"Model ID:      {registered_model.id}")