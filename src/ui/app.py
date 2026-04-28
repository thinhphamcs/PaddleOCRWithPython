import sys
from pathlib import Path
import io
import os
import tempfile
import streamlit as st
from src.core.ocr import OCREngine
from pdf2image import convert_from_path
from PIL import Image
import pytesseract
from ultralytics import YOLO

sys.path.insert(0, str(Path(__file__).parent.parent))

model = YOLO("/home/guess/github_repos/PaddleOCRWithPython/data/output/bank_statement_ocr_v1.pt")

def initialize_session():
    """Initialize Streamlit session state."""
    if "ocr_engine" not in st.session_state:
        st.session_state.ocr_engine = None
    if "doc_type" not in st.session_state:
        st.session_state.doc_type = "general"
    if "pdf_pages" not in st.session_state:
        st.session_state.pdf_pages = []
    if "pdf_path" not in st.session_state:
        st.session_state.pdf_path = None
    if "current_page" not in st.session_state:
        st.session_state.current_page = 0


def format_ocr_results(results):
    lines = [item["text"].strip() for item in results if item["text"].strip()]
    pairs = []
    other = []
    for line in lines:
        if ":" in line and len(line.split(":", 1)[0]) <= 30:
            key, value = line.split(":", 1)
            pairs.append((key.strip(), value.strip()))
        else:
            other.append(line)

    def is_table(lines):
        headers = [line for line in lines if ":" in line]
        return len(headers) > 0 and all(
            len(header.split(":")) == 2 for header in headers
        )

    if is_table(other):
        table = "| Field | Value |\n| --- | --- |\n"
        for key, value in pairs:
            table += f"| **{key}** | {value} |\n"
        return table
    else:
        return "\n".join(lines)
    # if pairs:
    #     table = "| Field | Value |\n| --- | --- |\n"
    #     for key, value in pairs:
    #         table += f"| **{key}** | {value} |\n"
    #     if other:
    #         table += "\n**Other text**\n"
    #         table += "\n".join(other)
    #     return table
    # return "\n".join(lines)


# def process_all_pages_in_pdf(pdf_path):
#     """This function is for processing images and save to my local for model training."""
#     try:
#         images = convert_from_path(pdf_path, dpi=150)
#         if not images:
#             print(f"No images found for the document")
#             return None
#         output_dir = Path("output_images")
#         if not output_dir.exists():
#             output_dir.mkdir(parents=True)
#         ocr_results = []
#         for i, image in enumerate(images):
#             # tif_image = Image.open(io.BytesIO(image.tobytes()))
#             text = pytesseract.image_to_string(image, lang="eng")
#             ocr_results.append(
#                 {
#                     "page_num": i + 1,
#                     "text_items": [
#                         {"text": line.strip()}
#                         for line in text.split("\n")
#                         if line.strip()
#                     ],
#                 }
#             )
#             # Save the image as a JPEG
#             output_path = output_dir / f"page_{i+1}.jpg"
#             image.save(output_path, format="JPEG")
#         return ocr_results
#     except Exception as e:
#         print(f"Error processing the document:{str(e)}")
#         raise


# def process_all_pages_in_pdf(pdf_path):
#     """Backup code"""
#     try:
#         images = convert_from_path(pdf_path, dpi=150)
#         if not images:
#             print(f"No images found for the document")
#             return None
#         ocr_results = []
#         for i, image in enumerate(images):
#             text = pytesseract.image_to_string(image, lang="eng")
#             ocr_results.append(
#                 {
#                     "page_num": i + 1,
#                     "text_items": [
#                         {"text": line.strip()}
#                         for line in text.split("\n")
#                         if line.strip()
#                     ],
#                 }
#             )
#         return ocr_results
#     except Exception as e:
#         print(f"Error processing the document:{str(e)}")
#         raise
    
def process_all_pages_in_pdf(pdf_path):
    """Process all pages in a PDF and extract text using pytesseract."""
    try:
        images = convert_from_path(pdf_path, dpi=150)
        if not images:
            print(f"No images found for the document")
            return None
        ocr_results = []
        for i, image in enumerate(images):
            results = model.predict(image, conf=0.25, iou=0.4)
            results[0].save(filename=f"test_page_{i+1}.jpg")
            page_text_items = []
            
            if len(results[0].boxes) == 0:
                page_text_items.append({"text": "No text detected"})
            else:
                for result in results:
                    for box in result.boxes:
                        
                        class_id = int(box.cls[0])
                        if class_id == 11 or class_id == 12:
                            page_text_items.append({"text": "This page left intentionally blank."})
                        else:
                            coords = box.xyxy[0].tolist()
                            cropped_image = image.crop((coords[0], coords[1], coords[2], coords[3]))
                            text = pytesseract.image_to_string(cropped_image, lang="eng")
                            for line in text.split("\n"):
                                if line.strip():
                                    page_text_items.append({"text": line.strip()})
            ocr_results.append(
                {
                    "page_num": i + 1,
                    "text_items": page_text_items
                }
            )
        return ocr_results
    except Exception as e:
        print(f"Error processing the document:{str(e)}")
        raise


def main():
    """Main Streamlit application."""
    st.set_page_config(page_title="OCR", layout="wide")
    initialize_session()
    doc_type = st.selectbox(
        "Select document type",
        ["general", "invoice", "healthcare", "bank_statement"],
        index=0,
    )
    if doc_type != st.session_state.doc_type or st.session_state.ocr_engine is None:
        st.session_state.doc_type = doc_type
        st.session_state.ocr_engine = OCREngine(doc_type=doc_type, lang="en")
    uploaded_file = st.file_uploader(
        "Drop your document here (images or PDF)",
        type=["jpeg", "png", "pdf", "tiff"],
        label_visibility="collapsed",
    )
    if uploaded_file:
        file_extension = Path(uploaded_file.name).suffix.lower()
        if file_extension == ".pdf":
            file_size_mb = len(uploaded_file.getbuffer()) / (1024 * 1024)
            if file_size_mb > 25:
                st.error(
                    f"PDF file is too large ({file_size_mb:.1f}MB). Maximum allowed size is 25MB."
                )
                st.stop()
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
                tmp_file.write(uploaded_file.getbuffer())
                tmp_path = tmp_file.name
            if st.session_state.pdf_path != tmp_path:
                st.session_state.pdf_path = tmp_path
                st.session_state.pdf_pages = []
            try:
                from pdf2image import pdfinfo_from_path
                info = pdfinfo_from_path(tmp_path)
                total_pages = min(info["Pages"], 10)
                st.info(
                    f"📄 PDF loaded: {total_pages} pages detected (max 10 pages supported)"
                )
                ocr_results = process_all_pages_in_pdf(tmp_path)
                for i, result in enumerate(ocr_results):
                    st.success(f"✓ Page {result['page_num']} processed")
                    formatted = format_ocr_results(result["text_items"])
                    st.markdown(formatted)
            except Exception as e:
                st.error(f"Error processing PDF: {str(e)}")
        else:
            image = Image.open(uploaded_file)
            preview_image = image.copy()
            preview_image.thumbnail((1200, 900), Image.LANCZOS)
            with st.spinner("Processing..."):
                text = pytesseract.image_to_string(image, lang="eng")
                formatted = format_ocr_results(
                    [
                        {"text": line.strip()}
                        for line in text.split("\n")
                        if line.strip()
                    ]
                )
                st.markdown(formatted)


if __name__ == "__main__":
    main()
