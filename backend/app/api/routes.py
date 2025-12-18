"""
API routes for product extraction.
"""
import time
from typing import List
from fastapi import APIRouter, File, UploadFile, HTTPException, Query
from pathlib import Path

from app.schemas.product import ExtractionResponse, ErrorResponse
from app.services.ocr_service import OCRService
from app.services.parser_service import ProductParser
from app.services.export_service import ExportService
from app.utils.image_processor import ImageProcessor
from app.utils.validators import FileValidator
from app.utils.file_handler import FileHandler
from app.core.config import settings
from app.core.logging import app_logger as logger


# Create router
router = APIRouter()

# Initialize services (will be created on first request)
ocr_service = None
parser_service = None
export_service = None
image_processor = None
file_handler = None


def get_services():
    """Lazy initialization of services"""
    global ocr_service, parser_service, export_service, image_processor, file_handler
    
    if ocr_service is None:
        ocr_service = OCRService()
    if parser_service is None:
        parser_service = ProductParser()
    if export_service is None:
        export_service = ExportService()
    if image_processor is None:
        image_processor = ImageProcessor()
    if file_handler is None:
        file_handler = FileHandler()
    
    return ocr_service, parser_service, export_service, image_processor, file_handler


@router.post(
    "/extract",
    response_model=ExtractionResponse,
    responses={
        400: {"model": ErrorResponse},
        500: {"model": ErrorResponse}
    },
    tags=["Extraction"]
)
async def extract_products(
    file: UploadFile = File(..., description="Image file (JPG, PNG, PDF)")
):
    """
    Extract products from a leaflet image.
    
    This endpoint:
    1. Validates the uploaded file
    2. Preprocesses the image
    3. Performs OCR text extraction
    4. Parses products from OCR results
    5. Exports results to JSON
    
    Returns structured product data with prices, names, and metadata.
    """
    start_time = time.time()
    
    try:
        # Validate file
        file_content = await file.read()
        file_size = len(file_content)
        
        is_valid, error_msg = FileValidator.validate_file(file.filename, file_size)
        if not is_valid:
            raise HTTPException(status_code=400, detail=error_msg)
        
        logger.info(f"Processing file: {file.filename} ({file_size} bytes)")
        
        # Get services
        ocr, parser, exporter, processor, handler = get_services()
        
        # Save uploaded file
        filepath = handler.save_upload_sync(file_content, file.filename)
        
        try:
            # Preprocess image
            logger.info("Preprocessing image...")
            processed_image = processor.preprocess(filepath)
            
            # Perform OCR
            logger.info("Performing OCR...")
            ocr_results = ocr.extract_text(processed_image)
            logger.info(f"OCR found {len(ocr_results)} text regions")
            
            # Parse products
            logger.info("Parsing products...")
            products = parser.parse_products(ocr_results)
            logger.info(f"Parsed {len(products)} products")
            
            # Calculate processing time
            processing_time = time.time() - start_time
            
            # Export to JSON
            json_filepath = exporter.export_to_json(
                products=products,
                source_image=file.filename,
                processing_time=processing_time
            )
            
            # Create response
            return ExtractionResponse(
                success=True,
                message=f"Successfully extracted {len(products)} products",
                products=products,
                total_products=len(products),
                processing_time_seconds=round(processing_time, 2),
                json_file=json_filepath
            )
            
        finally:
            # Cleanup uploaded file
            handler.cleanup_file(filepath)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Extraction failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Extraction failed: {str(e)}"
        )


@router.get(
    "/extractions",
    response_model=dict,
    tags=["Extraction"]
)
async def list_extractions(
    limit: int = Query(10, ge=1, le=50, description="Maximum number of results")
):
    """
    List recent extractions.
    
    Returns a list of recent extraction results with metadata.
    """
    try:
        _, _, exporter, _, _ = get_services()
        
        exports = exporter.list_exports(limit=limit)
        
        return {
            "success": True,
            "extractions": exports,
            "total": len(exports)
        }
    
    except Exception as e:
        logger.error(f"Failed to list extractions: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list extractions: {str(e)}"
        )


@router.get(
    "/extractions/{extraction_id}",
    response_model=dict,
    tags=["Extraction"]
)
async def get_extraction(extraction_id: str):
    """
    Get a specific extraction by ID.
    
    Returns the full extraction data including all products.
    """
    try:
        _, _, exporter, _, _ = get_services()
        
        # Find the extraction file
        exports = exporter.list_exports(limit=100)
        
        for export in exports:
            if export.get("extraction_id") == extraction_id:
                data = exporter.load_from_json(export["filepath"])
                return {
                    "success": True,
                    "extraction": data
                }
        
        raise HTTPException(
            status_code=404,
            detail=f"Extraction {extraction_id} not found"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get extraction: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get extraction: {str(e)}"
        )
