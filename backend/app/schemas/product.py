"""
Pydantic schemas for API request/response validation.

These schemas define the structure of data sent to/from the API.
"""
from typing import Optional, List
from pydantic import BaseModel, Field, field_validator
from datetime import datetime


class Position(BaseModel):
    """Bounding box position in image"""
    x: int = Field(..., ge=0, description="X coordinate")
    y: int = Field(..., ge=0, description="Y coordinate")
    width: int = Field(..., gt=0, description="Width in pixels")
    height: int = Field(..., gt=0, description="Height in pixels")
    
    class Config:
        json_schema_extra = {
            "example": {
                "x": 45,
                "y": 120,
                "width": 200,
                "height": 150
            }
        }


class Product(BaseModel):
    """Product extracted from leaflet"""
    id: str = Field(..., description="Unique product identifier")
    name: str = Field(..., min_length=1, description="Product name")
    description: Optional[str] = Field(None, description="Product description")
    price: float = Field(..., gt=0, description="Product price")
    unit_price: Optional[float] = Field(None, gt=0, description="Price per unit")
    unit: Optional[str] = Field(None, description="Unit of measurement")
    currency: str = Field(default="AUD", description="Currency code")
    special_offer: Optional[str] = Field(None, description="Special offer text")
    position: Optional[Position] = Field(None, description="Position in image")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Extraction confidence")
    
    @field_validator('price', 'unit_price')
    @classmethod
    def round_price(cls, v):
        """Round prices to 2 decimal places"""
        if v is not None:
            return round(v, 2)
        return v
    
    @field_validator('name', 'description')
    @classmethod
    def strip_whitespace(cls, v):
        """Strip leading/trailing whitespace"""
        if v is not None:
            return v.strip()
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "prod-001",
                "name": "Mini Cucumbers",
                "description": "Brussels Sprouts 250g Pack",
                "price": 3.49,
                "unit_price": 1.40,
                "unit": "per kg",
                "currency": "AUD",
                "special_offer": "Super Saver",
                "position": {
                    "x": 45,
                    "y": 120,
                    "width": 200,
                    "height": 150
                },
                "confidence": 0.95
            }
        }


class ExtractionResponse(BaseModel):
    """Response model for extraction endpoint"""
    success: bool = Field(..., description="Whether extraction was successful")
    message: str = Field(..., description="Status message")
    products: List[Product] = Field(default_factory=list, description="Extracted products")
    total_products: int = Field(..., ge=0, description="Total number of products")
    processing_time_seconds: float = Field(..., ge=0, description="Processing time")
    json_file: Optional[str] = Field(None, description="Path to generated JSON file")
    extraction_id: Optional[str] = Field(None, description="Unique extraction ID")
    timestamp: Optional[datetime] = Field(default_factory=datetime.now, description="Extraction timestamp")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Successfully extracted 15 products",
                "products": [],
                "total_products": 15,
                "processing_time_seconds": 4.5,
                "json_file": "data/output/products_20240115_103000.json",
                "extraction_id": "ext-abc123",
                "timestamp": "2024-01-15T10:30:00"
            }
        }


class HealthResponse(BaseModel):
    """Health check response"""
    status: str = Field(..., description="Service status")
    version: str = Field(..., description="Application version")
    environment: str = Field(..., description="Environment name")
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "version": "1.0.0",
                "environment": "development"
            }
        }


class ErrorResponse(BaseModel):
    """Error response model"""
    success: bool = Field(default=False, description="Always false for errors")
    message: str = Field(..., description="Error message")
    error_code: Optional[str] = Field(None, description="Error code")
    details: Optional[dict] = Field(None, description="Additional error details")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": False,
                "message": "Invalid file format",
                "error_code": "INVALID_FILE_FORMAT",
                "details": {"allowed_formats": [".jpg", ".png", ".pdf"]}
            }
        }
