# SEO Lab — Streamlit Edition

A lightweight, local-first Streamlit app that renders a comprehensive SEO curriculum from `content/**` using a visual-first approach, with a sidebar table of contents and progress tracking. No servers or external services required.

---

## Repository structure

- `content/` — Markdown lessons organized by SEO Playbook categories
- `streamlit_app/` — Streamlit application
  - `app.py` — main app (lesson rendering, sidebar ToC, navigation)
  - `content_loader.py` — loads Markdown + frontmatter, extracts headings, builds index, prev/next
  - `components.py` — UI helpers (callouts, ToC, checklist, style injection)
  - `state.py` — local JSON progress store with export/import/reset
  - `pages/1_Dashboard.py` — dashboard page (overall and per-category progress)
  - `.streamlit/config.toml` — Streamlit theme
  - `styles.css` — small CSS tweaks (anchors, code wrapping)
- `CONTENT_PLAN.md` — Content structure following SEO Playbook categories
- `BUILD_PLAN.md` — Implementation tracking and future enhancements

---

## Quickstart (Windows PowerShell)

```powershell
# From the repo root
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r streamlit_app\requirements.txt
streamlit run streamlit_app\app.py
```

Then open the browser (Streamlit defaults to http://localhost:8501). Use the sidebar to select lessons. The “Pages” selector in the sidebar also links to the Dashboard.

Tip: In VS Code, press F5 to run (launch config is set to Streamlit), or run the task "streamlit: run" from the Command Palette.

---

## How it works

- Content loading: Markdown files under `content/**` are parsed with YAML frontmatter. Headings (H2–H6) are extracted to build an on-page ToC, and anchor IDs are injected so links jump to sections.
- Callouts: Lines like `> [!TIP] Use descriptive alt text` render as styled callout boxes. Supported: NOTE, TIP, INFO, WARNING, DANGER.
- Checklist: Items under a `## Checklist` section using Markdown task-list syntax (`- [ ] ...`) are turned into checkboxes in the UI.
- Progress: Saved locally to `streamlit_app/progress.json`. Export/import and reset are available from the sidebar.
- Navigation: Sidebar lists categories and lessons (sorted by `order`). Prev/Next buttons appear at the end of each lesson. A Dashboard page summarizes progress.

---

## Authoring content

Place lessons at `content/{category}/{slug}.md`.

Frontmatter (minimal example):

```yaml
---
title: "What is SEO"
description: "Introduction to search engine optimization fundamentals."
category: "foundations"
order: 1.1
toc: true
updated: "2025-09-13"
canonical: "/foundations/what-is-seo" # optional
---
```

Recommended content structure:

- Visual overview (diagrams, icons, tables)
- Key concepts with clear headings
- Step-by-step instructions with checkpoints
- Real-world examples or case studies
- Actionable checklist
- Resources and further reading

Checklist section:

```markdown
## Checklist

- [ ] Titles are unique and front‑load key terms
- [ ] One <h1>; clear h2/h3 structure
- [ ] Images have meaningful alt text
```

Callouts:

```markdown
> [!INFO] A page can be crawlable but excluded from the index.
> [!TIP] Prioritize on‑page fundamentals first.
> [!WARNING] Don’t block critical pages in robots.txt.
```

Code blocks and tables use standard GitHub-flavored Markdown.

Content style: prefer short paragraphs and bullets; bold key terms for scannability.

---

## Progress and dashboard

- Storage: `streamlit_app/progress.json` (created on first run)
- Export/Import: Use the sidebar popover in the main app to download/upload JSON
- Reset: Clears all local progress (also available in the sidebar popover)
- Dashboard: Overall completion and per-category progress (see "Pages" → Dashboard)

Privacy: Everything is local—no accounts, no network calls.

---

## Theming and styling

- Streamlit theme: `streamlit_app/.streamlit/config.toml` (colors, fonts)
- App CSS tweaks: `streamlit_app/styles.css` (anchors, code wrapping, small utilities)
- Callouts/ToC classes are injected by `components.inject_styles()`

---

## CI

GitHub Actions runs a minimal check to install Python dependencies and validate that the content loader can index lessons without errors.

---

## Troubleshooting

- `ModuleNotFoundError: frontmatter`: Ensure dependencies were installed:
  - `pip install -r streamlit_app/requirements.txt`
- App doesn’t see lessons: Confirm files live under `content/**` and have valid frontmatter.
- ToC links don’t jump: Headings must be H2 or deeper (`##` or more).
- Progress not saving: Check write permissions to `streamlit_app/progress.json`; delete it if corrupt.
- Change the port: `streamlit run streamlit_app/app.py --server.port 8502`

---

## Contributing

- Keep lessons small and actionable; follow the authoring guide above.
- Keep the app local-first and privacy-friendly—no external services by default.
- CI should remain fast and deterministic.
