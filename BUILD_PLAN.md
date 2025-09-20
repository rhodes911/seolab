# SEO Lab — Build Plan (Streamlit)

This plan tracks the Streamlit implementation of the SEO Learn‑By‑Doing app. The app renders Markdown under `/content/**`, adds a sidebar table of contents, maps callouts, and stores progress locally.

---

## 0) Meta
- [x] Pivot plan (this file) and minimal README update

## 1) Streamlit scaffolding
- [x] Add `streamlit_app/` with theme, requirements, and quickstart

## 2) Content loader
- [x] Load Markdown + frontmatter
- [x] Extract headings (H2–H6) and inject anchors
- [x] Build index: by slug, by category, sortable list
- [x] Prev/Next helpers

## 3) UI & rendering
- [x] Sidebar navigation by category
- [x] Sidebar ToC for current lesson
- [x] Callouts mapping: > [!TIP] / [!INFO] / [!WARNING] / [!DANGER]
- [x] Basic CSS injection for layout and readability
	- Delivered reusable components:
		- Enhanced checklist (groups, rationale, progress)
		- Scenario presets (context toggle with tips)
		- Decision tree navigator (guided flows)

## 4) Progress
- [x] Local JSON store for completion + per‑lesson checklist
- [x] Export/Import JSON + Reset

## 5) Dashboard
- [x] Overall completion metric and per‑category progress
- [x] Simple suggestions with links

## 6) Content Format Testing
- [x] Create lesson format variations
- [x] Implement different formats
- [x] Make all versions accessible

## 7) Content Structure Implementation
- [ ] Reorganize content following SEO Playbook categories
- [ ] Create foundation lessons with visual-first approach
- [ ] Implement keyword research module
- [ ] Develop on-page SEO tutorials
- [ ] Build technical SEO guides
- [ ] Add content strategy resources
- [ ] Create off-page SEO materials
- [ ] Develop local SEO content
- [ ] Build analytics & measurement guides
- [ ] Add competitive analysis frameworks
- [ ] Create advanced SEO content

## 8) Polish & Enhancements
- [ ] Optional search/filter
- [ ] Syntax highlighting for code blocks
- [ ] Unit tests for parsing helpers
- [x] Additional interactive elements
- [ ] Export progress as completion certificate
