# GitHub Copilot Instructions — SEO Lab

Authoritative guide for automated coding agents and contributors. Follow this exactly.

Primary sources of truth:
- README.md — product spec, theming, components, SEO rules
- BUILD_PLAN.md — sequenced tasks; execute in order and check items off

Never skip or reorder tasks without updating BUILD_PLAN.md and explaining why in the commit.

---

## Prime directives
1) Always read README.md and BUILD_PLAN.md before editing code.
2) Work strictly top-to-bottom through BUILD_PLAN.md. One task in-flight at a time.
3) After each task:
   - Validate (build, lint/typecheck, minimal tests)
   - Update BUILD_PLAN.md checkbox ("[ ]" -> "[x]") with a one-line note
   - Commit with a scoped message referencing the task ID
4) Keep UI consistent with the chosen stack: TailwindCSS + shadcn/ui (Radix), CSS variables for colors, `html.dark` for dark mode.
5) Local-only progress by default. Do not add network calls for progress storage.
6) Dogfood the SEO utilities on all content pages.

---

## Execution loop (per task)
For each task in BUILD_PLAN.md:

1. Scope
   - Locate the task and its “Done when” outcomes
   - Re-read related sections in README.md
   - Note any assumptions; prefer the simplest implementation that satisfies the spec

2. Implement
   - Create or modify the minimal set of files
   - Follow the theme tokens via CSS variables only (no hard-coded hex)
   - Use shadcn/ui for primitives under `/components/ui/*` and keep domain components in `/components`

3. Validate
   - Run typecheck and lint
   - Add or update small, focused unit tests (at least happy path); prefer tests when adding new public utilities
   - Run tests and ensure green

4. Commit and tick off
   - Update BUILD_PLAN.md: change the task’s checkbox to `[x]` and add a brief outcome note under it
   - Commit with message format: `feat(task-<id>): <concise description>` or `chore(task-<id>)`, `fix(task-<id>)`, `docs(task-<id>)`

5. Proceed
   - Start the next task only after the current one is fully validated and checked off

---

## Commands (Windows PowerShell)
Use these commands (adjust if the project structure evolves):

```powershell
# Install deps
npm ci

# Dev server
npm run dev

# Typecheck
npm run typecheck

# Lint
npm run lint

# Unit tests (watch and CI)
npm run test
npm run test:ci
```

If scripts are missing, add them in package.json when you scaffold the project:

```json
{
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "lint": "eslint .",
    "typecheck": "tsc --noEmit",
    "test": "vitest",
    "test:ci": "vitest run"
  }
}
```

Preferred test stack: Vitest + Testing Library + React Testing Library. Adjust if an alternative is adopted during scaffolding.

---

## Style and structure
- TailwindCSS dark mode via `darkMode: 'class'`
- CSS variables defined in `app/globals.css` (light on `:root`, dark on `.dark`)
- No hard-coded hex in components; use `bg-[--bg]`, `text-[--fg]`, or mapped color tokens
- UI primitives in `/components/ui/*` (from shadcn/ui)
- Domain components in `/components` (AppShell, MarkdownPage, Checklist, ToC, PrevNext, ProgressBar, ResetProgressModal, AnchorHeading)
- Content in `/content/**` with required frontmatter and mandatory lesson sections
- Utilities in `/lib/**` as described in README (content, storage, progress, seo)

---

## Testing policy
- Add tests whenever you add new public utilities or storage logic
- Minimal but meaningful: 1–2 happy paths + 1 edge case
- Prefer unit tests for `/lib/**`; light smoke tests for routes/components

---

## Pull requests (if applicable)
- Reference the task ID(s) in the title
- Checklist in PR description:
  - [ ] I followed BUILD_PLAN.md order and updated the checklist
  - [ ] I ran typecheck and lint with no errors
  - [ ] I added/updated unit tests and they pass locally
  - [ ] Changes adhere to README.md (theme tokens, component strategy, local-only progress)

---

## Guardrails
- Do not add runtime network calls for progress or content
- Keep UI library consistent; do not mix multiple component libraries
- Keep changes minimal and scoped to the active task
- Use semantic HTML and ARIA where needed; one h1 per page

---

## Failure handling
- If a validation step fails, fix within the same task; do not proceed
- If a task cannot be completed due to missing context, update BUILD_PLAN.md with a blocker note and propose the smallest next step to unblock

---

By following this guide, Copilot (and humans) can deliver the app in small, validated increments that strictly adhere to the spec.
