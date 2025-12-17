"""
Pydantic schemas for product data
"""
from typing import Optional, Dict
from pydantic import BaseModel, Field, validator


class Position(BaseModel):
    """Bounding box position in image"""
    x: int
    y: int
    width: int
    height: int


class Product(BaseModel):
    """Product extracted from leaflet"""
    id: str
    name: str
    description: Optional[str] = None
    price: float = Field(..., gt=0)
    unit_price: Optional[float] = Field(None, gt=0)
    unit: Optional[str] = None
    currency: str = "AUD"
    special_offer: Optional[str] = None
    position: Optional[Position] = None
    confidence: float = Field(..., ge=0.0, le=1.0)
    
    @validator('price', 'unit_price')
    def round_price(cls, v):
        if v is not None:
            return round(v, 2)
        return v


class ExtractionResponse(BaseModel):
    """Response model for extraction endpoint"""
    success: bool
    message: str
    products: list[Product]
    total_products: int
    processing_time_seconds: float
    json_file: Optional[str] = None