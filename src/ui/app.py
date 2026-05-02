import sys
from pathlib import Path
import os
import tempfile
import streamlit as st
import pandas as pd # Added pandas for cleaner table rendering
from pdf2image import convert_from_path
from PIL import Image
import pytesseract
from ultralytics import YOLO

# Load the YOLO model
MODEL_PATH = "/home/guess/github_repos/PaddleOCRWithPython/data/output/best.pt"
model = YOLO(MODEL_PATH)

def process_items(image):
    """Detects regions and performs OCR."""
    results = model.predict(image, conf=0.30, verbose=False)
    page_data = []
    
    if len(results) > 0 and results[0].boxes:
        boxes = results[0].boxes
        # Sort top-to-bottom
        sorted_indices = boxes.xyxy[:, 1].sort()[1]
        
        for idx in sorted_indices:
            box = boxes[idx]
            label = model.names[int(box.cls[0])]
            if label.lower() == "ignore": continue
            
            coords = box.xyxy[0].tolist()
            crop = image.crop((coords[0], coords[1], coords[2], coords[3]))
            
            if label == "Account_Image":
                page_data.append({"label": label, "type": "image", "content": crop})
            else:
                text = pytesseract.image_to_string(crop, lang="eng").strip()
                if text:
                    page_data.append({"label": label, "type": "text", "content": text})
    return page_data

def display_results(items):
    """Cleanest display: No bold markdown tags, just raw data in tables."""
    
    # 1. Summary Section (Header/Summary)
    metadata = [it for it in items if it["label"] in ["Account_Header", "Account_Summary"]]
    if metadata:
        summary_rows = []
        for it in metadata:
            label_clean = it['label'].replace('_', ' ')
            text_clean = it['content'].replace("\n", " ")
            summary_rows.append({"Field": label_clean, "Information": text_clean})
        
        # Using DataFrame for a more professional look
        st.dataframe(pd.DataFrame(summary_rows), use_container_width=True, hide_index=True)

    # 2. Transaction Records
    transactions = [it for it in items if it["label"] == "Account_Transactions"]
    if transactions:
        all_lines = []
        for trans_block in transactions:
            lines = [line.strip() for line in trans_block["content"].split('\n') if line.strip()]
            all_lines.extend(lines)
        
        if all_lines:
            # Display transactions as a simple table
            st.dataframe(pd.DataFrame(all_lines, columns=["Transactions"]), use_container_width=True, hide_index=True)

    # 3. Images
    images = [it for it in items if it["type"] == "image"]
    if images:
        for img in images:
            st.image(img["content"], use_column_width=True)

def main():
    # Setting the theme to wide for better table visibility
    st.set_page_config(page_title="OCR Parser", layout="wide")

    # Minimalist CSS
    st.markdown("""
        <style>
        [data-testid="stHeader"] {display:none;}
        .block-container {padding-top: 2rem;}
        </style>
        """, unsafe_allow_html=True)

    uploaded_file = st.file_uploader("Upload", type=["pdf", "png", "jpg"], label_visibility="collapsed")

    if uploaded_file:
        file_ext = Path(uploaded_file.name).suffix.lower()
        
        if file_ext == ".pdf":
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                tmp.write(uploaded_file.getbuffer())
                tmp_path = tmp.name
            
            with st.spinner("Processing..."):
                images = convert_from_path(tmp_path, dpi=150)
                for i, img in enumerate(images):
                    with st.expander(f"Page {i+1}", expanded=True):
                        page_items = process_items(img)
                        display_results(page_items)
            os.unlink(tmp_path)
        else:
            with st.spinner("Processing..."):
                img = Image.open(uploaded_file).convert("RGB")
                page_items = process_items(img)
                display_results(page_items)

if __name__ == "__main__":
    main()