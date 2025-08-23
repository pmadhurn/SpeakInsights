import whisper
import os
import torch
from typing import Dict, Any, Union
from config import config

# Try to import WhisperX
try:
    from .whisperx_transcription import transcribe_with_whisperx, WHISPERX_AVAILABLE, WHISPERX_ERROR
    WHISPERX_INTEGRATION = True
except ImportError as e:
    WHISPERX_INTEGRATION = False
    WHISPERX_AVAILABLE = False
    WHISPERX_ERROR = str(e)

# Check GPU availability for Whisper
def get_whisper_device():
    """Get the best available device for Whisper"""
    if torch.cuda.is_available():
        print(f"[GPU] Whisper will use GPU: {torch.cuda.get_device_name(0)}")
        return "cuda"
    else:
        print("[CPU] Whisper will use CPU")
        return "cpu"

# Get device info
WHISPER_DEVICE = get_whisper_device()

# Lazy loading - model will be loaded when first needed
_model = None

def get_whisper_model():
    """Get Whisper model with lazy loading and GPU support"""
    global _model
    if _model is None:
        print(f"Loading Whisper model '{config.WHISPER_MODEL}' on {WHISPER_DEVICE.upper()}... This may take a minute on first run.")
        try:
            _model = whisper.load_model(config.WHISPER_MODEL, device=WHISPER_DEVICE)
            print(f"[OK] Whisper model loaded successfully on {WHISPER_DEVICE.upper()}")
        except Exception as e:
            print(f"[ERROR] Error loading Whisper model: {e}")
            print("Falling back to 'tiny' model...")
            _model = whisper.load_model("tiny", device=WHISPER_DEVICE)
    return _model

def transcribe_audio_basic(audio_path: str) -> str:
    """Basic transcription using standard Whisper (fallback method)"""
    if not os.path.exists(audio_path):
        return f"Error: Audio file not found: {audio_path}"
    
    try:
        print(f"[Whisper] Transcribing {audio_path}...")
        model = get_whisper_model()
        result = model.transcribe(audio_path, language="en" if "en" in config.LANGUAGES else None)
        transcript = result["text"].strip()
        
        if not transcript:
            return "Error: No speech detected in audio file"
            
        print(f"[Whisper] Transcription completed ({len(transcript)} characters)")
        return transcript
    except Exception as e:
        error_msg = f"Error during transcription: {str(e)}"
        print(f"[ERROR] {error_msg}")
        return error_msg

def transcribe_audio(audio_path: str, use_whisperx: bool = None) -> Union[str, Dict[str, Any]]:
    """
    Enhanced transcription function that can use WhisperX or fallback to standard Whisper
    
    Args:
        audio_path: Path to audio file
        use_whisperx: Force WhisperX usage (None = auto-detect from config)
    
    Returns:
        String transcript (basic mode) or Dict with enhanced data (WhisperX mode)
    """
    
    if not os.path.exists(audio_path):
        return f"Error: Audio file not found: {audio_path}"
    
    # Determine which transcription method to use
    if use_whisperx is None:
        use_whisperx = getattr(config, 'WHISPERX_ENABLED', True) and WHISPERX_AVAILABLE
    
    # Try WhisperX first if enabled and available
    if use_whisperx and WHISPERX_INTEGRATION:
        try:
            print(f"[WhisperX] Starting enhanced transcription for {audio_path}")
            
            result = transcribe_with_whisperx(
                audio_path=audio_path,
                enable_vad=getattr(config, 'WHISPERX_ENABLE_VAD', True),
                enable_diarization=getattr(config, 'WHISPERX_ENABLE_DIARIZATION', True),
                min_speakers=getattr(config, 'WHISPERX_MIN_SPEAKERS', None),
                max_speakers=getattr(config, 'WHISPERX_MAX_SPEAKERS', None)
            )
            
            print(f"[WhisperX] Enhanced transcription completed successfully")
            print(f"[WhisperX] Detected {len(result['speakers'])} speakers, {result['processing_info']['total_segments']} segments")
            
            return result
            
        except Exception as e:
            print(f"[WARNING] WhisperX transcription failed: {e}")
            print("[INFO] Falling back to standard Whisper...")
            
            # Fallback to basic Whisper
            return transcribe_audio_basic(audio_path)
    
    else:
        # Use standard Whisper
        if not use_whisperx:
            print("[INFO] Using standard Whisper (WhisperX disabled in config)")
        elif not WHISPERX_AVAILABLE:
            print("[INFO] Using standard Whisper (WhisperX not installed)")
        
        return transcribe_audio_basic(audio_path)

def get_transcript_text(transcription_result: Union[str, Dict[str, Any]]) -> str:
    """
    Extract plain text transcript from transcription result
    
    Args:
        transcription_result: Result from transcribe_audio()
    
    Returns:
        Plain text transcript
    """
    
    if isinstance(transcription_result, str):
        # Basic Whisper result
        return transcription_result
    elif isinstance(transcription_result, dict):
        # WhisperX result
        return transcription_result.get('transcript', '')
    else:
        return str(transcription_result)

def get_formatted_transcript(transcription_result: Union[str, Dict[str, Any]]) -> str:
    """
    Get formatted transcript with speaker labels if available
    
    Args:
        transcription_result: Result from transcribe_audio()
    
    Returns:
        Formatted transcript (with speakers if available)
    """
    
    if isinstance(transcription_result, str):
        # Basic Whisper result - no speaker info
        return transcription_result
    elif isinstance(transcription_result, dict):
        # WhisperX result - use formatted version if available
        if transcription_result.get('has_speakers', False):
            return transcription_result.get('formatted_transcript', transcription_result.get('transcript', ''))
        else:
            return transcription_result.get('transcript', '')
    else:
        return str(transcription_result)

def get_transcription_metadata(transcription_result: Union[str, Dict[str, Any]]) -> Dict[str, Any]:
    """
    Extract metadata from transcription result
    
    Args:
        transcription_result: Result from transcribe_audio()
    
    Returns:
        Dictionary with metadata
    """
    
    if isinstance(transcription_result, dict):
        # WhisperX result with rich metadata
        return {
            'has_speakers': transcription_result.get('has_speakers', False),
            'speakers': transcription_result.get('speakers', []),
            'language': transcription_result.get('language', 'en'),
            'total_segments': transcription_result.get('processing_info', {}).get('total_segments', 0),
            'total_words': transcription_result.get('processing_info', {}).get('total_words', 0),
            'total_speakers': transcription_result.get('processing_info', {}).get('total_speakers', 0),
            'duration': transcription_result.get('processing_info', {}).get('duration', 0),
            'method': 'whisperx'
        }
    else:
        # Basic Whisper result
        return {
            'has_speakers': False,
            'speakers': [],
            'language': 'en',
            'method': 'whisper'
        }

def check_whisperx_status() -> Dict[str, Any]:
    """Check WhisperX availability and configuration"""
    
    status = {
        'available': WHISPERX_AVAILABLE,
        'integration': WHISPERX_INTEGRATION,
        'enabled': getattr(config, 'WHISPERX_ENABLED', True),
        'model_size': getattr(config, 'WHISPERX_MODEL_SIZE', 'large-v2'),
        'diarization_enabled': getattr(config, 'WHISPERX_ENABLE_DIARIZATION', True),
        'vad_enabled': getattr(config, 'WHISPERX_ENABLE_VAD', True),
        'hf_token_configured': bool(getattr(config, 'WHISPERX_HF_TOKEN', None)),
        'device': getattr(config, 'WHISPERX_DEVICE', 'auto'),
        'error': WHISPERX_ERROR if not WHISPERX_AVAILABLE else None
    }
    
    return status

# Test function
if __name__ == "__main__":
    # Test with a sample audio file
    test_audio = input("Enter path to an audio file to test: ")
    if os.path.exists(test_audio):
        transcript = transcribe_audio(test_audio)
        print("\nTranscript:")
        print(transcript)
    else:
        print("File not found!")