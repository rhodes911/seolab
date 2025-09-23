from __future__ import annotations
import hashlib
import json
import os
import time
from typing import Any, Dict, List, Optional

from .base import PluginBase, EnrichmentResult


def _geo_from_locale(locale: str | None) -> str:
    if not locale:
        return ""
    loc = locale.lower()
    if loc.startswith("gb"):
        return "GB"
    if loc.startswith("us"):
        return "US"
    # Add more as needed; empty means worldwide
    return ""


def _label_and_factor(series: List[int]) -> tuple[str, float]:
    if not series:
        return "stable", 1.0
    overall = sum(series) / max(1, len(series))
    recent = sum(series[-5:]) / max(1, min(5, len(series)))
    if overall == 0:
        return "stable", 1.0
    delta = (recent - overall) / overall
    if delta >= 0.5:
        return "surging", 1.25
    if delta >= 0.1:
        return "rising", 1.15
    if delta <= -0.15:
        return "declining", 0.9
    return "stable", 1.0


class GoogleTrendsPlugin(PluginBase):
    name = "google_trends"

    def __init__(self, cache_dir: Optional[str] = None, **kwargs):
        super().__init__(**kwargs)
        self.cache_dir = cache_dir or os.path.join(os.path.dirname(__file__), "..", ".cache", "plugins", "google_trends")
        try:
            from pytrends.request import TrendReq  # type: ignore  # noqa: F401
            self._available = True
        except Exception:
            self._available = False

    def _cache_path(self, keyword: str, locale: str, timeframe: str) -> str:
        ym = time.strftime("%Y-%m")
        base = os.path.abspath(os.path.join(self.cache_dir, ym))
        os.makedirs(base, exist_ok=True)
        key = f"{keyword}\u0001{locale}\u0001{timeframe}"
        h = hashlib.sha1(key.encode("utf-8")).hexdigest()
        return os.path.join(base, f"{h}.json")

    def _cache_read(self, path: str, ttl_days: int) -> Optional[Dict[str, Any]]:
        try:
            if not os.path.isfile(path):
                return None
            st = os.stat(path)
            age_days = (time.time() - st.st_mtime) / 86400.0
            if age_days > float(ttl_days):
                return None
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return None

    def _cache_write(self, path: str, data: Dict[str, Any]) -> None:
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False)
        except Exception:
            pass

    def enrich_keyword(self, keyword: str, context: Optional[Dict[str, Any]] = None) -> EnrichmentResult:
        if not self._available:
            return EnrichmentResult(keyword, {})

        ctx = context or {}
        locale = ctx.get("locale") or "gb-en"
        timeframe = ctx.get("date_range") or "today 12-m"
        no_cache = bool(ctx.get("no_cache"))
        geo = _geo_from_locale(locale)

        cache_path = self._cache_path(keyword, locale, timeframe)
        if not no_cache:
            cached = self._cache_read(cache_path, ttl_days=30)
            if cached is not None:
                return EnrichmentResult(keyword, cached)

        # derive hl like 'en-GB' from locale 'gb-en' or 'us-en'
        def _hl_from_locale(loc: str) -> str:
            loc = (loc or "").lower()
            parts = loc.split("-")
            if len(parts) >= 2:
                cc, lang = parts[0], parts[1]
                return f"{lang}-{cc.upper()}"
            return "en-US"

        hl = _hl_from_locale(locale)
        try:
            from pytrends.request import TrendReq  # type: ignore
            # small retry loop to mitigate transient empty frames / rate limits
            last_exc: Optional[Exception] = None
            for _ in range(3):
                try:
                    pytrends = TrendReq(hl=hl, tz=0)
                    pytrends.build_payload([keyword], timeframe=timeframe, geo=geo)
                    df = pytrends.interest_over_time()
                    if df is not None and not df.empty and (keyword in df):
                        series = [int(x) for x in df[keyword].fillna(0).tolist()]
                        label, factor = _label_and_factor(series)
                        top_idx = sorted(range(len(series)), key=lambda i: series[i], reverse=True)[:2]
                        out = {
                            "trend_label": label,
                            "trend_factor": factor,
                            "seasonality_peaks": top_idx,
                            "source": self.name,
                        }
                        self._cache_write(cache_path, out)
                        return EnrichmentResult(keyword, out)
                except Exception as e:  # transient
                    last_exc = e
                time.sleep(1.5)
            # If we got here, return empty result
            return EnrichmentResult(keyword, {})
        except Exception:
            return EnrichmentResult(keyword, {})
