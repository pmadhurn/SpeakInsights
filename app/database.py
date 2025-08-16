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
    database_url = os.environ.get('DATABASE_URL')
    
    if database_url and HAS_POSTGRES:
        try:
            conn = psycopg2.connect(database_url, cursor_factory=RealDictCursor)
            return conn, 'postgresql'
        except Exception as e:
            print(f"PostgreSQL connection failed: {e}, falling back to SQLite")
    
    # SQLite fallback
    sqlite_path = os.environ.get('SQLITE_PATH', 'speakinsights.db')
    conn = sqlite3.connect(sqlite_path)
    conn.row_factory = sqlite3.Row
    return conn, 'sqlite'

def init_database():
    """Initialize database - PostgreSQL or SQLite"""
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
            action_items TEXT,
            audio_filename TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
    
    conn.commit()
    conn.close()

def save_meeting(meeting_data):
    """Save meeting to database"""
    conn, db_type = get_database_connection()
    cursor = conn.cursor()
    
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
            json.dumps(meeting_data['action_items']),
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
            json.dumps(meeting_data['action_items']),
            meeting_data.get('audio_filename', '')
        ))
        meeting_id = cursor.lastrowid
    
    conn.commit()
    conn.close()
    
    return meeting_id

def get_all_meetings():
    """Retrieve all meetings from database"""
    conn, db_type = get_database_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
    SELECT id, title, date, transcript, summary, sentiment, action_items, audio_filename
    FROM meetings
    ORDER BY date DESC
    ''')
    
    meetings = []
    for row in cursor.fetchall():
        meeting = dict(row)
        if db_type == 'sqlite' and isinstance(meeting.get('action_items'), str):
            meeting['action_items'] = json.loads(meeting['action_items'])
        meetings.append(meeting)
    
    conn.close()
    return meetings

def get_meeting_by_id(meeting_id):
    """Get specific meeting by ID"""
    conn, db_type = get_database_connection()
    cursor = conn.cursor()
    
    query = 'SELECT * FROM meetings WHERE id = %s' if db_type == 'postgresql' else 'SELECT * FROM meetings WHERE id = ?'
    cursor.execute(query, (meeting_id,))
    
    meeting = cursor.fetchone()
    conn.close()
    
    if meeting:
        meeting = dict(meeting)
        if db_type == 'sqlite' and isinstance(meeting.get('action_items'), str):
            meeting['action_items'] = json.loads(meeting['action_items'])
        return meeting
    return None

# Initialize database when module is imported
init_database()