"""
OCR service using EasyOCR
"""
import easyocr
from typing import List, Tuple
import numpy as np
from app.core.config import settings
from app.models.product import OCRResult, BoundingBox
from app.core.logging import logger


class OCRService:
    """Handles OCR operations using EasyOCR"""
    
    def __init__(self):
        self.reader = None
        self._initialize_reader()
    
    def _initialize_reader(self):
        """Initialize EasyOCR reader"""
        try:
            logger.info(f"Initializing EasyOCR with languages: {settings.OCR_LANGUAGES}")
            self.reader = easyocr.Reader(
                settings.OCR_LANGUAGES,
                gpu=settings.OCR_GPU
            )
            logger.info("EasyOCR initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize EasyOCR: {e}")
            raise
    
    def extract_text(self, image: np.ndarray) -> List[OCRResult]:
        """
        Extract text from image using OCR
        
        Args:
            image: Preprocessed image as numpy array
            
        Returns:
            List of OCR results with bounding boxes and text
        """
        if self.reader is None:
            raise RuntimeError("OCR reader not initialized")
        
        try:
            # Perform OCR
            results = self.reader.readtext(image)
            
            # Convert to OCRResult objects
            ocr_results = []
            for bbox, text, confidence in results:
                # Skip low confidence results
                if confidence < settings.OCR_CONFIDENCE_THRESHOLD:
                    continue
                
                # Create bounding box
                bounding_box = BoundingBox(
                    top_left=tuple(map(int, bbox[0])),
                    top_right=tuple(map(int, bbox[1])),
                    bottom_right=tuple(map(int, bbox[2])),
                    bottom_left=tuple(map(int, bbox[3]))
                )
                
                ocr_result = OCRResult(
                    bbox=bounding_box,
                    text=text.strip(),
                    confidence=confidence
                )
                
                ocr_results.append(ocr_result)
            
            logger.info(f"Extracted {len(ocr_results)} text regions from image")
            return ocr_results
            
        except Exception as e:
            logger.error(f"OCR extraction failed: {e}")
            raise