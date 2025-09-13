---
applyTo: "components/**/*.tsx,components/**/*.ts"
---

# Copilot: components/** instructions

Use Tailwind + shadcn/ui primitives consistently and keep them theme-token aware.

- Use `components/ui/*` for shadcn primitives; do not inline Radix in domain components. Wrap primitives to expose only what we need.
- Respect CSS variables from `app/globals.css` for colors (bg, fg, muted, primary, accent, success, warning, danger, border, card, ring).
- Dark mode: relies on `html.dark`. Avoid hard-coded colors; use Tailwind classes that map to our CSS vars.
- Accessibility: keyboard operable, focus-visible rings, ARIA where needed, proper labeling. Use semantic elements and roles.
- Responsiveness: mobile-first; avoid layout shift; prefer grid/flex utilities.
- Avoid business logic in components; move data shaping to `lib/**`.
- Story-friendly: keep props simple and typed. Prefer controlled inputs.
