from __future__ import annotations
import os
import re
import json
import time
from datetime import datetime
import streamlit as st

from keyword_pipeline import expand_seeds, normalize_and_dedupe
from serp import fetch_serp, fetch_page_headings, score_serp, fetch_paa_questions, fetch_related_searches, fetch_serper_json
from components import render_page_selector

# === COMPREHENSIVE LOGGING SYSTEM ===
def log_action(action_type, details):
    """Log all user actions with timestamps"""
    timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
    print(f"🔴 [{timestamp}] {action_type}: {details}")

def add_js_logging():
    """Add JavaScript console logging for all interactions"""
    st.markdown("""
    <script>
    // Log all clicks
    document.addEventListener('click', function(e) {
        console.log('🖱️ CLICK:', {
            target: e.target.tagName,
            className: e.target.className,
            text: e.target.textContent?.substring(0, 50),
            timestamp: new Date().toLocaleTimeString()
        });
    });
    
    // Log all changes
    document.addEventListener('change', function(e) {
        console.log('🔄 CHANGE:', {
            target: e.target.tagName,
            type: e.target.type,
            value: e.target.value?.substring(0, 50),
            timestamp: new Date().toLocaleTimeString()
        });
    });
    
    // Log all input events
    document.addEventListener('input', function(e) {
        console.log('⌨️ INPUT:', {
            target: e.target.tagName,
            type: e.target.type,
            value: e.target.value?.substring(0, 50),
            timestamp: new Date().toLocaleTimeString()
        });
    });
    
    // Log streamlit widget updates
    window.addEventListener('message', function(e) {
        if (e.data.type === 'streamlit:setComponentValue') {
            console.log('🎛️ WIDGET UPDATE:', {
                data: e.data,
                timestamp: new Date().toLocaleTimeString()
            });
        }
    });
    
    console.log('🚀 Streamlit Action Logging Initialized');
    </script>
    """, unsafe_allow_html=True)

# File paths for persistent storage
MODIFIER_STORAGE_FILE = os.path.join(os.path.dirname(__file__), "modifier_libraries.json")

def load_modifier_libraries():
    """Load persistent modifier libraries from JSON file"""
    default_libraries = {
        "prefixes": ["local", "professional", "expert", "top", "best", "affordable", "experienced"],
        "suffixes": ["services", "near me", "consultant", "company", "agency", "solutions", "specialist"],
        "locations": ["Surrey", "Camberley", "Mytchett", "Woking", "Guildford", "Farnham", "Aldershot"]
    }
    
    try:
        if os.path.exists(MODIFIER_STORAGE_FILE):
            with open(MODIFIER_STORAGE_FILE, 'r', encoding='utf-8') as f:
                saved_libraries = json.load(f)
                # Merge with defaults to ensure we have all keys
                for key in default_libraries:
                    if key not in saved_libraries:
                        saved_libraries[key] = default_libraries[key]
                return saved_libraries
    except Exception as e:
        print(f"Error loading modifier libraries: {e}")
    
    return default_libraries

def save_modifier_libraries(libraries):
    """Save modifier libraries to JSON file"""
    try:
        with open(MODIFIER_STORAGE_FILE, 'w', encoding='utf-8') as f:
            json.dump(libraries, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Error saving modifier libraries: {e}")
        return False

def add_to_library(library_type, new_item):
    """Add a new item to a modifier library and save persistently"""
    if not new_item.strip():
        return False
    
    libraries = load_modifier_libraries()
    if library_type in libraries:
        if new_item.strip() not in libraries[library_type]:
            libraries[library_type].append(new_item.strip())
            return save_modifier_libraries(libraries)
    return False


st.set_page_config(page_title="Seed → Select → SERP", page_icon="🧩", layout="wide", initial_sidebar_state="collapsed")

# Initialize logging after page config
add_js_logging()

st.title("Seed → Select → SERP 🧩")
st.caption("Generate variants from seeds, curate the exact queries, and run SERP competitor analysis — all on one page, no sidebar.")

# Direct path to TinaCMS site
ellie_root = r"C:\Users\rhode\source\repos\EllieEdwardsMarketingLeadgenSite"

# Reusable Page selector
selected_page, page_data = render_page_selector(ellie_root)

# Initialize session defaults using persistent libraries BEFORE widgets
libraries = load_modifier_libraries()

if "seeds" not in st.session_state:
    st.session_state["seeds"] = "seo audit\nlocal seo\nkeyword research"
if "prefix_options" not in st.session_state:
    st.session_state["prefix_options"] = libraries["prefixes"].copy()
if "suffix_options" not in st.session_state:
    st.session_state["suffix_options"] = libraries["suffixes"].copy()
if "location_options" not in st.session_state:
    st.session_state["location_options"] = libraries["locations"].copy()
if "selected_prefixes" not in st.session_state:
    st.session_state["selected_prefixes"] = []
if "selected_suffixes" not in st.session_state:
    st.session_state["selected_suffixes"] = []
if "selected_locations" not in st.session_state:
    st.session_state["selected_locations"] = []
if "options" not in st.session_state:
    st.session_state["options"] = []
if "selected" not in st.session_state:
    st.session_state["selected"] = []
if "last_loaded_page" not in st.session_state:
    st.session_state["last_loaded_page"] = None
if "seeds_manually_modified" not in st.session_state:
    st.session_state["seeds_manually_modified"] = False
if "analysis_results" not in st.session_state:
    st.session_state["analysis_results"] = None
if "last_analysis_data" not in st.session_state:
    st.session_state["last_analysis_data"] = None
if "show_analysis_results" not in st.session_state:
    st.session_state["show_analysis_results"] = False
if "save_status_message" not in st.session_state:
    st.session_state["save_status_message"] = None
if "analysis_summary" not in st.session_state:
    st.session_state["analysis_summary"] = None

# Log page selection
if selected_page:
    log_action("PAGE_SELECTED", f"Selected: {selected_page}")
else:
    log_action("PAGE_SELECTION", "No page selected")

if selected_page and selected_page in page_data:
    page_info = page_data[selected_page]
    full_url = f"https://ellieedwardsmarketing.com{page_info['url_path']}"
    log_action("PAGE_INFO_LOADED", f"URL: {full_url}, File: {page_info['file_path']}")
    
    st.info(f"Selected: **{selected_page}** → {full_url}")
    
    # Only load keywords if this is a NEW page selection (not a re-run)
    if (st.session_state["last_loaded_page"] != selected_page and 
        not st.session_state["seeds_manually_modified"]):
        
        try:
            import frontmatter
            with open(page_info["file_path"], 'r', encoding='utf-8') as f:
                post = frontmatter.load(f)
                
            existing_keywords = post.metadata.get("keywords", [])
            seo_section = post.metadata.get("seo", {})
            seo_keywords = seo_section.get("keywords", [])
            winning_keywords = seo_section.get("winningKeywords", [])
            
            # Combine all available keywords, prioritizing SEO section keywords
            all_keywords = []
            if seo_keywords:
                all_keywords.extend(seo_keywords)
            elif existing_keywords:
                all_keywords.extend(existing_keywords)
                
            if all_keywords:
                st.session_state["seeds"] = "\n".join(all_keywords)
                st.session_state["last_loaded_page"] = selected_page
                st.session_state["seeds_manually_modified"] = False
                log_action("KEYWORDS_LOADED", f"Loaded {len(all_keywords)} keywords from page: {all_keywords[:3]}")
                st.success(f"✅ Loaded {len(all_keywords)} keywords from page into seeds")
                
            if winning_keywords:
                log_action("WINNING_KEYWORDS_FOUND", f"Found {len(winning_keywords)} winning keywords: {winning_keywords[:3]}")
                st.info(f"📈 Page has {len(winning_keywords)} winning keywords: {', '.join(winning_keywords[:3])}{'...' if len(winning_keywords) > 3 else ''}")
                
        except Exception as e:
            st.warning(f"Could not load keywords from page: {e}")
    
    elif st.session_state["seeds_manually_modified"]:
        st.caption("💡 Seeds have been manually modified. Select a different page to auto-load new keywords.")
    
    # Auto-search for this page's URL
    with st.expander("🔍 Live page search results", expanded=True):
        # Create search query: domain + path (no https)
        search_query = f"ellieedwardsmarketing.com{page_info['url_path']}"
        st.write(f"Searching for: **{search_query}**")
        
        try:
            # Search for the specific page
            page_results = fetch_serp(search_query, provider="duckduckgo", num=10, locale="gb-en")
            
            # Filter to show results from the domain
            domain_pages = [res for res in page_results if "ellieedwardsmarketing.com" in res.link.lower()]
            
            if domain_pages:
                # Find the specific page we're looking for
                exact_matches = [res for res in domain_pages if page_info['url_path'] in res.link or (page_info['url_path'] == "/" and (res.link.endswith("ellieedwardsmarketing.com") or res.link.endswith("ellieedwardsmarketing.com/")))]
                
                if exact_matches:
                    st.success(f"✅ Found this page in search results:")
                    for i, res in enumerate(exact_matches):
                        st.markdown(f"**#{i + 1}** [{res.title}]({res.link})")
                        if res.snippet:
                            st.caption(res.snippet[:200] + "..." if len(res.snippet) > 200 else res.snippet)
                else:
                    st.warning(f"⚠️ This specific page ({page_info['url_path']}) not found in top results")
                
                # Show other pages from the domain
                other_pages = [res for res in domain_pages if res not in exact_matches]
                if other_pages:
                    st.markdown(f"**Other pages from domain ({len(other_pages)} found):**")
                    for i, res in enumerate(other_pages[:5]):  # Show top 5 to avoid clutter
                        st.markdown(f"**#{i + 1}** [{res.title}]({res.link})")
                        if res.snippet:
                            st.caption(res.snippet[:150] + "..." if len(res.snippet) > 150 else res.snippet)
                    if len(other_pages) > 5:
                        st.caption(f"... and {len(other_pages) - 5} more pages")
            else:
                st.error("❌ No pages found from ellieedwardsmarketing.com")
                # Show what was found instead
                if page_results:
                    st.caption("Found these other results:")
                    for i, res in enumerate(page_results[:3]):
                        st.markdown(f"**#{i + 1}** [{res.title}]({res.link})")
                
        except Exception as e:
            st.error(f"Search failed: {e}")

st.markdown("---")


def _split_lines(s: str) -> list[str]:
    return [l.strip() for l in (s or "").splitlines() if l.strip()]


def _split_csv(s: str) -> list[str]:
    return [p.strip() for p in (s or "").split(",") if p.strip()]


# 1) Inputs and variant generation
st.subheader("1) Seeds and modifiers")

# Track seeds changes
current_seeds = st.session_state.get("seeds", "")
log_action("SEEDS_CONTENT", f"Current seeds: {current_seeds.replace(chr(10), ' | ')}")

col1, col2 = st.columns([2, 1])
with col1:
    st.text_area(
        "Seed keywords (one per line)",
        key="seeds",
        height=160,
        help="Short core topics (1–3 words). We'll create realistic long-tail variants using the modifiers.",
    )
    
    # Log if seeds changed
    new_seeds = st.session_state.get("seeds", "")
    if new_seeds != current_seeds:
        log_action("SEEDS_MODIFIED", f"Seeds changed to: {new_seeds.replace(chr(10), ' | ')}")

with col2:
    # Prefix modifiers section
    st.markdown("**Prefix modifiers**")
    col2a, col2b = st.columns([3, 1])
    with col2a:
        selected_prefixes = st.multiselect(
            "Select prefix modifiers",
            options=st.session_state["prefix_options"],
            default=st.session_state["selected_prefixes"],
            key="prefix_multiselect",
            help="Qualifiers to prepend (e.g., local, small business)"
        )
        
        # Log prefix selection changes
        if selected_prefixes != st.session_state["selected_prefixes"]:
            log_action("PREFIXES_CHANGED", f"Prefixes: {selected_prefixes}")
        
        st.session_state["selected_prefixes"] = selected_prefixes
    with col2b:
        new_prefix = st.text_input("Add new prefix", key="new_prefix", placeholder="e.g. local")
        if st.button("➕", key="add_prefix", help="Add prefix") and new_prefix.strip():
            log_action("PREFIX_ADDED", f"Adding new prefix: {new_prefix.strip()}")
            if add_to_library("prefixes", new_prefix.strip()):
                # Reload libraries to get the updated list
                libraries = load_modifier_libraries()
                st.session_state["prefix_options"] = libraries["prefixes"].copy()
                if new_prefix.strip() not in st.session_state["selected_prefixes"]:
                    st.session_state["selected_prefixes"].append(new_prefix.strip())
                st.success(f"✅ Added '{new_prefix.strip()}' to prefix library")
                st.rerun()
    
    # Suffix modifiers section  
    st.markdown("**Suffix modifiers**")
    col2c, col2d = st.columns([3, 1])
    with col2c:
        selected_suffixes = st.multiselect(
            "Select suffix modifiers",
            options=st.session_state["suffix_options"],
            default=st.session_state["selected_suffixes"],
            key="suffix_multiselect",
            help="Qualifiers to append (e.g., near me, for small business)"
        )
        st.session_state["selected_suffixes"] = selected_suffixes
    with col2d:
        new_suffix = st.text_input("Add new suffix", key="new_suffix", placeholder="e.g. near me")
        if st.button("➕", key="add_suffix", help="Add suffix") and new_suffix.strip():
            if add_to_library("suffixes", new_suffix.strip()):
                # Reload libraries to get the updated list
                libraries = load_modifier_libraries()
                st.session_state["suffix_options"] = libraries["suffixes"].copy()
                if new_suffix.strip() not in st.session_state["selected_suffixes"]:
                    st.session_state["selected_suffixes"].append(new_suffix.strip())
                st.success(f"✅ Added '{new_suffix.strip()}' to suffix library")
                st.rerun()
    
    # Locations section
    st.markdown("**Locations**")
    col2e, col2f = st.columns([3, 1])
    with col2e:
        selected_locations = st.multiselect(
            "Select locations",
            options=st.session_state["location_options"],
            default=st.session_state["selected_locations"],
            key="location_multiselect",
            help="Service areas to include in variants"
        )
        st.session_state["selected_locations"] = selected_locations
    with col2f:
        new_location = st.text_input("Add new location", key="new_location", placeholder="e.g. Woking")
        if st.button("➕", key="add_location", help="Add location") and new_location.strip():
            if add_to_library("locations", new_location.strip()):
                # Reload libraries to get the updated list
                libraries = load_modifier_libraries()
                st.session_state["location_options"] = libraries["locations"].copy()
                if new_location.strip() not in st.session_state["selected_locations"]:
                    st.session_state["selected_locations"].append(new_location.strip())
                st.success(f"✅ Added '{new_location.strip()}' to location library")
                st.rerun()
                
    max_per_seed = st.number_input("Max expansions per seed", min_value=5, max_value=50, value=20, step=5)

gen_cols = st.columns([1, 1, 1, 1])
with gen_cols[0]:
    generate_btn = st.button("Generate variants", type="primary", key="generate_variants")
with gen_cols[1]:
    clear_btn = st.button("Clear all", key="clear_all")
with gen_cols[2]:
    reset_to_page_btn = st.button("Reset to page keywords", disabled=not bool(selected_page), key="reset_to_page")

if clear_btn:
    log_action("CLEAR_ALL_CLICKED", "Cleared all variants")
    st.session_state["options"] = []
    st.session_state["selected"] = []
    st.session_state["seeds_manually_modified"] = False
    st.session_state["last_loaded_page"] = None
    st.session_state["selected_prefixes"] = []
    st.session_state["selected_suffixes"] = []
    st.session_state["selected_locations"] = []

if reset_to_page_btn and selected_page:
    log_action("RESET_TO_PAGE_CLICKED", f"Resetting to page keywords for {selected_page}")
    st.session_state["seeds_manually_modified"] = False
    st.session_state["last_loaded_page"] = None
    st.rerun()

if generate_btn:
    log_action("GENERATE_VARIANTS_CLICKED", f"Generating variants from seeds")
    # Mark seeds as manually modified when user generates variants
    st.session_state["seeds_manually_modified"] = True
    
    seeds = _split_lines(st.session_state.get("seeds", ""))
    prefix = st.session_state["selected_prefixes"].copy()
    suffix = st.session_state["selected_suffixes"].copy()
    
    # Add selected locations to suffix
    suffix.extend(st.session_state["selected_locations"])

    # Sanitize banned terms
    banned = {"best", "affordable", "enterprise", "pricing", "price", "cheap", "cheapest"}
    prefix = [p for p in prefix if p.lower() not in banned]
    suffix = [s for s in suffix if s.lower() not in banned]

    expanded = expand_seeds(seeds, prefix_mods=prefix, suffix_mods=suffix, max_per_seed=int(max_per_seed))
    normalized = normalize_and_dedupe(expanded)
    st.session_state["options"] = normalized
    st.session_state["selected"] = normalized[: min(50, len(normalized))]


# 2) Curate the exact queries
options = st.session_state.get("options", [])
selected = st.session_state.get("selected", [])
st.subheader("2) Select queries to analyze")
if not options:
    st.info("Click ‘Generate variants’ to create a candidate list.")
else:
    filt_col1, filt_col2, filt_col3 = st.columns([2, 1, 1])
    with filt_col1:
        filter_text = st.text_input("Filter (contains)", value="", help="Type to filter (e.g., ‘near me’ or a locality)")
    filtered = [o for o in options if (not filter_text or filter_text.lower() in o.lower())]
    with filt_col2:
        if st.button("Select all filtered", key="select_all_filtered"):
            log_action("SELECT_ALL_CLICKED", f"Selected all filtered queries")
            # union of current selected and filtered
            st.session_state["selected"] = sorted(set(selected) | set(filtered))
            selected = st.session_state["selected"]
    with filt_col3:
        if st.button("Clear selection", key="clear_selection"):
            log_action("CLEAR_SELECTION_CLICKED", f"Cleared all selections")
            st.session_state["selected"] = []
            selected = []

    selected = st.multiselect(
        "Queries to analyze",
        options=filtered,
        default=[s for s in selected if s in filtered],
        key="selected",
        help="Pick the exact set to send to the SERP provider.",
    )
    st.caption(f"Selected {len(selected)} of {len(options)} generated ({len(filtered)} visible with current filter).")


# 3) Provider and output controls
st.subheader("3) Provider and outputs")
cols = st.columns([1, 1, 1, 1])
with cols[0]:
    provider = st.selectbox("Provider", options=["auto", "serper", "duckduckgo"], index=0, key="serp_provider")
    log_action("PROVIDER_SELECTED", f"Provider: {provider}")
with cols[1]:
    serper_key = st.text_input("SERP API key (serper.dev)", type="password", key="serper_api_key")
    if serper_key:
        log_action("API_KEY_PROVIDED", f"API key length: {len(serper_key)}")
with cols[2]:
    results_per_query = st.number_input("Results per query", min_value=5, max_value=20, value=10, step=1)
    log_action("RESULTS_PER_QUERY", f"Results per query: {results_per_query}")
with cols[3]:
    fetch_pages = st.checkbox("Fetch H1/H2 from top pages", value=True, key="fetch_headings")
    log_action("FETCH_PAGES_SETTING", f"Fetch pages: {fetch_pages}")

# PAA toggle
show_paa = st.checkbox("Fetch People Also Ask (PAA)", value=True, help="Pull PAA via serper.dev when available; fallback infers question-like headings from top pages")
log_action("PAA_SETTING", f"Fetch PAA: {show_paa}")
show_related = st.checkbox("Fetch Related Searches", value=True, help="Pull related searches via serper.dev when available")
log_action("RELATED_SETTING", f"Fetch Related: {show_related}")
show_raw_serper = st.checkbox("Show raw Serper JSON in results", value=False, help="Displays the exact serper.dev response for each keyword when using Google provider")
log_action("RAW_SERPER_SETTING", f"Show raw: {show_raw_serper}")
require_google_paa = st.checkbox("Require Google PAA (no fallback)", value=False, help="Only accept PAA when present in serper JSON. If missing, label 'google-missing' and skip")
require_google_related = st.checkbox("Require Google Related (no fallback)", value=False, help="Only accept Related Searches when present in serper JSON. If missing, label 'google-missing' and skip")
col_geo1, col_geo2 = st.columns([2, 1])
with col_geo1:
    serper_location = st.text_input("Serper location bias (optional)", value="Camberley, England, United Kingdom", help="Helps trigger local modules like PAA/Maps; examples: 'Camberley, England, United Kingdom' or a postcode")
with col_geo2:
    serper_no_cache = st.checkbox("No cache (fresh results)", value=False, help="Ask serper for fresh results to better match live SERPs")

st.markdown("---")

# 4) Run
save_analysis = st.checkbox("Save analysis results to selected page", value=bool(selected_page), disabled=not bool(selected_page), key="save_to_page")

# Log save analysis checkbox changes
if save_analysis:
    log_action("SAVE_ANALYSIS_ENABLED", f"Will save analysis to: {selected_page}")
else:
    log_action("SAVE_ANALYSIS_DISABLED", "Analysis will not be saved")

if selected_page:
    st.caption(f"Analysis will be saved to: **{selected_page}**")

run_btn = st.button("Run SERP Analysis", type="primary", disabled=not bool(selected), key="run_analysis")

# Log run button click
if run_btn:
    log_action("RUN_ANALYSIS_CLICKED", f"Starting analysis with {len(selected)} keywords, Provider: {provider}, Save: {save_analysis}")
    
    rows = [q for q in selected if q]
    use_provider = "duckduckgo"
    if provider == "serper" or (provider == "auto" and serper_key.strip()):
        use_provider = "serper"
    
    log_action("ANALYSIS_CONFIG", f"Provider: {use_provider}, Keywords: {len(rows)}, Results per query: {results_per_query}")

    analysis_rows: list[dict] = []
    paa_by_keyword: dict[str, list[str]] = {}
    paa_source_by_keyword: dict[str, str] = {}
    related_by_keyword: dict[str, list[str]] = {}
    related_source_by_keyword: dict[str, str] = {}
    with st.status("Running SERP…", expanded=True) as status:
        raw_serper_by_keyword: dict[str, dict] = {}
        organic_results_by_keyword: dict[str, list[dict]] = {}
        for q in rows:
            st.write(f"Query: {q}")
            try:
                # Fetch serper raw JSON if needed (and provider is serper)
                raw_serper = None
                if use_provider == "serper" and (show_paa or show_related or show_raw_serper):
                    try:
                        raw_serper = fetch_serper_json(
                            q,
                            api_key=serper_key.strip(),
                            num=int(results_per_query),
                            locale="gb-en",
                            location=(serper_location.strip() or None),
                            no_cache=bool(serper_no_cache),
                        )
                    except Exception as e:
                        st.caption(f"Raw Serper fetch failed for '{q}': {e}")

                # Build results either from raw_serper or using fetch_serp (which also supports fallback)
                if raw_serper is not None:
                    # Map organic to SerpResult shape
                    organic = raw_serper.get("organic") or []
                    results = []
                    for item in organic[: int(results_per_query)]:
                        results.append(type("SR", (), {
                            "title": item.get("title") or "",
                            "link": item.get("link") or "",
                            "snippet": item.get("snippet") or "",
                            "__dict__": {
                                "title": item.get("title") or "",
                                "link": item.get("link") or "",
                                "snippet": item.get("snippet") or "",
                            }
                        }))
                else:
                    results = fetch_serp(q, provider=use_provider, api_key=serper_key.strip() or None, num=int(results_per_query), locale="gb-en")
                metrics = score_serp(results, seed=q)
                st.json({
                    "difficulty": metrics["difficulty"],
                    "exact_in_title": metrics["exact_in_title"],
                    "unique_domains": metrics["unique_domains"],
                    "gov_edu": metrics["gov_edu"],
                    "aggregators": metrics["aggregators"],
                })
                page_outlines = []
                if fetch_pages:
                    for res in results[: min(5, len(results))]:
                        page_outlines.append(fetch_page_headings(res.link))
                # Fetch PAA
                paa_list: list[str] = []
                paa_source: str = "none"
                if show_paa:
                    try:
                        paa_list, paa_source = fetch_paa_questions(
                            q,
                            provider=use_provider,
                            api_key=serper_key.strip() or None,
                            results=results,
                            outlines=page_outlines,
                            raw=raw_serper,
                            require_google_only=require_google_paa,
                        )
                    except Exception as e:
                        st.caption(f"PAA fetch failed for '{q}': {e}")
                        paa_list = []
                        paa_source = "error"
                # Build structured results with explicit rank
                structured_results = [
                    {
                        "rank": i + 1,
                        "title": res.title,
                        "link": res.link,
                        "snippet": res.snippet,
                    }
                    for i, res in enumerate(results)
                ]
                # Stash for saving later
                organic_results_by_keyword[q] = structured_results

                row = {
                    "keyword": q,
                    "difficulty": metrics.get("difficulty"),
                    "exact_in_title": metrics.get("exact_in_title"),
                    "unique_domains": metrics.get("unique_domains"),
                    "gov_edu": metrics.get("gov_edu"),
                    "aggregators": metrics.get("aggregators"),
                    # Include explicit rank on each result for clearer display in Tina
                    "results": structured_results,
                    "outlines": page_outlines,
                    "paa": paa_list,
                }
                # Fetch Related Searches (after row built so headings are available)
                if show_related:
                    try:
                        related_list, related_src = fetch_related_searches(
                            q,
                            provider=use_provider,
                            api_key=serper_key.strip() or None,
                            raw=raw_serper,
                            require_google_only=require_google_related,
                        )
                    except Exception as e:
                        st.caption(f"Related searches fetch failed for '{q}': {e}")
                        related_list, related_src = [], "error"
                    row["related"] = related_list

                # Collect for analysis
                analysis_rows.append({
                    "keyword": q,
                    "difficulty": int(metrics.get("difficulty") or 0),
                    "exact_in_title": int(metrics.get("exact_in_title") or 0),
                    "unique_domains": int(metrics.get("unique_domains") or 0),
                    "gov_edu": int(metrics.get("gov_edu") or 0),
                    "aggregators": int(metrics.get("aggregators") or 0),
                    "is_local": any(s in q.lower() for s in ["local", "near me", "surrey", "camberley", "mytchett"]),
                    "is_smallbiz": any(s in q.lower() for s in ["small business", "local business"]),
                })
                if show_paa:
                    paa_by_keyword[q] = paa_list
                    paa_source_by_keyword[q] = paa_source
                if show_related:
                    related_by_keyword[q] = row.get("related", [])
                    related_source_by_keyword[q] = related_src

                # Show raw serper JSON if requested
                if show_raw_serper and raw_serper is not None:
                    # Store for later rendering outside of status (to avoid nested expanders)
                    raw_serper_by_keyword[q] = raw_serper

            except Exception as e:
                st.warning(f"Failed for '{q}': {e}")
        status.update(label="SERP complete", state="complete")
        
        # Store analysis flag in session state
        st.session_state["show_analysis_results"] = True
    # Compute aggregated PAA
        if show_paa:
            agg_seen = set()
            aggregated_paa: list[str] = []
            for q, qs in paa_by_keyword.items():
                for item in (qs or []):
                    key = (item or "").strip().lower()
                    if key and key not in agg_seen:
                        agg_seen.add(key)
                        aggregated_paa.append(item.strip())
        else:
            aggregated_paa = []
        if show_related:
            agg_r_seen = set()
            aggregated_related: list[str] = []
            for q, rs in related_by_keyword.items():
                for item in (rs or []):
                    key = (item or "").strip().lower()
                    if key and key not in agg_r_seen:
                        agg_r_seen.add(key)
                        aggregated_related.append(item.strip())
        else:
            aggregated_related = []
        # Stash raw serper JSON in session for later display
        if show_raw_serper and raw_serper_by_keyword:
            st.session_state["raw_serper_by_keyword"] = raw_serper_by_keyword
        # Stash organic results per keyword for save flow
        if organic_results_by_keyword:
            st.session_state["organic_results_by_keyword"] = organic_results_by_keyword

# ========== Analysis Summary Display ==========
# Check if we should show analysis results (either just completed or from session state)
if st.session_state.get("show_analysis_results") and (
    'analysis_rows' in locals() and analysis_rows or 
    st.session_state.get("last_analysis_data")
):
    # Use current analysis or load from session state
    if 'analysis_rows' in locals() and analysis_rows:
        current_analysis_rows = analysis_rows
        log_action("DISPLAYING_CURRENT_ANALYSIS", f"Showing current analysis results - {len(analysis_rows)} keywords")
    elif st.session_state.get("last_analysis_data"):
        current_analysis_rows = st.session_state["last_analysis_data"]["analysis_rows"]
        log_action("DISPLAYING_STORED_ANALYSIS", f"Showing stored analysis results - {len(current_analysis_rows)} keywords")
    else:
        current_analysis_rows = []
    if current_analysis_rows:
        st.markdown("---")
        st.header("📊 Analysis summary")

        # Difficulty distribution
        diffs = [r["difficulty"] for r in current_analysis_rows]
        mn, mx = min(diffs), max(diffs)
        avg = sum(diffs) / len(diffs)
        easy = sum(1 for d in diffs if d < 50)
        moderate = sum(1 for d in diffs if 50 <= d <= 69)
        hard = sum(1 for d in diffs if d >= 70)
        
        # Categorize keywords by difficulty
        easy_keywords = [r["keyword"] for r in current_analysis_rows if r["difficulty"] < 50]
        moderate_keywords = [r["keyword"] for r in current_analysis_rows if 50 <= r["difficulty"] <= 69]
        hard_keywords = [r["keyword"] for r in current_analysis_rows if r["difficulty"] >= 70]

        m1, m2, m3 = st.columns(3)
        with m1:
            st.metric("Avg. difficulty (0=easier)", f"{avg:.1f}", help="Lower is easier to rank; 0–49 easy, 50–69 moderate, 70–100 hard")
        with m2:
            st.metric("E/M/H counts", f"{easy} / {moderate} / {hard}")
        with m3:
            st.metric("Range", f"{mn}–{mx}")

        # Keyword difficulty breakdown
        if easy_keywords or moderate_keywords or hard_keywords:
            st.subheader("Keyword difficulty breakdown")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if easy_keywords:
                    st.markdown(f"**🟢 Easy Keywords (<50)** - {len(easy_keywords)} total")
                    for keyword in easy_keywords:
                        difficulty = next(r["difficulty"] for r in current_analysis_rows if r["keyword"] == keyword)
                        st.markdown(f"• {keyword} `({difficulty})`")
                else:
                    st.markdown("**🟢 Easy Keywords (<50)** - None")
            
            with col2:
                if moderate_keywords:
                    st.markdown(f"**🟡 Moderate Keywords (50-69)** - {len(moderate_keywords)} total")
                    for keyword in moderate_keywords:
                        difficulty = next(r["difficulty"] for r in current_analysis_rows if r["keyword"] == keyword)
                        st.markdown(f"• {keyword} `({difficulty})`")
                else:
                    st.markdown("**🟡 Moderate Keywords (50-69)** - None")
            
            with col3:
                if hard_keywords:
                    st.markdown(f"**🔴 Hard Keywords (70+)** - {len(hard_keywords)} total")
                    for keyword in hard_keywords:
                        difficulty = next(r["difficulty"] for r in current_analysis_rows if r["keyword"] == keyword)
                        st.markdown(f"• {keyword} `({difficulty})`")
                else:
                    st.markdown("**🔴 Hard Keywords (70+)** - None")

        # Top opportunities (lowest difficulty first)
        st.subheader("Top opportunities")
        opps = sorted(current_analysis_rows, key=lambda r: (r["difficulty"], -r["exact_in_title"]))[:10]
        st.table([
            {
                "keyword": r["keyword"],
                "difficulty": r["difficulty"],
                "exact_in_title": r["exact_in_title"],
                "unique_domains": r["unique_domains"],
                "local": "yes" if r["is_local"] else "",
                "small_biz": "yes" if r["is_smallbiz"] else "",
            }
            for r in opps
        ])

        # Thematic clusters (rough root extraction)
        def infer_root(q: str) -> str:
            ql = q.lower().split()
            drop = {"local", "near", "me", "for", "small", "business", "local", "surrey", "camberley", "mytchett"}
            core = [t for t in ql if t not in drop]
            return " ".join(core[:2]) if core else ql[0] if ql else q

        cluster_map: dict[str, list[dict]] = {}
        for r in current_analysis_rows:
            root = infer_root(r["keyword"]) or r["keyword"]
            cluster_map.setdefault(root, []).append(r)
        cluster_summ = [
            {
                "topic": k,
                "count": len(v),
                "min_diff": min(x["difficulty"] for x in v),
                "avg_diff": round(sum(x["difficulty"] for x in v) / len(v), 1),
            }
            for k, v in cluster_map.items()
        ]
        cluster_summ.sort(key=lambda x: (x["min_diff"], -x["count"]))
        st.subheader("Best topic clusters (by easiest member)")
        st.table(cluster_summ[:6])

        # Explanations and recommendations
        st.subheader("What this means")
        many_hard = hard > (easy + moderate)
        few_exact = sum(1 for r in current_analysis_rows if r["exact_in_title"] == 0) / len(current_analysis_rows) >= 0.5
        any_gov = any(r["gov_edu"] > 0 for r in current_analysis_rows)
        any_aggr = any(r["aggregators"] > 0 for r in current_analysis_rows)

        bullets = []
        if many_hard:
            bullets.append("Most selected queries are competitive (70+). Start with the lowest-difficulty opportunities above before tackling hard queries.")
        else:
            bullets.append("You have a good spread of easy/moderate queries — prioritise the easiest first to capture quick wins.")
        if few_exact:
            bullets.append("Many SERPs have few exact-in-title matches. Ensure your H1/title includes the exact query to strengthen relevance.")
        if any_gov:
            bullets.append("Gov/edu domains appear in some SERPs; consider informational angles or long-tail local variants to reduce competition.")
        if any_aggr:
            bullets.append("Aggregator directories are present; differentiate with local proof, case studies, and service-specific FAQs.")
        if not bullets:
            bullets.append("SERPs look balanced; focus on publishing high-quality, locally-signalled content and internal links.")
        for b in bullets:
            st.markdown(f"- {b}")

        st.subheader("Suggested next steps")
        steps = [
            "Pick 3–5 of the easiest queries and draft outlines using the generated competitor headings.",
            "Add local signals (service area, NAP, GBP links) and clear CTAs to each page.",
            "Interlink new pages with existing related content (strategy ↔ keyword research ↔ content).",
            "For harder terms (70+), publish support content first and build internal links before attempting a primary page.",
        ]
        for s in steps:
            st.markdown(f"- {s}")

        # Downloadable analysis JSON
        try:
            analysis_out = {
                "summary": {"avg": avg, "range": [mn, mx], "easy": easy, "moderate": moderate, "hard": hard},
                "top_opportunities": opps,
                "clusters": cluster_summ[:12],
                "notes": bullets,
                "next_steps": steps,
            }
            
            # Store complete analysis data in session state for save functionality
            # Pull PAA from local or existing session
            existing_paa_by_kw = st.session_state.get("last_analysis_data", {}).get("paa_by_keyword") if st.session_state.get("last_analysis_data") else {}
            existing_paa_agg = st.session_state.get("last_analysis_data", {}).get("paa_aggregated") if st.session_state.get("last_analysis_data") else []
            st.session_state["last_analysis_data"] = {
                "analysis_rows": analysis_rows,
                "analysis_out": analysis_out,
                "easy": easy,
                "moderate": moderate, 
                "hard": hard,
                "opps": opps,
                "easy_keywords": easy_keywords,
                "moderate_keywords": moderate_keywords,
                "hard_keywords": hard_keywords,
                "organic_results_by_keyword": organic_results_by_keyword if 'organic_results_by_keyword' in locals() else st.session_state.get("organic_results_by_keyword", {}),
                "paa_by_keyword": paa_by_keyword if 'paa_by_keyword' in locals() and paa_by_keyword else existing_paa_by_kw,
                "paa_source_by_keyword": paa_source_by_keyword if 'paa_source_by_keyword' in locals() and paa_source_by_keyword else {},
                "paa_aggregated": aggregated_paa if 'aggregated_paa' in locals() else existing_paa_agg,
                "related_by_keyword": related_by_keyword if 'related_by_keyword' in locals() else {},
                "related_source_by_keyword": related_source_by_keyword if 'related_source_by_keyword' in locals() else {},
                "related_aggregated": aggregated_related if 'aggregated_related' in locals() else [],
                "selected_page": selected_page,
                "timestamp": datetime.now().isoformat()
            }
            log_action("ANALYSIS_STORED", f"Analysis data stored in session state - {len(analysis_rows)} keywords")
            
            st.download_button(
                "Download analysis.json",
                data=json.dumps(analysis_out, ensure_ascii=False, indent=2),
                file_name="analysis.json",
                mime="application/json",
            )
        except Exception:
            pass

        # Save analysis and winning keywords to selected page
        if selected_page and selected_page in page_data and save_analysis:
            st.markdown("---")
            st.subheader("💾 Save analysis results to page")
            
            # Use current analysis data or fallback to stored session state
            current_opps = opps if 'opps' in locals() else []
            current_easy = easy if 'easy' in locals() else 0
            current_moderate = moderate if 'moderate' in locals() else 0 
            current_hard = hard if 'hard' in locals() else 0
            
            # If no current analysis, try to use stored data
            if not current_opps and st.session_state.get("last_analysis_data"):
                stored_data = st.session_state["last_analysis_data"]
                current_opps = stored_data.get("opps", [])
                current_easy = stored_data.get("easy", 0)
                current_moderate = stored_data.get("moderate", 0)
                current_hard = stored_data.get("hard", 0)
                log_action("USING_STORED_ANALYSIS", f"Using stored analysis data - {len(current_opps)} opportunities")
            
            # Get top opportunities as potential winning keywords
            top_winners = [r["keyword"] for r in current_opps if r["difficulty"] < 60][:10]
            
            if top_winners:
                st.write("**Suggested winning keywords** (difficulty < 60):")
                selected_winners = st.multiselect(
                    "Choose keywords to save as winning keywords for this page:",
                    options=top_winners,
                    default=top_winners[:5],
                    help="These will be saved to the page's seo.winningKeywords field in TinaCMS"
                )
            else:
                selected_winners = []
                st.info("No easy opportunities found (all keywords have difficulty ≥ 60)")
                
            # Report naming and multi-report interface
            st.subheader("📊 Report Management")
            col1, col2 = st.columns([2, 1])
            
            with col1:
                report_name = st.text_input(
                    "Report Name", 
                    value="SERP Analysis " + datetime.now().strftime("%Y-%m-%d"),
                    help="Give this analysis a descriptive name for easy identification"
                )
            
            with col2:
                # Check if there are existing reports
                existing_reports = []
                if selected_page:
                    try:
                        page_info = page_data[selected_page]
                        with open(page_info["file_path"], 'r', encoding='utf-8') as f:
                            post = frontmatter.load(f)
                        
                        if "seo" in post.metadata and "serpAnalysisHistory" in post.metadata["seo"]:
                            existing_reports = post.metadata["seo"]["serpAnalysisHistory"]
                    except:
                        pass
                
                st.metric("Existing Reports", len(existing_reports))

            # Log when save button is about to be rendered
            log_action("SAVE_BUTTON_RENDERED", f"Save button available - Page: {selected_page}, Report: {report_name}")

            # Initialize save trigger in session state
            if "save_triggered" not in st.session_state:
                st.session_state.save_triggered = False
            
            # Create unique key based on page and analysis data
            button_key = f"save_analysis_{selected_page.replace(' ', '_').replace('/', '_')}_{len(opps)}"
            save_clicked = st.button("Save Analysis & Keywords to TinaCMS", type="primary", key=button_key)
            log_action("SAVE_BUTTON_CHECK", f"Save button state: {save_clicked}, key: {button_key}")
            
            # If button was clicked, set session state flag
            if save_clicked:
                st.session_state.save_triggered = True
                log_action("SAVE_BUTTON_CLICKED", f"Save button clicked for {selected_page}")
            
            # Process save if triggered
            if st.session_state.save_triggered:
                log_action("SAVE_PROCESS_TRIGGERED", f"Processing save for {selected_page}")
                st.success("🎯 Save button clicked! Processing...")
                # Reset the trigger immediately to prevent repeated saves
                st.session_state.save_triggered = False
                
                # === COMPREHENSIVE DEBUG LOGGING ===
                print("\n" + "="*80)
                print("🚨 STREAMLIT SAVE BUTTON CLICKED!")
                print("="*80)
                
                st.info("🔄 Starting save process...")
                
                # Create a debug container for live updates
                debug_container = st.container()
                
                try:
                    import frontmatter
                    from datetime import datetime
                    import uuid
                    
                    print(f"✅ Imports successful")
                    debug_container.success("✅ Step 1: Imports loaded")
                    
                    # Get analysis data from current or stored
                    if 'easy' in locals() and 'moderate' in locals() and 'hard' in locals():
                        analysis_easy, analysis_moderate, analysis_hard = easy, moderate, hard
                        analysis_opps = opps if 'opps' in locals() else []
                        analysis_keywords = {
                            "easy": easy_keywords if 'easy_keywords' in locals() else [],
                            "moderate": moderate_keywords if 'moderate_keywords' in locals() else [],
                            "hard": hard_keywords if 'hard_keywords' in locals() else []
                        }
                        log_action("SAVE_USING_CURRENT", "Using current analysis data for save")
                    elif st.session_state.get("last_analysis_data"):
                        stored_data = st.session_state["last_analysis_data"]
                        analysis_easy = stored_data.get("easy", 0)
                        analysis_moderate = stored_data.get("moderate", 0)
                        analysis_hard = stored_data.get("hard", 0)
                        analysis_opps = stored_data.get("opps", [])
                        analysis_keywords = {
                            "easy": stored_data.get("easy_keywords", []),
                            "moderate": stored_data.get("moderate_keywords", []),
                            "hard": stored_data.get("hard_keywords", [])
                        }
                        log_action("SAVE_USING_STORED", "Using stored analysis data for save")
                    else:
                        raise Exception("No analysis data available for save")
                    
                    page_info = page_data[selected_page]
                    file_path = page_info['file_path']
                    
                    print(f"📁 Target file: {file_path}")
                    print(f"📊 Report name: {report_name}")
                    print(f"📈 Analysis data: Easy:{analysis_easy} Moderate:{analysis_moderate} Hard:{analysis_hard}")
                    
                    debug_container.info(f"📁 Step 2: Target file: {file_path}")
                    debug_container.info(f"📊 Report: '{report_name}' (E:{analysis_easy} M:{analysis_moderate} H:{analysis_hard})")
                    
                    # Check file exists and is accessible
                    if not os.path.exists(file_path):
                        raise FileNotFoundError(f"Target file does not exist: {file_path}")
                    
                    print(f"✅ File exists and accessible")
                    debug_container.success("✅ Step 3: File exists and accessible")
                    
                    # Load current page
                    print(f"📖 Loading file content...")
                    with open(file_path, 'r', encoding='utf-8') as f:
                        post = frontmatter.load(f)
                    
                    print(f"✅ File loaded - {len(post.metadata)} frontmatter fields")
                    debug_container.success(f"✅ Step 4: File loaded ({len(post.metadata)} frontmatter fields)")
                    
                    # Ensure SEO section exists
                    if "seo" not in post.metadata:
                        post.metadata["seo"] = {}
                        print(f"✅ Created new SEO section")
                        debug_container.info("🆕 Created new SEO section")
                    else:
                        seo_fields = len(post.metadata["seo"])
                        print(f"✅ SEO section exists with {seo_fields} fields")
                        debug_container.success(f"✅ Step 5: SEO section exists ({seo_fields} fields)")
                    
                    # Initialize serpAnalysisHistory if it doesn't exist
                    if "serpAnalysisHistory" not in post.metadata["seo"]:
                        post.metadata["seo"]["serpAnalysisHistory"] = []
                        print(f"✅ Created new serpAnalysisHistory array")
                        debug_container.info("🆕 Created new serpAnalysisHistory array")
                    else:
                        existing_count = len(post.metadata["seo"]["serpAnalysisHistory"])
                        print(f"✅ serpAnalysisHistory exists with {existing_count} reports")
                        debug_container.success(f"✅ Step 6: Found {existing_count} existing reports")
                    
                    pre_count = len(post.metadata["seo"]["serpAnalysisHistory"])
                    print(f"📊 Pre-save report count: {pre_count}")
                    debug_container.info(f"📊 Current report count: {pre_count}")
                    
                    # Generate unique report ID
                    report_id = f"report_{datetime.now().strftime('%Y_%m_%d_%H_%M_%S')}"
                    analysis_date = datetime.now().isoformat()
                    
                    print(f"🆔 Generated report ID: {report_id}")
                    print(f"📅 Analysis date: {analysis_date}")
                    debug_container.success(f"✅ Step 7: Generated report ID: {report_id}")
                    
                    # Create new report object
                    # Include PAA/Related in report if available
                    report_paa_by_kw = st.session_state.get("last_analysis_data", {}).get("paa_by_keyword", {})
                    report_paa_agg = st.session_state.get("last_analysis_data", {}).get("paa_aggregated", [])
                    report_paa_src_by_kw = st.session_state.get("last_analysis_data", {}).get("paa_source_by_keyword", {})
                    report_rel_by_kw = st.session_state.get("last_analysis_data", {}).get("related_by_keyword", {})
                    report_rel_agg = st.session_state.get("last_analysis_data", {}).get("related_aggregated", [])
                    report_rel_src_by_kw = st.session_state.get("last_analysis_data", {}).get("related_source_by_keyword", {})
                    # Organic results per keyword from current analysis_rows if available
                    organic_by_kw_list = []
                    # Prefer current analysis_rows
                    if 'analysis_rows' in locals() and analysis_rows:
                        for row in analysis_rows:
                            res_list = row.get("results", []) or []
                            normalized_results = []
                            for idx, r in enumerate(res_list):
                                if isinstance(r, dict):
                                    nr = {**r}
                                    nr.setdefault("rank", idx + 1)
                                    normalized_results.append(nr)
                                else:
                                    try:
                                        normalized_results.append({
                                            "rank": idx + 1,
                                            "title": getattr(r, "title", ""),
                                            "link": getattr(r, "link", ""),
                                            "snippet": getattr(r, "snippet", ""),
                                        })
                                    except Exception:
                                        continue
                            organic_by_kw_list.append({
                                "keyword": row.get("keyword"),
                                "results": normalized_results,
                            })
                    else:
                        # Fallback to session-stashed organic results keyed by keyword
                        sess_org = st.session_state.get("organic_results_by_keyword", {}) or st.session_state.get("last_analysis_data", {}).get("organic_results_by_keyword", {})
                        for kw, res_list in (sess_org or {}).items():
                            # Ensure rank present and sorted by rank
                            normalized = []
                            for idx, r in enumerate(res_list or []):
                                nr = dict(r) if isinstance(r, dict) else {}
                                nr.setdefault("rank", (idx + 1))
                                normalized.append(nr)
                            try:
                                normalized.sort(key=lambda x: int(x.get("rank") or 9999))
                            except Exception:
                                pass
                            organic_by_kw_list.append({
                                "keyword": kw,
                                "results": normalized,
                            })
                    # Build a ranked 1-line summary per keyword for Tina quick-scan
                    organic_summary_by_kw_list = []
                    for item in organic_by_kw_list:
                        kw = item.get("keyword")
                        lines: list[str] = []
                        for r in item.get("results", []) or []:
                            try:
                                rank = int(r.get("rank") or 0)
                            except Exception:
                                rank = 0
                            host = ""
                            try:
                                from urllib.parse import urlparse
                                host = urlparse(r.get("link") or "").netloc
                            except Exception:
                                pass
                            title = r.get("title") or ""
                            # Compose: #N domain — Title
                            parts = []
                            if rank:
                                parts.append(f"#{rank}")
                            if host:
                                parts.append(host)
                            if title:
                                parts.append("— " + title)
                            line = " ".join(parts).strip()
                            if line:
                                lines.append(line)
                        # Ensure proper order by rank if present
                        try:
                            lines_sorted = [x for _, x in sorted(
                                [
                                    (int((r.get("rank") or 0)), f"#{int((r.get('rank') or 0))} {urlparse(r.get('link') or '').netloc} — {r.get('title') or ''}".strip())
                                    for r in (item.get("results", []) or [])
                                ],
                                key=lambda t: (t[0] if t[0] else 9999)
                            ) if _]
                        except Exception:
                            lines_sorted = lines
                        organic_summary_by_kw_list.append({
                            "keyword": kw,
                            "lines": lines_sorted or lines,
                        })

                    # Raw serper JSON per keyword (only if captured this run)
                    raw_serper_map = st.session_state.get("raw_serper_by_keyword", {})
                    raw_serper_by_kw_list = []
                    for k, payload in (raw_serper_map or {}).items():
                        try:
                            raw_serper_by_kw_list.append({
                                "keyword": k,
                                "payload": json.dumps(payload, ensure_ascii=False),
                            })
                        except Exception:
                            # Fallback to string cast if non-serializable
                            raw_serper_by_kw_list.append({
                                "keyword": k,
                                "payload": str(payload),
                            })
                    # PAA/Related as list structures for Tina readability
                    paa_by_kw_list = []
                    for k, qs in (report_paa_by_kw or {}).items():
                        paa_by_kw_list.append({
                            "keyword": k,
                            "source": (report_paa_src_by_kw or {}).get(k, "unknown"),
                            "questions": qs or [],
                        })
                    related_by_kw_list = []
                    for k, qs in (report_rel_by_kw or {}).items():
                        related_by_kw_list.append({
                            "keyword": k,
                            "source": (report_rel_src_by_kw or {}).get(k, "unknown"),
                            "queries": qs or [],
                        })
                    # Serper config captured from current UI toggles
                    serper_config = {
                        "location": st.session_state.get("serper_location") if "serper_location" in st.session_state else None,
                        "noCache": bool(st.session_state.get("serper_no_cache")) if "serper_no_cache" in st.session_state else False,
                        "resultsPerQuery": int(st.session_state.get("results_per_query", 10)) if "results_per_query" in st.session_state else None,
                    }

                    new_report = {
                        "reportId": report_id,
                        "analysisDate": analysis_date,
                        "reportName": report_name,
                        "avgDifficulty": sum(r["difficulty"] for r in analysis_opps) / len(analysis_opps) if analysis_opps else 0,
                        "easyCount": analysis_easy,
                        "easyKeywords": analysis_keywords["easy"],
                        "moderateCount": analysis_moderate,
                        "moderateKeywords": analysis_keywords["moderate"],
                        "hardCount": analysis_hard,
                        "hardKeywords": analysis_keywords["hard"],
                        "topOpportunities": [r["keyword"] for r in analysis_opps[:10]],
                        "analysisNotes": [],  # bullets from stored data would need to be added
                        "nextSteps": [],      # steps from stored data would need to be added
                        "paaAggregated": report_paa_agg,
                        "paaByKeyword": report_paa_by_kw,
                        "paaSourceByKeyword": report_paa_src_by_kw,
                        "relatedAggregated": report_rel_agg,
                        "relatedByKeyword": report_rel_by_kw,
                        "relatedSourceByKeyword": report_rel_src_by_kw,
                        # Extended datasets for Tina visibility
                        "organicByKeyword": organic_by_kw_list,
                        "paaByKeywordList": paa_by_kw_list,
                        "relatedByKeywordList": related_by_kw_list,
                        "rawSerperByKeyword": raw_serper_by_kw_list,
                        "organicSummaryByKeyword": organic_summary_by_kw_list,
                        "serperConfig": serper_config,
                    }
                    
                    print(f"📝 Created report object with {len(new_report)} fields")
                    print(f"🔍 Report contents preview:")
                    print(f"   - Name: {new_report['reportName']}")
                    print(f"   - Keywords: E:{new_report['easyCount']} M:{new_report['moderateCount']} H:{new_report['hardCount']}")
                    print(f"   - Opportunities: {len(new_report['topOpportunities'])} items")
                    debug_container.success(f"✅ Step 8: Created report object ({len(new_report)} fields)")
                    
                    # Add the new report to history
                    print(f"📈 Adding report to serpAnalysisHistory...")
                    post.metadata["seo"]["serpAnalysisHistory"].append(new_report)
                    post_count_after_add = len(post.metadata["seo"]["serpAnalysisHistory"])
                    
                    print(f"✅ Report added! Count: {pre_count} → {post_count_after_add}")
                    debug_container.success(f"✅ Step 9: Report added ({pre_count} → {post_count_after_add})")
                    
                    # Set as current active report
                    post.metadata["seo"]["currentReport"] = report_id
                    print(f"🎯 Set as current active report: {report_id}")
                    debug_container.success(f"✅ Step 10: Set as current report")
                    
                    # Update winning keywords (maintain backward compatibility)
                    if selected_winners:
                        existing_winners = post.metadata["seo"].get("winningKeywords", [])
                        combined_winners = list(set(existing_winners + selected_winners))
                        post.metadata["seo"]["winningKeywords"] = combined_winners
                        print(f"🏆 Updated winning keywords: {len(existing_winners)} → {len(combined_winners)}")
                        debug_container.success(f"✅ Step 11: Updated {len(combined_winners)} winning keywords")
                    else:
                        print(f"📝 No winning keywords to update")
                        debug_container.info("📝 No winning keywords selected")
                    
                    # === CRITICAL: FILE WRITING ===
                    file_path = page_info["file_path"]
                    print(f"\n💾 WRITING TO FILE: {file_path}")
                    print(f"📊 About to write {len(post.metadata)} frontmatter fields")
                    print(f"🔍 SEO section has {len(post.metadata['seo'])} fields")
                    print(f"📈 serpAnalysisHistory has {len(post.metadata['seo']['serpAnalysisHistory'])} reports")
                    
                    debug_container.warning("⚠️ Step 12: WRITING FILE - DO NOT REFRESH PAGE!")
                    
                    try:
                        with open(file_path, 'w', encoding='utf-8') as f:
                            content_to_write = frontmatter.dumps(post)
                            f.write(content_to_write)
                        
                        print(f"✅ FILE WRITE SUCCESSFUL!")
                        print(f"📄 Wrote {len(content_to_write)} characters to file")
                        debug_container.success("✅ Step 13: FILE WRITTEN SUCCESSFULLY!")
                        
                        # Verify the write by reading back
                        print(f"🔍 Verifying file write...")
                        with open(file_path, 'r', encoding='utf-8') as f:
                            verification_post = frontmatter.load(f)
                        
                        if "seo" in verification_post.metadata and "serpAnalysisHistory" in verification_post.metadata["seo"]:
                            final_count = len(verification_post.metadata["seo"]["serpAnalysisHistory"])
                            print(f"✅ VERIFICATION SUCCESSFUL: {final_count} reports found in file")
                            debug_container.success(f"✅ Step 14: VERIFICATION PASSED ({final_count} reports)")
                            
                            # Check if our specific report is there
                            found_our_report = any(r.get("reportId") == report_id for r in verification_post.metadata["seo"]["serpAnalysisHistory"])
                            if found_our_report:
                                print(f"🎯 OUR REPORT FOUND IN FILE: {report_id}")
                                debug_container.success(f"✅ Step 15: Our report found in file!")
                            else:
                                print(f"❌ OUR REPORT NOT FOUND IN FILE!")
                                debug_container.error(f"❌ Our report NOT found in verification!")
                        else:
                            print(f"❌ VERIFICATION FAILED: No serpAnalysisHistory in saved file")
                            debug_container.error(f"❌ VERIFICATION FAILED: No serpAnalysisHistory found")
                            
                    except Exception as write_error:
                        print(f"❌ FILE WRITE ERROR: {write_error}")
                        debug_container.error(f"❌ FILE WRITE FAILED: {write_error}")
                        raise write_error
                    
                    post_count = len(post.metadata["seo"]["serpAnalysisHistory"])
                    
                    # === SUCCESS CONFIRMATION ===
                    print(f"\n🎉 SAVE PROCESS COMPLETED SUCCESSFULLY!")
                    print(f"📊 Final report count: {post_count}")
                    print(f"🆔 Saved report ID: {report_id}")
                    print("="*80)
                    
                    st.balloons()  # Visual celebration
                    
                    success_msg = f"🎉 SUCCESSFULLY SAVED '{report_name}' to {selected_page}!"
                    if selected_winners:
                        success_msg += f" with {len(selected_winners)} winning keywords"
                    
                    st.success(success_msg)
                    st.success(f"📈 Report count: {pre_count} → {post_count} reports")
                    st.success(f"📁 Saved to: {file_path}")
                    st.success(f"🆔 Report ID: {report_id}")
                    
                except Exception as e:
                    # === COMPREHENSIVE ERROR LOGGING ===
                    print(f"\n❌ SAVE PROCESS FAILED!")
                    print(f"❌ Error type: {type(e).__name__}")
                    print(f"❌ Error message: {str(e)}")
                    print("="*80)
                    
                    st.error(f"❌ SAVE FAILED: {e}")
                    st.error("🔧 **Debug Info:**")
                    st.error(f"   - Selected page: {selected_page}")
                    st.error(f"   - Report name: {report_name if 'report_name' in locals() else 'Not set'}")
                    st.error(f"   - File path: {page_info.get('file_path', 'Unknown') if 'page_info' in locals() else 'Page info not loaded'}")
                    st.error(f"   - Error type: {type(e).__name__}")
                    st.exception(e)
                    
                    # === SUCCESS CONFIRMATION ===
                    st.balloons()  # Visual celebration
                    
                    success_msg = f"🎉 SUCCESSFULLY SAVED '{report_name}' to {selected_page}!"
                    if selected_winners:
                        success_msg += f" with {len(selected_winners)} winning keywords"
                    
                    st.success(success_msg)
                    st.success(f"� Report count: {pre_count} → {post_count} reports")
                    st.success(f"📁 Saved to: {page_info['file_path']}")
                    st.success(f"🆔 Report ID: {report_id}")
                    
                    # Show detailed report summary
                    with st.expander("📋 Report Summary", expanded=True):
                        st.json({
                            "reportId": report_id,
                            "reportName": report_name,
                            "analysisDate": analysis_date[:19],
                            "filePath": str(page_info["file_path"]),
                            "keywordBreakdown": f"Easy: {easy}, Moderate: {moderate}, Hard: {hard}",
                            "totalReports": post_count
                        })
                    
                    st.info("💡 **Next Steps:**")
                    st.info("1. Refresh TinaCMS admin interface")
                    st.info("2. Navigate to your page in TinaCMS")
                    st.info("3. Check 'SERP Analysis History' section")
                    st.info("4. Your new report should appear in the list!")
                    
                except Exception as e:
                    st.error(f"❌ SAVE FAILED: {e}")
                    st.error("🔧 **Debug Info:**")
                    st.error(f"   - Selected page: {selected_page}")
                    st.error(f"   - Report name: {report_name}")
                    st.error(f"   - File path: {page_info.get('file_path', 'Unknown') if 'page_info' in locals() else 'Page info not loaded'}")
                    st.exception(e)
            
            # Historical Reports Viewer
            if selected_page and existing_reports:
                st.subheader("📈 Historical Reports")
                
                # Report selection
                report_options = []
                for report in existing_reports:
                    date_str = report.get("analysisDate", "")[:10]
                    name = report.get("reportName", "Unnamed Report")
                    report_options.append(f"{name} ({date_str})")
                
                selected_report_idx = st.selectbox(
                    "View Previous Report",
                    range(len(report_options)),
                    format_func=lambda i: report_options[i]
                )
                
                if selected_report_idx is not None:
                    selected_report = existing_reports[selected_report_idx]
                    
                    # Display report details
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Avg Difficulty", f"{selected_report.get('avgDifficulty', 0):.1f}")
                    with col2:
                        st.metric("Easy Keywords", selected_report.get('easyCount', 0))
                    with col3:
                        st.metric("Moderate Keywords", selected_report.get('moderateCount', 0))
                    with col4:
                        st.metric("Hard Keywords", selected_report.get('hardCount', 0))
                    
                    # Show keywords by difficulty
                    if selected_report.get('easyKeywords'):
                        with st.expander(f"Easy Keywords ({len(selected_report['easyKeywords'])})"):
                            for kw in selected_report['easyKeywords']:
                                st.write(f"• {kw}")
                    
                    if selected_report.get('moderateKeywords'):
                        with st.expander(f"Moderate Keywords ({len(selected_report['moderateKeywords'])})"):
                            for kw in selected_report['moderateKeywords']:
                                st.write(f"• {kw}")
                    
                    if selected_report.get('hardKeywords'):
                        with st.expander(f"Hard Keywords ({len(selected_report['hardKeywords'])})"):
                            for kw in selected_report['hardKeywords']:
                                st.write(f"• {kw}")
                    
                    # Show analysis notes and next steps
                    if selected_report.get('analysisNotes'):
                        st.subheader("Analysis Notes")
                        for note in selected_report['analysisNotes']:
                            st.write(f"• {note}")
                    
                    if selected_report.get('nextSteps'):
                        st.subheader("Next Steps")
                        for step in selected_report['nextSteps']:
                            st.write(f"• {step}")
                            
        # PAA display and add-to-selection UX
        if st.session_state.get("last_analysis_data", {}).get("paa_aggregated"):
            st.markdown("---")
            st.subheader("❓ People Also Ask (PAA)")
            agg = st.session_state["last_analysis_data"]["paa_aggregated"]
            st.caption(f"Aggregated across selected queries ({len(agg)} unique)")
            # Show source badges per keyword
            src_map = st.session_state.get("last_analysis_data", {}).get("paa_source_by_keyword", {})
            if src_map:
                with st.expander("PAA sources by keyword", expanded=False):
                    for k, src in src_map.items():
                        badge = (
                            "Google" if src == "google" else (
                                "Headings heuristic" if src == "headings" else (
                                    "Google module missing" if src == "google-missing" else src
                                )
                            )
                        )
                        st.write(f"• {k}: {badge}")
            with st.expander("Show aggregated PAA questions", expanded=False):
                for q in agg:
                    st.write(f"• {q}")
            to_add = st.multiselect("Select PAA to add to your query list", options=agg, default=agg[: min(10, len(agg))])
            if st.button("Add selected PAA to options"):
                # Merge into options and selected, de-dup
                cur_opts = st.session_state.get("options", [])
                cur_sel = st.session_state.get("selected", [])
                new_opts = cur_opts + [q for q in to_add if q not in cur_opts]
                new_sel = cur_sel + [q for q in to_add if q not in cur_sel]
                st.session_state["options"] = new_opts
                st.session_state["selected"] = new_sel
                st.success(f"Added {len(to_add)} PAA queries. They are now available in your selection.")
                st.rerun()

        if st.session_state.get("last_analysis_data", {}).get("related_aggregated"):
            st.markdown("---")
            st.subheader("🔗 Related Searches")
            rel_agg = st.session_state["last_analysis_data"]["related_aggregated"]
            st.caption(f"Aggregated across selected queries ({len(rel_agg)} unique)")
            rel_src_map = st.session_state.get("last_analysis_data", {}).get("related_source_by_keyword", {})
            if rel_src_map:
                with st.expander("Related sources by keyword", expanded=False):
                    for k, src in rel_src_map.items():
                        badge = "Google" if src == "google" else ("Google module missing" if src == "google-missing" else src)
                        st.write(f"• {k}: {badge}")
            with st.expander("Show aggregated related searches", expanded=False):
                for q in rel_agg:
                    st.write(f"• {q}")
            to_add_rel = st.multiselect("Select related searches to add to your query list", options=rel_agg, default=rel_agg[: min(10, len(rel_agg))])
            if st.button("Add selected related to options"):
                cur_opts = st.session_state.get("options", [])
                cur_sel = st.session_state.get("selected", [])
                new_opts = cur_opts + [q for q in to_add_rel if q not in cur_opts]
                new_sel = cur_sel + [q for q in to_add_rel if q not in cur_sel]
                st.session_state["options"] = new_opts
                st.session_state["selected"] = new_sel
                st.success(f"Added {len(to_add_rel)} related searches. They are now available in your selection.")
                st.rerun()

        # Show raw Serper JSON after results (outside status/other expanders nesting)
        if show_raw_serper and st.session_state.get("raw_serper_by_keyword"):
            st.markdown("---")
            st.subheader("🧩 Raw serper.dev JSON")
            raw_map = st.session_state.get("raw_serper_by_keyword", {})
            # Let user pick a keyword to inspect JSON for
            keys = list(raw_map.keys())
            if keys:
                sel = st.selectbox("Select keyword to view raw JSON", options=keys)
                if sel:
                    with st.expander(f"Raw JSON for: {sel}", expanded=False):
                        st.json(raw_map[sel])
                    # Normalized view to always show full structure
                    raw = raw_map[sel] or {}
                    norm = {
                        "knowledgeGraph": raw.get("knowledgeGraph") or {},
                        "organic": raw.get("organic") or [],
                        "peopleAlsoAsk": raw.get("peopleAlsoAsk") or [],
                        "relatedSearches": raw.get("relatedSearches") or [],
                    }
                    st.caption(
                        f"Modules present — KG: {'yes' if raw.get('knowledgeGraph') else 'no'}, "
                        f"PAA: {'yes' if raw.get('peopleAlsoAsk') else 'no'}, "
                        f"Related: {'yes' if raw.get('relatedSearches') else 'no'}"
                    )
                    with st.expander("Normalized structure (empty arrays when missing)", expanded=False):
                        st.json(norm)

        elif selected_page and not save_analysis:
            st.info("💡 Enable 'Save analysis results to selected page' to save results to TinaCMS")
