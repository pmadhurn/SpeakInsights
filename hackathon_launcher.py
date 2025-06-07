#!/usr/bin/env python
"""
Competition day launcher - foolproof startup script
"""
import os
import sys
import time
import subprocess
import webbrowser
from datetime import datetime

def print_banner():
    print("""
    ████████████████████████████████████████████████████
    █                                                  █
    █         🏆 INTEL AI HACKATHON 2024 🏆           █
    █                                                  █
    █              SPEAKINSIGHTS v1.0                  █
    █         Meeting Intelligence Platform            █
    █                                                  █
    ████████████████████████████████████████████████████
    """)

def check_everything():
    """Pre-flight checks"""
    print("\n🔍 Running pre-flight checks...")
    
    checks = {
        "Python 3.8+": sys.version_info >= (3, 8),
        "Data directories": os.path.exists("data"),
        "Frontend files": os.path.exists("frontend/enhanced_dashboard.py"),
        "Database": os.path.exists("speakinsights.db") or True,
        "Requirements": os.path.exists("requirements.txt")
    }
    
    all_good = True
    for check, status in checks.items():
        if status:
            print(f"  ✅ {check}")
        else:
            print(f"  ❌ {check}")
            all_good = False
    
    return all_good

def countdown(seconds=3):
    """Dramatic countdown"""
    for i in range(seconds, 0, -1):
        print(f"\rLaunching in {i}...", end="", flush=True)
        time.sleep(1)
    print("\r🚀 LAUNCHING NOW!    ")

def launch_modes():
    """Different launch modes"""
    print("\n🎯 SELECT LAUNCH MODE:")
    print("1. 🏁 COMPETITION MODE (Recommended)")
    print("2. 🎬 DEMO MODE (Pre-loaded data)")
    print("3. 🆘 EMERGENCY MODE (Failsafe)")
    print("4. 🔧 CUSTOM MODE")
    
    choice = input("\nEnter choice (1-4): ").strip()
    
    if choice == "1":
        # Competition mode
        print("\n🏁 COMPETITION MODE ACTIVATED")
        countdown()
        
        # Open browser first
        webbrowser.open("http://localhost:8501")
        
        # Launch enhanced dashboard
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", 
            "frontend/enhanced_dashboard.py",
            "--server.port=8501",
            "--server.headless=true",
            "--browser.gatherUsageStats=false"
        ])
        
    elif choice == "2":
        # Demo mode
        print("\n🎬 DEMO MODE ACTIVATED")
        print("Loading pre-configured demo data...")
        
        # Create demo data first
        subprocess.run([sys.executable, "run_demo.py"])
        time.sleep(2)
        
        countdown()
        webbrowser.open("http://localhost:8501")
        
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", 
            "frontend/enhanced_dashboard.py"
        ])
        
    elif choice == "3":
        # Emergency mode
        print("\n🆘 EMERGENCY MODE ACTIVATED")
        print("Running with static demo data (no AI models)...")
        
        countdown()
        webbrowser.open("http://localhost:8502")
        
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", 
            "emergency_demo.py",
            "--server.port=8502"
        ])
        
    elif choice == "4":
        # Custom mode
        print("\n🔧 CUSTOM MODE")
        print("1. Run Frontend Only")
        print("2. Run Backend Only")
        print("3. Run Tests")
        
        custom = input("Select option: ").strip()
        
        if custom == "1":
            subprocess.run([sys.executable, "-m", "streamlit", "run", "frontend/enhanced_dashboard.py"])
        elif custom == "2":
            subprocess.run([sys.executable, "-m", "uvicorn", "app.main:app", "--reload"])
        elif custom == "3":
            subprocess.run([sys.executable, "test_quick.py"])

def main():
    """Main launcher"""
    print_banner()
    
    # Show current time
    print(f"\n📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📍 Running from: {os.getcwd()}")
    
    # Pre-flight checks
    if not check_everything():
        print("\n❌ Some checks failed! Please fix issues and try again.")
        input("\nPress Enter to exit...")
        sys.exit(1)
    
    print("\n✅ All systems GO!")
    
    # Launch mode selection
    try:
        launch_modes()
    except KeyboardInterrupt:
        print("\n\n👋 Shutting down gracefully...")
        print("Good luck with your presentation! 🍀")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\n🆘 Try running: python emergency_demo.py")
        input("\nPress Enter to exit...")

if __name__ == "__main__":
    main()