# Installation, updates, and removal

## Recommended production installation

Hermes already provides the correct repository installer. Publish this project with `plugin.yaml` and
`__init__.py` at the repository root, then run:

```bash
hermes plugins install mindwired/hermess-sdd --enable
hermes gateway restart
hermes sdd ui install
hermes sdd doctor
```

The first command clones the complete repository into the active profile's plugin directory. Keeping the plugin
at the repository root is important: Hermes retains the Git checkout, so later updates can use:

```bash
hermes plugins update sdd
hermes gateway restart
```

### Why there is still a Desktop command

Hermes has three intentionally separate extension systems:

- Agent plugin: `$HERMES_HOME/plugins/sdd/plugin.yaml` and `__init__.py`
- Dashboard adapter: `$HERMES_HOME/plugins/sdd/dashboard/`
- Native Desktop adapter: `$HERMES_HOME/desktop-plugins/sdd/plugin.js`

Agent and Dashboard install together. Desktop cannot be discovered from the regular plugin folder, so
`hermes sdd ui install` creates the smallest possible bridge.

On POSIX, the default is a symlink. On Windows, it is a copy because symlink privileges are inconsistent.
Explicit modes are available:

```bash
hermes sdd ui install --mode link
hermes sdd ui install --mode copy
hermes sdd ui install --force
hermes sdd ui status
hermes sdd ui uninstall
```

## Is a manual clone sufficient?

The following can work for Agent and Dashboard:

```bash
git clone https://github.com/mindwired/hermess-sdd.git "$HERMES_HOME/plugins/sdd"
hermes plugins enable sdd
hermes gateway restart
```

It is less robust than `hermes plugins install` because the built-in command validates the plugin manifest,
normalizes the destination, handles an existing install safely, updates Hermes configuration, and displays the
repository's `after-install.md` instructions. Use manual cloning mainly for debugging the installer itself.

You would still need:

```bash
hermes sdd ui install
```

for native Desktop.

## Local development

POSIX:

```bash
./scripts/install-dev.sh
```

This creates development symlinks from the active `$HERMES_HOME` to the checkout. Existing destinations are
moved to timestamped backups unless they already point to this checkout.

Windows PowerShell:

```powershell
./scripts/install-dev.ps1
```

The PowerShell script copies the checkout because creating directory symlinks may require elevated privileges or
Developer Mode. Run it again to synchronize changes.

A production-like local Git installation is also available:

```bash
./scripts/install-local.sh
```

It asks Hermes to clone the current Git repository through a `file://` URL, then installs Desktop. Commit local
changes first because Git clones only committed content.

## Profiles and custom HERMES_HOME

All paths are derived from `HERMES_HOME`; no path is hardcoded to `~/.hermes`. When Hermes is operating under a
named profile, run installation and UI commands in that profile's environment. Confirm the resolved path with:

```bash
hermes sdd doctor
```

## Updates

Symlink Desktop installation:

```bash
hermes plugins update sdd
hermes gateway restart
```

Copy Desktop installation:

```bash
hermes plugins update sdd
hermes sdd ui install --force
hermes gateway restart
```

The gateway restart matters because Python plugin and FastAPI route modules are imported into long-lived
processes. Dashboard frontend-only rescans do not remount changed Python routes.

## Rollback

For a Git-managed installation:

```bash
cd "$HERMES_HOME/plugins/sdd"
git log --oneline --decorate -20
git checkout <known-good-tag-or-commit>
hermes sdd ui install --force   # required only for copy mode
hermes gateway restart
```

Project `.sdd/` state changes are intentionally explicit. Back up or commit project state before trying a newer
plugin against important repositories. Forced project reinitialization creates a backup instead of deleting the
old state.

## Uninstall

```bash
hermes sdd ui uninstall
hermes plugins remove sdd
hermes gateway restart
```

Removing the plugin does not delete `.sdd/` directories in projects. Those are normal project artifacts and must
be removed deliberately if no longer wanted.
