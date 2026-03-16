# Football Data Infrastructure — Scale & Coverage

**Updated:** 2026-03-16 07:24 CET  
**Request:** Carlos Cuevas — "ALL clubs from 22+ countries, 1st & 2nd divisions"

---

## Coverage Target

### Leagues: **47** (23 countries, up to Tier 4)
- 🇪🇸 Spain: La Liga + La Liga 2 + Primera Federación + Segunda Federación
- 🇮🇹 Italy: Serie A + Serie B  
- 🇩🇪 Germany: Bundesliga + 2. Bundesliga
- 🇵🇹 Portugal: Primeira Liga + Liga Portugal 2
- 🇫🇷 France: Ligue 1 + Ligue 2
- 🇯🇵 Japan: J1 League + J2 League
- 🇨🇳 China: Super League + League One
- 🇸🇦 Saudi Arabia: Pro League + First Division
- 🏴󠁧󠁢󠁥󠁮󠁧󠁿 England: Premier League + Championship
- 🇭🇷 Croatia: HNL + Prva NL
- 🇩🇰 Denmark: Superliga + 1st Division
- 🇳🇱 Netherlands: Eredivisie + Eerste Divisie
- 🏴󠁧󠁢󠁳󠁣󠁴󠁿 Scotland: Premiership + Championship
- 🇧🇷 Brazil: Série A + Série B
- 🇨🇴 Colombia: Liga BetPlay + Torneo BetPlay
- 🇦🇷 Argentina: Liga Profesional + Primera Nacional
- 🇲🇽 Mexico: Liga MX + Liga de Expansión
- 🇺🇾 Uruguay: Primera División + Segunda División
- 🇪🇨 Ecuador: LigaPro + Segunda Categoría
- 🇧🇴 Bolivia: División Profesional
- 🇵🇪 Peru: Liga 1 + Liga 2
- 🇻🇪 Venezuela: Primera División + Segunda División
- 🇺🇸🇨🇦 USA/Canada: MLS + USL Championship

### Clubs: **956 total**

**Breakdown by country (all divisions):**
- Spain: 172 clubs (20+22+40+90 — includes Barça B, Real Madrid Castilla, etc.)
- Italy: 40 clubs (20+20)
- Germany: 36 clubs (18+18)
- Portugal: 36 clubs (18+18)
- France: 38 clubs (18+20)
- Japan: 42 clubs (20+22)
- China: 34 clubs (16+18)
- Saudi Arabia: 38 clubs (18+20)
- England: 44 clubs (20+24)
- Croatia: 22 clubs (10+12)
- Denmark: 24 clubs (12+12)
- Netherlands: 38 clubs (18+20)
- Scotland: 22 clubs (12+10)
- Brazil: 40 clubs (20+20)
- Colombia: 36 clubs (20+16)
- Argentina: 65 clubs (28+37)
- Mexico: 34 clubs (18+16)
- Uruguay: 30 clubs (16+14)
- Ecuador: 28 clubs (16+12)
- Bolivia: 16 clubs (16+0)
- Peru: 34 clubs (18+16)
- Venezuela: 34 clubs (18+16)
- USA/Canada: 53 clubs (29+24)

---

## Scraping Time Estimates

### Phase 1: League Club Lists (47 leagues)
**Using:** `all_clubs_scraper.py`  
**Time:** ~6-8 minutes (8s delay between leagues)  
**Output:** Raw HTML/text with club names & URLs

### Phase 2: Individual Club Websites (956 clubs)
**Time:** ~125-150 minutes at 8s delay per club  
**Faster option:** 5s delay = ~66-80 minutes (higher risk of rate limiting)  
**Output:** Squad lists, news, contract announcements

### Phase 3: Contract/Salary Data
**Using:** `contract_scraper.py`  
**Coverage:** Capology has 7 major leagues (limited coverage)  
**Time:** ~1-2 minutes per league

### **Total Initial Scrape:** ~2-3 hours for complete coverage

---

## Storage Requirements

**Per club (estimated):**
- Raw HTML: 100-500 KB
- Processed JSON: 10-50 KB

**Total storage (956 clubs):**
- Raw data: ~80-400 MB
- Processed data: ~8-40 MB
- Database: ~50-100 MB (structured data)

**Total: ~150-500 MB for complete dataset**

---

## Rate Limiting & Respectful Scraping

### Current Settings:
- 8 seconds between league scrapes
- 5-8 seconds between club scrapes
- JavaScript rendering enabled (slower but more reliable)
- Headless browser mode (stealthy)

### Risks:
- Transfermarkt may block if too aggressive
- Official club sites vary in rate limit tolerance
- Some sites use Cloudflare/anti-bot protection

### Mitigation:
- ✅ Use delays (8s default)
- ✅ Rotate User-Agent (built into scraper)
- ✅ Respect robots.txt
- ⏰ Scrape during low-traffic hours (late night UTC)
- 💾 Cache results (avoid re-scraping)

---

## Update Frequency Recommendations

**League regulations:** Weekly  
**Club squads:** Weekly  
**Transfer news:** Daily during transfer windows  
**Contract data:** Monthly  
**Player market values:** Bi-weekly

**Cron schedule suggestion:**
```bash
# League regulations (every Monday 3am CET)
0 3 * * 1 python3 /path/to/league_scraper.py --type leagues --priority high

# All clubs (every Sunday 2am CET)
0 2 * * 0 python3 /path/to/all_clubs_scraper.py --delay 10

# Contract data (1st of each month, 4am CET)
0 4 1 * * python3 /path/to/contract_scraper.py --source all

# Transfer news (daily during windows: Jun-Sep, Jan-Feb)
0 1 * 6-9,1-2 * python3 /path/to/league_scraper.py --type clubs --limit 50
```

---

## Cost Analysis

### Current (Free Scraping):
- Server: Existing VPS (no added cost)
- Bandwidth: ~500 MB/week = negligible
- Storage: ~500 MB total = negligible
- **Total: $0/month** ✅

### With Transfermarkt API:
- Official API: €500-2000/month ❌
- RapidAPI (unofficial): $50-200/month ⚠️
- **Savings by scraping: €500-2000/month**

### With Database Hosting:
- VPS PostgreSQL: $0 (use existing server)
- Managed DB (Supabase): $25/month
- AWS RDS: $50-100/month
- **Recommendation: Use existing VPS ($0)**

---

## Scalability Concerns

### Current Bottlenecks:
1. **Scraping speed** (single-threaded, ~2-3 hours)
2. **Manual parsing** (need HTML → structured data parser)
3. **Data quality** (no validation layer yet)

### Solutions:
1. **Parallel scraping** (run 5-10 concurrent scrapers)
   - Time: 2-3 hours → 20-30 minutes
   - Risk: Higher chance of rate limiting
   
2. **Automated parsing** (BeautifulSoup + regex patterns)
   - Extract club names, URLs, squad lists automatically
   - Build validation layer to detect missing/incorrect data

3. **Database indexing** (PostgreSQL optimizations)
   - Index by league, country, position, salary
   - Views for common queries (top earners, expiring contracts)

---

## Next Steps

1. ✅ Configuration complete (47 leagues, 956 clubs mapped)
2. ✅ Scraper built (`all_clubs_scraper.py`)
3. ⏳ **Test run** (scrape 3 leagues to validate)
4. ⏳ Build HTML parser (extract club data from raw text)
5. ⏳ Run full scrape (all 792 clubs)
6. ⏳ Deploy database schema
7. ⏳ Build import pipeline (JSON → PostgreSQL)

---

## Questions for Carlos

1. **Scraping schedule:** Run full scrape now (2-3 hours) or wait for off-hours?
2. **Parallel scraping:** Risk rate limiting for faster results (20-30 min)?
3. **Database deployment:** VPS (free) or managed service ($25/month)?
4. **Data validation:** Manual review of first 50 clubs or automated?

---

**Status:** 🟢 Ready to start test scrape  
**Command:** `python3 scrapers/all_clubs_scraper.py --test`
