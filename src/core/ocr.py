import cv2
import os
import numpy as np
from pathlib import Path
from typing import List, Dict, Tuple
import pytesseract


class OCREngine:
    """Handles OCR operations using pytesseract with support for multiple document types."""
    def __init__(self, doc_type: str = 'general', lang: str = 'en'):
        self.doc_type = doc_type
        print(f"--- pytesseract initialized for {doc_type} documents ---")
    
    def extract_text(self, image_path: str) -> List[Dict]:
        result = pytesseract.image_to_data(Image.open(image_path), output_type=pytesseract.Output.DICT)
        extracted_data = []
        for i in range(len(result['text'])):
            extracted_data.append({
                'text': result['text'][i],
                'confidence': result['conf'][i] if i < len(result['conf']) else 0.0,
                'bounding_box': [result['left'][i], 
                result['top'][i], result['width'][i],
                result['height'][i]] if i < len(result['width']) else []
            })
        return extracted_data
    
    def extract_text_from_array(self, image_array) -> List[Dict]:
        result = pytesseract.image_to_data(Image.fromarray(image_array), output_type=pytesseract.Output.DICT)
        extracted_data = []
        for i in range(len(result['text'])):
            extracted_data.append({
                'text': result['text'][i],
                'confidence': result['conf'][i] if i < len(result['conf']) else 0.0,
                'bounding_box': [result['left'][i],
                result['top'][i], result['width'][i],
                result['height'][i]] if i < len(result['width']) else []
            })        
        return extracted_data
    
    def get_full_text(self, image_path: str) -> str:
        data = self.extract_text(image_path)
        return '\n'.join([item['text'] for item in data])
        