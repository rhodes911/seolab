---
applyTo: "lib/content/**,lib/seo/**"
---

# Copilot: lib/content and lib/seo instructions

Utilities only; keep them pure, typed, and testable.

- `lib/content`: types for frontmatter, FS/loader for Markdown, slug/category helpers, prev/next computation, ToC extraction. No React here.
- `lib/seo`: builders for `metadata`, OpenGraph, Twitter, canonical, robots, JSON-LD (article, breadcrumb, faq), slugify, joinUrl, heading ID generator.
- Strict TypeScript; no implicit anys. Export minimal public surface.
- Add small unit tests for public helpers. Keep deterministic and fast.
- No network or browser APIs here. Node or universal only.
