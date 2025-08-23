#!/usr/bin/env python3
"""
Test Current SpeakInsights Setup
Verify that standard Whisper transcription works
"""

import sys
import os

# Add the app directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_basic_imports():
    """Test basic imports work"""
    print("🔄 Testing basic imports...")
    
    try:
        import streamlit
        print(f"✅ Streamlit {streamlit.__version__} imported successfully")
    except ImportError as e:
        print(f"❌ Streamlit import failed: {e}")
        return False
    
    try:
        import whisper
        print("✅ OpenAI Whisper imported successfully")
    except ImportError as e:
        print(f"❌ Whisper import failed: {e}")
        return False
    
    try:
        import torch
        print(f"✅ PyTorch imported successfully")
        if torch.cuda.is_available():
            print(f"✅ CUDA available: {torch.cuda.get_device_name(0)}")
        else:
            print("⚠️ CUDA not available - using CPU")
    except ImportError as e:
        print(f"❌ PyTorch import failed: {e}")
        return False
    
    try:
        import numpy as np
        print(f"✅ NumPy {np.__version__} imported successfully")
    except ImportError as e:
        print(f"❌ NumPy import failed: {e}")
        return False
    
    return True

def test_config_loading():
    """Test configuration loading"""
    print("\n🔄 Testing configuration...")
    
    try:
        from config import config
        print("✅ Configuration loaded successfully")
        print(f"  - Whisper model: {config.WHISPER_MODEL}")
        print(f"  - App title: {config.APP_TITLE}")
        print(f"  - Ollama enabled: {config.USE_OLLAMA}")
        return True
    except Exception as e:
        print(f"❌ Configuration loading failed: {e}")
        return False

def test_transcription_module():
    """Test transcription module"""
    print("\n🔄 Testing transcription module...")
    
    try:
        from app.transcription import (
            transcribe_audio, 
            get_transcript_text, 
            check_whisperx_status,
            transcribe_audio_basic
        )
        print("✅ Transcription module imported successfully")
        
        # Check WhisperX status
        status = check_whisperx_status()
        print(f"  - WhisperX available: {status['available']}")
        if not status['available']:
            print(f"  - WhisperX error: {status.get('error', 'Unknown')}")
        
        return True
    except Exception as e:
        print(f"❌ Transcription module test failed: {e}")
        return False

def test_database_module():
    """Test database module"""
    print("\n🔄 Testing database module...")
    
    try:
        from app.database import get_database_connection, init_database
        print("✅ Database module imported successfully")
        
        # Test database connection
        conn, db_type = get_database_connection()
        print(f"  - Database type: {db_type}")
        conn.close()
        
        return True
    except Exception as e:
        print(f"❌ Database module test failed: {e}")
        return False

def test_nlp_module():
    """Test NLP module"""
    print("\n🔄 Testing NLP module...")
    
    try:
        from app.nlp_module import summarize_text, analyze_sentiment, extract_action_items
        print("✅ NLP module imported successfully")
        
        # Test basic functionality
        test_text = "This is a test meeting about project updates."
        
        sentiment = analyze_sentiment(test_text)
        print(f"  - Sentiment analysis: {sentiment}")
        
        return True
    except Exception as e:
        print(f"❌ NLP module test failed: {e}")
        return False

def test_whisper_basic():
    """Test basic Whisper functionality"""
    print("\n🔄 Testing basic Whisper...")
    
    try:
        from app.transcription import get_whisper_model
        
        print("  - Loading Whisper model (this may take a moment)...")
        model = get_whisper_model()
        print("✅ Whisper model loaded successfully")
        
        return True
    except Exception as e:
        print(f"❌ Whisper model test failed: {e}")
        return False

def main():
    print("🧪 SpeakInsights Current Setup Test")
    print("="*50)
    
    tests = [
        ("Basic Imports", test_basic_imports),
        ("Configuration", test_config_loading),
        ("Transcription Module", test_transcription_module),
        ("Database Module", test_database_module),
        ("NLP Module", test_nlp_module),
        ("Whisper Basic", test_whisper_basic)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "="*50)
    print("TEST SUMMARY")
    print("="*50)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    print(f"✅ Passed: {passed}/{total}")
    print(f"❌ Failed: {total - passed}/{total}")
    
    print("\nDetailed Results:")
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"  {status} - {test_name}")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED!")
        print("✅ SpeakInsights is ready to use with standard Whisper")
        print("📝 Upload audio files to test transcription")
        print("🚀 Run: streamlit run frontend/app.py")
    elif passed >= total * 0.8:
        print("\n⚠️ MOSTLY WORKING")
        print("✅ Core functionality available")
        print("⚠️ Some features may be limited")
    else:
        print("\n❌ SIGNIFICANT ISSUES")
        print("❌ Core functionality may not work properly")
        print("🔧 Check error messages above")
    
    print(f"\n📋 NOTES:")
    print("- WhisperX unavailable due to NumPy compatibility")
    print("- Standard Whisper transcription should work")
    print("- See WHISPERX_COMPATIBILITY.md for WhisperX solutions")

if __name__ == "__main__":
    main()