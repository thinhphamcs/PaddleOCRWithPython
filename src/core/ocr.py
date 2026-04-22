import cv2
import os
import numpy as np
from pathlib import Path
from paddleocr import PaddleOCR
from pdf2image import convert_from_path
from typing import List, Dict, Tuple


class OCREngine:
    """Handles OCR operations using PaddleOCR with support for multiple document types."""
    
    def __init__(self, doc_type: str = 'general', lang: str = 'en'):
        """
        Initialize the OCR engine.
        
        Args:
            doc_type: Document type ('general', 'invoice', 'healthcare', 'bank_statement')
            lang: Language code (default: 'en' for English)
        """
        self.doc_type = doc_type
        self.ocr = PaddleOCR(lang=lang)
        print(f"--- PaddleOCR initialized for {doc_type} documents ---")
    
    def extract_text(self, image_path: str) -> List[Dict]:
        """
        Extract text from an image file.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            List of dictionaries containing OCR results with text, confidence, and bounding box
        """
        result = self.ocr.predict(image_path)
        
        # Parse results into a more usable format
        extracted_data = []
        if result and 'rec_texts' in result[0]:
            for i, text in enumerate(result[0]['rec_texts']):
                extracted_data.append({
                    'text': text,
                    'confidence': result[0]['rec_scores'][i] if i < len(result[0]['rec_scores']) else 0.0,
                    'bounding_box': result[0]['rec_polys'][i] if i < len(result[0]['rec_polys']) else []
                })
        
        return extracted_data
    
    def extract_text_from_array(self, image_array) -> List[Dict]:
        """
        Extract text from a numpy array (image).
        
        Args:
            image_array: Numpy array representing an image
            
        Returns:
            List of dictionaries containing OCR results
        """
        result = self.ocr.predict(image_array)
        
        extracted_data = []
        if result and 'rec_texts' in result[0]:
            for i, text in enumerate(result[0]['rec_texts']):
                extracted_data.append({
                    'text': text,
                    'confidence': result[0]['rec_scores'][i] if i < len(result[0]['rec_scores']) else 0.0,
                    'bounding_box': result[0]['rec_polys'][i] if i < len(result[0]['rec_polys']) else []
                })
        
        return extracted_data
    
    def get_full_text(self, image_path: str) -> str:
        """
        Get all extracted text from an image as a single string.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Full text extracted from the image
        """
        data = self.extract_text(image_path)
        return '\n'.join([item['text'] for item in data])
    
