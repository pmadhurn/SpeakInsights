#!/usr/bin/env python3
"""
Data Migration Script for SpeakInsights
Migrates existing SQLite data to PostgreSQL and creates backups
"""

import os
import shutil
import sqlite3
import psycopg2
import json
from datetime import datetime
from pathlib import Path

def backup_existing_data():
    """Create backups of existing data before migration"""
    print("📁 Creating backups of existing data...")
    
    # Create timestamped backup directory
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = Path(f"backups/backup_{timestamp}")
    backup_dir.mkdir(parents=True, exist_ok=True)
    
    # Backup SQLite database
    if os.path.exists("speakinsights.db"):
        shutil.copy2("speakinsights.db", backup_dir / "speakinsights.db")
        print(f"✅ SQLite database backed up to {backup_dir}")
    
    # Backup data directory
    if os.path.exists("data"):
        shutil.copytree("data", backup_dir / "data", dirs_exist_ok=True)
        print(f"✅ Data directory backed up to {backup_dir}")
    
    # Copy to persistent_data directory
    if os.path.exists("data"):
        shutil.copytree("data", "persistent_data/data", dirs_exist_ok=True)
        print("✅ Data copied to persistent_data directory")
    
    if os.path.exists("speakinsights.db"):
        shutil.copy2("speakinsights.db", "persistent_data/speakinsights.db")
        print("✅ SQLite database copied to persistent_data directory")
    
    return backup_dir

def get_sqlite_schema(db_path):
    """Extract schema from SQLite database"""
    if not os.path.exists(db_path):
        print("❌ SQLite database not found")
        return []
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get all table schemas
    cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
    schemas = cursor.fetchall()
    
    conn.close()
    return [schema[0] for schema in schemas if schema[0]]

def migrate_sqlite_to_postgres():
    """Migrate data from SQLite to PostgreSQL"""
    sqlite_path = "speakinsights.db"
    
    if not os.path.exists(sqlite_path):
        print("❌ No SQLite database found to migrate")
        return
    
    try:
        # Connect to databases
        sqlite_conn = sqlite3.connect(sqlite_path)
        postgres_conn = psycopg2.connect(
            host="localhost",
            port=5432,
            database="speakinsights",
            user="speakinsights_user",
            password="speakinsights_password"
        )
        
        sqlite_cursor = sqlite_conn.cursor()
        postgres_cursor = postgres_conn.cursor()
        
        # Get list of tables
        sqlite_cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
        tables = [row[0] for row in sqlite_cursor.fetchall()]
        
        print(f"📊 Found {len(tables)} tables to migrate: {tables}")
        
        for table in tables:
            print(f"🔄 Migrating table: {table}")
            
            # Get table schema
            sqlite_cursor.execute(f"PRAGMA table_info({table})")
            columns_info = sqlite_cursor.fetchall()
            
            # Create PostgreSQL table (simplified - you may need to adjust data types)
            columns = []
            for col in columns_info:
                col_name = col[1]
                col_type = col[2].upper()
                
                # Map SQLite types to PostgreSQL types
                if col_type in ['INTEGER', 'INT']:
                    pg_type = 'INTEGER'
                elif col_type in ['TEXT', 'VARCHAR']:
                    pg_type = 'TEXT'
                elif col_type in ['REAL', 'FLOAT']:
                    pg_type = 'REAL'
                elif col_type in ['BLOB']:
                    pg_type = 'BYTEA'
                else:
                    pg_type = 'TEXT'  # Default fallback
                
                columns.append(f"{col_name} {pg_type}")
            
            create_table_sql = f"CREATE TABLE IF NOT EXISTS {table} ({', '.join(columns)})"
            postgres_cursor.execute(create_table_sql)
            
            # Copy data
            sqlite_cursor.execute(f"SELECT * FROM {table}")
            rows = sqlite_cursor.fetchall()
            
            if rows:
                placeholders = ', '.join(['%s'] * len(rows[0]))
                insert_sql = f"INSERT INTO {table} VALUES ({placeholders})"
                postgres_cursor.executemany(insert_sql, rows)
                print(f"✅ Migrated {len(rows)} rows from {table}")
        
        postgres_conn.commit()
        print("✅ Migration completed successfully!")
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        print("💡 You can still use SQLite - it will be stored in persistent volumes")
    finally:
        if 'sqlite_conn' in locals():
            sqlite_conn.close()
        if 'postgres_conn' in locals():
            postgres_conn.close()

def create_database_init_script():
    """Create initialization script for PostgreSQL"""
    init_script = """
-- SpeakInsights Database Initialization
-- This script will be run when PostgreSQL starts for the first time

-- Create extensions if needed
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Add any initial table creation or data here
-- Example:
-- CREATE TABLE IF NOT EXISTS users (
--     id SERIAL PRIMARY KEY,
--     username VARCHAR(255) UNIQUE NOT NULL,
--     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
-- );

-- You can add your specific table schemas here
"""
    
    with open("backups/init.sql", "w") as f:
        f.write(init_script)
    
    print("✅ Created database initialization script at backups/init.sql")

def main():
    print("🚀 Starting SpeakInsights Data Migration")
    print("=" * 50)
    
    # Step 1: Backup existing data
    backup_dir = backup_existing_data()
    
    # Step 2: Create database init script
    create_database_init_script()
    
    print("\n🏁 Migration preparation complete!")
    print("\n📋 Next Steps:")
    print("1. Run: docker-compose up -d postgres")
    print("2. Wait for PostgreSQL to be ready")
    print("3. Run this script again with --migrate flag to transfer data")
    print("4. Run: docker-compose up --build")
    
    print(f"\n💾 Your data is safely backed up in: {backup_dir}")
    print("💡 Even if migration fails, your SQLite data will be preserved in Docker volumes")

if __name__ == "__main__":
    import sys
    if "--migrate" in sys.argv:
        migrate_sqlite_to_postgres()
    else:
        main()
