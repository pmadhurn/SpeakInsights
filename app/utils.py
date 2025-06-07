import logging
import functools
import time
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('speakinsights.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def timer(func):
    """Decorator to time function execution"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        logger.info(f"{func.__name__} took {end - start:.2f} seconds")
        return result
    return wrapper

def safe_process(func):
    """Decorator for safe processing with error handling"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error in {func.__name__}: {str(e)}")
            return None
    return wrapper

def validate_audio_file(file_path):
    """Validate audio file"""
    valid_extensions = ['.mp3', '.wav', '.m4a', '.mp4', '.mpeg', '.mpga', '.webm']
    
    if not os.path.exists(file_path):
        raise ValueError("File does not exist")
    
    ext = os.path.splitext(file_path)[1].lower()
    if ext not in valid_extensions:
        raise ValueError(f"Invalid file type. Supported types: {', '.join(valid_extensions)}")
    
    # Check file size
    file_size = os.path.getsize(file_path)
    if file_size > config.MAX_FILE_SIZE:
        raise ValueError(f"File too large. Maximum size: {config.MAX_FILE_SIZE / (1024*1024)}MB")
    
    return True