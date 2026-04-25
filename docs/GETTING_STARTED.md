# Getting Started

## Installation

### 1. Clone the repository
```bash
git clone <repo-url>
cd PytesseractWithPython
```

### 2. Create virtual environment
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

## Running the Application

Start the OCR web interface:
```bash
python src/main.py
```

The application will launch at `http://localhost:8501`

## Usage

1. **Select Document Type**: Choose from the dropdown menu:
   - `general` - Standard OCR for any document
   - `invoice` - Optimized for invoices
   - `healthcare` - Optimized for healthcare forms
   - `bank_statement` - Optimized for bank statements

2. **Upload Image**: Drag and drop or select an image file (JPG, PNG, BMP, GIF)

3. **View Results**: The extracted text appears automatically on the right side

## Supported Document Types

- **Invoices**: Extract invoice numbers, dates, amounts, line items
- **Healthcare Forms**: Extract patient information, diagnoses, treatment codes
- **Bank Statements**: Extract account numbers, transactions, balances
- **General**: Works with any document

## Output

The OCR results are displayed with:
- Extracted text formatted by document type
- Confidence scores for each line
- Line count statistics
