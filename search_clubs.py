#!/usr/bin/env python3
"""
Enzo's Club Search Tool
Quick access to club database for scouting
"""

import sys
sys.path.append('/data/.openclaw/workspace-amaya/projects/football-data/tools')
from club_search import search_clubs, list_leagues, get_club_details

# Example: Search for Spanish clubs
print("🔍 Enzo's Club Search\n")

# Quick searches for Enzo
print("Top 5 Spanish Tier 1 clubs:")
results = search_clubs(country='Spain', tier=1)
for i, (name, league, country, tier, website) in enumerate(results[:5], 1):
    print(f"  {i}. {name} ({league})")

print("\nUsage:")
print("  python3 search_clubs.py --country Spain --tier 1")
print("  python3 search_clubs.py --name Barcelona")
print("  python3 search_clubs.py --list-countries")
