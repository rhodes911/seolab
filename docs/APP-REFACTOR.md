# Streamlit App Refactor Plan (Monolith → Modules)

This plan breaks `streamlit_app/app.py` into testable modules over time without functional changes. Refactoring is optional and can wait until after plugins stabilize.

## Current pain points
- Large single file with UI + IO + logic intertwined.
- Hard to test individual workflows (seed handling, SERP view, content integration).

## Target module layout
```
streamlit_app/
  app.py                  # thin composition root
  ui/
    layout.py            # headers, expanders, columns
    page_selector.py     # Ellie page discovery + selection
  workflows/
    seeds.py             # seed text input, modifiers, normalization
    serp_view.py         # SERP fetching and difficulty panels (uses services.serp)
    enriched_view.py     # optional table reading enriched CSVs if present
  services/
    content.py           # frontmatter reading/writing (today in app.py)
    serp.py              # existing (fetch_serp, score_serp, etc.)
    state.py             # session state helpers (today in app.py)
```

## Phased refactor
- Phase A: Extract `services/content.py` and `services/state.py` to reduce app.py size.
- Phase B: Move SERP rendering to `workflows/serp_view.py` that consumes `services.serp`.
- Phase C: Create `ui/layout.py` and `ui/page_selector.py` for clarity.
- Phase D: Add `workflows/enriched_view.py` (read-only) that loads `keyword_enriched.csv` if present from latest run.

## Non-goals (for now)
- No changes to business logic or UX.
- No coupling to new plugins; enriched view is optional.

## Testing strategy
- After each extraction, run a smoke test: app loads, page selection works, SERP sections render, no regressions.
- Add minimal unit tests for `services/content.py` (frontmatter parsing) and `services/state.py` utilities.

## Benefits
- Smaller, testable units.
- Clear place to later wire enrichment results if/when desired.
- Safer iterative changes.
