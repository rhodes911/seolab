# Copilot: Repository Instructions for seolab

These instructions apply to all suggestions and edits in this repository. Follow the project spec in `README.md` and the step-by-step plan in `BUILD_PLAN.md`. Prefer concrete edits over advice.

## Prime directives
- Obey `README.md` architecture: Next.js App Router + TypeScript, TailwindCSS with darkMode:"class", shadcn/ui primitives, local-first progress storage with an abstraction.
- Execute work in the order of `BUILD_PLAN.md`. For each task: scope → implement minimal slice → validate (lint/type/tests) → commit → tick the plan.
- Keep changes local-first and privacy-safe. No external services unless explicitly opted-in.

## Ground rules
- Folder layout: `app/**` routes, `components/ui` for shadcn-generated primitives, `components/**` for domain components, `lib/**` for utilities (content, seo, storage, progress), `content/**` for Markdown lessons, `config/**` for app config and feature flags.
- Theming: use CSS variables defined in `app/globals.css`. Toggle dark mode via `html.dark`. Tailwind plugins: `@tailwindcss/typography` and `@tailwindcss/forms`.
- Progress: use `ProgressStore` interface under `lib/storage`; default driver is localStorage with namespaced, versioned key, plus export/import and migration stub.
- SEO: provide `metadata` where applicable; include canonical and JSON-LD for articles and breadcrumb when rendering lessons.
- Accessibility: semantic landmarks, skip link, keyboard focus visible, ARIA labels, proper headings.

## Quality gates
- Build must type-check with strict TS and pass ESLint. Add small unit tests for new public helpers. Keep tests fast and deterministic.
- Validate rendering for lesson route and dashboard (smoke test) when touched.

## Commit and PR etiquette
- Prefer small, focused commits. Reference the BUILD_PLAN step. Update docs when behavior changes.

## If in doubt
- Re-check `README.md` and `BUILD_PLAN.md`. If a detail is missing, make one reasonable assumption, note it in code comments or PR description, and proceed.
