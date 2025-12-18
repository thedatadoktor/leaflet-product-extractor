# Leaflet Product Extractor

An AI-powered application that extracts product information from grocery store leaflet images using advanced OCR and intelligent parsing. Built with FastAPI, React, and EasyOCR for production-ready product data extraction and analysis.

## Features

- **Advanced OCR**: EasyOCR-powered text extraction with confidence filtering and bounding box detection
- **Smart Parsing**: Intelligent product clustering using spatial analysis and price detection algorithms
- **Interactive UI**: React + TypeScript frontend with drag-and-drop upload and real-time feedback
- **RESTful API**: FastAPI backend with automatic OpenAPI documentation and validation
- **Image Processing**: OpenCV and Pillow for optimal OCR preprocessing and enhancement
- **Data Export**: Timestamped JSON exports with structured product data and metadata
- **Production Ready**: Docker support, comprehensive testing, and CI/CD pipeline
- **Type Safety**: Full TypeScript coverage with shared type definitions between frontend and backend
- **Real-time Processing**: Live extraction progress with detailed feedback and error handling
- **Comprehensive Testing**: 96% backend test coverage with unit and integration tests

## Tech Stack

- **Backend**: FastAPI 0.104.1, Python 3.8+, Uvicorn
- **Frontend**: React 18, TypeScript 4.9, Axios, Create React App
- **OCR Engine**: EasyOCR 1.7.1 with PyTorch backend
- **Image Processing**: OpenCV 4.8, Pillow 10.1, NumPy 1.24
- **Data Storage**: JSON file-based storage with structured schemas
- **Testing**: Pytest (96% coverage), Jest + React Testing Library
- **Deployment**: Docker, Docker Compose, Production-ready containers
- **Documentation**: FastAPI OpenAPI/Swagger, Interactive API documentation
- **Development**: Pre-commit hooks, Black, isort, ESLint, Prettier

## Prerequisites

- **Python**: 3.8+ (3.10 recommended)
- **Node.js**: 16+ (18 recommended) 
- **Git**: Latest version
- **Docker**: Optional, for containerized deployment
- **Available Memory**: 4GB+ (for OCR model loading)

## Quick Start

### Local Development Setup

1. **Clone the repository**:
```bash
git clone https://github.com/yourusername/leaflet-product-extractor.git
cd leaflet-product-extractor
```

2. **Set up the backend**:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements-dev.txt
cp .env.example .env
# Edit .env with your configuration preferences
```

3. **Start the backend server**:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

4. **Set up the frontend** (in a new terminal):
```bash
cd frontend
npm install
cp .env.example .env
# Configure REACT_APP_API_URL if needed
```

5. **Start the frontend server**:
```bash
npm start
```

6. **Access the application**:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

### Using Docker

1. **Start all services**:
```bash
docker-compose up --build
```

2. **Access the application**:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

3. **Stop services**:
```bash
docker-compose down
```

## Environment Variables

### Backend (.env)
Create a `.env` file in the backend directory:

```env
# Application Settings
APP_NAME=Leaflet Product Extractor
APP_VERSION=1.0.0
DEBUG=True
ENVIRONMENT=development
HOST=0.0.0.0
PORT=8000

# CORS Configuration
CORS_ORIGINS=["http://localhost:3000", "http://127.0.0.1:3000"]
CORS_ALLOW_CREDENTIALS=True

# OCR Configuration
OCR_LANGUAGES=["en"]
OCR_GPU=False
OCR_CONFIDENCE_THRESHOLD=0.5
OCR_MODEL_STORAGE_DIRECTORY=./.EasyOCR/

# Image Processing
MAX_UPLOAD_SIZE=10485760  # 10MB
ALLOWED_EXTENSIONS=[".jpg", ".jpeg", ".png", ".pdf"]
IMAGE_RESIZE_MAX_WIDTH=2000
IMAGE_RESIZE_MAX_HEIGHT=2000

# File Paths
OUTPUT_DIRECTORY=../data/output
INPUT_DIRECTORY=../data/input

# Processing
MAX_CONCURRENT_EXTRACTIONS=3
EXTRACTION_TIMEOUT_SECONDS=300

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/app.log
```

### Frontend (.env)
Create a `.env` file in the frontend directory:

```env
# API Configuration
REACT_APP_API_URL=http://localhost:8000

# Optional: Additional configuration
REACT_APP_MAX_FILE_SIZE=10485760
REACT_APP_SUPPORTED_FORMATS=.jpg,.jpeg,.png,.pdf
```

## API Documentation

### Interactive Documentation (Swagger UI)
- **Local**: `http://localhost:8000/docs`
- **Production**: `https://your-domain.com/docs`

### Alternative Documentation (ReDoc)
- **Local**: `http://localhost:8000/redoc`
- **Production**: `https://your-domain.com/redoc`

### Raw OpenAPI Specification
- **JSON**: `http://localhost:8000/openapi.json`

The interactive Swagger UI allows you to:
- View all available endpoints with detailed schemas
- Test API calls directly in the browser with file uploads
- See real-time request/response examples
- Understand authentication requirements and error codes
- Copy cURL commands for testing and integration
- Download OpenAPI specification for code generation

### API Endpoints

| Method | Endpoint | Description | Content Type | Auth |
|--------|----------|-------------|--------------|------|
| POST | `/api/v1/extract` | Extract products from uploaded image | multipart/form-data | No |
| GET | `/api/v1/extractions` | List recent extraction results | application/json | No |
| GET | `/api/v1/extractions/{id}` | Get specific extraction by ID | application/json | No |
| GET | `/health` | API health check and status | application/json | No |
| GET | `/` | API information and version | application/json | No |

### Example Usage

#### Extract products from an image:
```bash
curl -X POST "http://localhost:8000/api/v1/extract" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@path/to/your/leaflet.jpg"
```

#### Response example:
```json
{
  "success": true,
  "message": "Successfully extracted 15 products",
  "products": [
    {
      "id": "prod-abc12345",
      "name": "Fresh Organic Apples",
      "description": "Premium quality red apples",
      "price": 4.99,
      "unit_price": 2.50,
      "unit": "per kg", 
      "currency": "AUD",
      "special_offer": "Buy 2 Get 1 Free",
      "position": {
        "x": 45,
        "y": 120, 
        "width": 200,
        "height": 150
      },
      "confidence": 0.95
    }
  ],
  "total_products": 15,
  "processing_time_seconds": 4.2,
  "json_file": "data/output/products_20241218_192845_abc123.json",
  "extraction_id": "ext-abc123",
  "timestamp": "2024-12-18T19:28:45.123456"
}
```

#### List recent extractions:
```bash
curl -X GET "http://localhost:8000/api/v1/extractions?limit=10" \
  -H "accept: application/json"
```

#### Get specific extraction:
```bash
curl -X GET "http://localhost:8000/api/v1/extractions/ext-abc123" \
  -H "accept: application/json"
```

## Testing

### Backend Testing (96% Coverage)

Run comprehensive test suites:

```bash
cd backend

# Run all tests with coverage report
pytest --cov=app --cov-report=html --cov-report=term

# Run specific test modules
pytest tests/unit/test_parser_service.py -v
pytest tests/integration/test_api.py -v

# Run tests with detailed output
pytest -v --tb=short

# Run tests and generate coverage HTML report
pytest --cov=app --cov-report=html
# Open htmlcov/index.html in browser
```

### Frontend Testing

```bash
cd frontend

# Run all tests
npm test

# Run tests with coverage
npm test -- --coverage --watchAll=false

# Run specific test file
npm test ProductTable.test.tsx

# Run tests in CI mode
npm run test:coverage
```

### Integration Testing

```bash
# Test full stack with Docker
docker-compose up -d
docker-compose exec backend pytest tests/integration/
docker-compose exec frontend npm test -- --watchAll=false
```

## Performance & Processing

- **Average Processing Time**: 3-8 seconds per standard leaflet image
- **Supported File Formats**: JPG, JPEG, PNG, PDF (up to 10MB)
- **OCR Accuracy**: 90%+ on clear, well-lit images with standard fonts
- **Concurrent Processing**: Up to 3 simultaneous extractions
- **Memory Usage**: ~1GB per OCR process (includes model loading)
- **CPU Requirements**: Multi-core recommended for optimal performance

## Deployment

### Deploy with Docker Compose (Recommended)

1. **Clone and configure**:
```bash
git clone <repository-url>
cd leaflet-product-extractor
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env
# Edit environment files as needed
```

2. **Deploy**:
```bash
docker-compose -f docker-compose.prod.yml up -d
```

3. **Verify deployment**:
```bash
curl http://localhost:8000/health
curl http://localhost:3000
```

### Deploy to Cloud Platforms

#### AWS ECS / Docker
```bash
# Build and push images
docker build -t leaflet-backend ./backend
docker build -t leaflet-frontend ./frontend
docker tag leaflet-backend:latest <your-registry>/leaflet-backend:latest
docker push <your-registry>/leaflet-backend:latest
```

#### Heroku
```bash
# Deploy backend
heroku create leaflet-backend
heroku container:push web --app leaflet-backend
heroku container:release web --app leaflet-backend

# Deploy frontend  
heroku create leaflet-frontend
heroku buildpacks:set heroku/nodejs --app leaflet-frontend
git subtree push --prefix frontend heroku-frontend main
```

### Production Configuration

Update environment variables for production:

```env
# Backend production settings
DEBUG=False
ENVIRONMENT=production
CORS_ORIGINS=["https://your-frontend-domain.com"]
LOG_LEVEL=WARNING

# Enable security features
MAX_CONCURRENT_EXTRACTIONS=5
EXTRACTION_TIMEOUT_SECONDS=600
```

## Architecture Overview

### System Architecture
```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   React Client  │    │  FastAPI Server  │    │  File Storage   │
│                 │    │                  │    │                 │
│ ┌─────────────┐ │    │ ┌──────────────┐ │    │ ┌─────────────┐ │
│ │ Upload Form │ │───▶│ │ API Routes   │ │    │ │ Input Images│ │
│ └─────────────┘ │    │ └──────────────┘ │    │ └─────────────┘ │
│                 │    │ ┌──────────────┐ │    │ ┌─────────────┐ │
│ ┌─────────────┐ │◀───│ │ OCR Service  │ │    │ │ Output JSON │ │
│ │Product Table│ │    │ └──────────────┘ │    │ └─────────────┘ │
│ └─────────────┘ │    │ ┌──────────────┐ │    └─────────────────┘
│                 │    │ │ Parser Logic │ │                      
└─────────────────┘    │ └──────────────┘ │                      
                       └──────────────────┘                      
```

### Data Flow Pipeline

1. **Image Upload**: User drags/drops image file in React frontend
2. **File Validation**: Size, format, and content validation on upload
3. **API Request**: Multipart form data sent to FastAPI backend
4. **Image Preprocessing**: OpenCV enhancement for optimal OCR accuracy
5. **OCR Processing**: EasyOCR extracts text with bounding boxes and confidence
6. **Smart Parsing**: Spatial clustering algorithm groups related text regions
7. **Product Extraction**: Price detection and product name identification
8. **Data Structuring**: Pydantic models validate and structure product data
9. **JSON Export**: Timestamped file generation with complete metadata
10. **Frontend Display**: Interactive table with sorting, filtering, and details

### Backend Services

#### Core Services
- **OCR Service** (`app/services/ocr_service.py`): EasyOCR integration with confidence filtering
- **Parser Service** (`app/services/parser_service.py`): Intelligent text clustering and product extraction
- **Export Service** (`app/services/export_service.py`): JSON file generation and management
- **Image Processor** (`app/utils/image_processor.py`): Image preprocessing and optimization

#### Utility Modules
- **Price Extractor** (`app/utils/price_extractor.py`): Regex-based price detection with currency support
- **Text Cleaner** (`app/utils/text_cleaner.py`): Product name normalization and special offer detection
- **Validators** (`app/utils/validators.py`): File and data validation utilities
- **File Handler** (`app/utils/file_handler.py`): Upload management and cleanup

### Frontend Components

#### Core Components
- **App** (`src/App.tsx`): Main application with state management
- **UploadForm** (`src/components/UploadForm.tsx`): Drag-and-drop file upload with progress
- **ProductTable** (`src/components/ProductTable.tsx`): Sortable, searchable product display
- **ProductDetails** (`src/components/ProductDetails.tsx`): Modal for detailed product information

#### Services & Types  
- **API Service** (`src/services/api.ts`): Type-safe HTTP client with error handling
- **Product Types** (`src/types/product.ts`): Shared TypeScript interfaces

## Project Structure

```
leaflet-product-extractor/
├── backend/                          # FastAPI Python backend
│   ├── app/
│   │   ├── api/                     # API layer
│   │   │   ├── deps.py             # Dependency injection
│   │   │   ├── routes.py           # API endpoints and route handlers
│   │   │   └── __init__.py
│   │   ├── core/                   # Core configuration
│   │   │   ├── config.py          # Pydantic settings management
│   │   │   ├── logging.py         # Loguru logging configuration
│   │   │   └── __init__.py
│   │   ├── models/                 # Internal data models
│   │   │   ├── product.py         # OCR and product data structures
│   │   │   └── __init__.py
│   │   ├── schemas/                # API request/response schemas
│   │   │   ├── product.py         # Pydantic API models
│   │   │   └── __init__.py
│   │   ├── services/               # Business logic layer
│   │   │   ├── ocr_service.py     # EasyOCR integration and management
│   │   │   ├── parser_service.py   # Intelligent product parsing logic
│   │   │   ├── export_service.py   # JSON export and file management
│   │   │   └── __init__.py
│   │   ├── utils/                  # Utility functions and helpers
│   │   │   ├── file_handler.py    # File upload and cleanup utilities
│   │   │   ├── image_processor.py  # OpenCV image preprocessing
│   │   │   ├── price_extractor.py  # Price detection algorithms
│   │   │   ├── text_cleaner.py     # Text normalization utilities
│   │   │   ├── unit_price_calculator.py # Unit price calculations
│   │   │   ├── validators.py       # Data validation functions
│   │   │   └── __init__.py
│   │   ├── main.py                 # FastAPI application entry point
│   │   └── __init__.py
│   ├── tests/                      # Comprehensive test suite
│   │   ├── integration/            # End-to-end integration tests
│   │   │   ├── test_api.py        # API endpoint testing
│   │   │   ├── test_extraction_pipeline.py # Full pipeline tests
│   │   │   └── __init__.py
│   │   ├── unit/                   # Unit tests for individual modules
│   │   │   ├── test_export_service.py     # Export service tests
│   │   │   ├── test_image_processor.py    # Image processing tests
│   │   │   ├── test_parser_service.py     # Parser logic tests
│   │   │   ├── test_price_extractor.py    # Price extraction tests
│   │   │   ├── test_text_cleaner.py       # Text cleaning tests
│   │   │   ├── test_unit_price_calculator.py # Unit price tests
│   │   │   ├── test_validators.py         # Validation tests
│   │   │   └── __init__.py
│   │   └── conftest.py             # Pytest configuration and fixtures
│   ├── requirements.txt            # Production dependencies
│   ├── requirements-dev.txt        # Development dependencies
│   ├── pytest.ini                 # Pytest configuration
│   ├── .env.example               # Environment variables template
│   ├── Dockerfile                 # Backend container definition
│   └── .gitignore                 # Git ignore patterns
├── frontend/                       # React TypeScript frontend
│   ├── public/
│   │   ├── index.html             # HTML template
│   │   ├── manifest.json          # PWA configuration
│   │   └── favicon.ico            # Application icon
│   ├── src/
│   │   ├── components/            # Reusable React components
│   │   │   ├── UploadForm.tsx     # File upload with drag-and-drop
│   │   │   ├── ProductTable.tsx   # Data table with sorting/filtering
│   │   │   ├── ProductDetails.tsx # Product detail modal
│   │   │   └── *.test.tsx         # Component unit tests
│   │   ├── services/              # API and external services
│   │   │   └── api.ts            # Axios-based API client
│   │   ├── types/                 # TypeScript type definitions
│   │   │   └── product.ts        # Shared type interfaces
│   │   ├── utils/                 # Frontend utility functions
│   │   ├── App.tsx               # Main application component
│   │   ├── App.css              # Application styles
│   │   ├── index.tsx            # React application entry point
│   │   ├── index.css            # Global styles
│   │   └── setupTests.ts        # Test configuration
│   ├── package.json             # Node.js dependencies and scripts
│   ├── tsconfig.json           # TypeScript configuration
│   ├── .env.example           # Frontend environment template
│   ├── Dockerfile             # Frontend container definition
│   └── .gitignore            # Git ignore patterns
├── data/                      # Data storage directory
│   ├── input/                # Temporary uploaded images
│   └── output/               # Generated JSON export files
├── docs/                     # Project documentation
│   ├── api/                 # API documentation
│   ├── deployment/          # Deployment guides
│   └── development/         # Development setup guides
├── scripts/                  # Utility scripts
│   ├── setup.sh            # Local development setup
│   └── deploy.sh           # Deployment automation
├── docker-compose.yml       # Development container orchestration
├── docker-compose.prod.yml  # Production container orchestration
├── .pre-commit-config.yaml  # Pre-commit hooks configuration
├── .github/                 # GitHub Actions CI/CD
│   └── workflows/
│       ├── backend-tests.yml    # Backend testing pipeline
│       ├── frontend-tests.yml   # Frontend testing pipeline
│       └── deploy.yml           # Deployment pipeline
├── .gitignore              # Global git ignore patterns
├── LICENSE                 # MIT license
└── README.md              # This comprehensive documentation
```

## Development Commands

### Backend Development
```bash
cd backend

# Environment setup
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements-dev.txt

# Development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Testing
pytest --cov=app --cov-report=html
pytest -v --tb=short
pytest tests/unit/test_parser_service.py -v

# Code quality
black app/ tests/              # Code formatting
isort app/ tests/              # Import sorting
flake8 app/ tests/             # Linting
mypy app/                      # Type checking
pylint app/                    # Advanced linting

# Pre-commit hooks
pre-commit install
pre-commit run --all-files
```

### Frontend Development
```bash
cd frontend

# Environment setup
npm install
cp .env.example .env

# Development server
npm start                      # Starts on http://localhost:3000

# Testing
npm test                       # Interactive test runner
npm test -- --coverage        # With coverage report
npm test -- --watchAll=false  # Run once

# Building
npm run build                  # Production build
npm run build -- --analyze    # Bundle analysis

# Code quality
npx tsc --noEmit              # Type checking
npx eslint src/               # Linting
npx prettier --write src/     # Code formatting
```

## Docker Commands

### Development
```bash
# Build and start all services
docker-compose up --build

# Start in detached mode
docker-compose up -d

# View real-time logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Execute commands in running containers
docker-compose exec backend pytest
docker-compose exec backend python -m pytest tests/ -v
docker-compose exec frontend npm test -- --watchAll=false
docker-compose exec frontend npm run build

# Database and cleanup
docker-compose down              # Stop services
docker-compose down -v          # Stop and remove volumes
docker system prune -f          # Clean up unused containers/images
```

### Production
```bash
# Production deployment
docker-compose -f docker-compose.prod.yml up -d

# Health checks
docker-compose -f docker-compose.prod.yml ps
docker-compose -f docker-compose.prod.yml logs

# Scaling
docker-compose -f docker-compose.prod.yml up -d --scale backend=3
```

## Security Features

- **Input Validation**: Comprehensive file type, size, and content validation
- **File Sanitization**: Automatic cleanup of temporary uploaded files
- **CORS Configuration**: Controlled cross-origin resource sharing
- **Error Handling**: Secure error responses without sensitive information exposure
- **Rate Limiting**: Built-in FastAPI rate limiting capabilities
- **Type Safety**: Full TypeScript and Pydantic validation throughout
- **Dependency Security**: Regular security updates and vulnerability scanning
- **Container Security**: Non-root user containers with minimal attack surface

## Performance Optimization

### Backend Optimizations
- **Lazy Loading**: Services initialized only when needed
- **Async Processing**: Non-blocking I/O for file operations
- **Memory Management**: Efficient image processing with garbage collection
- **Caching**: OCR model caching for faster subsequent requests
- **Connection Pooling**: Optimized HTTP client configurations

### Frontend Optimizations
- **Code Splitting**: Dynamic imports for optimal bundle sizes
- **Memoization**: React.memo for component re-render optimization
- **Lazy Loading**: Components loaded on-demand
- **Asset Optimization**: Compressed images and minified assets
- **Service Worker**: Caching strategy for offline functionality

## Troubleshooting

### Common Issues

#### Backend Issues
```bash
# OCR model download fails
rm -rf ./.EasyOCR/  # Clear model cache
pip install --upgrade easyocr

# Import errors
source venv/bin/activate  # Ensure virtual environment is active
pip install -r requirements-dev.txt

# Port conflicts
lsof -i :8000  # Check what's using port 8000
uvicorn app.main:app --port 8001  # Use different port
```

#### Frontend Issues  
```bash
# Module resolution errors
rm -rf node_modules package-lock.json
npm install

# Build failures
npm run build -- --verbose  # Detailed build output
npx tsc --noEmit  # Check TypeScript errors

# CORS errors
# Update REACT_APP_API_URL in .env
# Ensure backend CORS_ORIGINS includes frontend URL
```

#### Docker Issues
```bash
# Permission denied
sudo chmod +x scripts/*.sh

# Build failures
docker system prune -f  # Clean up
docker-compose build --no-cache

# Memory issues
docker system df  # Check disk usage
docker system prune --volumes -f  # Clean up volumes
```

### Performance Issues
- **Slow OCR**: Reduce image resolution in settings
- **Memory leaks**: Monitor with `docker stats`
- **Build times**: Use multi-stage Docker builds

## Contributing

We welcome contributions! Please follow these guidelines:

### Development Workflow

1. **Fork the repository**
2. **Create a feature branch**:
   ```bash
   git checkout -b feature/amazing-feature
   ```

3. **Set up development environment**:
   ```bash
   # Install pre-commit hooks
   pre-commit install
   
   # Install dependencies
   cd backend && pip install -r requirements-dev.txt
   cd ../frontend && npm install
   ```

4. **Make your changes**:
   - Follow existing code style and patterns
   - Add tests for new functionality
   - Update documentation as needed

5. **Run tests and quality checks**:
   ```bash
   # Backend
   cd backend
   pytest --cov=app
   black app/ tests/
   isort app/ tests/
   mypy app/
   
   # Frontend
   cd frontend
   npm test -- --watchAll=false
   npm run build
   npx tsc --noEmit
   ```

6. **Commit your changes**:
   ```bash
   git commit -am 'feat: add amazing feature'
   ```

7. **Push to your fork**:
   ```bash
   git push origin feature/amazing-feature
   ```

8. **Create a Pull Request**

### Code Standards

#### Python (Backend)
- Follow PEP 8 style guidelines
- Use type hints for all functions
- Add docstrings for public methods
- Maintain test coverage above 90%
- Use descriptive variable and function names

#### TypeScript (Frontend)
- Follow ESLint configuration
- Use proper TypeScript types
- Write unit tests for components
- Use semantic HTML and accessible design
- Optimize for performance and bundle size

### Pull Request Guidelines

- **Clear description** of changes and motivation
- **Reference related issues** with `Fixes #issue-number`
- **Include test coverage** for new features
- **Update documentation** for API changes
- **Follow conventional commit** message format
- **Ensure CI passes** all checks

## Commit Message Convention

This project follows [Conventional Commits](https://conventionalcommits.org/):

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

### Types:
- `feat:` - New features or functionality
- `fix:` - Bug fixes and error corrections
- `docs:` - Documentation updates and improvements
- `style:` - Code style changes (formatting, no logic changes)
- `refactor:` - Code refactoring without changing functionality
- `perf:` - Performance improvements and optimizations
- `test:` - Adding or updating tests
- `build:` - Build system or dependency changes
- `ci:` - Continuous integration configuration changes
- `chore:` - Maintenance tasks and minor updates

### Examples:
```bash
feat(parser): add unit price calculation for products
fix(ocr): resolve confidence threshold filtering issue
docs: update API documentation with new endpoints
test: add integration tests for extraction pipeline
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for complete details.

### MIT License Summary:
- **Commercial use** - Use in commercial applications
- **Modification** - Modify and adapt the code
- **Distribution** - Distribute original or modified versions
- **Private use** - Use for personal or internal projects
- **License and copyright notice** - Include original license
- **No warranty** - Software provided "as is"

## Authors

- **Edwin Anajemba** - *Initial development* - [GitHub Profile](https://github.com/thedatadoktor)
- **Contributors** - See [CONTRIBUTORS.md](CONTRIBUTORS.md) for full list

## Acknowledgments

### Core Technologies
- **[FastAPI](https://fastapi.tiangolo.com/)** - Modern, fast web framework for building APIs
- **[EasyOCR](https://github.com/JaidedAI/EasyOCR)** - Ready-to-use OCR with 80+ supported languages
- **[React](https://react.dev/)** - JavaScript library for building user interfaces
- **[OpenCV](https://opencv.org/)** - Computer vision and image processing library
- **[PyTorch](https://pytorch.org/)** - Machine learning framework powering EasyOCR

### Development Tools
- **[Docker](https://docker.com/)** - Containerization platform
- **[Pytest](https://pytest.org/)** - Python testing framework
- **[Jest](https://jestjs.io/)** - JavaScript testing framework
- **[TypeScript](https://typescriptlang.org/)** - Typed superset of JavaScript

### Community
- **Open source contributors** - For their invaluable contributions
- **Stack Overflow community** - For problem-solving assistance
- **GitHub community** - For hosting and collaboration tools

## Support

### Getting Help

If you encounter issues or have questions:

1. **Check the documentation** - Review this README and API docs
2. **Search existing issues** - [GitHub Issues](https://github.com/thedatadoktor/leaflet-product-extractor/issues)
3. **Create a new issue** - Provide detailed information including:
   - Operating system and version
   - Python/Node.js versions
   - Error messages and stack traces
   - Steps to reproduce the issue
   - Sample images (if applicable)

### Issue Templates

When creating issues, please use these templates:

#### Bug Report
```markdown
**Describe the bug**
A clear description of what the bug is.

**To Reproduce**
Steps to reproduce the behavior:
1. Go to '...'
2. Click on '....'
3. Upload file '....'
4. See error

**Expected behavior**
What you expected to happen.

**Screenshots/Logs**
If applicable, add screenshots or log output.

**Environment:**
- OS: [e.g. Windows 10, Ubuntu 20.04]
- Python version: [e.g. 3.10.0]
- Node.js version: [e.g. 18.17.0]
- Docker version: [e.g. 24.0.0]
```

#### Feature Request
```markdown
**Feature Description**
A clear description of the feature you'd like to see.

**Use Case**
Explain the use case and how this feature would be beneficial.

**Proposed Implementation**
If you have ideas on how this could be implemented.

**Additional Context**
Any other context or screenshots about the feature request.
```

### Community Guidelines

- **Be respectful** and inclusive in all interactions
- **Provide constructive feedback** with specific suggestions
- **Help others** by answering questions and sharing knowledge
- **Follow the code of conduct** in all community spaces

## Possible Roadmap

### Version 1.1.0 (Q1 2026)
- [ ] **Multi-language OCR support** - Support for multiple languages simultaneously
- [ ] **Batch processing** - Upload and process multiple images at once
- [ ] **User authentication** - User accounts and processing history
- [ ] **Advanced filtering** - Filter products by category, price range, etc.

### Version 1.2.0 (Q2 2026)
- [ ] **Machine learning improvements** - Custom product classification models
- [ ] **Mobile app** - React Native mobile application
- [ ] **Cloud deployment** - One-click cloud deployment options
- [ ] **Performance analytics** - Processing time and accuracy metrics

### Version 2.0.0 (Q3 2026)
- [ ] **Database integration** - PostgreSQL/MongoDB for data persistence
- [ ] **Real-time collaboration** - Multi-user processing and sharing
- [ ] **Advanced export formats** - Excel, CSV, XML export options
- [ ] **API rate limiting** - Production-grade rate limiting and quotas

## Changelog

### v1.0.0 (2025-12-18)
- **Initial release** - Complete product extraction system
- **FastAPI backend** - RESTful API with OpenAPI documentation
- **React frontend** - Interactive UI with drag-and-drop upload
- **EasyOCR integration** - Advanced text extraction with confidence scoring
- **Intelligent parsing** - Spatial clustering and price detection algorithms
- **JSON export** - Timestamped file generation with structured data
- **Docker support** - Complete containerization for easy deployment
- **Comprehensive testing** - 96% backend coverage with unit and integration tests
- **TypeScript coverage** - Full type safety across frontend and backend
- **Production ready** - Error handling, logging, and security features
- **Interactive documentation** - Swagger UI for API exploration and testing

---

**Built with ❤️ for extracting product data from grocery store leaflets**

*For technical support, feature requests, or contributions, please visit our [GitHub repository](https://github.com/thedatadoktor/leaflet-product-extractor).*