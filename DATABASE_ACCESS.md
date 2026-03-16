# Football Data Database — Agent Access Guide

**Created:** 2026-03-16 12:26 CET  
**Database:** SQLite  
**Location:** `/data/.openclaw/workspace-amaya/projects/football-data/data/football_data.db`

---

## Database Stats

- **Leagues:** 36 (all divisions, 21 countries)
- **Clubs:** 609 (authenticated Transfermarkt scrape)
- **Tables:** 7 (players, contracts, transfers, clubs, leagues, scrape_cache, data_quality)
- **Size:** 0.12 MB

---

## Quick Access (Python)

```python
import sqlite3

# Connect
conn = sqlite3.connect('/data/.openclaw/workspace-amaya/projects/football-data/data/football_data.db')
cursor = conn.cursor()

# Example: Search clubs by country
cursor.execute('''
    SELECT c.name, l.name as league
    FROM clubs c
    LEFT JOIN leagues l ON c.league_id = l.id
    WHERE c.country = ?
    ORDER BY c.name
''', ('Spain',))

for name, league in cursor.fetchall():
    print(f"{name} ({league})")

conn.close()
```

---

## Common Queries for Agents

### For Enzo (Club Scout)
```sql
-- Find all clubs in a specific league
SELECT name, official_website
FROM clubs
WHERE league_id = (SELECT id FROM leagues WHERE name = 'Premier League')
ORDER BY name;

-- Count clubs by country
SELECT country, COUNT(*) as club_count
FROM clubs
GROUP BY country
ORDER BY club_count DESC;
```

### For Tania/Bernie (Player Advisors)
```sql
-- Find leagues in a country
SELECT name, tier, 
       (SELECT COUNT(*) FROM clubs WHERE league_id = leagues.id) as num_clubs
FROM leagues
WHERE country = 'Spain'
ORDER BY tier;

-- Get club details
SELECT c.name, c.country, l.name as league, l.tier, c.official_website
FROM clubs c
LEFT JOIN leagues l ON c.league_id = l.id
WHERE c.name LIKE '%Barcelona%';
```

---

## Database Schema

**Main Tables:**
- `clubs` — 609 clubs with league affiliations
- `leagues` — 36 leagues with country/tier info
- `players` — (empty, ready for player data)
- `contracts` — (empty, ready for contract data)
- `transfers` — (empty, ready for transfer data)

**Fields in clubs table:**
- id, name, league_id, country, official_website, salary_cap, total_budget, last_updated

**Fields in leagues table:**
- id, name, country, tier, num_teams, salary_cap, regulations, official_website, last_updated

---

## Coverage by Country

| Country | Clubs | Leagues |
|---------|-------|---------|
| Spain | 82 | 4 |
| England | 44 | 2 |
| Japan | 40 | 2 |
| Italy | 40 | 2 |
| Brazil | 40 | 2 |
| Netherlands | 38 | 2 |
| Portugal | 36 | 2 |
| Germany | 36 | 2 |
| France | 36 | 2 |
| Uruguay | 30 | 2 |
| USA/Canada | 38 | 2 |
| Argentina | 28 | 1 |
| Denmark | 24 | 2 |
| Scotland | 22 | 2 |
| Croatia | 22 | 2 |
| Saudi Arabia | 18 | 1 |
| Peru | 18 | 1 |
| Mexico | 18 | 1 |
| China | 16 | 1 |
| Ecuador | 3 | 1 |

---

## Next Steps

1. ⏳ Import player data (10,000+ profiles)
2. ⏳ Import contract data (5,000+ comparables)
3. ⏳ Import transfer history (15,000+ records)
4. ⏳ Build agent query interfaces

---

**Status:** ✅ Database deployed and ready for agent queries
