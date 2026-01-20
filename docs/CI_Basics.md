# Continuous Integration (CI) Pipeline

## Pre-Requisite

### What is CI?
**CI (Continuous Integration)** means:
- Every time code is pushed or a PR is opened, Automatically :
    - Build
    - Test
    - Lint
    - Scan
- So broken or insecure code **never reaches production**

#### Is CI only about testing?
- No — CI includes **quality, security, and build verification**

### What is GitHub Actions?
GitHub Actions is **GitHub’s automation platform.**

It lets you define:
- **When** to run (push, PR, manual)
- **Where** to run (runner)
- **What** to run (jobs, steps)

All defined using **YAML workflows** like this file.

### What is a Runner?
A runner is a machine that executes the jobs defined in a GitHub Actions workflow.

Example:
```yaml
runs-on: ubuntu-latest
```
This means:
- GitHub gives you a fresh Ubuntu VM, with Linux, docker, git, etc pre-installed
- After the job → VM is destroyed

#### Types of runners
| Type                 | Meaning                       |
| -------------------- | ----------------------------- |
| GitHub-hosted runner | Managed by GitHub             |
| Self-hosted runner   | Your own server / VM          |

Why use GitHub-hosted runners?
- No maintenance, quick setup, free tier available

Why would someone use self-hosted?
- Custom hardware, GPUs, internal networks, cost at scale
- Github-Hosted runners cannot access private resources in your network

## CI Trigger Conditions

```yaml
on:
  push:
    branches: ["main"]
  workflow_dispatch:
```

The CI pipeline runs on:
- Pushes to the `main` branch
- Manual execution (`workflow_dispatch`) from GitHub UI

#### What if I mention push but NOT the branch?
- The CI runs on pushes to **all branches**

## `env` in Workflows
- `env` are like global environment variables for the workflow
- I had used it to avoid duplication of common values

Example:
```yaml
env:
  PYTHON_VERSION: "3.11"
  IMAGE_NAME: shorturl
```
> `SERVICE_PORT: "8001"` can be a potential addition here

#### Why do we need env at all?
- Avoid duplication
- Single source of truth
- Easy maintenance
- Cleaner YAML

### Scope of env
You can define env at 3 levels:
| Level          | Scope                             |
| -------------- | --------------------------------- |
| Workflow level | Available to **all jobs & steps** |
| Job level      | Available to **that job only**    |
| Step level     | Available to **that step only**   |


---

# JOBs
A job is a collection of steps that run on the same runner (VM).

Each job:

- Gets its own fresh machine
- Has its own filesystem
- Runs independently by default

#### Default behavior
All jobs run in parallel, unless restricted using `needs`.
```yaml
build-and-push:
  needs:
    - quality-tests
    - sast
    - sca
    - secrets-scan
```
This makes:
- Checks → parallel
- Build → gated

#### Merits of parallel jobs
- Faster pipelines
- Fail fast
- Independent responsibilities

#### Demerits of parallel jobs
- Repeated setup (checkout, tooling)
- More YAML
- More runner minutes

## `uses` vs `run`
`uses` runs a pre-built GitHub Action, while `run` executes shell commands on the runner.

### uses
```yaml
- uses: actions/checkout@v4
```
- Leverages existing actions from GitHub Marketplace or public repos
- Maintained by community/GitHub
- Cleaner and safer

#### Use `uses` when:
- Standard task
- Well-known tool
- Setup or integration

### run
```yaml
- run: pip install -r requirements.txt
```
- Executes custom shell commands/scripts
- More flexible and powerful