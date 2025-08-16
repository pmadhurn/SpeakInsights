"""Test MCP connection to Docker container"""
import subprocess
import sys
import json
from pathlib import Path

def test_docker_container():
    """Test if Docker container is running"""
    try:
        result = subprocess.run(['docker', 'ps', '--filter', 'name=speakinsights-mcp', '--format', 'json'], 
                              capture_output=True, text=True, check=True)
        
        if result.stdout.strip():
            container_info = json.loads(result.stdout.strip())
            print(f"✅ Container 'speakinsights-mcp' is running")
            print(f"   Status: {container_info.get('Status', 'Unknown')}")
            return True
        else:
            print("❌ Container 'speakinsights-mcp' is not running")
            return False
    except subprocess.CalledProcessError as e:
        print(f"❌ Error checking Docker container: {e}")
        return False
    except json.JSONDecodeError:
        print("❌ Error parsing Docker container info")
        return False

def test_mcp_dependencies():
    """Test if MCP dependencies are installed in container"""
    try:
        result = subprocess.run(['docker', 'exec', 'speakinsights-mcp', 'python', '-c', 
                                'import mcp; print("MCP version:", mcp.__version__)'], 
                              capture_output=True, text=True, check=True)
        
        print(f"✅ MCP dependencies installed: {result.stdout.strip()}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ MCP dependencies not available: {e}")
        print("   Try rebuilding the container with: docker-compose down && docker-compose up -d --build")
        return False

def test_database_access():
    """Test if database is accessible in container"""
    try:
        result = subprocess.run(['docker', 'exec', 'speakinsights-mcp', 'python', '-c', 
                                'import sqlite3, os; print("DB exists:", os.path.exists("/app/speakinsights.db"))'], 
                              capture_output=True, text=True, check=True)
        
        print(f"✅ Database access: {result.stdout.strip()}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Database not accessible: {e}")
        return False

def test_mcp_server():
    """Test if MCP server can start (just import test)"""
    try:
        result = subprocess.run(['docker', 'exec', 'speakinsights-mcp', 'python', '-c', 
                                'import mcp_server; print("MCP server module loaded successfully")'], 
                              capture_output=True, text=True, check=True)
        
        print(f"✅ MCP server: {result.stdout.strip()}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ MCP server issue: {e}")
        if "ModuleNotFoundError" in str(e):
            print("   Make sure mcp_server.py exists in the container")
        return False

def check_claude_config():
    """Check if Claude Desktop config exists and is correct"""
    config_path = Path.home() / "AppData/Roaming/Claude/claude_desktop_config.json"
    
    if not config_path.exists():
        print("❌ Claude Desktop config not found")
        print(f"   Expected at: {config_path}")
        return False
    
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        if "mcpServers" not in config:
            print("❌ No mcpServers section in Claude config")
            return False
        
        if "speakinsights" not in config["mcpServers"]:
            print("❌ SpeakInsights MCP server not configured in Claude config")
            return False
        
        server_config = config["mcpServers"]["speakinsights"]
        if server_config.get("command") == "docker" and "exec" in server_config.get("args", []):
            print("✅ Claude Desktop config is correct")
            return True
        else:
            print("❌ Claude Desktop config uses old format")
            print("   Run setup_docker_mcp.py to update the configuration")
            return False
            
    except Exception as e:
        print(f"❌ Error reading Claude config: {e}")
        return False

def main():
    """Run all tests"""
    print("🔍 Testing SpeakInsights MCP Docker Setup")
    print("=" * 50)
    
    tests = [
        ("Docker Container", test_docker_container),
        ("MCP Dependencies", test_mcp_dependencies),
        ("Database Access", test_database_access),
        ("MCP Server Module", test_mcp_server),
        ("Claude Desktop Config", check_claude_config),
    ]
    
    passed = 0
    for test_name, test_func in tests:
        print(f"\n🧪 Testing {test_name}...")
        if test_func():
            passed += 1
    
    print(f"\n📊 Results: {passed}/{len(tests)} tests passed")
    
    if passed == len(tests):
        print("\n🎉 All tests passed! Your MCP setup should work with Claude Desktop.")
        print("\n📋 Next steps:")
        print("1. Restart Claude Desktop")
        print("2. Try asking Claude: 'What SpeakInsights data do you have access to?'")
    else:
        print(f"\n⚠️  {len(tests) - passed} test(s) failed. Please fix the issues above.")
        print("\n🔧 Common fixes:")
        print("- Run: docker-compose up -d --build")
        print("- Run: python setup_docker_mcp.py")
        print("- Restart Claude Desktop")

if __name__ == "__main__":
    main()
