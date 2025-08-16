# SpeakInsights MCP Docker Setup Guide

This guide will help you fix the MCP (Model Context Protocol) server setup issues and get Claude Desktop connected to your SpeakInsights Docker container.

## Issues Fixed

1. **Persistent Container**: Now uses `docker exec` instead of `docker run` for reliable connections
2. **Proper Dependencies**: All MCP requirements are correctly installed
3. **Database Schema**: Fixed missing columns and proper table structure
4. **Volume Mounting**: Corrected database and data directory mounting
5. **Configuration**: Proper Claude Desktop config format

## Step-by-Step Setup

### 1. Clean Up Previous Setup (if needed)

```powershell
# Stop any running containers
docker-compose down

# Remove old containers (optional)
docker container prune -f

# Remove old images (optional, if you want to rebuild completely)
docker image rm speakinsights:latest
```

### 2. Build and Start the Containers

```powershell
# Run the setup script
python setup_docker_mcp.py

# Start the containers using PowerShell script
.\start_docker_mcp.ps1
```

Or manually:

```powershell
# Build the Docker image
docker build -t speakinsights:latest .

# Start the services
docker-compose up -d

# Check if containers are running
docker-compose ps
```

### 3. Verify the Setup

```powershell
# Run the test script
python test_mcp_connection.py
```

This will check:
- ✅ Docker container is running
- ✅ MCP dependencies are installed
- ✅ Database is accessible
- ✅ MCP server module loads correctly
- ✅ Claude Desktop config is correct

### 4. Configure Claude Desktop

The setup script automatically creates the correct configuration at:
`%USERPROFILE%\AppData\Roaming\Claude\claude_desktop_config.json`

The configuration should look like:

```json
{
  "mcpServers": {
    "speakinsights": {
      "command": "docker",
      "args": [
        "exec",
        "-i",
        "speakinsights-mcp",
        "python",
        "mcp_server.py"
      ],
      "env": {
        "PYTHONPATH": "/app"
      }
    }
  }
}
```

### 5. Restart Claude Desktop

After the setup is complete:

1. Close Claude Desktop completely
2. Wait 5 seconds
3. Restart Claude Desktop
4. The MCP server should now be available

## Testing the Connection

Once setup is complete, you can test Claude's connection by asking:

- "What SpeakInsights data do you have access to?"
- "Get the list of meetings"
- "What is the container status?"

## Troubleshooting

### Container Not Running
```powershell
# Check container status
docker-compose ps

# View container logs
docker-compose logs speakinsights-mcp

# Restart the container
docker-compose restart speakinsights-mcp
```

### MCP Dependencies Missing
```powershell
# Rebuild with fresh dependencies
docker-compose down
docker-compose up -d --build
```

### Database Issues
```powershell
# Check if database file exists
docker exec speakinsights-mcp ls -la /app/speakinsights.db

# Test database connection
docker exec speakinsights-mcp python -c "import sqlite3; print('DB accessible:', sqlite3.connect('/app/speakinsights.db').execute('SELECT name FROM sqlite_master').fetchall())"
```

### Claude Desktop Config Issues
```powershell
# Recreate the config
python setup_docker_mcp.py

# Check the config file
Get-Content "$env:USERPROFILE\AppData\Roaming\Claude\claude_desktop_config.json"
```

## Key Changes Made

### 1. Dockerfile
- Fixed persistent container approach with `tail -f /dev/null`
- Proper MCP dependencies installation
- Correct user permissions

### 2. docker-compose.yml
- Added `container_name: speakinsights-mcp` for consistent naming
- Removed unnecessary port mappings for MCP server
- Simplified environment variables

### 3. MCP Server
- Fixed database schema with proper columns
- Better error handling
- Environment detection (Docker vs Local)

### 4. Configuration
- Uses `docker exec` instead of `docker run`
- Simplified arguments
- Proper container naming

## Manual Commands Reference

```powershell
# Build and start
docker build -t speakinsights:latest .
docker-compose up -d

# Test MCP server manually
docker exec -i speakinsights-mcp python mcp_server.py

# View logs
docker-compose logs -f speakinsights-mcp

# Stop services
docker-compose down

# Complete rebuild
docker-compose down
docker build -t speakinsights:latest . --no-cache
docker-compose up -d
```

## Success Indicators

When everything is working correctly:

1. ✅ `docker-compose ps` shows `speakinsights-mcp` as "Up"
2. ✅ `python test_mcp_connection.py` passes all tests
3. ✅ Claude Desktop shows no connection errors in logs
4. ✅ You can ask Claude about SpeakInsights data and get responses

## Support

If you encounter issues:

1. Run `python test_mcp_connection.py` to identify specific problems
2. Check container logs: `docker-compose logs speakinsights-mcp`
3. Verify Claude Desktop config exists and is correct
4. Ensure Claude Desktop is fully restarted after configuration changes

The key improvement is using a persistent container that Claude can reliably connect to via `docker exec` instead of creating new containers each time with `docker run`.
