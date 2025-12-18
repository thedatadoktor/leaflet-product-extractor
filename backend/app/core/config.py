"""
Application configuration using Pydantic Settings.

This module handles all environment-based configuration for the application.
"""
from typing import List
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Application
    APP_NAME: str = Field(default="Leaflet Product Extractor")
    APP_VERSION: str = Field(default="1.0.0")
    DEBUG: bool = Field(default=True)
    ENVIRONMENT: str = Field(default="development")
    
    # Server
    HOST: str = Field(default="0.0.0.0")
    PORT: int = Field(default=8000)
    
    # CORS - allows frontend to communicate with backend
    CORS_ORIGINS: List[str] = Field(
        default=["http://localhost:3000", "http://127.0.0.1:3000"]
    )
    CORS_ALLOW_CREDENTIALS: bool = Field(default=True)
    CORS_ALLOW_METHODS: List[str] = Field(default=["*"])
    CORS_ALLOW_HEADERS: List[str] = Field(default=["*"])
    
    # OCR Settings
    OCR_LANGUAGES: List[str] = Field(default=["en"])
    OCR_GPU: bool = Field(default=False)
    OCR_CONFIDENCE_THRESHOLD: float = Field(default=0.5, ge=0.0, le=1.0)
    OCR_MODEL_STORAGE_DIRECTORY: str = Field(default="./.EasyOCR/")
    
    # Image Processing
    MAX_UPLOAD_SIZE: int = Field(default=10485760)  # 10MB in bytes
    ALLOWED_EXTENSIONS: List[str] = Field(
        default=[".jpg", ".jpeg", ".png", ".pdf"]
    )
    IMAGE_RESIZE_MAX_WIDTH: int = Field(default=2000)
    IMAGE_RESIZE_MAX_HEIGHT: int = Field(default=2000)
    
    # File Paths
    OUTPUT_DIRECTORY: str = Field(default="../data/output")
    INPUT_DIRECTORY: str = Field(default="../data/input")
    
    # Logging
    LOG_LEVEL: str = Field(default="INFO")
    LOG_FILE: str = Field(default="logs/app.log")
    
    # Processing
    MAX_CONCURRENT_EXTRACTIONS: int = Field(default=3)
    EXTRACTION_TIMEOUT_SECONDS: int = Field(default=300)
    
    class Config:
        """Pydantic config"""
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"  # Ignore extra fields in .env


# Create global settings instance
settings = Settings()
