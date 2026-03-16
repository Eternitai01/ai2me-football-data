#!/usr/bin/env python3
"""
Authenticated Transfermarkt Scraper
Uses Carlos's account credentials to bypass anti-bot protection
Username: Eternitai
Password: Americo1804@@@
"""

import requests
import json
import time
import os
from datetime import datetime
from bs4 import BeautifulSoup

# Transfermarkt credentials
TM_USERNAME = "Eternitai"
TM_PASSWORD = "Americo1804@@@"
TM_LOGIN_URL = "https://www.transfermarkt.com/login"
TM_BASE_URL = "https://www.transfermarkt.com"

class TransfermarktAuthSession:
    """Authenticated Transfermarkt session"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Referer': 'https://www.transfermarkt.com/'
        })
        self.logged_in = False
    
    def login(self):
        """Login to Transfermarkt"""
        print(f"\n🔐 Logging in to Transfermarkt...")
        print(f"👤 Username: {TM_USERNAME}")
        
        try:
            # Get login page to extract CSRF token
            login_page = self.session.get(TM_LOGIN_URL)
            soup = BeautifulSoup(login_page.content, 'html.parser')
            
            # Find CSRF token (if present)
            csrf_token = None
            csrf_input = soup.find('input', {'name': '_token'}) or soup.find('input', {'name': 'csrf_token'})
            if csrf_input:
                csrf_token = csrf_input.get('value')
            
            # Prepare login data
            login_data = {
                'login': TM_USERNAME,
                'password': TM_PASSWORD,
                'submit': 'Login'
            }
            
            if csrf_token:
                login_data['_token'] = csrf_token
            
            # Submit login
            response = self.session.post(
                TM_LOGIN_URL,
                data=login_data,
                allow_redirects=True
            )
            
            # Check if logged in
            if 'logout' in response.text.lower() or TM_USERNAME.lower() in response.text.lower():
                self.logged_in = True
                print(f"✅ Login successful!")
                return True
            else:
                print(f"❌ Login failed (no logout link found)")
                return False
        
        except Exception as e:
            print(f"❌ Login error: {str(e)}")
            return False
    
    def scrape_league_clubs(self, league_url):
        """Scrape club list from league page"""
        if not self.logged_in:
            print(f"⚠️  Not logged in, attempting login...")
            if not self.login():
                return None
        
        print(f"\n📥 Fetching: {league_url}")
        
        try:
            response = self.session.get(league_url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract clubs (Transfermarkt uses specific table classes)
            clubs = []
            
            # Method 1: Look for club table
            club_table = soup.find('table', class_='items')
            if club_table:
                rows = club_table.find_all('tr', class_=['odd', 'even'])
                for row in rows:
                    club_link = row.find('a', href=True)
                    if club_link and '/verein/' in club_link['href']:
                        club_name = club_link.text.strip()
                        club_url = TM_BASE_URL + club_link['href']
                        clubs.append({
                            'name': club_name,
                            'url': club_url
                        })
            
            # Method 2: Look for responsive table (mobile view)
            if not clubs:
                responsive_tables = soup.find_all('div', class_='responsive-table')
                for table_div in responsive_tables:
                    links = table_div.find_all('a', href=True)
                    for link in links:
                        if '/verein/' in link['href']:
                            club_name = link.text.strip()
                            club_url = TM_BASE_URL + link['href']
                            if club_name and {'name': club_name, 'url': club_url} not in clubs:
                                clubs.append({
                                    'name': club_name,
                                    'url': club_url
                                })
            
            print(f"✅ Found {len(clubs)} clubs")
            
            if clubs:
                for i, club in enumerate(clubs[:5], 1):
                    print(f"  {i}. {club['name']}")
                if len(clubs) > 5:
                    print(f"  ... and {len(clubs) - 5} more")
            
            return clubs
        
        except Exception as e:
            print(f"❌ Scrape error: {str(e)}")
            return None

def scrape_league_with_auth(league_config):
    """Scrape league clubs using authenticated session"""
    url = league_config['transfermarkt_url']
    
    print(f"\n{'='*60}")
    print(f"🏆 {league_config['name']} ({league_config['country']})")
    print(f"📊 Expected: {league_config['num_teams']} teams")
    print(f"{'='*60}")
    
    # Create authenticated session
    tm_session = TransfermarktAuthSession()
    
    # Login
    if not tm_session.login():
        print(f"❌ Failed to login, cannot scrape")
        return None
    
    # Scrape clubs
    clubs = tm_session.scrape_league_clubs(url)
    
    if clubs:
        # Save results
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        output_dir = os.path.join(os.path.dirname(__file__), '..', 'data', 'transfermarkt_auth')
        os.makedirs(output_dir, exist_ok=True)
        
        safe_name = f"{league_config['country']}_{league_config['name']}".replace(' ', '_').replace('/', '-').lower()
        filename = f"{safe_name}_{timestamp}.json"
        filepath = os.path.join(output_dir, filename)
        
        result = {
            'league': league_config['name'],
            'country': league_config['country'],
            'tier': league_config['tier'],
            'expected_teams': league_config['num_teams'],
            'clubs_found': len(clubs),
            'clubs': clubs,
            'url': url,
            'scraped_at': datetime.utcnow().isoformat(),
            'success': True
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Saved: {filepath}")
        return filepath
    
    return None

def main():
    """Test authenticated scraper"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Authenticated Transfermarkt scraper')
    parser.add_argument('--test', action='store_true',
                       help='Test with La Liga')
    
    args = parser.parse_args()
    
    print(f"""
╔════════════════════════════════════════════════════════════╗
║      Transfermarkt Authenticated Scraper (Carlos)          ║
║      Username: Eternitai | Bypasses anti-bot checks        ║
╚════════════════════════════════════════════════════════════╝
    """)
    
    if args.test:
        # Test with La Liga
        league_config = {
            'name': 'La Liga',
            'country': 'Spain',
            'tier': 1,
            'num_teams': 20,
            'transfermarkt_url': 'https://www.transfermarkt.com/laliga/startseite/wettbewerb/ES1'
        }
        
        scrape_league_with_auth(league_config)
    else:
        print("Usage: --test")

if __name__ == '__main__':
    main()
