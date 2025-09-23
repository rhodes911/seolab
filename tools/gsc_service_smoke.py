import argparse
import json
import datetime as dt
from pathlib import Path

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2 import service_account


SCOPES = ["https://www.googleapis.com/auth/webmasters.readonly"]
DEFAULT_SA = Path(r"C:\\Users\\rhode\\source\\repos\\seolab\\.secrets\\gsc\\service_account.json")
DEFAULT_SITE = "sc-domain:ellieedwardsmarketing.com"


def main(sa_file: Path, site_url: str):
    if not sa_file.exists():
        raise FileNotFoundError(f"Service account file not found: {sa_file}")

    creds = service_account.Credentials.from_service_account_file(str(sa_file), scopes=SCOPES)
    svc = build("searchconsole", "v1", credentials=creds, cache_discovery=False)

    end = dt.date.today().isoformat()
    start = (dt.date.today() - dt.timedelta(days=28)).isoformat()
    body = {"startDate": start, "endDate": end, "dimensions": ["query"], "rowLimit": 10}

    try:
        resp = svc.searchanalytics().query(siteUrl=site_url, body=body).execute()
        print(json.dumps(resp, indent=2))
    except HttpError as e:
        # Provide friendly hints for common misconfigurations
        msg = str(e)
        if "accessNotConfigured" in msg or "has not been used in project" in msg:
            print("ERROR: Search Console API not enabled for this Cloud project.")
            print("Fix: Open https://console.developers.google.com/apis/api/searchconsole.googleapis.com/overview and ensure it is enabled for your project.")
        elif "insufficientPermissions" in msg or e.resp.status == 403:
            print("ERROR: 403 permission issue. Ensure the service account email is added as a user on the GSC property: ", site_url)
        elif e.resp.status == 404:
            print("ERROR: 404 not found. Check the siteUrl is correct (use sc-domain:example.com for Domain properties).")
        else:
            print("HttpError:", msg)
        raise


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="GSC Service Account smoke test")
    parser.add_argument("--site", default=DEFAULT_SITE, help="GSC siteUrl, e.g., sc-domain:example.com")
    parser.add_argument("--key", default=str(DEFAULT_SA), help="Path to service_account.json")
    args = parser.parse_args()

    main(Path(args.key), args.site)
