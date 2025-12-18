"""
OCR service using EasyOCR for text extraction from images.

This service handles:
- OCR initialization and configuration
- Text extraction from preprocessed images
- Bounding box detection
- Confidence filtering
"""
import easyocr
from typing import List, Optional
import numpy as np
from app.core.config import settings
from app.core.logging import app_logger as logger
from app.models.product import OCRResult, BoundingBox


class OCRService:
    """Handles OCR operations using EasyOCR"""
    
    def __init__(self, languages: Optional[List[str]] = None, gpu: Optional[bool] = None):
        """
        Initialize OCR service.
        
        Args:
            languages: List of language codes (default from settings)
            gpu: Whether to use GPU (default from settings)
        """
        self.languages = languages or settings.OCR_LANGUAGES
        self.gpu = gpu if gpu is not None else settings.OCR_GPU
        self.reader = None
        self._initialize_reader()
    
    def _initialize_reader(self):
        """Initialize EasyOCR reader"""
        try:
            logger.info(f"Initializing EasyOCR - Languages: {self.languages}, GPU: {self.gpu}")
            
            self.reader = easyocr.Reader(
                self.languages,
                gpu=self.gpu,
                model_storage_directory=settings.OCR_MODEL_STORAGE_DIRECTORY,
                download_enabled=True
            )
            
            logger.info("EasyOCR initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize EasyOCR: {e}")
            raise RuntimeError(f"OCR initialization failed: {e}")
    
    def extract_text(
        self,
        image: np.ndarray,
        confidence_threshold: Optional[float] = None
    ) -> List[OCRResult]:
        """
        Extract text from image using OCR.
        
        Args:
            image: Preprocessed image as numpy array
            confidence_threshold: Minimum confidence score (default from settings)
            
        Returns:
            List of OCR results with bounding boxes and text
            
        Raises:
            RuntimeError: If OCR reader is not initialized
        """
        if self.reader is None:
            raise RuntimeError("OCR reader not initialized")
        
        confidence_threshold = confidence_threshold or settings.OCR_CONFIDENCE_THRESHOLD
        
        try:
            logger.info("Starting OCR text extraction")
            
            # Perform OCR
            # EasyOCR returns: [(bbox, text, confidence), ...]
            results = self.reader.readtext(image)
            
            logger.info(f"OCR completed - Found {len(results)} text regions")
            
            # Convert to OCRResult objects
            ocr_results = []
            filtered_count = 0
            
            for bbox_coords, text, confidence in results:
                # Skip low confidence results
                if confidence < confidence_threshold:
                    filtered_count += 1
                    logger.debug(f"Filtered low confidence result: '{text}' ({confidence:.2f})")
                    continue
                
                # Create bounding box
                # bbox_coords is [[x1,y1], [x2,y2], [x3,y3], [x4,y4]]
                bounding_box = BoundingBox(
                    top_left=(int(bbox_coords[0][0]), int(bbox_coords[0][1])),
                    top_right=(int(bbox_coords[1][0]), int(bbox_coords[1][1])),
                    bottom_right=(int(bbox_coords[2][0]), int(bbox_coords[2][1])),
                    bottom_left=(int(bbox_coords[3][0]), int(bbox_coords[3][1]))
                )
                
                # Create OCR result
                ocr_result = OCRResult(
                    bbox=bounding_box,
                    text=text.strip(),
                    confidence=float(confidence)
                )
                
                ocr_results.append(ocr_result)
                logger.debug(f"Extracted: '{text}' (confidence: {confidence:.2f})")
            
            logger.info(
                f"OCR extraction complete - "
                f"Accepted: {len(ocr_results)}, "
                f"Filtered: {filtered_count}, "
                f"Threshold: {confidence_threshold}"
            )
            
            return ocr_results
            
        except Exception as e:
            logger.error(f"OCR extraction failed: {e}")
            raise RuntimeError(f"Text extraction failed: {e}")
    
    def extract_text_from_regions(
        self,
        image: np.ndarray,
        regions: List[tuple]
    ) -> List[OCRResult]:
        """
        Extract text from specific regions of an image.
        
        Args:
            image: Input image
            regions: List of (x, y, width, height) tuples
            
        Returns:
            List of OCR results for specified regions
        """
        results = []
        
        for i, (x, y, w, h) in enumerate(regions):
            logger.debug(f"Processing region {i+1}/{len(regions)}: ({x}, {y}, {w}, {h})")
            
            # Extract region
            region = image[y:y+h, x:x+w]
            
            # Perform OCR on region
            region_results = self.extract_text(region)
            
            # Adjust bounding boxes to global coordinates
            for result in region_results:
                result.bbox.top_left = (
                    result.bbox.top_left[0] + x,
                    result.bbox.top_left[1] + y
                )
                result.bbox.top_right = (
                    result.bbox.top_right[0] + x,
                    result.bbox.top_right[1] + y
                )
                result.bbox.bottom_right = (
                    result.bbox.bottom_right[0] + x,
                    result.bbox.bottom_right[1] + y
                )
                result.bbox.bottom_left = (
                    result.bbox.bottom_left[0] + x,
                    result.bbox.bottom_left[1] + y
                )
            
            results.extend(region_results)
        
        logger.info(f"Extracted text from {len(regions)} regions - Total results: {len(results)}")
        return results
    
    def get_text_only(self, ocr_results: List[OCRResult]) -> List[str]:
        """
        Extract just the text strings from OCR results.
        
        Args:
            ocr_results: List of OCR results
            
        Returns:
            List of text strings
        """
        return [result.text for result in ocr_results]
    
    def filter_by_confidence(
        self,
        ocr_results: List[OCRResult],
        min_confidence: float
    ) -> List[OCRResult]:
        """
        Filter OCR results by confidence threshold.
        
        Args:
            ocr_results: List of OCR results
            min_confidence: Minimum confidence score
            
        Returns:
            Filtered list of OCR results
        """
        filtered = [r for r in ocr_results if r.confidence >= min_confidence]
        logger.debug(f"Filtered {len(ocr_results)} -> {len(filtered)} results (threshold: {min_confidence})")
        return filtered
