# Trends CLI – Spec for Developer Harness (No Code)

This document specifies a tiny command-line utility to run the Google Trends plugin in isolation for smoke tests and demos.

## Command

```text
trends-cli --keywords-file <path> [--locale gb-en] [--date-range "today 12-m"] [--no-cache] [--out out.json|out.csv]
```

## Behavior
- Read keywords from file:
  - JSON array: ["seo camberley", "web design surrey"]
  - or newline-delimited text
- Build context from flags:
  - `locale` → pytrends `geo`: `gb-en` → `GB`; otherwise map `us-en` → `US`, etc.
  - `date-range` → pytrends timeframe string.
  - `no-cache` → bypass local cache.
- Call plugin `enrich_many(keywords, context)`.
- Output format:
  - Default JSON to stdout: `{ "seo camberley": {"trend_label":"rising", ...}, ... }`
  - If `--out out.csv`, write a CSV with columns: keyword, trend_label, trend_factor, seasonality_peaks, source.
- Exit code:
  - 0 on success (even if all results empty).
  - Non-zero only for CLI misuse (missing file, unreadable input), not for API errors.

## Examples

```text
trends-cli --keywords-file sample_keywords.json
trends-cli --keywords-file sample_keywords.txt --locale gb-en --date-range "today 5-y" --out trends.csv
trends-cli --keywords-file sample_keywords.txt --no-cache
```

## Notes
- This CLI is for developer workflows and CI smoke tests; not a user-facing tool.
- Keep runtime dependencies minimal: `pytrends` and `pandas` (transitive).
