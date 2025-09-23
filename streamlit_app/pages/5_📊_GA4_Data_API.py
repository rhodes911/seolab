import os
import datetime as dt
from typing import List, Dict

import streamlit as st
import pandas as pd

try:
    from google.oauth2 import service_account
    from google.analytics.data_v1beta import BetaAnalyticsDataClient
    from google.analytics.data_v1beta.types import DateRange, Dimension, Metric, RunReportRequest, OrderBy
except Exception:
    service_account = None
    BetaAnalyticsDataClient = None
    DateRange = Dimension = Metric = RunReportRequest = OrderBy = None  # type: ignore


def _repo_root() -> str:
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # streamlit_app/pages -> streamlit_app


def _default_sa_path() -> str:
    # repo root is one level above streamlit_app
    repo = os.path.dirname(_repo_root())
    return os.path.join(repo, ".secrets", "ga", "service_account.json")


def _run_ga4_report(property_id: str, days: int, end_offset_days: int, row_limit: int, sa_path: str) -> List[Dict]:
    if service_account is None or BetaAnalyticsDataClient is None:
        raise RuntimeError("Google Analytics client libraries not available. Install 'google-analytics-data' and 'google-auth'.")
    if not os.path.isabs(sa_path):
        raise RuntimeError("Please provide an absolute path to the GA service_account.json")
    if not os.path.exists(sa_path):
        raise FileNotFoundError("service_account.json not found at provided path")

    creds = service_account.Credentials.from_service_account_file(
        sa_path, scopes=["https://www.googleapis.com/auth/analytics.readonly"]
    )
    client = BetaAnalyticsDataClient(credentials=creds)

    # End some days ago to avoid GA processing lag
    end_date = dt.date.today() - dt.timedelta(days=int(end_offset_days))
    start_date = end_date - dt.timedelta(days=int(days))

    req = RunReportRequest(
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
    resp = client.run_report(req)

    rows: List[Dict] = []
    for r in (resp.rows or []):
        dim_vals = [d.value for d in r.dimension_values]
        met_vals = [m.value for m in r.metric_values]
        def _to_int(s: str) -> int:
            try:
                return int(float(s))
            except Exception:
                return 0
        def _to_float(s: str) -> float:
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


def _download_bytes(data: List[Dict], fmt: str) -> bytes:
    if fmt == "json":
        import json
        return json.dumps(data, indent=2).encode("utf-8")
    # csv
    import io, csv
    buf = io.StringIO()
    if not data:
        return "".encode("utf-8")
    fieldnames = list(data[0].keys())
    w = csv.DictWriter(buf, fieldnames=fieldnames)
    w.writeheader()
    for r in data:
        w.writerow(r)
    return buf.getvalue().encode("utf-8")


def main():
    st.set_page_config(page_title="GA4 Data API (Service Account)", layout="wide")
    st.title("📊 GA4 Data API (Service Account)")
    st.caption("See top pages by sessions/users via GA4. Export JSON/CSV. Service Account only.")

    with st.expander("What am I looking at? (Beginner-friendly)", expanded=False):
        st.markdown(
            """
            This page queries your GA4 property using the Google Analytics Data API and a service account key.

            It returns page-level engagement for a recent window:
            - Sessions: Visits (groups of interactions) on the site.
            - Total Users: Unique users who visited.
            - Engaged Sessions: Sessions with meaningful engagement (GA4 definition).
            - Conversions: Total conversions attributed in that window.

            Notes:
            - Data freshness: GA4 can lag, so we end the window a couple of days ago for stability.
            - Property ID is numeric (e.g. 500316527); don't confuse it with Measurement ID (G-XXXX...).
            """
        )

    if service_account is None or BetaAnalyticsDataClient is None:
        st.error("Google Analytics libraries not available. Install 'google-analytics-data' and 'google-auth' in the env.")
        return

    c1, c2 = st.columns([2, 2])
    with c1:
        prop_id = st.text_input(
            "GA4 Property ID",
            value="500316527",
            help="Numeric Property ID from GA Admin → Property settings.",
        )
        days = st.slider(
            "Lookback (days)", 7, 180, 28, 1,
            help="How far back to aggregate performance (ends a few days ago for freshness).",
        )
        end_offset = st.slider(
            "End offset (days ago)", 0, 7, 2, 1,
            help="End the window this many days ago to avoid GA processing lag.",
        )
    with c2:
        sa_path = st.text_input(
            "Service account key (JSON path)",
            value=_default_sa_path(),
            help="Absolute path to service_account.json for GA4. Keep this file secret.",
        )
        row_limit = st.slider(
            "Row limit",
            min_value=10, max_value=5000, value=50, step=10,
            help="Maximum number of top pages to return.",
        )

    st.markdown("---")
    run = st.button(
        "Fetch GA4 metrics",
        type="primary",
        use_container_width=True,
        help="Runs the query against the GA4 Data API for the selected property and date window.",
    )

    results: List[Dict] = []
    err: str | None = None
    if run:
        try:
            results = _run_ga4_report(prop_id.strip(), int(days), int(end_offset), int(row_limit), sa_path.strip())
        except Exception as e:
            msg = str(e)
            if "Permission" in msg or "403" in msg:
                err = "403 permission issue. Ensure the service account email is added as a user on the GA4 property."
            elif "not found" in msg or "404" in msg:
                err = "Property not found. Double-check the numeric GA4 Property ID."
            elif "ENOTFOUND" in msg or "Name or service not known" in msg:
                err = "Network/DNS issue. Check your connection."
            else:
                err = msg

    if err:
        st.error(err)
    if results:
        df = pd.DataFrame(results)
        st.dataframe(df, use_container_width=True, hide_index=True)
        st.caption("Columns: pagePath = URL path; Sessions = visits; Users = unique visitors; Engaged Sessions = engaged; Conversions = total.")
        cx, cy = st.columns(2)
        with cx:
            st.download_button(
                "Download JSON",
                data=_download_bytes(results, "json"),
                file_name="ga4_top_pages.json",
                mime="application/json",
                use_container_width=True,
            )
        with cy:
            st.download_button(
                "Download CSV",
                data=_download_bytes(results, "csv"),
                file_name="ga4_top_pages.csv",
                mime="text/csv",
                use_container_width=True,
            )


if __name__ == "__main__":
    main()
