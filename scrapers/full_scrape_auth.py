#!/usr/bin/env python3
"""
Full Authenticated Scrape - All 47 Leagues (956 Clubs)
Uses Carlos's Transfermarkt account: Eternitai
Time: ~2.5-3 hours with 8s delay between leagues
"""

import sys
import json
import time
from datetime import datetime

# Import the auth scraper
sys.path.append('/data/.openclaw/workspace-amaya/projects/football-data/scrapers')
from transfermarkt_auth import scrape_league_with_auth, TransfermarktAuthSession

# Load league configuration
with open('/data/.openclaw/workspace-amaya/projects/football-data/scrapers/leagues_full.json', 'r') as f:
    CONFIG = json.load(f)

def main():
    """Scrape all 47 leagues"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Full authenticated scrape')
    parser.add_argument('--delay', type=int, default=8,
                       help='Delay between leagues (seconds, default: 8)')
    parser.add_argument('--country', help='Filter by country')
    parser.add_argument('--tier', type=int, help='Filter by tier')
    
    args = parser.parse_args()
    
    leagues = CONFIG['leagues']
    
    # Apply filters
    if args.country:
        leagues = [l for l in leagues if args.country.lower() in l['country'].lower()]
    if args.tier:
        leagues = [l for l in leagues if l['tier'] == args.tier]
    
    total_clubs = sum(l['num_teams'] for l in leagues)
    
    print(f"""
╔════════════════════════════════════════════════════════════╗
║     FULL AUTHENTICATED SCRAPE - ALL CLUBS                  ║
║     Leagues: {len(leagues):3d} | Expected Clubs: {total_clubs:4d}                    ║
║     Delay: {args.delay}s between leagues                            ║
╚════════════════════════════════════════════════════════════╝

Started: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}
Estimated completion: ~{int(len(leagues) * args.delay / 60)} minutes
    """)
    
    results = {
        'started_at': datetime.utcnow().isoformat(),
        'total_leagues': len(leagues),
        'expected_clubs': total_clubs,
        'leagues': []
    }
    
    success_count = 0
    total_clubs_scraped = 0
    
    for i, league in enumerate(leagues, 1):
        print(f"\n{'─'*60}")
        print(f"Progress: {i}/{len(leagues)} leagues | {total_clubs_scraped} clubs scraped")
        print(f"{'─'*60}")
        
        try:
            filepath = scrape_league_with_auth(league)
            
            if filepath:
                # Read back the result to get club count
                with open(filepath, 'r') as f:
                    league_result = json.load(f)
                
                success_count += 1
                total_clubs_scraped += league_result.get('clubs_found', 0)
                
                results['leagues'].append({
                    'name': league['name'],
                    'country': league['country'],
                    'tier': league['tier'],
                    'clubs_found': league_result.get('clubs_found', 0),
                    'success': True,
                    'file': filepath
                })
            else:
                results['leagues'].append({
                    'name': league['name'],
                    'country': league['country'],
                    'tier': league['tier'],
                    'success': False,
                    'error': 'Scrape returned None'
                })
        
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            results['leagues'].append({
                'name': league['name'],
                'country': league['country'],
                'tier': league['tier'],
                'success': False,
                'error': str(e)
            })
        
        # Delay between leagues (respectful scraping)
        if i < len(leagues):
            print(f"\n⏳ Waiting {args.delay} seconds before next league...")
            time.sleep(args.delay)
    
    # Final summary
    results['completed_at'] = datetime.utcnow().isoformat()
    results['success_count'] = success_count
    results['total_clubs_scraped'] = total_clubs_scraped
    
    # Save summary
    summary_file = f'/data/.openclaw/workspace-amaya/projects/football-data/data/transfermarkt_auth/SUMMARY_{datetime.utcnow().strftime("%Y%m%d_%H%M%S")}.json'
    with open(summary_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"""
╔════════════════════════════════════════════════════════════╗
║                   SCRAPE COMPLETE                          ║
║                                                            ║
║  Leagues scraped: {success_count:3d}/{len(leagues):3d}                             ║
║  Clubs scraped: {total_clubs_scraped:4d}/{total_clubs:4d}                          ║
║  Success rate: {int(success_count/len(leagues)*100):3d}%                                  ║
║                                                            ║
║  Summary: {summary_file.split('/')[-1]}  ║
╚════════════════════════════════════════════════════════════╝

Completed: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}
    """)

if __name__ == '__main__':
    main()
