.PHONY: install lint format test clean help

# Python interpreter to use
PYTHON := python3.12
# Poetry executable
POETRY := poetry
# Source directory
SRC_DIR := ars
# Test directory
TEST_DIR := tests

help:  ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install:  ## Install dependencies using Poetry
	$(POETRY) install

update:  ## Update dependencies to their latest versions
	$(POETRY) update

lint:  ## Run all linting checks
	$(POETRY) run ruff check $(SRC_DIR) $(TEST_DIR) --fix
	$(POETRY) run black --check $(SRC_DIR) $(TEST_DIR)
	$(POETRY) run isort --check-only $(SRC_DIR) $(TEST_DIR)

format:  ## Format code using black and isort
	$(POETRY) run black $(SRC_DIR) $(TEST_DIR)
	$(POETRY) run isort $(SRC_DIR) $(TEST_DIR)

fix:  ## Fix linting issues automatically where possible
	$(POETRY) run ruff check --fix $(SRC_DIR) $(TEST_DIR)
	$(POETRY) run black $(SRC_DIR) $(TEST_DIR)
	$(POETRY) run isort $(SRC_DIR) $(TEST_DIR)

test:  ## Run tests with pytest
	$(POETRY) run pytest -v $(TEST_DIR)

test-cov:  ## Run tests with coverage report
	$(POETRY) run pytest --cov=$(SRC_DIR) --cov-report=term-missing $(TEST_DIR)

clean:  ## Clean up Python cache files
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	find . -type f -name ".coverage" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name "*.egg" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".ruff_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +

build:  ## Build the package
	$(POETRY) build

dev:  ## Install the package in development mode
	$(POETRY) install --with dev

run:  ## Run the CLI application
	$(POETRY) run ars

check: lint test  ## Run all checks (linting and tests)

pre-commit: format lint test  ## Run all pre-commit checks 