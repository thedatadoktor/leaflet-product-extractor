"""
Validation utilities for file uploads and data.
"""
from pathlib import Path
from typing import Union
from app.core.config import settings
from app.core.logging import app_logger as logger


class FileValidator:
    """Validates uploaded files"""
    
    @staticmethod
    def validate_file_extension(filename: str) -> bool:
        """
        Check if file has allowed extension.
        
        Args:
            filename: Name of file to validate
            
        Returns:
            True if extension is allowed
        """
        file_path = Path(filename)
        extension = file_path.suffix.lower()
        
        is_valid = extension in settings.ALLOWED_EXTENSIONS
        
        if not is_valid:
            logger.warning(f"Invalid file extension: {extension}")
        
        return is_valid
    
    @staticmethod
    def validate_file_size(file_size: int) -> bool:
        """
        Check if file size is within limits.
        
        Args:
            file_size: Size of file in bytes
            
        Returns:
            True if size is within limits
        """
        is_valid = file_size <= settings.MAX_UPLOAD_SIZE
        
        if not is_valid:
            max_mb = settings.MAX_UPLOAD_SIZE / (1024 * 1024)
            actual_mb = file_size / (1024 * 1024)
            logger.warning(f"File too large: {actual_mb:.2f}MB (max: {max_mb:.2f}MB)")
        
        return is_valid
    
    @staticmethod
    def validate_file(filename: str, file_size: int) -> tuple[bool, str]:
        """
        Validate file extension and size.
        
        Args:
            filename: Name of file
            file_size: Size in bytes
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check extension
        if not FileValidator.validate_file_extension(filename):
            return False, f"Invalid file type. Allowed: {settings.ALLOWED_EXTENSIONS}"
        
        # Check size
        if not FileValidator.validate_file_size(file_size):
            max_mb = settings.MAX_UPLOAD_SIZE / (1024 * 1024)
            return False, f"File too large. Maximum size: {max_mb:.1f}MB"
        
        return True, ""


class PriceValidator:
    """Validates price data"""
    
    @staticmethod
    def is_valid_price(price: float) -> bool:
        """
        Check if price is valid.
        
        Args:
            price: Price value to validate
            
        Returns:
            True if price is valid (positive, reasonable)
        """
        if price <= 0:
            return False
        
        # Reject unreasonably high prices (likely OCR error)
        if price > 10000:
            logger.warning(f"Suspiciously high price: ${price}")
            return False
        
        return True
    
    @staticmethod
    def validate_unit_price(price: float, unit_price: float) -> bool:
        """
        Validate that unit price makes sense relative to main price.
        
        Args:
            price: Main product price
            unit_price: Price per unit
            
        Returns:
            True if unit price is reasonable
        """
        if unit_price <= 0:
            return False
        
        # Unit price should generally be less than or equal to main price
        # Allow some tolerance for edge cases
        if unit_price > price * 2:
            logger.warning(f"Unit price ${unit_price} seems high compared to price ${price}")
            return False
        
        return True


class TextValidator:
    """Validates extracted text"""
    
    @staticmethod
    def is_valid_product_name(text: str, min_length: int = 2) -> bool:
        """
        Check if text is a valid product name.
        
        Args:
            text: Text to validate
            min_length: Minimum length for product name
            
        Returns:
            True if text is a valid product name
        """
        if not text or len(text.strip()) < min_length:
            return False
        
        # Check if text is mostly alphabetic or numeric (not symbols)
        alphanumeric_count = sum(c.isalnum() or c.isspace() for c in text)
        if alphanumeric_count / len(text) < 0.5:
            return False
        
        return True
    
    @staticmethod
    def clean_text(text: str) -> str:
        """
        Clean and normalize extracted text.
        
        Args:
            text: Raw text to clean
            
        Returns:
            Cleaned text
        """
        # Remove extra whitespace
        cleaned = " ".join(text.split())
        
        # Remove common OCR artifacts
        cleaned = cleaned.replace("  ", " ")
        
        return cleaned.strip()
