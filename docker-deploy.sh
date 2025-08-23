#!/bin/bash
# SpeakInsights Docker Deployment Script

set -e

echo "🐳 SpeakInsights Docker Deployment"
echo "=================================="

# Check if Docker and Docker Compose are installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check for Docker Compose (v1 or v2)
DOCKER_COMPOSE_CMD=""
if command -v docker-compose >/dev/null 2>&1; then
    DOCKER_COMPOSE_CMD="docker-compose"
elif docker compose version >/dev/null 2>&1; then
    DOCKER_COMPOSE_CMD="docker compose"
else
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

echo "✅ Using Docker Compose: $DOCKER_COMPOSE_CMD"

# Function to check if a port is in use
check_port() {
    local port=$1
    # Try multiple methods to check port usage
    if command -v netstat >/dev/null 2>&1; then
        if netstat -tuln 2>/dev/null | grep -q ":$port "; then
            echo "⚠️  Port $port is already in use"
            return 1
        fi
    elif command -v ss >/dev/null 2>&1; then
        if ss -tuln 2>/dev/null | grep -q ":$port "; then
            echo "⚠️  Port $port is already in use"
            return 1
        fi
    elif command -v lsof >/dev/null 2>&1; then
        if lsof -i ":$port" >/dev/null 2>&1; then
            echo "⚠️  Port $port is already in use"
            return 1
        fi
    else
        # Skip port check if no tools available
        echo "⚠️  Cannot check port $port (no netstat/ss/lsof available)"
        return 0
    fi
    return 0
}

# Check required ports
echo "🔍 Checking ports..."
PORTS_OK=true

if ! check_port 8000; then
    echo "   Port 8000 (FastAPI) is in use"
    PORTS_OK=false
fi

if ! check_port 8501; then
    echo "   Port 8501 (Streamlit) is in use"
    PORTS_OK=false
fi

if ! check_port 3000; then
    echo "   Port 3000 (External API) is in use"
    PORTS_OK=false
fi

if ! check_port 5432; then
    echo "   Port 5432 (PostgreSQL) is in use"
    PORTS_OK=false
fi

if [ "$PORTS_OK" = false ]; then
    echo ""
    echo "❌ Some required ports are in use. Please stop other services or modify docker-compose.yml"
    echo "   You can also use environment variables to change ports:"
    echo "   export STREAMLIT_PORT=8502"
    echo "   export FASTAPI_PORT=8001"
    exit 1
fi

echo "✅ All required ports are available"

# Create required directories
echo "📁 Creating required directories..."
mkdir -p persistent_data backups data/audio data/transcripts data/exports

# Copy environment file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env.docker .env
    echo "   Please review and modify .env file if needed"
fi

# Parse command line arguments
MODE="full"
BUILD_FLAG=""
DETACH_FLAG="-d"
DEV_MODE=false
COMPOSE_FILES="-f docker-compose.yml"

while [[ $# -gt 0 ]]; do
    case $1 in
        --mode)
            MODE="$2"
            shift 2
            ;;
        --build)
            BUILD_FLAG="--build"
            shift
            ;;
        --foreground)
            DETACH_FLAG=""
            shift
            ;;
        --dev)
            DEV_MODE=true
            COMPOSE_FILES="-f docker-compose.yml -f docker-compose.dev.yml"
            shift
            ;;
        --help)
            echo "Usage: $0 [options]"
            echo "Options:"
            echo "  --mode MODE        Set application mode (full, api, frontend, mcp)"
            echo "  --build           Force rebuild of Docker images"
            echo "  --foreground      Run in foreground (don't detach)"
            echo "  --dev             Enable development mode with hot reload"
            echo "  --help            Show this help message"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Set environment variable for mode
export SPEAKINSIGHTS_MODE=$MODE

echo "🚀 Starting SpeakInsights in Docker..."
echo "   Mode: $MODE"
echo "   Build: ${BUILD_FLAG:-"using existing images"}"
echo "   Running: ${DETACH_FLAG:-"in foreground"}"

# Start the services
if [ "$MODE" = "mcp" ]; then
    echo "🔗 Starting MCP server only..."
    $DOCKER_COMPOSE_CMD $COMPOSE_FILES up $BUILD_FLAG $DETACH_FLAG speakinsights-mcp postgres
else
    echo "🚀 Starting full application..."
    if [ "$DEV_MODE" = true ]; then
        echo "   Development mode enabled with hot reload"
    fi
    $DOCKER_COMPOSE_CMD $COMPOSE_FILES up $BUILD_FLAG $DETACH_FLAG
fi

if [ -n "$DETACH_FLAG" ]; then
    echo ""
    echo "✅ SpeakInsights is starting in the background!"
    echo ""
    echo "🌐 Access points:"
    echo "   Frontend:     http://localhost:8501"
    echo "   API:          http://localhost:8000"
    echo "   External API: http://localhost:3000"
    echo "   API Docs:     http://localhost:8000/docs"
    echo ""
    echo "📊 Monitor with:"
    echo "   $DOCKER_COMPOSE_CMD logs -f                    # All services"
    echo "   $DOCKER_COMPOSE_CMD logs -f speakinsights      # Main app"
    echo "   $DOCKER_COMPOSE_CMD logs -f speakinsights-mcp  # MCP server"
    echo ""
    echo "🛑 Stop with:"
    echo "   $DOCKER_COMPOSE_CMD down"
    echo ""
    echo "🔧 MCP Server access:"
    echo "   docker exec -it speakinsights-mcp python mcp_server.py"
fi