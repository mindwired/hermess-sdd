# Contributing

## Setup

```bash
uv sync --locked
uv run python -m unittest discover -s tests -v
uv run python scripts/verify.py
```

Lint and format with the pinned Ruff release:

```bash
uvx --from ruff==0.16.1 ruff check .
uvx --from ruff==0.16.1 ruff format --check .
```

## Change expectations

- Preserve the single compact Agent-tool surface unless measurements justify expansion.
- Keep `.sdd/` as the portable source of truth; UI registries must remain derived/non-authoritative.
- Add evidence-oriented tests for scheduler, transition, locking, or context-pack changes.
- Avoid mandatory ceremony for small work. New process steps must show a concrete quality or recovery gain.
- Maintain compatibility across Python 3.11–3.13 and current Hermes Agent plugin APIs.
- Update `CHANGELOG.md`, compatibility notes, and all version declarations for releases.

## Pull requests

Explain the user-visible behavior, state-format impact, token/process overhead, migration requirements,
and tests. Breaking state changes require a migration and a documented rollback path.

## Release and repository hygiene

- Never commit `.sdd/` project state, Hermes home state, credentials, generated release archives, or local test artifacts.
- Keep `dashboard/dist/` tracked: Hermes loads the Dashboard adapter without a build step.
- Run `uv run python scripts/verify.py --require-node` before opening a pull request.
- Changes to the Python plugin contract require a disposable-profile Hermes installation smoke test.
