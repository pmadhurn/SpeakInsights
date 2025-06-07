"""
Quick test script to verify everything works
"""
import os
import sys
from datetime import datetime

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_basic_functionality():
    """Test core features"""
    print("🧪 Running Quick Tests...\n")
    
    # Test 1: Database
    print("1️⃣ Testing Database...")
    try:
        from app.database import init_database, save_meeting, get_all_meetings
        init_database()
        
        # Save test meeting
        test_meeting = {
            "title": "Test Meeting",
            "date": datetime.now().isoformat(),
            "transcript": "This is a test transcript.",
            "summary": "Test summary",
            "sentiment": "Positive",
            "action_items": ["Test action"],
            "audio_filename": "test.mp3"
        }
        
        meeting_id = save_meeting(test_meeting)
        meetings = get_all_meetings()
        
        assert len(meetings) > 0
        print("✅ Database working!\n")
    except Exception as e:
        print(f"❌ Database error: {e}\n")
    
    # Test 2: NLP Models
    print("2️⃣ Testing NLP Models...")
    try:
        from app.nlp_module import summarize_text, analyze_sentiment
        
        test_text = "This is a great meeting. We accomplished a lot today."
        summary = summarize_text(test_text)
        sentiment = analyze_sentiment(test_text)
        
        assert len(summary) > 0
        assert sentiment is not None
        print(f"✅ NLP working! Sentiment: {sentiment}\n")
    except Exception as e:
        print(f"❌ NLP error: {e}\n")
    
    # Test 3: File Operations
    print("3️⃣ Testing File Operations...")
    try:
        dirs = ["data/audio", "data/transcripts", "data/exports"]
        for dir in dirs:
            os.makedirs(dir, exist_ok=True)
            assert os.path.exists(dir)
        print("✅ File system ready!\n")
    except Exception as e:
        print(f"❌ File system error: {e}\n")
    
    print("🎉 Basic tests complete!")

if __name__ == "__main__":
    test_basic_functionality()