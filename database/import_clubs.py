#!/usr/bin/env python3
"""
Import scraped clubs from JSON files to SQLite database
"""

import sqlite3
import json
import glob
import os
from datetime import datetime

DB_PATH = '/data/.openclaw/workspace-amaya/projects/football-data/data/football_data.db'
DATA_DIR = '/data/.openclaw/workspace-amaya/projects/football-data/data/transfermarkt_auth'

def import_clubs():
    """Import all clubs from JSON files"""
    print(f"Connecting to database: {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Get all JSON files
    json_files = glob.glob(os.path.join(DATA_DIR, '*.json'))
    print(f"Found {len(json_files)} JSON files\n")
    
    total_clubs = 0
    total_leagues = 0
    
    for json_file in json_files:
        if 'SUMMARY' in json_file:
            continue  # Skip summary files
        
        with open(json_file, 'r') as f:
            data = json.load(f)
        
        if not data.get('success') or not data.get('clubs'):
            continue
        
        league_name = data.get('league', 'Unknown')
        country = data.get('country', 'Unknown')
        tier = data.get('tier', 1)
        clubs = data.get('clubs', [])
        
        print(f"📂 {league_name} ({country}) - {len(clubs)} clubs")
        
        # Insert or update league
        cursor.execute('''
            INSERT OR IGNORE INTO leagues (name, country, tier, last_updated)
            VALUES (?, ?, ?, ?)
        ''', (league_name, country, tier, datetime.now().isoformat()))
        
        league_id = cursor.lastrowid
        if league_id == 0:  # League already exists
            cursor.execute('SELECT id FROM leagues WHERE name = ? AND country = ?', 
                          (league_name, country))
            result = cursor.fetchone()
            if result:
                league_id = result[0]
        
        total_leagues += 1
        
        # Insert clubs
        clubs_added = 0
        for club in clubs:
            club_name = club.get('name', '').strip()
            club_url = club.get('url', '')
            
            if not club_name or len(club_name) < 2:
                continue
            
            try:
                cursor.execute('''
                    INSERT INTO clubs (name, league_id, country, official_website, last_updated)
                    VALUES (?, ?, ?, ?, ?)
                ''', (club_name, league_id, country, club_url, datetime.now().isoformat()))
                clubs_added += 1
                total_clubs += 1
            except sqlite3.IntegrityError:
                # Duplicate, skip
                pass
        
        print(f"   ✅ Imported {clubs_added} clubs")
    
    conn.commit()
    
    # Get actual counts from database
    cursor.execute('SELECT COUNT(*) FROM leagues')
    db_leagues = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM clubs')
    db_clubs = cursor.fetchone()[0]
    
    conn.close()
    
    print(f"\n{'='*60}")
    print(f"✅ IMPORT COMPLETE")
    print(f"{'='*60}")
    print(f"Leagues in database: {db_leagues}")
    print(f"Clubs in database: {db_clubs}")
    print(f"\nDatabase: {DB_PATH}")
    print(f"Size: {os.path.getsize(DB_PATH) / 1024 / 1024:.2f} MB")

def test_query():
    """Test some queries"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print(f"\n{'='*60}")
    print("TEST QUERIES")
    print(f"{'='*60}")
    
    # Top 10 clubs
    print("\n📊 Sample clubs:")
    cursor.execute('''
        SELECT c.name, l.name as league, c.country
        FROM clubs c
        LEFT JOIN leagues l ON c.league_id = l.id
        ORDER BY c.name
        LIMIT 10
    ''')
    
    for row in cursor.fetchall():
        print(f"  - {row[0]} ({row[1]}, {row[2]})")
    
    # Clubs by country
    print("\n🌍 Clubs by country:")
    cursor.execute('''
        SELECT country, COUNT(*) as count
        FROM clubs
        GROUP BY country
        ORDER BY count DESC
        LIMIT 10
    ''')
    
    for row in cursor.fetchall():
        print(f"  - {row[0]}: {row[1]} clubs")
    
    conn.close()

if __name__ == '__main__':
    import_clubs()
    test_query()
