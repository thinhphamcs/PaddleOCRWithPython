import sys
from pathlib import Path
import os
import tempfile
import re
import streamlit as st
import pandas as pd
from pdf2image import convert_from_path
from PIL import Image
import pytesseract
from ultralytics import YOLO
from dotenv import load_dotenv

load_dotenv()

# Initialize Model
MODEL_PATH = os.getenv("MODEL_OUTPUT_PATH")
if not MODEL_PATH:
    st.error("MODEL_OUTPUT_PATH not found in .env file.")
    st.stop()

model = YOLO(MODEL_PATH)

def parse_transaction_line(line):
    """
    Highly flexible parser for Transactions and Daily Ledgers.
    Cleans noise and extracts Date, Description, and Amount.
    """
    # 1. Clean the line: remove leading/trailing dashes, pipes, or whitespace
    clean_line = line.strip().strip("-| ").strip()
    
    if not clean_line:
        return None

    # 2. Extract Amount: Look for the last number/decimal in the string
    # Matches numbers like 113.00, 21,001.87, or -246.00
    amount_match = re.findall(r"(-?[\d,]+\.\d{2})", clean_line)
    amount = amount_match[-1] if amount_match else ""
    
    # 3. Extract Date: Look for MM/DD/YY or MM/DD at the start
    date_match = re.search(r"^(\d{2}/\d{2}(?:/\d{2,4})?)", clean_line)
    date = date_match.group(1) if date_match else ""
    
    # 4. Extract Description: Everything between Date and Amount
    description = clean_line
    if date:
        description = description.replace(date, "", 1)
    if amount:
        # Replace the last occurrence of the amount to avoid messing up description
        description = description.rsplit(amount, 1)[0]
    
    # Clean up the description
    description = description.strip().strip("-| ").strip()

    return {
        "Date": date if date else "N/A",
        "Description": description if description else "---",
        "Amount": f"${amount}" if amount else "N/A"
    }

def process_items(image):
    results = model.predict(image, conf=0.30, verbose=False)
    page_data = []
    
    if len(results) > 0 and results[0].boxes:
        boxes = results[0].boxes
        best_detections = {}
        multi_detections = {"Account_Transactions": [], "Account_Image": []}

        for box in boxes:
            label = model.names[int(box.cls[0])]
            conf = float(box.conf[0])
            if label.lower() == "ignore": continue
            
            if label in ["Account_Header", "Account_Summary"]:
                if label not in best_detections or conf > float(best_detections[label].conf[0]):
                    best_detections[label] = box
            elif label in multi_detections:
                multi_detections[label].append(box)

        for label in ["Account_Header", "Account_Summary"]:
            if label in best_detections:
                box = best_detections[label]
                coords = box.xyxy[0].tolist()
                crop = image.crop((coords[0], coords[1], coords[2], coords[3]))
                text = pytesseract.image_to_string(crop, lang="eng").strip()
                if text:
                    page_data.append({"label": label, "type": "text", "content": text})

        if multi_detections["Account_Transactions"]:
            sorted_trans = sorted(multi_detections["Account_Transactions"], key=lambda b: b.xyxy[0][1])
            for box in sorted_trans:
                coords = box.xyxy[0].tolist()
                crop = image.crop((coords[0], coords[1], coords[2], coords[3]))
                # PSM 6 is vital for keeping row structure
                text = pytesseract.image_to_string(crop, lang="eng", config='--psm 6').strip()
                if text:
                    page_data.append({"label": "Account_Transactions", "type": "text", "content": text})

        for box in multi_detections["Account_Image"]:
            coords = box.xyxy[0].tolist()
            crop = image.crop((coords[0], coords[1], coords[2], coords[3]))
            page_data.append({"label": "Account_Image", "type": "image", "content": crop})

    return page_data

def display_results(items):
    # Metadata
    metadata = [it for it in items if it["label"] in ["Account_Header", "Account_Summary"]]
    if metadata:
        summary_rows = [{"Field": it["label"].replace("_", " "), "Information": it["content"].replace("\n", " ")} for it in metadata]
        st.dataframe(pd.DataFrame(summary_rows), use_container_width=True, hide_index=True)

    # Transactions & Ledgers
    transactions = [it for it in items if it["label"] == "Account_Transactions"]
    if transactions:
        parsed_data = []
        for trans_block in transactions:
            lines = [line.strip() for line in trans_block["content"].split("\n") if line.strip()]
            for line in lines:
                res = parse_transaction_line(line)
                if res:
                    parsed_data.append(res)
        
        if parsed_data:
            st.markdown("### Transaction Details")
            st.dataframe(pd.DataFrame(parsed_data), use_container_width=True, hide_index=True)

    # Images
    images = [it for it in items if it["type"] == "image"]
    if images:
        for img in images:
            st.image(img["content"], use_column_width=True)

def main():
    st.set_page_config(page_title="OCR Parser", layout="wide")
    st.markdown("<style>[data-testid='stHeader'] {display:none;} .block-container {padding-top: 2rem;} [data-testid='stElementToolbar'] { display: none; }</style>", unsafe_allow_html=True)

    uploaded_file = st.file_uploader("Upload", type=["pdf", "png", "jpg", "tiff"], label_visibility="collapsed")

    if uploaded_file:
        file_ext = Path(uploaded_file.name).suffix.lower()
        if file_ext == ".pdf":
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                tmp.write(uploaded_file.getbuffer())
                tmp_path = tmp.name
            with st.spinner("Processing PDF..."):
                images = convert_from_path(tmp_path, dpi=300) # Bumped to 300 for Ledger accuracy
                for i, img in enumerate(images):
                    with st.expander(f"Page {i+1}", expanded=True):
                        page_items = process_items(img)
                        display_results(page_items)
            os.unlink(tmp_path)
        else:
            with st.spinner("Processing Image..."):
                img = Image.open(uploaded_file).convert("RGB")
                page_items = process_items(img)
                display_results(page_items)

if __name__ == "__main__":
    main()