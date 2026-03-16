#!/usr/bin/env python3
"""
Import additional club data from Wikipedia scrapes
Clean and import the 4,063 entries scraped from alternative sources
"""

import sqlite3
import json
import glob
import os
import re
from datetime import datetime

DB_PATH = '/data/.openclaw/workspace-amaya/projects/football-data/data/football_data.db'
WIKI_DATA_DIR = '/data/.openclaw/workspace-amaya/projects/football-data/data/alternative_sources'

def is_valid_club_name(name):
    """Filter out non-club entries"""
    if not name or len(name) < 3:
        return False
    
    # Skip years, references, stadium names
    skip_patterns = [
        r'^\d{4}',  # Years (1986, 2025)
        r'^\[\d+\]',  # References ([7], [n1 1])
        r'stadium$',  # Stadium names
        r'^\d{4}[-–]\d{2,4}$',  # Year ranges (1986-87)
        r'^(edit|citation|season)',  # Wikipedia artifacts
    ]
    
    for pattern in skip_patterns:
        if re.search(pattern, name, re.IGNORECASE):
            return False
    
    return True

def import_wikipedia_clubs():
    """Import clubs from Wikipedia JSON files"""
    print("Connecting to database...")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    json_files = glob.glob(os.path.join(WIKI_DATA_DIR, '*.json'))
    print(f"Found {len(json_files)} Wikipedia files\n")
    
    total_raw = 0
    total_valid = 0
    total_imported = 0
    
    for json_file in sorted(json_files):
        with open(json_file, 'r') as f:
            data = json.load(f)
        
        if not data.get('success') or not data.get('clubs'):
            continue
        
        league_name = data.get('league', 'Unknown')
        country = data.get('country', 'Unknown')
        tier = data.get('tier', 1)
        clubs = data.get('clubs', [])
        
        total_raw += len(clubs)
        
        # Filter valid clubs
        valid_clubs = []
        for club in clubs:
            name = club.get('name', '').strip()
            if is_valid_club_name(name):
                valid_clubs.append(club)
        
        total_valid += len(valid_clubs)
        
        if not valid_clubs:
            continue
        
        print(f"📂 {league_name} ({country}): {len(valid_clubs)}/{len(clubs)} valid clubs")
        
        # Get or create league
        cursor.execute('SELECT id FROM leagues WHERE name = ? AND country = ?', 
                      (league_name, country))
        result = cursor.fetchone()
        
        if result:
            league_id = result[0]
        else:
            cursor.execute('''
                INSERT INTO leagues (name, country, tier, last_updated)
                VALUES (?, ?, ?, ?)
            ''', (league_name, country, tier, datetime.now().isoformat()))
            league_id = cursor.lastrowid
        
        # Import clubs
        imported = 0
        for club in valid_clubs:
            name = club.get('name', '').strip()
            url = club.get('url', '')
            
            # Check if club already exists
            cursor.execute('SELECT id FROM clubs WHERE name = ? AND league_id = ?',
                          (name, league_id))
            
            if not cursor.fetchone():
                try:
                    cursor.execute('''
                        INSERT INTO clubs (name, league_id, country, official_website, last_updated, data_source)
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', (name, league_id, country, url, datetime.now().isoformat(), 'wikipedia'))
                    imported += 1
                except:
                    pass  # Skip duplicates
        
        total_imported += imported
        print(f"   ✅ Imported {imported} new clubs\n")
    
    conn.commit()
    
    # Get final counts
    cursor.execute('SELECT COUNT(*) FROM clubs')
    total_clubs = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM leagues')
    total_leagues = cursor.fetchone()[0]
    
    conn.close()
    
    print(f"{'='*60}")
    print(f"✅ WIKIPEDIA IMPORT COMPLETE")
    print(f"{'='*60}")
    print(f"Raw entries: {total_raw}")
    print(f"Valid clubs: {total_valid}")
    print(f"New imports: {total_imported}")
    print(f"\nDatabase totals:")
    print(f"  Leagues: {total_leagues}")
    print(f"  Clubs: {total_clubs}")

if __name__ == '__main__':
    import_wikipedia_clubs()
