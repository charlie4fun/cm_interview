.PHONY: help setup check test

help: ## List available commands.
	@awk 'BEGIN {FS = ":.*## "} /^[a-zA-Z_-]+:.*## / {printf "%-12s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

setup: ## Install development tools.
	python3 -m pip install pre-commit

check: ## Run repository checks.
	pre-commit run --all-files

test: ## Run Python tests.
	python3 -m unittest discover -v
