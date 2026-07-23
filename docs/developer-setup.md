# Developer Setup

## Prerequisites
- Python 3.12 or newer, but lower than 3.14

Python is the only prerequisite for setup, lint, and unit tests. Pre-commit is
installed into `.venv` by `make setup`.

The end-to-end workflow also requires:

- Docker 24 or newer, with the daemon running
- kubectl 1.31 or newer
- kind 0.27 or newer
- Helm 3.15 or newer

Install system tools with the supported method for your operating system. The
repository does not install them.

## Commands
1. Run `make setup` to create `.venv`, install development dependencies, and
   install Git hooks.
2. Run `make check` to execute lint and unit tests.
3. Install the end-to-end tools and run `make check-env` to validate them.
4. Run `make e2e` to lint the Helm chart, build the image, create the
   `interview-dev` kind cluster, deploy the release, and verify its runtime
   behaviour.
5. Run `make clean-cluster` to remove the local cluster.

The local delivery check verifies the HTTP endpoints and Kubernetes probes,
performs a rolling update, sends `SIGTERM` to one application process, and
checks its shutdown log before Kubernetes restarts it.
