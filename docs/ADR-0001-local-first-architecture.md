# ADR-0001: Local-first architecture

## Status

Accepted

## Decision

Run Kubernetes locally with kind, deploy with Helm, build the application in Python, and use GitHub Actions for CI and automated releases.

Do not introduce cloud infrastructure or services. This keeps the assignment reproducible, free to run, and focused on delivery and operations.
