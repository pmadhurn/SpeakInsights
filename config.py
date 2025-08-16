import os
import json
from pathlib import Path

class Config:
    def __init__(self):
        # Load config.json if it exists
        config_file = Path("config.json")
        if config_file.exists():
            with open(config_file, 'r') as f:
                json_config = json.load(f)
        else:
            json_config = {}
        
        # Model settings - prioritize environment variables, then JSON config, then defaults
        model_settings = json_config.get("model_settings", {})
        self.WHISPER_MODEL = os.environ.get("WHISPER_MODEL", model_settings.get("whisper_model", "base"))
        self.SUMMARIZER_MODEL = model_settings.get("summarizer_model", "sshleifer/distilbart-xsum-1-1")
        self.SENTIMENT_MODEL = model_settings.get("sentiment_model", "distilbert-base-uncased-finetuned-sst-2-english")
        self.MAX_SUMMARY_LENGTH = model_settings.get("max_summary_length", 150)
        
        # App settings
        app_settings = json_config.get("app_settings", {})
        self.APP_TITLE = app_settings.get("title", "SpeakInsights")
        self.APP_VERSION = app_settings.get("version", "1.0.0")
        self.MAX_UPLOAD_SIZE_MB = app_settings.get("max_upload_size_mb", 100)
        
        # Processing settings
        processing_settings = json_config.get("processing_settings", {})
        self.CHUNK_SIZE = processing_settings.get("chunk_size", 1000)
        self.MAX_ACTION_ITEMS = processing_settings.get("max_action_items", 10)
        self.ENABLE_SPEAKER_DETECTION = processing_settings.get("enable_speaker_detection", False)
        self.LANGUAGES = processing_settings.get("languages", ["en"])
        
        # File settings
        self.UPLOAD_FOLDER = "data/audio"
        self.TRANSCRIPT_FOLDER = "data/transcripts"
        self.EXPORT_FOLDER = "data/exports"
        self.MAX_FILE_SIZE = self.MAX_UPLOAD_SIZE_MB * 1024 * 1024
        
        # Database settings
        self.DATABASE_URL = os.environ.get('DATABASE_URL')
        self.SQLITE_PATH = os.environ.get('SQLITE_PATH', 'speakinsights.db')
        
        # API settings - avoid port conflicts
        self.API_HOST = "0.0.0.0"
        self.MAIN_API_PORT = 8000  # Main FastAPI app
        self.EXTERNAL_API_PORT = 3000  # External API access
        self.STREAMLIT_PORT = 8501  # Streamlit frontend
        
        # Security settings
        self.ALLOWED_ORIGINS = ["http://localhost:8501", "http://localhost:3000", "http://127.0.0.1:8501", "http://127.0.0.1:3000"]
        
        # Integration settings
        integration_settings = json_config.get("integration_settings", {})
        self.MCP_ENABLED = integration_settings.get("mcp_enabled", True)
        self.EXPORT_FORMATS = integration_settings.get("export_formats", ["json", "txt", "csv"])
        self.AUTO_EXPORT = integration_settings.get("auto_export", False)

config = Config()