# Compatibility policy

## Tested baseline

- Hermes Agent: `0.19.1` or later
- Python: `3.11`–`3.13`
- Dashboard: current `window.__HERMES_PLUGIN_SDK__` tab/backend contract
- Desktop: current `@hermes/plugin-sdk` disk-plugin contract

`hermes_sdd.version.MIN_HERMES_VERSION` is a tested floor, not a guarantee that every future Hermes release will
remain compatible. Hermes evolves quickly; CI validates repository contracts, while release smoke tests must use
the actual target Hermes build.

## Stable plugin contracts used

Agent:

- root `plugin.yaml` and `__init__.py`
- `ctx.register_tool`
- `ctx.register_command`
- `ctx.register_cli_command`
- `ctx.register_skill`

Dashboard:

- `dashboard/manifest.json`
- `window.__HERMES_PLUGIN_SDK__`
- `window.__HERMES_PLUGINS__.register`
- FastAPI `plugin_api.py` mounted under `/api/plugins/sdd`

Desktop:

- `$HERMES_HOME/desktop-plugins/sdd/plugin.js`
- `@hermes/plugin-sdk`
- route, navigation, status bar, and palette contributions
- `ctx.rest` to the shared plugin backend

## Compatibility checks

`hermes sdd doctor` reports the detectable Hermes version, layout, active Hermes home, Desktop adapter mode and
freshness, and optional project initialization. `scripts/verify.py` enforces static contract and version
consistency before release.

## Breaking changes

A change is breaking when it alters an existing `.sdd/` field's meaning, removes an operation, changes accepted
status transitions, weakens evidence semantics, or requires a manual project migration. Such changes require:

1. a major version increment after `1.0` (or a minor increment during `0.x`);
2. an explicit migration function and tests;
3. backup and rollback instructions;
4. compatibility notes in the changelog.
