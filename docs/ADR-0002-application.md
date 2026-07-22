# ADR-0002: Application Design

## Status
Accepted

## Context
The assignment needs a small application that demonstrates delivery and operational practices without adding unrelated business logic.

## Decisions
1. Implement the service in Python using only the standard library.
2. Expose build information at `/`, liveness at `/healthz`, readiness at `/readyz`, and Prometheus-compatible metrics at `/metrics`.
3. Write structured JSON logs to standard output and support graceful shutdown on `SIGTERM` and `SIGINT`.
4. Configure the application through environment variables and provide version and commit metadata at runtime.
5. Keep monitoring infrastructure out of scope; `/metrics` only provides an integration point.

## Consequences
The application is small, has no runtime dependencies, and is easy to run and explain. The standard-library HTTP server is sufficient for this exercise but is not intended to replace a production application server.
