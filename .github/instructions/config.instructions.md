---
applyTo: "config/**"
---

# Copilot: config/\*\* instructions

- Centralize site metadata (title, description, baseUrl), feature flags, and environment-driven toggles here.
- Keep objects serializable; export typed config. No side effects.
- Consumers should read from `config/app.ts` (or similar) rather than duplicating constants.
