# Automation Exercise Test Automation

Playwright Python test framework for [automationexercise.com](https://automationexercise.com/), covering browser flows and the public REST API with maintainable page objects, typed response validation, and CI-ready quality checks.

## What This Demonstrates

- Page Object Model coverage for core ecommerce flows.
- API validation for all 14 documented Automation Exercise endpoints.
- Pydantic models for response contracts and account form payloads.
- Reusable pytest fixtures for browser pages, API contexts, test data, and cleanup.
- Local quality gates with Ruff, mypy, pytest, and pre-commit.
- GitHub Actions workflow for linting, type checking, and test execution.

## Setup

```powershell
uv sync --dev
uv run playwright install
```

For account-based tests, copy `.env.example` to `.env` and fill in the optional credentials.

## Common Commands

```powershell
# Run the full suite
uv run pytest

# Run targeted suites
uv run pytest -m smoke
uv run pytest -m api
uv run pytest -m "e2e and not api"

# Run specific modules
uv run pytest tests/api/test_api.py
uv run pytest tests/test_products.py

# Debug locally with a visible browser
uv run pytest --headed

# Run checks before opening a pull request
uv run ruff check .
uv run ruff format --check .
uv run mypy pages tests conftest.py
```

## API Tests

The API test suite covers all 14 endpoints documented on the
[API list page](https://automationexercise.com/api_list). Responses are
validated against Pydantic models defined in `tests/api/api_models.py`.

> Note: the Automation Exercise API always responds with HTTP 200 and carries
> the real status in the JSON body's `responseCode` field; tests assert on that
> rather than the HTTP status.

```powershell
uv run pytest -m api            # run only the API tests
uv run pytest tests/api/test_api.py # run the API test module directly
```

Account-mutating tests (create/update/delete/login) self-clean up via the
`created_account` fixture, which deletes the test account in teardown even if a
test assertion fails.

## Quality Checks And CI

```powershell
uv run ruff check .
uv run ruff format --check .
uv run mypy pages tests conftest.py
uv run pytest
```

The GitHub Actions workflow in `.github/workflows/tests.yml` runs the same checks on pushes and pull requests. It installs dependencies with `uv`, installs Playwright browsers, uploads Playwright failure artifacts when available, and keeps the commands aligned with local development.

## Structure

- `pages/`: page objects and reusable UI components
- `tests/`: pytest test modules and test-level fixtures
- `conftest.py`: project-wide fixtures and environment loading
- `tests/api/api_models.py`: Pydantic contracts for API responses and account payloads
