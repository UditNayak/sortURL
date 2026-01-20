# Job 1: Quality & Test
This job ensures the codebase is correct and maintainable by running linting and unit tests on a clean machine.

- If this job fails → pipeline stops (because build depends on it).

### Job header
```yaml
quality-tests:              # job id
  name: Quality & Tests     # job name (UI display)
  runs-on: ubuntu-latest    # runner environment
```

## Steps-by-Step

### Step 1: Checkout code
```yaml
- name: Checkout code
  uses: actions/checkout@v4
```

**Purpose**: Clones the repo into the runner(VM) filesystem

#### Why this is mandatory
- Runner starts empty
- Your repository code is not present by default

### Step 2: Set up Python
```yaml
- name: Set up Python
  uses: actions/setup-python@v5
  with:
    python-version: ${{ env.PYTHON_VERSION }}
    cache: pip
    cache-dependency-path: src/requirements.txt
```

**What this does**:
1. Installs Python 3.11
2. Sets it as the active python
3. Enables pip dependency caching

**Why caching matters**:
- Without cache → pip installs every run
- With cache → faster CI, fewer downloads

### Step 3: Install dependencies
```yaml
- name: Install dependencies
  run: |
    python -m pip install --upgrade pip
    pip install -r src/requirements.txt
```

**Why two commands?**
- Upgrade pip → avoid old-version bugs
- Install project dependencies

### Step 4: Linting (ruff)
```yaml
- name: Lint (ruff)
  run: ruff check src tests
```

**What linting means**: Static analysis to detect style issues, unused imports, bad patterns.

- Linting do not guarantee correctness, it only checks code quality not logic.

#### What Ruff actually checks:
- Unused imports
- Unused variables
- Syntax mistakes
- Bad coding patterns
- Formatting issues

**Why Ruff and not something else?**
| Tool     | Why / Why not                   |
| -------- | ------------------------------- |
| **Ruff** | Very fast, all-in-one, modern |
| flake8   | Slower, plugin-heavy          |
| pylint   | Very slow, too strict         |
| black    | Formatter only (not a linter) |


**Why lint BEFORE tests?**
- Faster feedback
- Cheaper failure
- No need to run tests on bad code

### Step 5: Unit tests
```yaml
- name: Unit tests
  env:
    ENV: test
  run: |
    pytest -v --cov=src --cov-report=term-missing
```

**What this does**:
- Runs unit tests with verbose output
- Generates coverage report

| Command                     | What it does          |
| --------------------------- | --------------------- |
| `pytest -v`                 | Runs tests only       |
| `pytest -v --cov=src`       | Tests + coverage      |
| `--cov-report=term-missing` | Shows uncovered lines |

- `-v` is for verbose output (see which tests ran)

```
yaml pytest -v --cov=src --cov-fail-under=80
```
- This would fail the job if coverage is under 80%

---

# Job 2: SAST (CodeQL)

> SAST (Static Application Security Testing) analyzes source code to find security vulnerabilities without running the application.

### Why CodeQL?
CodeQL is GitHub’s native SAST tool that uses semantic code analysis to detect security vulnerabilities accurately.

**Why it’s chosen:**
- Built into GitHub Security tab
- Deep understanding of code (not regex-based)
- Minimal setup
- Industry-standard

### Permissions block
```yaml
permissions:
  actions: read
  contents: read
  security-events: write
```

CodeQL needs to:
- Read repository code
- Upload findings to GitHub Security → Code scanning

Without: `security-events: write`, findings cannot be uploaded to GitHub Security tab.

### Step 1: Checkout step
Still required:
- CodeQL scans source code
- Runner starts empty

### Step 2: Initialize CodeQL
```yaml
- name: Initialize CodeQL
  uses: github/codeql-action/init@v4
  with:
    languages: python
    build-mode: none
```
- `languages: python` → Tells CodeQL what analyzers to load

#### Why `build-mode: none`?
- Python is interpreted, don't need compilation → no build step
- It tells CodeQL: “Don’t try to build anything. Just scan the source code.”
- Speeds up the process

### Step 3: Perform CodeQL Analysis
```yaml
- name: Perform CodeQL Analysis
  uses: github/codeql-action/analyze@v4
```
**What it does:**
- Runs security queries
- Uploads results to GitHub

Without this → no scan actually happens.

---

# Job 3: SCA (Dependency Scanning)
> SCA (Software Composition Analysis) checks third-party dependencies for known vulnerabilities.

### Why OWASP Dependency-Check?
OWASP Dependency-Check scans dependencies against public vulnerability databases like NVD to detect known CVEs.

**Why it’s used:**
- OWASP-backed (trusted)
- Language-agnostic
- Widely accepted in security audits

### Step 1: Checkout code
Required because: Tool needs access to requirements.txt

### Step 2: Run OWASP Dependency-Check
```yaml
- name: Run OWASP Dependency-Check
  uses: dependency-check/Dependency-Check_Action@1.1.0
  with:
    project: shorturl
    path: src/requirements.txt
    format: HTML
    args: >
      --enableExperimental
      --out reports
```

- `project: shorturl`: Just a label for the report
- `path: src/requirements.txt`: Tells the tool what dependencies to scan
- `format: HTML`: Output format for the report
- `--enableExperimental`: Enables additional checks for Python dependencies
- `--out reports`: Saves the report in the `reports` directory

### Step 3: Upload SCA report as artifact
```yaml
- name: Upload Dependency Check Report
  uses: actions/upload-artifact@v4
```

- This allows you to download the SCA report from the workflow run page after execution.

```
continue-on-error: true
```
- This means that even if the SCA scan finds vulnerabilities (which would normally fail the job), the job will not fail. This allows you to review the report without blocking the entire pipeline.

---

# Job 4: Secrerts Scanning (GitLeaks)
> This job scans the Git repository for hard-coded secrets that were accidentally committed.

That’s it. No build. No runtime. Just history inspection.

#### What exactly are we checking here?
Gitleaks looks for things like:
- API keys
- Tokens
- Passwords
- Private keys
- Cloud credentials (AWS, GitHub, Docker, etc.)

It does this by:
- Pattern matching (known secret formats)
- Entropy checks (random-looking strings)
- Commit history scanning

Important: It scans source code + git history, not running containers or env vars.

#### Why do we even need secrets scanning?
Secrets committed to Git are permanent and hard to fully remove, so scanning prevents credential leaks early.

### Why Gitleaks?
> Gitleaks is a fast, widely used tool specifically designed to detect secrets in Git repositories.

### Important detail: fetch-depth: 0
```yaml
        with:
          fetch-depth: 0
```

**Why is this needed?**
- By default, `actions/checkout`:fetches only the latest commit.
- But secrets could be: Added in an old commit & Later removed (still dangerous)

- `fetch-depth: 0` means: “Clone the full Git history.”

---

# Job 5: Build, Scan & Push
> This job builds a Docker image, verifies it is safe and working, and then pushes it to Docker Hub only if all checks pass.

### Step 1: Checkout code
- Docker build needs the Dockerfile and source code

### Step 2: Docker Buildx
```yaml
- name: Set up Docker Buildx
  uses: docker/setup-buildx-action@v3
```
- Enables advanced Docker builds (multi-platform, cache)

**Is it required here?**

No, because:
- You are doing a simple docker build
- No multi-arch, no cache config

### Step 3: Login to Docker Hub
```yaml
      - name: Docker login
        uses: docker/login-action@v3
        with:
          username: ${{ secrets.DOCKERHUB_USERNAME }}
          password: ${{ secrets.DOCKERHUB_TOKEN }}
```
- Required to push images to Docker Hub
- Uses encrypted GitHub secrets

### Step 4: Build image
```yaml
- name: Build image
  run: |
    IMAGE=${{ secrets.DOCKERHUB_USERNAME }}/${{ env.IMAGE_NAME }}
    SHA_TAG=sha-${GITHUB_SHA::7}

    docker build -t $IMAGE:latest -t $IMAGE:$SHA_TAG .
```

**Why two tags?**:
- `latest` → human-friendly
- `sha-xxxxxxx` → immutable, traceable

### Step 5: Scan image with Trivy
> Trivy scans a Docker image to find known security vulnerabilities before it is deployed.
```yaml
- name: Image scan (Trivy)
  uses: aquasecurity/trivy-action@0.24.0
```

In simple terms:
- You built an image
- Trivy opens it
- Checks what’s inside
- Warns if something dangerous is found

#### What exactly does Trivy check?
- OS packages (e.g., apt, yum)
- Application dependencies (e.g., Python packages)
- Known CVEs (Common Vulnerabilities and Exposures) - public vulnerability database

**Note**: Trivy does not check your source code logic
(that’s SAST’s job)

```yaml
with:
  image-ref: <image>
  exit-code: 1
  severity: CRITICAL
```

- `image-ref`: The Docker image to scan
- `severity: CRITICAL`: Only fail on critical vulnerabilities 
    - Severity levels: LOW, MEDIUM, HIGH, CRITICAL
- `exit-code: 1`: If vulnerabilities matching the severity filter are found, fail the job.
    - `0`: CI always pass
    - `1`: CI fail on findings

### Step 6: Container Smoke Test
> A smoke test is a quick check to verify that the application starts and basic functionality works.
```yaml
      - name: Container Smoke Testing
        run: |
          docker run -d -p 8001:8001 --name shorturl-test \
            ${{ secrets.DOCKERHUB_USERNAME }}/${{ env.IMAGE_NAME }}:latest
          sleep 5
          curl -f http://localhost:8001/api/health
```
A container smoke test verifies that a Docker image can start successfully and respond to a basic request.

```
curl -f http://localhost:8001/api/health
```
- Calls health endpoint
- `-f` → fails if HTTP status is not 2xx
- If the container fails to start or the health check fails → job fails

### Step 7: Push image to Docker Hub
> This step uploads the built Docker image from the CI runner to Docker Hub so it can be reused or deployed.

```yaml
      - name: Push image
        run: |
          IMAGE=${{ secrets.DOCKERHUB_USERNAME }}/${{ env.IMAGE_NAME }}
          SHA_TAG=sha-${GITHUB_SHA::7}

          docker push $IMAGE:latest
          docker push $IMAGE:$SHA_TAG
```

```
IMAGE=username/image_name
```
Why this format?
- Docker Hub images are namespaced by username
- Ensures the image is pushed to your repository

#### Why SHA tag push?
- `latest` tag can change (not immutable)
- `sha-xxxxxxx` tag is fixed to a specific commit
    - Useful for rollbacks and traceability
- Both tags are pushed for flexibility in deployment strategies.

### Step 8: Cleanup
> This step ensures that the test container is removed so the CI runner is left in a clean state.

```yaml
      - name: Cleanup
        if: always()
        run: docker rm -f shorturl-test || true
```

#### `if: always()`
**Why?**
- By default, steps run only if previous steps succeed
- `always()` forces this step to run:
    - Even if tests fail
    - Even if Trivy fails
    - Even if smoke test fails

`always()` ensures cleanup runs regardless of job success or failure.

**Without this:**
- Container might remain running
- Future steps may fail due to conflicts

#### Docker remove command
```bash
docker rm -f shorturl-test
```
- `rm`: Remove container
- `-f`: Force stop if running

#### `|| true`
> ensures cleanup errors don’t affect the job result.
```yaml
docker rm -f shorturl-test || true
```
- Prevents cleanup failure from failing the job
- Handles cases where:
    - Container never started
    - Container was already removed