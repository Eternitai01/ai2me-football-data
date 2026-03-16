# Quick Start — Football Data Scraping

**Updated:** 2026-03-16 07:43 CET  
**Status:** Ready to scrape 956 clubs from 47 leagues

---

## What You Can Do Right Now

### Option 1: Test Run (Recommended First)
Scrape 3 leagues to validate everything works:
```bash
cd /data/.openclaw/workspace-amaya/projects/football-data
python3 scrapers/all_clubs_scraper.py --test
```
**Time:** ~1 minute  
**Output:** 3 league club lists (Spain, Italy, Germany)

---

### Option 2: Country-Specific Scrape
Scrape all clubs from one country:
```bash
# Spain (all 4 divisions = 172 clubs, includes Barça B)
python3 scrapers/all_clubs_scraper.py --country Spain

# England (Premier League + Championship = 44 clubs)
python3 scrapers/all_clubs_scraper.py --country England

# Brazil (Série A + Série B = 40 clubs)
python3 scrapers/all_clubs_scraper.py --country Brazil
```
**Time:** ~1-2 minutes per country

---

### Option 3: Division-Specific Scrape
Scrape only 1st or 2nd division clubs:
```bash
# All 1st division leagues (top tier only)
python3 scrapers/all_clubs_scraper.py --tier 1

# All 2nd division leagues
python3 scrapers/all_clubs_scraper.py --tier 2
```
**Time:** ~3-4 minutes

---

### Option 4: FULL SCRAPE (All 956 Clubs)
Scrape everything:
```bash
python3 scrapers/all_clubs_scraper.py --delay 8
```
**Time:** ~2.5-3 hours  
**Output:** 956 club profiles across 47 leagues

⚠️ **Recommendation:** Run overnight or during low-traffic hours

---

## What Happens When You Run a Scrape

1. **Fetches league pages** from Transfermarkt (club lists)
2. **Saves raw HTML/text** to `data/clubs_raw/`
3. **Saves structured JSON** to `data/league_clubs/`
4. **Logs progress** (shows which leagues/clubs succeeded/failed)

---

## After Scraping

### View Results:
```bash
# List scraped data
ls -lh data/league_clubs/
ls -lh data/clubs_raw/

# Preview JSON output
cat data/league_clubs/spain_la_liga_*.json | jq
```

### Next Steps:
1. Build HTML parser (extract club names/URLs from raw text)
2. Run second pass to scrape individual club websites
3. Import to PostgreSQL database
4. Set up automated updates (cron jobs)

---

## Coverage Summary

| Region | Leagues | Clubs |
|--------|---------|-------|
| Europe | 26 | 548 |
| Americas | 18 | 366 |
| Asia | 6 | 100 |
| Middle East | 2 | 38 |
| **TOTAL** | **47** | **956** |

**Countries:** Spain, Italy, Germany, Portugal, France, Japan, China, Saudi Arabia, England, Croatia, Denmark, Netherlands, Scotland, Brazil, Colombia, Argentina, Mexico, Uruguay, Ecuador, Bolivia, Peru, Venezuela, USA/Canada

---

## Need Help?

- **Technical issues:** Check logs in terminal output
- **Rate limiting errors:** Increase `--delay` to 10-15 seconds
- **Incomplete data:** Re-run specific country with `--country X`
- **Questions:** Ask Amaya (CoS) or Tania (CDO)

---

**Ready to start?** Run the test command above ↑
