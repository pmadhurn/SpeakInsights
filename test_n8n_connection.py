#!/usr/bin/env python3
"""Test script for n8n PostgreSQL connection"""

import psycopg2
import json

# Test PostgreSQL connection for n8n
connection_params = {
    'host': 'localhost',
    'port': 5432,
    'database': 'speakinsights',
    'user': 'speakinsights_user',
    'password': 'speakinsights_password'
}

print("🔗 Testing PostgreSQL connection for n8n integration...")
print(f"Connection parameters: {connection_params}")

try:
    # Connect to PostgreSQL
    conn = psycopg2.connect(**connection_params)
    cursor = conn.cursor()
    
    print("✅ Database connection successful!")
    
    # Test query
    cursor.execute("SELECT COUNT(*) FROM meetings")
    count = cursor.fetchone()[0]
    print(f"📊 Total meetings in database: {count}")
    
    # Get sample data
    cursor.execute("SELECT id, title, date FROM meetings ORDER BY id DESC LIMIT 3")
    meetings = cursor.fetchall()
    
    print("\n📋 Sample meetings:")
    for meeting in meetings:
        print(f"  ID: {meeting[0]}, Title: {meeting[1]}, Date: {meeting[2]}")
    
    # Test n8n-style query
    cursor.execute("""
        SELECT 
            id,
            title,
            date,
            sentiment,
            CASE 
                WHEN action_items IS NOT NULL 
                THEN jsonb_array_length(action_items) 
                ELSE 0 
            END as action_count
        FROM meetings 
        ORDER BY date DESC
    """)
    
    results = cursor.fetchall()
    print(f"\n🔄 n8n query test returned {len(results)} results")
    
    cursor.close()
    conn.close()
    
    print("\n✅ All tests passed! n8n can connect using these parameters:")
    print("Host: localhost")
    print("Port: 5432")
    print("Database: speakinsights")
    print("User: speakinsights_user")
    print("Password: speakinsights_password")
    
except Exception as e:
    print(f"❌ Connection failed: {e}")
    print("\nTroubleshooting:")
    print("1. Make sure Docker containers are running")
    print("2. Check if port 5432 is accessible")
    print("3. Verify PostgreSQL container is healthy")
