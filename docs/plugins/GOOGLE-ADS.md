# Google Ads – Keyword Plan Plugin (Ranges to Tiers) – Design & Test Plan

This plugin converts Google Ads Keyword Plan data into normalized demand tiers and weights. Start with ranges and avoid exact volume dependencies.

## Purpose
- Expand seeds (optionally) and/or accept keywords.
- Retrieve average monthly search ranges and competition if available.
- Normalize into demand tiers and a `volume_weight` for scoring.

## Inputs
- `keywords: list[str]`
- `context: dict` (optional)
  - `locale` (e.g., `gb-en`)
  - `location` (Geo target) – optional
  - `date_range` – optional
  - `no_cache` – optional

## Outputs (per keyword)
- `volume_tier`: `"<10" | "10-100" | "100-1K" | "1K-10K" | "10K-100K" | ">=100K"`
- `volume_weight`: float
- `competition_index`: float | null (0–1 scale) if available
- `cpc`: float | null (avg CPC if available)
- `source`: `"google_ads"`

## Tier mapping (defaults)
- `<10` → 0.0
- `10-100` → 0.6
- `100-1K` → 1.0
- `1K-10K` → 1.3
- `10K-100K` → 1.5
- `>=100K` → 1.7

## Behavior
- Authenticate via Google Ads SDK (service account or OAuth config file).
- Use Keyword Ideas / Keyword Plan endpoints to fetch ranges for given keywords.
- Convert returned ranges to tiers by midpoint or min-bound; document choice and be consistent.
- Derive `volume_weight` from tier mapping.
- Include `competition_index` and `cpc` if available; otherwise null.

## Error handling
- Missing SDK/creds or quota errors → return `{}` per keyword.
- Timeouts/429/5xx → backoff-retry, then `{}`.

## Caching
- `.cache/plugins/google_ads/{yyyy-mm}/` with hash of keyword+locale+location+date.
- TTL: 30 days.

## Testing

### Unit tests (mocked SDK)
- Given a set of range responses, ensure correct tier mapping and `volume_weight`.
- Missing fields → default tier `<10` → `0.0`.
- Competition and CPC gracefully optional.

### Smoke test
- Provide a small list of keywords (3–5) and print normalized outputs.
- Run twice; confirm cache hit.

### CLI harness
- Flags: `--keywords-file`, `--locale`, `--location`, `--no-cache`.
- Output JSON/CSV.

## Env & install
- `pip install google-ads`
- `GOOGLE_ADS_CONFIGURATION_FILE` or `GOOGLE_ADS_JSON`

## Notes
- If you want seed expansion here, accept `seed_sites` or `seed_keywords` and leverage Ads suggestion endpoints. Keep that optional to avoid overreach.
- If Ads is too heavy, keep the interface but allow a lightweight test mode that reads mocked data from disk.
