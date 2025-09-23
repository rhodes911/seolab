# Plugins Overview – Keyword Enrichment Layer (Design Spec)

This document defines the plugin architecture, shared contracts, error handling, caching, and the developer workflow to build, test, and run each enrichment plugin in isolation. Code is intentionally omitted; this is the spec.

## Goals
- Stand-alone enrichment providers that accept keywords and return normalized JSON-serializable data.
- No coupling to Streamlit UI or existing pipeline code.
- Optional, fail-safe behavior: missing creds/deps cause empty results, never exceptions.
- Consistent output shape across providers to make merging trivial later.

## Core contract

- Method signatures
  - `enrich_many(keywords: list[str], context: dict | None = None) -> dict[str, dict]`
  - `enrich_keyword(keyword: str, context: dict | None = None) -> dict` (optional convenience)
- Inputs
  - `keywords`: non-empty strings; duplicates are allowed but may be de-duped internally.
  - `context`: optional dictionary, may include:
    - `locale`: e.g., `gb-en`
    - `location`: e.g., `"Camberley, England, United Kingdom"`
    - `site`: domain or property name (for GSC overlay)
    - `date_range`: ISO strings or provider-specific codes
- Outputs (per keyword)
  - A dict of normalized fields for the plugin (see per-plugin docs).
  - Must always be JSON-serializable; numeric types where relevant.
  - On any error, return `{}` for that keyword; do not raise.
  - Include a `source` field (e.g., `"google_trends"`).

## Cross-cutting concerns

- Caching (recommended)
  - Local cache directory: `.cache/plugins/{provider}/{yyyy-mm}/`.
  - Key: `hash(keyword + locale + location + dateBucket)`.
  - TTL: 7–30 days per provider; document per-plugin defaults.
  - Support `context["no_cache"] = True` to bypass.
- Rate limiting & retries
  - Use exponential backoff with jitter.
  - Retry up to 2–3 times on 429/5xx or network errors.
- Logging & observability
  - Emit structured logs (provider, keyword, attempt, result: hit/miss/error).
  - Summarize batch outcomes (counts of hits/misses/errors) when returning.
- Testing
  - Unit: mock HTTP and assert on normalized shapes (see per-plugin test plan).
  - Smoke: read 5–10 keywords from a small fixture and print normalized outputs.
  - Golden fixtures: store known API responses (redacted) and expected normalized outputs.

## Normalized fields (by provider)

- Google Ads – Keyword Plan
  - `volume_tier`: `"<10" | "10-100" | "100-1K" | "1K-10K" | "10K-100K" | ">=100K"`
  - `volume_weight`: float (mapping from tier)
  - `competition_index`: float | null
  - `cpc`: float | null
  - `source`: `"google_ads"`
- Microsoft Bing Ads – Keyword Planner
  - `volume_tier_bing`: string (label)
  - `volume_weight_bing`: float
  - `source`: `"bing_ads"`
- Google Trends
  - `trend_label`: `"declining" | "stable" | "rising" | "surging"`
  - `trend_factor`: `0.9 | 1.0 | 1.15 | 1.25`
  - `seasonality_peaks`: array[int] (indices or months if enriched)
  - `source`: `"google_trends"`
- Google Search Console (CSV overlay)
  - `gsc_impressions`: int
  - `gsc_clicks`: int
  - `gsc_ctr`: float (0–1)
  - `gsc_position`: float
  - `gsc_page`: string | null
  - `quick_win`: bool
  - `source`: `"gsc_csv"`

## Developer workflow

1. Implement a provider in `plugins/<provider_name>/` with the above signatures.
2. Provide a CLI harness under `tools/` that:
   - Reads keywords from a file (JSON list or newline-delimited).
   - Calls `enrich_many` and prints JSON or writes CSV.
   - Supports `--context` JSON blob for locale/location/date.
3. Ship tests and fixtures under `tests/plugins/<provider_name>/`.
4. Document required env vars and optional dependencies in the provider’s README.

## Success criteria
- Given 10 keywords and valid provider configuration, returns normalized dicts for ≥80% within reasonable time and without errors, with caching on repeats.
- With no credentials or missing deps, returns `{}` per keyword (no crashes).
- Test suite passes locally and in CI.
