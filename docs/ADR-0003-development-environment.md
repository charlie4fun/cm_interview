# ADR-0003: Development Environment Checks

## Status
Accepted

## Decision
`make check-env` checks Docker, kubectl, kind, Helm, Python, pre-commit, their minimum versions, and Docker daemon access. It is read-only and never installs tools, creates a cluster, or changes system configuration.

`make setup` creates `.venv`, installs project-local development dependencies, and installs Git hooks. `make check` runs pre-commit checks without installing hooks.

System tools must be installed by the user. Clear errors point to the repository prerequisites.
