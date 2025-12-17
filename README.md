# Leaflet Product Extractor

AI-powered application that extracts product information from grocery store leaflet images.

## Features

- **Advanced OCR**: EasyOCR-powered text extraction
- **Smart Parsing**: Intelligent product data extraction
- **Interactive UI**: React-based frontend
- **RESTful API**: FastAPI backend
- **Production Ready**: Docker support, testing, CI/CD

## Quick Start

### Local Development

#### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements-dev.txt
cp .env.example .env
uvicorn app.main:app --reload
```

#### Frontend
```bash
cd frontend
npm install
cp .env.example .env
npm start
```

### Docker
```bash
docker-compose up --build
```

## URLs

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## Project Structure
```
leaflet-product-extractor/
├── backend/                # FastAPI backend
│   ├── app/
│   │   ├── api/           # API endpoints
│   │   ├── core/          # Core functionality
│   │   ├── models/        # Data models
│   │   ├── schemas/       # Pydantic schemas
│   │   ├── services/      # Business logic
│   │   └── utils/         # Utilities
│   └── tests/             # Tests
├── frontend/              # React frontend
│   └── src/
│       ├── components/    # React components
│       ├── services/      # API services
│       └── types/         # TypeScript types
├── data/                  # Data storage
│   ├── input/            # Input images
│   └── output/           # Generated JSON
└── docs/                 # Documentation
```

## Testing
```bash
# Backend
cd backend
pytest --cov=app

# Frontend
cd frontend
npm test -- --coverage
```

## License

MIT License - see LICENSE file
