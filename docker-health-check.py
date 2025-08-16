#!/usr/bin/env python3
"""
Docker health check script for SpeakInsights
Tests if all services are running correctly
"""

import requests
import sys
import time
import json

def check_service(name, url, timeout=10):
    """Check if a service is healthy"""
    try:
        response = requests.get(url, timeout=timeout)
        if response.status_code == 200:
            print(f"✅ {name}: Healthy")
            return True
        else:
            print(f"❌ {name}: HTTP {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ {name}: {str(e)}")
        return False

def check_database():
    """Check database connectivity through API"""
    try:
        response = requests.get("http://localhost:8000/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "healthy":
                print(f"✅ Database ({data.get('database', 'unknown')}): Healthy")
                return True
        print(f"❌ Database: Unhealthy")
        return False
    except Exception as e:
        print(f"❌ Database: {str(e)}")
        return False

def main():
    print("🏥 SpeakInsights Docker Health Check")
    print("=" * 40)
    
    services = [
        ("FastAPI Backend", "http://localhost:8000/"),
        ("Streamlit Frontend", "http://localhost:8501/"),
        ("External API", "http://localhost:3000/"),
    ]
    
    all_healthy = True
    
    # Check main services
    for name, url in services:
        if not check_service(name, url):
            all_healthy = False
    
    # Check database
    if not check_database():
        all_healthy = False
    
    print("=" * 40)
    
    if all_healthy:
        print("🎉 All services are healthy!")
        return 0
    else:
        print("⚠️  Some services are unhealthy")
        return 1

if __name__ == "__main__":
    sys.exit(main())