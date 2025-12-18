"""
API dependencies for dependency injection.
"""
from typing import Generator
from app.services.ocr_service import OCRService
from app.services.parser_service import ProductParser
from app.services.export_service import ExportService
from app.utils.image_processor import ImageProcessor


# Singleton instances
_ocr_service = None
_parser_service = None
_export_service = None
_image_processor = None


def get_ocr_service() -> OCRService:
    """Get OCR service instance (singleton)"""
    global _ocr_service
    if _ocr_service is None:
        _ocr_service = OCRService()
    return _ocr_service


def get_parser_service() -> ProductParser:
    """Get parser service instance (singleton)"""
    global _parser_service
    if _parser_service is None:
        _parser_service = ProductParser()
    return _parser_service


def get_export_service() -> ExportService:
    """Get export service instance (singleton)"""
    global _export_service
    if _export_service is None:
        _export_service = ExportService()
    return _export_service


def get_image_processor() -> ImageProcessor:
    """Get image processor instance (singleton)"""
    global _image_processor
    if _image_processor is None:
        _image_processor = ImageProcessor()
    return _image_processor
