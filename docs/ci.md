# Continuous Integration (CI) Pipeline

This document explains the basic GitHub Actions–based CI pipeline used in this project and the reasoning behind each stage.

## CI Trigger Conditions

The CI pipeline runs on:

- Pushes to the `main` branch
- Pull requests targeting `main`
- Manual execution (`workflow_dispatch`)

This ensures all critical code paths are validated before integration.

---

## CI Workflow Overview

The CI workflow is defined in: `.github/workflows/ci.yml`


It consists of a single job with multiple ordered steps.


## 📦 CI Stages and Justification

### 1. Checkout Source Code
```yaml
uses: actions/checkout@v4
```

**Purpose**:
- Retrieves the repository code for the CI runner

**Why it matters:**
- CI cannot operate without a clean copy of the source code

### 2. Set Up Python Runtime
```yaml
uses: actions/setup-python@v5
python-version: 3.11
```

**Purpose**:
- Ensures a consistent and stable Python runtime

**Why it matters:**
- Prevents environment-specific bugs
- Python 3.11 is stable and widely supported in CI environments

### 3. Install Dependencies
```yaml
python -m pip install --upgrade pip
pip install -r requirements.txt
```

**Purpose:**
- Installs application, testing, and linting dependencies

**Why it matters:**
- Guarantees CI uses declared dependencies only
- Prevents “works on my machine” issues

### 4. Linting (Code Quality Gate)
```yaml
ruff check src tests
```

**Purpose:**
- Enforces coding standards
- Detects unused imports, bad patterns, and style issues

**Why it matters:**
- Prevents technical debt
- Fails fast before running more expensive stages
- Improves maintainability and readability

### 5. Automated Tests
```yaml
pytest -v --cov=src
```

**Purpose:**
- Executes unit and API smoke tests
- Generates coverage metrics

**Why it matters:**
- Validates core functionality
- Prevents regressions
- Acts as a CI quality gate before further stages (security, Docker)

## 🔐 Test Environment

The CI pipeline runs tests using:
```env
ENV=test
```

This ensures:
- Isolation from local or production environments
- Use of a separate SQLite test database

## ✅ Current CI Scope

This initial CI pipeline focuses on:
- Continuous Integration
- Code Quality (Linting)
- Automated Testing

Security scanning, containerization, and deployment stages will be added incrementally.

## 📈 Future Enhancements

Planned CI/CD improvements include:
- Static Application Security Testing (SAST)
- Dependency vulnerability scanning (SCA)
- Docker image build and validation
- Container security scanning
- Deployment workflows