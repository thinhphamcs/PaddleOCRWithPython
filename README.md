# PaddleOCR
A professional, learning-focused repository for Optical Character Recognition (OCR) using PaddleOCR and Python.

This project demonstrates real-world software architecture patterns with clean separation of concerns, modular design, and a production-ready Streamlit interface. It supports **multiple fine-tuned models** for different document types (invoices, healthcare forms, bank statements, etc.).

## Quick Start

```bash
# Setup
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Run
python src/main.py
```

## Features

- **Multi-format support**: Process both images and PDF documents
- **Multi-model support**: Load different models based on document type for better accuracy
- **Professional architecture**: Clean separation between business logic and UI
- **Streamlit interface**: Simple, intuitive web interface
- **Extensible**: Easy to add new document types and models

## Documentation

- [Getting Started](docs/GETTING_STARTED.md) - Detailed setup and usage
- [Architecture](docs/ARCHITECTURE.md) - Project structure and design
- [Training](docs/TRAINING.md) - Fine-tuning models for custom document types

## Supported Document Types

- **Invoices**: Extract invoice numbers, dates, amounts, line items
- **Healthcare Forms**: Extract patient information, diagnoses, treatment codes
- **Bank Statements**: Extract account numbers, transactions, balances
- **General**: Works with any document

## Supported File Formats

- **Images**: JPG, JPEG, PNG, PDF, TIFF
- **Documents**: PDF (automatically converted to images and processed page-by-page)