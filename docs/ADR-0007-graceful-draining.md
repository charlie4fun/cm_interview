# ADR-0007: Add Graceful Draining

## Status
Proposed

## Context
The application handles `SIGTERM`: it changes its readiness state, stops the
HTTP server, and exits. The Helm chart has no `preStop` hook. An earlier hook
only sent `GET /readyz`, which did not change the readiness state or start
draining, so it was removed.

The current signal handling does not guarantee that active requests finish
during Pod termination.

## Decision
If this proposal is implemented:

1. Add an idempotent `POST /drain` endpoint that changes readiness to false.
2. Add a `preStop` hook that calls `/drain` through localhost and waits for
   Kubernetes to remove the Pod from Service endpoints.
3. Adjust the readiness probe and termination grace period for the drain
   delay.
4. Make the HTTP server stop accepting new requests and wait for active
   requests to finish.
5. Add unit tests for `/drain` and an end-to-end test with traffic during Pod
   termination.

## Consequences
Until this proposal is implemented, the demo shows clean `SIGTERM` handling
but not full graceful draining. Implementation will add lifecycle complexity
and make termination tests slower, but it will demonstrate that active
requests can finish without sending new traffic to a terminating Pod.
