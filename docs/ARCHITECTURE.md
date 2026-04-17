# Project Architecture

## Overview

This project follows a **three-tier architecture** with clean separation of concerns:

```
User Interface (Streamlit)
        ↓
    Business Logic (OCREngine)
        ↓
    PaddleOCR Models
```

## Directory Structure

```
PaddleOCRWithPython/
├── .venv/                      # Python virtual environment
├── LICENSE                     # Apache 2.0
├── README.md                   # Project overview and quick start
├── requirements.txt            # Python dependencies
├── docs/                       # Documentation
│   ├── GETTING_STARTED.md      # Detailed setup guide
│   ├── ARCHITECTURE.md         # This file
│   └── TRAINING.md             # Fine-tuning guide
├── models/                     # Fine-tuned models for different document types
│   ├── invoice/               # Invoice model
│   ├── healthcare/            # Healthcare form model
│   └── bank_statement/        # Bank statement model
├── data/
│   ├── input/                 # Images to scan
│   └── output/                # Save results (JSON/TXT)
└── src/
    ├── main.py                # Entry point - launches Streamlit UI
    ├── core/                  # Business logic layer
    │   ├── __init__.py
    │   └── ocr.py             # OCREngine class - PaddleOCR wrapper
    └── ui/                    # Presentation layer
        ├── __init__.py
        └── app.py             # Streamlit web interface
```

### `src/core/`
**Business Logic Layer**
- `ocr.py` - OCREngine class that:
  - Manages PaddleOCR initialization
  - Supports multiple document types
  - Handles image processing
  - Returns structured OCR results

### `src/ui/`
**Presentation Layer**
- `app.py` - Streamlit web interface that:
  - Displays document type selector
  - Handles file upload
  - Formats and displays results
  - Manages user session state

### `models/`
**Fine-tuned Model Directory**
- `models/invoice/` - Invoice-specific model
- `models/healthcare/` - Healthcare form model
- `models/bank_statement/` - Bank statement model

Each folder can contain fine-tuned model weights for specialized accuracy.

### `data/`
**Input/Output Directory**
- `data/input/` - Store sample images for testing
- `data/output/` - Save OCR results and processed data

## Design Patterns

### 1. Single Responsibility
- `ocr.py` handles ONLY OCR operations
- `app.py` handles ONLY UI logic
- `main.py` handles ONLY application entry

### 2. Session State Management
Streamlit session state stores:
- Current document type
- Active OCR engine instance
- Prevents re-initialization on every interaction

### 3. Model Selection
The `OCREngine.__init__()` accepts a `doc_type` parameter to load the appropriate model:
```python
ocr = OCREngine(doc_type='invoice', lang='en')
```

## Data Flow

```
1. User uploads image
   ↓
2. App converts image to numpy array
   ↓
3. OCREngine.extract_text_from_array()
   ↓
4. PaddleOCR processes image
   ↓
5. Results formatted by document type
   ↓
6. Display in Streamlit UI
```

## Extensibility

To add a new document type:

1. Create folder: `models/new_type/`
2. Add `.gitkeep` file
3. Update `TRAINING.md` with fine-tuning instructions
4. Update UI dropdown in `src/ui/app.py`
5. Add model weights when ready

That's it! The engine automatically supports the new type.
