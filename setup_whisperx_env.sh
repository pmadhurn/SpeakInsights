#!/bin/bash
# WhisperX Environment Setup Script for Linux/Mac
# This creates a separate environment for WhisperX to avoid NumPy conflicts

echo "========================================"
echo "WhisperX Environment Setup"
echo "========================================"
echo

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python3 not found. Please install Python first."
    exit 1
fi

echo "Creating WhisperX virtual environment..."
python3 -m venv whisperx_env

if [ ! -d "whisperx_env" ]; then
    echo "ERROR: Failed to create virtual environment"
    exit 1
fi

echo "Activating environment..."
source whisperx_env/bin/activate

echo "Installing WhisperX and dependencies..."
pip install --upgrade pip
pip install whisperx
pip install pyannote.audio>=3.1.0
pip install faster-whisper>=0.9.0
pip install ctranslate2>=3.20.0
pip install onnxruntime>=1.16.0

echo "Copying necessary files..."
cp whisperx_cli.py whisperx_env/ 2>/dev/null || true
cp config.json whisperx_env/ 2>/dev/null || true
cp WHISPERX_COMPATIBILITY.md whisperx_env/ 2>/dev/null || true

if [ -f "app/whisperx_transcription.py" ]; then
    mkdir -p whisperx_env/app
    cp app/whisperx_transcription.py whisperx_env/app/
    cp app/__init__.py whisperx_env/app/ 2>/dev/null || true
    cp config.py whisperx_env/
fi

echo "Testing WhisperX installation..."
if python -c "import whisperx; print('WhisperX installed successfully')" 2>/dev/null; then
    echo "SUCCESS: WhisperX environment ready!"
else
    echo "WARNING: WhisperX test failed"
fi

echo
echo "========================================"
echo "Setup Complete!"
echo "========================================"
echo
echo "To use WhisperX:"
echo "1. Activate environment: source whisperx_env/bin/activate"
echo "2. Process audio: python whisperx_cli.py audio.mp3"
echo "3. Deactivate: deactivate"
echo
echo "For help: python whisperx_cli.py --help"
echo