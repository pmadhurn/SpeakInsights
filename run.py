import subprocess
import time
import os
import sys
import signal
from pathlib import Path
from config import config

def cleanup_processes(processes):
    """Clean up running processes"""
    for process in processes:
        if process and process.poll() is None:
            try:
                process.terminate()
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
            except Exception as e:
                print(f"Warning: Could not terminate process: {e}")

def main():
    print(f"[START] Starting {config.APP_TITLE} v{config.APP_VERSION}...")
    
    # Check if MCP server flag is passed
    if len(sys.argv) > 1 and sys.argv[1] == "--mcp":
        print("[MCP] Starting MCP Server for Claude integration...")
        try:
            os.system("python mcp_server.py")
        except KeyboardInterrupt:
            print("\n[STOP] MCP Server stopped")
        return
    
    processes = []
    
    try:
        # Ensure data directories exist
        Path(config.UPLOAD_FOLDER).mkdir(parents=True, exist_ok=True)
        Path(config.TRANSCRIPT_FOLDER).mkdir(parents=True, exist_ok=True)
        Path(config.EXPORT_FOLDER).mkdir(parents=True, exist_ok=True)
        
        # Start external API server
        print(f"[API] Starting external API server on port {config.EXTERNAL_API_PORT}...")
        api_process = subprocess.Popen([
            sys.executable, "api_server.py"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        processes.append(api_process)
        time.sleep(2)
        
        # Check if API server started successfully
        if api_process.poll() is not None:
            # Get the actual error output
            stdout, stderr = api_process.communicate()
            print("[ERROR] External API server failed to start")
            print(f"STDOUT: {stdout.decode()}")
            print(f"STDERR: {stderr.decode()}")
            return
        
        print(f"[OK] External API server running on http://localhost:{config.EXTERNAL_API_PORT}")
        
        # Start main FastAPI backend
        print(f"[BACKEND] Starting main backend on port {config.MAIN_API_PORT}...")
        backend_process = subprocess.Popen([
            sys.executable, "-m", "uvicorn", "app.main:app", 
            "--host", config.API_HOST, 
            "--port", str(config.MAIN_API_PORT),
            "--reload"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        processes.append(backend_process)
        time.sleep(3)
        
        # Check if backend started successfully
        if backend_process.poll() is not None:
            print("[ERROR] Main backend failed to start")
            return
        
        print(f"[OK] Main backend running on http://localhost:{config.MAIN_API_PORT}")
        
        # Start Streamlit frontend
        print(f"[FRONTEND] Starting frontend on port {config.STREAMLIT_PORT}...")
        frontend_cmd = [
            sys.executable, "-m", "streamlit", "run", "frontend/app.py",
            "--server.port", str(config.STREAMLIT_PORT),
            "--server.address", "0.0.0.0",
            "--server.headless", "true",
            "--browser.gatherUsageStats", "false"
        ]
        
        # Run frontend in foreground so we can catch Ctrl+C
        subprocess.run(frontend_cmd)
        
    except KeyboardInterrupt:
        print("\n[STOP] Shutting down services...")
    except Exception as e:
        print(f"[ERROR] Error: {e}")
    finally:
        cleanup_processes(processes)
        print("[OK] All services stopped")

if __name__ == "__main__":
    main()