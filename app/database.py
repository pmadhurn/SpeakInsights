import sqlite3
import json
import os
from datetime import datetime
try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    HAS_POSTGRES = True
except ImportError:
    HAS_POSTGRES = False

def get_database_connection():
    """Get database connection - PostgreSQL if available, SQLite as fallback"""
    from config import config
    
    database_url = config.DATABASE_URL
    
    if database_url and HAS_POSTGRES and not database_url.startswith('sqlite'):
        try:
            conn = psycopg2.connect(database_url, cursor_factory=RealDictCursor)
            # Test the connection
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            cursor.fetchone()
            return conn, 'postgresql'
        except Exception as e:
            print(f"PostgreSQL connection failed: {e}, falling back to SQLite")
    
    # SQLite fallback
    sqlite_path = config.SQLITE_PATH
    try:
        # Ensure directory exists
        import os
        os.makedirs(os.path.dirname(sqlite_path) if os.path.dirname(sqlite_path) else '.', exist_ok=True)
        
        conn = sqlite3.connect(sqlite_path, timeout=30.0)
        conn.row_factory = sqlite3.Row
        # Enable WAL mode for better concurrency
        conn.execute("PRAGMA journal_mode=WAL")
        return conn, 'sqlite'
    except Exception as e:
        print(f"SQLite connection failed: {e}")
        raise

def init_database():
    """Initialize database - PostgreSQL or SQLite"""
    conn = None
    try:
        conn, db_type = get_database_connection()
        cursor = conn.cursor()
        
        if db_type == 'postgresql':
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS meetings (
                id SERIAL PRIMARY KEY,
                title TEXT NOT NULL,
                date TIMESTAMP NOT NULL,
                transcript TEXT,
                formatted_transcript TEXT,
                summary TEXT,
                sentiment TEXT,
                sentiment_score REAL,
                action_items JSONB,
                audio_filename TEXT,
                transcription_metadata JSONB,
                speaker_segments JSONB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            ''')
        else:
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS meetings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                date TIMESTAMP NOT NULL,
                transcript TEXT,
                formatted_transcript TEXT,
                summary TEXT,
                sentiment TEXT,
                sentiment_score REAL,
                action_items TEXT,
                audio_filename TEXT,
                transcription_metadata TEXT,
                speaker_segments TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            ''')
        
        conn.commit()
        print(f"[OK] Database initialized ({db_type})")
        
    except Exception as e:
        print(f"[ERROR] Database initialization failed: {e}")
        if conn:
            conn.rollback()
        raise
    finally:
        if conn:
            conn.close()

def ensure_database_initialized():
    """Ensure database is initialized before use"""
    try:
        conn, db_type = get_database_connection()
        cursor = conn.cursor()
        
        # Check if meetings table exists
        if db_type == 'postgresql':
            cursor.execute("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'meetings')")
        else:
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='meetings'")
        
        result = cursor.fetchone()
        conn.close()
        
        if not result or (db_type == 'sqlite' and not result[0]):
            print("[INFO] Initializing database tables...")
            init_database()
    except Exception as e:
        print(f"[WARNING] Database check failed, initializing: {e}")
        init_database()

def save_meeting(meeting_data):
    """Save meeting to database with proper error handling"""
    ensure_database_initialized()
    conn = None
    try:
        conn, db_type = get_database_connection()
        cursor = conn.cursor()
        
        # Serialize JSON fields
        action_items = meeting_data.get('action_items', [])
        action_items_json = json.dumps(action_items) if isinstance(action_items, list) else str(action_items)
        
        transcription_metadata = meeting_data.get('transcription_metadata', {})
        metadata_json = json.dumps(transcription_metadata) if isinstance(transcription_metadata, dict) else str(transcription_metadata)
        
        speaker_segments = meeting_data.get('speaker_segments', [])
        segments_json = json.dumps(speaker_segments) if isinstance(speaker_segments, list) else str(speaker_segments)
        
        if db_type == 'postgresql':
            cursor.execute('''
            INSERT INTO meetings (title, date, transcript, formatted_transcript, summary, sentiment, 
                                action_items, audio_filename, transcription_metadata, speaker_segments)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
            ''', (
                meeting_data['title'],
                meeting_data['date'],
                meeting_data['transcript'],
                meeting_data.get('formatted_transcript', meeting_data['transcript']),
                meeting_data['summary'],
                meeting_data['sentiment'],
                action_items_json,
                meeting_data.get('audio_filename', ''),
                metadata_json,
                segments_json
            ))
            meeting_id = cursor.fetchone()['id']
        else:
            cursor.execute('''
            INSERT INTO meetings (title, date, transcript, formatted_transcript, summary, sentiment, 
                                action_items, audio_filename, transcription_metadata, speaker_segments)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                meeting_data['title'],
                meeting_data['date'],
                meeting_data['transcript'],
                meeting_data.get('formatted_transcript', meeting_data['transcript']),
                meeting_data['summary'],
                meeting_data['sentiment'],
                action_items_json,
                meeting_data.get('audio_filename', ''),
                metadata_json,
                segments_json
            ))
            meeting_id = cursor.lastrowid
        
        conn.commit()
        return meeting_id
        
    except Exception as e:
        if conn:
            conn.rollback()
        print(f"Error saving meeting: {e}")
        raise
    finally:
        if conn:
            conn.close()

def get_all_meetings():
    """Retrieve all meetings from database"""
    ensure_database_initialized()
    conn = None
    try:
        conn, db_type = get_database_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT id, title, date, transcript, formatted_transcript, summary, sentiment, action_items, 
               audio_filename, transcription_metadata, speaker_segments, created_at
        FROM meetings
        ORDER BY created_at DESC
        ''')
        
        meetings = []
        for row in cursor.fetchall():
            meeting = dict(row)
            
            # Parse JSON fields
            if meeting.get('action_items'):
                try:
                    if isinstance(meeting['action_items'], str):
                        meeting['action_items'] = json.loads(meeting['action_items'])
                except (json.JSONDecodeError, TypeError):
                    meeting['action_items'] = []
            else:
                meeting['action_items'] = []
            
            if meeting.get('transcription_metadata'):
                try:
                    if isinstance(meeting['transcription_metadata'], str):
                        meeting['transcription_metadata'] = json.loads(meeting['transcription_metadata'])
                except (json.JSONDecodeError, TypeError):
                    meeting['transcription_metadata'] = {}
            else:
                meeting['transcription_metadata'] = {}
            
            if meeting.get('speaker_segments'):
                try:
                    if isinstance(meeting['speaker_segments'], str):
                        meeting['speaker_segments'] = json.loads(meeting['speaker_segments'])
                except (json.JSONDecodeError, TypeError):
                    meeting['speaker_segments'] = []
            else:
                meeting['speaker_segments'] = []
            
            meetings.append(meeting)
        
        return meetings
        
    except Exception as e:
        print(f"Error fetching meetings: {e}")
        return []
    finally:
        if conn:
            conn.close()

def get_meeting_by_id(meeting_id):
    """Get specific meeting by ID"""
    ensure_database_initialized()
    conn = None
    try:
        conn, db_type = get_database_connection()
        cursor = conn.cursor()
        
        query = 'SELECT * FROM meetings WHERE id = %s' if db_type == 'postgresql' else 'SELECT * FROM meetings WHERE id = ?'
        cursor.execute(query, (meeting_id,))
        
        meeting = cursor.fetchone()
        
        if meeting:
            meeting = dict(meeting)
            
            # Parse JSON fields
            if meeting.get('action_items'):
                try:
                    if isinstance(meeting['action_items'], str):
                        meeting['action_items'] = json.loads(meeting['action_items'])
                except (json.JSONDecodeError, TypeError):
                    meeting['action_items'] = []
            else:
                meeting['action_items'] = []
            
            if meeting.get('transcription_metadata'):
                try:
                    if isinstance(meeting['transcription_metadata'], str):
                        meeting['transcription_metadata'] = json.loads(meeting['transcription_metadata'])
                except (json.JSONDecodeError, TypeError):
                    meeting['transcription_metadata'] = {}
            else:
                meeting['transcription_metadata'] = {}
            
            if meeting.get('speaker_segments'):
                try:
                    if isinstance(meeting['speaker_segments'], str):
                        meeting['speaker_segments'] = json.loads(meeting['speaker_segments'])
                except (json.JSONDecodeError, TypeError):
                    meeting['speaker_segments'] = []
            else:
                meeting['speaker_segments'] = []
            
            return meeting
        return None
        
    except Exception as e:
        print(f"Error fetching meeting {meeting_id}: {e}")
        return None
    finally:
        if conn:
            conn.close()

def update_meeting_summary(meeting_id, new_summary):
    """Update the summary for an existing meeting"""
    ensure_database_initialized()
    conn = None
    try:
        conn, db_type = get_database_connection()
        cursor = conn.cursor()
        
        query = 'UPDATE meetings SET summary = %s WHERE id = %s' if db_type == 'postgresql' else 'UPDATE meetings SET summary = ? WHERE id = ?'
        cursor.execute(query, (new_summary, meeting_id))
        
        if cursor.rowcount == 0:
            raise Exception(f"Meeting with ID {meeting_id} not found")
        
        conn.commit()
        print(f"[OK] Updated summary for meeting {meeting_id}")
        
    except Exception as e:
        if conn:
            conn.rollback()
        print(f"Error updating meeting summary: {e}")
        raise
    finally:
        if conn:
            conn.close()

def update_meeting_action_items(meeting_id, new_action_items):
    """Update the action items for an existing meeting"""
    ensure_database_initialized()
    conn = None
    try:
        conn, db_type = get_database_connection()
        cursor = conn.cursor()
        
        # Serialize action items
        action_items_json = json.dumps(new_action_items) if isinstance(new_action_items, list) else str(new_action_items)
        
        query = 'UPDATE meetings SET action_items = %s WHERE id = %s' if db_type == 'postgresql' else 'UPDATE meetings SET action_items = ? WHERE id = ?'
        cursor.execute(query, (action_items_json, meeting_id))
        
        if cursor.rowcount == 0:
            raise Exception(f"Meeting with ID {meeting_id} not found")
        
        conn.commit()
        print(f"[OK] Updated action items for meeting {meeting_id}")
        
    except Exception as e:
        if conn:
            conn.rollback()
        print(f"Error updating meeting action items: {e}")
        raise
    finally:
        if conn:
            conn.close()

# Initialize database when module is imported - with error handling
try:
    init_database()
except Exception as e:
    print(f"[WARNING] Database initialization deferred: {e}")
    # Database will be initialized on first use