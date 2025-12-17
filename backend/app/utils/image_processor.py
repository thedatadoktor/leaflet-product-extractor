"""
Image preprocessing utilities
"""
import cv2
import numpy as np
from PIL import Image
from typing import Tuple


class ImageProcessor:
    """Handles image preprocessing for OCR"""
    
    @staticmethod
    def load_image(file_path: str) -> np.ndarray:
        """Load image from file"""
        img = cv2.imread(file_path)
        if img is None:
            raise ValueError(f"Could not load image: {file_path}")
        return img
    
    @staticmethod
    def to_grayscale(image: np.ndarray) -> np.ndarray:
        """Convert to grayscale"""
        return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    @staticmethod
    def denoise(image: np.ndarray) -> np.ndarray:
        """Apply denoising"""
        return cv2.fastNlMeansDenoising(image, None, 10, 7, 21)
    
    @staticmethod
    def enhance_contrast(image: np.ndarray) -> np.ndarray:
        """Enhance image contrast using CLAHE"""
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        return clahe.apply(image)
    
    @staticmethod
    def resize_if_needed(
        image: np.ndarray, 
        max_width: int = 2000, 
        max_height: int = 2000
    ) -> np.ndarray:
        """Resize image if it exceeds max dimensions"""
        h, w = image.shape[:2]
        
        if w <= max_width and h <= max_height:
            return image
        
        scale = min(max_width / w, max_height / h)
        new_w = int(w * scale)
        new_h = int(h * scale)
        
        return cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_AREA)
    
    def preprocess(self, image_path: str) -> np.ndarray:
        """Complete preprocessing pipeline"""
        # Load
        img = self.load_image(image_path)
        
        # Resize if needed
        img = self.resize_if_needed(img)
        
        # Convert to grayscale
        gray = self.to_grayscale(img)
        
        # Denoise
        denoised = self.denoise(gray)
        
        # Enhance contrast
        enhanced = self.enhance_contrast(denoised)
        
        return enhanced