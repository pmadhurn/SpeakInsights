#!/bin/bash
set -e

echo "🚀 Starting SpeakInsights in Docker..."

# Function to wait for database
wait_for_database() {
    if [ -n "$DATABASE_URL" ] && echo "$DATABASE_URL" | grep -q "^postgresql"; then
        echo "⏳ Waiting for PostgreSQL database..."
        
        # Extract host and port from DATABASE_URL
        DB_HOST=$(echo "$DATABASE_URL" | sed -n 's/.*@\([^:]*\):.*/\1/p')
        DB_PORT=$(echo "$DATABASE_URL" | sed -n 's/.*:\([0-9]*\)\/.*/\1/p')
        
        # Default to postgres if extraction fails
        DB_HOST=${DB_HOST:-postgres}
        DB_PORT=${DB_PORT:-5432}
        
        echo "   Checking connection to ${DB_HOST}:${DB_PORT}"
        
        # Simple wait loop
        for i in $(seq 1 30); do
            if command -v nc >/dev/null 2>&1 && nc -z "$DB_HOST" "$DB_PORT" >/dev/null 2>&1; then
                echo "✅ Database is ready!"
                return 0
            fi
            echo "⏳ Waiting for database... (attempt $i/30)"
            sleep 2
        done
        
        echo "⚠️  Database connection timeout, continuing anyway..."
    fi
}

# Function to initialize database
init_database() {
    echo "🗄️ Initializing database..."
    
    # Set Python path
    export PYTHONPATH="/app:$PYTHONPATH"
    
    # Try to initialize database
    if python3 -c "
import sys
sys.path.insert(0, '/app')
try:
    from app.database import init_database
    init_database()
    print('✅ Database initialized successfully')
except Exception as e:
    print(f'❌ Database initialization failed: {e}')
    sys.exit(1)
"; then
        echo "✅ Database initialization completed"
    else
        echo "⚠️  Database initialization failed, but continuing..."
    fi
}

# Function to setup model directories
setup_models() {
    echo "🤖 Setting up model directories..."
    
    # Create model directories
    mkdir -p /app/models/whisper /app/models/transformers /app/models/huggingface /app/models/torch
    
    # Set permissions
    chmod -R 777 /app/models 2>/dev/null || true
    
    echo "✅ Model directories ready"
}

# Main execution
main() {
    # Wait for database
    wait_for_database
    
    # Initialize database
    init_database
    
    # Setup models
    setup_models
    
    # Get application mode
    MODE=${SPEAKINSIGHTS_MODE:-full}
    
    # Start application based on mode
    case "$MODE" in
        "mcp")
            echo "🔗 Starting MCP Server mode..."
            exec python3 start.py --mcp
            ;;
        "api")
            echo "🌐 Starting API only mode..."
            exec python3 start.py --api
            ;;
        "frontend")
            echo "🎯 Starting Frontend only mode..."
            exec python3 start.py --frontend
            ;;
        *)
            echo "🚀 Starting full application..."
            exec python3 start.py
            ;;
    esac
}

# Run main function
main "$@"