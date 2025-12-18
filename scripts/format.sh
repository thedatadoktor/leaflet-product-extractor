#!/bin/bash

echo "🎨 Formatting code..."

cd backend
source venv/bin/activate

echo ""
echo "📝 Running Black..."
black app/ tests/

echo ""
echo "📦 Running isort..."
isort app/ tests/

echo ""
echo "✨ Code formatted!"
