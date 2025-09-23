from __future__ import annotations
import os
import sys
import json
import streamlit as st
import frontmatter

# Ensure repository root is on sys.path to import top-level packages like 'plugins'
_REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir))
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

try:
    from plugins.google_trends import GoogleTrendsPlugin  # type: ignore
except Exception:
    GoogleTrendsPlugin = None

st.set_page_config(page_title="Google Trends", page_icon="📈", layout="wide")
st.title("Google Trends 📈")
st.caption("Use the page selector to load keywords, or use your current Seeds/Selected queries.")

# Reuse the shared page selector from components
from components import render_page_selector

# Default path to TinaCMS site (same as in app.py)
ellie_root = r"C:\\Users\\rhode\\source\\repos\\EllieEdwardsMarketingLeadgenSite"

selected_page, page_data = render_page_selector(ellie_root)

# Attempt to load keywords directly from the selected page
page_loaded_keywords = []
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

def _load_settings_keywords(frontend_root: str):
    try:
        seo_path = os.path.join(frontend_root, "content", "settings", "seo.json")
        with open(seo_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        pol = data.get("keywordPolicy") or {}
        arr = (pol.get("includeAlways") or []) + (pol.get("includePreferred") or [])
        # dedupe preserve order
        seen = set()
        out = []
        for k in arr:
            if isinstance(k, str) and k not in seen:
                seen.add(k)
                out.append(k)
        return out
    except Exception:
        return []

# Pull candidate sets from session state populated by app.py
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
    )
with col_top2:
    st.metric("Page keywords", len(page_loaded_keywords))
    st.metric("Seeds loaded", len(seed_keywords))
    st.metric("Selected queries", len(selected_keywords))
    st.metric("Site settings", len(settings_keywords))

if scope == "Page (from selected)":
    keywords = page_loaded_keywords
elif scope == "Page seeds":
    keywords = seed_keywords
elif scope == "Selected queries":
    keywords = selected_keywords
else:
    keywords = settings_keywords

tf_col1, tf_col2, tf_col3 = st.columns([1, 1, 1])
with tf_col1:
    timeframe = st.selectbox(
        "Timeframe",
        options=["today 12-m", "today 5-y", "today 3-m", "today 1-m"],
        index=0,
    )
with tf_col2:
    locale = st.text_input("Locale", value="gb-en")
with tf_col3:
    no_cache = st.checkbox("No cache", value=False)

run = st.button("Fetch Google Trends", type="primary")

if run:
    if not keywords:
        st.warning("No keywords available. In the main app, load a page to populate Seeds or generate/select queries.")
    elif GoogleTrendsPlugin is None:
        st.error("Google Trends plugin unavailable. Ensure 'pytrends' is installed in the env.")
    else:
        try:
            plugin = GoogleTrendsPlugin()
            ctx = {"locale": locale, "date_range": timeframe, "no_cache": bool(no_cache)}
            with st.spinner("Fetching Google Trends…"):
                data = plugin.enrich_many(keywords, context=ctx)
            st.session_state["trend_results"] = data
            st.success(f"Fetched trends for {len(data)} keyword(s)")
        except Exception as e:
            st.error(f"Failed to fetch trends: {e}")

# Show last results
data = st.session_state.get("trend_results")
if data:
    st.markdown("---")
    st.subheader("Latest results")
    with st.expander("Preview keywords used", expanded=False):
        st.write(keywords[:25])
    rows = []
    for k, v in (data or {}).items():
        if isinstance(v, dict):
            rows.append({
                "keyword": k,
                "trend_label": v.get("trend_label"),
                "trend_factor": v.get("trend_factor"),
                "seasonality_peaks": ", ".join(str(x) for x in (v.get("seasonality_peaks") or [])[:2]),
                "source": v.get("source"),
            })
    if rows:
        try:
            rows.sort(key=lambda r: (r.get("trend_factor") or 0), reverse=True)
        except Exception:
            pass
        st.dataframe(rows, use_container_width=True)
    else:
        st.info("No trend data to display.")
