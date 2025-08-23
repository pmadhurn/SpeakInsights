# WhisperX Compatibility Guide

## 🚨 Dependency Conflict Issue

There's a known compatibility issue between WhisperX and Streamlit due to NumPy version requirements:

- **WhisperX** requires `numpy >= 2.0.2`
- **Streamlit** requires `numpy < 2.0`

This creates a dependency conflict that prevents both from running in the same environment.

## 🔧 Solutions

### Option 1: Separate Environment (Recommended)

Create a separate Python environment for WhisperX processing:

```bash
# Create WhisperX environment
python -m venv whisperx_env
whisperx_env\Scripts\activate  # Windows
# source whisperx_env/bin/activate  # Linux/Mac

# Install WhisperX with compatible dependencies
pip install whisperx pyannote.audio>=3.1.0 faster-whisper>=0.9.0

# Use CLI for processing
python whisperx_cli.py audio.mp3 -o ./output
```

### Option 2: Docker Container

Use Docker to isolate WhisperX dependencies:

```dockerfile
FROM python:3.11-slim

# Install WhisperX dependencies
RUN pip install whisperx pyannote.audio>=3.1.0 faster-whisper>=0.9.0

# Copy CLI script
COPY whisperx_cli.py /app/
WORKDIR /app

ENTRYPOINT ["python", "whisperx_cli.py"]
```

```bash
# Build and run
docker build -t whisperx-processor .
docker run -v $(pwd)/audio:/audio -v $(pwd)/output:/output whisperx-processor /audio/meeting.mp3 -o /output
```

### Option 3: Fallback Mode (Current Implementation)

SpeakInsights gracefully falls back to standard Whisper when WhisperX is unavailable:

- ✅ **Standard Whisper** transcription works
- ❌ **Speaker diarization** not available
- ❌ **Word-level timestamps** not available
- ❌ **VAD preprocessing** not available

## 🎯 Recommended Workflow

### For Development/Testing
1. Use main SpeakInsights environment with standard Whisper
2. Create separate WhisperX environment for enhanced processing
3. Use CLI tools for batch processing with WhisperX

### For Production
1. **Option A**: Use standard Whisper in main application
2. **Option B**: Deploy WhisperX as separate microservice
3. **Option C**: Use Docker containers for isolation

## 📋 Step-by-Step Setup

### 1. Main SpeakInsights Environment
```bash
# Keep current environment for SpeakInsights
pip install -r requirements.txt
# This uses standard Whisper (no speaker diarization)
```

### 2. WhisperX Processing Environment
```bash
# Create new environment
python -m venv whisperx_env
whisperx_env\Scripts\activate

# Install WhisperX
pip install whisperx pyannote.audio>=3.1.0 faster-whisper>=0.9.0 ctranslate2>=3.20.0 onnxruntime>=1.16.0

# Copy processing scripts
copy whisperx_cli.py whisperx_env/
copy app/whisperx_transcription.py whisperx_env/
copy config.json whisperx_env/

# Test WhisperX
python whisperx_cli.py sample.mp3
```

### 3. Integration Workflow
```bash
# Process with WhisperX (separate environment)
whisperx_env\Scripts\activate
python whisperx_cli.py meeting.mp3 -o ./transcripts

# Import results into SpeakInsights
# (Manual import or API integration)
```

## 🔄 Alternative Solutions

### Future NumPy Compatibility
Monitor these projects for NumPy 2.0 compatibility:
- **Streamlit**: Track [NumPy 2.0 support](https://github.com/streamlit/streamlit/issues)
- **WhisperX**: May add NumPy 1.x compatibility

### Microservice Architecture
Deploy WhisperX as a separate service:

```python
# whisperx_service.py
from flask import Flask, request, jsonify
from whisperx_transcription import transcribe_with_whisperx

app = Flask(__name__)

@app.route('/transcribe', methods=['POST'])
def transcribe():
    audio_file = request.files['audio']
    result = transcribe_with_whisperx(audio_file.filename)
    return jsonify(result)

if __name__ == '__main__':
    app.run(port=5001)
```

### Conda Environment
Use Conda for better dependency resolution:

```bash
# Create conda environment
conda create -n whisperx python=3.11
conda activate whisperx

# Install with conda-forge
conda install -c conda-forge numpy>=2.0
pip install whisperx pyannote.audio
```

## 🧪 Testing Compatibility

### Check Current Status
```python
# test_compatibility.py
try:
    import whisperx
    import streamlit
    print("✅ Both WhisperX and Streamlit available")
except ImportError as e:
    print(f"❌ Import error: {e}")

import numpy as np
print(f"NumPy version: {np.__version__}")
```

### Verify WhisperX Functionality
```bash
# In WhisperX environment
python -c "import whisperx; print('WhisperX OK')"
python whisperx_cli.py --help
```

### Verify SpeakInsights Functionality
```bash
# In main environment
python -c "import streamlit; print('Streamlit OK')"
streamlit run frontend/app.py
```

## 📊 Feature Comparison

| Feature | Standard Whisper | WhisperX (Separate Env) |
|---------|------------------|-------------------------|
| Basic Transcription | ✅ | ✅ |
| Speed | 1× | 70× (GPU) |
| Word Timestamps | ❌ | ✅ |
| Speaker Diarization | ❌ | ✅ |
| VAD Preprocessing | ❌ | ✅ |
| Integration | Direct | CLI/API |
| Setup Complexity | Simple | Complex |

## 🚀 Quick Start Commands

### Standard Whisper (Current)
```bash
# Works in main environment
python frontend/app.py
# Upload audio → Basic transcription
```

### WhisperX Processing
```bash
# Switch to WhisperX environment
whisperx_env\Scripts\activate

# Process single file
python whisperx_cli.py meeting.mp3 -o ./output

# Batch process
python whisperx_cli.py -d ./audio_files -o ./transcripts

# With diarization
python whisperx_cli.py meeting.mp3 --hf-token YOUR_TOKEN
```

## 💡 Tips

1. **Use standard Whisper** for quick testing and development
2. **Use WhisperX** for production-quality transcription with speakers
3. **Automate the workflow** with scripts that switch environments
4. **Consider cloud services** like AWS Transcribe for production
5. **Monitor dependency updates** for future compatibility

## 🔗 Resources

- [WhisperX GitHub](https://github.com/m-bain/whisperX)
- [NumPy 2.0 Migration Guide](https://numpy.org/devdocs/numpy_2_0_migration_guide.html)
- [Streamlit NumPy Support](https://github.com/streamlit/streamlit/issues)
- [Python Virtual Environments](https://docs.python.org/3/tutorial/venv.html)