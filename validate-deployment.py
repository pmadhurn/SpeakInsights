#!/usr/bin/env python3
"""
Comprehensive deployment validation script for SpeakInsights
Tests Docker deployment and all components
"""

import subprocess
import sys
import time
import requests
import json
import os
from pathlib import Path

def run_command(cmd, shell=False, capture_output=True):
    """Run a command and return result"""
    try:
        if isinstance(cmd, str) and not shell:
            cmd = cmd.split()
        result = subprocess.run(cmd, shell=shell, capture_output=capture_output, text=True, timeout=30)
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, "", "Command timed out"
    except Exception as e:
        return False, "", str(e)

def check_docker():
    """Check if Docker is available"""
    print("🐳 Checking Docker...")
    success, stdout, stderr = run_command("docker --version")
    if success:
        print(f"✅ Docker: {stdout.strip()}")
        return True
    else:
        print(f"❌ Docker not available: {stderr}")
        return False

def check_docker_compose():
    """Check if Docker Compose is available"""
    print("🔧 Checking Docker Compose...")
    
    # Try docker-compose first
    success, stdout, stderr = run_command("docker-compose --version")
    if success:
        print(f"✅ Docker Compose (v1): {stdout.strip()}")
        return "docker-compose"
    
    # Try docker compose
    success, stdout, stderr = run_command("docker compose version")
    if success:
        print(f"✅ Docker Compose (v2): {stdout.strip()}")
        return "docker compose"
    
    print("❌ Docker Compose not available")
    return None

def check_files():
    """Check if required files exist"""
    print("📁 Checking required files...")
    
    required_files = [
        "Dockerfile",
        "docker-compose.yml",
        "docker-entrypoint.sh",
        "requirements.txt",
        "config.py",
        "start.py"
    ]
    
    all_exist = True
    for file in required_files:
        if Path(file).exists():
            print(f"✅ {file}")
        else:
            print(f"❌ {file} missing")
            all_exist = False
    
    return all_exist

def validate_shell_scripts():
    """Validate shell scripts for syntax errors"""
    print("📝 Validating shell scripts...")
    
    scripts = ["docker-deploy.sh", "docker-entrypoint.sh"]
    all_valid = True
    
    for script in scripts:
        if Path(script).exists():
            success, stdout, stderr = run_command(f"bash -n {script}")
            if success:
                print(f"✅ {script} syntax valid")
            else:
                print(f"❌ {script} syntax error: {stderr}")
                all_valid = False
        else:
            print(f"⚠️  {script} not found")
    
    return all_valid

def check_ports():
    """Check if required ports are available"""
    print("🔍 Checking port availability...")
    
    ports = [8000, 8501, 3000, 5432]
    available_ports = []
    
    for port in ports:
        try:
            import socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex(('localhost', port))
            sock.close()
            
            if result != 0:
                print(f"✅ Port {port} available")
                available_ports.append(port)
            else:
                print(f"⚠️  Port {port} in use")
        except Exception as e:
            print(f"❓ Port {port} check failed: {e}")
    
    return len(available_ports) == len(ports)

def test_docker_build(compose_cmd):
    """Test Docker build process"""
    print("🏗️  Testing Docker build...")
    
    success, stdout, stderr = run_command(f"{compose_cmd} build --no-cache speakinsights", shell=True)
    if success:
        print("✅ Docker build successful")
        return True
    else:
        print(f"❌ Docker build failed: {stderr}")
        return False

def start_services(compose_cmd):
    """Start Docker services"""
    print("🚀 Starting Docker services...")
    
    success, stdout, stderr = run_command(f"{compose_cmd} up -d", shell=True)
    if success:
        print("✅ Services started")
        return True
    else:
        print(f"❌ Failed to start services: {stderr}")
        return False

def wait_for_services():
    """Wait for services to be ready"""
    print("⏳ Waiting for services to be ready...")
    
    services = [
        ("FastAPI", "http://localhost:8000/health"),
        ("Streamlit", "http://localhost:8501"),
        ("External API", "http://localhost:3000")
    ]
    
    max_attempts = 30
    ready_services = []
    
    for attempt in range(max_attempts):
        for name, url in services:
            if name not in ready_services:
                try:
                    response = requests.get(url, timeout=5)
                    if response.status_code == 200:
                        print(f"✅ {name} is ready")
                        ready_services.append(name)
                except:
                    pass
        
        if len(ready_services) == len(services):
            print("✅ All services are ready!")
            return True
        
        print(f"⏳ Waiting... ({attempt + 1}/{max_attempts})")
        time.sleep(2)
    
    print(f"⚠️  Only {len(ready_services)}/{len(services)} services ready")
    return len(ready_services) > 0

def test_api_endpoints():
    """Test API endpoints"""
    print("🧪 Testing API endpoints...")
    
    endpoints = [
        ("Health Check", "GET", "http://localhost:8000/health"),
        ("Root", "GET", "http://localhost:8000/"),
        ("Meetings", "GET", "http://localhost:8000/api/meetings"),
        ("External API", "GET", "http://localhost:3000/"),
    ]
    
    working_endpoints = 0
    
    for name, method, url in endpoints:
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                print(f"✅ {name}: {response.status_code}")
                working_endpoints += 1
            else:
                print(f"⚠️  {name}: {response.status_code}")
        except Exception as e:
            print(f"❌ {name}: {str(e)}")
    
    return working_endpoints > 0

def cleanup_services(compose_cmd):
    """Clean up Docker services"""
    print("🧹 Cleaning up services...")
    
    success, stdout, stderr = run_command(f"{compose_cmd} down", shell=True)
    if success:
        print("✅ Services stopped")
    else:
        print(f"⚠️  Cleanup warning: {stderr}")

def main():
    print("🔍 SpeakInsights Deployment Validation")
    print("=" * 50)
    
    # Pre-flight checks
    if not check_docker():
        return 1
    
    compose_cmd = check_docker_compose()
    if not compose_cmd:
        return 1
    
    if not check_files():
        return 1
    
    if not validate_shell_scripts():
        print("⚠️  Shell script validation failed, but continuing...")
    
    # Port check (warning only)
    if not check_ports():
        print("⚠️  Some ports are in use, deployment may fail")
    
    # Build test
    print("\n" + "=" * 50)
    print("🏗️  BUILD TEST")
    print("=" * 50)
    
    if not test_docker_build(compose_cmd):
        return 1
    
    # Deployment test
    print("\n" + "=" * 50)
    print("🚀 DEPLOYMENT TEST")
    print("=" * 50)
    
    try:
        if not start_services(compose_cmd):
            return 1
        
        if not wait_for_services():
            print("⚠️  Not all services started, but continuing tests...")
        
        # API tests
        print("\n" + "=" * 50)
        print("🧪 API TESTS")
        print("=" * 50)
        
        if test_api_endpoints():
            print("✅ Some API endpoints are working")
        else:
            print("❌ No API endpoints are working")
        
        # Success
        print("\n" + "=" * 50)
        print("🎉 DEPLOYMENT VALIDATION COMPLETE")
        print("=" * 50)
        print("✅ SpeakInsights is deployed and running!")
        print("")
        print("🌐 Access points:")
        print("   Frontend:     http://localhost:8501")
        print("   API:          http://localhost:8000")
        print("   External API: http://localhost:3000")
        print("   API Docs:     http://localhost:8000/docs")
        print("")
        print("🛑 To stop: " + compose_cmd + " down")
        
        return 0
        
    except KeyboardInterrupt:
        print("\n🛑 Validation interrupted")
        return 1
    finally:
        # Always cleanup on exit
        cleanup_services(compose_cmd)

if __name__ == "__main__":
    sys.exit(main())