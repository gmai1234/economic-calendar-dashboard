#!/usr/bin/env python3
"""
Economic Calendar Dashboard Data Collector — Phase 1: BLS ICS
Fetches BLS Economic News Release Schedule (ICS), parses VEVENTs, outputs calendar_data.js.
"""

import json
import sys
import time
import traceback
import urllib.request
from datetime import datetime, date, timezone, timedelta

KST = timezone(timedelta(hours=9))
OUTPUT_PATH = "calendar_data.js"
BLS_ICS_URL = "https://www.bls.gov/schedule/news_release/bls.ics"
MAX_EVENTS = 50
DAYS_AHEAD = 180


def fetch_text(url, timeout=30, max_retries=3):
    """Fetch with Mozilla-like UA + retry on transient errors."""
    last_err = None
    for attempt in range(max_retries):
        try:
            req = urllib.request.Request(url, headers={
                "User-Agent": "Mozilla/5.0 (compatible; economic-calendar-dashboard/1.0; +https://github.com/gmai1234)",
                "Accept": "text/calendar, text/html, */*",
                "Accept-Language": "en-US,en;q=0.9",
            })
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                code = resp.getcode()
                if code >= 500:
                    raise RuntimeError(f"HTTP {code}")
                return resp.read().decode("utf-8", errors="ignore")
        except Exception as e:
            last_err = e
            print(f"  attempt {attempt+1}/{max_retries} failed: {type(e).__name__}: {e}", file=sys.stderr, flush=True)
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
    raise last_err


def parse_ics(ics_text):
    events = []
    cur = None
    for raw in ics_text.splitlines():
        line = raw.rstrip('\r').strip()
        if line == "BEGIN:VEVENT":
            cur = {}
        elif line == "END:VEVENT":
            if cur:
                events.append(cur)
            cur = None
        elif cur is not None:
            if ':' not in line:
                continue
            key_part, val = line.split(':', 1)
            key = key_part.split(';', 1)[0]
            cur[key] = val
    return events


def parse_dt(dt_str):
    s = (dt_str or '').rstrip('Z').strip()
    if not s:
        return None
    try:
        if 'T' in s:
            return datetime.strptime(s[:15], '%Y%m%dT%H%M%S')
        else:
            return datetime.strptime(s[:8], '%Y%m%d')
    except (ValueError, IndexError):
        return None


def normalize_summary(s):
    return (s or '').replace('\\,', ',').replace('\\;', ';').replace('\\n', ' ').strip()


def filter_future(events, today, horizon, max_count):
    result = []
    for e in events:
        dtstart_raw = e.get('DTSTART', '')
        dt = parse_dt(dtstart_raw)
        if not dt:
            continue
        if dt.date() < today:
            continue
        if dt.date() > horizon:
            continue
        result.append({
            'date': dt.strftime('%Y-%m-%d'),
            'time_et': dt.strftime('%H:%M') if 'T' in dtstart_raw else None,
            'summary': normalize_summary(e.get('SUMMARY', '')),
            'source': 'BLS',
            'uid': e.get('UID', ''),
            'days_until': (dt.date() - today).days,
        })
    result.sort(key=lambda x: (x['date'], x.get('time_et') or '00:00'))
    return result[:max_count]


def main():
    print(f"Fetching BLS ICS calendar: {BLS_ICS_URL}", flush=True)
    try:
        ics_text = fetch_text(BLS_ICS_URL)
    except Exception as e:
        print(f"\nFATAL: BLS ICS fetch failed: {type(e).__name__}: {e}", file=sys.stderr, flush=True)
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)
    print(f"  Fetched {len(ics_text):,} bytes", flush=True)

    events = parse_ics(ics_text)
    print(f"  Parsed {len(events)} VEVENTs", flush=True)

    today = date.today()
    horizon = today + timedelta(days=DAYS_AHEAD)
    future = filter_future(events, today, horizon, MAX_EVENTS)
    print(f"  Future events (today..+{DAYS_AHEAD}d): {len(future)}", flush=True)

    if not future:
        print(f"WARNING: No future events found. Today: {today}", file=sys.stderr, flush=True)

    payload = {
        'releases': future,
        'sources': {'BLS': BLS_ICS_URL},
        'collected_at': datetime.now(KST).strftime('%Y-%m-%dT%H:%M:%S+09:00'),
        'count': len(future),
    }

    js_content = f'window.CALENDAR_DATA = {json.dumps(payload, ensure_ascii=False, indent=2)};\n'
    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        f.write(js_content)

    print(f"\nNext 10 releases:", flush=True)
    for r in future[:10]:
        t = r['time_et'] or '----'
        print(f"  {r['date']} {t}  D-{r['days_until']:3}  {r['summary']}", flush=True)

    print(f"\nWrote {OUTPUT_PATH} ({len(js_content):,} bytes)", flush=True)


if __name__ == '__main__':
    main()
