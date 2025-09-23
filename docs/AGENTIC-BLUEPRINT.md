# Agentic SEO Workflow – Blueprint (Living Doc)

This document sketches how independent enrichment plugins and the Streamlit UI evolve into an agentic, end-to-end SEO workflow. It's intentionally vendor-agnostic and incremental.

## Goals
- Orchestrate tasks across data sources (SERP, Trends, GSC, Ads/Bing) and internal content graph.
- Make decisions autonomously with transparent heuristics and guard rails.
- Keep each capability useful on its own (plugin-first), but composable.

## Building blocks
- Plugins (enrichment layer):
  - google_trends: temporal interest labels and seasonality.
  - gsc_csv: overlay site performance metrics per keyword.
  - google_ads / bing_planner: demand tiers and CPC (future).
- Streamlit app: seed → expand → select → analyze + plugin pages.
- Orchestrator (CLI or service): batch runner and fusion scorer.
- Frontend adapter: exports for the Next.js site (e.g., `trends.json`).

## Execution graph (concept)
1. Keyword intake
   - Sources: existing content pages, sitemap, analytics, manual seeds, TinaCMS settings.
2. Normalization/expansion
   - Apply prefix/suffix/location libraries; de-dup; cap per seed.
3. Enrichment fan-out (parallel where possible)
   - Trends, GSC, Ads/Bing, SERPER JSON (optional), internal link graph.
4. Fusion & ranking
   - Compute opportunity_score using weights from: demand, difficulty, temporal trend, your site position/CTR.
5. Recommendations
   - Page type suggestion, intent alignment, cluster membership, next actions.
6. Actions & exports
   - Update frontmatter (winningKeywords, analysis blocks), generate CSV/JSON, create tickets.

## Agent loop (future)
- Observe: periodic refresh; detect shifts (position drops, trend surges).
- Orient: recompute scores; compare to thresholds and backlog.
- Decide: pick next N opportunities; choose action types per page (create, expand, consolidate).
- Act: draft outlines/FAQs; update TinaCMS content; open PRs.

## Data contracts (summary)
- Plugin outputs: normalized fields per provider with `source` and safe empty-on-failure behavior.
- Orchestrator input/output:
  - Input: `keywords_scored.csv` (from pipeline) or a flat keyword list.
  - Output: `keyword_enriched.csv`, `area_service_opportunities.csv`.

## Safety & observability
- Caching by provider; retries with exponential backoff.
- Dry runs; explicit `no_cache` flag.
- Structured logs with per-plugin summaries; CI smoke tests.

## Roadmap
- [x] google_trends plugin + page + CLI + frontend export.
- [x] gsc_csv plugin + page + CLI.
- [ ] google_ads / bing_planner plugins.
- [ ] Orchestrator runner v1 (merge + score + export).
- [ ] Agent loop with pluggable policies, PR automation (Git, Tina).

> Keep this doc updated as pieces land. Small, composable steps win.
