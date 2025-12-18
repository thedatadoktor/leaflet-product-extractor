"""Unit tests for ExportService"""
import pytest
import json
import time
from pathlib import Path
from app.services.export_service import ExportService
from app.schemas.product import Product, Position


class TestExportService:
    
    @pytest.fixture
    def export_service(self, tmp_path):
        return ExportService(output_dir=str(tmp_path))
    
    @pytest.fixture
    def sample_products(self):
        return [
            Product(
                id="test-001",
                name="Fresh Apples",
                description="250g",
                price=3.49,
                unit_price=13.96,
                unit="per kg",
                currency="AUD",
                special_offer="Super Saver",
                position=Position(x=10, y=10, width=100, height=50),
                confidence=0.95
            )
        ]
    
    def test_export_to_json(self, export_service, sample_products):
        filepath = export_service.export_to_json(
            products=sample_products,
            source_image="test.jpg",
            processing_time=5.5
        )
        
        assert Path(filepath).exists()
        
        # Load and verify
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        assert data["total_products"] == 1
        assert data["source_image"] == "test.jpg"
        assert len(data["products"]) == 1
        assert data["products"][0]["name"] == "Fresh Apples"
    
    def test_load_from_json(self, export_service, sample_products):
        # Export first
        filepath = export_service.export_to_json(
            products=sample_products,
            source_image="test.jpg",
            processing_time=5.5
        )
        
        # Load it back
        data = export_service.load_from_json(filepath)
        assert data["total_products"] == 1
    
    def test_list_exports(self, export_service, sample_products):
        # Create a few exports with small delays to ensure unique timestamps
        for i in range(3):
            export_service.export_to_json(
                products=sample_products,
                source_image=f"test_{i}.jpg",
                processing_time=5.5
            )
            # Small delay to ensure different microsecond timestamps
            time.sleep(0.001)
        
        exports = export_service.list_exports(limit=10)
        assert len(exports) == 3
        
        # Verify they're sorted by most recent first
        assert exports[0]["source_image"] == "test_2.jpg"
        assert exports[2]["source_image"] == "test_0.jpg"
