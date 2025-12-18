"""
Unit tests for validators
"""
import pytest
from app.utils.validators import FileValidator, PriceValidator, TextValidator


class TestFileValidator:
    """Test FileValidator"""
    
    def test_validate_file_extension_valid(self):
        """Test valid file extensions"""
        assert FileValidator.validate_file_extension("test.jpg") is True
        assert FileValidator.validate_file_extension("test.jpeg") is True
        assert FileValidator.validate_file_extension("test.png") is True
        assert FileValidator.validate_file_extension("test.pdf") is True
    
    def test_validate_file_extension_invalid(self):
        """Test invalid file extensions"""
        assert FileValidator.validate_file_extension("test.exe") is False
        assert FileValidator.validate_file_extension("test.txt") is False
        assert FileValidator.validate_file_extension("test") is False
    
    def test_validate_file_size_valid(self):
        """Test valid file sizes"""
        assert FileValidator.validate_file_size(1000000) is True  # 1MB
        assert FileValidator.validate_file_size(5000000) is True  # 5MB
    
    def test_validate_file_size_invalid(self):
        """Test file size exceeding limit"""
        assert FileValidator.validate_file_size(20000000) is False  # 20MB
    
    def test_validate_file_complete(self):
        """Test complete file validation"""
        is_valid, msg = FileValidator.validate_file("test.jpg", 5000000)
        assert is_valid is True
        assert msg == ""
        
        is_valid, msg = FileValidator.validate_file("test.exe", 1000)
        assert is_valid is False
        assert "Invalid file type" in msg


class TestPriceValidator:
    """Test PriceValidator"""
    
    def test_is_valid_price_positive(self):
        """Test valid positive prices"""
        assert PriceValidator.is_valid_price(3.49) is True
        assert PriceValidator.is_valid_price(0.99) is True
        assert PriceValidator.is_valid_price(99.99) is True
    
    def test_is_valid_price_invalid(self):
        """Test invalid prices"""
        assert PriceValidator.is_valid_price(0) is False
        assert PriceValidator.is_valid_price(-1.0) is False
        assert PriceValidator.is_valid_price(15000) is False  # Too high
    
    def test_validate_unit_price(self):
        """Test unit price validation"""
        assert PriceValidator.validate_unit_price(3.49, 1.40) is True
        assert PriceValidator.validate_unit_price(5.00, 2.50) is True
        
        # Unit price shouldn't be way higher than main price
        assert PriceValidator.validate_unit_price(3.00, 10.00) is False


class TestTextValidator:
    """Test TextValidator"""
    
    def test_is_valid_product_name(self):
        """Test product name validation"""
        assert TextValidator.is_valid_product_name("Fresh Apples") is True
        assert TextValidator.is_valid_product_name("Bananas 1kg") is True
        
        assert TextValidator.is_valid_product_name("") is False
        assert TextValidator.is_valid_product_name("A") is False  # Too short
        assert TextValidator.is_valid_product_name("$#@!") is False  # Mostly symbols
    
    def test_clean_text(self):
        """Test text cleaning"""
        assert TextValidator.clean_text("  Extra   spaces  ") == "Extra spaces"
        assert TextValidator.clean_text("Test") == "Test"
        assert TextValidator.clean_text("  ") == ""
