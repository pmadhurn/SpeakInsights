"""
Generate simple test audio files for demo
"""
import os

def create_test_audio():
    """Create a simple test audio file using text-to-speech"""
    try:
        # Try using pyttsx3 (offline TTS)
        import pyttsx3
        
        engine = pyttsx3.init()
        
        test_scripts = {
            "team_meeting.mp3": """
            Hello everyone, welcome to our team meeting. Today we need to discuss 
            the project timeline. John will handle the backend development. 
            Sarah will work on the frontend. We must complete this by Friday.
            """,
            
            "planning_session.mp3": """
            Good morning team. Let's plan our Q4 strategy. We need to increase 
            our productivity by 20 percent. I will prepare the budget report. 
            The marketing team should launch the campaign next week.
            """,
            
            "standup.mp3": """
            Quick standup everyone. Yesterday I completed the API integration. 
            Today I will work on testing. I'm blocked on the database access. 
            We need to review the code by tomorrow.
            """
        }
        
        os.makedirs("data/test_audio", exist_ok=True)
        
        for filename, text in test_scripts.items():
            output_path = f"data/test_audio/{filename}"
            engine.save_to_file(text, output_path)
        
        engine.runAndWait()
        print("✅ Test audio files created!")
        
    except ImportError:
        print("⚠️  Install pyttsx3 for test audio: pip install pyttsx3")
        
        # Create a text file instead
        test_transcript = """
        This is a sample meeting transcript. We discussed several important 
        topics today. First, we need to complete the project by next Friday. 
        John will handle the backend tasks. Sarah will work on the UI design. 
        Mike should coordinate with the client. We must improve our communication.
        """
        
        os.makedirs("data/test_audio", exist_ok=True)
        with open("data/test_audio/sample_transcript.txt", "w") as f:
            f.write(test_transcript)
        
        print("✅ Sample transcript created instead")

if __name__ == "__main__":
    create_test_audio()