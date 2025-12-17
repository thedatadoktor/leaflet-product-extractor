"""
Data models for product representation
"""
from dataclasses import dataclass
from typing import Optional, Tuple


@dataclass
class BoundingBox:
    """Represents text bounding box from OCR"""
    top_left: Tuple[int, int]
    top_right: Tuple[int, int]
    bottom_right: Tuple[int, int]
    bottom_left: Tuple[int, int]
    
    @property
    def center(self) -> Tuple[int, int]:
        """Calculate center point"""
        x = (self.top_left[0] + self.bottom_right[0]) // 2
        y = (self.top_left[1] + self.bottom_right[1]) // 2
        return (x, y)
    
    @property
    def width(self) -> int:
        return self.bottom_right[0] - self.top_left[0]
    
    @property
    def height(self) -> int:
        return self.bottom_right[1] - self.top_left[1]


@dataclass
class OCRResult:
    """Single OCR detection result"""
    bbox: BoundingBox
    text: str
    confidence: float