.PHONY: help check-env setup check test

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
	python3 -m unittest discover -v
