# Architecture

The project uses Python for the application and tooling. Kubernetes runs locally with kind, Helm manages application deployment, and GitHub Actions provides CI and automated releases.

Cloud infrastructure must not be introduced. Terraform, Argo CD, Flux, ingress, monitoring, and databases are out of scope.
