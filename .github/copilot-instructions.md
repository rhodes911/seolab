# Copilot: Repository Instructions for seolab

These instructions apply to all suggestions and edits in this repository. Follow the project spec in `README.md` and the step-by-step plan in `BUILD_PLAN.md`. Prefer concrete edits over advice.

## Prime directives

- Obey `README.md` architecture: Streamlit app under `streamlit_app/` rendering Markdown from `content/**`, local-only progress in JSON, no external services.
- Execute work in the order of `BUILD_PLAN.md`. For each task: scope → implement minimal slice → validate → commit → tick the plan.
- Keep changes local-first and privacy-safe. No external services unless explicitly opted-in.

## Ground rules

- Folder layout: `streamlit_app/**` (app.py, state.py, components.py, styles.css, pages/), `content/**` for Markdown lessons, `.github/**` for CI and repo guidance.
- Theming/styling: keep CSS in `streamlit_app/styles.css` and minimal inline CSS via `inject_styles`.
- Progress: use `streamlit_app/state.py` with a local JSON file (`progress.json`) and provide export/import.
- Accessibility: clear headings, readable defaults, keyboard-friendly controls.

## Quality gates

- CI validates that the content loader can index lessons without errors.
- Keep any tests fast and deterministic.

## Commit and PR etiquette

- Prefer small, focused commits. Reference the BUILD_PLAN step. Update docs when behavior changes.

## If in doubt

- Re-check `README.md` and `BUILD_PLAN.md`. If a detail is missing, make one reasonable assumption, note it briefly, and proceed.
