import whisper
import os
from config import config

# Lazy loading - model will be loaded when first needed
_model = None

def get_whisper_model():
    """Get Whisper model with lazy loading"""
    global _model
    if _model is None:
        print(f"Loading Whisper model '{config.WHISPER_MODEL}'... This may take a minute on first run.")
        try:
            _model = whisper.load_model(config.WHISPER_MODEL)
            print("✅ Whisper model loaded successfully")
        except Exception as e:
            print(f"❌ Error loading Whisper model: {e}")
            print("Falling back to 'tiny' model...")
            _model = whisper.load_model("tiny")
    return _model

def transcribe_audio(audio_path):
    """Transcribe audio file using Whisper"""
    if not os.path.exists(audio_path):
        return f"Error: Audio file not found: {audio_path}"
    
    try:
        print(f"Transcribing {audio_path}...")
        model = get_whisper_model()
        result = model.transcribe(audio_path, language="en" if "en" in config.LANGUAGES else None)
        transcript = result["text"].strip()
        
        if not transcript:
            return "Error: No speech detected in audio file"
            
        print(f"✅ Transcription completed ({len(transcript)} characters)")
        return transcript
    except Exception as e:
        error_msg = f"Error during transcription: {str(e)}"
        print(f"❌ {error_msg}")
        return error_msg

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