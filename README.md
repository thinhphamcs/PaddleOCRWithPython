# PaddleOCR
Learning and developing an Optical Character Recognition (OCR) system using PaddleOCR and Python

## Python Commands

```bash
python3 -m venv .venv
```

```bash
source .venv/bin/activate
```

```bash
pip install -r requirements.txt
```

```bash
python src/main.py
```

## Repository layout

```
PaddleOCRWithPython/
├── .venv/
├── LICENSE                     # Apache 2.0
├── README.md
├── requirements.txt
├── models/
├── data/
│   ├── input                   # Images to be scan
│   └── output                  # Save resutls (JSON/TXT)
└── src/
    └── main.py
```