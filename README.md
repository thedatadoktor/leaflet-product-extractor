# Leaflet Product Extractor

An AI-powered application that extracts product information from grocery store leaflet images using advanced OCR and intelligent parsing. Built with FastAPI, React, and EasyOCR for production-ready product data extraction.

## Features

- **Advanced OCR**: EasyOCR-powered text extraction with confidence filtering
- **Smart Parsing**: Intelligent product clustering using spatial analysis and price detection
- **Interactive UI**: React + TypeScript frontend with drag-and-drop upload
- **RESTful API**: FastAPI backend with automatic OpenAPI documentation
- **Image Processing**: OpenCV and Pillow for optimal OCR preprocessing
- **Data Export**: Timestamped JSON exports with structured product data
- **Production Ready**: Docker support, comprehensive testing, and CI/CD
- **Type Safety**: Full TypeScript coverage with shared type definitions
- **Real-time Processing**: Live extraction progress with detailed feedback

## Tech Stack

- **Backend**: FastAPI 0.104.1, Python 3.8+
- **Frontend**: React 18, TypeScript, Axios
- **OCR Engine**: EasyOCR 1.7.1
- **Image Processing**: OpenCV, Pillow, NumPy
- **Database**: JSON file-based storage
- **Testing**: Pytest (96% coverage), Jest + React Testing Library
- **Deployment**: Docker, Docker Compose
- **Documentation**: FastAPI OpenAPI/Swagger

## Prerequisites

- Python 3.8+
- Node.js 16+
- Git

## Quick Start

### Local Development Setup

1. **Clone the repository**:
```bash
git clone https://github.com/yourusername/leaflet-product-extractor.git
cd leaflet-product-extractor
```

2. **Start the backend**:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements-dev.txt
cp .env.example .env
uvicorn app.main:app --reload
```

3. **Start the frontend** (in a new terminal):
```bash
cd frontend
npm install
cp .env.example .env
npm start
```

### Using Docker

1. **Start all services**:
```bash
docker-compose up --build
```

2. **Access the application**:
- Frontend: `http://localhost:3000`
- Backend API: `http://localhost:8000`
- API Documentation: `http://localhost:8000/docs`

## Environment Variables

### Backend (.env)
```env
# Application Settings
APP_NAME=Leaflet Product Extractor
APP_VERSION=1.0.0
DEBUG=True
ENVIRONMENT=development

# Server Configuration
HOST=0.0.0.0
PORT=8000

# CORS Settings
CORS_ORIGINS=["http://localhost:3000", "http://127.0.0.1:3000"]

# OCR Configuration
OCR_LANGUAGES=["en"]
OCR_GPU=False
OCR_CONFIDENCE_THRESHOLD=0.5

# File Processing
MAX_UPLOAD_SIZE=10485760  # 10MB
IMAGE_RESIZE_MAX_WIDTH=2000
IMAGE_RESIZE_MAX_HEIGHT=2000
```

### Frontend (.env)
```env
REACT_APP_API_URL=http://localhost:8000
```

## API Documentation

### Interactive Documentation (Swagger UI)
- **Local**: `http://localhost:8000/docs`
- **Production**: `https://your-app.com/docs`

### Alternative Documentation (ReDoc)
- **Local**: `http://localhost:8000/redoc`  
- **Production**: `https://your-app.com/redoc`

The interactive Swagger UI allows you to:
- ✅ View all available endpoints
- ✅ Test API calls directly in the browser
- ✅ Upload images and see extraction results
- ✅ Download generated JSON exports
- ✅ View detailed request/response schemas

### Endpoints

| Method | Endpoint | Description | Content Type |
|--------|----------|-------------|--------------|
| POST | `/api/v1/extract` | Extract products from image | multipart/form-data |
| GET | `/api/v1/extractions` | List recent extractions | application/json |
| GET | `/api/v1/extractions/{id}` | Get specific extraction | application/json |
| GET | `/health` | API health check | application/json |
| GET | `/` | API information | application/json |

### Example Usage

#### Extract products from an image:
```bash
curl -X POST http://localhost:8000/api/v1/extract \
  -H "accept: application/json" \
  -F "file=@leaflet.jpg"
```

#### Response:
```json
{
  "success": true,
  "message": "Successfully extracted 15 products",
  "products": [
    {
      "id": "prod-abc123",
      "name": "Mini Cucumbers",
      "description": "Brussels Sprouts 250g Pack",
      "price": 3.49,
      "unit_price": 1.40,
      "unit": "per kg",
      "currency": "AUD",
      "special_offer": "Super Saver",
      "position": {"x": 45, "y": 120, "width": 200, "height": 150},
      "confidence": 0.95
    }
  ],
  "total_products": 15,
  "processing_time_seconds": 4.5,
  "json_file": "data/output/products_20240115_103000.json"
}
```

## Testing

Run comprehensive test suites for both backend and frontend:

### Backend Testing (96% Coverage)
```bash
cd backend

# Run all tests with coverage
pytest --cov=app

# Run specific test modules
pytest tests/unit/test_parser_service.py
pytest tests/integration/test_api.py

# Run tests with detailed output
pytest -v --cov=app --cov-report=html
```

### Frontend Testing
```bash
cd frontend

# Run all tests
npm test

# Run tests with coverage
npm test -- --coverage --watchAll=false

# Run tests in CI mode
npm run test:coverage
```

## Performance & Processing

- **Average Processing Time**: 3-8 seconds per image
- **Supported File Formats**: JPG, JPEG, PNG, PDF
- **Maximum File Size**: 10MB
- **OCR Confidence Threshold**: 50% (configurable)
- **Concurrent Extractions**: Up to 3 simultaneous processes

## Architecture Overview

### Data Flow
1. **Image Upload**: React frontend with drag-and-drop support
2. **File Validation**: Size, format, and content validation
3. **Image Preprocessing**: OpenCV optimization for OCR accuracy
4. **OCR Extraction**: EasyOCR text detection with bounding boxes
5. **Smart Parsing**: Price-based clustering and spatial analysis
6. **Product Structuring**: Name extraction, unit price calculation
7. **JSON Export**: Timestamped file generation
8. **Frontend Display**: Interactive table with sorting and filtering

### Backend Services
- **OCR Service**: EasyOCR wrapper with confidence filtering
- **Parser Service**: Intelligent product clustering and extraction
- **Export Service**: JSON file management and metadata tracking
- **Image Processor**: Preprocessing pipeline for optimal OCR
- **File Handler**: Upload management and cleanup

### Frontend Components
- **App**: Main application state management
- **UploadForm**: Drag-and-drop file upload with progress
- **ProductTable**: Sortable, searchable product display
- **ProductDetails**: Modal for detailed product information
- **API Service**: Type-safe HTTP client with error handling

## Project Structure
```
leaflet-product-extractor/
├── backend/                    # FastAPI backend
│   ├── app/
│   │   ├── api/               # API routes and endpoints
│   │   │   ├── deps.py       # Dependency injection
│   │   │   └── routes.py     # Main API routes
│   │   ├── core/              # Core configuration
│   │   │   ├── config.py     # App settings
│   │   │   └── logging.py    # Logging configuration
│   │   ├── models/            # Data models
│   │   │   └── product.py    # Product data structures
│   │   ├── schemas/           # Pydantic schemas
│   │   │   └── product.py    # API request/response models
│   │   ├── services/          # Business logic
│   │   │   ├── ocr_service.py      # EasyOCR integration
│   │   │   ├── parser_service.py   # Product parsing logic
│   │   │   └── export_service.py   # JSON export handling
│   │   ├── utils/             # Utility functions
│   │   │   ├── image_processor.py  # Image preprocessing
│   │   │   ├── price_extractor.py  # Price detection
│   │   │   ├── text_cleaner.py     # Text normalization
│   │   │   └── validators.py       # Data validation
│   │   └── main.py           # FastAPI application
│   ├── tests/                 # Test suites
│   │   ├── unit/             # Unit tests
│   │   └── integration/      # Integration tests
│   ├── requirements.txt      # Production dependencies
│   ├── requirements-dev.txt  # Development dependencies
│   └── Dockerfile           # Backend Docker image
├── frontend/                  # React TypeScript frontend
│   ├── src/
│   │   ├── components/       # React components
│   │   │   ├── UploadForm.tsx     # File upload component
│   │   │   ├── ProductTable.tsx   # Product display table
│   │   │   └── ProductDetails.tsx # Product detail modal
│   │   ├── services/         # API integration
│   │   │   └── api.ts       # HTTP client service
│   │   ├── types/           # TypeScript definitions
│   │   │   └── product.ts   # Shared type definitions
│   │   ├── App.tsx          # Main application component
│   │   └── index.tsx        # Application entry point
│   ├── package.json         # Frontend dependencies
│   └── Dockerfile          # Frontend Docker image
├── data/                    # Data storage
│   ├── input/              # Uploaded images (temporary)
│   └── output/             # Generated JSON exports
├── docs/                   # Documentation
├── scripts/                # Utility scripts
├── docker-compose.yml      # Multi-container setup
├── .pre-commit-config.yaml # Code quality hooks
└── README.md              # This file
```

## Development Commands

### Backend
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements-dev.txt

# Run development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Run tests
pytest --cov=app

# Code formatting
black app/
isort app/

# Type checking
mypy app/

# Run linting
flake8 app/
pylint app/
```

### Frontend
```bash
# Install dependencies
npm install

# Start development server
npm start

# Run tests
npm test

# Build for production
npm run build

# Type checking
npx tsc --noEmit
```

## Docker Commands

```bash
# Build and start all services
docker-compose up --build

# Start in detached mode
docker-compose up -d

# View logs
docker-compose logs backend
docker-compose logs frontend

# Execute commands in containers
docker-compose exec backend pytest
docker-compose exec frontend npm test

# Stop all services
docker-compose down

# Remove volumes (clean slate)
docker-compose down -v
```

## Security Features

- **File Validation**: Strict file type and size validation
- **Input Sanitization**: Text cleaning and validation
- **CORS Configuration**: Controlled cross-origin requests
- **Error Handling**: Secure error responses without sensitive data
- **File Cleanup**: Automatic temporary file removal
- **Rate Limiting**: Built-in FastAPI rate limiting support

## Contributing

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/new-feature`
3. **Install pre-commit hooks**: `pre-commit install`
4. **Make changes** with proper testing
5. **Run tests**: `pytest` (backend) and `npm test` (frontend)
6. **Commit changes**: `git commit -am 'feat: add new feature'`
7. **Push to branch**: `git push origin feature/new-feature`
8. **Submit a Pull Request**

## Commit Message Convention

This project follows conventional commit messages:

- `feat:` - New features
- `fix:` - Bug fixes
- `docs:` - Documentation updates
- `test:` - Test additions/updates
- `refactor:` - Code refactoring
- `perf:` - Performance improvements
- `config:` - Configuration changes

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Authors

- **Your Name** - *Initial work* - [https://github.com/yourusername](https://github.com/yourusername)

## Acknowledgments

- **FastAPI** team for the excellent framework
- **EasyOCR** developers for the powerful OCR engine
- **React** team for the frontend framework
- **OpenCV** community for image processing tools
- The open-source community for the amazing tools

## Support

If you have any questions or need help, please:

1. Check the [API Documentation](http://localhost:8000/docs)
2. Look at existing [Issues](https://github.com/yourusername/leaflet-product-extractor/issues)
3. Create a new issue with detailed information
4. Include sample images and error messages for faster resolution

## Changelog

### v1.0.0 (2024-12-18)
- Initial release
- AI-powered product extraction from leaflet images
- FastAPI backend with comprehensive OCR pipeline
- React TypeScript frontend with drag-and-drop upload
- Intelligent product parsing with spatial clustering
- JSON export functionality with timestamps
- Docker support for easy deployment
- Comprehensive test coverage (96% backend)
- Interactive API documentation with Swagger UI
- Production-ready configuration and error handling
