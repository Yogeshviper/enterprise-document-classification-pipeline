# Resource Naming Standards

## Environment

Current environment:

Development

Environment identifier:

dev

---

## Deployment Region

Current development region:

Central India

Azure region name:

centralindia

# Azure Resources

## Resource Group

rg-docclass-dev-002

## Storage Account

stdocclassdev002

## Azure AI Foundry Hub

aih-docclass-dev-002

## Azure AI Foundry Project

aip-docclass-dev-002

## Azure Machine Learning Workspace

mlw-docclass-dev-002

## AKS Cluster

aks-docclass-dev-002

---

# Blob Containers

The Blob Storage architecture is based on document processing stages,
not document types.

## Raw Documents

raw-documents

Purpose:

Stores documents exactly as uploaded by the user.

---

## Processed Documents

processed-documents

Purpose:

Stores processed document data and intermediate processing output.

---

## Classified Documents

classified-documents

Purpose:

Stores classification results and processed output associated
with classified documents.

---

# Important Design Principle

Document types are NOT represented as Blob Storage containers
or hard-coded folder structures.

The ML model determines the document type based on document
content.

For example:

A document uploaded as:

document123.pdf

may be classified as:

Invoice

Another document:

file456.pdf

may be classified as:

Salary Slip

The Blob Storage structure remains unchanged.

---

# Future Environment Naming

Development:

rg-docclass-dev-002
stdocclassdev002
mlw-docclass-dev-002
aks-docclass-dev-002

Test:

rg-docclass-test-002
stdocclasstest002
mlw-docclass-test-002
aks-docclass-test-002

Production:

rg-docclass-prod-001
stdocclassprod001
mlw-docclass-prod-001
aks-docclass-prod-001
