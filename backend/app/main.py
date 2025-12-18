"""
FastAPI application entry point.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.logging import app_logger as logger
from app.api.routes import router as api_router


# Create FastAPI app with comprehensive metadata
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="""
    🛒 **AI-Powered Product Extraction System**
    
    Advanced OCR and machine learning pipeline for extracting structured product data from grocery store leaflet images.
    
    **Key Features:**
    - 🔍 **EasyOCR Integration** - High-accuracy text extraction with 80+ language support
    - 🧠 **Intelligent Parsing** - Spatial clustering algorithms for product recognition
    - 📊 **Structured Output** - JSON exports with product names, prices, and metadata
    - ⚡ **Fast Processing** - 3-8 second average processing time per image
    - 🔒 **Production Ready** - Comprehensive validation, testing, and error handling
    
    **Supported Formats:** JPG, JPEG, PNG, PDF (up to 10MB)
    
    **Use Cases:**
    - Retail price monitoring and analysis
    - Grocery store data collection
    - Market research and competitive analysis
    - Product catalog automation
    """,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    contact={
        "name": "Leaflet Product Extractor Support",
        "url": "https://github.com/thedatadoktor/leaflet-product-extractor",
        "email": "support@leaflet-extractor.com"
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT"
    },
    tags_metadata=[
        {
            "name": "Product Extraction",
            "description": "Core functionality for extracting product data from leaflet images using OCR and intelligent parsing algorithms."
        },
        {
            "name": "Data Management", 
            "description": "Retrieve and manage extraction results, view processing history, and download exported data."
        },
        {
            "name": "Health",
            "description": "System health monitoring and API status endpoints."
        },
        {
            "name": "Root",
            "description": "Basic API information and version details."
        }
    ]
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=settings.CORS_ALLOW_METHODS,
    allow_headers=settings.CORS_ALLOW_HEADERS,
)

# Include API routes
app.include_router(api_router, prefix="/api/v1")

# Startup event
@app.on_event("startup")
async def startup_event():
    """Run on application startup"""
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"Debug mode: {settings.DEBUG}")

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Run on application shutdown"""
    logger.info("Shutting down application")

# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """Root endpoint - API information"""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "docs": "/docs",
        "health": "/health"
    }

# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT
    }

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Handle all uncaught exceptions"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "message": "Internal server error",
            "error": str(exc) if settings.DEBUG else "An error occurred"
        }
    )
