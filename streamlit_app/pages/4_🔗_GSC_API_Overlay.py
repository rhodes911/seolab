import os
from pathlib import Path
import json
import datetime as dt
from typing import List, Dict

import streamlit as st
import pandas as pd
import sys
import frontmatter

try:
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
    from google.oauth2 import service_account
except Exception:
    build = None
    HttpError = Exception
    service_account = None

# Make sure we can import shared components and pipeline
try:
    from components import render_page_selector, ensure_modifier_session_defaults, render_modifier_controls
    from keyword_pipeline import expand_seeds, normalize_and_dedupe
except Exception:
    render_page_selector = None  # type: ignore
    ensure_modifier_session_defaults = lambda: None  # type: ignore
    def render_modifier_controls(key_prefix: str = ""):
        return ([], [], [])
    def expand_seeds(base, prefix_mods=None, suffix_mods=None, max_per_seed=20):
        return list(base or [])
    def normalize_and_dedupe(arr):
        seen = set(); out = []
        for a in arr or []:
            a2 = (a or "").strip()
            if a2 and a2 not in seen:
                seen.add(a2); out.append(a2)
        return out


def _repo_root() -> Path:
    # streamlit_app/pages/ -> repo root is two levels up
    return Path(__file__).resolve().parents[2]


def _default_sa_path() -> Path:
    return _repo_root() / ".secrets" / "gsc" / "service_account.json"


def _query_keyword(svc, site_url: str, start: str, end: str, keyword: str, operator: str = "equals") -> Dict:
    filt = {
        "dimension": "query",
        "operator": operator,
        "expression": keyword,
    }
    body = {
        "startDate": start,
        "endDate": end,
        "dimensions": ["query"],
        "dimensionFilterGroups": [{"filters": [filt]}],
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


def _download_bytes(data: List[Dict], fmt: str) -> bytes:
    if fmt == "json":
        return json.dumps(data, indent=2).encode("utf-8")
    # csv
    import io, csv
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=["keyword", "impressions", "clicks", "ctr", "position"])
    w.writeheader()
    for r in data:
        w.writerow(r)
    return buf.getvalue().encode("utf-8")


def main():
    st.set_page_config(page_title="GSC API Overlay (Service Account)", layout="wide")
    st.title("🔗 GSC API Overlay (Service Account)")
    st.caption(
        "Pull search performance from Google Search Console. Choose exact keywords or fetch the site's top queries, then export to JSON/CSV."
    )

    with st.expander("What am I looking at? (Beginner-friendly)", expanded=False):
        st.markdown(
            """
            This page talks to Google's Search Console Search Analytics API for your website (the property you own in Search Console).

            It returns how your site performed on Google Search for specific search terms (queries/keywords) over a time window:
            - Impressions: How many times your site appeared in Google search results for that query.
            - Clicks: How many times someone clicked your result for that query.
            - CTR: Click-through rate = Clicks ÷ Impressions (shown as a decimal here, e.g. 0.12 = 12%).
            - Avg position: The average topmost rank of your site when it appeared for that query. Lower is better (1 = top organic result).

            Notes for newcomers:
            - Data freshness: Search Console data is typically delayed by up to ~2 days. Very recent dates can look low or empty.
            - "Keyword list" mode checks queries you provide. "All queries" shows the site's top queries (limited by row limit).
            - "Match mode" = equals (exact query only) or contains (any query that includes your text). Start with equals for clean comparisons.
            - Domain vs URL property: A domain property looks like `sc-domain:example.com`. A URL property looks like `https://www.example.com/`.
            """
        )

    # Check deps
    if build is None or service_account is None:
        st.error("Google API libraries not available. Ensure 'google-api-python-client' and 'google-auth' are installed in the env.")
        return

    # Inputs
    colA, colB = st.columns([2, 2])
    with colA:
        site_url = st.text_input(
            "GSC property (siteUrl)",
            value="sc-domain:ellieedwardsmarketing.com",
            help=(
                "Where to read data from in Search Console.\n"
                "• Domain property: use sc-domain:yourdomain.com (covers all subdomains and protocols).\n"
                "• URL property: use the exact URL like https://www.yourdomain.com/"
            ),
        )
        mode = st.radio(
            "Mode",
            ["Keyword list", "All queries"],
            index=0,
            horizontal=True,
            help=(
                "Keyword list: check only the terms you provide.\n"
                "All queries: fetch the site's top queries for the period (limited by Row limit)."
            ),
        )
        operator = st.radio(
            "Match mode",
            ["equals", "contains"],
            index=0,
            horizontal=True,
            disabled=(mode == "All queries"),
            help=(
                "How to match your keywords against search queries.\n"
                "• equals: exact query only (recommended for clean comparisons).\n"
                "• contains: any query that includes your text (broader, can include variations)."
            ),
        )

    with colB:
        sa_path = st.text_input(
            "Service account key (JSON path)",
            value=str(_default_sa_path()),
            help=(
                "Absolute path to your Google Cloud service account key file (JSON).\n"
                "Keep this file secret; it's how this app authenticates to the API."
            ),
        )
        lookback = st.slider(
            "Lookback (days)",
            min_value=7,
            max_value=180,
            value=28,
            step=1,
            help=(
                "How far back to aggregate performance.\n"
                "Tip: GSC data is delayed ~2 days; very recent dates may appear low or empty."
            ),
        )
        row_limit = st.slider(
            "Row limit (for 'All queries')",
            min_value=10,
            max_value=5000,
            value=500,
            step=10,
            disabled=(mode != "All queries"),
            help=(
                "Maximum number of top queries to return for the site in the chosen period."
            ),
        )

    st.markdown("---")
    if mode == "Keyword list":
        st.subheader("Keywords")
        tab1, tab2 = st.tabs(["Page + Modifiers", "Manual keywords"])  # reuse site page selector + modifiers

        keywords: List[str] = []

        with tab1:
            # Default path to TinaCMS Ellie site
            ellie_root = r"C:\\Users\\rhode\\source\\repos\\EllieEdwardsMarketingLeadgenSite"
            if render_page_selector is None:
                st.info("Shared components are unavailable, switch to 'Manual keywords' tab.")
            else:
                selected_page, page_data = render_page_selector(ellie_root)

                # Try to load keywords directly from selected page frontmatter
                page_loaded_keywords: List[str] = []
                if selected_page and selected_page in page_data:
                    try:
                        with open(page_data[selected_page]["file_path"], "r", encoding="utf-8") as f:
                            post = frontmatter.load(f)
                        existing_keywords = post.metadata.get("keywords", []) or []
                        seo_section = post.metadata.get("seo", {}) or {}
                        seo_keywords = seo_section.get("keywords", []) or []
                        if seo_keywords:
                            page_loaded_keywords.extend([k for k in seo_keywords if isinstance(k, str)])
                        elif existing_keywords:
                            page_loaded_keywords.extend([k for k in existing_keywords if isinstance(k, str)])
                        if page_loaded_keywords:
                            st.caption(f"Loaded {len(page_loaded_keywords)} keyword(s) from page")
                    except Exception as e:
                        st.warning(f"Could not load page keywords: {e}")

                # Also support other sources consistent with Trends page
                def _load_settings_keywords(frontend_root: str):
                    try:
                        import json, os
                        seo_path = os.path.join(frontend_root, "content", "settings", "seo.json")
                        with open(seo_path, "r", encoding="utf-8") as f:
                            data = json.load(f)
                        pol = data.get("keywordPolicy") or {}
                        arr = (pol.get("includeAlways") or []) + (pol.get("includePreferred") or [])
                        seen = set(); out = []
                        for k in arr:
                            if isinstance(k, str) and k not in seen:
                                seen.add(k); out.append(k)
                        return out
                    except Exception:
                        return []

                # Pull candidate sets from session state populated by main app
                seed_keywords = [l.strip() for l in (st.session_state.get("seeds", "") or "").splitlines() if l.strip()]
                selected_keywords = st.session_state.get("selected", []) or []
                settings_keywords = _load_settings_keywords(ellie_root)

                col_top1, col_top2 = st.columns([2, 1])
                with col_top1:
                    scope = st.radio(
                        "Keyword source",
                        options=["Page (from selected)", "Page seeds", "Selected queries", "Site settings"],
                        index=(0 if page_loaded_keywords else (1 if seed_keywords else (2 if selected_keywords else 3))),
                        horizontal=True,
                        help="Choose where to start from. Then apply modifiers to generate variants.",
                        key="gsc_scope",
                    )
                with col_top2:
                    st.metric("Page keywords", len(page_loaded_keywords))
                    st.metric("Seeds loaded", len(seed_keywords))
                    st.metric("Selected queries", len(selected_keywords))
                    st.metric("Site settings", len(settings_keywords))

                if scope == "Page (from selected)":
                    base_keywords = page_loaded_keywords
                elif scope == "Page seeds":
                    base_keywords = seed_keywords
                elif scope == "Selected queries":
                    base_keywords = selected_keywords
                else:
                    base_keywords = settings_keywords

                st.markdown("---")
                st.caption("Add optional prefixes, suffixes, and locations. New items are saved for reuse across pages.")
                ensure_modifier_session_defaults()
                sel_prefixes, sel_suffixes, sel_locations = render_modifier_controls(key_prefix="gsc_")

                # Compute expanded final keyword list
                prefix = list(sel_prefixes or [])
                suffix = list(sel_suffixes or []) + list(sel_locations or [])
                banned = {"best", "affordable", "enterprise", "pricing", "price", "cheap", "cheapest"}
                prefix = [p for p in prefix if p.lower() not in banned]
                suffix = [s for s in suffix if s.lower() not in banned]

                expanded: List[str] = []
                if base_keywords:
                    try:
                        expanded = expand_seeds(base_keywords, prefix_mods=prefix, suffix_mods=suffix, max_per_seed=20)
                        expanded = normalize_and_dedupe(expanded)
                    except Exception as e:
                        st.warning(f"Expansion failed: {e}")

                final_keywords: List[str] = []
                include_base = st.checkbox("Include base keywords in final set", value=True, key="gsc_include_base")
                if include_base:
                    final_keywords.extend(base_keywords)
                final_keywords.extend([k for k in expanded if k not in final_keywords])

                with st.expander("Preview final keyword list", expanded=False):
                    st.caption(f"{len(final_keywords)} total → base: {len(base_keywords)} | expanded: {len(expanded)}")
                    st.write(final_keywords[:200])

                keywords = final_keywords

        with tab2:
            c1, c2 = st.columns([2, 1])
            with c1:
                kw_text = st.text_area(
                    "Enter keywords (one per line)",
                    height=150,
                    placeholder="e.g.\ncontent marketing\ncontent marketing surrey\nbrand strategy consultant",
                    help=(
                        "Paste a list of search terms (queries/keywords). Each line is checked in Search Console for the chosen period."
                    ),
                    key="gsc_kw_textarea",
                )
            with c2:
                up = st.file_uploader(
                    "or upload a text/CSV with a 'keyword' column",
                    type=["txt", "csv"],
                    help=(
                        "Upload a .txt with one keyword per line, or a .csv that contains a 'keyword' column."
                    ),
                    key="gsc_kw_upload",
                )
                uploaded_keywords: List[str] = []
                if up is not None:
                    try:
                        content = up.getvalue().decode("utf-8", errors="ignore")
                        if "," in content and "\n" in content:
                            import csv
                            rows = list(csv.DictReader(content.splitlines()))
                            uploaded_keywords = [ (r.get("keyword") or "").strip() for r in rows if (r.get("keyword") or "").strip() ]
                        else:
                            uploaded_keywords = [ln.strip() for ln in content.splitlines() if ln.strip()]
                    except Exception as e:
                        st.warning(f"Could not parse upload: {e}")

            typed_keywords = [ln.strip() for ln in (kw_text.splitlines() if kw_text else []) if ln.strip()]
            manual_keywords: List[str] = typed_keywords + [kw for kw in uploaded_keywords if kw not in typed_keywords]

            # Only override if user provided manual keywords in this tab
            if manual_keywords:
                keywords = manual_keywords
    else:
        keywords = []

    st.markdown("---")
    run = st.button(
        "Fetch metrics",
        type="primary",
        use_container_width=True,
        help=(
            "Runs the query against Google's Search Console API for the selected property and time range."
        ),
    )

    results: List[Dict] = []
    err_msg = None
    if run:
        # Resolve dates
        end = dt.date.today().isoformat()
        start = (dt.date.today() - dt.timedelta(days=int(lookback))).isoformat()
        # Validate
        if not os.path.isabs(sa_path):
            st.error("Please provide an absolute path to the service_account.json")
            return
        if not os.path.exists(sa_path):
            st.error("service_account.json not found at the provided path")
            return
        if mode == "Keyword list" and not keywords:
            st.warning("No keywords provided.")
            return

        try:
            creds = service_account.Credentials.from_service_account_file(sa_path, scopes=["https://www.googleapis.com/auth/webmasters.readonly"])
            svc = build("searchconsole", "v1", credentials=creds, cache_discovery=False)
            if mode == "All queries":
                body = {
                    "startDate": start,
                    "endDate": end,
                    "dimensions": ["query"],
                    "rowLimit": int(row_limit),
                    # Show most meaningful results first
                    "orderBy": [{"field": "clicks", "descending": True}],
                }
                resp = svc.searchanalytics().query(siteUrl=site_url, body=body).execute()
                for row in (resp.get("rows") or []):
                    key = (row.get("keys") or [None])[0]
                    results.append({
                        "keyword": key,
                        "impressions": int(row.get("impressions", 0)),
                        "clicks": int(row.get("clicks", 0)),
                        "ctr": float(row.get("ctr", 0.0)),
                        "position": float(row.get("position", 0.0)),
                    })
            else:
                for kw in keywords:
                    results.append(_query_keyword(svc, site_url, start, end, kw, operator=operator))
        except HttpError as e:
            msg = str(e)
            if "accessNotConfigured" in msg or "has not been used in project" in msg:
                err_msg = "Search Console API not enabled for this Cloud project. Enable it in Google Cloud Console and retry."
            elif getattr(e, "resp", None) and getattr(e.resp, "status", None) == 403:
                err_msg = "403 permission issue. Ensure the service account email is added as a user on the GSC property."
            elif getattr(e, "resp", None) and getattr(e.resp, "status", None) == 404:
                err_msg = "404 not found. Check siteUrl (use sc-domain:example.com for Domain properties)."
            else:
                err_msg = f"HttpError: {msg}"
        except Exception as e:
            err_msg = f"Error: {e}"

    # Render results
    if err_msg:
        st.error(err_msg)
    if results:
        df = pd.DataFrame(results)
        st.dataframe(df, use_container_width=True, hide_index=True)
        st.caption(
            "Columns: Impressions = times your site appeared; Clicks = visits from Google; CTR = Clicks/Impressions; Avg position = average rank (lower is better)."
        )
        colx, coly = st.columns(2)
        with colx:
            st.download_button(
                "Download JSON",
                data=_download_bytes(results, "json"),
                file_name="gsc_overlay.json",
                mime="application/json",
                use_container_width=True,
            )
        with coly:
            st.download_button(
                "Download CSV",
                data=_download_bytes(results, "csv"),
                file_name="gsc_overlay.csv",
                mime="text/csv",
                use_container_width=True,
            )


if __name__ == "__main__":
    main()
