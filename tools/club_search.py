#!/usr/bin/env python3
"""
Club Search Tool - For all agents (Enzo, Tania, Bernie)
Search and filter clubs by various criteria
"""

import sqlite3
import sys

DB_PATH = '/data/.openclaw/workspace-amaya/projects/football-data/data/football_data.db'

def search_clubs(country=None, league=None, name=None, tier=None):
    """
    Search clubs with filters
    
    Args:
        country: Country name (e.g., 'Spain', 'England')
        league: League name (e.g., 'La Liga', 'Premier League')
        name: Club name (partial match)
        tier: League tier (1, 2, 3, 4)
    
    Returns:
        List of (club_name, league_name, country, tier, website)
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    query = '''
        SELECT 
            c.name as club_name,
            l.name as league_name,
            c.country,
            l.tier,
            c.official_website
        FROM clubs c
        LEFT JOIN leagues l ON c.league_id = l.id
        WHERE 1=1
    '''
    params = []
    
    if country:
        query += ' AND c.country LIKE ?'
        params.append(f'%{country}%')
    
    if league:
        query += ' AND l.name LIKE ?'
        params.append(f'%{league}%')
    
    if name:
        query += ' AND c.name LIKE ?'
        params.append(f'%{name}%')
    
    if tier:
        query += ' AND l.tier = ?'
        params.append(tier)
    
    query += ' ORDER BY c.name'
    
    cursor.execute(query, params)
    results = cursor.fetchall()
    conn.close()
    
    return results

def list_countries():
    """Get all countries with club count"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT country, COUNT(*) as count
        FROM clubs
        GROUP BY country
        ORDER BY count DESC
    ''')
    
    results = cursor.fetchall()
    conn.close()
    return results

def list_leagues(country=None):
    """Get all leagues, optionally filtered by country"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    if country:
        cursor.execute('''
            SELECT name, country, tier,
                   (SELECT COUNT(*) FROM clubs WHERE league_id = leagues.id) as club_count
            FROM leagues
            WHERE country LIKE ?
            ORDER BY tier, name
        ''', (f'%{country}%',))
    else:
        cursor.execute('''
            SELECT name, country, tier,
                   (SELECT COUNT(*) FROM clubs WHERE league_id = leagues.id) as club_count
            FROM leagues
            ORDER BY country, tier, name
        ''')
    
    results = cursor.fetchall()
    conn.close()
    return results

def get_club_details(club_name):
    """Get detailed info for a specific club"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT 
            c.name,
            l.name as league,
            c.country,
            l.tier,
            c.official_website,
            c.salary_cap,
            c.total_budget
        FROM clubs c
        LEFT JOIN leagues l ON c.league_id = l.id
        WHERE c.name LIKE ?
    ''', (f'%{club_name}%',))
    
    results = cursor.fetchall()
    conn.close()
    return results

def main():
    """CLI interface"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Search football clubs')
    parser.add_argument('--country', help='Country name')
    parser.add_argument('--league', help='League name')
    parser.add_argument('--name', help='Club name (partial match)')
    parser.add_argument('--tier', type=int, help='League tier (1, 2, 3, 4)')
    parser.add_argument('--list-countries', action='store_true', help='List all countries')
    parser.add_argument('--list-leagues', action='store_true', help='List all leagues')
    parser.add_argument('--details', help='Get details for a specific club')
    
    args = parser.parse_args()
    
    if args.list_countries:
        print("\n📊 Countries with clubs:\n")
        for country, count in list_countries():
            print(f"  {country}: {count} clubs")
        return
    
    if args.list_leagues:
        print("\n🏆 Leagues:\n")
        current_country = None
        for name, country, tier, club_count in list_leagues(args.country):
            if country != current_country:
                print(f"\n{country}:")
                current_country = country
            print(f"  Tier {tier}: {name} ({club_count} clubs)")
        return
    
    if args.details:
        print(f"\n🔍 Club details for '{args.details}':\n")
        results = get_club_details(args.details)
        if results:
            for name, league, country, tier, website, salary_cap, budget in results:
                print(f"Name: {name}")
                print(f"League: {league} (Tier {tier})")
                print(f"Country: {country}")
                print(f"Website: {website}")
                if salary_cap:
                    print(f"Salary Cap: €{salary_cap:,.0f}")
                if budget:
                    print(f"Budget: €{budget:,.0f}")
                print()
        else:
            print("No clubs found")
        return
    
    # Search clubs
    print(f"\n🔍 Searching clubs...\n")
    results = search_clubs(
        country=args.country,
        league=args.league,
        name=args.name,
        tier=args.tier
    )
    
    if results:
        print(f"Found {len(results)} clubs:\n")
        for club_name, league_name, country, tier, website in results:
            print(f"⚽ {club_name}")
            print(f"   League: {league_name} (Tier {tier})")
            print(f"   Country: {country}")
            print(f"   Website: {website}")
            print()
    else:
        print("No clubs found matching criteria")

if __name__ == '__main__':
    main()
