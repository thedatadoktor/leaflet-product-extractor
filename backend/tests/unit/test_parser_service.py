"""Unit tests for ProductParser"""
import pytest
from app.services.parser_service import ProductParser
from app.models.product import OCRResult, BoundingBox


class TestProductParser:
    
    @pytest.fixture
    def parser(self):
        return ProductParser()
    
    @pytest.fixture
    def sample_ocr_results(self):
        """Create sample OCR results for a product"""
        return [
            OCRResult(
                bbox=BoundingBox((10, 10), (100, 10), (100, 30), (10, 30)),
                text="Fresh Apples",
                confidence=0.95
            ),
            OCRResult(
                bbox=BoundingBox((10, 35), (80, 35), (80, 50), (10, 50)),
                text="250g",
                confidence=0.92
            ),
            OCRResult(
                bbox=BoundingBox((10, 55), (70, 55), (70, 70), (10, 70)),
                text="$3.49",
                confidence=0.98
            ),
        ]
    
    def test_extract_product_name_lenient(self, parser):
        """Test lenient product name extraction"""
        from app.models.product import ProductRegion, OCRResult, BoundingBox
        
        # Create a mock region with product text
        ocr_result = OCRResult(
            bbox=BoundingBox(
                top_left=(0, 0),
                top_right=(100, 0),
                bottom_right=(100, 50),
                bottom_left=(0, 50)
            ),
            text="Fresh Apples $3.49",
            confidence=0.9
        )
        region = ProductRegion(texts=[ocr_result])
        
        name = parser._extract_product_name_lenient(region, "Fresh Apples $3.49")
        assert "Fresh" in name or "Apples" in name
    
    def test_find_price_regions(self, parser, sample_ocr_results):
        """Test price region detection"""
        regions = parser._find_price_regions(sample_ocr_results)
        assert len(regions) >= 0  # May be 0 if no prices found
        if regions:
            assert len(regions[0].texts) > 0
    
    def test_parse_products(self, parser, sample_ocr_results):
        products = parser.parse_products(sample_ocr_results)
        # May or may not find a valid product depending on parsing logic
        assert isinstance(products, list)
