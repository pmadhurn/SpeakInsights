import sqlite3
import os

DB_PATH = "/app/speakinsights.db"
print(f"Database exists: {os.path.exists(DB_PATH)}")

try:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Check tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    print(f"Tables: {tables}")
    
    # Check meetings table structure if it exists
    if tables:
        cursor.execute("PRAGMA table_info(meetings)")
        schema = cursor.fetchall()
        print(f"Meetings table schema: {schema}")
        
        # Check if there are any meetings
        cursor.execute("SELECT COUNT(*) FROM meetings")
        count = cursor.fetchone()[0]
        print(f"Number of meetings: {count}")
    
    conn.close()
    print("Database test completed successfully!")
    
except Exception as e:
    print(f"Database error: {e}")
