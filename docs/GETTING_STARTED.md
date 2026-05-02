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

### 4. Adding `.env` to home directory
```bash
# Environment variables for model training
MODEL_TRAIN_DATA= #Path to data.yaml file
MODEL_TRAIN_EPOCHS= #100 or higher
MODEL_TRAIN_IMGSZ= #640 or higher
MODEL_TRAIN_DEVICE= #cpu or gpu
MODEL_TRAIN_WORKERS= #2 or more
MODEL_TRAIN_BATCH= #4 or more
MODEL_TRAIN_NAME= #Model Name
MODEL_TRAIN_EXIST_OK= #True or False

# Environment variable for model output path
MODEL_OUTPUT_PATH= #Path to the output .pt file
```

### 5. Tesseract requirement

The application will not run without the system PATH, so run the below command
```bash
sudo apt install tesseract-ocr
```

## Running the Application

Start the OCR web interface:
```bash
python src/main.py
```

The application will launch at `http://localhost:8501`

## Usage

1. More document types will be work on in the future:
   - `general` - Future enhancement
   - `invoice` - Future enhancement
   - `healthcare` - Future enhancement
   - `bank_statement` - Currently working on BoA

2. **Upload Image**: Drag and drop or select an image file (JPG, PNG, PDF, TIF)

3. **View Results**: The extracted text appears automatically
