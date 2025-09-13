---
applyTo: "**/*.test.ts,**/*.test.tsx,**/*.spec.ts,**/*.spec.tsx,**/*.config.{js,ts},.eslintrc*,tsconfig*.json"
---

# Copilot: tests and configs instructions

- Tests must be fast and deterministic. Prefer unit tests for `lib/**` helpers. Add smoke tests when touching pages.
- TypeScript: strict mode; no implicit anys. Fix types before merging.
- ESLint: follow repo rules. Keep formatting consistent; avoid large refactors.
- Keep CI-friendly defaults. Avoid relying on network or timeouts.
