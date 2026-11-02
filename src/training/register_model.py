from azure.ai.ml import MLClient
from azure.ai.ml.entities import Model
#from azure.identity import AzureCliCredential
from azure.identity import InteractiveBrowserCredential


# ============================================================
# Azure configuration
# ============================================================

SUBSCRIPTION_ID = "2611858c-37e9-4158-990e-572dbd349687"
RESOURCE_GROUP = "RG-YogeshKhairnar"
WORKSPACE_NAME = "enterprise-document-ml-1"


# ============================================================
# Connect to Azure ML
# ============================================================

print("Connecting to Azure ML...")

#credential = AzureCliCredential()
credential = InteractiveBrowserCredential(
    tenant_id="6557bae0-e0d1-4268-8782-39d8cadbefe7"
)

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

MODEL_PATH = "models/document_classifier.pk2"

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