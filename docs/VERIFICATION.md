# Verification report

Date: **August 1, 2026**

## Completed locally

- `uv lock --offline` and `uv sync --locked --offline` with Python 3.13.5.
- 23 standard-library unit/integration tests with `ResourceWarning` promoted to an error.
- FastAPI Dashboard integration test with FastAPI 0.128.2 and HTTPX 0.28.1.
- Python AST parsing and isolated bytecode compilation for every Python file.
- JSON parsing for every committed JSON file.
- Node.js syntax checks for Dashboard and Desktop JavaScript.
- Hermes-style package loading with `spec_from_file_location(..., submodule_search_locations=[...])`.
- Native Desktop copy, symlink, idempotency, overwrite protection, freshness, and uninstall tests.
- A clean `file://` Git clone, locked offline environment synchronization, full test suite, and contract verification.
- Deterministic ZIP and tar.gz builds; consecutive builds produced identical SHA-256 hashes.
- No SQLite `ResourceWarning` under repeated lifecycle and concurrent-worker operations.

## Core behaviors exercised

- Complete project initialization → specification → milestone → plan → execution → evidence → validation → finalization.
- Adaptive complexity modes and context budgets.
- Task dependency cycles, incomplete dependencies, file-scope overlap, and critical-task isolation.
- Start-time safety revalidation against stale clients and already-running work.
- Concurrent non-overlapping task starts without lost plan updates.
- Optimistic plan revisions and targeted task updates.
- Context checkpoints, wildcard source scopes, and changed-file deltas.
- Program-mode evidence requirements and failed/manual evidence handling.
- Future-milestone validation errors isolated from current-milestone finalization.
- Forced initialization backup and recovery behavior.
- Compact Hermes tool/command/skill registration.

## CI-only checks

The repository includes pinned Ruff linting and a multi-OS Python 3.11–3.13 matrix. Ruff could not be downloaded in
the artifact runtime because its Python package registry has no network access or cached Ruff wheel. The CI job is
the authoritative Ruff execution and is intentionally required before merging or releasing.

## Remaining deployment validation

The repository environment includes Hermes Agent `0.19.1`; local validation must still include a disposable-profile
plugin installation and CLI smoke test. Graphical Dashboard/Desktop interaction remains a manual gate because this
checkout does not provide a graphical Hermes application. Run the smoke test in `HANDOFF.md` against the exact
Hermes release and profile that will be used before creating `v0.1.0`.
