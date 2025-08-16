#!/usr/bin/env python3
"""
Setup script for SpeakInsights MCP Server
Fixes common issues and ensures proper configuration
"""
import os
import sys
import subprocess
import sqlite3
from pathlib import Path

def check_dependencies():
    """Check if all required dependencies are installed"""
    print("🔍 Checking dependencies...")
    
    required_packages = [
        'mcp',
        'psutil', 
        'anyio',
        'sqlite3',
        'asyncio'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package} - MISSING")
    
    if missing_packages:
        print(f"\n⚠️ Missing packages: {missing_packages}")
        print("Run: pip install " + " ".join(missing_packages))
        return False
    
    print("✅ All dependencies are installed")
    return True

def setup_database():
    """Setup the SQLite database"""
    print("\n🗄️ Setting up database...")
    
    db_path = "speakinsights.db"
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Create meetings table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS meetings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                date TEXT NOT NULL,
                transcript TEXT,
                summary TEXT,
                sentiment TEXT,
                action_items TEXT,
                audio_filename TEXT
            )
        ''')
        
        # Create sample data for testing
        cursor.execute('''
            INSERT OR IGNORE INTO meetings (title, date, transcript, summary, sentiment, action_items, audio_filename)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            "Sample Meeting",
            "2024-01-01 10:00:00",
            "This is a sample transcript for testing the MCP server.",
            "Sample meeting summary for testing purposes.",
            "Positive (85%)",
            '["Sample action item 1", "Sample action item 2"]',
            "sample_audio.mp3"
        ))
        
        conn.commit()
        conn.close()
        print("✅ Database setup complete")
        return True
        
    except Exception as e:
        print(f"❌ Database setup failed: {e}")
        return False

def setup_directories():
    """Setup required directories"""
    print("\n📁 Setting up directories...")
    
    directories = [
        "data",
        "data/audio", 
        "data/meetings",
        "data/mcp_exports",
        "data/transcripts"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✅ {directory}")
    
    print("✅ All directories created")

def test_mcp_server():
    """Test the MCP server"""
    print("\n🧪 Testing MCP server...")
    
    try:
        # Import and test the MCP server
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from mcp_server import app, DB_PATH
        
        # Test database connection
        if os.path.exists(DB_PATH):
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM meetings")
            count = cursor.fetchone()[0]
            print(f"✅ Database connected with {count} meetings")
            conn.close()
        else:
            print("⚠️ Database not found")
        
        print("✅ MCP server test passed")
        return True
        
    except Exception as e:
        print(f"❌ MCP server test failed: {e}")
        return False

def create_docker_compose_override():
    """Create a docker-compose override for development"""
    print("\n🐳 Creating Docker Compose override...")
    
    override_content = """version: '3.8'

services:
  speakinsights-mcp:
    environment:
      - DEBUG=1
      - LOG_LEVEL=DEBUG
    volumes:
      - ./mcp_server.py:/app/mcp_server.py
      - ./test_mcp_server.py:/app/test_mcp_server.py
    command: python -u mcp_server.py
"""
    
    with open("docker-compose.override.yml", "w") as f:
        f.write(override_content)
    
    print("✅ Docker Compose override created")

def main():
    """Main setup function"""
    print("🚀 SpeakInsights MCP Server Setup")
    print("=" * 40)
    
    # Check dependencies
    if not check_dependencies():
        print("\n❌ Setup failed: Missing dependencies")
        return False
    
    # Setup directories
    setup_directories()
    
    # Setup database
    if not setup_database():
        print("\n❌ Setup failed: Database setup failed")
        return False
    
    # Test MCP server
    if not test_mcp_server():
        print("\n❌ Setup failed: MCP server test failed")
        return False
    
    # Create Docker override
    create_docker_compose_override()
    
    print("\n" + "=" * 40)
    print("✅ Setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Rebuild Docker containers: docker-compose build")
    print("2. Start the services: docker-compose up -d")
    print("3. Check MCP server logs: docker logs speakinsights-speakinsights-mcp-1")
    print("4. Test connection: python test_mcp_server.py")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
