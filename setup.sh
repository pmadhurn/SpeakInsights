#!/bin/bash

echo "🚀 Setting up SpeakInsights..."

# Create virtual environment
python -m venv venv

# Activate virtual environment
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    source venv/Scripts/activate
else
    source venv/bin/activate
fi

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Download NLTK data
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p data/audio data/transcripts data/exports data/meetings data/mcp_exports

# Initialize database
echo "🗄️ Initializing database..."
python -c "from app.database import init_database; init_database()"

echo "✅ Setup complete! Run 'python run.py' to start the application."