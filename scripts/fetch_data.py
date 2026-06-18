"""Fetch GitHub Top 50 data and save to data/ directory.

Usage: python scripts/fetch_data.py

Requires: GITHUB_TOKEN env var (used as HTTP auth to avoid rate limits)
"""

import json, os, sys, time, logging
from datetime import date
try:
    import requests
except ImportError:
    print("Missing 'requests'. Run: pip install requests")
    sys.exit(1)

# Suppress request-level logging (prevents accidental header/token leak)
logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')
UA = "Mozilla/5.0 (oss-top50-bot)"
TOKEN = os.environ.get("GITHUB_TOKEN", "")

def fetch(query, sort="stars", order="desc", per_page=50):
    """Fetch repos from GitHub Search API"""
    url = "https://api.github.com/search/repositories"
    headers = {"User-Agent": UA, "Accept": "application/vnd.github.v3+json"}
    if TOKEN:
        headers["Authorization"] = f"token {TOKEN}"

    params = {"q": query, "sort": sort, "order": order, "per_page": per_page}
    resp = requests.get(url, headers=headers, params=params, timeout=30)

    if resp.status_code == 403:
        print("Rate limited. Waiting 60s...")
        time.sleep(60)
        resp = requests.get(url, headers=headers, params=params, timeout=30)

    resp.raise_for_status()
    return resp.json()

def compress(items):
    """Keep only the fields needed for the site"""
    today = date.today()
    compressed = []
    for r in items:
        topics = r.get('topics', []) or []
        lic = r.get('license', {}) or {}
        created = r.get('created_at', '')[:10]
        pushed = r.get('pushed_at', '')[:10]
        
        # Calculate monthly star growth
        try:
            from datetime import datetime
            created_dt = datetime.strptime(created, '%Y-%m-%d')
            months = max(1, (today - created_dt.date()).days / 30.0)
            stars_month = round(r.get('stargazers_count', 0) / months)
        except (ValueError, AttributeError):
            stars_month = 0

        compressed.append({
            'name': r.get('full_name', ''),
            'url': r.get('html_url', ''),
            'desc': r.get('description', '') or '',
            'stars': r.get('stargazers_count', 0),
            'forks': r.get('forks_count', 0),
            'lang': r.get('language', '') or 'Other',
            'created': created,
            'pushed': pushed,
            'issues': r.get('open_issues_count', 0),
            'topics': topics[:10],
            'license': lic.get('spdx_id', ''),
            'stars_month': stars_month
        })
    return compressed

def main():
    print("Fetching all-time Top 50...")
    alltime = fetch("stars:>10000", sort="stars", per_page=50)
    compressed_all = compress(alltime['items'])
    path_all = os.path.join(DATA_DIR, 'alltime.json')
    # Preserve existing desc_cn translations
    if os.path.exists(path_all):
        existing = json.load(open(path_all, 'r', encoding='utf-8'))
        existing_map = {r['name']: {'desc_cn': r.get('desc_cn', ''), 'source': r.get('desc_cn_source', '')} for r in existing}
        for r in compressed_all:
            if r['name'] in existing_map and existing_map[r['name']]['desc_cn']:
                r['desc_cn'] = existing_map[r['name']]['desc_cn']
                r['desc_cn_source'] = existing_map[r['name']]['source']
    with open(path_all, 'w', encoding='utf-8') as f:
        json.dump(compressed_all, f, ensure_ascii=False, indent=2)
    print(f"  Saved {len(compressed_all)} repos to {path_all}")

    print("Fetching recent Top 50 (2026-01-01 to today)...")
    today = date.today().isoformat()
    recent = fetch(f"created:2026-01-01..{today}", sort="stars", per_page=50)
    compressed_rec = compress(recent['items'])
    path_rec = os.path.join(DATA_DIR, 'recent.json')
    if os.path.exists(path_rec):
        existing = json.load(open(path_rec, 'r', encoding='utf-8'))
        existing_map = {r['name']: r.get('desc_cn', '') for r in existing}
        for r in compressed_rec:
            if r['name'] in existing_map and existing_map[r['name']]:
                r['desc_cn'] = existing_map[r['name']]
    with open(path_rec, 'w', encoding='utf-8') as f:
        json.dump(compressed_rec, f, ensure_ascii=False, indent=2)
    print(f"  Saved {len(compressed_rec)} repos to {path_rec}")

if __name__ == '__main__':
    main()
