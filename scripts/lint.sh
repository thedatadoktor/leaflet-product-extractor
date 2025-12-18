#!/bin/bash

echo "🔍 Running code quality checks..."

cd backend
source venv/bin/activate

echo ""
echo "📝 Running Black (formatter)..."
black app/ tests/ --check

echo ""
echo "📦 Running isort (import sorter)..."
isort app/ tests/ --check-only

echo ""
echo "🔎 Running Flake8 (linter)..."
flake8 app/ tests/

echo ""
echo "✅ All checks passed!"

# Format code
# ./scripts/format.sh