"""Docker MCP Configuration for SpeakInsights"""
import json
from pathlib import Path
import os

def create_docker_mcp_config():
    """Create MCP configuration for Claude Desktop with Docker"""
    
    # Get the current directory
    project_dir = Path.cwd()
    
    config = {
        "mcpServers": {
            "speakinsights": {
                "command": "docker",
                "args": [
                    "exec", 
                    "-i",
                    "speakinsights-mcp",
                    "python", "mcp_server.py"
                ],
                "env": {
                    "PYTHONPATH": "/app"
                }
            }
        }
    }
    
    # Windows Claude Desktop config path
    config_path = Path.home() / "AppData/Roaming/Claude/claude_desktop_config.json"
    config_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Load existing config if it exists
    if config_path.exists():
        with open(config_path, 'r') as f:
            existing_config = json.load(f)
        if "mcpServers" not in existing_config:
            existing_config["mcpServers"] = {}
        existing_config["mcpServers"].update(config["mcpServers"])
        config = existing_config
    
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)
    
    print("✅ Docker MCP Configuration created successfully!")
    print(f"📍 Configuration file: {config_path}")
    print("\n🔧 Docker Configuration:")
    print(json.dumps(config, indent=2))
    print("\n📋 Next steps:")
    print("1. Build Docker image: docker build -t speakinsights:latest .")
    print("2. Start services: docker-compose up -d")
    print("3. Restart Claude Desktop")
    print("4. Test MCP: Ask Claude about your SpeakInsights data!")

def create_docker_startup_script():
    """Create a startup script for Docker MCP testing"""
    script_content = """#!/bin/bash
echo "Docker SpeakInsights MCP Setup"
echo "=============================="

echo "Building Docker image..."
docker build -t speakinsights:latest .

echo "Starting services..."
docker-compose up -d

echo "Services started!"
echo "Container status:"
docker-compose ps

echo ""
echo "MCP Server ready!"
echo "Now restart Claude Desktop to use the integration."
echo ""
echo "Available commands:"
echo "  - View logs: docker-compose logs -f speakinsights-mcp"
echo "  - Stop services: docker-compose down"
echo "  - Rebuild: docker-compose down && docker build -t speakinsights:latest . && docker-compose up -d"
"""
    
    script_path = Path("start_docker_mcp.sh")
    with open(script_path, 'w', encoding='utf-8') as f:
        f.write(script_content)
    
    print(f"✅ Docker startup script created: {script_path}")

if __name__ == "__main__":
    print("🐳 Setting up SpeakInsights Docker MCP integration...")
    create_docker_mcp_config()
    create_docker_startup_script()
    print("\n🎉 Docker MCP setup complete!")
