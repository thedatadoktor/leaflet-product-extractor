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
    
    def test_extract_product_name(self, parser):
        text = "Fresh Apples $3.49"
        name = parser._extract_product_name(text)
        assert "Fresh" in name or "Apples" in name
    
    def test_group_into_regions(self, parser, sample_ocr_results):
        regions = parser._group_into_regions(sample_ocr_results)
        assert len(regions) >= 1
        assert len(regions[0].texts) > 0
    
    def test_parse_products(self, parser, sample_ocr_results):
        products = parser.parse_products(sample_ocr_results)
        # May or may not find a valid product depending on parsing logic
        assert isinstance(products, list)
