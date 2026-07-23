# ADR-0002: Application Design

## Status
Accepted

## Context
The assignment needs a small application that demonstrates delivery and operational practices without adding unrelated business logic.

## Decisions
1. Implement the service in Python using only the standard library. Prebuilt echo servers and static web servers were considered. They would reduce initial implementation effort but provide limited control over application-level metrics, structured logging, readiness transitions, build metadata exposure, and graceful shutdown.
2. The application does not provide TLS, authentication, rate limiting, request size controls, or production-grade HTTP hardening.
3. Expose build information at `/`, liveness at `/healthz`, readiness at `/readyz`, and Prometheus-compatible metrics at `/metrics`.
4. Write structured JSON logs to standard output and support graceful shutdown on `SIGTERM` and `SIGINT`.
5. Configure the application through environment variables and provide version and commit metadata during the image build or release pipeline.
6. Keep monitoring infrastructure out of scope; `/metrics` only provides an integration point.

## Consequences
The application is small, has no runtime dependencies, and is easy to run and explain.
The standard-library HTTP server is sufficient for this exercise but is not intended to replace a production application server.
Metrics exposition and request instrumentation must be implemented and tested manually because no client library is used.
