# Enterprise Document Classification Pipeline

## Overview

The Enterprise Document Classification Pipeline is a production-
oriented MLOps solution for automatically classifying enterprise
documents based on their content.

The solution manages the machine learning lifecycle from document
preparation and model training through model registration,
deployment and reporting.

---

## Architecture

<img width="1536" height="1024" alt="image" src="https://github.com/user-attachments/assets/503b26ec-fca2-431f-b643-20aad8192669" />




## Key Microsoft Services

- Azure Blob Storage
- Azure AI Foundry
- Azure Machine Learning
- Model Registry
- GitHub Actions
- Azure Kubernetes Service
- Power BI
- Microsoft Entra ID

---

## Document Classification

The solution classifies documents based on their content rather
than relying on filenames.

The document categories are configurable according to customer
requirements.

The storage architecture is independent of document type.

---

## Blob Storage Structure

```text
raw-documents/
classified-documents/
