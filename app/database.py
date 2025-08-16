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
                summary TEXT,
                sentiment TEXT,
                sentiment_score REAL,
                action_items JSONB,
                audio_filename TEXT,
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
                summary TEXT,
                sentiment TEXT,
                sentiment_score REAL,
                action_items TEXT,
                audio_filename TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            ''')
        
        conn.commit()
        print(f"✅ Database initialized ({db_type})")
        
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        if conn:
            conn.rollback()
        raise
    finally:
        if conn:
            conn.close()

def save_meeting(meeting_data):
    """Save meeting to database with proper error handling"""
    conn = None
    try:
        conn, db_type = get_database_connection()
        cursor = conn.cursor()
        
        # Ensure action_items is properly serialized
        action_items = meeting_data.get('action_items', [])
        if isinstance(action_items, list):
            action_items_json = json.dumps(action_items)
        else:
            action_items_json = str(action_items)
        
        if db_type == 'postgresql':
            cursor.execute('''
            INSERT INTO meetings (title, date, transcript, summary, sentiment, action_items, audio_filename)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING id
            ''', (
                meeting_data['title'],
                meeting_data['date'],
                meeting_data['transcript'],
                meeting_data['summary'],
                meeting_data['sentiment'],
                action_items_json,
                meeting_data.get('audio_filename', '')
            ))
            meeting_id = cursor.fetchone()['id']
        else:
            cursor.execute('''
            INSERT INTO meetings (title, date, transcript, summary, sentiment, action_items, audio_filename)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                meeting_data['title'],
                meeting_data['date'],
                meeting_data['transcript'],
                meeting_data['summary'],
                meeting_data['sentiment'],
                action_items_json,
                meeting_data.get('audio_filename', '')
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
    conn = None
    try:
        conn, db_type = get_database_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT id, title, date, transcript, summary, sentiment, action_items, audio_filename, created_at
        FROM meetings
        ORDER BY created_at DESC
        ''')
        
        meetings = []
        for row in cursor.fetchall():
            meeting = dict(row)
            # Parse action_items JSON
            if meeting.get('action_items'):
                try:
                    if isinstance(meeting['action_items'], str):
                        meeting['action_items'] = json.loads(meeting['action_items'])
                except (json.JSONDecodeError, TypeError):
                    meeting['action_items'] = []
            else:
                meeting['action_items'] = []
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
    conn = None
    try:
        conn, db_type = get_database_connection()
        cursor = conn.cursor()
        
        query = 'SELECT * FROM meetings WHERE id = %s' if db_type == 'postgresql' else 'SELECT * FROM meetings WHERE id = ?'
        cursor.execute(query, (meeting_id,))
        
        meeting = cursor.fetchone()
        
        if meeting:
            meeting = dict(meeting)
            # Parse action_items JSON
            if meeting.get('action_items'):
                try:
                    if isinstance(meeting['action_items'], str):
                        meeting['action_items'] = json.loads(meeting['action_items'])
                except (json.JSONDecodeError, TypeError):
                    meeting['action_items'] = []
            else:
                meeting['action_items'] = []
            return meeting
        return None
        
    except Exception as e:
        print(f"Error fetching meeting {meeting_id}: {e}")
        return None
    finally:
        if conn:
            conn.close()

# Initialize database when module is imported
init_database()