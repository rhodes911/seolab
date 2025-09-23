from __future__ import annotations
import argparse
import csv
import json
import os
import sys
from typing import Any, Dict, List

import os
import sys as _sys

# Ensure repository root is on sys.path so 'plugins' can be imported when running from tools/
_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_REPO_ROOT = os.path.abspath(os.path.join(_THIS_DIR, os.pardir))
if _REPO_ROOT not in _sys.path:
    _sys.path.insert(0, _REPO_ROOT)

from plugins.google_trends import GoogleTrendsPlugin


def read_keywords(path: str) -> List[str]:
    with open(path, "r", encoding="utf-8") as f:
        txt = f.read().strip()
    if not txt:
        return []
    # Try JSON list first
    try:
        data = json.loads(txt)
        if isinstance(data, list):
            return [str(x).strip() for x in data if str(x).strip()]
    except Exception:
        pass
    # Fallback to newline-delimited
    return [line.strip() for line in txt.splitlines() if line.strip()]


def write_csv(path: str, data: Dict[str, Dict[str, Any]]):
    rows = []
    for k, v in data.items():
        row = {"keyword": k}
        row.update(v or {})
        rows.append(row)
    if not rows:
        # ensure header
        rows = [{"keyword": ""}]
    fieldnames = sorted({fn for r in rows for fn in r.keys()}, key=lambda s: (s != "keyword", s))
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in rows:
            w.writerow(r)


def main():
    ap = argparse.ArgumentParser(description="Run Google Trends plugin on a list of keywords.")
    ap.add_argument("--keywords-file", required=True, help="Path to JSON array or newline-delimited text of keywords")
    ap.add_argument("--locale", default="gb-en", help="Locale (e.g., gb-en, us-en)")
    ap.add_argument("--date-range", default="today 12-m", help="Pytrends timeframe (e.g., 'today 12-m', 'today 5-y')")
    ap.add_argument("--no-cache", action="store_true", help="Bypass local cache")
    ap.add_argument("--out", default=None, help="Output file (.json or .csv). Default prints JSON to stdout")
    args = ap.parse_args()

    if not os.path.isfile(args.keywords_file):
        print(f"keywords file not found: {args.keywords_file}", file=sys.stderr)
        return 2

    keywords = read_keywords(args.keywords_file)
    ctx = {"locale": args.locale, "date_range": args.date_range, "no_cache": bool(args.no_cache)}
    plugin = GoogleTrendsPlugin()
    result = plugin.enrich_many(keywords, context=ctx)

    if args.out:
        out_lower = args.out.lower()
        if out_lower.endswith(".csv"):
            write_csv(args.out, result)
        else:
            with open(args.out, "w", encoding="utf-8") as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
        print(args.out)
        return 0
    else:
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0


if __name__ == "__main__":
    sys.exit(main())
