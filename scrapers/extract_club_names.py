#!/usr/bin/env python3
"""
Extract club names from Transfermarkt URLs
Quick fix to populate empty names
"""

import json
import glob
import re

def extract_name_from_url(url):
    """Extract club name from Transfermarkt URL"""
    # URL format: https://www.transfermarkt.com/real-madrid/startseite/verein/418
    match = re.search(r'/([^/]+)/startseite/verein/', url)
    if match:
        slug = match.group(1)
        # Convert slug to readable name
        name = slug.replace('-', ' ').title()
        return name
    return ""

def fix_club_names(json_file):
    """Fix empty club names in JSON file"""
    print(f"📝 Processing: {json_file}")
    
    with open(json_file, 'r') as f:
        data = json.load(f)
    
    if 'clubs' in data:
        for club in data['clubs']:
            if not club['name'] and club['url']:
                club['name'] = extract_name_from_url(club['url'])
        
        # Save fixed version
        with open(json_file, 'w') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Fixed {len(data['clubs'])} clubs")
        for i, club in enumerate(data['clubs'][:5], 1):
            print(f"  {i}. {club['name']}")

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1:
        fix_club_names(sys.argv[1])
    else:
        # Fix all JSON files in transfermarkt_auth directory
        pattern = '/data/.openclaw/workspace-amaya/projects/football-data/data/transfermarkt_auth/*.json'
        files = glob.glob(pattern)
        
        if files:
            print(f"Found {len(files)} file(s) to fix\n")
            for file in files:
                fix_club_names(file)
                print()
        else:
            print("No files found")
