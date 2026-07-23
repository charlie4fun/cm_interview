.PHONY: help check-env setup check test image cluster deploy verify-local local-delivery clean-cluster

CLUSTER_NAME ?= interview-dev
NAMESPACE ?= interview
RELEASE_NAME ?= interview
IMAGE_REPOSITORY ?= interview-app
APP_VERSION ?= dev
COMMIT_SHA ?= $(shell git rev-parse --short HEAD 2>/dev/null || echo unknown)
IMAGE_TAG ?= $(APP_VERSION)
IMAGE := $(IMAGE_REPOSITORY):$(IMAGE_TAG)

help: ## List available commands.
	@awk 'BEGIN {FS = ":.*## "} /^[a-zA-Z_-]+:.*## / {printf "%-12s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

check-env: ## Check required tools, versions, and Docker daemon access.
	@python3 scripts/check_environment.py

setup: ## Install project-local tools and Git hooks.
	@python3 scripts/check_environment.py --skip-pre-commit
	python3 -m venv .venv
	.venv/bin/python -m pip install --upgrade pip
	.venv/bin/python -m pip install -r requirements-dev.txt
	@python3 scripts/check_environment.py
	.venv/bin/pre-commit install

check: ## Run repository checks.
	.venv/bin/pre-commit run --all-files

test: ## Run Python tests.
	.venv/bin/python -m unittest discover -s tests -v

image: ## Build the local application image.
	docker build \
		--build-arg APP_VERSION=$(APP_VERSION) \
		--build-arg COMMIT_SHA=$(COMMIT_SHA) \
		--tag $(IMAGE) .

cluster: ## Create the local kind cluster if it does not exist.
	@if ! kind get clusters | grep -qx '$(CLUSTER_NAME)'; then \
		kind create cluster --name $(CLUSTER_NAME) --config cluster/kind.yaml; \
	fi

deploy: image cluster ## Load the image and deploy it with Helm.
	kind load docker-image $(IMAGE) --name $(CLUSTER_NAME)
	helm upgrade --install $(RELEASE_NAME) charts/interview-app \
		--kube-context kind-$(CLUSTER_NAME) \
		--namespace $(NAMESPACE) \
		--create-namespace \
		--set-string image.repository=$(IMAGE_REPOSITORY) \
		--set-string image.tag=$(IMAGE_TAG) \
		--set-string deploymentRevision=$(COMMIT_SHA) \
		--wait --timeout 90s

verify-local: ## Verify endpoints, probes, rolling updates, and graceful shutdown.
	CLUSTER_NAME=$(CLUSTER_NAME) NAMESPACE=$(NAMESPACE) RELEASE_NAME=$(RELEASE_NAME) \
		CHART=charts/interview-app scripts/verify_local_delivery.sh

local-delivery: deploy verify-local ## Build, deploy, and verify the complete local path.

clean-cluster: ## Delete the local kind cluster.
	kind delete cluster --name $(CLUSTER_NAME)
