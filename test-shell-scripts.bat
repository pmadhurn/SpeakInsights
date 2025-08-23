@echo off
REM Test script to validate shell scripts for Windows

echo 🧪 Testing Shell Scripts
echo ========================

REM Check if bash is available (Git Bash, WSL, etc.)
bash --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Bash is not available. Please install Git Bash or WSL.
    echo    Shell script validation skipped.
    pause
    exit /b 1
)

REM Test docker-deploy.sh
echo 📝 Testing docker-deploy.sh...
bash -n docker-deploy.sh
if errorlevel 1 (
    echo ❌ docker-deploy.sh has syntax errors
    pause
    exit /b 1
) else (
    echo ✅ docker-deploy.sh syntax is valid
)

REM Test docker-entrypoint.sh
echo 📝 Testing docker-entrypoint.sh...
bash -n docker-entrypoint.sh
if errorlevel 1 (
    echo ❌ docker-entrypoint.sh has syntax errors
    pause
    exit /b 1
) else (
    echo ✅ docker-entrypoint.sh syntax is valid
)

echo.
echo 🎉 All shell script tests completed!
pause