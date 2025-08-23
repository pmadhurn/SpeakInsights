#!/usr/bin/env python3
"""
WhisperX Setup Script for SpeakInsights
Automated installation and configuration of WhisperX
"""

import os
import sys
import subprocess
import json
from pathlib import Path

def run_command(cmd, description=""):
    """Run a command and handle errors"""
    print(f"🔄 {description}")
    print(f"Running: {cmd}")
    
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed:")
        print(f"Error: {e.stderr}")
        return False

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"❌ Python 3.8+ required, found {version.major}.{version.minor}")
        return False
    
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} is compatible")
    return True

def check_gpu():
    """Check GPU availability"""
    try:
        import torch
        if torch.cuda.is_available():
            gpu_name = torch.cuda.get_device_name(0)
            print(f"✅ GPU detected: {gpu_name}")
            return True
        else:
            print("⚠️ No GPU detected - WhisperX will use CPU (slower)")
            return False
    except ImportError:
        print("⚠️ PyTorch not installed - cannot check GPU")
        return False

def install_whisperx():
    """Install WhisperX and dependencies"""
    print("\n" + "="*60)
    print("INSTALLING WHISPERX")
    print("="*60)
    
    # Install WhisperX
    if not run_command("pip install whisperx", "Installing WhisperX"):
        return False
    
    # Install additional dependencies
    dependencies = [
        "pyannote.audio>=3.1.0",
        "faster-whisper>=0.9.0", 
        "ctranslate2>=3.20.0",
        "onnxruntime>=1.16.0"
    ]
    
    for dep in dependencies:
        if not run_command(f"pip install {dep}", f"Installing {dep}"):
            print(f"⚠️ Warning: Failed to install {dep}")
    
    return True

def test_whisperx_installation():
    """Test WhisperX installation"""
    print("\n" + "="*60)
    print("TESTING WHISPERX INSTALLATION")
    print("="*60)
    
    try:
        import whisperx
        print("✅ WhisperX imported successfully")
        
        # Test model loading
        print("🔄 Testing model loading...")
        device = "cuda" if check_gpu() else "cpu"
        compute_type = "float16" if device == "cuda" else "int8"
        
        model = whisperx.load_model("tiny", device=device, compute_type=compute_type)
        print("✅ WhisperX model loaded successfully")
        
        return True
        
    except ImportError as e:
        print(f"❌ WhisperX import failed: {e}")
        return False
    except Exception as e:
        print(f"❌ WhisperX test failed: {e}")
        return False

def update_config():
    """Update config.json with WhisperX settings"""
    print("\n" + "="*60)
    print("UPDATING CONFIGURATION")
    print("="*60)
    
    config_file = Path("config.json")
    
    if not config_file.exists():
        print("❌ config.json not found")
        return False
    
    try:
        with open(config_file, 'r') as f:
            config = json.load(f)
        
        # Add WhisperX settings if not present
        if "whisperx_settings" not in config:
            config["whisperx_settings"] = {
                "enabled": True,
                "model_size": "large-v2",
                "compute_type": "float16",
                "batch_size": 16,
                "enable_vad": True,
                "vad_onset": 0.500,
                "vad_offset": 0.363,
                "enable_diarization": True,
                "min_speakers": None,
                "max_speakers": None,
                "hf_token": None,
                "device": "auto",
                "language": "en",
                "align_model": None,
                "interpolate_method": "nearest"
            }
            
            # Enable speaker detection in processing settings
            if "processing_settings" in config:
                config["processing_settings"]["enable_speaker_detection"] = True
            
            # Save updated config
            with open(config_file, 'w') as f:
                json.dump(config, f, indent=2)
            
            print("✅ Configuration updated with WhisperX settings")
        else:
            print("✅ WhisperX settings already present in config")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to update config: {e}")
        return False

def setup_huggingface_token():
    """Guide user through Hugging Face token setup"""
    print("\n" + "="*60)
    print("HUGGING FACE TOKEN SETUP")
    print("="*60)
    
    print("For speaker diarization, you need a Hugging Face token.")
    print("This enables WhisperX to identify who is speaking when.")
    print()
    print("Steps to get a token:")
    print("1. Visit: https://huggingface.co/settings/tokens")
    print("2. Create a new token with 'Read' access")
    print("3. Copy the token")
    print()
    
    choice = input("Do you want to add your Hugging Face token now? (y/n): ").lower().strip()
    
    if choice == 'y':
        token = input("Enter your Hugging Face token: ").strip()
        
        if token:
            try:
                # Update config with token
                config_file = Path("config.json")
                with open(config_file, 'r') as f:
                    config = json.load(f)
                
                config["whisperx_settings"]["hf_token"] = token
                
                with open(config_file, 'w') as f:
                    json.dump(config, f, indent=2)
                
                print("✅ Hugging Face token added to config")
                return True
                
            except Exception as e:
                print(f"❌ Failed to save token: {e}")
                return False
        else:
            print("⚠️ No token provided")
    else:
        print("⚠️ Skipping token setup - speaker diarization will be disabled")
        print("You can add the token later in config.json")
    
    return True

def create_demo_script():
    """Create a demo script for testing WhisperX"""
    demo_script = '''#!/usr/bin/env python3
"""
WhisperX Demo Script
Quick test of WhisperX functionality
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.whisperx_transcription import transcribe_with_whisperx, WHISPERX_AVAILABLE

def main():
    if not WHISPERX_AVAILABLE:
        print("❌ WhisperX not available")
        return
    
    print("🎙️ WhisperX Demo")
    print("="*40)
    
    audio_file = input("Enter path to an audio file: ").strip()
    
    if not os.path.exists(audio_file):
        print(f"❌ File not found: {audio_file}")
        return
    
    try:
        print("🔄 Processing with WhisperX...")
        result = transcribe_with_whisperx(audio_file)
        
        print("\\n✅ Processing completed!")
        print(f"Language: {result['language']}")
        print(f"Speakers: {len(result['speakers'])}")
        print(f"Segments: {result['processing_info']['total_segments']}")
        
        if result['has_speakers']:
            print("\\n🎭 Speakers detected:")
            for speaker in result['speakers']:
                print(f"  - {speaker}")
            
            print("\\n📝 Formatted transcript:")
            print(result['formatted_transcript'][:500] + "..." if len(result['formatted_transcript']) > 500 else result['formatted_transcript'])
        else:
            print("\\n📝 Transcript:")
            print(result['transcript'][:500] + "..." if len(result['transcript']) > 500 else result['transcript'])
    
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
'''
    
    try:
        with open("test_whisperx_demo.py", 'w') as f:
            f.write(demo_script)
        print("✅ Demo script created: test_whisperx_demo.py")
        return True
    except Exception as e:
        print(f"❌ Failed to create demo script: {e}")
        return False

def main():
    print("🎙️ WhisperX Setup for SpeakInsights")
    print("="*60)
    
    # Check prerequisites
    if not check_python_version():
        sys.exit(1)
    
    check_gpu()
    
    # Install WhisperX
    if not install_whisperx():
        print("❌ WhisperX installation failed")
        sys.exit(1)
    
    # Test installation
    if not test_whisperx_installation():
        print("❌ WhisperX installation test failed")
        sys.exit(1)
    
    # Update configuration
    if not update_config():
        print("⚠️ Configuration update failed")
    
    # Setup Hugging Face token
    setup_huggingface_token()
    
    # Create demo script
    create_demo_script()
    
    print("\n" + "="*60)
    print("✅ WHISPERX SETUP COMPLETED!")
    print("="*60)
    
    print("\nNext steps:")
    print("1. 🔄 Restart your SpeakInsights application")
    print("2. 🧪 Test with: python test_whisperx_demo.py")
    print("3. 🎙️ Upload audio files to see enhanced transcription")
    print("4. 🎭 Enjoy speaker diarization and word-level timestamps!")
    
    print("\nFeatures now available:")
    print("✅ 70× faster transcription on GPU")
    print("✅ Word-level timestamps")
    print("✅ VAD preprocessing")
    print("✅ Speaker diarization (if HF token configured)")
    print("✅ Enhanced accuracy for long-form audio")

if __name__ == "__main__":
    main()