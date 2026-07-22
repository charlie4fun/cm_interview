# Developer Setup

## Prerequisites
- Docker 24 or newer, with the daemon running
- kubectl 1.31 or newer
- kind 0.27 or newer
- Helm 3.15 or newer
- Python 3.12 or newer, but lower than 3.14

Install these tools with the supported method for your operating system. The repository does not install system tools.
Pre-commit is installed into `.venv` by `make setup`.

## Commands
1. Run `make setup` on a fresh checkout to validate system tools, create `.venv`, and install Git hooks.
2. Run `make check-env` for a read-only environment check.
3. Run `make check` to execute all repository checks.
