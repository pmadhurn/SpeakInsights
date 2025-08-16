# Docker MCP Integration for SpeakInsights

This document explains how to use SpeakInsights with Claude Desktop through Docker and the Model Context Protocol (MCP) integration.

## 🐳 Docker Setup Instructions

### Prerequisites
- Docker Desktop installed and running
- Claude Desktop installed
- Git repository cloned to your local machine

### Step 1: Build the Docker Image
```bash
docker build -t speakinsights:latest .
```

### Step 2: Configure Claude Desktop for Docker
```bash
python setup_docker_mcp.py
```

### Step 3: Start the Services
```bash
docker-compose up -d
```

### Step 4: Test MCP Server (Optional)
```bash
# Test the MCP server directly
docker run --rm -it \
  -v ./data:/app/data \
  -v ./speakinsights.db:/app/speakinsights.db \
  speakinsights:latest python run.py --mcp
```

### Step 5: Restart Claude Desktop
Close and restart Claude Desktop to load the new Docker MCP configuration.

## 🚀 Usage Examples

### Available Docker Commands

1. **Start Main Application:**
   ```bash
   docker-compose up speakinsights
   ```

2. **Start MCP Server Only:**
   ```bash
   docker-compose up speakinsights-mcp
   ```

3. **View Service Logs:**
   ```bash
   docker-compose logs -f speakinsights-mcp
   ```

4. **Stop All Services:**
   ```bash
   docker-compose down
   ```

### Claude Desktop Integration

After setup, you can ask Claude:
- "Show me all meetings in my SpeakInsights Docker container"
- "Search for 'budget' in my containerized meeting transcripts"
- "Get container status for SpeakInsights"
- "Export meeting data from the Docker container"
- "What's the sentiment analysis for meetings in Docker?"

## 📊 Data Persistence

Data is persisted through Docker volumes:
- `./data:/app/data` - Audio files, transcripts, exports
- `./speakinsights.db:/app/speakinsights.db` - SQLite database

## 🔧 Available Tools in Claude

The Docker MCP server provides these tools:

1. **get_meetings** - Retrieve meeting list from Docker container
2. **get_meeting_details** - Get detailed meeting information
3. **search_transcripts** - Search through transcripts in container
4. **get_sentiment_analysis** - Get sentiment analysis results
5. **export_meeting_data** - Export meeting data to files
6. **get_container_status** - Get Docker container status and info

## 🛠 Troubleshooting

### Common Issues:

1. **Port Conflicts:**
   ```bash
   # Check running containers
   docker ps
   # Stop conflicting containers
   docker stop <container_id>
   ```

2. **Volume Mount Issues:**
   ```bash
   # Ensure data directories exist
   mkdir -p data/audio data/transcripts data/exports data/meetings data/mcp_exports
   ```

3. **MCP Connection Issues:**
   - Restart Claude Desktop completely
   - Check Docker container logs: `docker-compose logs speakinsights-mcp`
   - Verify configuration: `cat %APPDATA%\\Claude\\claude_desktop_config.json`

4. **Container Build Issues:**
   ```bash
   # Clean rebuild
   docker-compose down
   docker system prune -f
   docker build --no-cache -t speakinsights:latest .
   docker-compose up -d
   ```

## 🔄 Development Workflow

### After Making Code Changes:
```bash
# Stop services
docker-compose down

# Rebuild image
docker build -t speakinsights:latest .

# Start services
docker-compose up -d

# View logs
docker-compose logs -f speakinsights-mcp
```

### Quick Restart MCP Only:
```bash
docker-compose restart speakinsights-mcp
```

## 📋 Example Claude Conversation

```
You: "What's the status of my SpeakInsights Docker container?"
Claude: *uses get_container_status tool* 
"Your SpeakInsights is running in a Docker Container with:
- Environment: Docker Container
- Platform: Linux-5.4.0-linux-x86_64
- Python Version: 3.9.x
- Database: /app/speakinsights.db (exists: true)
- Data Directory: /app/data (exists: true)"

You: "Show me my recent meetings from the Docker container"
Claude: *uses get_meetings tool*
"Recent Meetings (Docker Container):
- ID: 1, Title: Weekly Standup, Date: 2024-01-15, Audio: meeting_001.wav
- ID: 2, Title: Project Review, Date: 2024-01-16, Audio: meeting_002.wav"

You: "Export meeting 1 as JSON from the container"
Claude: *uses export_meeting_data tool*
"Meeting data exported to: /app/data/mcp_exports/meeting_1.json (Docker Container)"
```

## 🌟 Benefits of Docker MCP Integration

- **Containerized Environment**: Consistent runtime environment
- **Easy Deployment**: Simple docker-compose setup
- **Isolated Dependencies**: No conflicts with host system
- **Scalable**: Can run multiple instances
- **Privacy-First**: All data stays in your containers
- **Natural Language Interface**: Ask questions in plain English
- **Real-time Access**: Direct access to containerized database

## 📁 File Structure

```
SpeakInsights/
├── docker-compose.yml          # Docker services configuration
├── Dockerfile                  # Container build instructions
├── mcp_server.py              # MCP server with Docker support
├── setup_docker_mcp.py        # Docker MCP configuration script
├── run.py                     # Updated with --mcp flag
├── requirements.txt           # Including mcp and psutil
└── data/                      # Volume-mounted data directory
    ├── audio/
    ├── transcripts/
    ├── exports/
    └── mcp_exports/           # MCP export directory
```

## 🎯 Quick Start Commands

```bash
# Complete setup in one go
python setup_docker_mcp.py && docker build -t speakinsights:latest . && docker-compose up -d

# Check everything is working
docker-compose ps
docker-compose logs speakinsights-mcp

# Ready to use with Claude Desktop! 🎉
```

Enjoy using your Dockerized SpeakInsights with Claude Desktop! 🚀🐳
