#!/usr/bin/env python3
"""
Fresh import - clear database and import all clubs
"""

import sqlite3
import json
import glob
import os
from datetime import datetime

DB_PATH = '/data/.openclaw/workspace-amaya/projects/football-data/data/football_data.db'
DATA_DIR = '/data/.openclaw/workspace-amaya/projects/football-data/data/transfermarkt_auth'

def fresh_import():
    """Clear database and import all clubs"""
    print("Connecting to database...")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Clear existing data
    print("Clearing existing data...")
    cursor.execute('DELETE FROM clubs')
    cursor.execute('DELETE FROM leagues')
    conn.commit()
    print("✅ Database cleared\n")
    
    # Get all JSON files
    json_files = [f for f in glob.glob(os.path.join(DATA_DIR, '*.json')) if 'SUMMARY' not in f]
    print(f"Found {len(json_files)} JSON files\n")
    
    total_clubs_imported = 0
    total_leagues_imported = 0
    
    for json_file in sorted(json_files):
        with open(json_file, 'r') as f:
            data = json.load(f)
        
        if not data.get('success') or not data.get('clubs'):
            continue
        
        league_name = data.get('league', 'Unknown')
        country = data.get('country', 'Unknown')
        tier = data.get('tier', 1)
        clubs = data.get('clubs', [])
        
        # Insert league
        cursor.execute('''
            INSERT INTO leagues (name, country, tier, last_updated)
            VALUES (?, ?, ?, ?)
        ''', (league_name, country, tier, datetime.now().isoformat()))
        
        league_id = cursor.lastrowid
        total_leagues_imported += 1
        
        # Insert clubs
        clubs_added = 0
        for club in clubs:
            club_name = club.get('name', '').strip()
            club_url = club.get('url', '')
            
            if not club_name or len(club_name) < 2:
                continue
            
            cursor.execute('''
                INSERT INTO clubs (name, league_id, country, official_website, last_updated)
                VALUES (?, ?, ?, ?, ?)
            ''', (club_name, league_id, country, club_url, datetime.now().isoformat()))
            
            clubs_added += 1
        
        total_clubs_imported += clubs_added
        print(f"✅ {league_name} ({country}): {clubs_added}/{len(clubs)} clubs")
    
    conn.commit()
    conn.close()
    
    print(f"\n{'='*60}")
    print(f"✅ IMPORT COMPLETE")
    print(f"{'='*60}")
    print(f"Leagues imported: {total_leagues_imported}")
    print(f"Clubs imported: {total_clubs_imported}")
    print(f"\nDatabase: {DB_PATH}")
    print(f"Size: {os.path.getsize(DB_PATH) / 1024 / 1024:.2f} MB")
    
    # Test queries
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print(f"\n{'='*60}")
    print("VERIFICATION")
    print(f"{'='*60}")
    
    # Sample clubs
    print("\n📊 Sample clubs from each country:")
    cursor.execute('''
        SELECT DISTINCT country FROM clubs ORDER BY country LIMIT 10
    ''')
    
    for (country,) in cursor.fetchall():
        cursor.execute('''
            SELECT name, (SELECT name FROM leagues WHERE id = clubs.league_id) as league
            FROM clubs
            WHERE country = ?
            LIMIT 2
        ''', (country,))
        
        clubs = cursor.fetchall()
        print(f"\n{country}:")
        for club, league in clubs:
            print(f"  - {club} ({league})")
    
    # Clubs by country
    print(f"\n{'='*60}")
    print("📈 Clubs by country:")
    cursor.execute('''
        SELECT country, COUNT(*) as count
        FROM clubs
        GROUP BY country
        ORDER BY count DESC
    ''')
    
    for country, count in cursor.fetchall():
        print(f"  {country}: {count} clubs")
    
    conn.close()

if __name__ == '__main__':
    fresh_import()
