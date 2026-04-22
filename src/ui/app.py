import sys
from pathlib import Path
import io
import tempfile

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
    if 'pdf_pages' not in st.session_state:
        st.session_state.pdf_pages = []
    if 'pdf_path' not in st.session_state:
        st.session_state.pdf_path = None
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 0


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


def process_single_pdf_page(pdf_path, page_num, ocr_engine):
    """Process a single PDF page to save memory."""
    try:
        from pdf2image import convert_from_path
        
        # Convert only this specific page
        images = convert_from_path(pdf_path, dpi=150, first_page=page_num, last_page=page_num)
        
        if not images:
            return None
            
        image = images[0]
        
        # Convert PIL image to opencv format
        image_array = np.array(image)
        
        # Resize if too large to prevent memory issues
        height, width = image_array.shape[:2]
        max_dimension = 1500  # Smaller max dimension for memory safety
        
        if width > max_dimension or height > max_dimension:
            scale = min(max_dimension / width, max_dimension / height)
            new_width = int(width * scale)
            new_height = int(height * scale)
            image_array = cv2.resize(image_array, (new_width, new_height), interpolation=cv2.INTER_AREA)
        
        image_cv = cv2.cvtColor(image_array, cv2.COLOR_RGB2BGR)
        
        # Run OCR on the page
        result = ocr_engine.ocr.predict(image_cv)
        
        # Parse results
        page_data = {
            'page': page_num,
            'text_items': []
        }
        
        if result and 'rec_texts' in result[0]:
            for i, text in enumerate(result[0]['rec_texts']):
                page_data['text_items'].append({
                    'text': text,
                    'confidence': result[0]['rec_scores'][i] if i < len(result[0]['rec_scores']) else 0.0,
                    'bounding_box': result[0]['rec_polys'][i] if i < len(result[0]['rec_polys']) else []
                })
        
        return page_data
        
    except Exception as e:
        print(f"Error processing page {page_num}: {str(e)}")
        return None


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
    
    # Input section - unified uploader for images and PDFs
    uploaded_file = st.file_uploader(
        "Drop your document here (images or PDF)",
        type=["jpg", "jpeg", "png", "bmp", "gif", "pdf"],
        label_visibility="collapsed"
    )
    
    if uploaded_file:
        file_extension = Path(uploaded_file.name).suffix.lower()
        
        # Handle PDF files
        if file_extension == ".pdf":
            # Check file size (limit to 25MB for safety)
            file_size_mb = len(uploaded_file.getbuffer()) / (1024 * 1024)
            if file_size_mb > 25:
                st.error(f"PDF file is too large ({file_size_mb:.1f}MB). Maximum allowed size is 25MB.")
                st.stop()
            
            # Save uploaded PDF to temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
                tmp_file.write(uploaded_file.getbuffer())
                tmp_path = tmp_file.name
            
            # Store PDF path in session state
            if st.session_state.pdf_path != tmp_path:
                st.session_state.pdf_path = tmp_path
                st.session_state.pdf_pages = []
            
            try:
                # Get PDF info
                from pdf2image import pdfinfo_from_path
                info = pdfinfo_from_path(tmp_path)
                total_pages = min(info["Pages"], 10)  # Limit to 10 pages max
                
                st.info(f"📄 PDF loaded: {total_pages} pages detected (max 10 pages supported)")
                
                # Page selector
                selected_page = st.selectbox(
                    "Select page to process:",
                    options=range(1, total_pages + 1),
                    format_func=lambda x: f"Page {x}"
                )
                
                # Process page if not already processed
                if selected_page > len(st.session_state.pdf_pages) or st.session_state.pdf_pages[selected_page - 1] is None:
                    with st.spinner(f"Processing page {selected_page}..."):
                        page_data = process_single_pdf_page(tmp_path, selected_page, st.session_state.ocr_engine)
                        
                        # Extend list if needed
                        while len(st.session_state.pdf_pages) < selected_page:
                            st.session_state.pdf_pages.append(None)
                        
                        st.session_state.pdf_pages[selected_page - 1] = page_data
                
                # Display results
                if selected_page <= len(st.session_state.pdf_pages) and st.session_state.pdf_pages[selected_page - 1]:
                    current_page_data = st.session_state.pdf_pages[selected_page - 1]
                    formatted = format_ocr_results(current_page_data['text_items'])
                    
                    st.success(f"✓ Page {selected_page} processed")
                    
                    st.markdown(
                        '<div style="max-height:70vh; overflow:auto; border-radius: 12px; background: rgba(255,255,255,0.015); padding: 16px; box-sizing:border-box;">',
                        unsafe_allow_html=True
                    )
                    
                    if formatted.strip():
                        st.markdown(f"<h3 style='margin: 0 0 0.5rem; padding: 0;'>📄 Page {selected_page} - Extracted Text</h3>", unsafe_allow_html=True)
                        st.markdown(formatted, unsafe_allow_html=True)
                        st.caption(f"{len(current_page_data['text_items'])} OCR lines detected | Type: {doc_type}")
                    else:
                        st.info("No text detected on this page")
                    
                    st.markdown('</div>', unsafe_allow_html=True)
                else:
                    st.error(f"Failed to process page {selected_page}")
                
            except Exception as e:
                st.error(f"Error processing PDF: {str(e)}")
        
        # Handle image files
        else:
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
