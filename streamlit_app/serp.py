from __future__ import annotations
import json
import re
import time
from dataclasses import dataclass
from typing import List, Dict, Any, Optional, Tuple
from urllib.parse import urlparse, parse_qs, unquote

import requests


@dataclass
class SerpResult:
    title: str
    link: str
    snippet: str


def _ddg_unwrap(url: str) -> str:
    try:
        # DuckDuckGo sometimes wraps links as /l/?uddg=<encoded>
        if "/l/?" in url:
            qs = parse_qs(urlparse(url).query)
            if "uddg" in qs:
                return unquote(qs["uddg"][0])
    except Exception:
        pass
    return url


def fetch_serp(query: str, provider: str = "duckduckgo", api_key: Optional[str] = None, num: int = 10, locale: str = "gb-en") -> List[SerpResult]:
    """Fetch SERP results for a query.

    provider: 'serper' (Google via serper.dev) or 'duckduckgo' (HTML fallback, no key).
    locale: e.g., 'gb-en'. For serper, we'll set gl=gb, hl=en. For DDG, kl=uk-en.
    """
    results: List[SerpResult] = []
    if provider == "serper" and api_key:
        url = "https://google.serper.dev/search"
        payload = {
            "q": query,
            "gl": "gb",
            "hl": "en",
            "num": min(20, max(1, int(num))),
        }
        try:
            r = requests.post(url, headers={"X-API-KEY": api_key, "Content-Type": "application/json"}, data=json.dumps(payload), timeout=15)
            r.raise_for_status()
            data = r.json()
            for item in (data.get("organic") or [])[:num]:
                results.append(SerpResult(
                    title=item.get("title") or "",
                    link=item.get("link") or "",
                    snippet=item.get("snippet") or "",
                ))
        except Exception:
            # fall back to ddg
            pass
    if not results:
        # DuckDuckGo HTML fallback
        try:
            kl = "uk-en" if locale.lower().startswith("gb") else "us-en"
            url = f"https://html.duckduckgo.com/html/?q={requests.utils.quote(query)}&kl={kl}"
            r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=15)
            r.raise_for_status()
            # Lazy import to avoid static resolution issues
            try:
                from bs4 import BeautifulSoup  # type: ignore
            except Exception:
                return results
            soup = BeautifulSoup(r.text, "html.parser")
            # DDG HTML results: a.result__a, snippet in .result__snippet
            for res in soup.select("div.result"):
                a = res.select_one("a.result__a")
                if not a:
                    continue
                href = _ddg_unwrap(a.get("href") or "")
                title = a.get_text(strip=True)
                snippet_el = res.select_one("a.result__snippet") or res.select_one("div.result__snippet")
                snippet = snippet_el.get_text(" ", strip=True) if snippet_el else ""
                if href and title:
                    results.append(SerpResult(title=title, link=href, snippet=snippet))
                if len(results) >= num:
                    break
        except Exception:
            pass
    return results


def fetch_serper_json(
    query: str,
    api_key: str,
    num: int = 10,
    locale: str = "gb-en",
    location: Optional[str] = None,
    no_cache: bool = False,
    timeout: int = 15,
) -> Dict[str, Any]:
    """Fetch raw serper.dev JSON for a query (Google results).

    Returns the JSON dict as returned by serper.dev Search API.
    """
    url = "https://google.serper.dev/search"
    payload = {
        "q": query,
        "gl": "gb" if locale.lower().startswith("gb") else "us",
        "hl": "en",
        "num": min(20, max(1, int(num))),
    }
    if location:
        payload["location"] = location
    if no_cache:
        payload["no_cache"] = True
    r = requests.post(
        url,
        headers={"X-API-KEY": api_key, "Content-Type": "application/json"},
        data=json.dumps(payload),
        timeout=timeout,
    )
    r.raise_for_status()
    return r.json()


def fetch_page_headings(url: str, timeout: int = 15) -> Dict[str, Any]:
    out: Dict[str, Any] = {"url": url, "title": "", "h1": [], "h2": []}
    try:
        r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=timeout)
        r.raise_for_status()
        try:
            from bs4 import BeautifulSoup  # type: ignore
        except Exception:
            return out
        soup = BeautifulSoup(r.text, "html.parser")
        t = soup.title.get_text(strip=True) if soup.title else ""
        out["title"] = t
        out["h1"] = [h.get_text(" ", strip=True) for h in soup.find_all("h1") if h.get_text(strip=True)]
        out["h2"] = [h.get_text(" ", strip=True) for h in soup.find_all("h2") if h.get_text(strip=True)]
    except Exception:
        pass
    return out


def score_serp(results: List[SerpResult], seed: str) -> Dict[str, Any]:
    """Compute simple difficulty heuristics for a SERP."""
    seed_l = seed.lower()
    domains = []
    exact_in_title = 0
    gov_edu = 0
    aggregators = 0
    aggregator_hosts = {
        "yell.com", "trustpilot.com", "clutch.co", "bark.com", "upwork.com", "fiverr.com",
        "facebook.com", "linkedin.com", "maps.google.", "business.site"
    }
    strong_info = {"wikipedia.org", "moz.com", "ahrefs.com", "backlinko.com", "hubspot.com", "semrush.com", "searchenginejournal.com"}
    strong_count = 0

    for r in results:
        try:
            host = urlparse(r.link).netloc.lower()
        except Exception:
            host = ""
        if host:
            domains.append(host)
            if host.endswith(".gov") or host.endswith(".gov.uk") or host.endswith(".edu"):
                gov_edu += 1
            if any(h in host for h in aggregator_hosts):
                aggregators += 1
            if any(h in host for h in strong_info):
                strong_count += 1
        if seed_l in (r.title or "").lower():
            exact_in_title += 1

    unique_domains = len(set(domains))
    n = max(1, len(results))

    # Simple difficulty scoring (0 easy → 100 hard)
    # Start with baseline 50, add penalties for strong sites/gov/edu and low exact-in-title, add aggregator penalty.
    score = 50
    score += 10 * min(3, strong_count)  # strong info sites present
    score += 8 * min(2, gov_edu)
    score += 4 * min(3, aggregators)
    if exact_in_title <= n * 0.2:
        score += 10  # few exact matches suggests broader/ambiguous SERP
    if unique_domains < n * 0.5:
        score += 8  # domain dominance
    score = max(0, min(100, score))

    return {
        "unique_domains": unique_domains,
        "exact_in_title": exact_in_title,
        "gov_edu": gov_edu,
        "aggregators": aggregators,
        "strong_info": strong_count,
        "difficulty": score,
    }


def fetch_paa_questions(
    query: str,
    provider: str = "serper",
    api_key: Optional[str] = None,
    results: Optional[List[SerpResult]] = None,
    outlines: Optional[List[Dict[str, Any]]] = None,
    raw: Optional[Dict[str, Any]] = None,
    require_google_only: bool = False,
    timeout: int = 15,
) -> Tuple[List[str], str]:
    """Fetch People Also Ask (PAA) questions for a query.

    Strategy:
    - If provider is serper and api_key is provided, call serper.dev and read peopleAlsoAsk[].question
    - Fallback: extract question-like headings from provided outlines or top result pages
    """
    questions: List[str] = []
    source: str = "none"

    # Try serper.dev first
    if raw is not None:
        try:
            paa = raw.get("peopleAlsoAsk") or []
            for item in paa:
                q = (item.get("question") or "").strip()
                if q:
                    questions.append(q)
            if questions:
                source = "google"
            elif require_google_only:
                # Explicitly do not fallback; indicate Google module missing
                return [], "google-missing"
        except Exception:
            pass
    elif provider == "serper" and api_key:
        try:
            url = "https://google.serper.dev/search"
            payload = {"q": query, "gl": "gb", "hl": "en", "num": 10}
            r = requests.post(
                url,
                headers={"X-API-KEY": api_key, "Content-Type": "application/json"},
                data=json.dumps(payload),
                timeout=timeout,
            )
            r.raise_for_status()
            data = r.json()
            paa = data.get("peopleAlsoAsk") or []
            for item in paa:
                q = (item.get("question") or "").strip()
                if q:
                    questions.append(q)
            if questions:
                source = "google"
        except Exception:
            pass

    # Fallback: infer from outlines/headings
    def looks_like_question(s: str) -> bool:
        s2 = s.strip()
        if not s2:
            return False
        if s2.endswith("?"):
            return True
        lower = s2.lower()
        prefixes = (
            "what ", "how ", "why ", "who ", "where ", "when ",
            "can ", "should ", "does ", "do ", "is ", "are ", "will ", "could ", "would ", "which ",
        )
        return any(lower.startswith(p) for p in prefixes)

    collected: List[str] = []
    # Use outlines if provided
    if outlines:
        for o in outlines:
            for tag in ("h1", "h2", "h3"):
                for h in (o.get(tag) or []):
                    if isinstance(h, str) and looks_like_question(h):
                        collected.append(h.strip())

    # If no outlines provided, fetch a few page headings
    if not collected and results:
        for res in results[:3]:
            try:
                page = fetch_page_headings(res.link, timeout=timeout)
                for tag in ("h1", "h2", "h3"):
                    for h in (page.get(tag) or []):
                        if isinstance(h, str) and looks_like_question(h):
                            collected.append(h.strip())
            except Exception:
                continue

    # Merge
    if collected:
        questions.extend(collected)
        if source == "none":
            source = "headings"

    # Dedupe while preserving order
    seen = set()
    deduped: List[str] = []
    for q in questions:
        qn = q.strip()
        key = qn.lower().rstrip("? ")
        if key and key not in seen:
            seen.add(key)
            deduped.append(qn if qn.endswith("?") else qn + "?")

    # Limit to reasonable number
    return deduped[:20], source


def fetch_related_searches(
    query: str,
    provider: str = "serper",
    api_key: Optional[str] = None,
    raw: Optional[Dict[str, Any]] = None,
    require_google_only: bool = False,
    timeout: int = 15,
) -> Tuple[List[str], str]:
    """Fetch Related Searches for a query.

    Returns (queries, source) where source is 'google' when from serper.dev, else 'none'.
    """
    related: List[str] = []
    source = "none"
    if raw is not None:
        try:
            rs = raw.get("relatedSearches") or []
            for item in rs:
                q = (item.get("query") or "").strip()
                if q:
                    related.append(q)
            if related:
                source = "google"
            elif require_google_only:
                return [], "google-missing"
        except Exception:
            pass
    elif provider == "serper" and api_key:
        try:
            url = "https://google.serper.dev/search"
            payload = {"q": query, "gl": "gb", "hl": "en", "num": 10}
            r = requests.post(
                url,
                headers={"X-API-KEY": api_key, "Content-Type": "application/json"},
                data=json.dumps(payload),
                timeout=timeout,
            )
            r.raise_for_status()
            data = r.json()
            rs = data.get("relatedSearches") or []
            for item in rs:
                q = (item.get("query") or "").strip()
                if q:
                    related.append(q)
            if related:
                source = "google"
        except Exception:
            pass
    # Dedupe and cap
    seen = set()
    out: List[str] = []
    for q in related:
        key = q.lower()
        if key and key not in seen:
            seen.add(key)
            out.append(q)
    return out[:20], source
