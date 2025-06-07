import sqlite3
import json
from datetime import datetime

def init_database():
    """Initialize SQLite database"""
    conn = sqlite3.connect('speakinsights.db')
    cursor = conn.cursor()
    
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
    conn = sqlite3.connect('speakinsights.db')
    cursor = conn.cursor()
    
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
    conn = sqlite3.connect('speakinsights.db')
    cursor = conn.cursor()
    
    cursor.execute('''
    SELECT id, title, date, transcript, summary, sentiment, action_items, audio_filename
    FROM meetings
    ORDER BY date DESC
    ''')
    
    meetings = []
    for row in cursor.fetchall():
        meeting = {
            'id': row[0],
            'title': row[1],
            'date': row[2],
            'transcript': row[3],
            'summary': row[4],
            'sentiment': row[5],
            'action_items': json.loads(row[6]) if row[6] else [],
            'audio_filename': row[7]
        }
        meetings.append(meeting)
    
    conn.close()
    return meetings

def get_meeting_by_id(meeting_id):
    """Get specific meeting by ID"""
    conn = sqlite3.connect('speakinsights.db')
    cursor = conn.cursor()
    
    cursor.execute('''
    SELECT id, title, date, transcript, summary, sentiment, action_items, audio_filename
    FROM meetings
    WHERE id = ?
    ''', (meeting_id,))
    
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return {
            'id': row[0],
            'title': row[1],
            'date': row[2],
            'transcript': row[3],
            'summary': row[4],
            'sentiment': row[5],
            'action_items': json.loads(row[6]) if row[6] else [],
            'audio_filename': row[7]
        }
    return None

# Initialize database when module is imported
init_database()