@echo off
REM WhisperX Environment Setup Script for Windows
REM This creates a separate environment for WhisperX to avoid NumPy conflicts

echo ========================================
echo WhisperX Environment Setup
echo ========================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found. Please install Python first.
    pause
    exit /b 1
)

echo Creating WhisperX virtual environment...
python -m venv whisperx_env

if not exist "whisperx_env" (
    echo ERROR: Failed to create virtual environment
    pause
    exit /b 1
)

echo Activating environment...
call whisperx_env\Scripts\activate.bat

echo Installing WhisperX and dependencies...
pip install --upgrade pip
pip install whisperx
pip install pyannote.audio>=3.1.0
pip install faster-whisper>=0.9.0
pip install ctranslate2>=3.20.0
pip install onnxruntime>=1.16.0

echo Copying necessary files...
copy whisperx_cli.py whisperx_env\ >nul 2>&1
copy config.json whisperx_env\ >nul 2>&1
copy WHISPERX_COMPATIBILITY.md whisperx_env\ >nul 2>&1

if exist "app\whisperx_transcription.py" (
    mkdir whisperx_env\app >nul 2>&1
    copy app\whisperx_transcription.py whisperx_env\app\ >nul 2>&1
    copy app\__init__.py whisperx_env\app\ >nul 2>&1
    copy config.py whisperx_env\ >nul 2>&1
)

echo Testing WhisperX installation...
python -c "import whisperx; print('WhisperX installed successfully')"

if errorlevel 1 (
    echo WARNING: WhisperX test failed
) else (
    echo SUCCESS: WhisperX environment ready!
)

echo.
echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo To use WhisperX:
echo 1. Activate environment: whisperx_env\Scripts\activate
echo 2. Process audio: python whisperx_cli.py audio.mp3
echo 3. Deactivate: deactivate
echo.
echo For help: python whisperx_cli.py --help
echo.

pause