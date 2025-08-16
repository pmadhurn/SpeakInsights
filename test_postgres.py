#!/usr/bin/env python3
"""Test script to verify PostgreSQL data persistence"""

from app.database import save_meeting, get_all_meetings, get_database_connection
from datetime import datetime

def test_database():
    # Test database connection
    conn, db_type = get_database_connection()
    print(f"Using database: {db_type}")
    conn.close()
    
    # Create test meeting data
    test_meeting = {
        'title': 'PostgreSQL Test Meeting',
        'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'transcript': 'This is a test transcript to verify PostgreSQL persistence.',
        'summary': 'Test meeting for database verification',
        'sentiment': 'Positive (100%)',
        'action_items': ['Test PostgreSQL', 'Verify persistence', 'Check n8n connectivity'],
        'audio_filename': 'test.mp3'
    }
    
    # Save meeting
    meeting_id = save_meeting(test_meeting)
    print(f"Saved meeting with ID: {meeting_id}")
    
    # Retrieve all meetings
    meetings = get_all_meetings()
    print(f"Found {len(meetings)} meetings in database")
    
    for meeting in meetings:
        print(f"Meeting: {meeting['title']} (ID: {meeting['id']})")
    
    return meetings

if __name__ == "__main__":
    test_database()
