#!/usr/bin/env python3
"""
Unified startup script for SpeakInsights
Handles different startup modes and ensures proper configuration
"""

import sys
import os
import subprocess
import time
from pathlib import Path

def ensure_directories():
    """Ensure required directories exist"""
    directories = ["data", "data/audio", "data/transcripts", "data/exports"]
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
    print("✅ Required directories created")

def check_dependencies():
    """Check if required dependencies are available"""
    try:
        import fastapi
        import streamlit
        import whisper
        import transformers
        print("✅ Core dependencies available")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Please run: pip install -r requirements.txt")
        return False

def start_mcp_server():
    """Start MCP server for Claude integration"""
    print("🔗 Starting MCP Server for Claude integration...")
    try:
        subprocess.run([sys.executable, "mcp_server.py"], check=True)
    except KeyboardInterrupt:
        print("\n🛑 MCP Server stopped")
    except Exception as e:
        print(f"❌ MCP Server error: {e}")

def start_api_only():
    """Start only the API server"""
    print("🌐 Starting API server only...")
    try:
        subprocess.run([
            sys.executable, "-m", "uvicorn", "app.main:app",
            "--host", "0.0.0.0", "--port", "8000", "--reload"
        ], check=True)
    except KeyboardInterrupt:
        print("\n🛑 API server stopped")

def start_frontend_only():
    """Start only the frontend"""
    print("🎯 Starting frontend only...")
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "frontend/app.py",
            "--server.port", "8501", "--server.address", "0.0.0.0"
        ], check=True)
    except KeyboardInterrupt:
        print("\n🛑 Frontend stopped")

def start_full_application():
    """Start the full application (API + Frontend)"""
    print("🚀 Starting full SpeakInsights application...")
    try:
        subprocess.run([sys.executable, "run.py"], check=True)
    except KeyboardInterrupt:
        print("\n🛑 Application stopped")

def main():
    print("=" * 60)
    print("🎤 SpeakInsights - AI Meeting Assistant")
    print("=" * 60)
    
    # Check dependencies first
    if not check_dependencies():
        return 1
    
    # Ensure directories exist
    ensure_directories()
    
    # Parse command line arguments
    if len(sys.argv) > 1:
        mode = sys.argv[1].lower()
        
        if mode == "--mcp":
            start_mcp_server()
        elif mode == "--api":
            start_api_only()
        elif mode == "--frontend":
            start_frontend_only()
        elif mode == "--help":
            print("Usage: python start.py [mode]")
            print("Modes:")
            print("  --mcp       Start MCP server for Claude integration")
            print("  --api       Start API server only")
            print("  --frontend  Start frontend only")
            print("  (no args)   Start full application")
            return 0
        else:
            print(f"Unknown mode: {mode}")
            print("Use --help for available modes")
            return 1
    else:
        start_full_application()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())