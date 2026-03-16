# Football Data Infrastructure — Access Log

## Authorized Users

| User | Role | Workspace | Access Granted |
|------|------|-----------|----------------|
| Amaya Sinclair | CoS (Owner) | `/data/.openclaw/workspace-amaya/projects/football-data/` | 2026-03-16 07:09 CET |
| Enzo Rubio | AI Sporting Director | `/data/.openclaw/workspace-enzo/football-data/` (symlink) | 2026-03-16 07:16 CET |
| Tania Freeman | Chief Data Officer | `/data/.openclaw/workspace-enzo/tania-freeman/football-data/` (symlink) | 2026-03-16 07:16 CET |
| Bernie Brooks | Transfer Specialist | `/data/.openclaw/workspace-enzo/bernie-brooks/football-data/` (symlink) | 2026-03-16 07:16 CET |

## Access Method

All non-owner access is via **symbolic links** to the source directory.

- Changes made by any user affect the shared source
- Data is centralized (no duplication)
- All users see the same scraped data output

## Documentation Provided

- `/data/.openclaw/workspace-enzo/FOOTBALL_DATA_ACCESS.md` — Shared access guide
- `/data/.openclaw/workspace-enzo/tania-freeman/TOOLS.md` — Tania's guide
- `/data/.openclaw/workspace-enzo/bernie-brooks/TOOLS.md` — Bernie's guide

## Permissions

All users can:
- ✅ Run scrapers
- ✅ Read documentation
- ✅ View scraped data
- ✅ Access database schema

No restrictions currently in place (all files owned by `node` user).

---

**Last updated:** 2026-03-16 07:16 CET  
**By:** Amaya (CoS)
