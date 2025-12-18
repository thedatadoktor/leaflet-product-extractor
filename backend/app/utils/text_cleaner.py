"""
Text cleaning and normalization for product names and descriptions.
"""
import re
from typing import List
from app.core.logging import app_logger as logger


class TextCleaner:
    """Clean and normalize extracted text"""
    
    # Common OCR errors and corrections
    OCR_CORRECTIONS = {
        '0': 'O',  # Zero to letter O in some contexts
        'l': '1',  # Lowercase L to 1 in numeric contexts
        '5': 'S',  # 5 to S in some contexts
    }
    
    # Words to remove from product names
    NOISE_WORDS = [
        'special', 'offer', 'buy', 'now', 'save', 'only',
        'today', 'limited', 'new', 'fresh', 'quality'
    ]
    
    # Special offer indicators
    OFFER_PATTERNS = [
        'super saver', 'special buy', 'aldi special',
        'limited time', 'while stocks last', 'special offer'
    ]
    
    @staticmethod
    def clean_product_name(text: str) -> str:
        """
        Clean and normalize product name.
        
        Args:
            text: Raw product name
            
        Returns:
            Cleaned product name
        """
        if not text:
            return ""
        
        # Remove extra whitespace
        cleaned = " ".join(text.split())
        
        # Remove special characters but keep alphanumeric and common punctuation
        cleaned = re.sub(r'[^\w\s\-\&\(\)\/]', '', cleaned)
        
        # Capitalize properly
        cleaned = cleaned.title()
        
        # Remove common noise words (case insensitive)
        words = cleaned.split()
        words = [w for w in words if w.lower() not in TextCleaner.NOISE_WORDS]
        cleaned = " ".join(words)
        
        logger.debug(f"Cleaned product name: '{text}' -> '{cleaned}'")
        return cleaned.strip()
    
    @staticmethod
    def extract_quantity_from_name(text: str) -> tuple[str, str]:
        """
        Extract quantity information from product name.
        
        Args:
            text: Product name with potential quantity
            
        Returns:
            Tuple of (cleaned_name, quantity) - quantity is lowercase
        """
        # Patterns: 250g, 500ml, 1kg, 2L, 6 Pack
        quantity_patterns = [
            r'(\d+\s*(?:g|kg|ml|l|pack))',
            r'(\d+\s*x\s*\d+\s*(?:g|ml))',
        ]
        
        quantity = ""
        cleaned_name = text
        
        for pattern in quantity_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                quantity = match.group(1).strip().lower()  # Convert to lowercase
                # Remove quantity from name
                cleaned_name = re.sub(pattern, '', text, flags=re.IGNORECASE)
                break
        
        cleaned_name = " ".join(cleaned_name.split()).strip()
        
        if quantity:
            logger.debug(f"Extracted quantity '{quantity}' from '{text}'")
        
        return (cleaned_name, quantity)
    
    @staticmethod
    def detect_special_offer(text: str) -> str:
        """
        Detect special offer text.
        
        Args:
            text: Text to search for offer indicators
            
        Returns:
            Special offer text or empty string
        """
        text_lower = text.lower()
        
        for pattern in TextCleaner.OFFER_PATTERNS:
            if pattern in text_lower:
                # Extract the actual offer text
                match = re.search(pattern, text_lower, re.IGNORECASE)
                if match:
                    offer_text = text[match.start():match.end()]
                    logger.debug(f"Detected special offer: '{offer_text}'")
                    return offer_text.title()
        
        return ""
    
    @staticmethod
    def normalize_whitespace(text: str) -> str:
        """
        Normalize all whitespace to single spaces.
        
        Args:
            text: Input text
            
        Returns:
            Text with normalized whitespace
        """
        return " ".join(text.split())
    
    @staticmethod
    def remove_symbols(text: str, keep: str = "") -> str:
        """
        Remove special symbols from text.
        
        Args:
            text: Input text
            keep: String of symbols to keep
            
        Returns:
            Text without symbols
        """
        # Build pattern: keep alphanumeric, spaces, and specified symbols
        pattern = f'[^\\w\\s{re.escape(keep)}]'
        cleaned = re.sub(pattern, '', text)
        return cleaned
    
    @staticmethod
    def extract_brand(text: str, known_brands: List[str]) -> str:
        """
        Extract brand name from product text.
        
        Args:
            text: Product text
            known_brands: List of known brand names
            
        Returns:
            Brand name or empty string
        """
        text_lower = text.lower()
        
        for brand in known_brands:
            if brand.lower() in text_lower:
                logger.debug(f"Detected brand: '{brand}'")
                return brand
        
        return ""
    
    @staticmethod
    def clean_description(text: str) -> str:
        """
        Clean product description text.
        
        Args:
            text: Raw description
            
        Returns:
            Cleaned description
        """
        # Remove extra whitespace
        cleaned = TextCleaner.normalize_whitespace(text)
        
        # Remove multiple punctuation
        cleaned = re.sub(r'([.!?]){2,}', r'\1', cleaned)
        
        # Capitalize sentences
        sentences = cleaned.split('. ')
        sentences = [s.capitalize() for s in sentences]
        cleaned = '. '.join(sentences)
        
        return cleaned.strip()
