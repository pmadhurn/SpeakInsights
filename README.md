# SpeakInsights - AI Meeting Assistant

SpeakInsights is an AI-powered tool designed to help users transcribe, summarize, and analyze audio recordings of meetings. It extracts key information, identifies action items, and provides sentiment analysis to offer comprehensive insights into meeting discussions.

## Features

*   **Audio Transcription:** Converts audio recordings of meetings into text using OpenAI's Whisper model.
*   **Meeting Summarization:** Generates concise summaries of meeting transcripts.
*   **Sentiment Analysis:** Analyzes the overall sentiment of the meeting discussion.
*   **Action Item Extraction:** Identifies and extracts actionable tasks mentioned during the meeting.
*   **Web Interface:** Provides a user-friendly interface built with Streamlit to upload audio files and view insights.
*   **API Endpoints:** Offers a FastAPI backend with endpoints for programmatic access and integration.
*   **Data Persistence:** Saves meeting data, including transcripts and generated insights, in an SQLite database.

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
*   **`app/database.py`**: Manages all interactions with the SQLite database (`speakinsights.db`). This includes:
    *   Initializing the database schema.
    *   Saving new meeting records (transcript, summary, sentiment, etc.).
    *   Fetching existing meeting records.
*   **`app/models.py`**: Defines Pydantic data models used for request and response validation in the FastAPI application, ensuring data consistency.
*   **`app/nlp_module.py`**: Houses the Natural Language Processing functionalities. It uses pre-trained models from the `transformers` library to:
    *   Summarize transcribed text.
    *   Perform sentiment analysis on the text.
    *   Extract potential action items from the transcript.
*   **`app/transcription.py`**: Responsible for converting audio files to text. It utilizes the `openai-whisper` library to perform the speech-to-text transcription.
*   **`frontend/app.py`**: The main file for the Streamlit web application. It provides the user interface for:
    *   Uploading meeting audio files.
    *   Displaying meeting details, including transcripts, summaries, sentiment, and action items.
    *   Viewing basic meeting analytics.
*   **`config.py`**: Contains configuration settings for the application, such as model names for Whisper and NLP tasks, file upload paths, database path, and API server settings.
*   **`requirements.txt`**: Lists all Python dependencies required to run the project.
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
    Review `config.py` if you need to change default settings like model choices, file paths, or API ports. Some configurations might also be in `config.json`.

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
        *   **Summary:** A concise overview of the meeting.
        *   **Full Transcript:** The complete text transcribed from the audio. You can also download the transcript.
        *   **Action Items:** A list of tasks identified from the discussion.
        *   **Analytics:** Basic analytics like word count, estimated duration, and sentiment.

The backend API can also be used by other services if needed. API documentation is typically available via FastAPI's auto-generated docs (usually at `http://localhost:8000/docs` or `http://localhost:8000/redoc` when the backend server is running).

## Contributing

Contributions to SpeakInsights are welcome! If you have suggestions for improvements or want to contribute code, please feel free to:

1.  Fork the repository.
2.  Create a new branch for your feature or bug fix.
3.  Make your changes.
4.  Submit a pull request with a clear description of your changes.

Alternatively, you can open an issue to discuss potential changes or report bugs.
