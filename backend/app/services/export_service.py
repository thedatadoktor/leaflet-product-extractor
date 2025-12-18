"""
Export service for saving extracted products to JSON files.
"""
import json
from pathlib import Path
from datetime import datetime
from typing import List, Optional
import uuid
import time

from app.schemas.product import Product
from app.core.config import settings
from app.core.logging import app_logger as logger


class ExportService:
    """Handle exporting product data to JSON"""
    
    def __init__(self, output_dir: Optional[str] = None):
        """
        Initialize export service.
        
        Args:
            output_dir: Directory to save JSON files (default from settings)
        """
        self.output_dir = Path(output_dir or settings.OUTPUT_DIRECTORY)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"ExportService initialized - Output: {self.output_dir}")
    
    def export_to_json(
        self,
        products: List[Product],
        source_image: str,
        processing_time: float
    ) -> str:
        """
        Export products to JSON file.
        
        Args:
            products: List of extracted products
            source_image: Source image filename
            processing_time: Time taken to process (seconds)
            
        Returns:
            Path to created JSON file
        """
        # Generate extraction ID
        extraction_id = f"ext-{uuid.uuid4().hex[:12]}"
        
        # Generate filename with timestamp including microseconds for uniqueness
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        filename = f"products_{timestamp}.json"
        filepath = self.output_dir / filename
        
        # Build export data
        export_data = {
            "extraction_id": extraction_id,
            "timestamp": datetime.now().isoformat(),
            "source_image": source_image,
            "products": [self._product_to_dict(p) for p in products],
            "total_products": len(products),
            "processing_time_seconds": round(processing_time, 2)
        }
        
        # Write to file
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Exported {len(products)} products to: {filepath}")
        return str(filepath)
    
    def _product_to_dict(self, product: Product) -> dict:
        """
        Convert Product to dictionary for JSON serialization.
        
        Args:
            product: Product object
            
        Returns:
            Dictionary representation
        """
        product_dict = {
            "id": product.id,
            "name": product.name,
            "price": product.price,
            "currency": product.currency,
            "confidence": round(product.confidence, 2)
        }
        
        # Add optional fields if present
        if product.description:
            product_dict["description"] = product.description
        
        if product.unit_price:
            product_dict["unit_price"] = product.unit_price
        
        if product.unit:
            product_dict["unit"] = product.unit
        
        if product.special_offer:
            product_dict["special_offer"] = product.special_offer
        
        if product.position:
            product_dict["position"] = {
                "x": product.position.x,
                "y": product.position.y,
                "width": product.position.width,
                "height": product.position.height
            }
        
        return product_dict
    
    def load_from_json(self, filepath: str) -> dict:
        """
        Load extraction data from JSON file.
        
        Args:
            filepath: Path to JSON file
            
        Returns:
            Loaded extraction data
        """
        filepath = Path(filepath)
        
        if not filepath.exists():
            raise FileNotFoundError(f"JSON file not found: {filepath}")
        
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        logger.info(f"Loaded {data.get('total_products', 0)} products from: {filepath}")
        return data
    
    def list_exports(self, limit: int = 10) -> List[dict]:
        """
        List recent export files.
        
        Args:
            limit: Maximum number of files to return
            
        Returns:
            List of file information dictionaries
        """
        json_files = sorted(
            self.output_dir.glob("products_*.json"),
            key=lambda f: f.stat().st_mtime,
            reverse=True
        )[:limit]
        
        exports = []
        for filepath in json_files:
            try:
                with open(filepath, 'r') as f:
                    data = json.load(f)
                
                exports.append({
                    "filename": filepath.name,
                    "filepath": str(filepath),
                    "extraction_id": data.get("extraction_id"),
                    "timestamp": data.get("timestamp"),
                    "total_products": data.get("total_products", 0),
                    "source_image": data.get("source_image")
                })
            except Exception as e:
                logger.warning(f"Failed to read {filepath}: {e}")
                continue
        
        return exports
