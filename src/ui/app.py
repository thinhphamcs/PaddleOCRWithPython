import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st
import cv2
import numpy as np
from PIL import Image
from core.ocr import OCREngine


def initialize_session():
    """Initialize Streamlit session state."""
    if 'ocr_engine' not in st.session_state:
        st.session_state.ocr_engine = None
    if 'doc_type' not in st.session_state:
        st.session_state.doc_type = 'general'


def format_ocr_results(results):
    lines = [item['text'].strip() for item in results if item['text'].strip()]
    pairs = []
    other = []

    for line in lines:
        if ':' in line and len(line.split(':', 1)[0]) <= 30:
            key, value = line.split(':', 1)
            pairs.append((key.strip(), value.strip()))
        else:
            other.append(line)

    if pairs:
        table = "| Field | Value |\n| --- | --- |\n"
        for key, value in pairs:
            table += f"| **{key}** | {value} |\n"
        if other:
            table += "\n**Other text**\n"
            table += "\n".join(other)
        return table

    return "\n".join(lines)


def main():
    """Main Streamlit application."""
    st.set_page_config(
        page_title="OCR",
        layout="wide"
    )
    
    initialize_session()
    
    # Document type selector
    doc_type = st.selectbox(
        "Select document type",
        ["general", "invoice", "healthcare", "bank_statement"],
        index=0
    )
    
    # Initialize OCR engine if document type changed
    if doc_type != st.session_state.doc_type or st.session_state.ocr_engine is None:
        st.session_state.doc_type = doc_type
        st.session_state.ocr_engine = OCREngine(doc_type=doc_type, lang='en')
    
    # Input section
    uploaded_file = st.file_uploader(
        "Drop your image here",
        type=["jpg", "jpeg", "png", "bmp", "gif"],
        label_visibility="collapsed"
    )
    
    if uploaded_file:
        image = Image.open(uploaded_file)
        preview_image = image.copy()
        preview_image.thumbnail((1200, 900), Image.LANCZOS)
        
        # Process automatically
        with st.spinner("Processing..."):
            image_array = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            results = st.session_state.ocr_engine.extract_text_from_array(image_array)
        
        # Two columns: Image preview (60%) | Results (40%) with gap
        col1, col2 = st.columns([6, 4], gap="medium")
        
        with col1:
            st.markdown(
                '<div style="max-height:70vh; overflow:auto; padding: 4px; border-radius: 12px; box-sizing:border-box;">',
                unsafe_allow_html=True
            )
            st.image(preview_image, use_column_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            formatted = format_ocr_results(results)
            
            st.markdown(
                '<div style="max-height:70vh; overflow:auto; border-radius: 12px; background: rgba(255,255,255,0.015); box-sizing:border-box;">',
                unsafe_allow_html=True
            )
            
            if formatted.strip():
                st.markdown("<h3 style='margin: 0 0 0.5rem; padding: 0;'>📝 Extracted Text</h3>", unsafe_allow_html=True)
                st.markdown(formatted, unsafe_allow_html=True)
                st.caption(f"{len(results)} OCR lines detected | Type: {doc_type}")
            else:
                st.info("No text detected in the image")
            
            st.markdown('</div>', unsafe_allow_html=True)


if __name__ == "__main__":
    main()
