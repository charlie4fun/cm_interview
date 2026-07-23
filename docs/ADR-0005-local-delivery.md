# ADR-0005: Local Delivery Before CI/CD

## Status
Accepted

## Context
The application and local development environment are ready. The next step is to validate the complete delivery path: build the container image, deploy it with Helm to a local kind cluster, and verify its runtime behaviour.

Starting with GitHub Actions would require debugging Docker, Helm, Kubernetes, CI configuration, and GHCR permissions at the same time.

## Considered Options
#### 1. Build the GitHub Actions pipelines first.
This demonstrates CI/CD early, but failures are harder to investigate because they may come from the application, Dockerfile, workflow, registry, or Kubernetes configuration.

#### 2. Develop the local and CI workflows in parallel.
This provides early CI feedback, but increases complexity and may create differences between local and CI commands.

#### 3. Build a complete local vertical slice first.
Build the image locally, load it into kind, deploy it with Helm, and verify probes, rolling updates, and graceful shutdown. Then reuse the same commands in GitHub Actions.

## Decision
Choose the third option.

The local delivery path will be:
application → container image → kind cluster → Helm deployment → runtime verification

The kind cluster will be named `interview-dev`.

After the local workflow is working, add:
1. `ci.yml` for tests, code checks, image builds, and Helm validation;
2. `release.yml` for publishing versioned images to GHCR.

GitHub Actions should automate an already working local process instead of implementing a separate delivery process.

## Consequences
Docker, Helm, and Kubernetes problems can be investigated locally without depending on GitHub Actions or GHCR. The same Makefile commands can later be reused in CI.

Image publishing and the final CI/CD pipelines will be added only after the local delivery path is verified.
