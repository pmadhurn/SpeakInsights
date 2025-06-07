import os

class Config:
    # Whisper settings
    WHISPER_MODEL = os.environ.get("WHISPER_MODEL", "base")
    
    # NLP settings
    SUMMARIZER_MODEL = "sshleifer/distilbart-cnn-6-6"
    SENTIMENT_MODEL = "distilbert-base-uncased-finetuned-sst-2-english"
    
    # File settings
    UPLOAD_FOLDER = "data/audio"
    TRANSCRIPT_FOLDER = "data/transcripts"
    EXPORT_FOLDER = "data/exports"
    MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB
    
    # Database
    DATABASE_PATH = "speakinsights.db"
    
    # API settings
    API_HOST = "0.0.0.0"
    API_PORT = 8000

config = Config()