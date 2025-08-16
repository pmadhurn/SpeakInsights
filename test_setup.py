#!/usr/bin/env python3
"""
Test script to verify SpeakInsights setup
"""

import sys
import os
from pathlib import Path

def test_imports():
    """Test if all required modules can be imported"""
    print("🧪 Testing imports...")
    
    try:
        import fastapi
        print("✅ FastAPI")
    except ImportError:
        print("❌ FastAPI - run: pip install fastapi")
        return False
    
    try:
        import streamlit
        print("✅ Streamlit")
    except ImportError:
        print("❌ Streamlit - run: pip install streamlit")
        return False
    
    try:
        import whisper
        print("✅ OpenAI Whisper")
    except ImportError:
        print("❌ OpenAI Whisper - run: pip install openai-whisper")
        return False
    
    try:
        import transformers
        print("✅ Transformers")
    except ImportError:
        print("❌ Transformers - run: pip install transformers")
        return False
    
    try:
        from config import config
        print(f"✅ Config loaded - Whisper model: {config.WHISPER_MODEL}")
    except ImportError as e:
        print(f"❌ Config import failed: {e}")
        return False
    
    return True

def test_database():
    """Test database connection"""
    print("\n🗄️ Testing database...")
    
    try:
        from app.database import get_database_connection, init_database
        
        # Initialize database
        init_database()
        
        # Test connection
        conn, db_type = get_database_connection()
        cursor = conn.cursor()
        
        if db_type == 'postgresql':
            cursor.execute("SELECT version()")
        else:
            cursor.execute("SELECT sqlite_version()")
        
        version = cursor.fetchone()
        conn.close()
        
        print(f"✅ Database connection successful ({db_type})")
        print(f"   Version: {version[0] if version else 'Unknown'}")
        return True
        
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False

def test_directories():
    """Test if required directories exist"""
    print("\n📁 Testing directories...")
    
    required_dirs = ["data", "data/audio", "data/transcripts", "data/exports"]
    
    for directory in required_dirs:
        path = Path(directory)
        if path.exists():
            print(f"✅ {directory}")
        else:
            try:
                path.mkdir(parents=True, exist_ok=True)
                print(f"✅ {directory} (created)")
            except Exception as e:
                print(f"❌ {directory} - {e}")
                return False
    
    return True

def test_models():
    """Test if models can be loaded"""
    print("\n🤖 Testing model loading...")
    
    try:
        from app.transcription import get_whisper_model
        model = get_whisper_model()
        print("✅ Whisper model loaded")
    except Exception as e:
        print(f"❌ Whisper model failed: {e}")
        return False
    
    try:
        from app.nlp_module import get_summarizer
        summarizer = get_summarizer()
        print("✅ Summarization model loaded")
    except Exception as e:
        print(f"❌ Summarization model failed: {e}")
        return False
    
    try:
        from app.nlp_module import get_sentiment_analyzer
        sentiment = get_sentiment_analyzer()
        print("✅ Sentiment model loaded")
    except Exception as e:
        print(f"❌ Sentiment model failed: {e}")
        return False
    
    return True

def main():
    print("=" * 60)
    print("🧪 SpeakInsights Setup Test")
    print("=" * 60)
    
    tests = [
        ("Imports", test_imports),
        ("Directories", test_directories),
        ("Database", test_database),
        ("Models", test_models),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 60)
    print("📊 Test Results:")
    print("=" * 60)
    
    all_passed = True
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{test_name:20} {status}")
        if not passed:
            all_passed = False
    
    print("=" * 60)
    
    if all_passed:
        print("🎉 All tests passed! SpeakInsights is ready to use.")
        print("Run: python start.py")
        return 0
    else:
        print("⚠️  Some tests failed. Please fix the issues above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())