"""
Master script to run both backend and frontend
"""
import subprocess
import time
import webbrowser
import os
import sys
import threading

def run_backend():
    """Run FastAPI backend"""
    print("🚀 Starting backend API...")
    subprocess.run([sys.executable, "-m", "uvicorn", "app.main:app", "--reload", "--port", "8000"])

def run_frontend():
    """Run Streamlit frontend"""
    print("🎯 Starting frontend...")
    subprocess.run([sys.executable, "-m", "streamlit", "run", "frontend/enhanced_dashboard.py"])

def main():
    print("""
    ╔══════════════════════════════════════╗
    ║       🎙️  SpeakInsights v1.0        ║
    ║   AI-Powered Meeting Intelligence    ║
    ╚══════════════════════════════════════╝
    """)
    
    # Check if demo mode
    if len(sys.argv) > 1 and sys.argv[1] == "--demo":
        print("📊 Running in demo mode...")
        os.system(f"{sys.executable} run_demo.py")
        time.sleep(2)
    
    # Ask user for mode
    print("\nSelect mode:")
    print("1. Frontend only (Recommended for hackathon)")
    print("2. Frontend + Backend API")
    print("3. Backend API only")
    
    choice = input("\nEnter choice (1-3): ").strip()
    
    if choice == "1":
        print("\n✨ Starting SpeakInsights Dashboard...")
        time.sleep(2)
        webbrowser.open("http://localhost:8501")
        run_frontend()
        
    elif choice == "2":
        print("\n✨ Starting Full Stack Application...")
        
        # Start backend in a thread
        backend_thread = threading.Thread(target=run_backend, daemon=True)
        backend_thread.start()
        
        # Wait for backend to start
        time.sleep(5)
        
        # Open browser and start frontend
        webbrowser.open("http://localhost:8501")
        run_frontend()
        
    elif choice == "3":
        print("\n✨ Starting Backend API...")
        webbrowser.open("http://localhost:8000/docs")
        run_backend()
    
    else:
        print("Invalid choice. Exiting.")
        sys.exit(1)

if __name__ == "__main__":
    main()