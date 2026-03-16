#!/usr/bin/env python3
"""
League & Club Official Data Scraper
Scrapes regulations, salary caps, squad lists from official league/club websites
Uses advanced_scraper.py as base for JavaScript-heavy sites
"""

import sys
import json
import os
import time
from datetime import datetime

# Add parent directory to path to import advanced_scraper
sys.path.append('/data/.openclaw/workspace-amaya')
from advanced_scraper import scrape_url

# Load league URLs configuration
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(SCRIPT_DIR, 'league_urls.json'), 'r') as f:
    CONFIG = json.load(f)

def scrape_league_regulations(league):
    """Scrape regulations and salary cap info from league official site"""
    print(f"\n{'='*60}")
    print(f"🏆 Scraping: {league['name']} ({league['country']})")
    print(f"{'='*60}")
    
    results = {
        'league': league['name'],
        'country': league['country'],
        'confederation': league['confederation'],
        'scraped_at': datetime.utcnow().isoformat(),
        'data': {}
    }
    
    # Scrape main website
    if league.get('official_website'):
        print(f"\n📄 Main website: {league['official_website']}")
        main_data = scrape_url(league['official_website'], wait_time=5)
        if main_data.get('success'):
            results['data']['main_page'] = {
                'url': league['official_website'],
                'text_length': len(main_data.get('text', '')),
                'extracted_at': main_data.get('timestamp')
            }
    
    # Scrape regulations page
    if league.get('regulations_url'):
        print(f"\n📋 Regulations: {league['regulations_url']}")
        reg_data = scrape_url(league['regulations_url'], wait_time=8)
        if reg_data.get('success'):
            results['data']['regulations'] = {
                'url': league['regulations_url'],
                'text': reg_data.get('text', ''),
                'extracted_at': reg_data.get('timestamp')
            }
    
    # Scrape salary cap info
    if league.get('salary_cap_url'):
        print(f"\n💰 Salary Cap: {league['salary_cap_url']}")
        cap_data = scrape_url(league['salary_cap_url'], wait_time=8)
        if cap_data.get('success'):
            results['data']['salary_cap'] = {
                'url': league['salary_cap_url'],
                'text': cap_data.get('text', ''),
                'extracted_at': cap_data.get('timestamp')
            }
    
    # Scrape squad cost control (Premier League specific)
    if league.get('squad_cost_control_url'):
        print(f"\n📊 Squad Cost Control: {league['squad_cost_control_url']}")
        scc_data = scrape_url(league['squad_cost_control_url'], wait_time=8)
        if scc_data.get('success'):
            results['data']['squad_cost_control'] = {
                'url': league['squad_cost_control_url'],
                'text': scc_data.get('text', ''),
                'extracted_at': scc_data.get('timestamp')
            }
    
    return results

def scrape_club_data(club):
    """Scrape squad list and news from club official site"""
    print(f"\n{'='*60}")
    print(f"⚽ Scraping: {club['name']} ({club['league']})")
    print(f"{'='*60}")
    
    results = {
        'club': club['name'],
        'league': club['league'],
        'scraped_at': datetime.utcnow().isoformat(),
        'data': {}
    }
    
    # Scrape squad page
    if club.get('squad_url'):
        print(f"\n👥 Squad: {club['squad_url']}")
        squad_data = scrape_url(club['squad_url'], wait_time=8)
        if squad_data.get('success'):
            results['data']['squad'] = {
                'url': club['squad_url'],
                'text': squad_data.get('text', ''),
                'extracted_at': squad_data.get('timestamp')
            }
    
    # Scrape news page (for contract announcements)
    if club.get('news_url'):
        print(f"\n📰 News: {club['news_url']}")
        news_data = scrape_url(club['news_url'], wait_time=5)
        if news_data.get('success'):
            results['data']['news'] = {
                'url': club['news_url'],
                'text': news_data.get('text', ''),
                'extracted_at': news_data.get('timestamp')
            }
    
    return results

def save_results(results, output_type='league'):
    """Save scraping results to JSON file"""
    timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
    output_dir = os.path.join(SCRIPT_DIR, '..', 'data', output_type)
    os.makedirs(output_dir, exist_ok=True)
    
    # Create filename from league/club name
    name = results.get('league') or results.get('club')
    safe_name = name.replace(' ', '_').replace('/', '-').lower()
    filename = f"{safe_name}_{timestamp}.json"
    filepath = os.path.join(output_dir, filename)
    
    with open(filepath, 'w') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Results saved: {filepath}")
    return filepath

def main():
    """Main scraper orchestration"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Scrape league/club official data')
    parser.add_argument('--type', choices=['leagues', 'clubs', 'all'], default='all',
                       help='What to scrape')
    parser.add_argument('--priority', choices=['high', 'medium', 'low', 'all'], default='high',
                       help='Data priority filter (for leagues)')
    parser.add_argument('--limit', type=int, help='Limit number of sources to scrape')
    parser.add_argument('--delay', type=int, default=5,
                       help='Delay between scrapes (seconds)')
    
    args = parser.parse_args()
    
    print(f"""
╔════════════════════════════════════════════════════════════╗
║         Football Data Scraper - Official Sources          ║
╚════════════════════════════════════════════════════════════╝
    """)
    
    scraped_count = 0
    
    # Scrape leagues
    if args.type in ['leagues', 'all']:
        leagues_to_scrape = CONFIG['leagues']
        
        # Filter by priority
        if args.priority != 'all':
            leagues_to_scrape = [l for l in leagues_to_scrape 
                                if l.get('data_priority') == args.priority]
        
        # Apply limit
        if args.limit:
            leagues_to_scrape = leagues_to_scrape[:args.limit]
        
        print(f"\n🏆 Scraping {len(leagues_to_scrape)} league(s)...")
        
        for league in leagues_to_scrape:
            try:
                results = scrape_league_regulations(league)
                save_results(results, output_type='league')
                scraped_count += 1
                
                # Delay between scrapes (respectful scraping)
                if scraped_count < len(leagues_to_scrape):
                    print(f"\n⏳ Waiting {args.delay} seconds before next scrape...")
                    time.sleep(args.delay)
                    
            except Exception as e:
                print(f"\n❌ Error scraping {league['name']}: {str(e)}")
                continue
    
    # Scrape clubs
    if args.type in ['clubs', 'all']:
        clubs_to_scrape = CONFIG['top_clubs']
        
        # Apply limit
        if args.limit:
            clubs_to_scrape = clubs_to_scrape[:args.limit]
        
        print(f"\n⚽ Scraping {len(clubs_to_scrape)} club(s)...")
        
        for club in clubs_to_scrape:
            try:
                results = scrape_club_data(club)
                save_results(results, output_type='club')
                scraped_count += 1
                
                # Delay between scrapes
                if scraped_count < len(clubs_to_scrape) + len(leagues_to_scrape if args.type == 'all' else []):
                    print(f"\n⏳ Waiting {args.delay} seconds before next scrape...")
                    time.sleep(args.delay)
                    
            except Exception as e:
                print(f"\n❌ Error scraping {club['name']}: {str(e)}")
                continue
    
    print(f"""
╔════════════════════════════════════════════════════════════╗
║                   Scraping Complete                        ║
║  Total sources scraped: {scraped_count:3d}                             ║
╚════════════════════════════════════════════════════════════╝
    """)

if __name__ == '__main__':
    main()
