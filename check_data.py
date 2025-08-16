import sqlite3
import os

# Check database file
db_path = 'speakinsights.db'
print(f"Database exists: {os.path.exists(db_path)}")
print(f"Database size: {os.path.getsize(db_path) if os.path.exists(db_path) else 0} bytes")

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    print(f"Tables: {tables}")
    
    if tables:
        # Check meetings table structure
        cursor.execute("PRAGMA table_info(meetings)")
        schema = cursor.fetchall()
        print(f"Meetings table schema: {schema}")
        
        # Check if there are any meetings
        cursor.execute("SELECT COUNT(*) FROM meetings")
        count = cursor.fetchone()[0]
        print(f"Number of meetings: {count}")
        
        if count > 0:
            # Show sample data
            cursor.execute("SELECT id, title, date, audio_filename FROM meetings LIMIT 5")
            sample_meetings = cursor.fetchall()
            print("Sample meetings:")
            for meeting in sample_meetings:
                print(f"  ID: {meeting[0]}, Title: {meeting[1]}, Date: {meeting[2]}, Audio: {meeting[3]}")
    
    conn.close()
    print("Database check completed successfully!")
    
except Exception as e:
    print(f"Database error: {e}")

# Check for audio files or uploads directories
print("\nChecking for data directories...")
data_dirs = ['data', 'uploads', 'audio', 'recordings', 'media']
for dir_name in data_dirs:
    if os.path.exists(dir_name):
        print(f"{dir_name} directory exists")
        files = os.listdir(dir_name)
        print(f"  Contains {len(files)} files: {files[:5]}")  # Show first 5 files
    else:
        print(f"{dir_name} directory not found")
