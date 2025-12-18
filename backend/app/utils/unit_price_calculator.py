"""
Unit price calculation and validation.
"""
from typing import Optional, Tuple
from app.core.logging import app_logger as logger


class UnitPriceCalculator:
    """Calculate and validate unit prices"""
    
    # Conversion factors to standard units
    WEIGHT_CONVERSIONS = {
        'kg': 1.0,
        'g': 0.001,
        '100g': 0.1,
        '250g': 0.25,
        '500g': 0.5,
        'lb': 0.453592,
        'oz': 0.0283495,
    }
    
    VOLUME_CONVERSIONS = {
        'l': 1.0,
        'litre': 1.0,
        'liter': 1.0,
        'ml': 0.001,
        '100ml': 0.1,
        '250ml': 0.25,
        '500ml': 0.5,
    }
    
    @staticmethod
    def calculate_unit_price(
        total_price: float,
        quantity: float,
        unit: str
    ) -> Optional[float]:
        """
        Calculate unit price.
        
        Args:
            total_price: Total product price
            quantity: Quantity value
            unit: Unit of measurement
            
        Returns:
            Unit price or None if calculation fails
        """
        if total_price <= 0 or quantity <= 0:
            logger.warning(f"Invalid inputs: price={total_price}, quantity={quantity}")
            return None
        
        unit_lower = unit.lower().strip()
        
        # Determine conversion factor
        conversion = None
        if unit_lower in UnitPriceCalculator.WEIGHT_CONVERSIONS:
            conversion = UnitPriceCalculator.WEIGHT_CONVERSIONS[unit_lower]
        elif unit_lower in UnitPriceCalculator.VOLUME_CONVERSIONS:
            conversion = UnitPriceCalculator.VOLUME_CONVERSIONS[unit_lower]
        else:
            logger.debug(f"Unknown unit: {unit}")
            # For items like 'each', 'pack', just return price
            return round(total_price / quantity, 2)
        
        # Calculate price per standard unit (kg or L)
        quantity_in_standard = quantity * conversion
        unit_price = total_price / quantity_in_standard
        
        logger.debug(
            f"Calculated unit price: ${total_price} / {quantity}{unit} = "
            f"${unit_price:.2f}/{'kg' if unit_lower in UnitPriceCalculator.WEIGHT_CONVERSIONS else 'L'}"
        )
        
        return round(unit_price, 2)
    
    @staticmethod
    def validate_unit_price(
        total_price: float,
        unit_price: float,
        quantity: float,
        unit: str,
        tolerance: float = 0.10  # Increased tolerance to 10 cents
    ) -> bool:
        """
        Validate that unit price is correct.
        
        Args:
            total_price: Total product price
            unit_price: Claimed unit price
            quantity: Quantity value
            unit: Unit of measurement
            tolerance: Allowed difference in dollars (default 0.10)
            
        Returns:
            True if unit price is valid
        """
        calculated = UnitPriceCalculator.calculate_unit_price(
            total_price, quantity, unit
        )
        
        if calculated is None:
            return False
        
        # Allow tolerance for rounding
        is_valid = abs(calculated - unit_price) <= tolerance
        
        if not is_valid:
            logger.warning(
                f"Unit price mismatch: calculated ${calculated} vs claimed ${unit_price} "
                f"(difference: ${abs(calculated - unit_price):.2f}, tolerance: ${tolerance})"
            )
        
        return is_valid
    
    @staticmethod
    def normalize_unit(unit: str) -> str:
        """
        Normalize unit to standard form.
        
        Args:
            unit: Raw unit string
            
        Returns:
            Normalized unit (lowercase)
        """
        unit_lower = unit.lower().strip()
        
        # Map common variations to standard units
        unit_mapping = {
            'kilogram': 'kg',
            'kilograms': 'kg',
            'gram': 'g',
            'grams': 'g',
            'litre': 'l',
            'liter': 'l',
            'litres': 'l',
            'liters': 'l',
            'milliliter': 'ml',
            'millilitre': 'ml',
            'milliliters': 'ml',
            'millilitres': 'ml',
        }
        
        return unit_mapping.get(unit_lower, unit_lower)
    
    @staticmethod
    def compare_unit_prices(
        price1: float,
        unit1: str,
        price2: float,
        unit2: str
    ) -> Optional[float]:
        """
        Compare two unit prices (normalize to same unit).
        
        Args:
            price1: First unit price
            unit1: First unit
            price2: Second unit price
            unit2: Second unit
            
        Returns:
            Difference (price1 - price2) or None if can't compare
        """
        # Normalize units
        unit1_norm = UnitPriceCalculator.normalize_unit(unit1)
        unit2_norm = UnitPriceCalculator.normalize_unit(unit2)
        
        # Must be same type (both weight or both volume)
        is_weight1 = unit1_norm in UnitPriceCalculator.WEIGHT_CONVERSIONS
        is_weight2 = unit2_norm in UnitPriceCalculator.WEIGHT_CONVERSIONS
        
        if is_weight1 != is_weight2:
            logger.warning("Cannot compare different unit types (weight vs volume)")
            return None
        
        # Both should be same, just return difference
        return price1 - price2
