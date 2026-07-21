# ADR-0001: Local-First Architecture, Repository Structure, and Tools

## Status
Accepted

## Context
The task description is intentionally flexible. The main strict requirements are that the solution must run locally, must not use cloud providers, and should address several expectations that can be derived from the job description.

I chose reproducibility as the main design principle. Additional context was taken from the position description.

This ADR defines the repository structure and the tools used in the solution.

## Decisions

#### 1. Kind
I chose kind not because it is the closest option to a production environment, but because the deployment must be local-first and the main risk of this task is the reproducibility of the solution in CI, on a developer machine, and on a reviewer’s machine.

Kind creates an isolated Kubernetes cluster using Docker containers. It does not install system services, works well with rootless container runtimes, and allows locally built images to be loaded into the cluster explicitly.

Minikube would also be a suitable option, especially for interactive development and Ingress demonstrations. However, its behaviour depends more heavily on the selected driver and operating system.

K3s is useful for homelabs, edge environments, and lightweight long-running clusters. In this case, however, its deeper integration with the host networking and operating system would increase the chance of environment-specific problems during review without demonstrating additional skills required by the task.

#### 2. Helm
Plain Kubernetes YAML files would be simpler and sufficient for a reproducible solution. However, the job description places significant emphasis on Helm, so I will use this task to demonstrate parameterisation, release versioning, and reusable packaging, provided there is enough time.

Argo CD will not be used because it would be excessive for a local scenario. It would introduce an additional component, a bootstrap process, and unnecessary operational overhead.

#### 3. GitHub Actions and GHCR
The position description mentions GitLab, but the test assignment specifically asks candidates to use GitHub.

GitHub Actions is the most natural CI/CD option for a repository hosted on GitHub. The workflows will demonstrate two common scenarios: continuous integration and release automation.

GHCR was selected to complete the Helm-based release and deployment workflow.

#### 4. Bash and Python
The application will be implemented in Python. The position description mentions Bash, Python, and Go, but this assignment is focused on delivery and operations. I therefore chose the language I am most comfortable with.

Bash scripts will be used to configure and manage the local environment.

#### 5. Monorepo
In production environments, CI templates, application code, and infrastructure configuration are often stored separately to simplify teamwork and separate responsibilities.

For this small assignment, however, the application, kind cluster configuration, and deployment configuration form a single deliverable. A monorepo provides atomic changes, simple CI, and easier review.

#### 6. Additional conventions
1. Use Semantic Versioning instead of using latest as the only image tag.
2. Link each release to a Git tag.
3. Provide a minimal interface through a Makefile.
4. Support fast cleanup.
5. Include a smoke test that runs against the kind cluster.
6. Pin GitHub Actions versions.
7. Do not store secrets in Git.
8. Use Conventional Commits (https://www.conventionalcommits.org/en/v1.0.0/)

#### 7. Out of scope
The following components and practices will not be included:
1. Terraform
2. Argo CD
3. Prometheus, Grafana, or Loki
4. A database
5. A service mesh
6. Vault
7. Multiple environments
8. Complex Ingress or TLS configuration
9. A custom Kubernetes operator
10. Generated documentation
11. Not to add: CONTRIBUTORS.md, CODEOWNERS, SUPPORT.md

## Consequences
1. The solution should be easy to run in CI and on different developer machines.
2. Kind provides good isolation and reproducibility, but it is not a full production-like Kubernetes environment.
3. Helm adds some complexity compared to plain YAML, but demonstrates reusable and versioned deployments.
4. The monorepo makes changes and reviews simpler, but would be less suitable for a larger project with multiple teams.
5. GitHub Actions and GHCR provide a simple automated release process, but the workflow is specific to GitHub.
6. Not using GitOps or additional infrastructure tools keeps the solution small and easy to understand, but demonstrates fewer production operations practices.

