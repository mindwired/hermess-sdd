#!/usr/bin/env bash
set -euo pipefail

if command -v hermes >/dev/null 2>&1; then
  hermes sdd ui uninstall || true
  hermes plugins remove sdd
  hermes gateway restart || true
else
  HERMES_HOME="${HERMES_HOME:-$HOME/.hermes}"
  rm -f "$HERMES_HOME/desktop-plugins/sdd/plugin.js"
  rm -rf "$HERMES_HOME/plugins/sdd"
fi
