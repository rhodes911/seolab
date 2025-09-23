# Orchestrator – Enrichment Runner (Design Spec)

This doc specifies a runner that consumes keywords from an existing pipeline run and produces enriched outputs. It doesn’t change the Streamlit app or pipeline—pure add-on.

## Purpose
- Read the latest (or a specified) `reports/keyword_runs/<timestamp>/keywords_scored.csv`.
- For those keywords, call selected plugins (Trends, GSC CSV, Ads, Bing) and optionally Serper JSON for SERP-derived ratios.
- Compute a fused `opportunity_score` and a `recommendation` for each keyword.
- Write enriched CSVs next to existing artifacts.

## Inputs
- `run_dir`: path to a specific run folder; or auto-detect latest.
- `plugins`: which providers to include (by name).
- `serper_api_key`: optional; if provided, fetch SERPER JSON to derive intent ratios and use `score_serp` for difficulty.
- `locale`, `location`: optional context.

## Outputs
- `keyword_enriched.csv`: full table including plugin fields + `opportunity_score` + `recommendation`.
- `area_service_opportunities.csv`: filtered subset (recommendation == `area_service_page`).

## Fusion scoring (defaults)
```
score = volume_weight × trend_factor × (1 + quick_win_boost) × intent_weight ÷ competition_proxy
```
- `volume_weight`: Ads first, fallback to Bing weight; 0.0 if neither.
- `trend_factor`: from Trends or default 1.0 if absent.
- `quick_win_boost`: +0.25 when `quick_win=true`.
- `intent_weight`: ×1.3 when `local_pack=true` AND intent suggests service (transactional/commercial).
- `competition_proxy`: 1.0–2.0 scaled from `difficulty` (1 + difficulty/100).

## Decision rules
- `area_service_page`: `local_pack` and `service_ratio ≥ 0.5` and `score ≥ 0.6`.
- `guide_or_blog`: `blog_ratio > service_ratio` and no `local_pack`.
- `citations_focus`: `directories_ratio > 0.5`.
- `deprioritise`: `volume=0` OR (`trend_label=declining` and `gsc_impressions=0`).
- else: `evaluate`.

## SERPER-derived fields (optional)
- From raw Serper JSON (`organic`, `peopleAlsoAsk`, `related`, `localResults`):
  - `local_pack` (bool)
  - `service_ratio`, `blog_ratio`, `directories_ratio` (heuristics by URL patterns/baselists)
  - `difficulty`: reuse existing `score_serp` on top results

## Execution flow
1. Read keywords from `keywords_scored.csv`.
2. Build a `context` dict from CLI flags and env.
3. For each chosen plugin, call `enrich_many` on all keywords; merge by keyword.
4. If `serper_api_key`, fetch SERPER JSON per keyword (cap to first N=100) and derive SERP features; reuse `score_serp` for `difficulty`.
5. Compute `opportunity_score` + `recommendation` for each keyword.
6. Write `keyword_enriched.csv` and `area_service_opportunities.csv`.

## Testing
- Dry run mode: `--plugins none` just copies inputs to enriched CSV with default scores (all 0) to validate format.
- Deterministic fixtures: scripted inputs → expected outputs for scorer and recommendation rules.
- CLI smoke test against 5 sample keywords with only Trends and/or GSC CSV.

## Safety
- All providers optional; if none present, orchestrator still writes a CSV with default columns.
- Serper JSON is rate-limited and capped; skip if missing.
- Never mutates existing artifacts; only adds new files.
