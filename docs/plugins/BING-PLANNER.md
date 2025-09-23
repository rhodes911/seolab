# Microsoft Bing Ads – Keyword Planner Plugin – Design & Test Plan

This plugin mirrors the Google Ads mapping so that Bing can act as a cross-check for demand. Keep schema consistent.

## Purpose
- Retrieve Bing Keyword Planner data for the provided keywords.
- Normalize to `volume_tier_bing` and `volume_weight_bing`.

## Inputs
- `keywords: list[str]`
- `context: dict` (optional)
  - `locale`, `location`, `date_range`, `no_cache` (same semantics as Ads)

## Outputs (per keyword)
- `volume_tier_bing`: string
- `volume_weight_bing`: float
- `source`: `"bing_ads"`

## Tier mapping
- Use the same mapping as Google Ads; document any differences the API implies.

## Behavior
- Authenticate against Microsoft Advertising API.
- Request keyword ideas/ranges.
- Map ranges → tiers → `volume_weight_bing`.

## Error handling
- Missing creds/SDK → `{}` per keyword.
- Rate limits/5xx → retry then `{}`.

## Caching
- `.cache/plugins/bing_ads/{yyyy-mm}/`, hash of keyword+locale+location+date.
- TTL: 30 days.

## Testing

### Unit tests (mocked API)
- Verify tier mapping identical to Ads mapping.
- Ensure graceful behavior on missing fields and partial responses.

### Smoke test
- 3–5 keywords; print outputs; verify cache on repeat.

### CLI harness
- Flags mirror Ads.

## Env & install
- Microsoft Advertising SDK or REST + OAuth configuration.
- Document required env vars (client ID/secret/tenant as applicable).

## Notes
- If access is difficult initially, implement a file-backed mock mode to validate the interface and combining logic.
