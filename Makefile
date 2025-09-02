# Makefile for Fal MCP Server development

.PHONY: help install test lint format ci-local ci-test ci-publish clean

help: ## Show this help message
	@echo "Usage: make [target]"
	@echo ""
	@echo "Available targets:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-15s %s\n", $$1, $$2}'

install: ## Install the package in development mode
	pip install -e ".[dev]"

test: ## Run tests
	pytest tests/ -v --asyncio-mode=auto --cov=src/fal_mcp_server --cov-report=term-missing

lint: ## Run linting
	ruff check src/ tests/

format: ## Format code
	black src/ tests/

typecheck: ## Run type checking
	mypy src/

check: format lint typecheck test ## Run all checks (format, lint, typecheck, test)

# Act commands for local CI testing
act-install: ## Install act (macOS with Homebrew)
	@which act > /dev/null || (echo "Installing act..." && brew install act)

ci-local: act-install ## Run CI workflow locally with act (tests only, NO release)
	@if [ ! -f .secrets ]; then \
		echo "Error: .secrets file not found. Copy .secrets.example to .secrets and add your keys."; \
		exit 1; \
	fi
	@echo "Running CI tests locally (no release/publish)..."
	act push --workflows .github/workflows/ci.yml

ci-test: act-install ## Test specific Python version locally
	@if [ ! -f .secrets ]; then \
		echo "Error: .secrets file not found. Copy .secrets.example to .secrets and add your keys."; \
		exit 1; \
	fi
	act push --workflows .github/workflows/ci.yml --matrix python-version:3.10

ci-publish: act-install ## Test publish workflow locally (dry run)
	@if [ ! -f .secrets ]; then \
		echo "Error: .secrets file not found. Copy .secrets.example to .secrets and add your keys."; \
		exit 1; \
	fi
	@echo "Testing publish workflow (dry run - won't actually publish)"
	act push --workflows .github/workflows/publish.yml --dryrun

clean: ## Clean build artifacts
	rm -rf build/ dist/ *.egg-info
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete