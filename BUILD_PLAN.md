# SEO Lab — Build Plan (Live Checklist)

This is the step‑by‑step scaffold and delivery plan for the SEO Learn‑By‑Doing app. It follows the README spec (TailwindCSS + shadcn/ui, local‑first progress, Markdown as source). We’ll tick items off as we go.

Quick choices:
- UI: TailwindCSS + shadcn/ui (Radix) for primitives; domain components custom.
- Theming: CSS variables + `html.dark` toggle. No hard-coded hex.
- Content: Markdown under `/content/**` with required frontmatter.
- Storage: Local‑only with a `ProgressStore` abstraction for easy swap later.

---

## 0) Meta
- [x] Author project plan (this file)
  - Done when: This checklist exists with clear tasks, outcomes, and artifacts.

---

## 1) Initialize Next.js + TS + Tailwind
- [ ] Scaffold project with App Router, TypeScript, ESLint, Tailwind
  - Done when:
    - Next.js app boots locally.
    - Tailwind configured with `darkMode: 'class'` and plugins `@tailwindcss/typography` + `@tailwindcss/forms`.
  - Artifacts:
    - `package.json`, `next.config.js/ts`, `tailwind.config.ts`, `postcss.config.js`

## 2) Add theme tokens (CSS variables)
- [ ] Define tokens in `app/globals.css` with light/dark values
  - Done when: `--bg`, `--fg`, `--muted`, `--primary`, `--accent`, `--success`, `--warning`, `--danger`, `--border`, `--card`, `--ring` exist and base styles apply.
  - Artifacts: `app/globals.css`

## 3) Install shadcn/ui primitives
- [ ] Generate core UI primitives under `/components/ui`
  - Button, Card, Input, Select, Checkbox, Dialog, Drawer, Dropdown, Tabs, Tooltip, Toast, Progress, Badge/Alert
  - Done when: Components render and inherit CSS variables; dark mode works.

## 4) Content folders + sample lessons
- [ ] Create `/content/**` structure and add 2+ lessons
  - Done when: Files contain valid frontmatter and the mandatory lesson template.

## 5) Content indexing utilities
- [ ] Implement `/lib/content`
  - Types for frontmatter
  - Loader (build‑time), slug/category helpers
  - Prev/next computation by category/order
  - Heading extraction for ToC
  - Done when: Can list lessons, compute neighbors, and produce headings.

## 6) SEO utilities
- [ ] Implement `/lib/seo`
  - `buildMeta`, `buildOg`, `buildTwitter`
  - `schema.article`, `schema.breadcrumb`, `schema.faq`
  - `canonical`, `robots`, `slugify`, `joinUrl`, heading ID generator
  - Done when: Lesson pages can set titles/metas/JSON‑LD consistently.

## 7) Progress storage abstraction
- [ ] Implement `/lib/storage`
  - `ProgressStore` interface
  - `LocalStorageProgressStore` with namespaced key + version and migration stub
  - Done when: Load/save/reset works and is versioned.

## 8) Progress context and hooks
- [ ] Implement `/lib/progress`
  - `ProgressProvider`, `useProgress(slug)`
  - Stats: overall %, per‑category %, ETA, recently viewed, recommended next
  - Done when: Checklist state persists; computed stats are available.

## 9) Domain components
- [ ] Build custom components under `/components`
  - AppShell (landmarks, breadcrumbs, skip link, dark toggle)
  - MarkdownPage (MD/MDX renderer + anchor headings)
  - Checklist (binds to `useProgress`; auto‑complete when all checked)
  - TableOfContents (lazy on long pages)
  - PrevNext
  - ProgressBar (wraps library progress)
  - ResetProgressModal (confirmation + focus trap)
  - AnchorHeading (stable IDs + copy link)
  - SearchInput (optional)
  - Done when: Components render and meet a11y + theming rules.

## 10) Dynamic lesson route
- [ ] Create `/app/[...slug]/page.tsx`
  - SSG from `/content`, with breadcrumbs, ToC (when `toc: true`), PrevNext
  - Apply SEO: meta, canonical, breadcrumb JSON‑LD
  - Done when: Visiting a lesson slug renders full page with nav + SEO.

## 11) Dashboard route
- [ ] Create `/app/dashboard/page.tsx`
  - Overall and per‑category progress, recently viewed, recommended next
  - Optional streak; Export/Import JSON; Reset progress
  - Done when: All sections render and interact with local progress.

## 12) Home route
- [ ] Create `/app/page.tsx`
  - List categories and lessons with completion indicators
  - Optional quick search/filter
  - Done when: Users can browse into any lesson easily.

## 13) Accessibility & performance polish
- [ ] A11y: skip links, focus outlines, ARIA labels, landmarks
- [ ] Perf: prefetch prev/next, lazy‑load ToC on long pages, CLS‑safe layout
  - Done when: Keyboard‑only use is smooth; CWV best practices applied.

## 14) Quality gates: lint, typecheck, tests
- [ ] ESLint/Prettier, TS strict
- [ ] Unit tests: content indexing, SEO utils, ProgressStore
- [ ] Smoke tests: lesson route and dashboard render
  - Done when: Lint/typecheck pass and tests are green.

## 15) Docs & quick start
- [ ] Update README
  - Add run/build steps, theme editing, component usage, export/import
  - Optional LICENSE
  - Done when: A new contributor can run and extend the app easily.

---

### Notes
- Do not mix UI libraries—stick to Tailwind + shadcn/ui for consistency.
- All colors use CSS variables; dark mode via `html.dark`.
- No network calls for progress; Export/Import is local JSON only by default.
