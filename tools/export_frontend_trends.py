import argparse
import json
import os
import sys
from typing import List, Dict, Any

# Ensure repository root (seolab) is on sys.path so we can import plugins/
_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_REPO_ROOT = os.path.abspath(os.path.join(_THIS_DIR, os.pardir))
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

from plugins.google_trends import GoogleTrendsPlugin  # type: ignore


def _derive_locale_from_seo(seo: Dict[str, Any]) -> str:
    # Attempt to map settings like region: UK and locale: en-GB to plugin's expected 'gb-en'
    region = (seo.get("region") or "").strip().upper()
    locale = (seo.get("locale") or "").strip()
    # Prefer locale when present, else region
    lang = None
    country = None
    if locale:
        # Accept forms like en-GB or en_GB
        parts = locale.replace("_", "-").split("-")
        if len(parts) >= 2:
            lang = parts[0].lower()
            country = parts[1].lower()
    if not country:
        # Map common region strings to ISO country
        region_map = {
            "UK": "gb",
            "GB": "gb",
            "UNITED KINGDOM": "gb",
            "US": "us",
            "USA": "us",
            "UNITED STATES": "us",
        }
        country = region_map.get(region, None)
    if not lang:
        # Default language based on country
        lang = "en"
    if not country:
        country = "us"
    return f"{country}-{lang}"


def _load_frontend_keywords(frontend_root: str) -> Dict[str, Any]:
    """Load keywords and settings from the frontend repo.

    Returns a dict with keys: keywords (List[str]), locale (str)
    """
    seo_path = os.path.join(frontend_root, "content", "settings", "seo.json")
    keywords: List[str] = []
    locale = "us-en"
    try:
        with open(seo_path, "r", encoding="utf-8") as f:
            seo = json.load(f)
        policy = seo.get("keywordPolicy") or {}
        include_always = policy.get("includeAlways") or []
        include_preferred = policy.get("includePreferred") or []
        keywords = [k for k in (include_always + include_preferred) if isinstance(k, str)]
        # derive locale
        locale = _derive_locale_from_seo(seo)
    except FileNotFoundError:
        pass
    except Exception as e:
        print(f"Warning: failed to read seo.json: {e}")

    # Deduplicate, preserve order
    seen = set()
    deduped = []
    for k in keywords:
        if k not in seen and k.strip():
            seen.add(k)
            deduped.append(k.strip())
    return {"keywords": deduped, "locale": locale}


def main():
    parser = argparse.ArgumentParser(description="Export Google Trends for frontend keywords (Next.js site)")
    parser.add_argument(
        "--frontend-root",
        default=os.path.abspath(os.path.join(_REPO_ROOT, os.pardir, "EllieEdwardsMarketingLeadgenSite")),
        help="Path to the frontend repository root"
    )
    parser.add_argument(
        "--date-range",
        default="today 12-m",
        help="Pytrends timeframe (e.g., 'today 12-m', 'today 5-y')"
    )
    parser.add_argument(
        "--no-cache",
        action="store_true",
        help="Bypass local cache"
    )
    parser.add_argument(
        "--out",
        default=None,
        help="Output file (.json). Defaults to <frontend-root>/data/keywords/trends.json"
    )
    args = parser.parse_args()

    frontend_root = os.path.abspath(args.frontend_root)
    info = _load_frontend_keywords(frontend_root)
    keywords: List[str] = info.get("keywords", [])
    locale: str = info.get("locale", "us-en")

    if not keywords:
        print("No keywords found in frontend seo.json (keywordPolicy.includeAlways/includePreferred). Nothing to do.")
        return 0

    context = {
        "locale": locale,
        "date_range": args.date_range,
        "no_cache": bool(args.no_cache),
    }

    plugin = GoogleTrendsPlugin()
    results = plugin.enrich_many(keywords, context=context)

    out_path = args.out
    if not out_path:
        out_path = os.path.join(frontend_root, "data", "keywords", "trends.json")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    print(out_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
