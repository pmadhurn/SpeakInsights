@echo off
REM SpeakInsights Docker Deployment Script for Windows

echo 🐳 SpeakInsights Docker Deployment
echo ==================================

REM Check if Docker is installed
docker --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker is not installed. Please install Docker Desktop first.
    pause
    exit /b 1
)

REM Check if Docker Compose is available
docker-compose --version >nul 2>&1
if errorlevel 1 (
    docker compose version >nul 2>&1
    if errorlevel 1 (
        echo ❌ Docker Compose is not available. Please install Docker Compose.
        pause
        exit /b 1
    )
)

echo ✅ Docker and Docker Compose are available

REM Create required directories
echo 📁 Creating required directories...
if not exist "persistent_data" mkdir persistent_data
if not exist "backups" mkdir backups
if not exist "data" mkdir data
if not exist "data\audio" mkdir data\audio
if not exist "data\transcripts" mkdir data\transcripts
if not exist "data\exports" mkdir data\exports

REM Copy environment file if it doesn't exist
if not exist ".env" (
    echo 📝 Creating .env file from template...
    copy ".env.docker" ".env"
    echo    Please review and modify .env file if needed
)

REM Parse command line arguments
set MODE=full
set BUILD_FLAG=
set DETACH_FLAG=-d

:parse_args
if "%1"=="--mode" (
    set MODE=%2
    shift
    shift
    goto parse_args
)
if "%1"=="--build" (
    set BUILD_FLAG=--build
    shift
    goto parse_args
)
if "%1"=="--foreground" (
    set DETACH_FLAG=
    shift
    goto parse_args
)
if "%1"=="--help" (
    echo Usage: %0 [options]
    echo Options:
    echo   --mode MODE        Set application mode (full, api, frontend, mcp)
    echo   --build           Force rebuild of Docker images
    echo   --foreground      Run in foreground (don't detach)
    echo   --help            Show this help message
    pause
    exit /b 0
)
if "%1" neq "" (
    echo Unknown option: %1
    echo Use --help for usage information
    pause
    exit /b 1
)

REM Set environment variable for mode
set SPEAKINSIGHTS_MODE=%MODE%

echo 🚀 Starting SpeakInsights in Docker...
echo    Mode: %MODE%
if "%BUILD_FLAG%"=="" (
    echo    Build: using existing images
) else (
    echo    Build: %BUILD_FLAG%
)
if "%DETACH_FLAG%"=="" (
    echo    Running: in foreground
) else (
    echo    Running: %DETACH_FLAG%
)

REM Start the services
if "%MODE%"=="mcp" (
    echo 🔗 Starting MCP server only...
    docker-compose up %BUILD_FLAG% %DETACH_FLAG% speakinsights-mcp postgres
) else (
    echo 🚀 Starting full application...
    docker-compose up %BUILD_FLAG% %DETACH_FLAG%
)

if "%DETACH_FLAG%"=="-d" (
    echo.
    echo ✅ SpeakInsights is starting in the background!
    echo.
    echo 🌐 Access points:
    echo    Frontend:     http://localhost:8501
    echo    API:          http://localhost:8000
    echo    External API: http://localhost:3000
    echo    API Docs:     http://localhost:8000/docs
    echo.
    echo 📊 Monitor with:
    echo    docker-compose logs -f                    # All services
    echo    docker-compose logs -f speakinsights      # Main app
    echo    docker-compose logs -f speakinsights-mcp  # MCP server
    echo.
    echo 🛑 Stop with:
    echo    docker-compose down
    echo.
    echo 🔧 MCP Server access:
    echo    docker exec -it speakinsights-mcp python mcp_server.py
    echo.
    pause
)