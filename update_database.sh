#!/bin/bash
# Auto-update football database
# Run via cron: weekly full refresh

set -e

PROJECT_DIR="/data/.openclaw/workspace-amaya/projects/football-data"
LOG_FILE="$PROJECT_DIR/data/update_log.txt"

echo "[$(date)] Starting database update..." | tee -a "$LOG_FILE"

# 1. Run authenticated Transfermarkt scrape (47 leagues)
cd "$PROJECT_DIR"
python3 scrapers/full_scrape_auth.py 2>&1 | tee -a "$LOG_FILE"

# 2. Extract club names from results
python3 scrapers/extract_club_names.py 2>&1 | tee -a "$LOG_FILE"

# 3. Import Wikipedia fallback data
python3 database/import_wikipedia_data.py 2>&1 | tee -a "$LOG_FILE"

# 4. Fresh import to database
python3 database/fresh_import.py 2>&1 | tee -a "$LOG_FILE"

echo "[$(date)] Database update complete" | tee -a "$LOG_FILE"

# Send summary to Carlos
CLUB_COUNT=$(sqlite3 "$PROJECT_DIR/data/football_data.db" "SELECT COUNT(*) FROM clubs")
echo "✅ Football database updated: $CLUB_COUNT clubs"
