---
applyTo: "app/**"
---

# Copilot: app/** (routes) instructions

Follow Next.js App Router conventions with SSG for Markdown lessons.

- Provide `export const metadata` where applicable. Use canonical and JSON-LD for lessons.
- Lesson route (`/app/[...slug]/page.tsx`): render Markdown via loader, ToC when `toc:true`, breadcrumbs, Prev/Next, progress hooks.
- Dashboard route: overall and per-category progress, recently viewed, recommended, export/import, reset progress.
- Home route: list categories/lessons with completion indicators. Optional quick search.
- Accessibility: skip link, semantic landmarks, headings, focus-visible. Avoid CLS; prefetch prev/next.
- Keep route files lean; push logic to `lib/**` and `components/**`.
