from paddleocr import PaddleOCR

ocr = PaddleOCR(use_angle_cls=True, lang='en')
print("--- PaddleOCR initialzied Successfully ---")