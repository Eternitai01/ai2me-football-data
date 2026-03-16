-- Football Data Database Schema
-- Created: 2026-03-16
-- For: AI2me Pro - Tania (Chief Data Officer)

-- Players table (10,000+ profiles target)
CREATE TABLE IF NOT EXISTS players (
    id SERIAL PRIMARY KEY,
    transfermarkt_id VARCHAR(50) UNIQUE,
    name VARCHAR(200) NOT NULL,
    date_of_birth DATE,
    nationality VARCHAR(100),
    position VARCHAR(50),
    current_club_id INT,
    market_value DECIMAL(15,2),
    market_value_currency VARCHAR(10) DEFAULT 'EUR',
    height_cm INT,
    foot VARCHAR(20),
    agent VARCHAR(200),
    created_at TIMESTAMP DEFAULT NOW(),
    last_updated TIMESTAMP DEFAULT NOW(),
    data_source VARCHAR(100)
);

-- Contracts table (5,000+ comparables target)
CREATE TABLE IF NOT EXISTS contracts (
    id SERIAL PRIMARY KEY,
    player_id INT REFERENCES players(id) ON DELETE CASCADE,
    club_id INT,
    start_date DATE NOT NULL,
    end_date DATE,
    annual_salary DECIMAL(15,2),
    salary_currency VARCHAR(10) DEFAULT 'EUR',
    signing_bonus DECIMAL(15,2),
    release_clause DECIMAL(15,2),
    performance_bonuses TEXT,
    agent VARCHAR(200),
    contract_type VARCHAR(50), -- permanent, loan, trial
    verified BOOLEAN DEFAULT FALSE,
    source VARCHAR(100),
    created_at TIMESTAMP DEFAULT NOW(),
    last_updated TIMESTAMP DEFAULT NOW()
);

-- Transfers table (15,000+ career paths target)
CREATE TABLE IF NOT EXISTS transfers (
    id SERIAL PRIMARY KEY,
    player_id INT REFERENCES players(id) ON DELETE CASCADE,
    from_club_id INT,
    to_club_id INT,
    transfer_date DATE NOT NULL,
    fee DECIMAL(15,2),
    fee_currency VARCHAR(10) DEFAULT 'EUR',
    loan BOOLEAN DEFAULT FALSE,
    loan_fee DECIMAL(15,2),
    buy_option DECIMAL(15,2),
    agent VARCHAR(200),
    source VARCHAR(100),
    created_at TIMESTAMP DEFAULT NOW(),
    last_updated TIMESTAMP DEFAULT NOW()
);

-- Clubs table
CREATE TABLE IF NOT EXISTS clubs (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    league_id INT,
    country VARCHAR(100),
    official_website VARCHAR(500),
    founded_year INT,
    stadium VARCHAR(200),
    total_squad_value DECIMAL(15,2),
    salary_cap DECIMAL(15,2),
    total_budget DECIMAL(15,2),
    owner VARCHAR(200),
    president VARCHAR(200),
    manager VARCHAR(200),
    data_source VARCHAR(100),
    created_at TIMESTAMP DEFAULT NOW(),
    last_updated TIMESTAMP DEFAULT NOW()
);

-- Leagues table (1,200+ leagues target)
CREATE TABLE IF NOT EXISTS leagues (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    country VARCHAR(100),
    tier INT,
    confederation VARCHAR(50), -- UEFA, CONMEBOL, AFC, CAF, CONCACAF, OFC
    num_teams INT,
    salary_cap DECIMAL(15,2),
    salary_cap_currency VARCHAR(10) DEFAULT 'EUR',
    transfer_window_summer_start DATE,
    transfer_window_summer_end DATE,
    transfer_window_winter_start DATE,
    transfer_window_winter_end DATE,
    regulations TEXT,
    official_website VARCHAR(500),
    data_source VARCHAR(100),
    created_at TIMESTAMP DEFAULT NOW(),
    last_updated TIMESTAMP DEFAULT NOW()
);

-- Scraped data cache (raw JSON storage)
CREATE TABLE IF NOT EXISTS scrape_cache (
    id SERIAL PRIMARY KEY,
    url VARCHAR(1000) NOT NULL,
    content_type VARCHAR(50), -- league, club, player
    raw_json JSONB,
    scraped_at TIMESTAMP DEFAULT NOW(),
    success BOOLEAN DEFAULT TRUE,
    error_message TEXT
);

-- Data quality tracking
CREATE TABLE IF NOT EXISTS data_quality (
    id SERIAL PRIMARY KEY,
    table_name VARCHAR(100),
    record_id INT,
    field_name VARCHAR(100),
    issue_type VARCHAR(100), -- missing, outdated, conflicting, invalid
    severity VARCHAR(20), -- low, medium, high, critical
    detected_at TIMESTAMP DEFAULT NOW(),
    resolved BOOLEAN DEFAULT FALSE,
    resolved_at TIMESTAMP
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_players_name ON players(name);
CREATE INDEX IF NOT EXISTS idx_players_club ON players(current_club_id);
CREATE INDEX IF NOT EXISTS idx_players_transfermarkt ON players(transfermarkt_id);
CREATE INDEX IF NOT EXISTS idx_contracts_player ON contracts(player_id);
CREATE INDEX IF NOT EXISTS idx_contracts_club ON contracts(club_id);
CREATE INDEX IF NOT EXISTS idx_contracts_dates ON contracts(start_date, end_date);
CREATE INDEX IF NOT EXISTS idx_transfers_player ON transfers(player_id);
CREATE INDEX IF NOT EXISTS idx_transfers_clubs ON transfers(from_club_id, to_club_id);
CREATE INDEX IF NOT EXISTS idx_transfers_date ON transfers(transfer_date);
CREATE INDEX IF NOT EXISTS idx_clubs_league ON clubs(league_id);
CREATE INDEX IF NOT EXISTS idx_leagues_country ON leagues(country);
CREATE INDEX IF NOT EXISTS idx_scrape_cache_url ON scrape_cache(url);
CREATE INDEX IF NOT EXISTS idx_scrape_cache_type ON scrape_cache(content_type);

-- Views for common queries
CREATE OR REPLACE VIEW active_contracts AS
SELECT 
    c.*,
    p.name AS player_name,
    cl.name AS club_name
FROM contracts c
JOIN players p ON c.player_id = p.id
LEFT JOIN clubs cl ON c.club_id = cl.id
WHERE c.end_date > NOW() OR c.end_date IS NULL;

CREATE OR REPLACE VIEW recent_transfers AS
SELECT 
    t.*,
    p.name AS player_name,
    cf.name AS from_club,
    ct.name AS to_club
FROM transfers t
JOIN players p ON t.player_id = p.id
LEFT JOIN clubs cf ON t.from_club_id = cf.id
LEFT JOIN clubs ct ON t.to_club_id = ct.id
WHERE t.transfer_date > NOW() - INTERVAL '365 days'
ORDER BY t.transfer_date DESC;

CREATE OR REPLACE VIEW data_quality_summary AS
SELECT 
    table_name,
    issue_type,
    severity,
    COUNT(*) as count,
    SUM(CASE WHEN resolved THEN 1 ELSE 0 END) as resolved_count
FROM data_quality
GROUP BY table_name, issue_type, severity
ORDER BY severity DESC, count DESC;
