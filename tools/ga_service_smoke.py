import os
import json
import argparse
import datetime as dt
from typing import List

from google.oauth2 import service_account
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import DateRange, Dimension, Metric, RunReportRequest, OrderBy


def _repo_root() -> str:
    # repo root = parent of the tools directory
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _default_sa_path() -> str:
    return os.path.join(_repo_root(), ".secrets", "ga", "service_account.json")


def run_report(property_id: str, days: int, row_limit: int, sa_path: str) -> List[dict]:
    if not os.path.isabs(sa_path):
        raise RuntimeError("Please provide an absolute path to the GA service_account.json")
    if not os.path.exists(sa_path):
        raise FileNotFoundError("service_account.json not found at provided path")

    creds = service_account.Credentials.from_service_account_file(
        sa_path,
        scopes=["https://www.googleapis.com/auth/analytics.readonly"],
    )
    client = BetaAnalyticsDataClient(credentials=creds)

    # End 2 days ago to avoid processing lag
    end_date = dt.date.today() - dt.timedelta(days=2)
    start_date = end_date - dt.timedelta(days=int(days))

    request = RunReportRequest(
        property=f"properties/{property_id}",
        dimensions=[Dimension(name="pagePath")],
        metrics=[
            Metric(name="sessions"),
            Metric(name="totalUsers"),
            Metric(name="engagedSessions"),
            Metric(name="conversions"),
        ],
        date_ranges=[DateRange(start_date=start_date.isoformat(), end_date=end_date.isoformat())],
        limit=int(row_limit),
        order_bys=[OrderBy(metric=OrderBy.MetricOrderBy(metric_name="sessions"), desc=True)],
    )
    resp = client.run_report(request)

    rows = []
    for r in resp.rows:
        dim_vals = [d.value for d in r.dimension_values]
        # metric_values entries are strings; parse safely
        met_vals = [m.value for m in r.metric_values]
        def _to_int(s):
            try:
                return int(float(s))
            except Exception:
                return 0
        def _to_float(s):
            try:
                return float(s)
            except Exception:
                return 0.0
        rows.append({
            "pagePath": dim_vals[0] if dim_vals else None,
            "sessions": _to_int(met_vals[0] if len(met_vals) > 0 else "0"),
            "totalUsers": _to_int(met_vals[1] if len(met_vals) > 1 else "0"),
            "engagedSessions": _to_int(met_vals[2] if len(met_vals) > 2 else "0"),
            "conversions": _to_float(met_vals[3] if len(met_vals) > 3 else "0"),
        })
    return rows


def main():
    p = argparse.ArgumentParser(description="GA4 Data API smoke test (Service Account)")
    p.add_argument("--property-id", required=True, help="GA4 Property ID (number)")
    p.add_argument("--days", type=int, default=28)
    p.add_argument("--row-limit", type=int, default=25)
    p.add_argument("--sa-path", default=_default_sa_path())
    args = p.parse_args()

    try:
        rows = run_report(property_id=args.property_id, days=args.days, row_limit=args.row_limit, sa_path=args.sa_path)
        print(json.dumps({"rows": rows}, indent=2))
    except Exception as e:
        print(f"ERROR: {e}")
        raise


if __name__ == "__main__":
    main()
