"""Unit tests for PriceExtractor"""
import pytest
from app.utils.price_extractor import PriceExtractor


class TestPriceExtractor:
    
    def test_extract_price_with_dollar_sign(self):
        assert PriceExtractor.extract_price("$3.49") == 3.49
        assert PriceExtractor.extract_price("Only $10.99") == 10.99
    
    def test_extract_price_exclude_unit_prices(self):
        # Should exclude unit price in parentheses
        price = PriceExtractor.extract_price("$3.49 ($13.96 per kg)", exclude_unit_prices=True)
        assert price == 3.49
    
    def test_extract_price_no_match(self):
        assert PriceExtractor.extract_price("No price here") is None
    
    def test_extract_all_prices(self):
        prices = PriceExtractor.extract_all_prices("Was $5.99, Now $3.49")
        assert len(prices) == 2
        assert 3.49 in prices
        assert 5.99 in prices
    
    def test_extract_unit_price(self):
        result = PriceExtractor.extract_unit_price("$3.49 per kg")
        assert result is not None
        price, unit = result
        assert price == 3.49
        assert unit == "kg"
    
    def test_extract_discount(self):
        assert PriceExtractor.extract_discount("Save $2.50") == 2.50
        assert PriceExtractor.extract_discount("No savings") is None
    
    def test_normalize_price(self):
        assert PriceExtractor.normalize_price(3.499) == 3.50
        assert PriceExtractor.normalize_price(10.991) == 10.99
