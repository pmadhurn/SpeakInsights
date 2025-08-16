import json
import sqlite3
import os
import asyncio
from pathlib import Path
from typing import List, Dict, Any
from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import Resource, Tool, TextContent

# Initialize MCP Server
app = Server("speakinsights-mcp")

# Docker-friendly paths - check if running in Docker
if os.path.exists("/app"):
    DB_PATH = "/app/speakinsights.db"
    DATA_DIR = Path("/app/data")
else:
    DB_PATH = "speakinsights.db"
    DATA_DIR = Path("data")

# Ensure data directory exists
DATA_DIR.mkdir(parents=True, exist_ok=True)
(DATA_DIR / "mcp_exports").mkdir(exist_ok=True)

@app.list_resources()
async def list_resources() -> List[Resource]:
    """List available resources from SpeakInsights data"""
    resources = []
    
    # Add database as a resource
    if os.path.exists(DB_PATH):
        resources.append(Resource(
            uri=f"sqlite://{DB_PATH}",
            name="SpeakInsights Database",
            description="SQLite database containing meetings, transcripts, and analysis",
            mimeType="application/x-sqlite3"
        ))
    
    # Add audio files
    audio_dir = DATA_DIR / "audio"
    if audio_dir.exists():
        for audio_file in audio_dir.glob("*"):
            if audio_file.suffix.lower() in ['.mp3', '.wav', '.m4a']:
                resources.append(Resource(
                    uri=f"file://{audio_file}",
                    name=f"Audio: {audio_file.name}",
                    description=f"Audio recording: {audio_file.name}",
                    mimeType=f"audio/{audio_file.suffix[1:]}"
                ))
    
    return resources

@app.read_resource()
async def read_resource(uri: str) -> str:
    """Read resource content"""
    if uri.startswith("sqlite://"):
        db_path = uri.replace("sqlite://", "")
        return await get_database_summary(db_path)
    elif uri.startswith("file://"):
        file_path = uri.replace("file://", "")
        return f"Audio file: {os.path.basename(file_path)}"
    
    return "Resource not found"

@app.list_tools()
async def list_tools() -> List[Tool]:
    """List available tools for interacting with SpeakInsights data"""
    return [
        Tool(
            name="get_meetings",
            description="Get all meetings from the database",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {"type": "integer", "description": "Limit number of results"}
                }
            }
        ),
        Tool(
            name="get_meeting_details",
            description="Get detailed information about a specific meeting",
            inputSchema={
                "type": "object",
                "properties": {
                    "meeting_id": {"type": "integer", "description": "Meeting ID"}
                },
                "required": ["meeting_id"]
            }
        ),
        Tool(
            name="search_transcripts",
            description="Search through meeting transcripts",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query"},
                    "limit": {"type": "integer", "description": "Limit number of results"}
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="get_sentiment_analysis",
            description="Get sentiment analysis for meetings",
            inputSchema={
                "type": "object",
                "properties": {
                    "meeting_id": {"type": "integer", "description": "Meeting ID (optional)"}
                }
            }
        ),
        Tool(
            name="export_meeting_data",
            description="Export meeting data to MCP exports directory",
            inputSchema={
                "type": "object",
                "properties": {
                    "meeting_id": {"type": "integer", "description": "Meeting ID"},
                    "format": {"type": "string", "enum": ["json", "txt"], "description": "Export format"}
                },
                "required": ["meeting_id", "format"]
            }
        ),
        Tool(
            name="get_container_status",
            description="Get Docker container status and information",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        )
    ]

@app.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle tool calls"""
    
    if name == "get_meetings":
        return await get_meetings(arguments.get("limit", 10))
    
    elif name == "get_meeting_details":
        meeting_id = arguments.get("meeting_id")
        return await get_meeting_details(meeting_id)
    
    elif name == "search_transcripts":
        query = arguments.get("query")
        limit = arguments.get("limit", 5)
        return await search_transcripts(query, limit)
    
    elif name == "get_sentiment_analysis":
        meeting_id = arguments.get("meeting_id")
        return await get_sentiment_analysis(meeting_id)
    
    elif name == "export_meeting_data":
        meeting_id = arguments.get("meeting_id")
        format_type = arguments.get("format", "json")
        return await export_meeting_data(meeting_id, format_type)
    
    elif name == "get_container_status":
        return await get_container_status()
    
    return [TextContent(type="text", text="Tool not found")]

# Helper functions
async def get_database_summary(db_path: str) -> str:
    """Get summary of database content"""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get table info
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        environment = "Docker Container" if os.path.exists("/app") else "Local Environment"
        summary = f"SpeakInsights Database Summary ({environment}):\n"
        for table in tables:
            table_name = table[0]
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            summary += f"- {table_name}: {count} records\n"
        
        conn.close()
        return summary
    except Exception as e:
        return f"Error reading database: {str(e)}"

async def get_meetings(limit: int) -> List[TextContent]:
    """Get meetings from database"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, title, created_at, audio_filename 
            FROM meetings 
            ORDER BY created_at DESC 
            LIMIT ?
        """, (limit,))
        
        meetings = cursor.fetchall()
        conn.close()
        
        environment = "Docker Container" if os.path.exists("/app") else "Local Environment"
        result = f"Recent Meetings ({environment}):\n"
        for meeting in meetings:
            result += f"ID: {meeting[0]}, Title: {meeting[1]}, Date: {meeting[2]}, Audio: {meeting[3]}\n"
        
        return [TextContent(type="text", text=result)]
    except Exception as e:
        return [TextContent(type="text", text=f"Error fetching meetings: {str(e)}")]

async def get_meeting_details(meeting_id: int) -> List[TextContent]:
    """Get detailed meeting information"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM meetings WHERE id = ?
        """, (meeting_id,))
        
        meeting = cursor.fetchone()
        if not meeting:
            return [TextContent(type="text", text="Meeting not found")]
        
        # Get column names
        cursor.execute("PRAGMA table_info(meetings)")
        columns = [row[1] for row in cursor.fetchall()]
        
        environment = "Docker Container" if os.path.exists("/app") else "Local Environment"
        result = f"Meeting Details (ID: {meeting_id}) [{environment}]:\n"
        for i, value in enumerate(meeting):
            result += f"{columns[i]}: {value}\n"
        
        conn.close()
        return [TextContent(type="text", text=result)]
    except Exception as e:
        return [TextContent(type="text", text=f"Error fetching meeting details: {str(e)}")]

async def search_transcripts(query: str, limit: int) -> List[TextContent]:
    """Search through transcripts"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, title, transcript 
            FROM meetings 
            WHERE transcript LIKE ? 
            LIMIT ?
        """, (f"%{query}%", limit))
        
        results = cursor.fetchall()
        conn.close()
        
        if not results:
            return [TextContent(type="text", text=f"No transcripts found matching '{query}'")]
        
        result = f"Search Results for '{query}':\n"
        for meeting in results:
            result += f"\nMeeting ID: {meeting[0]}, Title: {meeting[1]}\n"
            # Show snippet of matching text
            transcript = meeting[2] or ""
            if query.lower() in transcript.lower():
                start = max(0, transcript.lower().find(query.lower()) - 50)
                end = min(len(transcript), start + 200)
                snippet = transcript[start:end]
                result += f"...{snippet}...\n"
        
        return [TextContent(type="text", text=result)]
    except Exception as e:
        return [TextContent(type="text", text=f"Error searching transcripts: {str(e)}")]

async def get_sentiment_analysis(meeting_id: int = None) -> List[TextContent]:
    """Get sentiment analysis results"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        if meeting_id:
            cursor.execute("""
                SELECT id, title, sentiment, sentiment_score 
                FROM meetings 
                WHERE id = ?
            """, (meeting_id,))
        else:
            cursor.execute("""
                SELECT id, title, sentiment, sentiment_score 
                FROM meetings 
                WHERE sentiment IS NOT NULL
                ORDER BY created_at DESC
            """)
        
        results = cursor.fetchall()
        conn.close()
        
        if not results:
            return [TextContent(type="text", text="No sentiment analysis data found")]
        
        result = "Sentiment Analysis Results:\n"
        for meeting in results:
            result += f"Meeting ID: {meeting[0]}, Title: {meeting[1]}, Sentiment: {meeting[2]}, Score: {meeting[3]}\n"
        
        return [TextContent(type="text", text=result)]
    except Exception as e:
        return [TextContent(type="text", text=f"Error fetching sentiment analysis: {str(e)}")]

async def export_meeting_data(meeting_id: int, format_type: str) -> List[TextContent]:
    """Export meeting data to file"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM meetings WHERE id = ?", (meeting_id,))
        meeting = cursor.fetchone()
        
        if not meeting:
            return [TextContent(type="text", text="Meeting not found")]
        
        # Get column names
        cursor.execute("PRAGMA table_info(meetings)")
        columns = [row[1] for row in cursor.fetchall()]
        
        # Create export directory
        export_dir = DATA_DIR / "mcp_exports"
        export_dir.mkdir(exist_ok=True)
        
        # Prepare data
        meeting_data = dict(zip(columns, meeting))
        
        if format_type == "json":
            export_file = export_dir / f"meeting_{meeting_id}.json"
            with open(export_file, 'w') as f:
                json.dump(meeting_data, f, indent=2, default=str)
        else:  # txt format
            export_file = export_dir / f"meeting_{meeting_id}.txt"
            with open(export_file, 'w') as f:
                for key, value in meeting_data.items():
                    f.write(f"{key}: {value}\n")
        
        conn.close()
        return [TextContent(type="text", text=f"Meeting data exported to: {export_file}")]
    except Exception as e:
        return [TextContent(type="text", text=f"Error exporting data: {str(e)}")]

async def get_container_status() -> List[TextContent]:
    """Get Docker container status"""
    try:
        import platform
        
        environment = "Docker Container" if os.path.exists("/app") else "Local Environment"
        status = f"SpeakInsights Environment Status:\n"
        status += f"Environment: {environment}\n"
        status += f"Platform: {platform.platform()}\n"
        status += f"Python Version: {platform.python_version()}\n"
        status += f"Database Path: {DB_PATH}\n"
        status += f"Database Exists: {os.path.exists(DB_PATH)}\n"
        status += f"Data Directory: {DATA_DIR}\n"
        status += f"Data Directory Exists: {DATA_DIR.exists()}\n"
        
        # Try to get additional info if in Docker
        if os.path.exists("/app"):
            try:
                import psutil
                status += f"CPU Usage: {psutil.cpu_percent()}%\n"
                status += f"Memory Usage: {psutil.virtual_memory().percent}%\n"
            except ImportError:
                status += "psutil not available for system metrics\n"
        
        return [TextContent(type="text", text=status)]
    except Exception as e:
        return [TextContent(type="text", text=f"Error getting container status: {str(e)}")]

async def main():
    """Main function to run MCP server"""
    environment = "Docker Container" if os.path.exists("/app") else "Local Environment"
    print(f"Starting SpeakInsights MCP Server in {environment}...")
    print(f"Database path: {DB_PATH}")
    print(f"Data directory: {DATA_DIR}")
    
    # Check if database exists, if not create it
    if not os.path.exists(DB_PATH):
        print("Database not found, creating new database...")
        try:
            import sqlite3
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS meetings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    date TEXT NOT NULL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    transcript TEXT,
                    summary TEXT,
                    sentiment TEXT,
                    sentiment_score REAL,
                    action_items TEXT,
                    audio_filename TEXT
                )
            ''')
            conn.commit()
            conn.close()
            print("Database created successfully")
        except Exception as e:
            print(f"Error creating database: {e}")
    
    try:
        async with stdio_server() as (read_stream, write_stream):
            await app.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="speakinsights-mcp",
                    server_version="1.0.0",
                    capabilities={
                        "tools": {},
                        "resources": {}
                    }
                )
            )
    except Exception as e:
        print(f"MCP Server error: {e}")
        raise

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
