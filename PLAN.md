# Football Data Infrastructure Plan

## Task #3: League/Club Official Data Scraper

### Target Data Sources:
1. **League Official Sites** (regulations, salary caps)
   - UEFA (Champions League, Europa League)
   - Premier League
   - La Liga
   - Serie A
   - Bundesliga
   - Ligue 1
   - MLS
   - Saudi Pro League
   
2. **Club Official Sites** (contracts, news, squad lists)
   - Top 100 clubs by revenue
   - Focus: Big 5 leagues + emerging markets

### Scraper Architecture:
- Base: `/data/.openclaw/workspace-amaya/advanced_scraper.py`
- Structure: Modular per league/federation
- Storage: PostgreSQL (structured) + JSON (raw cache)
- Update frequency: Daily for news, weekly for regulations

### Implementation Steps:
1. ✅ Create project structure
2. [ ] Map league/club URLs and data locations
3. [ ] Build league scraper (regulations, salary caps)
4. [ ] Build club scraper (contracts, rosters, news)
5. [ ] Set up database schema
6. [ ] Create update scheduler (cron jobs)
7. [ ] Build validation layer (detect missing/stale data)

---

## Task #4: Player/Contract Database

### Option A: License Existing Database
**Research needed:**
- Transfermarkt Database (API + full dataset)
- SportsRadar Player Database
- StatsBomb Database
- Opta Sports Data

**Pros:** Immediate access, professional quality
**Cons:** Recurring cost, dependency, limited customization

### Option B: Build Our Own
**Data Sources:**
- Scrape from Transfermarkt (public data)
- Aggregate from club official announcements
- Contract data from Capology, Spotrac
- Career paths from Wikipedia, league archives

**Pros:** Full control, no licensing fees, customizable
**Cons:** Time to build, maintenance burden, data quality risk

### Recommended Hybrid Approach:
1. Start with licensed data (Transfermarkt API) for immediate coverage
2. Build proprietary enrichment layer (contract details, insider intel)
3. Gradually reduce dependency by building our own historical database

### Database Schema (PostgreSQL):

```sql
-- Players table
CREATE TABLE players (
    id SERIAL PRIMARY KEY,
    transfermarkt_id VARCHAR(50) UNIQUE,
    name VARCHAR(200),
    date_of_birth DATE,
    nationality VARCHAR(100),
    position VARCHAR(50),
    current_club_id INT,
    market_value DECIMAL(15,2),
    last_updated TIMESTAMP
);

-- Contracts table
CREATE TABLE contracts (
    id SERIAL PRIMARY KEY,
    player_id INT REFERENCES players(id),
    club_id INT,
    start_date DATE,
    end_date DATE,
    annual_salary DECIMAL(15,2),
    signing_bonus DECIMAL(15,2),
    release_clause DECIMAL(15,2),
    agent VARCHAR(200),
    source VARCHAR(100),
    verified BOOLEAN DEFAULT FALSE,
    last_updated TIMESTAMP
);

-- Transfers table
CREATE TABLE transfers (
    id SERIAL PRIMARY KEY,
    player_id INT REFERENCES players(id),
    from_club_id INT,
    to_club_id INT,
    transfer_date DATE,
    fee DECIMAL(15,2),
    fee_currency VARCHAR(10),
    loan BOOLEAN DEFAULT FALSE,
    source VARCHAR(100),
    last_updated TIMESTAMP
);

-- Clubs table
CREATE TABLE clubs (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200),
    league VARCHAR(100),
    country VARCHAR(100),
    official_website VARCHAR(500),
    salary_cap DECIMAL(15,2),
    total_budget DECIMAL(15,2),
    last_updated TIMESTAMP
);

-- Leagues table
CREATE TABLE leagues (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200),
    country VARCHAR(100),
    tier INT,
    salary_cap DECIMAL(15,2),
    regulations TEXT,
    official_website VARCHAR(500),
    last_updated TIMESTAMP
);
```

### Next Actions:
1. Research Transfermarkt API licensing costs
2. Design scraper for contract data (Capology, Spotrac)
3. Set up PostgreSQL database
4. Build initial data import pipeline
5. Create validation/enrichment layer

---

**Created:** 2026-03-16 07:09 CET
**Owner:** Amaya (CoS)
**For:** Tania (Chief Data Officer)
