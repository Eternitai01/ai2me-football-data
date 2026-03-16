#!/usr/bin/env python3
"""
Create SQLite database and import schema
"""

import sqlite3
import os

DB_PATH = '/data/.openclaw/workspace-amaya/projects/football-data/data/football_data.db'
SCHEMA_PATH = '/data/.openclaw/workspace-amaya/projects/football-data/database/schema.sql'

def create_database():
    """Create database and apply schema"""
    print(f"Creating database at: {DB_PATH}")
    
    # Read schema
    with open(SCHEMA_PATH, 'r') as f:
        schema = f.read()
    
    # Convert PostgreSQL schema to SQLite
    # SQLite doesn't support SERIAL, use INTEGER PRIMARY KEY AUTOINCREMENT
    schema = schema.replace('SERIAL PRIMARY KEY', 'INTEGER PRIMARY KEY AUTOINCREMENT')
    schema = schema.replace('TIMESTAMP DEFAULT NOW()', 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP')
    schema = schema.replace('NOW()', 'CURRENT_TIMESTAMP')
    schema = schema.replace('JSONB', 'TEXT')  # SQLite stores JSON as TEXT
    
    # Create database
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Execute schema (split by semicolon)
    statements = [s.strip() for s in schema.split(';') if s.strip()]
    
    for i, statement in enumerate(statements, 1):
        try:
            cursor.execute(statement)
            if 'CREATE TABLE' in statement.upper():
                table_name = statement.split('TABLE')[1].split('(')[0].strip().split()[0]
                print(f"  ✅ Created table: {table_name}")
            elif 'CREATE INDEX' in statement.upper():
                print(f"  ✅ Created index #{i}")
            elif 'CREATE VIEW' in statement.upper() or 'CREATE OR REPLACE VIEW' in statement.upper():
                view_name = statement.split('VIEW')[1].split('AS')[0].strip()
                print(f"  ✅ Created view: {view_name}")
        except Exception as e:
            if 'already exists' not in str(e).lower():
                print(f"  ⚠️  Skipped statement {i}: {str(e)[:100]}")
    
    conn.commit()
    conn.close()
    
    print(f"\n✅ Database created: {DB_PATH}")
    print(f"   Size: {os.path.getsize(DB_PATH) / 1024:.1f} KB")
    
    # Verify tables
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = cursor.fetchall()
    conn.close()
    
    print(f"\n📊 Tables created ({len(tables)}):")
    for table in tables:
        print(f"   - {table[0]}")

if __name__ == '__main__':
    create_database()
