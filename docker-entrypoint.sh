#!/bin/bash
set -e

echo "🚀 Starting SpeakInsights in Docker..."

# Wait for database if using PostgreSQL
if [ -n "$DATABASE_URL" ] && [[ "$DATABASE_URL" == postgresql* ]]; then
    echo "⏳ Waiting for PostgreSQL database..."
    
    # Extract host and port from DATABASE_URL
    DB_HOST=$(echo $DATABASE_URL | sed -n 's/.*@\([^:]*\):.*/\1/p')
    DB_PORT=$(echo $DATABASE_URL | sed -n 's/.*:\([0-9]*\)\/.*/\1/p')
    
    # Wait for database to be ready
    for i in {1..30}; do
        if curl -s "http://${DB_HOST}:${DB_PORT}" > /dev/null 2>&1 || \
           nc -z "${DB_HOST}" "${DB_PORT}" > /dev/null 2>&1; then
            echo "✅ Database is ready!"
            break
        fi
        echo "⏳ Waiting for database... (attempt $i/30)"
        sleep 2
    done
fi

# Initialize database
echo "🗄️ Initializing database..."
python -c "
try:
    from app.database import init_database
    init_database()
    print('✅ Database initialized successfully')
except Exception as e:
    print(f'❌ Database initialization failed: {e}')
    exit(1)
"

# Pre-download models if not present (in background to speed up startup)
echo "🤖 Checking models..."
python -c "
import os
from pathlib import Path

# Create model directories
model_dirs = [
    '/app/models/whisper',
    '/app/models/transformers', 
    '/app/models/huggingface',
    '/app/models/torch'
]

for dir_path in model_dirs:
    Path(dir_path).mkdir(parents=True, exist_ok=True)

print('✅ Model directories ready')
" &

# Run the application based on the mode
MODE=${SPEAKINSIGHTS_MODE:-full}

case $MODE in
    "mcp")
        echo "🔗 Starting MCP Server mode..."
        exec python start.py --mcp
        ;;
    "api")
        echo "🌐 Starting API only mode..."
        exec python start.py --api
        ;;
    "frontend")
        echo "🎯 Starting Frontend only mode..."
        exec python start.py --frontend
        ;;
    *)
        echo "🚀 Starting full application..."
        exec python start.py
        ;;
esac