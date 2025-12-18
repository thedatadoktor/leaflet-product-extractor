"""Unit tests for TextCleaner"""
import pytest
from app.utils.text_cleaner import TextCleaner


class TestTextCleaner:
    
    def test_clean_product_name(self):
        result = TextCleaner.clean_product_name("  FRESH   Apples  ")
        assert result == "Apples"
    
    def test_extract_quantity_from_name(self):
        name, qty = TextCleaner.extract_quantity_from_name("Fresh Milk 2L")
        assert "Milk" in name
        # Quantity is returned in lowercase
        assert qty == "2l"
    
    def test_detect_special_offer(self):
        offer = TextCleaner.detect_special_offer("Super Saver Special")
        assert offer == "Super Saver"
    
    def test_normalize_whitespace(self):
        result = TextCleaner.normalize_whitespace("  too   many    spaces  ")
        assert result == "too many spaces"
    
    def test_clean_description(self):
        result = TextCleaner.clean_description("  fresh.  high quality!!!  ")
        assert "Fresh" in result
        assert "!!!" not in result
