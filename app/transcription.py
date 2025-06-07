import whisper
import os

print("Loading Whisper model... This may take a minute on first run.")
model = whisper.load_model("base")  # Using 'base' for speed

def transcribe_audio(audio_path):
    """Transcribe audio file using Whisper"""
    try:
        print(f"Transcribing {audio_path}...")
        result = model.transcribe(audio_path)
        return result["text"]
    except Exception as e:
        return f"Error: {str(e)}"

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