"""
Product parser service - extracts structured product data from OCR results.
"""
import re
import uuid
from typing import List, Optional, Tuple

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
        """Parse OCR results into structured products."""
        logger.info(f"Parsing {len(ocr_results)} OCR results into products")
        
        # Log all OCR text for debugging
        logger.info("=== OCR EXTRACTED TEXT ===")
        for i, result in enumerate(ocr_results):
            logger.info(f"  [{i}] '{result.text}' (confidence: {result.confidence:.2f})")
        logger.info("=== END OCR TEXT ===")
        
        # Find all price locations first
        price_regions = self._find_price_regions(ocr_results)
        logger.info(f"Found {len(price_regions)} price-based regions")
        
        # Extract products from each price region
        products = []
        for i, region in enumerate(price_regions):
            try:
                product = self._extract_product_from_region(region, index=i)
                if product:
                    products.append(product)
                    logger.info(f"Successfully extracted product {len(products)}: {product.name}")
            except Exception as e:
                logger.warning(f"Failed to parse region {i}: {e}")
                continue
        
        logger.info(f"Successfully parsed {len(products)} products")
        return products
    
    def _find_price_regions(self, ocr_results: List[OCRResult]) -> List[ProductRegion]:
        """Find product regions by clustering text around prices."""
        # Find all OCR results that contain prices (with or without $)
        price_results = []
        
        for result in ocr_results:
            # Try to extract price with $ sign
            price = self.price_extractor.extract_price(result.text, exclude_unit_prices=True)
            
            # If no price with $, try to find standalone numbers that look like prices
            if not price:
                # Look for patterns like "3.49" or "10.99" or just "5"
                match = re.search(r'(\d+\.\d{2})|(\d+)', result.text)
                if match:
                    try:
                        price = float(match.group(0))
                    except:
                        price = None
            
            if price and self.price_validator.is_valid_price(price):
                price_results.append((result, price))
                logger.info(f"Found price ${price} in: '{result.text}'")
        
        logger.info(f"Found {len(price_results)} prices in OCR results")
        
        if not price_results:
            logger.warning("No prices found in OCR results")
            # FALLBACK: If no prices found, create regions from all text
            # This helps with images where OCR doesn't detect prices well
            logger.info("Using fallback: creating regions from spatial clustering")
            return self._fallback_spatial_clustering(ocr_results)
        
        # For each price, gather nearby text
        regions = []
        radius = 200
        used_results = set()
        
        for price_result, price_value in price_results:
            price_center = price_result.bbox.center
            region_texts = [price_result]
            used_results.add(id(price_result))
            
            # Find all text near this price
            nearby_texts = []
            for result in ocr_results:
                if id(result) in used_results:
                    continue
                
                result_center = result.bbox.center
                distance = ((price_center[0] - result_center[0]) ** 2 + 
                           (price_center[1] - result_center[1]) ** 2) ** 0.5
                
                if distance < radius:
                    nearby_texts.append((result, distance))
            
            nearby_texts.sort(key=lambda x: x[1])
            for result, _ in nearby_texts[:10]:
                region_texts.append(result)
                used_results.add(id(result))
            
            if region_texts:
                regions.append(ProductRegion(texts=region_texts))
        
        return regions
    
    def _fallback_spatial_clustering(self, ocr_results: List[OCRResult]) -> List[ProductRegion]:
        """
        Fallback method: Cluster text by spatial proximity when no prices found.
        """
        if not ocr_results:
            return []
        
        # Sort by position
        sorted_results = sorted(ocr_results, key=lambda r: (r.bbox.center[1], r.bbox.center[0]))
        
        regions = []
        used = set()
        
        for result in sorted_results:
            if id(result) in used:
                continue
            
            # Start new region
            region_texts = [result]
            used.add(id(result))
            center = result.bbox.center
            
            # Find nearby text
            for other in sorted_results:
                if id(other) in used:
                    continue
                
                distance = ((center[0] - other.bbox.center[0]) ** 2 + 
                           (center[1] - other.bbox.center[1]) ** 2) ** 0.5
                
                if distance < 150:
                    region_texts.append(other)
                    used.add(id(other))
            
            if len(region_texts) >= 2:  # At least 2 texts to form a product
                regions.append(ProductRegion(texts=region_texts))
        
        logger.info(f"Fallback created {len(regions)} regions")
        return regions
    
    def _extract_product_from_region(
        self, 
        region: ProductRegion,
        index: int
    ) -> Optional[Product]:
        """Extract product data from a text region."""
        combined_text = region.combined_text
        logger.debug(f"Region {index} text: '{combined_text[:150]}'")
        
        # Extract price - be lenient, accept numbers without $
        price = self.price_extractor.extract_price(combined_text, exclude_unit_prices=True)
        if not price:
            # Try to find any number that could be a price
            match = re.search(r'(\d+\.\d{2})|(\d+)', combined_text)
            if match:
                try:
                    price = float(match.group(0))
                except:
                    pass
        
        if not price or not self.price_validator.is_valid_price(price):
            logger.debug(f"No valid price in region {index}")
            return None
        
        # Extract product name
        product_name = self._extract_product_name_lenient(region, combined_text)
        
        if not product_name or len(product_name.strip()) < 2:
            logger.debug(f"No valid name in region {index}")
            return None
        
        # Clean product name
        cleaned_name = self.text_cleaner.clean_product_name(product_name)
        name_without_qty, quantity = self.text_cleaner.extract_quantity_from_name(cleaned_name)
        final_name = name_without_qty if name_without_qty and len(name_without_qty) > 2 else cleaned_name
        
        # Extract unit price
        unit_price_result = self.price_extractor.extract_unit_price(combined_text)
        unit_price = None
        unit = None
        if unit_price_result:
            unit_price, unit = unit_price_result
            unit = self.unit_calculator.normalize_unit(unit)
        
        # Extract special offer
        special_offer = self.text_cleaner.detect_special_offer(combined_text)
        
        # Calculate position
        position = self._calculate_region_position(region)
        
        # Create Product
        product = Product(
            id=f"prod-{uuid.uuid4().hex[:8]}",
            name=final_name,
            description=quantity if quantity else None,
            price=price,
            unit_price=unit_price,
            unit=f"per {unit}" if unit else None,
            currency="AUD",
            special_offer=special_offer if special_offer else None,
            position=position,
            confidence=region.average_confidence
        )
        
        return product
    
    def _extract_product_name_lenient(self, region: ProductRegion, combined_text: str) -> str:
        """Extract product name with lenient rules."""
        # Sort by size (larger text = product name)
        sorted_by_size = sorted(region.texts, key=lambda r: r.bbox.area, reverse=True)
        
        for result in sorted_by_size:
            candidate = result.text.strip()
            
            # Skip if only numbers
            if re.match(r'^[\d\$\.\s]+$', candidate):
                continue
            
            if len(candidate) >= 2:
                # Clean it
                cleaned = re.sub(r'\$?\d+\.\d{2}', '', candidate)
                cleaned = re.sub(r'\b\d+\b', '', cleaned)
                cleaned = cleaned.strip()
                
                if len(cleaned) >= 2:
                    words = cleaned.split()
                    return ' '.join(words[:8]) if len(words) > 8 else cleaned
        
        # Fallback
        cleaned = re.sub(r'\$?\d+\.\d{2}', '', combined_text)
        cleaned = self.text_validator.clean_text(cleaned)
        words = cleaned.split()
        return ' '.join(words[:8]) if len(words) > 8 else cleaned
    
    def _calculate_region_position(self, region: ProductRegion) -> Optional[Position]:
        """Calculate bounding box for entire region."""
        if not region.texts:
            return None
        
        all_x = []
        all_y = []
        
        for result in region.texts:
            bbox = result.bbox
            all_x.extend([bbox.top_left[0], bbox.bottom_right[0]])
            all_y.extend([bbox.top_left[1], bbox.bottom_right[1]])
        
        return Position(
            x=min(all_x),
            y=min(all_y),
            width=max(all_x) - min(all_x),
            height=max(all_y) - min(all_y)
        )
    
    def validate_product(self, product: Product) -> Tuple[bool, List[str]]:
        """Validate extracted product data."""
        errors = []
        
        if not self.price_validator.is_valid_price(product.price):
            errors.append(f"Invalid price: ${product.price}")
        
        if len(product.name.strip()) < 2:
            errors.append(f"Invalid product name: '{product.name}'")
        
        return len(errors) == 0, errors
