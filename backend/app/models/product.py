"""
Data models for product representation.

These are internal data structures used during processing,
separate from the API schemas.
"""
from dataclasses import dataclass
from typing import Tuple, Optional


@dataclass
class BoundingBox:
    """
    Represents a text bounding box from OCR.
    
    Attributes:
        top_left: (x, y) coordinates of top-left corner
        top_right: (x, y) coordinates of top-right corner
        bottom_right: (x, y) coordinates of bottom-right corner
        bottom_left: (x, y) coordinates of bottom-left corner
    """
    top_left: Tuple[int, int]
    top_right: Tuple[int, int]
    bottom_right: Tuple[int, int]
    bottom_left: Tuple[int, int]
    
    @property
    def center(self) -> Tuple[int, int]:
        """Calculate center point of bounding box"""
        x = (self.top_left[0] + self.bottom_right[0]) // 2
        y = (self.top_left[1] + self.bottom_right[1]) // 2
        return (x, y)
    
    @property
    def width(self) -> int:
        """Calculate width of bounding box"""
        return self.bottom_right[0] - self.top_left[0]
    
    @property
    def height(self) -> int:
        """Calculate height of bounding box"""
        return self.bottom_right[1] - self.top_left[1]
    
    @property
    def area(self) -> int:
        """Calculate area of bounding box"""
        return self.width * self.height
    
    def __repr__(self) -> str:
        return f"BoundingBox(center={self.center}, width={self.width}, height={self.height})"


@dataclass
class OCRResult:
    """
    Single OCR detection result.
    
    Attributes:
        bbox: Bounding box of detected text
        text: Extracted text content
        confidence: OCR confidence score (0.0 to 1.0)
    """
    bbox: BoundingBox
    text: str
    confidence: float
    
    def __repr__(self) -> str:
        return f"OCRResult(text='{self.text[:30]}...', confidence={self.confidence:.2f})"


@dataclass
class ProductRegion:
    """
    Represents a detected product region in the image.
    
    Attributes:
        texts: List of OCR results in this region
        bbox: Combined bounding box for the region
    """
    texts: list
    bbox: Optional[BoundingBox] = None
    
    @property
    def combined_text(self) -> str:
        """Get all text combined from this region"""
        return " ".join([result.text for result in self.texts])
    
    @property
    def average_confidence(self) -> float:
        """Calculate average confidence for this region"""
        if not self.texts:
            return 0.0
        return sum(result.confidence for result in self.texts) / len(self.texts)
