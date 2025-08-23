# SpeakInsights - AI Meeting Assistant

SpeakInsights is an AI-powered tool designed to help users transcribe, summarize, and analyze audio recordings of meetings. It extracts key information, identifies action items, and provides sentiment analysis to offer comprehensive insights into meeting discussions.

## Features

*   **Audio Transcription:** Converts audio recordings of meetings into text using OpenAI's Whisper model with GPU acceleration.
*   **Enhanced Transcription (Optional):** WhisperX integration for 70× faster processing, word-level timestamps, VAD preprocessing, and speaker diarization (requires separate environment due to dependency conflicts).
*   **AI-Powered Summarization:** Generates comprehensive summaries using Ollama (local LLMs) or fallback to transformer models.
*   **Sentiment Analysis:** Analyzes the overall sentiment of the meeting discussion with GPU acceleration.
*   **Action Item Extraction:** Identifies and extracts actionable tasks mentioned during the meeting.
*   **Speaker Analysis:** Timeline visualization and statistics when using WhisperX (separate environment).
*   **Web Interface:** Provides a user-friendly interface built with Streamlit to upload audio files and view insights.
*   **API Endpoints:** Offers a FastAPI backend with endpoints for programmatic access and integration.
*   **Data Persistence:** Saves meeting data, including transcripts and generated insights, in PostgreSQL or SQLite database.
*   **GPU Acceleration:** Automatic GPU detection and usage for faster AI processing.
*   **Ollama Integration:** Local LLM support for high-quality, unlimited-length summarization.
*   **Webhook Integration:** n8n webhook support for automated workflows.
*   **Regenerate Summaries:** Re-process existing transcripts with improved models.

## Project Structure

The project is organized into the following main directories:

*   **`app/`**: Contains the backend FastAPI application, including modules for handling API requests, database interactions, audio transcription, and NLP tasks.
*   **`frontend/`**: Contains the Streamlit frontend application, providing the user interface for interacting with the SpeakInsights tool.
*   **`data/`**: This directory is used for storing data such as uploaded audio files, generated transcripts, and the SQLite database (`speakinsights.db`). (Note: This directory might be created automatically when the application runs and saves data).
*   **`ffmpeg-7.1.1-essentials_build/`**: Contains the FFMPEG executables, which are used for audio processing tasks.

## Modules

Key Python modules and their functions:

*   **`app/main.py`**: The core of the backend application built with FastAPI. It defines API endpoints for:
    *   Uploading audio files.
    *   Processing meetings (transcription, summarization, sentiment analysis, action item extraction).
    *   Retrieving meeting data.
*   **`app/database.py`**: Manages all interactions with PostgreSQL or SQLite databases. Enhanced schema includes:
    *   Standard meeting data (transcript, summary, sentiment, action items).
    *   WhisperX enhancements (formatted transcripts, speaker segments, transcription metadata).
    *   Support for both PostgreSQL (production) and SQLite (development).
*   **`app/models.py`**: Defines Pydantic data models used for request and response validation in the FastAPI application, ensuring data consistency.
*   **`app/nlp_module.py`**: Houses the Natural Language Processing functionalities. It uses pre-trained models from the `transformers` library to:
    *   Summarize transcribed text.
    *   Perform sentiment analysis on the text.
    *   Extract potential action items from the transcript.
*   **`app/transcription.py`**: Responsible for converting audio files to text. Enhanced with WhisperX integration and automatic fallback to standard Whisper.
*   **`app/whisperx_transcription.py`**: Complete WhisperX implementation with speaker diarization, VAD preprocessing, and word-level timestamps.
*   **`frontend/app.py`**: The main Streamlit web application with enhanced features:
    *   Uploading and processing meeting audio files.
    *   Speaker analysis tab with timeline visualization (when WhisperX data available).
    *   WhisperX status monitoring and compatibility warnings.
    *   Formatted transcript display with speaker labels.
    *   Enhanced meeting analytics including speaker statistics.
*   **`config.py`**: Contains configuration settings for the application, such as model names for Whisper and NLP tasks, file upload paths, database path, and API server settings.
*   **`requirements.txt`**: Lists all Python dependencies required to run the project.

### WhisperX Integration Files

*   **`whisperx_cli.py`**: Command-line tool for batch processing audio files with WhisperX. Supports single files, directory processing, and various output formats.
*   **`setup_whisperx.py`**: Automated setup script for WhisperX installation and configuration.
*   **`setup_whisperx_env.bat/.sh`**: Platform-specific scripts to create separate WhisperX environments.
*   **`test_whisperx_integration.py`**: Comprehensive testing suite for WhisperX functionality.
*   **`test_current_setup.py`**: Verification script for the main SpeakInsights setup.

### Documentation Files

*   **`WHISPERX_INTEGRATION.md`**: Complete guide to WhisperX integration, features, and API reference.
*   **`WHISPERX_COMPATIBILITY.md`**: Detailed solutions for NumPy dependency conflicts and environment setup.
*   **`INTEGRATION_STATUS.md`**: Current implementation status and feature comparison.

## 🎙️ WhisperX Integration - Enhanced Transcription

SpeakInsights includes advanced WhisperX integration for professional-grade transcription with speaker diarization and enhanced accuracy.

### 🚀 WhisperX Features

- **🏃‍♂️ 70× Faster:** GPU-accelerated transcription with massive speed improvements
- **🎭 Speaker Diarization:** Identifies who said what using pyannote-audio
- **⏱️ Word-Level Timestamps:** Precise timing for every word spoken
- **🔊 VAD Preprocessing:** Voice Activity Detection for better accuracy
- **📊 Speaker Analytics:** Timeline visualization and speaking statistics
- **🎯 Enhanced Accuracy:** Superior performance on long-form audio
- **🔄 Batch Processing:** CLI tools for processing multiple files

### ⚠️ Compatibility Issue & Solutions

**Issue:** WhisperX and Streamlit have conflicting NumPy requirements:
- WhisperX requires `numpy >= 2.0.2`
- Streamlit requires `numpy < 2.0`

**Solution:** Use separate environments for optimal functionality.

### 🛠️ Setup Options

#### Option 1: Automated Setup (Recommended)

**Windows:**
```cmd
setup_whisperx_env.bat
```

**Linux/Mac:**
```bash
chmod +x setup_whisperx_env.sh
./setup_whisperx_env.sh
```

#### Option 2: Manual Setup

```bash
# Create WhisperX environment
python -m venv whisperx_env

# Activate environment
whisperx_env\Scripts\activate  # Windows
# source whisperx_env/bin/activate  # Linux/Mac

# Install WhisperX and dependencies
pip install whisperx
pip install pyannote.audio>=3.1.0
pip install faster-whisper>=0.9.0
pip install ctranslate2>=3.20.0
pip install onnxruntime>=1.16.0

# Copy processing files
copy whisperx_cli.py whisperx_env/
copy config.json whisperx_env/
```

#### Option 3: Current Setup (Standard Whisper)

The main SpeakInsights application uses standard Whisper:
- ✅ **Basic transcription** works perfectly
- ✅ **All other features** (summaries, action items, etc.)
- ❌ **No speaker diarization**
- ❌ **No word-level timestamps**
- ❌ **Standard processing speed**

### 🎯 Usage Examples

#### CLI Processing (WhisperX Environment)

```bash
# Activate WhisperX environment
whisperx_env\Scripts\activate  # Windows
# source whisperx_env/bin/activate  # Linux/Mac

# Process single file
python whisperx_cli.py meeting.mp3 -o ./output

# Batch process directory
python whisperx_cli.py -d ./audio_files -o ./transcripts

# With speaker diarization (requires HF token)
python whisperx_cli.py meeting.mp3 --hf-token YOUR_TOKEN

# Custom model and settings
python whisperx_cli.py meeting.mp3 --model large-v3 --no-vad

# Get help
python whisperx_cli.py --help
```

#### Python API (WhisperX Environment)

```python
from app.whisperx_transcription import transcribe_with_whisperx

# Enhanced transcription
result = transcribe_with_whisperx(
    audio_path="meeting.mp3",
    enable_vad=True,
    enable_diarization=True,
    min_speakers=2,
    max_speakers=5
)

# Access results
print(f"Speakers detected: {len(result['speakers'])}")
print(f"Total segments: {result['processing_info']['total_segments']}")
print(f"Duration: {result['processing_info']['duration']/60:.1f} minutes")

# Formatted transcript with speakers
print(result['formatted_transcript'])

# Speaker timeline data
for segment in result['speaker_segments']:
    print(f"[{segment['speaker']}] {segment['start']:.1f}s: {segment['text']}")
```

#### Integration with Main App

```python
# In main SpeakInsights environment
from app.transcription import transcribe_audio, get_transcription_metadata

# Automatic fallback to standard Whisper
result = transcribe_audio("meeting.mp3")
metadata = get_transcription_metadata(result)

if metadata['method'] == 'whisperx':
    print("Enhanced transcription with speakers!")
else:
    print("Standard Whisper transcription")
```

### 🔧 Configuration

Edit `config.json` to customize WhisperX settings:

```json
{
  "whisperx_settings": {
    "enabled": true,
    "model_size": "large-v2",
    "compute_type": "float16",
    "batch_size": 16,
    "enable_vad": true,
    "vad_onset": 0.500,
    "vad_offset": 0.363,
    "enable_diarization": true,
    "min_speakers": null,
    "max_speakers": null,
    "hf_token": "your_huggingface_token_here",
    "device": "auto",
    "language": "en"
  }
}
```

### 🎭 Speaker Diarization Setup

For speaker diarization (who said what), you need a Hugging Face token:

1. **Get Token:**
   - Visit https://huggingface.co/settings/tokens
   - Create a new token with 'Read' access
   - Copy the token

2. **Configure Token:**
   ```json
   {
     "whisperx_settings": {
       "hf_token": "hf_your_token_here"
     }
   }
   ```

3. **Test Diarization:**
   ```bash
   python whisperx_cli.py meeting.mp3 --hf-token YOUR_TOKEN
   ```

### 📊 Performance Comparison

| Feature | Standard Whisper | WhisperX |
|---------|------------------|----------|
| **Speed** | 1× baseline | 70× faster (GPU) |
| **Basic Transcription** | ✅ | ✅ |
| **Word Timestamps** | ❌ | ✅ Precise alignment |
| **Speaker Diarization** | ❌ | ✅ Multi-speaker |
| **VAD Preprocessing** | ❌ | ✅ Noise filtering |
| **Long-form Audio** | ⚠️ Limited | ✅ Optimized |
| **Integration** | Direct | CLI/API |
| **Setup Complexity** | Simple | Moderate |

### 🧪 Testing WhisperX

#### Test Current Setup
```bash
# Test main SpeakInsights setup
python test_current_setup.py

# Test WhisperX integration (if available)
python test_whisperx_integration.py

# Test with sample audio
python test_whisperx_integration.py --audio sample.mp3
```

#### Verify WhisperX Environment
```bash
# In WhisperX environment
python -c "import whisperx; print('✅ WhisperX available')"
python -c "import pyannote.audio; print('✅ Speaker diarization available')"
```

### 🔄 Recommended Workflow

#### Development Workflow
1. **Main Environment:** Use for SpeakInsights development and basic transcription
2. **WhisperX Environment:** Use for enhanced processing when needed
3. **CLI Processing:** Batch process audio files with WhisperX
4. **Import Results:** Manually import enhanced results into main app

#### Production Workflow
1. **Standard Deployment:** Use main SpeakInsights for most users
2. **Enhanced Service:** Deploy WhisperX as separate microservice
3. **API Integration:** Connect services via REST API
4. **Docker Containers:** Use containers for environment isolation

### 🐳 Docker Integration

Create a WhisperX Docker container:

```dockerfile
# Dockerfile.whisperx
FROM python:3.11-slim

# Install WhisperX
RUN pip install whisperx pyannote.audio>=3.1.0

# Copy CLI tools
COPY whisperx_cli.py /app/
COPY config.json /app/
WORKDIR /app

ENTRYPOINT ["python", "whisperx_cli.py"]
```

```bash
# Build and use
docker build -f Dockerfile.whisperx -t whisperx-processor .
docker run -v $(pwd)/audio:/audio -v $(pwd)/output:/output \
  whisperx-processor /audio/meeting.mp3 -o /output
```

### 🚨 Troubleshooting

#### Common Issues

**NumPy Version Conflict:**
```bash
# Check NumPy version
python -c "import numpy; print(numpy.__version__)"

# Fix in main environment (for Streamlit)
pip install "numpy<2.0,>=1.19.3"

# Fix in WhisperX environment
pip install "numpy>=2.0.2"
```

**WhisperX Import Error:**
```bash
# In WhisperX environment
pip install --upgrade whisperx
pip install --upgrade pyannote.audio
```

**GPU Not Detected:**
```bash
# Check CUDA availability
python -c "import torch; print(torch.cuda.is_available())"

# Install CUDA-compatible PyTorch
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

**Speaker Diarization Fails:**
- Verify Hugging Face token is valid
- Check internet connection for model download
- Ensure `pyannote.audio` is properly installed
- Try processing without diarization first

#### Performance Optimization

**GPU Setup:**
```bash
# Check GPU memory
nvidia-smi

# Optimize batch size based on GPU memory
# RTX 4090: batch_size: 32
# RTX 3080: batch_size: 16  
# RTX 3060: batch_size: 8
```

**CPU Optimization:**
```json
{
  "whisperx_settings": {
    "device": "cpu",
    "compute_type": "int8",
    "batch_size": 4
  }
}
```

### 📚 Documentation Files

- **`WHISPERX_INTEGRATION.md`** - Complete integration guide
- **`WHISPERX_COMPATIBILITY.md`** - Detailed compatibility solutions  
- **`INTEGRATION_STATUS.md`** - Current implementation status
- **`whisperx_cli.py`** - Command-line processing tool
- **`setup_whisperx.py`** - Automated setup script
- **`test_whisperx_integration.py`** - Comprehensive testing

### 🎯 Quick Start Commands

**Standard SpeakInsights (Works Now):**
```bash
python test_current_setup.py  # Verify setup
streamlit run frontend/app.py  # Run application
```

**WhisperX Enhanced Processing:**
```bash
# Setup (one-time)
setup_whisperx_env.bat  # Windows
# ./setup_whisperx_env.sh  # Linux/Mac

# Use (daily workflow)
whisperx_env\Scripts\activate
python whisperx_cli.py meeting.mp3 -o ./output
deactivate
```

The WhisperX integration provides professional-grade transcription capabilities while maintaining full compatibility with the existing SpeakInsights application through intelligent fallback mechanisms.
*   **`run.py` (and similar scripts like `run_all.py`, `hackathon_launcher.py`):** These are likely utility scripts to start the backend and/or frontend services. For example, `run.py` might start the Uvicorn server for the FastAPI app and the Streamlit app.
*   **`setup.sh`**: A shell script that likely automates the setup process, which may include creating virtual environments, installing dependencies, and initializing the database.

## Setup and Installation

### 🐳 Docker Deployment (Recommended)

The easiest way to run SpeakInsights is using Docker:

**Windows:**
```cmd
docker-deploy.bat
```

**Linux/Mac:**
```bash
chmod +x docker-deploy.sh
./docker-deploy.sh
```

**Manual Docker:**
```bash
docker-compose up -d
```

Access the application at:
- Frontend: http://localhost:8501
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs

For detailed Docker deployment instructions, see [DOCKER.md](DOCKER.md).

### 🦙 Ollama Integration (Recommended for Best Summaries)

For superior summarization quality without text length limits, integrate with Ollama:

1.  **Install Ollama:**
    ```bash
    # Download from https://ollama.ai or use:
    curl -fsSL https://ollama.ai/install.sh | sh
    ```

2.  **Start Ollama:**
    ```bash
    ollama serve
    ```

3.  **Install a Model:**
    ```bash
    # Fast and efficient (1.2GB)
    ollama pull llama3.2:1b
    
    # Higher quality (3.8GB)
    ollama pull dolphin-mistral:7b
    
    # Excellent for summaries (4.7GB)
    ollama pull qwen2.5:7b
    ```

4.  **Test Integration:**
    ```bash
    python test_ollama.py
    ```

5.  **Configure (Optional):**
    Edit `config.json` to change model or settings:
    ```json
    {
      "ollama_settings": {
        "enabled": true,
        "base_url": "http://localhost:11434",
        "model": "llama3.2:1b",
        "timeout": 120,
        "fallback_to_local": true
      }
    }
    ```

**Benefits of Ollama:**
- ✅ No text length limits (processes entire transcripts)
- ✅ Superior summary quality compared to BART models
- ✅ Runs locally (completely private)
- ✅ Multiple model options for different needs
- ✅ GPU accelerated on compatible hardware

### 🚀 GPU Acceleration Setup

For optimal performance, ensure GPU support:

1.  **Test GPU Availability:**
    ```bash
    python test_gpu.py
    ```

2.  **Install GPU-enabled PyTorch (if needed):**
    ```bash
    pip uninstall torch torchvision torchaudio
    pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
    ```

3.  **Verify GPU Usage:**
    The application will automatically detect and use GPU for:
    - Whisper transcription
    - Transformer-based summarization
    - Sentiment analysis

### 💻 Local Development Setup

Follow these steps to set up and run SpeakInsights on your local machine:

1.  **Clone the Repository:**
    ```bash
    git clone <repository_url>
    cd speakinsights
    ```
    (Replace `<repository_url>` with the actual URL of the repository. If you cloned this, you already have it.)

2.  **Create a Virtual Environment (Recommended):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3.  **Install Dependencies:**
    Install all required Python packages using the `requirements.txt` file:
    ```bash
    pip install -r requirements.txt
    ```
    This will install FastAPI, Uvicorn, Streamlit, OpenAI Whisper, Transformers, PyTorch, and other necessary libraries.

4.  **FFMPEG:**
    The project includes a version of FFMPEG in the `ffmpeg-7.1.1-essentials_build/` directory.
    *   **Windows:** The `ffmpeg.exe` is included. Ensure that this directory (or the `bin` subdirectory within it) is accessible by the application, or add it to your system's PATH. The application might be configured to look for it in a specific relative path.
    *   **Linux/macOS:** You might need to install FFMPEG separately if the bundled version is not compatible or if you prefer a system-wide installation.
        ```bash
        # For Debian/Ubuntu
        sudo apt update && sudo apt install ffmpeg
        # For macOS (using Homebrew)
        brew install ffmpeg
        ```
    FFMPEG is required by `openai-whisper` for audio processing.

5.  **Initialize Database:**
    The SQLite database (`speakinsights.db`) is typically initialized automatically when `app/database.py` is first imported (which happens when the backend app starts). If you need to manually create it or if there's a specific setup script for it (e.g., within `setup.sh`), refer to that.

6.  **Running the Application:**
    
    **Simple Start (Recommended):**
    ```bash
    python start.py
    ```
    This will start both the backend API and frontend automatically.
    
    **Alternative Start Methods:**
    ```bash
    python run.py              # Start full application
    python start.py --api      # Start API server only
    python start.py --frontend # Start frontend only
    python start.py --mcp      # Start MCP server for Claude integration
    ```
    
    **Manual Start:**
    *   **Backend (FastAPI):**
        ```bash
        uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
        ```
    *   **Frontend (Streamlit):**
        ```bash
        streamlit run frontend/app.py --server.port 8501
        ```

7.  **Configuration (Optional):**
    Review `config.py` for basic settings or edit `config.json` for advanced configuration:
    ```json
    {
      "model_settings": {
        "whisper_model": "base",
        "max_summary_length": 300
      },
      "ollama_settings": {
        "enabled": true,
        "model": "llama3.2:1b"
      },
      "processing_settings": {
        "summarize_full_transcript": true
      }
    }
    ```

After these steps, you should be able to access the Streamlit frontend in your web browser (usually at `http://localhost:8501`) and the FastAPI backend API (usually at `http://localhost:8000`).

## Usage

Once the backend and frontend services are running:

1.  **Open the Web Interface:**
    Navigate to the Streamlit application URL in your web browser (typically `http://localhost:8501`).

2.  **Upload an Audio File:**
    *   In the sidebar of the web interface, you'll find an "Upload New Meeting" section.
    *   Enter a title for your meeting.
    *   Click the "Choose an audio file" button and select an audio file from your computer (supported formats include mp3, wav, m4a, etc.).

3.  **Process Meeting:**
    *   Click the "Process Meeting" button.
    *   The application will upload the file, transcribe the audio, generate a summary, analyze sentiment, and extract action items. This process may take a few minutes depending on the length of the audio and the models being used.

4.  **View Insights:**
    *   Once processing is complete, the meeting will appear in the dashboard.
    *   You can select a meeting to view its details:
        *   **Summary:** A comprehensive overview of the meeting (powered by Ollama if available).
        *   **Full Transcript:** The complete text transcribed from the audio. Download options for both plain and speaker-labeled transcripts.
        *   **Speaker Analysis:** (WhisperX data) Timeline visualization, speaker statistics, and detailed speaker segments.
        *   **Action Items:** A list of tasks identified from the discussion.
        *   **Analytics:** Enhanced analytics including speaker count, actual duration, and transcription method used.
        *   **Settings:** Configure Ollama and WhisperX integration, test connectivity, and view compatibility status.

5.  **Regenerate Summaries:**
    *   Use the "🔄 Regenerate Summary" button to create new summaries with improved models.
    *   Existing transcripts can be re-processed without re-uploading audio files.

The backend API can also be used by other services if needed. API documentation is typically available via FastAPI's auto-generated docs (usually at `http://localhost:8000/docs` or `http://localhost:8000/redoc` when the backend server is running).

## 🔧 Testing & Troubleshooting

### Test Scripts

*   **GPU Test:** `python test_gpu.py` - Verify GPU detection and PyTorch CUDA support
*   **Ollama Test:** `python test_ollama.py` - Check Ollama connectivity and model availability
*   **Current Setup Test:** `python test_current_setup.py` - Verify main SpeakInsights functionality
*   **WhisperX Integration Test:** `python test_whisperx_integration.py` - Test WhisperX availability and functionality
*   **WhisperX with Audio:** `python test_whisperx_integration.py --audio sample.mp3` - Test with actual audio file

### Common Issues

**GPU Not Detected:**
```bash
# Reinstall PyTorch with CUDA support
pip uninstall torch torchvision torchaudio
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

**Ollama Connection Failed:**
```bash
# Start Ollama server
ollama serve

# Install a model
ollama pull llama3.2:1b
```

**External API Server Failed:**
- Check if ports 3000, 8000, 8501 are available
- Ensure database permissions are correct
- Try starting components individually with `python start.py --api` and `python start.py --frontend`

### Performance Tips

*   **Use GPU:** Ensure CUDA-enabled PyTorch for 5-10x faster processing
*   **Use Ollama:** Get better summaries without text length limitations
*   **Model Selection:** 
    *   `llama3.2:1b` - Fast, good quality (1.2GB)
    *   `dolphin-mistral:7b` - Better quality (3.8GB)
    *   `qwen2.5:7b` - Best for summaries (4.7GB)

## Contributing

Contributions to SpeakInsights are welcome! If you have suggestions for improvements or want to contribute code, please feel free to:

1.  Fork the repository.
2.  Create a new branch for your feature or bug fix.
3.  Make your changes.
4.  Submit a pull request with a clear description of your changes.

Alternatively, you can open an issue to discuss potential changes or report bugs.
