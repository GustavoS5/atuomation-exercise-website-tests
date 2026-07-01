# Automation Exercise Test Automation

[![Tests](https://github.com/GustavoS5/automation-exercise-website-tests/actions/workflows/tests.yml/badge.svg)](https://github.com/GustavoS5/automation-exercise-website-tests/actions/workflows/tests.yml)
[![Locust smoke](https://github.com/GustavoS5/automation-exercise-website-tests/actions/workflows/locust-smoke.yml/badge.svg)](https://github.com/GustavoS5/automation-exercise-website-tests/actions/workflows/locust-smoke.yml)

Playwright Python test framework for [automationexercise.com](https://automationexercise.com/), covering browser flows and the public REST API with maintainable page objects, typed response validation, and CI-ready quality checks.

## What This Demonstrates

- Page Object Model coverage for core ecommerce flows.
- API validation for all 14 documented Automation Exercise endpoints.
- Pydantic models for response contracts and account form payloads.
- Reusable pytest fixtures for browser pages, API contexts, test data, and cleanup.
- Locust load profiles for read-only and stateful API behavior, including reports and thresholds.
- Local quality gates with Ruff, mypy, pytest, and pre-commit.
- GitHub Actions workflows for functional checks and manual Locust smoke validation.

## Setup

```powershell
uv sync --dev
uv run playwright install
```

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

## Load Testing With Locust

Locust complements the pytest suite by repeatedly exercising API behavior with
simulated users and reporting latency, throughput, percentiles, and failures.
The load profile lives in `performance/locustfile.py`.

Implemented Locust coverage:

- `AutomationExerciseApiUser`: read-only product, brand, and search traffic.
- `AutomationExerciseAccountUser`: stateful account flow with Faker-generated
  users, per-user setup, login/profile/update tasks, and teardown cleanup.
- Business-level validation using the API body's `responseCode`, not only the
  HTTP status.
- Shared JSON parsing failure handling so non-JSON responses are reported as
  Locust failures.
- Task tags for targeted runs: `browse`, `products`, `brands`, `search`,
  `account`, `login`, `profile`, and `update`.
- A gated `LearningLoadShape` enabled by `LOCUST_USE_SHAPE=1`.
- Global and per-endpoint thresholds that set the Locust process exit code.

Because this targets a public demo site, all committed examples use small
load profiles.

### Interactive Runs

```powershell
# Open the Locust web UI at http://localhost:8089
uv run locust -f performance/locustfile.py -H https://automationexercise.com
```

### Repeatable Local Scripts

```powershell
# Read-only API baseline with CSV/HTML reports
.\scripts\locust_api_baseline.ps1

# Search-only baseline using Locust tags
.\scripts\locust_search_baseline.ps1

# Small stateful account smoke run
.\scripts\locust_account_smoke.ps1

# Read-only API run using the custom load shape
.\scripts\locust_api_shape.ps1
```

Generated CSV and HTML reports are written under `reports/locust/`, which is
ignored by git.

### Thresholds

Locust runs fail by exit code when the configured thresholds are exceeded:

- aggregate failure ratio must remain `0%`
- aggregate average response time must stay at or below `1000 ms`
- aggregate p95 response time must stay at or below `2500 ms`
- selected endpoint p95 thresholds are checked individually, for example
  product/brand/search read paths and account login/profile/update paths

Skipped endpoints are ignored, so tag-filtered runs do not fail because an
unselected task did not execute.

## Quality Checks And CI

```powershell
uv run ruff check .
uv run ruff format --check .
uv run mypy pages tests conftest.py
uv run pytest
```

The GitHub Actions workflow in `.github/workflows/tests.yml` runs the same checks on pushes and pull requests. It installs dependencies with `uv`, installs Playwright browsers, uploads Playwright failure artifacts when available, and keeps the commands aligned with local development.

The manual `.github/workflows/locust-smoke.yml` workflow runs a tiny read-only
Locust smoke check and uploads the generated Locust CSV/HTML report artifacts.

## Structure

- `pages/`: page objects and reusable UI components
- `tests/`: pytest test modules and test-level fixtures
- `performance/locustfile.py`: Locust users, tags, load shape, and thresholds
- `scripts/`: repeatable local PowerShell commands for Locust runs
- `conftest.py`: project-wide fixtures and environment loading
- `tests/api/api_models.py`: Pydantic contracts for API responses and account payloads
