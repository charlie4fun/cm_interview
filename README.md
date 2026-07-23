
# Local Kubernetes Delivery

This repository contains a local-first implementation of the original
[test assignment](TASK.md).

## What Is Implemented

- A dependency-free Python HTTP service with health, readiness, metrics, build
  information, structured logs, and graceful shutdown.
- A non-root container image with build version and commit metadata.
- A local kind cluster named `interview-dev`.
- A Helm deployment with two replicas, probes, resource limits, a rolling
  update strategy, and a restricted container security context.
- A runtime check for endpoints, probes, rolling updates, and graceful
  shutdown.
- Local environment checks, unit tests, and pre-commit validation.

## Architecture

The Python application is built into a local Docker image.
Kind runs an isolated Kubernetes cluster on the developer machine.
The image is loaded directly into kind without an external registry.
Helm installs and upgrades the application in the `interview` namespace.
A ClusterIP Service exposes the application inside the cluster.
Kubernetes probes and a two-replica rolling strategy maintain availability.
The Makefile provides the same entry points intended for later CI automation.

## Quick Start

Prerequisites are listed in [developer setup](docs/developer-setup.md).

```shell
make setup
make check
make check-env
make e2e
```

Remove the local cluster when finished:

```shell
make clean-cluster
```

## Main Commands

| Command | Purpose |
| --- | --- |
| `make setup` | Create the virtual environment and install Git hooks |
| `make check` | Run lint and unit tests |
| `make test` | Run application and tooling tests |
| `make check-env` | Check the complete Docker and Kubernetes toolchain |
| `make e2e` | Validate the toolchain and run local delivery |
| `make image` | Build the local container image |
| `make cluster` | Create the kind cluster |
| `make deploy` | Build, load, and deploy the application |
| `make verify-local` | Run runtime verification |
| `make local-delivery` | Build, deploy, and verify without tool checks |
| `make clean-cluster` | Delete the kind cluster |

## Release Model

Local builds use `APP_VERSION`, `COMMIT_SHA`, and an image tag passed through
the Makefile. The intended release model is Semantic Versioning, with each Git
tag producing a versioned image in GHCR. Automated CI and release workflows
are intentionally deferred until the local delivery path is stable.

## Review Tasks

The original files to review are [shell/script.sh](shell/script.sh) and
[k8s/nginx.yaml](k8s/nginx.yaml). Their written reviews have not been added
yet.

## Known Limitations

- CI, automatic releases, and GHCR publishing are not implemented yet.
- The shell script and Kubernetes deployment reviews are still pending.
- The setup is intended for local development, not production.
- There is no ingress, TLS, authentication, monitoring stack, or persistent
  storage.
