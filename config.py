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
        self.SUMMARIZE_FULL_TRANSCRIPT = processing_settings.get("summarize_full_transcript", True)
        self.MAX_CHUNK_SUMMARIES = processing_settings.get("max_chunk_summaries", 10)
        
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
        
        # Ollama settings
        ollama_settings = json_config.get("ollama_settings", {})
        self.USE_OLLAMA = ollama_settings.get("enabled", True)
        self.OLLAMA_BASE_URL = ollama_settings.get("base_url", "http://localhost:11434")
        self.OLLAMA_MODEL = ollama_settings.get("model", "llama3.2")
        self.OLLAMA_TIMEOUT = ollama_settings.get("timeout", 120)
        self.FALLBACK_TO_LOCAL = ollama_settings.get("fallback_to_local", True)
        
        # Webhook settings
        webhook_settings = json_config.get("webhook_settings", {})
        self.WEBHOOK_ENABLED = webhook_settings.get("enabled", False)
        self.WEBHOOK_URL = webhook_settings.get("n8n_webhook_url", "")
        self.WEBHOOK_SEND_ACTION_ITEMS = webhook_settings.get("send_action_items", True)
        self.WEBHOOK_SEND_SUMMARIES = webhook_settings.get("send_summaries", False)
        self.WEBHOOK_TIMEOUT = webhook_settings.get("timeout", 30)
        self.WEBHOOK_RETRY_ATTEMPTS = webhook_settings.get("retry_attempts", 3)
        self.WEBHOOK_INCLUDE_METADATA = webhook_settings.get("include_meeting_metadata", True)
        
        # WhisperX settings
        whisperx_settings = json_config.get("whisperx_settings", {})
        self.WHISPERX_ENABLED = whisperx_settings.get("enabled", True)
        self.WHISPERX_MODEL_SIZE = whisperx_settings.get("model_size", "large-v2")
        self.WHISPERX_COMPUTE_TYPE = whisperx_settings.get("compute_type", "float16")
        self.WHISPERX_BATCH_SIZE = whisperx_settings.get("batch_size", 16)
        self.WHISPERX_ENABLE_VAD = whisperx_settings.get("enable_vad", True)
        self.WHISPERX_VAD_ONSET = whisperx_settings.get("vad_onset", 0.500)
        self.WHISPERX_VAD_OFFSET = whisperx_settings.get("vad_offset", 0.363)
        self.WHISPERX_ENABLE_DIARIZATION = whisperx_settings.get("enable_diarization", True)
        self.WHISPERX_MIN_SPEAKERS = whisperx_settings.get("min_speakers", None)
        self.WHISPERX_MAX_SPEAKERS = whisperx_settings.get("max_speakers", None)
        self.WHISPERX_HF_TOKEN = whisperx_settings.get("hf_token", None) or os.environ.get("HF_TOKEN")
        self.WHISPERX_DEVICE = whisperx_settings.get("device", "auto")
        self.WHISPERX_LANGUAGE = whisperx_settings.get("language", "en")
        self.WHISPERX_ALIGN_MODEL = whisperx_settings.get("align_model", None)
        self.WHISPERX_INTERPOLATE_METHOD = whisperx_settings.get("interpolate_method", "nearest")
        
        # Store the raw JSON config for webhook manager
        self.RAW_CONFIG = json_config

config = Config()