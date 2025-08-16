import subprocess
import time
import webbrowser
import os
import sys

def main():
    print("🚀 Starting SpeakInsights...")
    
    # Check if MCP server flag is passed
    if len(sys.argv) > 1 and sys.argv[1] == "--mcp":
        print("🔗 Starting MCP Server for Claude integration...")
        os.system("python mcp_server.py")
        return
    
    # Start API server for external access
    api_process = subprocess.Popen(["python", "api_server.py"])
    print("✅ API server started on http://localhost:3000")
    time.sleep(3)
    
    # Start Streamlit frontend
    print("🎯 Starting frontend...")
    try:
        os.system("streamlit run frontend/app.py")
    finally:
        # Cleanup API process when Streamlit exits
        api_process.terminate()

if __name__ == "__main__":
    main()