# SpeakInsights MCP Integration

This document explains how to use SpeakInsights with Claude Desktop through the Model Context Protocol (MCP) integration.

## Setup Complete ✅

The MCP server has been successfully configured for your SpeakInsights project!

## How to Use

### 1. Start the MCP Server
```bash
python run.py --mcp
```

### 2. Restart Claude Desktop
After starting the MCP server, restart Claude Desktop to load the new configuration.

### 3. Available Commands in Claude

Once connected, you can ask Claude to interact with your SpeakInsights data using natural language:

#### View Meetings
- "Show me all meetings in SpeakInsights"
- "List the last 5 meetings"
- "What meetings do I have?"

#### Search Transcripts
- "Search for mentions of 'budget' in meeting transcripts"
- "Find discussions about 'project timeline'"
- "Look for keywords 'deadline' in my meetings"

#### Get Meeting Details
- "Show me details for meeting ID 3"
- "What was discussed in meeting 5?"
- "Give me the full transcript of meeting 2"

#### Sentiment Analysis
- "What's the sentiment analysis for recent meetings?"
- "Show sentiment for meeting ID 4"
- "Analyze the mood of my meetings"

#### Export Data
- "Export meeting 3 data as JSON"
- "Save meeting 1 information as text file"
- "Export all data for meeting 2"

## Available Tools

The MCP server provides these tools:

1. **get_meetings** - Retrieve meeting list
2. **get_meeting_details** - Get detailed meeting information
3. **search_transcripts** - Search through transcripts
4. **get_sentiment_analysis** - Get sentiment analysis results
5. **export_meeting_data** - Export meeting data to files

## Data Access

The MCP server can access:
- SQLite database (`speakinsights.db`)
- Audio files in `data/audio/`
- Transcripts in `data/transcripts/`
- All meeting metadata and analysis results

## Configuration Location

Claude Desktop configuration: `%APPDATA%\Claude\claude_desktop_config.json`

## Troubleshooting

### If Claude doesn't see the MCP server:
1. Make sure the MCP server is running: `python run.py --mcp`
2. Restart Claude Desktop completely
3. Check that the configuration file exists at the correct location

### If you get permission errors:
- Make sure the virtual environment is activated
- Run the server from the SpeakInsights project directory

### If the database is not found:
- Ensure `speakinsights.db` exists in the project root
- Run some meetings through the main app first to populate data

## Example Conversation

```
You: "What meetings do I have in SpeakInsights?"
Claude: *uses get_meetings tool* "Here are your recent meetings:
- Meeting ID 1: Weekly Standup (2024-01-15)
- Meeting ID 2: Project Review (2024-01-16)
- Meeting ID 3: Client Call (2024-01-17)"

You: "Show me the sentiment analysis for meeting 2"
Claude: *uses get_sentiment_analysis tool* "Meeting 2 (Project Review) has a POSITIVE sentiment with a confidence score of 0.85..."
```

## Benefits

- **Natural Language Interface**: Ask questions in plain English
- **Privacy-First**: All data stays local on your machine
- **Real-time Access**: Direct access to your meeting database
- **Export Capabilities**: Save meeting data in multiple formats
- **Search Functionality**: Find specific content across all transcripts

Enjoy using SpeakInsights with Claude Desktop! 🚀
