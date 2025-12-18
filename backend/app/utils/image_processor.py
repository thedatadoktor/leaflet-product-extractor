"""
Image preprocessing utilities for optimal OCR performance.

This module handles all image preprocessing operations including:
- Loading and validation
- Grayscale conversion
- Denoising
- Contrast enhancement
- Resizing
"""
import cv2
import numpy as np
from PIL import Image
from pathlib import Path
from typing import Union, Tuple, Optional
from app.core.config import settings
from app.core.logging import app_logger as logger


class ImageProcessor:
    """Handles image preprocessing for OCR"""
    
    def __init__(
        self,
        max_width: Optional[int] = None,
        max_height: Optional[int] = None
    ):
        """
        Initialize ImageProcessor.
        
        Args:
            max_width: Maximum image width (default from settings)
            max_height: Maximum image height (default from settings)
        """
        self.max_width = max_width or settings.IMAGE_RESIZE_MAX_WIDTH
        self.max_height = max_height or settings.IMAGE_RESIZE_MAX_HEIGHT
        logger.info(f"ImageProcessor initialized - Max size: {self.max_width}x{self.max_height}")
    
    @staticmethod
    def load_image(file_path: Union[str, Path]) -> np.ndarray:
        """
        Load image from file path.
        
        Args:
            file_path: Path to image file
            
        Returns:
            Image as numpy array in BGR format
            
        Raises:
            ValueError: If image cannot be loaded
        """
        file_path = str(file_path)
        logger.debug(f"Loading image: {file_path}")
        
        img = cv2.imread(file_path)
        
        if img is None:
            raise ValueError(f"Could not load image: {file_path}")
        
        logger.info(f"Image loaded - Shape: {img.shape}")
        return img
    
    @staticmethod
    def to_grayscale(image: np.ndarray) -> np.ndarray:
        """
        Convert image to grayscale.
        
        Args:
            image: Input image in BGR format
            
        Returns:
            Grayscale image
        """
        if len(image.shape) == 2:
            # Already grayscale
            logger.debug("Image already in grayscale")
            return image
        
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        logger.debug("Converted to grayscale")
        return gray
    
    @staticmethod
    def denoise(image: np.ndarray, strength: int = 10) -> np.ndarray:
        """
        Apply denoising to image.
        
        Args:
            image: Input grayscale image
            strength: Denoising strength (higher = more denoising)
            
        Returns:
            Denoised image
        """
        if len(image.shape) == 3:
            # Color image - use different denoising
            denoised = cv2.fastNlMeansDenoisingColored(image, None, strength, strength, 7, 21)
        else:
            # Grayscale image
            denoised = cv2.fastNlMeansDenoising(image, None, strength, 7, 21)
        
        logger.debug(f"Applied denoising with strength {strength}")
        return denoised
    
    @staticmethod
    def enhance_contrast(image: np.ndarray, clip_limit: float = 2.0) -> np.ndarray:
        """
        Enhance image contrast using CLAHE (Contrast Limited Adaptive Histogram Equalization).
        
        Args:
            image: Input grayscale image
            clip_limit: Threshold for contrast limiting
            
        Returns:
            Contrast-enhanced image
        """
        clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=(8, 8))
        enhanced = clahe.apply(image)
        logger.debug("Enhanced contrast using CLAHE")
        return enhanced
    
    @staticmethod
    def adaptive_threshold(image: np.ndarray) -> np.ndarray:
        """
        Apply adaptive thresholding to improve text visibility.
        
        Args:
            image: Input grayscale image
            
        Returns:
            Binary threshold image
        """
        # Apply Gaussian blur first
        blurred = cv2.GaussianBlur(image, (5, 5), 0)
        
        # Adaptive threshold
        thresh = cv2.adaptiveThreshold(
            blurred,
            255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            11,
            2
        )
        
        logger.debug("Applied adaptive thresholding")
        return thresh
    
    def resize_if_needed(
        self,
        image: np.ndarray,
        max_width: Optional[int] = None,
        max_height: Optional[int] = None
    ) -> np.ndarray:
        """
        Resize image if it exceeds maximum dimensions.
        
        Args:
            image: Input image
            max_width: Maximum width (uses instance default if None)
            max_height: Maximum height (uses instance default if None)
            
        Returns:
            Resized image (or original if within limits)
        """
        max_width = max_width or self.max_width
        max_height = max_height or self.max_height
        
        h, w = image.shape[:2]
        
        if w <= max_width and h <= max_height:
            logger.debug(f"Image size {w}x{h} within limits, no resize needed")
            return image
        
        # Calculate scaling factor
        scale = min(max_width / w, max_height / h)
        new_w = int(w * scale)
        new_h = int(h * scale)
        
        resized = cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_AREA)
        logger.info(f"Resized image from {w}x{h} to {new_w}x{new_h}")
        
        return resized
    
    @staticmethod
    def deskew(image: np.ndarray) -> np.ndarray:
        """
        Deskew image (correct rotation).
        
        Args:
            image: Input grayscale image
            
        Returns:
            Deskewed image
        """
        # Detect edges
        edges = cv2.Canny(image, 50, 150, apertureSize=3)
        
        # Detect lines using Hough transform
        lines = cv2.HoughLines(edges, 1, np.pi / 180, 200)
        
        if lines is None:
            logger.debug("No lines detected for deskewing")
            return image
        
        # Calculate average angle
        angles = []
        for rho, theta in lines[:, 0]:
            angle = np.degrees(theta) - 90
            angles.append(angle)
        
        median_angle = np.median(angles)
        
        # Only rotate if angle is significant
        if abs(median_angle) < 0.5:
            logger.debug("Image already aligned, no deskewing needed")
            return image
        
        # Rotate image
        h, w = image.shape[:2]
        center = (w // 2, h // 2)
        rotation_matrix = cv2.getRotationMatrix2D(center, median_angle, 1.0)
        rotated = cv2.warpAffine(image, rotation_matrix, (w, h), 
                                  flags=cv2.INTER_CUBIC,
                                  borderMode=cv2.BORDER_REPLICATE)
        
        logger.info(f"Deskewed image by {median_angle:.2f} degrees")
        return rotated
    
    def preprocess(
        self,
        image_path: Union[str, Path],
        apply_deskew: bool = False,
        apply_threshold: bool = False
    ) -> np.ndarray:
        """
        Complete preprocessing pipeline.
        
        Args:
            image_path: Path to input image
            apply_deskew: Whether to apply deskewing
            apply_threshold: Whether to apply adaptive thresholding
            
        Returns:
            Preprocessed image ready for OCR
        """
        logger.info(f"Starting preprocessing pipeline for: {image_path}")
        
        # Load image
        img = self.load_image(image_path)
        
        # Resize if needed (do this first to reduce processing time)
        img = self.resize_if_needed(img)
        
        # Convert to grayscale
        gray = self.to_grayscale(img)
        
        # Denoise
        denoised = self.denoise(gray)
        
        # Enhance contrast
        enhanced = self.enhance_contrast(denoised)
        
        # Optionally deskew
        if apply_deskew:
            enhanced = self.deskew(enhanced)
        
        # Optionally apply thresholding
        if apply_threshold:
            enhanced = self.adaptive_threshold(enhanced)
        
        logger.info("Preprocessing pipeline completed")
        return enhanced
    
    @staticmethod
    def save_image(image: np.ndarray, output_path: Union[str, Path]) -> None:
        """
        Save processed image to file.
        
        Args:
            image: Image to save
            output_path: Output file path
        """
        output_path = str(output_path)
        cv2.imwrite(output_path, image)
        logger.info(f"Saved image to: {output_path}")
