#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
if ! git -C "$ROOT" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  printf 'This command requires the checkout to be a Git repository. Use install-dev.sh instead.\n' >&2
  exit 2
fi
if [[ -n "$(git -C "$ROOT" status --porcelain)" ]]; then
  printf 'Commit or stash changes first; file:// installation clones committed content only.\n' >&2
  exit 2
fi

URL="file://$(python3 -c 'import pathlib,sys; print(pathlib.Path(sys.argv[1]).resolve())' "$ROOT")"
hermes plugins install "$URL" --force --enable
hermes sdd ui install --force
hermes gateway restart
hermes sdd doctor
