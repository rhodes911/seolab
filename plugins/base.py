from __future__ import annotations
import json
from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class EnrichmentResult:
    keyword: str
    data: Dict[str, Any]


class PluginBase:
    name: str = "base"

    def __init__(self, **kwargs):
        self.config = kwargs

    def enrich_keyword(self, keyword: str, context: Optional[Dict[str, Any]] = None) -> EnrichmentResult:
        """Enrich a single keyword; never raise on failures."""
        return EnrichmentResult(keyword=keyword, data={})

    def enrich_many(self, keywords: list[str], context: Optional[Dict[str, Any]] = None) -> dict[str, dict]:
        out: dict[str, dict] = {}
        for k in keywords:
            try:
                res = self.enrich_keyword(k, context=context)
                out[k] = res.data or {}
            except Exception:
                out[k] = {}
        return out
