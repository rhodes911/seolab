# SEO Learn-By-Doing Playbook — Content Library + Local Progress Dashboard

## Purpose
Build a content-first Next.js app that renders a complete SEO learning library from Markdown/MDX files and includes a local-only dashboard to track reading and completion.

- Content (Markdown) is the source of truth.
- Progress is stored locally (e.g., `localStorage`) — no accounts.

---

## Core Principles
- Markdown/MDX as content: all lessons live in `/content/...`.
- Uniform lesson template: every topic uses the same teaching sections.
- Local-only progress: completion and reading history saved per-browser.
- Theme-driven UI: one theme file controls colors/typography/spacing.
- Reusable components: single component set for all pages.
- Reusable SEO utilities: app uses its own meta/schema/canonical helpers.
- Accessible & fast: keyboard-first, semantic headings, strong CWV.

---

## Local‑first, upgradable architecture (so others can use it too)
The app is local-only by default, but the code should be structured so you can swap storage or ship a multi-user version without rewriting UI.

- Separation of concerns
  - Content is static under `/content/**` and compiled at build time.
  - UI lives in reusable, theme-aware components.
  - App logic (SEO utils, content indexing, progress) lives in `/lib/**` with narrow, testable APIs.
- Storage abstraction for progress
  - Define a `ProgressStore` interface and inject it via context (`ProgressProvider`).
  - Default driver uses `localStorage`; you can later swap an IndexedDB or remote API driver with the same interface.
  - Namespaced key (e.g., `seolab:progress:v{version}`) and a simple migration pipeline (`version` already in the schema).
- Export/Import (optional but recommended)
  - Allow users to export their progress as JSON and import it back (with validation and version migration).
  - Keeps data portable across devices without requiring accounts.
- App configuration
  - Centralize in `/config/app.ts` (or JSON): `baseUrl`, `siteName`, `defaultAuthor`, `features` (search, streaks, exportImport, pwa), `theme` preset.
  - No secrets required for the base app; remote/sync variants can read env vars separately.
- Distribution options
  - Static export is viable (`next export`) because content is local and prebuilt.
  - Optional PWA (e.g., next-pwa) for offline reading and installability.
  - A remote-enabled variant can swap only the progress driver + add an API route.

Suggested project layout:
```
/app
  /dashboard
  /[...slug]/page.tsx     # renders MarkdownPage by content slug
/components               # AppShell, MarkdownPage, ToC, Checklist, PrevNext, etc.
/content                  # the Markdown library (source of truth)
/lib
  /content                # content indexing, frontmatter types, slug helpers
  /progress               # ProgressProvider, useProgress, stats helpers
  /storage                # ProgressStore interface + drivers (localStorage default)
  /seo                    # buildMeta, schema, canonical, slugify, joinUrl
/theme                    # tokens and global styles
/config                   # app.ts with site metadata + feature flags
```

Minimal storage interface (example):

```ts
export type Checklist = {
  understandWhy?: boolean;
  applyManually?: boolean;
  knowGood?: boolean;
};

export type LessonProgress = {
  completed?: boolean;
  checkedAt?: string; // ISO
  readingTime?: number;
  lastReadAt?: string; // ISO
  checklist?: Checklist;
};

export type ProgressState = {
  version: number;
  lessons: Record<string, LessonProgress>; // key = slug
};

export interface ProgressStore {
  load(): ProgressState;
  save(next: ProgressState): void;
  reset(): void;
}
```

Default driver: `LocalStorageProgressStore` using a namespaced key like `seolab:progress:v1`. Future drivers can implement the same `ProgressStore` for IndexedDB or a remote API.

## Content Source (Markdown Library)
- All lessons live in the repo under `/content/{category}/{slug}.md`.
- Built at compile time; no runtime fetching or DB.

### Directory Structure
```
/content
  /foundations
    what-is-seo.md
    how-search-engines-work.md
    ranking-systems.md
    serp-anatomy.md
    types-of-seo.md
    core-kpis.md
  /keyword-research
    seed-keywords.md
    keyword-expansion.md
    search-volume.md
    keyword-difficulty.md
    search-intent.md
    long-tail-keywords.md
    keyword-clustering.md
    opportunity-scoring.md
    mapping-to-content-types.md
  /on-page
    title-tags-and-meta-descriptions.md
    headings-h1-h6.md
    body-content-optimization.md
    alt-text.md
    internal-linking.md
    url-structure.md
    canonicals.md
    schema-basics.md
    content-depth-readability.md
    user-experience-signals.md
  /technical
    crawling-indexation.md
    robots-txt.md
    meta-robots-canonicals.md
    sitemaps-xml-html.md
    site-architecture.md
    core-web-vitals.md
    page-speed-optimization.md
    mobile-first-indexing.md
    https-security.md
    redirects.md
    duplicate-content.md
    log-file-analysis.md
    international-seo-basics.md
  /content-strategy
    content-types.md
    buyer-journey-mapping.md
    content-briefs.md
    topical-authority-eeat.md
    semantic-seo.md
    evergreen-vs-seasonal.md
    repurposing-content.md
    avoid-thin-duplicate.md
  /off-page
    backlinks.md
    link-attributes.md
    backlink-quality.md
    link-building-strategies.md
    local-citations.md
    toxic-links-disavow.md
    unlinked-mentions.md
    authority-measurement.md
  /local
    google-business-profile.md
    nap-consistency.md
    local-citations-directories.md
    local-keywords.md
    reviews-reputation.md
    local-link-building.md
    local-pack-signals.md
    sab-vs-location-businesses.md
  /analytics
    google-search-console.md
    ga4.md
    rank-tracking.md
    dashboards-reporting.md
    kpis-by-goal.md
    ab-testing-seo.md
    log-analysis.md
  /competitive
    identify-competitors.md
    keyword-gap-analysis.md
    content-benchmarking.md
    serp-feature-analysis.md
    backlink-profile-comparison.md
    market-share-tracking.md
  /advanced
    semantic-search-nlp.md
    entity-seo.md
    programmatic-seo.md
    edge-seo.md
    automated-internal-linking.md
    content-pruning.md
    schema-optimization.md
    seo-at-scale.md
    voice-search.md
    video-seo.md
  /automation
    crawlers.md
    keyword-tools.md
    analytics-tools.md
    reporting-automation.md
    seo-apis.md
    automation-ideas.md
```

---

## Required Frontmatter
Each Markdown file must start with:

```yaml
---
title: "SEO Foundations — What is SEO?"
category: "Foundations"
slug: "foundations/what-is-seo"
summary: "Practical introduction to Search Engine Optimization."
readingTime: 5
order: 1
seo:
  metaTitle: "What is SEO? | SEO Foundations"
  metaDescription: "Understand SEO and its core pillars: on-page, technical, off-page."
  canonical: "/foundations/what-is-seo"
  schemaType: "Article"
toc: true
updatedAt: "2025-09-13"
---
```

Rules:

- `category` must match the folder label shown in the sidebar.
- `slug` must be unique and mirror its path.
- `order` determines sort within the category.
- `seo` feeds the SEO utilities; keep fields concise and valid.
- `toc` toggles in-page table of contents.

---

## Lesson Template (Mandatory)
All Markdown topics must follow this exact structure and concise detail:

```markdown
# {Category} — {Topic Title}

## Why This Matters
2–4 sentences explaining the practical importance.

## Definition / Explanation
Plain-English description. Use bullets where helpful.

## How to Do It (Manually)
3–6 numbered steps a beginner can follow.

## What Good Looks Like
3–5 bullets indicating correct application.

## Pitfalls
3–5 common mistakes to avoid.

## Example
One realistic example showing the concept in action.

## Action
A short exercise (1–3 steps) to apply the learning.

## Mark Complete
- [ ] I understand why this matters
- [ ] I can apply it manually
- [ ] I know what good looks like
```

Content style:

- Short paragraphs, bullets, and bolded key terms for scannability.
- Avoid walls of text; aim for clarity over depth where trade-offs exist.

---

## Navigation & Information Architecture
- Sidebar: Categories → Topics (ordered by `order`).
- Breadcrumbs: Home / Category / Topic.
- Prev/Next: At the end of each lesson, computed by category order.
- On-page ToC: Generated from `##` headings when `toc: true`.
- Search (optional): lightweight client-side filter by title/summary.

---

## Theme-Driven UI
One theme file controls the entire look (e.g., `/theme/theme.ts` or `/theme/theme.json`).

Theme tokens:

- Colors: `bg`, `fg`, `muted`, `primary`, `accent`, `success`, `warning`, `danger`
- Typography: families, sizes, line-heights, weights
- Spacing: consistent scale (e.g., 4/8-based)
- Radii, shadows, borders
- Breakpoints, container widths

Support light/dark and high-contrast modes from the same theme.

Changing a token must update UI globally (no hard-coded styles in components).

---

## Reusable Components
- AppShell (header, sidebar, content, breadcrumbs)
- MarkdownPage (MD/MDX renderer with ToC, anchor links)
- Callout (info/warning/success for tips and pitfalls)
- Checklist (checkbox list; ties into local progress)
- TableOfContents (from headings)
- PrevNext (prev/next lesson links)
- SearchInput (optional)
- Badge, Tag, AnchorHeading, ProgressBar

All components must be theme-aware, accessible (keyboard/ARIA), and reused across the app.

---

## Reusable SEO Utilities (Applied by the App)
Centralize under `/lib/seo/`:

- `buildMeta({ title, description, canonical, noindex? })`
- `buildOg({ title, description, url, image })`
- `buildTwitter({ title, description, image, card })`
- `schema.article({ headline, datePublished, author, image })`
- `schema.breadcrumb({ items })`
- `schema.faq([{ question, answer }])`
- `canonical(path)`
- `robots({ index, follow })`
- `slugify(title)`
- `joinUrl(base, path)`
- Heading ID generator (for ToC and deep links)

Dogfooding: All library pages must use these utilities for their own meta, canonical, breadcrumb JSON-LD, etc.

---

## Local Progress (Dashboard)
Local-only progress stored per-browser (no accounts). Use `localStorage` (or IndexedDB) keyed by `slug`.

### Progress Data Model (Client-Side)
```json
{
  "version": 1,
  "lessons": {
    "foundations/what-is-seo": {
      "completed": true,
      "checkedAt": "2025-09-13T09:30:00Z",
      "readingTime": 5,
      "lastReadAt": "2025-09-13T09:28:00Z",
      "checklist": {
        "understandWhy": true,
        "applyManually": true,
        "knowGood": true
      }
    }
  }
}
```

### Dashboard Requirements
- Route: `/dashboard`

Cards/sections:

- Overall Progress: total lessons, completed, % complete, estimated time remaining (sum of `readingTime` of incomplete).
- By Category: progress bars per category (e.g., Foundations 4/6, 67%).
- Recently Viewed: last 5 lessons with “Resume” links.
- Recommended Next: next incomplete lesson in the current category.
- Streak (optional): simple local “days read in a row” count.
- Export/Import (optional): buttons to download current progress JSON and to upload a JSON file to merge/replace state with validation and version migration.

Interactions:

- Mark lesson complete from the lesson page or dashboard.
- Reset progress (with confirmation) — clears local storage.
 - Export progress (download JSON). Import progress (select JSON, validate, then merge/replace).

Privacy:

- All data local to the browser; no network or sync.
- Notice on the dashboard: “Progress is stored locally on this device only.”
 - Exported files remain on the user’s device; no uploads by default.

### Components for Progress
- ProgressProvider (context for reading/writing local progress)
- `useProgress(slug)` hook (get/set completion and checklist)
- ProgressBar (linear bar for overall and per-category)
- LessonList (category grouped list with completion state)
- ResetProgressModal

### Lesson Page → Progress Integration
- Checklist section binds to `useProgress(slug)` to persist checkbox state.
- When all three checkboxes are ticked, set `completed = true` and timestamp.
- “Mark Complete” button toggles completion explicitly.
- Update `lastReadAt` on route view.
- Provide a “Back to Dashboard” CTA.

---

## Accessibility & Performance
- A11y: skip links, focus outlines, labelled controls, ARIA landmarks.
- Semantics: one `h1` per lesson (from Markdown), `h2/h3` for sections.
- Performance: prefetch next/prev lesson routes, lazy-load ToC on long pages.
- Core Web Vitals: stable layout (no CLS), responsive interactions (INP), fast content paint (LCP).
- SEO: titles/metas, canonical, breadcrumb JSON-LD, clean internal links.

---

## Example Lesson Skeleton (with Frontmatter)
```yaml
---
title: "SEO Foundations — What is SEO?"
category: "Foundations"
slug: "foundations/what-is-seo"
summary: "Understand SEO and its core pillars: on-page, technical, off-page."
readingTime: 5
order: 1
seo:
  metaTitle: "What is SEO? | SEO Foundations"
  metaDescription: "Plain-English intro to Search Engine Optimization and how it drives organic traffic."
  canonical: "/foundations/what-is-seo"
  schemaType: "Article"
toc: true
updatedAt: "2025-09-13"
---
```

# SEO Foundations — What is SEO?

## Why This Matters
SEO is how websites become visible in Google and other search engines.
Without it, even a great site won’t attract visitors at the right moment of intent.

## Definition / Explanation
- **SEO = Search Engine Optimization** — making your site easier to **find**, **understand**, and **trust** in search results.
- The goal is to increase **relevant, organic traffic** (not paid ads).
- Core areas:
  1. **On-Page SEO** (content, HTML, structure)
  2. **Technical SEO** (speed, crawlability, mobile-friendliness)
  3. **Off-Page SEO** (backlinks, authority, brand signals)

## How to Do It (Manually)
1. Search 3–5 keywords that matter to your business.
2. Review the top results: content depth, page type, freshness, authority.
3. Compare your page: does it match intent? is it readable? can Google access it?

## What Good Looks Like
- You appear for relevant queries.
- Pages are clear, structured, and easy to navigate.
- Important content is crawlable and indexable.
- Other sites naturally link to your content.

## Pitfalls
- Treating SEO as “just keywords.”
- Ignoring speed and mobile basics.
- Expecting instant results.
- Writing for bots, not people.

## Example
Keyword: **“landlord furniture packs”** — page 1 shows service providers and buying guides.
SEO is what helps you compete to appear there when buyers are searching.

## Action
1. Write your one-sentence definition of SEO.
2. Google 3 target keywords.
3. Note the page types that rank (service, blog, local maps).

## Mark Complete
- [ ] I understand why this matters
- [ ] I can apply it manually
- [ ] I know what good looks like

---

## Definition of Done
- All curriculum topics exist as Markdown files with valid frontmatter.
- Each lesson follows the mandatory template and consistent detail level.
- Sidebar, breadcrumbs, prev/next, and ToC are generated from content metadata.
- A single theme file controls styles across all components.
- SEO utilities are applied to all library pages (titles, metas, JSON-LD, canonical).
- Dashboard exists, showing overall and per-category local progress, recent items, recommended next, and reset progress.
- Local-only storage is used; no network calls for progress. A `ProgressStore` abstraction exists so storage can be swapped (e.g., IndexedDB or remote API) without changing UI.
- Export/Import is available (optional): users can download/upload progress JSON with validation and version-aware migration.
- App is accessible, fast, and semantically structured.
