"""
Integration tests for complete extraction pipeline
"""
import pytest
import numpy as np
from app.utils.image_processor import ImageProcessor
from app.utils.price_extractor import PriceExtractor
from app.utils.text_cleaner import TextCleaner
from app.utils.unit_price_calculator import UnitPriceCalculator


class TestExtractionPipeline:
    """Test the complete extraction pipeline"""
    
    def test_price_extraction_and_validation(self):
        """Test extracting and validating prices"""
        # Simulate OCR text
        ocr_text = "Fresh Apples 250g $3.49 ($13.96 per kg)"
        
        # Extract MAIN price (not unit price) - use extract_price, not extract_all_prices
        extractor = PriceExtractor()
        main_price = extractor.extract_price(ocr_text, exclude_unit_prices=True)
        
        assert main_price is not None, "Main price extraction failed"
        assert main_price == 3.49, f"Expected $3.49, got ${main_price}"
        
        # Extract unit price
        unit_result = extractor.extract_unit_price(ocr_text)
        assert unit_result is not None, "Unit price extraction failed"
        
        unit_price, unit = unit_result
        assert unit_price == 13.96, f"Expected $13.96/kg, got ${unit_price}"
        assert unit == "kg", f"Expected 'kg', got '{unit}'"
        
        # Calculate what the unit price should be
        calc = UnitPriceCalculator()
        calculated_unit_price = calc.calculate_unit_price(
            total_price=main_price,
            quantity=250,
            unit='g'
        )
        
        # The calculated unit price should be 13.96
        # $3.49 / 0.25kg = $13.96/kg
        assert calculated_unit_price == 13.96, f"Expected calculated $13.96/kg, got ${calculated_unit_price}"
        
        # Validate with proper tolerance
        is_valid = calc.validate_unit_price(
            total_price=main_price,
            unit_price=unit_price,
            quantity=250,
            unit='g',
            tolerance=0.10
        )
        
        assert is_valid is True, (
            f"Unit price validation failed. "
            f"Calculated: ${calculated_unit_price}, "
            f"Extracted: ${unit_price}"
        )
    
    def test_product_name_cleaning_pipeline(self):
        """Test cleaning product names"""
        raw_name = "  SUPER SAVER Fresh Organic Apples 1kg Pack  "
        
        cleaner = TextCleaner()
        
        # Clean name
        cleaned = cleaner.clean_product_name(raw_name)
        assert "Apples" in cleaned
        assert "SUPER" not in cleaned  # Noise word removed
        
        # Extract quantity
        name_only, quantity = cleaner.extract_quantity_from_name(cleaned)
        
        # Quantity should be lowercase now
        assert quantity.lower() == "1kg"
        
        # Detect offer
        offer = cleaner.detect_special_offer(raw_name)
        assert offer == "Super Saver"
    
    def test_image_to_price_pipeline(self):
        """Test image processing pipeline"""
        # Create sample image
        test_image = np.random.randint(0, 255, (1000, 1000, 3), dtype=np.uint8)
        
        # Process image
        processor = ImageProcessor()
        gray = processor.to_grayscale(test_image)
        denoised = processor.denoise(gray)
        enhanced = processor.enhance_contrast(denoised)
        
        # Verify pipeline
        assert gray.shape[:2] == test_image.shape[:2]
        assert denoised.shape == gray.shape
        assert enhanced.shape == gray.shape
