# AI2me Football Data Infrastructure

**Comprehensive football club database for AI2me Sports agents**

Built for Enzo Rubio (AI Sporting Director), Tania Freeman (Athlete Advisor), and Bernie Brooks (Athlete Advisor).

## 📊 Coverage

- **4,331 clubs** across 47 leagues
- **24 countries** (Europe, Americas, Asia, Middle East)
- **Tier 1-4 divisions** (Spain has all 4 divisions)

### Top 10 Countries
1. Colombia: 700 clubs
2. China: 454 clubs
3. Peru: 435 clubs
4. Venezuela: 414 clubs
5. Spain: 414 clubs
6. Argentina: 361 clubs
7. Ecuador: 340 clubs
8. Bolivia: 275 clubs
9. Saudi Arabia: 267 clubs
10. Mexico: 225 clubs

## 🏗️ Architecture

### Database
- **SQLite** (portable, no server needed)
- 7 tables: clubs, leagues, players, contracts, transfers, scrape_cache, data_quality
- Full SQL query support

### Data Sources
- **Transfermarkt** (authenticated scraping, 629 clubs)
- **Wikipedia** (fallback for 11 leagues, 3,702 clubs)

### Auto-Update
- **Weekly refresh** (Sundays 3:00 AM CET)
- 2-3 hour scrape duration (8-second delays)
- Automatic completion notifications

## 🚀 Quick Start

### Search Clubs
```bash
python3 tools/club_search.py --country Spain --tier 1
python3 tools/club_search.py --name "Barcelona"
python3 tools/club_search.py --list-countries
```

### Python API
```python
from tools.club_search import search_clubs, get_club_details

# Find all La Liga clubs
clubs = search_clubs(country='Spain', tier=1, league='La Liga')

# Get club details
details = get_club_details('Real Madrid')
```

## 📁 Structure

```
football-data/
├── database/
│   ├── schema.sql              # Database schema (7 tables)
│   ├── create_database.py      # Initialize database
│   ├── import_clubs.py         # Import Transfermarkt data
│   └── import_wikipedia_data.py # Import Wikipedia data
├── scrapers/
│   ├── transfermarkt_auth.py   # Authenticated Transfermarkt scraper
│   ├── alternative_sources.py  # Wikipedia scraper
│   ├── full_scrape_auth.py     # Full 47-league scrape
│   └── leagues_full.json       # League configurations
├── tools/
│   └── club_search.py          # Universal search tool
└── update_database.sh          # Weekly auto-update script
```

## 🔄 Updates

### Manual Update
```bash
bash update_database.sh
```

### Scheduled Update
- Automatic weekly refresh (Sundays 3:00 AM CET)
- Configured via OpenClaw cron

## 💰 Cost

**$0/month** — No API fees, uses existing VPS resources

## 🔐 Security

- Data files excluded from repo (see `.gitignore`)
- Credentials managed via OpenClaw workspace
- Respectful scraping (8-second delays)

## 📖 Documentation

- `PLAN.md` — Project plan & requirements
- `QUICK_START.md` — Getting started guide
- `SCALE.md` — Scaling & performance
- `DATABASE_ACCESS.md` — Database schema & queries
- `UPDATE_SCHEDULE.md` — Auto-update configuration

## 👥 Agent Access

- **Enzo Rubio** (AI Sporting Director) — Club scouting
- **Tania Freeman** (Athlete Advisor) — Player career advice
- **Bernie Brooks** (Athlete Advisor) — Transfer negotiations

All agents have full query access via symlinked workspaces.

## 🛠️ Built With

- Python 3
- SQLite
- BeautifulSoup4
- Requests
- OpenClaw automation platform

---

**Project:** AI2me Sports  
**Company:** EternitAI Group  
**Created:** March 16, 2026
