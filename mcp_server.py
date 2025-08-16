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

# Import config
try:
    from config import config
    DB_PATH = config.SQLITE_PATH
    DATA_DIR = Path("data")
except ImportError:
    # Fallback if config is not available
    if os.path.exists("/app"):
        DB_PATH = "/app/database/speakinsights.db"
        DATA_DIR = Path("/app/data")
    else:
        DB_PATH = "speakinsights.db"
        DATA_DIR = Path("data")

# Initialize MCP Server
app = Server("speakinsights-mcp")

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
            description="Search through meeting transcripts with context",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query"},
                    "limit": {"type": "integer", "description": "Limit number of results", "default": 5},
                    "context_chars": {"type": "integer", "description": "Characters of context around matches", "default": 300}
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="get_full_transcript",
            description="Get the complete transcript for a specific meeting",
            inputSchema={
                "type": "object",
                "properties": {
                    "meeting_id": {"type": "integer", "description": "Meeting ID"},
                    "chunk_size": {"type": "integer", "description": "Split transcript into chunks of this size", "default": 2000}
                },
                "required": ["meeting_id"]
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
        context_chars = arguments.get("context_chars", 300)
        return await search_transcripts(query, limit, context_chars)
    
    elif name == "get_full_transcript":
        meeting_id = arguments.get("meeting_id")
        chunk_size = arguments.get("chunk_size", 2000)
        return await get_full_transcript(meeting_id, chunk_size)
    
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
        result = f"Meeting Details (ID: {meeting_id}) [{environment}]:\n\n"
        
        # Format the output better, handling long transcripts
        for i, value in enumerate(meeting):
            column_name = columns[i]
            if column_name == 'transcript' and value:
                # Truncate very long transcripts for readability
                transcript = str(value)
                if len(transcript) > 2000:
                    result += f"{column_name}: {transcript[:1000]}...\n[TRANSCRIPT TRUNCATED - {len(transcript)} total characters]\n..{transcript[-500:]}\n\n"
                else:
                    result += f"{column_name}: {transcript}\n\n"
            elif column_name == 'action_items' and value:
                # Format action items nicely
                try:
                    import json
                    items = json.loads(value) if isinstance(value, str) else value
                    if isinstance(items, list):
                        result += f"{column_name}:\n"
                        for idx, item in enumerate(items, 1):
                            result += f"  {idx}. {item}\n"
                        result += "\n"
                    else:
                        result += f"{column_name}: {value}\n\n"
                except:
                    result += f"{column_name}: {value}\n\n"
            else:
                result += f"{column_name}: {value}\n\n"
        
        conn.close()
        return [TextContent(type="text", text=result)]
    except Exception as e:
        return [TextContent(type="text", text=f"Error fetching meeting details: {str(e)}")]

async def search_transcripts(query: str, limit: int, context_chars: int = 300) -> List[TextContent]:
    """Search through transcripts with better context"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, title, transcript, created_at
            FROM meetings 
            WHERE transcript LIKE ? 
            ORDER BY created_at DESC
            LIMIT ?
        """, (f"%{query}%", limit))
        
        results = cursor.fetchall()
        conn.close()
        
        if not results:
            return [TextContent(type="text", text=f"No transcripts found matching '{query}'")]
        
        result = f"Search Results for '{query}' ({len(results)} matches):\n\n"
        
        for meeting in results:
            meeting_id, title, transcript, created_at = meeting
            result += f"📋 Meeting ID: {meeting_id}\n"
            result += f"📝 Title: {title}\n"
            result += f"📅 Date: {created_at}\n\n"
            
            # Find all occurrences of the query
            transcript = transcript or ""
            query_lower = query.lower()
            transcript_lower = transcript.lower()
            
            matches = []
            start = 0
            while True:
                pos = transcript_lower.find(query_lower, start)
                if pos == -1:
                    break
                matches.append(pos)
                start = pos + 1
            
            if matches:
                result += f"🔍 Found {len(matches)} occurrence(s):\n"
                for i, pos in enumerate(matches[:3]):  # Show max 3 matches per meeting
                    context_start = max(0, pos - context_chars // 2)
                    context_end = min(len(transcript), pos + len(query) + context_chars // 2)
                    
                    context = transcript[context_start:context_end]
                    
                    # Highlight the match (simple text highlighting)
                    highlighted = context.replace(
                        transcript[pos:pos + len(query)], 
                        f"**{transcript[pos:pos + len(query)]}**"
                    )
                    
                    result += f"  Match {i+1}: ...{highlighted}...\n\n"
                
                if len(matches) > 3:
                    result += f"  ... and {len(matches) - 3} more matches\n\n"
            
            result += "─" * 50 + "\n\n"
        
        return [TextContent(type="text", text=result)]
    except Exception as e:
        return [TextContent(type="text", text=f"Error searching transcripts: {str(e)}")]

async def get_full_transcript(meeting_id: int, chunk_size: int = 2000) -> List[TextContent]:
    """Get complete transcript for a meeting, optionally chunked"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT title, transcript, created_at, audio_filename
            FROM meetings 
            WHERE id = ?
        """, (meeting_id,))
        
        result = cursor.fetchone()
        conn.close()
        
        if not result:
            return [TextContent(type="text", text=f"Meeting {meeting_id} not found")]
        
        title, transcript, created_at, audio_filename = result
        
        if not transcript:
            return [TextContent(type="text", text=f"No transcript available for meeting {meeting_id}")]
        
        # Prepare header
        header = f"📋 Full Transcript - Meeting ID: {meeting_id}\n"
        header += f"📝 Title: {title}\n"
        header += f"📅 Date: {created_at}\n"
        header += f"🎵 Audio File: {audio_filename or 'N/A'}\n"
        header += f"📊 Length: {len(transcript)} characters\n"
        header += "=" * 60 + "\n\n"
        
        # If transcript is small enough, return as single chunk
        if len(transcript) <= chunk_size:
            full_content = header + transcript
            return [TextContent(type="text", text=full_content)]
        
        # Split into chunks
        chunks = []
        total_chunks = (len(transcript) + chunk_size - 1) // chunk_size
        
        for i in range(0, len(transcript), chunk_size):
            chunk_num = (i // chunk_size) + 1
            chunk_text = transcript[i:i + chunk_size]
            
            chunk_header = f"📋 Transcript Chunk {chunk_num}/{total_chunks} - Meeting ID: {meeting_id}\n"
            chunk_header += f"📝 Title: {title}\n"
            chunk_header += f"Characters: {i+1}-{min(i+len(chunk_text), len(transcript))} of {len(transcript)}\n"
            chunk_header += "-" * 40 + "\n\n"
            
            chunks.append(TextContent(type="text", text=chunk_header + chunk_text))
        
        return chunks
        
    except Exception as e:
        return [TextContent(type="text", text=f"Error fetching transcript: {str(e)}")]

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
