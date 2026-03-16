#!/usr/bin/env python3
"""
Alternative Sources Scraper
For leagues that failed on Transfermarkt, scrape from:
- Official league websites
- Wikipedia club lists
- Other reliable sources
"""

import requests
import json
import time
import os
import re
from datetime import datetime
from bs4 import BeautifulSoup

# Alternative sources for failed leagues
ALTERNATIVE_SOURCES = {
    'segunda_federacion_spain': {
        'name': 'Segunda Federación',
        'country': 'Spain',
        'tier': 4,
        'sources': [
            {
                'type': 'wikipedia',
                'url': 'https://en.wikipedia.org/wiki/Segunda_Federaci%C3%B3n',
                'extract_pattern': r'verein|team|club'
            },
            {
                'type': 'official',
                'url': 'https://www.rfef.es/en/competitions/segunda-division-rfef',
                'extract_pattern': r'club|team'
            }
        ]
    },
    'china_league_one': {
        'name': 'China League One',
        'country': 'China',
        'tier': 2,
        'sources': [
            {
                'type': 'wikipedia',
                'url': 'https://en.wikipedia.org/wiki/China_League_One',
                'extract_pattern': r'club|team'
            }
        ]
    },
    'saudi_first_division': {
        'name': 'Saudi First Division',
        'country': 'Saudi Arabia',
        'tier': 2,
        'sources': [
            {
                'type': 'wikipedia',
                'url': 'https://en.wikipedia.org/wiki/Saudi_First_Division_League',
                'extract_pattern': r'club|team'
            }
        ]
    },
    'liga_betplay_colombia': {
        'name': 'Liga BetPlay',
        'country': 'Colombia',
        'tier': 1,
        'sources': [
            {
                'type': 'wikipedia',
                'url': 'https://en.wikipedia.org/wiki/Categor%C3%ADa_Primera_A',
                'extract_pattern': r'club|team'
            },
            {
                'type': 'official',
                'url': 'https://www.dimayor.com.co/',
                'extract_pattern': r'club|equipo'
            }
        ]
    },
    'torneo_betplay_colombia': {
        'name': 'Torneo BetPlay',
        'country': 'Colombia',
        'tier': 2,
        'sources': [
            {
                'type': 'wikipedia',
                'url': 'https://en.wikipedia.org/wiki/Categor%C3%ADa_Primera_B',
                'extract_pattern': r'club|team'
            }
        ]
    },
    'primera_nacional_argentina': {
        'name': 'Primera Nacional',
        'country': 'Argentina',
        'tier': 2,
        'sources': [
            {
                'type': 'wikipedia',
                'url': 'https://en.wikipedia.org/wiki/Primera_Nacional',
                'extract_pattern': r'club|team'
            }
        ]
    },
    'liga_expansion_mexico': {
        'name': 'Liga de Expansión MX',
        'country': 'Mexico',
        'tier': 2,
        'sources': [
            {
                'type': 'wikipedia',
                'url': 'https://en.wikipedia.org/wiki/Liga_de_Expansi%C3%B3n_MX',
                'extract_pattern': r'club|team'
            }
        ]
    },
    'ligapro_ecuador': {
        'name': 'LigaPro',
        'country': 'Ecuador',
        'tier': 1,
        'sources': [
            {
                'type': 'wikipedia',
                'url': 'https://en.wikipedia.org/wiki/Ecuadorian_Serie_A',
                'extract_pattern': r'club|team'
            },
            {
                'type': 'official',
                'url': 'https://www.ligapro.ec/',
                'extract_pattern': r'club|equipo'
            }
        ]
    },
    'division_profesional_bolivia': {
        'name': 'División Profesional',
        'country': 'Bolivia',
        'tier': 1,
        'sources': [
            {
                'type': 'wikipedia',
                'url': 'https://en.wikipedia.org/wiki/Bolivian_Primera_Divisi%C3%B3n',
                'extract_pattern': r'club|team'
            }
        ]
    },
    'liga1_peru': {
        'name': 'Liga 1',
        'country': 'Peru',
        'tier': 1,
        'sources': [
            {
                'type': 'wikipedia',
                'url': 'https://en.wikipedia.org/wiki/Peruvian_Primera_Divisi%C3%B3n',
                'extract_pattern': r'club|team'
            }
        ]
    },
    'primera_division_venezuela': {
        'name': 'Primera División',
        'country': 'Venezuela',
        'tier': 1,
        'sources': [
            {
                'type': 'wikipedia',
                'url': 'https://en.wikipedia.org/wiki/Venezuelan_Primera_Divisi%C3%B3n',
                'extract_pattern': r'club|team'
            }
        ]
    },
    'segunda_division_venezuela': {
        'name': 'Segunda División',
        'country': 'Venezuela',
        'tier': 2,
        'sources': [
            {
                'type': 'wikipedia',
                'url': 'https://en.wikipedia.org/wiki/Segunda_Divisi%C3%B3n_de_Venezuela',
                'extract_pattern': r'club|team'
            }
        ]
    }
}

class AlternativeScraper:
    """Scraper for alternative sources"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml',
            'Accept-Language': 'en-US,en;q=0.9'
        })
    
    def extract_clubs_from_wikipedia(self, url):
        """Extract club names from Wikipedia table"""
        print(f"📖 Scraping Wikipedia: {url}")
        
        try:
            response = self.session.get(url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            clubs = []
            
            # Look for tables with class 'wikitable'
            tables = soup.find_all('table', class_='wikitable')
            
            for table in tables:
                rows = table.find_all('tr')
                for row in rows:
                    cells = row.find_all(['td', 'th'])
                    for cell in cells:
                        # Look for links that might be clubs
                        links = cell.find_all('a', href=True)
                        for link in links:
                            href = link['href']
                            text = link.text.strip()
                            
                            # Filter: likely club links
                            if text and len(text) > 2 and not text.isdigit():
                                # Skip common non-club links
                                skip_terms = ['edit', 'citation', 'wikipedia', 'season', 
                                            'championship', 'league', 'division', 'federation']
                                if not any(term in text.lower() for term in skip_terms):
                                    if not any(c['name'] == text for c in clubs):  # Deduplicate
                                        clubs.append({
                                            'name': text,
                                            'url': f"https://en.wikipedia.org{href}" if href.startswith('/') else href
                                        })
            
            # Additional extraction: look for list items with club names
            lists = soup.find_all(['ul', 'ol'])
            for lst in lists:
                items = lst.find_all('li')
                for item in items:
                    link = item.find('a', href=True)
                    if link:
                        text = link.text.strip()
                        href = link['href']
                        if text and len(text) > 2 and not text.isdigit():
                            skip_terms = ['edit', 'citation', 'wikipedia', 'season']
                            if not any(term in text.lower() for term in skip_terms):
                                if not any(c['name'] == text for c in clubs):
                                    clubs.append({
                                        'name': text,
                                        'url': f"https://en.wikipedia.org{href}" if href.startswith('/') else href
                                    })
            
            return clubs
        
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            return []
    
    def extract_clubs_from_official(self, url):
        """Extract club names from official league website"""
        print(f"🏟️ Scraping official site: {url}")
        
        try:
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            clubs = []
            
            # Look for common club listing patterns
            # Method 1: Links with 'club' or 'team' in href
            links = soup.find_all('a', href=re.compile(r'club|team|equipo', re.I))
            for link in links[:50]:  # Limit to first 50
                text = link.text.strip()
                if text and len(text) > 2:
                    clubs.append({
                        'name': text,
                        'url': link.get('href', '')
                    })
            
            return clubs
        
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            return []

def scrape_league_alternative(league_key, config):
    """Scrape league from alternative sources"""
    print(f"\n{'='*60}")
    print(f"🏆 {config['name']} ({config['country']}) - Tier {config['tier']}")
    print(f"{'='*60}")
    
    scraper = AlternativeScraper()
    all_clubs = []
    
    for source in config['sources']:
        clubs = []
        
        if source['type'] == 'wikipedia':
            clubs = scraper.extract_clubs_from_wikipedia(source['url'])
        elif source['type'] == 'official':
            clubs = scraper.extract_clubs_from_official(source['url'])
        
        if clubs:
            print(f"✅ Found {len(clubs)} clubs from {source['type']}")
            all_clubs.extend(clubs)
            break  # Use first successful source
        else:
            print(f"⚠️  No clubs found from {source['type']}")
    
    # Deduplicate
    seen = set()
    unique_clubs = []
    for club in all_clubs:
        if club['name'] not in seen:
            seen.add(club['name'])
            unique_clubs.append(club)
    
    if unique_clubs:
        print(f"\n📊 Total unique clubs: {len(unique_clubs)}")
        for i, club in enumerate(unique_clubs[:10], 1):
            print(f"  {i}. {club['name']}")
        if len(unique_clubs) > 10:
            print(f"  ... and {len(unique_clubs) - 10} more")
        
        # Save results
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        output_dir = '/data/.openclaw/workspace-amaya/projects/football-data/data/alternative_sources'
        os.makedirs(output_dir, exist_ok=True)
        
        safe_name = f"{config['country']}_{config['name']}".replace(' ', '_').replace('/', '-').lower()
        filename = f"{safe_name}_{timestamp}.json"
        filepath = os.path.join(output_dir, filename)
        
        result = {
            'league': config['name'],
            'country': config['country'],
            'tier': config['tier'],
            'clubs_found': len(unique_clubs),
            'clubs': unique_clubs,
            'scraped_at': datetime.utcnow().isoformat(),
            'success': True
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Saved: {filepath}")
        return filepath
    
    return None

def main():
    """Scrape all failed leagues from alternative sources"""
    print(f"""
╔════════════════════════════════════════════════════════════╗
║     Alternative Sources Scraper (12 Failed Leagues)       ║
║     Wikipedia + Official Websites                          ║
╚════════════════════════════════════════════════════════════╝
    """)
    
    results = []
    success_count = 0
    total_clubs = 0
    
    for i, (key, config) in enumerate(ALTERNATIVE_SOURCES.items(), 1):
        print(f"\n{'─'*60}")
        print(f"Progress: {i}/{len(ALTERNATIVE_SOURCES)} leagues")
        print(f"{'─'*60}")
        
        try:
            filepath = scrape_league_alternative(key, config)
            if filepath:
                with open(filepath, 'r') as f:
                    data = json.load(f)
                success_count += 1
                total_clubs += data['clubs_found']
                results.append({
                    'league': config['name'],
                    'country': config['country'],
                    'clubs_found': data['clubs_found'],
                    'success': True
                })
            else:
                results.append({
                    'league': config['name'],
                    'country': config['country'],
                    'success': False
                })
        
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            results.append({
                'league': config['name'],
                'country': config['country'],
                'success': False,
                'error': str(e)
            })
        
        # Delay between scrapes
        if i < len(ALTERNATIVE_SOURCES):
            print(f"\n⏳ Waiting 5 seconds...")
            time.sleep(5)
    
    # Summary
    print(f"""
╔════════════════════════════════════════════════════════════╗
║                   SCRAPE COMPLETE                          ║
║                                                            ║
║  Leagues scraped: {success_count:3d}/{len(ALTERNATIVE_SOURCES):3d}                             ║
║  Clubs found: {total_clubs:4d}                                   ║
╚════════════════════════════════════════════════════════════╝
    """)

if __name__ == '__main__':
    main()
