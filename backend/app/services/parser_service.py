"""
Product parser service - extracts structured product data from OCR results.

This service takes OCR results and parses them into structured Product objects.
"""
import re
import uuid
from typing import List, Optional, Tuple
from datetime import datetime

from app.models.product import OCRResult, ProductRegion, BoundingBox
from app.schemas.product import Product, Position
from app.utils.price_extractor import PriceExtractor
from app.utils.text_cleaner import TextCleaner
from app.utils.unit_price_calculator import UnitPriceCalculator
from app.utils.validators import PriceValidator, TextValidator
from app.core.logging import app_logger as logger


class ProductParser:
    """Parse OCR results into structured product data"""
    
    def __init__(self):
        self.price_extractor = PriceExtractor()
        self.text_cleaner = TextCleaner()
        self.unit_calculator = UnitPriceCalculator()
        self.price_validator = PriceValidator()
        self.text_validator = TextValidator()
    
    def parse_products(self, ocr_results: List[OCRResult]) -> List[Product]:
        """
        Parse OCR results into structured products.
        
        Args:
            ocr_results: List of OCR text detections
            
        Returns:
            List of parsed Product objects
        """
        logger.info(f"Parsing {len(ocr_results)} OCR results into products")
        
        # Group OCR results into product regions
        regions = self._group_into_regions(ocr_results)
        logger.info(f"Grouped text into {len(regions)} potential product regions")
        
        # Extract products from each region
        products = []
        for i, region in enumerate(regions):
            try:
                product = self._extract_product_from_region(region, index=i)
                if product:
                    products.append(product)
            except Exception as e:
                logger.warning(f"Failed to parse region {i}: {e}")
                continue
        
        logger.info(f"Successfully parsed {len(products)} products")
        return products
    
    def _group_into_regions(
        self, 
        ocr_results: List[OCRResult],
        vertical_threshold: int = 100,
        horizontal_threshold: int = 50
    ) -> List[ProductRegion]:
        """
        Group OCR results into product regions using spatial clustering.
        
        Args:
            ocr_results: List of OCR detections
            vertical_threshold: Max vertical distance to group items
            horizontal_threshold: Max horizontal distance to group items
            
        Returns:
            List of ProductRegion objects
        """
        if not ocr_results:
            return []
        
        # Sort by vertical position (top to bottom)
        sorted_results = sorted(ocr_results, key=lambda r: r.bbox.center[1])
        
        regions = []
        current_region = [sorted_results[0]]
        
        for result in sorted_results[1:]:
            # Check if this result belongs to current region
            last_result = current_region[-1]
            
            vertical_distance = abs(result.bbox.center[1] - last_result.bbox.center[1])
            horizontal_distance = abs(result.bbox.center[0] - last_result.bbox.center[0])
            
            # If close enough, add to current region
            if vertical_distance < vertical_threshold or horizontal_distance < horizontal_threshold:
                current_region.append(result)
            else:
                # Start new region
                regions.append(ProductRegion(texts=current_region))
                current_region = [result]
        
        # Add last region
        if current_region:
            regions.append(ProductRegion(texts=current_region))
        
        logger.debug(f"Created {len(regions)} regions from {len(ocr_results)} OCR results")
        return regions
    
    def _extract_product_from_region(
        self, 
        region: ProductRegion,
        index: int
    ) -> Optional[Product]:
        """
        Extract product data from a text region.
        
        Args:
            region: ProductRegion containing OCR results
            index: Region index for ID generation
            
        Returns:
            Product object or None if extraction fails
        """
        # Combine all text from region
        combined_text = region.combined_text
        logger.debug(f"Processing region {index}: '{combined_text}'")
        
        # Extract price (required)
        price = self.price_extractor.extract_price(combined_text, exclude_unit_prices=True)
        if not price or not self.price_validator.is_valid_price(price):
            logger.debug(f"No valid price found in region {index}")
            return None
        
        # Extract product name
        product_name = self._extract_product_name(combined_text)
        if not product_name or not self.text_validator.is_valid_product_name(product_name):
            logger.debug(f"No valid product name found in region {index}")
            return None
        
        # Clean product name and extract quantity
        cleaned_name = self.text_cleaner.clean_product_name(product_name)
        name_without_qty, quantity = self.text_cleaner.extract_quantity_from_name(cleaned_name)
        
        # Extract unit price
        unit_price_result = self.price_extractor.extract_unit_price(combined_text)
        unit_price = None
        unit = None
        if unit_price_result:
            unit_price, unit = unit_price_result
            unit = self.unit_calculator.normalize_unit(unit)
        
        # Extract special offer
        special_offer = self.text_cleaner.detect_special_offer(combined_text)
        
        # Calculate bounding box position
        position = self._calculate_region_position(region)
        
        # Generate product ID
        product_id = f"prod-{uuid.uuid4().hex[:8]}"
        
        # Create Product
        product = Product(
            id=product_id,
            name=name_without_qty or cleaned_name,
            description=quantity if quantity else None,
            price=price,
            unit_price=unit_price,
            unit=f"per {unit}" if unit else None,
            currency="AUD",
            special_offer=special_offer if special_offer else None,
            position=position,
            confidence=region.average_confidence
        )
        
        logger.info(f"Extracted product: {product.name} - ${product.price}")
        return product
    
    def _extract_product_name(self, text: str) -> str:
        """
        Extract product name from text.
        
        Args:
            text: Combined region text
            
        Returns:
            Extracted product name
        """
        # Remove prices and unit prices from text
        cleaned = re.sub(r'\$\d+\.\d{2}', '', text)
        cleaned = re.sub(r'\d+\.\d{2}\s*(?:per|/)\s*\w+', '', cleaned)
        cleaned = re.sub(r'\([^)]*\)', '', cleaned)  # Remove parentheses content
        
        # Clean and return
        cleaned = self.text_validator.clean_text(cleaned)
        return cleaned
    
    def _calculate_region_position(self, region: ProductRegion) -> Optional[Position]:
        """
        Calculate bounding box for entire region.
        
        Args:
            region: ProductRegion with text detections
            
        Returns:
            Position object or None
        """
        if not region.texts:
            return None
        
        # Find min/max coordinates
        all_x = []
        all_y = []
        
        for result in region.texts:
            bbox = result.bbox
            all_x.extend([bbox.top_left[0], bbox.bottom_right[0]])
            all_y.extend([bbox.top_left[1], bbox.bottom_right[1]])
        
        min_x = min(all_x)
        min_y = min(all_y)
        max_x = max(all_x)
        max_y = max(all_y)
        
        return Position(
            x=min_x,
            y=min_y,
            width=max_x - min_x,
            height=max_y - min_y
        )
    
    def validate_product(self, product: Product) -> Tuple[bool, List[str]]:
        """
        Validate extracted product data.
        
        Args:
            product: Product to validate
            
        Returns:
            Tuple of (is_valid, error_messages)
        """
        errors = []
        
        # Validate price
        if not self.price_validator.is_valid_price(product.price):
            errors.append(f"Invalid price: ${product.price}")
        
        # Validate unit price if present
        if product.unit_price and product.description:
            # Try to extract quantity from description
            qty_match = re.search(r'(\d+)\s*(\w+)', product.description)
            if qty_match:
                qty_val = float(qty_match.group(1))
                qty_unit = qty_match.group(2)
                
                is_valid = self.unit_calculator.validate_unit_price(
                    total_price=product.price,
                    unit_price=product.unit_price,
                    quantity=qty_val,
                    unit=qty_unit
                )
                
                if not is_valid:
                    errors.append(f"Unit price mismatch: ${product.unit_price}")
        
        # Validate product name
        if not self.text_validator.is_valid_product_name(product.name):
            errors.append(f"Invalid product name: '{product.name}'")
        
        is_valid = len(errors) == 0
        return is_valid, errors
