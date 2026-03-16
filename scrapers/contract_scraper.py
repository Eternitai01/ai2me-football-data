#!/usr/bin/env python3
"""
Contract & Salary Data Scraper
Scrapes player contract data from Capology, Spotrac, and other public sources
Goal: Build 5,000+ contract comparables database
"""

import sys
import json
import os
import time
from datetime import datetime

# Add parent directory to path
sys.path.append('/data/.openclaw/workspace-amaya')
from advanced_scraper import scrape_url

# Contract data sources
CONTRACT_SOURCES = {
    'capology': {
        'name': 'Capology',
        'base_url': 'https://www.capology.com',
        'leagues': [
            {'name': 'Premier League', 'url': '/uk/premier-league/salaries'},
            {'name': 'La Liga', 'url': '/es/la-liga/salaries'},
            {'name': 'Serie A', 'url': '/it/serie-a/salaries'},
            {'name': 'Bundesliga', 'url': '/de/bundesliga/salaries'},
            {'name': 'Ligue 1', 'url': '/fr/ligue-1/salaries'},
            {'name': 'MLS', 'url': '/us/mls/salaries'},
            {'name': 'Saudi Pro League', 'url': '/sa/saudi-pro-league/salaries'},
        ],
        'priority': 'high'
    },
    'spotrac': {
        'name': 'Spotrac',
        'base_url': 'https://www.spotrac.com',
        'leagues': [
            {'name': 'Premier League', 'url': '/epl/rankings'},
            {'name': 'MLS', 'url': '/mls/rankings'},
        ],
        'priority': 'medium'
    }
}

def scrape_league_salaries(source_key, league_info, delay=5):
    """Scrape salary data for a league from a specific source"""
    source = CONTRACT_SOURCES[source_key]
    url = source['base_url'] + league_info['url']
    
    print(f"\n{'='*60}")
    print(f"💰 {source['name']}: {league_info['name']}")
    print(f"🔗 {url}")
    print(f"{'='*60}")
    
    results = {
        'source': source['name'],
        'league': league_info['name'],
        'url': url,
        'scraped_at': datetime.utcnow().isoformat(),
        'data': None,
        'success': False
    }
    
    try:
        # Scrape with extended wait for dynamic content
        data = scrape_url(url, wait_time=10)
        
        if data.get('success'):
            results['data'] = {
                'text': data.get('text', ''),
                'text_length': len(data.get('text', '')),
                'extracted_at': data.get('timestamp')
            }
            results['success'] = True
            
            # Preview first 500 chars
            preview = data.get('text', '')[:500]
            print(f"\n✅ Success! Extracted {len(data.get('text', ''))} characters")
            print(f"\n📋 Preview:\n{preview}...")
        else:
            print(f"\n❌ Failed to scrape")
            results['error'] = data.get('error', 'Unknown error')
    
    except Exception as e:
        print(f"\n❌ Exception: {str(e)}")
        results['error'] = str(e)
    
    # Respectful delay
    time.sleep(delay)
    
    return results

def scrape_club_payroll(club_name, source='capology', delay=5):
    """Scrape detailed payroll for a specific club"""
    # Club URLs follow pattern: /club/{slug}/salaries
    club_slug = club_name.lower().replace(' ', '-')
    
    if source == 'capology':
        url = f"https://www.capology.com/club/{club_slug}/salaries"
    else:
        print(f"❌ Source {source} not yet supported for club payroll")
        return None
    
    print(f"\n{'='*60}")
    print(f"⚽ Club Payroll: {club_name}")
    print(f"🔗 {url}")
    print(f"{'='*60}")
    
    results = {
        'source': source,
        'club': club_name,
        'url': url,
        'scraped_at': datetime.utcnow().isoformat(),
        'data': None,
        'success': False
    }
    
    try:
        data = scrape_url(url, wait_time=10)
        
        if data.get('success'):
            results['data'] = {
                'text': data.get('text', ''),
                'text_length': len(data.get('text', '')),
                'extracted_at': data.get('timestamp')
            }
            results['success'] = True
            print(f"\n✅ Success! Extracted {len(data.get('text', ''))} characters")
        else:
            print(f"\n❌ Failed to scrape")
            results['error'] = data.get('error', 'Unknown error')
    
    except Exception as e:
        print(f"\n❌ Exception: {str(e)}")
        results['error'] = str(e)
    
    time.sleep(delay)
    return results

def save_results(results, output_type='salary'):
    """Save scraping results to JSON"""
    timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
    output_dir = os.path.join(os.path.dirname(__file__), '..', 'data', output_type)
    os.makedirs(output_dir, exist_ok=True)
    
    # Create filename
    league_or_club = results.get('league') or results.get('club')
    source = results.get('source', 'unknown')
    safe_name = f"{source}_{league_or_club}".replace(' ', '_').replace('/', '-').lower()
    filename = f"{safe_name}_{timestamp}.json"
    filepath = os.path.join(output_dir, filename)
    
    with open(filepath, 'w') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Saved: {filepath}")
    return filepath

def main():
    """Main contract scraper orchestration"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Scrape contract & salary data')
    parser.add_argument('--source', choices=['capology', 'spotrac', 'all'], default='all',
                       help='Data source to scrape')
    parser.add_argument('--type', choices=['league', 'club'], default='league',
                       help='Scrape league salaries or specific club payroll')
    parser.add_argument('--club', help='Club name for club payroll scraping')
    parser.add_argument('--limit', type=int, help='Limit number of leagues to scrape')
    parser.add_argument('--delay', type=int, default=5,
                       help='Delay between scrapes (seconds)')
    
    args = parser.parse_args()
    
    print(f"""
╔════════════════════════════════════════════════════════════╗
║       Contract & Salary Data Scraper                       ║
║       Target: 5,000+ contract comparables                  ║
╚════════════════════════════════════════════════════════════╝
    """)
    
    scraped_count = 0
    
    if args.type == 'club':
        if not args.club:
            print("❌ Error: --club required for club payroll scraping")
            sys.exit(1)
        
        results = scrape_club_payroll(args.club, source=args.source, delay=args.delay)
        if results and results.get('success'):
            save_results(results, output_type='club_salary')
            scraped_count = 1
    
    else:  # league salaries
        sources_to_scrape = []
        
        if args.source == 'all':
            sources_to_scrape = CONTRACT_SOURCES.keys()
        else:
            sources_to_scrape = [args.source]
        
        for source_key in sources_to_scrape:
            source = CONTRACT_SOURCES[source_key]
            leagues = source['leagues']
            
            # Apply limit
            if args.limit:
                leagues = leagues[:args.limit]
            
            print(f"\n🏆 Scraping {len(leagues)} league(s) from {source['name']}...")
            
            for league in leagues:
                try:
                    results = scrape_league_salaries(source_key, league, delay=args.delay)
                    if results.get('success'):
                        save_results(results, output_type='league_salary')
                        scraped_count += 1
                
                except Exception as e:
                    print(f"\n❌ Error: {str(e)}")
                    continue
    
    print(f"""
╔════════════════════════════════════════════════════════════╗
║                   Scraping Complete                        ║
║  Successful scrapes: {scraped_count:3d}                             ║
╚════════════════════════════════════════════════════════════╝
    """)

if __name__ == '__main__':
    main()
