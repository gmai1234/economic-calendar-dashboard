# economic-calendar-dashboard

Economic release calendar data collector (Phase 1: BLS ICS).

## Architecture

- `scripts/collect_data.py` — Fetches BLS Economic News Release Schedule (iCalendar ICS), parses VEVENTs, filters future events (up to 180 days), outputs `calendar_data.js`
- `.github/workflows/update.yml` — GitHub Actions cron, twice daily (08:00 + 20:00 KST)
- `calendar_data.js` — Output: `window.CALENDAR_DATA = {releases, sources, collected_at, count}`
- GitHub Pages serves `calendar_data.js` for client-side consumption by [market-dashboard](https://github.com/gmai1234/market-dashboard)

## Data Source (Phase 1)

- BLS (Bureau of Labor Statistics) ICS calendar: <https://www.bls.gov/schedule/news_release/bls.ics>
  - CPI, PPI, NFP, ECI, JOLTS, etc.
- Phase 2 후보: BEA (PCE/GDP), Fed (FOMC), Treasury (auctions)

## Manual Run

`Actions` tab → `update` workflow → `Run workflow`.
