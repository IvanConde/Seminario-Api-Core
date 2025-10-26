#!/bin/bash

echo "🚀 Starting Core Unified Messaging API..."

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found. Creating from example..."
    cp .env.example .env
    echo "📝 Please edit .env file with your database credentials"
fi

# Install dependencies if needed
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

echo "🔧 Activating virtual environment..."
source venv/bin/activate

echo "📥 Installing dependencies..."
pip install -r requirements.txt

echo "🗄️  Starting database initialization..."
python -c "from src.database import init_db; import asyncio; asyncio.run(init_db())"

echo "🌐 Starting Core API server..."
python -m src.main
