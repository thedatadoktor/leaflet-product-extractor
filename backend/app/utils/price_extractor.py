"""
Price extraction and normalization utilities.

This module handles extracting prices from OCR text using regex patterns.
"""
import re
from typing import Optional, Tuple, List
from app.core.logging import app_logger as logger


class PriceExtractor:
    """Extract and normalize prices from text"""
    
    # Regex patterns for price matching
    PRICE_PATTERNS = [
        # $3.49, $10.99 - explicit dollar sign
        r'\$\s*(\d+\.\d{2})',
        # $3, $10 (whole dollars)
        r'\$\s*(\d+)(?!\.\d)',
    ]
    
    # Unit price patterns - these are separate to avoid confusion
    UNIT_PRICE_PATTERNS = [
        # $3.49 per kg, $2.50/kg, $1.40 per 100g
        r'\$\s*(\d+\.\d{2})\s*(?:per|/)\s*(\w+)',
        # Inside parentheses: ($13.96 per kg)
        r'\(\$\s*(\d+\.\d{2})\s*(?:per|/)\s*(\w+)\)',
        # 3.49 per kg
        r'(\d+\.\d{2})\s*(?:per|/)\s*(\w+)',
    ]
    
    # Common units
    UNITS = ['kg', 'g', '100g', 'l', 'ml', 'each', 'pack', 'ea']
    
    @staticmethod
    def extract_price(text: str, exclude_unit_prices: bool = True) -> Optional[float]:
        """
        Extract main price from text (excluding unit prices).
        
        Args:
            text: Text containing price
            exclude_unit_prices: Whether to exclude unit prices from extraction
            
        Returns:
            Extracted price as float, or None if not found
        """
        # If we want to exclude unit prices, remove them from text first
        clean_text = text
        if exclude_unit_prices:
            # Remove text in parentheses (usually unit prices)
            clean_text = re.sub(r'\([^)]*\)', '', text)
            # Remove "per kg" type patterns
            clean_text = re.sub(r'\d+\.\d{2}\s*(?:per|/)\s*\w+', '', clean_text)
        
        for pattern in PriceExtractor.PRICE_PATTERNS:
            matches = re.findall(pattern, clean_text)
            if matches:
                try:
                    # Take the first match (should be main price)
                    price = float(matches[0])
                    logger.debug(f"Extracted main price ${price} from: '{text}'")
                    return price
                except ValueError:
                    continue
        
        logger.debug(f"No main price found in: '{text}'")
        return None
    
    @staticmethod
    def extract_all_prices(text: str) -> List[float]:
        """
        Extract all prices from text.
        
        Args:
            text: Text potentially containing multiple prices
            
        Returns:
            List of all extracted prices, sorted lowest to highest
        """
        prices = []
        
        for pattern in PriceExtractor.PRICE_PATTERNS:
            matches = re.findall(pattern, text)
            for match in matches:
                try:
                    price = float(match)
                    if price not in prices:  # Avoid duplicates
                        prices.append(price)
                except ValueError:
                    continue
        
        logger.debug(f"Extracted {len(prices)} prices from: '{text}'")
        return sorted(prices)  # Sort ascending (main price usually lower)
    
    @staticmethod
    def extract_unit_price(text: str) -> Optional[Tuple[float, str]]:
        """
        Extract unit price and unit from text.
        
        Args:
            text: Text containing unit price
            
        Returns:
            Tuple of (unit_price, unit) or None if not found
        """
        text_lower = text.lower()
        
        for pattern in PriceExtractor.UNIT_PRICE_PATTERNS:
            matches = re.findall(pattern, text_lower)
            if matches:
                try:
                    price_str, unit = matches[0]
                    price = float(price_str)
                    
                    # Normalize unit
                    unit = unit.strip()
                    
                    logger.debug(f"Extracted unit price ${price} per {unit} from: '{text}'")
                    return (price, unit)
                except (ValueError, IndexError):
                    continue
        
        logger.debug(f"No unit price found in: '{text}'")
        return None
    
    @staticmethod
    def normalize_price(price: float) -> float:
        """
        Normalize price to 2 decimal places.
        
        Args:
            price: Raw price value
            
        Returns:
            Normalized price
        """
        return round(price, 2)
    
    @staticmethod
    def extract_discount(text: str) -> Optional[float]:
        """
        Extract discount amount from text.
        
        Args:
            text: Text containing discount info
            
        Returns:
            Discount amount or None
        """
        # Pattern: Save $2.50, Save $5
        patterns = [
            r'[Ss]ave\s+\$\s*(\d+\.\d{2})',
            r'[Ss]ave\s+\$\s*(\d+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                try:
                    discount = float(match.group(1))
                    logger.debug(f"Extracted discount ${discount} from: '{text}'")
                    return discount
                except ValueError:
                    continue
        
        return None
    
    @staticmethod
    def calculate_unit_price_from_price(
        price: float,
        quantity: float,
        from_unit: str,
        to_unit: str = 'kg'
    ) -> Optional[float]:
        """
        Calculate unit price from total price and quantity.
        
        Args:
            price: Total price
            quantity: Quantity amount
            from_unit: Unit of quantity (e.g., '250g')
            to_unit: Target unit (default 'kg')
            
        Returns:
            Calculated unit price or None
        """
        # Unit conversion factors (to kg)
        conversions = {
            'g': 0.001,
            'kg': 1.0,
            '100g': 0.1,
            '250g': 0.25,
            '500g': 0.5,
        }
        
        from_unit_clean = from_unit.lower().strip()
        to_unit_clean = to_unit.lower().strip()
        
        if from_unit_clean not in conversions or to_unit_clean not in conversions:
            logger.warning(f"Unknown unit conversion: {from_unit} to {to_unit}")
            return None
        
        try:
            # Convert to base unit (kg)
            quantity_in_kg = quantity * conversions[from_unit_clean]
            
            # Calculate price per kg
            unit_price = price / quantity_in_kg
            
            # Convert to target unit
            unit_price_final = unit_price * conversions[to_unit_clean]
            
            return round(unit_price_final, 2)
        except (ZeroDivisionError, ValueError):
            return None
