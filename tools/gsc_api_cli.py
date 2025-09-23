import argparse
import csv
import json
import sys
import datetime as dt
from pathlib import Path
from typing import Iterable, List, Dict

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2 import service_account


SCOPES = ["https://www.googleapis.com/auth/webmasters.readonly"]
DEFAULT_SA = Path(r"C:\\Users\\rhode\\source\\repos\\seolab\\.secrets\\gsc\\service_account.json")
DEFAULT_SITE = "sc-domain:ellieedwardsmarketing.com"


def read_keywords(args) -> List[str]:
    if args.keywords:
        return [k.strip() for k in args.keywords if k.strip()]
    if args.keywords_file:
        p = Path(args.keywords_file)
        text = p.read_text(encoding="utf-8")
        # One keyword per line; also support simple CSV with header 'keyword'
        if "," in text and "\n" in text:
            # try CSV
            out = []
            for row in csv.DictReader(text.splitlines()):
                kw = (row.get("keyword") or "").strip()
                if kw:
                    out.append(kw)
            if out:
                return out
        # fallback: newline list
        return [line.strip() for line in text.splitlines() if line.strip()]
    return []


def query_keyword(svc, site_url: str, start: str, end: str, keyword: str) -> Dict:
    body = {
        "startDate": start,
        "endDate": end,
        "dimensions": ["query"],
        "dimensionFilterGroups": [
            {
                "filters": [
                    {"dimension": "query", "operator": "equals", "expression": keyword}
                ]
            }
        ],
        "rowLimit": 1,
    }
    resp = svc.searchanalytics().query(siteUrl=site_url, body=body).execute()
    rows = resp.get("rows", [])
    if not rows:
        return {
            "keyword": keyword,
            "impressions": 0,
            "clicks": 0,
            "ctr": 0.0,
            "position": None,
        }
    row = rows[0]
    return {
        "keyword": keyword,
        "impressions": int(row.get("impressions", 0)),
        "clicks": int(row.get("clicks", 0)),
        "ctr": float(row.get("ctr", 0.0)),
        "position": float(row.get("position", 0.0)),
    }


def to_csv(rows: Iterable[Dict], out_file: Path | None):
    fieldnames = ["keyword", "impressions", "clicks", "ctr", "position"]
    if out_file:
        f = out_file.open("w", newline="", encoding="utf-8")
        close = True
    else:
        f = sys.stdout
        close = False
    try:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in rows:
            w.writerow(r)
    finally:
        if close:
            f.close()


def to_json(rows: Iterable[Dict], out_file: Path | None):
    data = list(rows)
    text = json.dumps(data, indent=2)
    if out_file:
        out_file.write_text(text, encoding="utf-8")
    else:
        print(text)


def main():
    parser = argparse.ArgumentParser(description="Query GSC metrics for keywords via Service Account")
    parser.add_argument("--site", default=DEFAULT_SITE, help="GSC siteUrl e.g. sc-domain:example.com")
    parser.add_argument("--key", default=str(DEFAULT_SA), help="Path to service_account.json")
    grp = parser.add_mutually_exclusive_group(required=True)
    grp.add_argument("--keywords", nargs="*", help="Keywords to query (space-separated)")
    grp.add_argument("--keywords-file", help="Path to a file with keywords (one per line, or CSV with 'keyword' column)")
    date = parser.add_mutually_exclusive_group()
    date.add_argument("--days", type=int, default=28, help="Lookback window in days (default 28)")
    date.add_argument("--start")
    date.add_argument("--end")
    parser.add_argument("--format", choices=["json", "csv"], default="json")
    parser.add_argument("-o", "--output", help="Output file path (default stdout)")

    args = parser.parse_args()

    sa_path = Path(args.key)
    if not sa_path.exists():
        parser.error(f"Service account file not found: {sa_path}")

    if args.start and args.end:
        start, end = args.start, args.end
    else:
        end = dt.date.today()
        start = end - dt.timedelta(days=args.days)
        start, end = start.isoformat(), end.isoformat()

    kws = read_keywords(args)
    if not kws:
        parser.error("No keywords provided. Use --keywords or --keywords-file")

    creds = service_account.Credentials.from_service_account_file(str(sa_path), scopes=SCOPES)
    svc = build("searchconsole", "v1", credentials=creds, cache_discovery=False)

    results: List[Dict] = []
    try:
        for kw in kws:
            results.append(query_keyword(svc, args.site, start, end, kw))
    except HttpError as e:
        msg = str(e)
        if "accessNotConfigured" in msg or "has not been used in project" in msg:
            print("ERROR: Search Console API not enabled for this Cloud project.")
            print("Fix: Enable it at https://console.developers.google.com/apis/api/searchconsole.googleapis.com/overview for your project, then retry.")
        elif "insufficientPermissions" in msg or e.resp.status == 403:
            print("ERROR: 403 permission issue. Ensure the service account is added as a user on the GSC property:", args.site)
        elif e.resp.status == 404:
            print("ERROR: 404 not found. Check siteUrl (use sc-domain:example.com for Domain properties).")
        else:
            print("HttpError:", msg)
        raise

    out_path = Path(args.output) if args.output else None
    if args.format == "csv":
        to_csv(results, out_path)
    else:
        to_json(results, out_path)


if __name__ == "__main__":
    main()
