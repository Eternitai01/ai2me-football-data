# Football Database Update Schedule

**Auto-update configured:** ✅

---

## Schedule

**Weekly Full Refresh:**
- **When:** Every Sunday at 3:00 AM CET
- **What:** Scrape all 47 leagues, update all 4,331+ clubs
- **Duration:** ~2-3 hours (8-second delay per club)
- **Notification:** Automatic summary sent to Carlos

**Cron Expression:** `0 3 * * 0` (3 AM every Sunday)

---

## What Gets Updated

1. **Transfermarkt scrape** (authenticated)
   - All 47 leagues
   - Club names, URLs, league affiliations
   
2. **Wikipedia fallback** (for failed leagues)
   - Alternative source for missing data
   
3. **Database import**
   - Fresh import to SQLite
   - Preserves historical data
   - Updates `last_updated` timestamps

---

## Manual Update (On-Demand)

If you need to update before Sunday:

```bash
bash /data/.openclaw/workspace-amaya/projects/football-data/update_database.sh
```

Or ask me: "Update football database now"

---

## Update Log

Check recent updates:
```bash
tail -50 /data/.openclaw/workspace-amaya/projects/football-data/data/update_log.txt
```

---

## Data Freshness

Check when database was last updated:

```bash
sqlite3 /data/.openclaw/workspace-amaya/projects/football-data/data/football_data.db \
  "SELECT MAX(last_updated) FROM clubs"
```

---

## Cost

**$0/month** — Uses existing VPS resources, no API fees

---

**Status:** ✅ Auto-update active (weekly refresh)  
**Next update:** Sunday, March 23, 2026 at 3:00 AM CET
