#!/bin/bash

set -e

echo "🚀 Setting up Leaflet Product Extractor..."

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.9+"
    exit 1
fi
echo "✅ Python 3 found"

# Check Node
if ! command -v node &> /dev/null; then
    echo "❌ Node.js not found. Please install Node.js 16+"
    exit 1
fi
echo "✅ Node.js found"

# Backend setup
echo ""
echo "📦 Setting up Backend..."
cd backend

if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✅ Virtual environment created"
fi

source venv/bin/activate
pip install --upgrade pip > /dev/null 2>&1
pip install -r requirements-dev.txt > /dev/null 2>&1
echo "✅ Backend dependencies installed"

if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "✅ Created .env file"
fi

cd ..

# Frontend setup
echo ""
echo "📦 Setting up Frontend..."
cd frontend

npm install > /dev/null 2>&1
echo "✅ Frontend dependencies installed"

if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "✅ Created frontend .env file"
fi

cd ..

# Pre-commit hooks
echo ""
echo "🔧 Installing pre-commit hooks..."
pip install pre-commit > /dev/null 2>&1
pre-commit install > /dev/null 2>&1
echo "✅ Pre-commit hooks installed"

echo ""
echo "✨ Setup complete!"
echo ""
echo "To start development:"
echo "  Backend:  cd backend && source venv/bin/activate && uvicorn app.main:app --reload"
echo "  Frontend: cd frontend && npm start"
