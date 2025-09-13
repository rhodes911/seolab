---
applyTo: "lib/storage/**,lib/progress/**"
---

# Copilot: storage and progress instructions

Local-first, swappable storage with a clean context layer.

- `lib/storage`: define `ProgressStore` interface. Implement `LocalStorageProgressStore` with a namespaced, versioned key. Include export/import and a migration stub.
- Namespacing: stable prefix + version. Handle missing/old versions gracefully.
- `lib/progress`: React context/provider + hooks (e.g., `useProgress(slug)`, stats helpers, recently viewed, recommended next).
- No external services. Do not store PII. Keep data small and serializable.
- Add unit tests for store behavior and basic progress reducers.
