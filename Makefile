.PHONY: help check-env install setup check test chart e2e image pull-release cluster deploy-built deploy deploy-release verify-local local-delivery release-delivery clean-cluster

CLUSTER_NAME ?= interview-dev
NAMESPACE ?= interview
RELEASE_NAME ?= interview
IMAGE_REPOSITORY ?= interview-app
GHCR_IMAGE_REPOSITORY ?= ghcr.io/charlie4fun/cm_interview
APP_VERSION ?= dev
COMMIT_SHA ?= $(shell git rev-parse --short HEAD 2>/dev/null || echo unknown)
IMAGE_TAG ?= $(APP_VERSION)
IMAGE := $(IMAGE_REPOSITORY):$(IMAGE_TAG)

help: ## List available commands.
	@awk 'BEGIN {FS = ":.*## "} /^[a-zA-Z_-]+:.*## / {printf "%-12s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

check-env: ## Check required tools, versions, and Docker daemon access.
	@python3 scripts/check_environment.py

install: ## Install project-local development dependencies.
	python3 -m venv .venv
	.venv/bin/python -m pip install --upgrade pip
	.venv/bin/python -m pip install -r requirements-dev.txt

setup: install ## Install development dependencies and Git hooks.
	.venv/bin/pre-commit install

check: ## Run lint and unit tests.
	.venv/bin/pre-commit run --all-files
	.venv/bin/ruff check app tests scripts
	.venv/bin/shellcheck scripts/*.sh
	.venv/bin/python -m unittest discover -s tests -v

test: ## Run Python tests.
	.venv/bin/python -m unittest discover -s tests -v

chart: ## Validate the Helm chart.
	helm lint charts/interview-app

e2e: check-env chart ## Validate and run the complete local delivery path.
	$(MAKE) local-delivery

image: ## Build the local application image.
	docker build \
		--build-arg APP_VERSION=$(APP_VERSION) \
		--build-arg COMMIT_SHA=$(COMMIT_SHA) \
		--tag $(IMAGE) .

pull-release: ## Pull a released image from GHCR (requires RELEASE_VERSION).
	@test -n "$(RELEASE_VERSION)" || { \
		echo "RELEASE_VERSION is required, for example: RELEASE_VERSION=0.1.0" >&2; \
		exit 1; \
	}
	docker pull $(GHCR_IMAGE_REPOSITORY):$(RELEASE_VERSION)

cluster: ## Create the local kind cluster if it does not exist.
	@if ! kind get clusters | grep -qx '$(CLUSTER_NAME)'; then \
		kind create cluster --name $(CLUSTER_NAME) --config cluster/kind.yaml; \
	fi

deploy-built: cluster ## Load the existing image and deploy it with Helm.
	kind load docker-image $(IMAGE) --name $(CLUSTER_NAME)
	helm upgrade --install $(RELEASE_NAME) charts/interview-app \
		--kube-context kind-$(CLUSTER_NAME) \
		--namespace $(NAMESPACE) \
		--create-namespace \
		--set-string image.repository=$(IMAGE_REPOSITORY) \
		--set-string image.tag=$(IMAGE_TAG) \
		--set-string deploymentRevision=$(COMMIT_SHA) \
		--wait --timeout 90s

deploy: image deploy-built ## Build, load, and deploy the application.

deploy-release: pull-release ## Pull and deploy a released image from GHCR.
	$(MAKE) deploy-built \
		IMAGE_REPOSITORY=$(GHCR_IMAGE_REPOSITORY) \
		IMAGE_TAG=$(RELEASE_VERSION) \
		COMMIT_SHA=release-$(RELEASE_VERSION)

verify-local: ## Verify endpoints, probes, rolling updates, and graceful shutdown.
	CLUSTER_NAME=$(CLUSTER_NAME) NAMESPACE=$(NAMESPACE) RELEASE_NAME=$(RELEASE_NAME) \
		CHART=charts/interview-app scripts/verify_local_delivery.sh

local-delivery: deploy verify-local ## Build, deploy, and verify the complete local path.

release-delivery: deploy-release verify-local ## Deploy and verify a released GHCR image.

clean-cluster: ## Delete the local kind cluster.
	kind delete cluster --name $(CLUSTER_NAME)
