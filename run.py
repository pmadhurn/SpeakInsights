import subprocess
import time
import webbrowser
import os

def main():
    print("🚀 Starting SpeakInsights...")
    
    # Start FastAPI backend (optional)
    # backend_process = subprocess.Popen(["uvicorn", "app.main:app", "--reload"])
    # print("✅ Backend started on http://localhost:8000")
    # time.sleep(3)
    
    # Start Streamlit frontend
    print("🎯 Starting frontend...")
    os.system("streamlit run frontend/app.py")

if __name__ == "__main__":
    main()