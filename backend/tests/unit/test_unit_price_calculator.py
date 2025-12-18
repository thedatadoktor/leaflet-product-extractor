"""Unit tests for UnitPriceCalculator"""
import pytest
from app.utils.unit_price_calculator import UnitPriceCalculator


class TestUnitPriceCalculator:
    
    def test_calculate_unit_price_grams_to_kg(self):
        result = UnitPriceCalculator.calculate_unit_price(3.49, 250, 'g')
        assert result == 13.96  # $3.49 / 0.25kg = $13.96/kg
    
    def test_calculate_unit_price_liters(self):
        result = UnitPriceCalculator.calculate_unit_price(5.99, 2, 'L')
        assert result == 3.00  # $5.99 / 2L ≈ $3.00/L
    
    def test_validate_unit_price_correct(self):
        is_valid = UnitPriceCalculator.validate_unit_price(
            total_price=3.49,
            unit_price=13.96,
            quantity=250,
            unit='g'
        )
        assert is_valid is True
    
    def test_validate_unit_price_incorrect(self):
        is_valid = UnitPriceCalculator.validate_unit_price(
            total_price=3.49,
            unit_price=20.00,
            quantity=250,
            unit='g'
        )
        assert is_valid is False
    
    def test_normalize_unit(self):
        assert UnitPriceCalculator.normalize_unit('kilograms') == 'kg'
        assert UnitPriceCalculator.normalize_unit('litres') == 'l'
