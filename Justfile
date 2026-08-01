set shell := ["bash", "-eu", "-o", "pipefail", "-c"]

_default:
    @just --list

sync:
    uv sync --locked

test:
    uv run python -m unittest discover -s tests -v

verify:
    uv run python scripts/verify.py

lint:
    uvx --from ruff==0.16.1 ruff check .

format:
    uvx --from ruff==0.16.1 ruff check --fix .
    uvx --from ruff==0.16.1 ruff format .

check: test verify lint

release version:
    uv run python scripts/build_release.py --version {{version}}

install-dev:
    ./scripts/install-dev.sh
