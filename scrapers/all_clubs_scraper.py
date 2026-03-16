#!/usr/bin/env python3
"""
All Clubs Scraper - Comprehensive Coverage
Scrapes ALL clubs from 43 leagues (1st & 2nd divisions)
Target: 792 clubs across 22 countries

Uses Transfermarkt as primary source for club lists
Then scrapes official club websites for detailed data
"""

import sys
import json
import os
import time
from datetime import datetime

# Add parent directory to path
sys.path.append('/data/.openclaw/workspace-amaya')
from advanced_scraper import scrape_url

# Load full league configuration
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(SCRIPT_DIR, 'leagues_full.json'), 'r') as f:
    CONFIG = json.load(f)

def scrape_league_clubs_list(league):
    """
    Scrape list of all clubs in a league from Transfermarkt
    Returns: List of club names and URLs
    """
    url = league['transfermarkt_url']
    
    print(f"\n{'='*60}")
    print(f"🏆 {league['name']} ({league['country']}) - Tier {league['tier']}")
    print(f"📊 Expected: {league['num_teams']} teams")
    print(f"🔗 {url}")
    print(f"{'='*60}")
    
    results = {
        'league': league['name'],
        'country': league['country'],
        'tier': league['tier'],
        'expected_teams': league['num_teams'],
        'url': url,
        'scraped_at': datetime.utcnow().isoformat(),
        'clubs': [],
        'success': False
    }
    
    try:
        # Scrape Transfermarkt league page
        data = scrape_url(url, wait_time=8)
        
        if data.get('success'):
            text = data.get('text', '')
            results['raw_text_length'] = len(text)
            
            # Extract club information from text
            # (In production, we'd parse HTML properly with BeautifulSoup)
            # For now, save raw data for manual processing
            results['raw_data'] = text[:10000]  # First 10k chars for preview
            results['full_text_path'] = save_raw_text(league, text)
            results['success'] = True
            
            print(f"✅ Scraped {len(text)} characters")
            print(f"💾 Full text saved for processing")
        else:
            print(f"❌ Failed to scrape")
            results['error'] = data.get('error', 'Unknown error')
    
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        results['error'] = str(e)
    
    return results

def save_raw_text(league, text):
    """Save raw scraped text for later processing"""
    timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
    output_dir = os.path.join(SCRIPT_DIR, '..', 'data', 'clubs_raw')
    os.makedirs(output_dir, exist_ok=True)
    
    safe_name = f"{league['country']}_{league['name']}".replace(' ', '_').replace('/', '-').lower()
    filename = f"{safe_name}_{timestamp}.txt"
    filepath = os.path.join(output_dir, filename)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(text)
    
    return filepath

def scrape_club_detail(club_name, club_url):
    """Scrape detailed data from a specific club's official website"""
    print(f"\n  ⚽ {club_name}")
    print(f"  🔗 {club_url}")
    
    try:
        data = scrape_url(club_url, wait_time=6)
        
        if data.get('success'):
            return {
                'name': club_name,
                'url': club_url,
                'text': data.get('text', '')[:5000],  # First 5k chars
                'success': True,
                'scraped_at': datetime.utcnow().isoformat()
            }
        else:
            return {
                'name': club_name,
                'url': club_url,
                'success': False,
                'error': data.get('error', 'Unknown error')
            }
    
    except Exception as e:
        return {
            'name': club_name,
            'url': club_url,
            'success': False,
            'error': str(e)
        }

def save_results(results, output_type='league_clubs'):
    """Save scraping results to JSON"""
    timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
    output_dir = os.path.join(SCRIPT_DIR, '..', 'data', output_type)
    os.makedirs(output_dir, exist_ok=True)
    
    safe_name = f"{results['country']}_{results['league']}".replace(' ', '_').replace('/', '-').lower()
    filename = f"{safe_name}_{timestamp}.json"
    filepath = os.path.join(output_dir, filename)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Saved: {filepath}")
    return filepath

def main():
    """Main orchestration - scrape all 792 clubs"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Scrape all clubs from 43 leagues')
    parser.add_argument('--country', help='Filter by country (e.g., Spain, England)')
    parser.add_argument('--tier', type=int, choices=[1, 2], help='Filter by tier (1 or 2)')
    parser.add_argument('--limit', type=int, help='Limit number of leagues to scrape')
    parser.add_argument('--delay', type=int, default=8,
                       help='Delay between league scrapes (seconds, default: 8)')
    parser.add_argument('--test', action='store_true',
                       help='Test mode: scrape first 3 leagues only')
    
    args = parser.parse_args()
    
    print(f"""
╔════════════════════════════════════════════════════════════╗
║       All Clubs Scraper - Comprehensive Coverage           ║
║       Target: 792 clubs from 43 leagues                    ║
║       Countries: 22 | Divisions: 1st & 2nd                 ║
╚════════════════════════════════════════════════════════════╝
    """)
    
    # Filter leagues
    leagues = CONFIG['leagues']
    
    if args.country:
        leagues = [l for l in leagues if args.country.lower() in l['country'].lower()]
        print(f"🔍 Filtered to country: {args.country} ({len(leagues)} leagues)")
    
    if args.tier:
        leagues = [l for l in leagues if l['tier'] == args.tier]
        print(f"🔍 Filtered to tier {args.tier}: ({len(leagues)} leagues)")
    
    if args.test:
        leagues = leagues[:3]
        print(f"🧪 TEST MODE: First 3 leagues only")
    
    if args.limit:
        leagues = leagues[:args.limit]
        print(f"🔍 Limited to {args.limit} leagues")
    
    print(f"\n📋 Scraping {len(leagues)} league(s)...")
    
    total_expected_clubs = sum(l['num_teams'] for l in leagues)
    print(f"🎯 Expected total clubs: {total_expected_clubs}")
    
    scraped_count = 0
    success_count = 0
    
    for i, league in enumerate(leagues, 1):
        print(f"\n{'─'*60}")
        print(f"Progress: {i}/{len(leagues)} leagues")
        print(f"{'─'*60}")
        
        try:
            results = scrape_league_clubs_list(league)
            save_results(results, output_type='league_clubs')
            
            scraped_count += 1
            if results.get('success'):
                success_count += 1
            
            # Delay between scrapes (respectful scraping)
            if i < len(leagues):
                print(f"\n⏳ Waiting {args.delay} seconds before next league...")
                time.sleep(args.delay)
        
        except Exception as e:
            print(f"\n❌ Error scraping {league['name']}: {str(e)}")
            continue
    
    # Summary
    print(f"""
╔════════════════════════════════════════════════════════════╗
║                   Scraping Complete                        ║
║                                                            ║
║  Leagues attempted: {scraped_count:3d}/{len(leagues):3d}                           ║
║  Successful scrapes: {success_count:3d}                                ║
║  Target clubs: {total_expected_clubs:3d}                                   ║
║                                                            ║
║  Data saved to: data/league_clubs/                         ║
║  Raw text saved to: data/clubs_raw/                        ║
╚════════════════════════════════════════════════════════════╝

📊 Next Step: Build parser to extract club names/URLs from raw data

⚠️  Note: This scraper fetches league pages with club lists.
    To scrape individual club websites, we need to:
    1. Parse the raw data to extract club names & URLs
    2. Run a second pass to scrape each club's official site
    3. This will take ~90-120 minutes for all 792 clubs (8s delay)
    """)

if __name__ == '__main__':
    main()
