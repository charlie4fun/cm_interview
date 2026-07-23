# ADR-0004: AI-Assisted Deployment Diagnostics

## Status
Proposed

## Context
AI may still be useful as an optional troubleshooting aid. It can help an engineer understand why a deployment failed by combining Kubernetes events, logs, resource state, configuration, and validation results.

This feature is out of scope for the current implementation and is documented only as a possible future extension.

## Decision
An optional read-only AI agent may be used to assist with deployment diagnostics.

The agent must not replace linters, tests, policy checks, smoke tests, or Kubernetes validation. It must not apply patches, restart workloads, delete resources, change configuration, or make production decisions.

The intended responsibility split is:
1. deterministic tools provide facts and act as CI gates;
2. the AI agent explains and correlates those facts;
3. an engineer reviews and applies any proposed change.

The agent should be disabled by default and must not be required for CI/CD or local development.

## How It Works

A diagnostic command, for example `make diagnose`, would collect a limited support bundle containing:
1. Kubernetes resources and their current state;
2. recent events;
3. deployment and pod descriptions;
4. recent container logs;
5. relevant manifests;
6. validation and smoke-test results.

The agent would analyse this data and return:
1. a short problem summary;
2. likely root causes;
3. supporting evidence;
4. confidence levels;
5. suggested verification commands;
6. a proposed remediation for manual review.

The agent must only have access to approved read-only commands and must not receive secrets or unrelated cluster data.

## Test Incidents

The agent should be evaluated against a small set of known failure scenarios:
1. Deployment or Service selector does not match Pod labels;
2. Service uses an incorrect target port;
3. container image cannot be pulled;
4. application enters `CrashLoopBackOff`;
5. smoke test fails because the Service has no endpoints.

Each scenario should define the expected findings and forbidden actions. For example, the agent may identify a selector mismatch, but it must never run `kubectl apply`, `kubectl patch`, or `kubectl delete`.

## Consequences

This approach may improve troubleshooting speed and make failures easier to explain during development and incident review.

It also introduces risks such as incorrect conclusions, inconsistent output, data exposure, and unnecessary complexity. These risks are limited by keeping the agent optional, read-only, isolated from CI gates, and subject to human review.

The project remains fully operational without this feature.
