#!/bin/bash
# Quick start script for Citizen Urban Planning Participation System

echo "🚀 Starting Citizen Urban Planning Participation System"
echo "=================================================="

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "⚠️  Virtual environment not found. Creating one..."
    python3 -m venv venv
    echo "✅ Virtual environment created"
fi

# Activate virtual environment
echo "📦 Activating virtual environment..."
source venv/bin/activate

# Check if dependencies are installed
if [ ! -f "venv/bin/uvicorn" ]; then
    echo "📥 Installing dependencies..."
    pip install -r requirements.txt
    echo "✅ Dependencies installed"
fi

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found. Please copy .env.example to .env and configure it."
    echo "   cp .env.example .env"
    exit 1
fi

echo ""
echo "🌐 Starting API server..."
echo "   API: http://localhost:8000"
echo "   Docs: http://localhost:8000/api/docs"
echo ""

# Start the server
python -m uvicorn src.main.python.core.app:app --reload --host 0.0.0.0 --port 8000
