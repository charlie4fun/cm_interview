# ADR-0003: Local Development Environment Validation and Setup

## Status
Accepted

## Decisions
1. `make check-env` checks Docker, kubectl, kind, Helm, Python, pre-commit, their minimum versions, and Docker daemon access. It is read-only and never installs tools, creates a cluster, or changes system configuration.
2. `make setup` creates `.venv`, installs project-local development dependencies, and installs Git hooks. `make check` runs pre-commit checks without installing hooks.
3. System tools must be installed by the user. Clear errors point to the repository prerequisites.
4. Result of `make check-env` should be formatted as follows:
   1. OK: Python 3.12.8
   2. MISSING: Docker - current version: ...; desired version: ...
   3. OK: Docker daemon accessible
   4. MISSING: kubectl - not found
   5. ....
