# Testing Guide

This document explains how to run tests locally and how testing is structured in the project.



## 📁 Test Structure

Tests are located in the `tests/` directory and are organized by purpose:

- **API tests** – Validate key HTTP endpoints
- **Service tests** – Validate core business logic
- **Utility tests** – Validate pure helper functions

Tests are intentionally minimal and focused on CI reliability.

## Test Files

| File               | Purpose                                |
| ------------------ | -------------------------------------- |
| `conftest.py`      | Shared fixtures (app, client, test DB) |
| `test_utils.py`    | Pure unit tests (no FastAPI, no DB)    |
| `test_services.py` | One core business-logic test           |
| `test_api.py`      | API smoke tests (health + happy path)  |
| `pytest.ini`       | Pytest configuration for CI            |




## 📦 Test Dependencies

Testing dependencies are included in `src/requirements.txt`:

- `pytest`
- `pytest-cov`
- `httpx` (required by FastAPI TestClient)

Install dependencies (if not already installed):

```bash
pip install -r src/requirements.txt
```

## 🔐 Test Environment

Tests run in an isolated environment.

### Environment File

| File        | Purpose            | Git       |
| ----------- | ------------------ | --------- |
| `.env.test` | Test configuration | ❌ Ignored |

Recommended `.env.test`:
```env
ENV=test
DB_PATH=./data/test.db
```

## 🧪 Running Tests

Run all tests from the project root:

```bash
pytest
```

Run tests with coverage:

```bash
pytest -v --cov=src
```

## 🗄 Test Database
- SQLite is used for testing
- Database file is created automatically
- Default location: data/test.db
- Database files are ignored by git

## What Tests Validate
- Application starts correctly
- Core API endpoints respond as expected
- URL shortening logic works
- Utility functions behave correctly

## Linting
Run linting with:

```bash
ruff check src tests
```