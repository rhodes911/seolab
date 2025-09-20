# SEO Lab (Streamlit)

A streamlined Streamlit app that renders the SEO lesson library from Markdown and lets you track local reading progress.

## Quick start

1. Create a Python env (recommended)
2. Install deps:
   - `pip install -r streamlit_app/requirements.txt`
3. Run:
   - `streamlit run streamlit_app/app.py`

## Features
- Renders Markdown from `content/**` with frontmatter
- Sidebar Table of Contents and search
- Per-lesson checklist stored locally (JSON)
- Export/Import progress
- Interactive add-ons via frontmatter:
   - Context presets (segmented control)
   - Enhanced checklist (groups, rationale, preset filtering)
   - Decision tree navigator

## Project layout
```
streamlit_app/
  app.py            # main entry
  state.py          # progress storage
  content_loader.py # frontmatter + ToC + index
  components.py     # UI helpers (callouts, checklist)
  styles.css        # extra CSS tweaks
  pages/
    1_Dashboard.py
```

