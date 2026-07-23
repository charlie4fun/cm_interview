# ADR-0006: CI/CD and Artifact Publishing

## Status
Accepted

## Context
The project needs automated checks and repeatable releases without using external infrastructure.

The same build, test, and deployment commands should work locally and in CI.

## Decision
Use GitHub Actions for CI/CD and GitHub Container Registry (GHCR) for released artifacts.

The CI workflow runs on pull requests and pushes to `main`. It:
1. runs tests and pre-commit checks;
2. builds the container image without publishing it;
3. validates the Helm chart;
4. creates a temporary kind cluster;
5. deploys the application and runs basic smoke tests.

The release workflow runs for SemVer tags such as `v1.2.0`. Release tags must point to commits from `main`.

It builds one application image and publishes it to GHCR with:
1. the release version, such as `1.2.0`;
2. the Git commit tag, such as `sha-a8c41e7`.

Both tags point to the same image digest. The `latest` tag is not used.

Released images can be pulled and used with Docker, kind, or any Kubernetes cluster.

The Helm chart may also be published to GHCR as an OCI artifact with the same release version. This is optional and will be added only after image publishing works.

## Alternatives
Publishing an image for every commit was considered, but it would create many unused artifacts.

Using an external Kubernetes cluster for CI was also considered, but kind is simpler, isolated, and does not require cloud credentials.

## Consequences
1. Pull requests validate the complete Kubernetes deployment path without publishing artifacts.
2. Releases are traceable to a version, Git commit, and immutable image digest.
3. Publishing the Helm chart adds a complete installation artifact, but also requires chart version management and extra release logic.
