# Google Search Console CSV Overlay – Design & Test Plan

A simple plugin that reads a local GSC CSV export and returns first-party visibility metrics for given keywords. This avoids OAuth complexity initially and supports the “Quick Win” heuristic.

## Purpose
- Attach `impressions/clicks/ctr/position/page` per keyword when available.
- Mark `quick_win` if `impressions > 50` and `8 ≤ position ≤ 20`.

## Inputs
- `keywords: list[str]`
- `context: dict` (optional)
  - `csv_path`: explicit CSV path; else read from `GSC_EXPORT_CSV` env var.
  - `site`: optional domain filter (if CSV contains multiple sites; otherwise ignored).

## Expected CSV columns
- `query` (string)
- `impressions` (int)
- `clicks` (int)
- `ctr` (percentage or fraction – plugin normalizes to fraction 0–1)
- `position` (float)
- `page` (landing page URL, optional)

## Outputs (per keyword)
- `gsc_impressions`: int
- `gsc_clicks`: int
- `gsc_ctr`: float (0–1)
- `gsc_position`: float
- `gsc_page`: string | null
- `quick_win`: bool
- `source`: `"gsc_csv"`

## Behavior
- Lower-case and strip the `query` field before matching.
- Build an in-memory dict from CSV: `query → metrics`.
- For each input keyword (lowercased), return metrics if present; else `{}`.
- Quick win rule: `impressions > 50 && 8 ≤ position ≤ 20`.

## Error handling
- Missing file or bad CSV: return `{}` for all and log a warning.
- Missing/invalid numeric fields: coerce to 0 or `None`.

## Caching
- Caching not required (local file), but can keep a simple in-process cache keyed by `csv_path` mtime.

## Testing

### Unit tests
- CSV fixture with rows:
  - `query,impressions,clicks,ctr,position,page`
  - Include one query with impressions=180, position=13 → expect `quick_win=true`.
  - Include mixed-case queries to ensure case-insensitive matching.
  - Missing/blank fields should not break; default to zeros.
- Empty/missing CSV path → `{}` for all keywords.

### Smoke test
- Provide a small CSV; run plugin on 3–5 keywords and print outputs.

### CLI harness
- Flags: `--csv path`, `--keywords-file`, `--out`.
- Outputs JSON/CSV.

## Env
- `GSC_EXPORT_CSV` optional; otherwise pass `csv_path`.

## Notes
- Later phases may replace or augment with OAuth-based Search Console API queries.
- If CSV includes multiple properties, add a `site` filter in context.
