# Google Trends Plugin – Design & Test Plan

This spec defines a light, reliable adapter around Google Trends via `pytrends` that returns trend factors and basic seasonality for a list of keywords. No UI coupling.

## Purpose
- Provide temporal context: rising, stable, declining.
- Derive a numeric `trend_factor` multiplier for the fusion scorer.
- Optional: rough `seasonality_peaks` for planning.

## Inputs
- `keywords: list[str]`
- `context: dict` (optional)
  - `locale` (default `gb-en` → pytrends `geo = "GB"`)
  - `date_range` (default `today 12-m`)
  - `no_cache` (bool)

## Outputs (per keyword)
- `trend_label`: `declining | stable | rising | surging`
- `trend_factor`: `0.9 | 1.0 | 1.15 | 1.25`
- `seasonality_peaks`: array[int] – indices of top 1–2 weeks (or months) in the time window
- `source`: `"google_trends"`

## Behavior
- Use `pytrends.TrendReq(hl="en-GB", tz=0)`.
- `build_payload([keyword], timeframe="today 12-m", geo="GB")` by default.
- Fetch `interest_over_time()` → series of ints.
- Compute label + factor using simple deltas:
  - Compare recent mean (last 5 points) to overall mean.
  - `delta >= +50% → surging` → `1.25`
  - `+10% ≤ delta < +50% → rising` → `1.15`
  - `-15% ≥ delta → declining` → `0.9`
  - else → `stable` → `1.0`
- `seasonality_peaks` = indices of top 2 values.

## Error handling
- Missing `pytrends`: return `{}`.
- HTTP errors, captchas, empty frames: return `{}`.
- Never raise; log and continue.

## Caching
- Directory: `.cache/plugins/google_trends/{yyyy-mm}/`.
- Key: hash(keyword + locale + date_range).
- TTL: 30 days.
- Allow `context.no_cache = True` to bypass.

## Testing

### Unit tests (mocked pytrends)
- Given a fixed series, assert the expected `trend_label` and `trend_factor`:
  - Rising case (delta +20%) → `rising`, `1.15`
  - Surging case (+60%) → `surging`, `1.25`
  - Declining case (−20%) → `declining`, `0.9`
  - Stable case (±<10%) → `stable`, `1.0`
- Missing pytrends import → `{}` per keyword.
- Empty dataframe → `{}`.

### Smoke test (real, optional)
- Input keywords: `seo camberley`, `web design surrey`
- Print JSON outputs; confirm presence of `trend_label` & `trend_factor`.
- Run twice; confirm second run uses cache (timing/log check).

### CLI harness (tools/trends_cli.md)
- Accept `--keywords-file`, `--locale`, `--date-range`, `--no-cache`.
- Output JSON to stdout or `--out` CSV.

## Env & install
- `pip install pytrends`
- No API keys required.

## Limits & notes
- pytrends is unofficial; be gentle with rate limits.
- For multi-year seasonality, adjust `timeframe` (e.g., `today 5-y`) and compute peaks per month instead of raw indices.
