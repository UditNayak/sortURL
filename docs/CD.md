# CD (Continuous Deployment)

CD (Continuous Deployment) automatically deploys the application after CI succeeds, so tested and secure code reaches the runtime environment.

## Continious Delivery V/S Continoius Deployment
Continuous Delivery ensures the application is always ready to deploy but requires manual approval, whereas Continuous Deployment automatically deploys every successful change to production.

### Continuous Delivery (CD – “Ready to deploy”)
Code is always in a deployable state, but deployment to production needs manual approval.

**Why teams use this**
- High control
- Compliance requirements
- Business approval needed

**Example**
- Pipeline builds & tests
- Artifact is ready
- Engineer clicks Deploy

### Continuous Deployment (CD – “Automatically deploy”)
Every successful change is automatically deployed to production without human intervention.

**Why teams use this**
- Faster feedback
- Rapid iteration
- Small, safe changes

**Example**
- Merge to main
- CI passes
- App is live in minutes

### Where does my pipeline fit?
My pipeline is Continuous Deployment, because deployment to AKS happens automatically after CI succeeds.

## Self-Managed K8s vs Cloud-Managed K8s (AKS)

#### Self-Managed Kubernetes

- You manage:
    - Control plane
    - etcd
    - Upgrades
    - Security patches
- More control
- More operational pain

**Used when**:
- Custom infra
- Special compliance needs

#### Cloud-Managed Kubernetes (AKS / EKS / GKE)
Cloud provider manages the control plane, you manage workloads.

**AKS gives you**:
- Managed API server
- Managed etcd
- Built-in scaling
- Azure IAM integration

**Why AKS here?**

AKS reduces operational complexity and lets us focus on deploying and running applications instead of managing Kubernetes itself.

## GitHub-Hosted Runner vs Self-Hosted Runner
This CD uses:
```yaml
runs-on: ubuntu-latest
```

### GitHub-Hosted Runner
- Managed by GitHub
- Clean VM every run
- No maintenance

### Self-Hosted Runner (not used here)

- Runs inside:
    - Your VM
    - Your VPC
    - Your K8s cluster

- Needed when:
    - Private cluster access
    - Internal networks
    - Cost optimization at scale

#### Why GitHub-Hosted is OK in this case?
- AKS API is publicly reachable and authentication is handled via Azure credentials.
- So no private networking needed.

## How CD is triggered
```yaml
on:
  workflow_run:
    workflows: ["CI - Quality, Security & Build"]
    types:
      - completed
```

### Why `workflow_run`?
It connects CD to CI, instead of triggering on git events.
- CI runs first
- CD listens to CI
- CD reacts only after CI finishes

### Why not `push`?
If you used: `on: push` then:
- CI and CD could run in parallel
- Deployment might happen even if CI fails 

### Why `types: completed`?
- Trigger CD when CI finishes
- Not when it starts

---

# Job Definition

```yaml
jobs:
  deploy:
    name: Deploy (AKS)
    if: ${{ github.event.workflow_run.conclusion == 'success' }}
    runs-on: ubuntu-latest
```

### Why the `if` condition?
- `completed` only means CI finished, not that it succeeded.
- The `if` condition ensures deployment runs only when CI succeeds.

#### What `github.event.workflow_run` actually is.
When CI finishes, GitHub sends an event payload to CD.

Inside that payload is an object called:   `github.event.workflow_run`

That object contains:
- Which workflow ran
- Its status
- Its conclusion
- Commit SHA
- Branch
- Actor
- etc.

### Mental model
- `on`: → *who can trigger me*
- `if`: → *should I actually run*

## Steps 3: Set AKS context
```yaml
      - name: Set AKS context
        uses: azure/aks-set-context@v3
        with:
          resource-group: ${{ env.AKS_RESOURCE_GROUP }}
          cluster-name: ${{ env.AKS_CLUSTER_NAME }}
```
- Configures `kubectl`
- Tells it **which cluster to talk to**

**Without this:**
- `kubectl apply` fails
- No kubeconfig is available

## Step 4: Apply Kubernetes manifests
```yaml
      - name: Apply Kubernetes manifests
        run: |
          kubectl apply -f k8s/deployment.yaml
          kubectl apply -f k8s/service.yaml
```
***Why?***
- Kubernetes is **declarative** ( we describe desired state )
- `apply` is **idempotent** ( safe to run multiple times )
- Ensures Deployment and Service exist and are updated

The manifest file pulls the latest image from dockerhub, so every time we deploy, the new image is used.

## Step 5: Verify rollout
```yaml
      - name: Verify rollout
        run: kubectl rollout status deployment/shorturl
```
- Waits until new pods are ready
- Ensures deployment actually succeeded
- Prevents CD from finishing early

## Step 6: Dummy DAST (Runtime Security Checks)
```yaml
      - name: Dummy DAST (Basic Runtime Security Checks)
        run: |
          IP=$(kubectl get svc shorturl-service \
            -o jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>/dev/null || true)

          if [ -z "$IP" ]; then
            echo "Service IP not available"
            exit 1
          fi

          curl -f http://$IP/api/health
          curl -I http://$IP | grep -i "content-type" || true
          curl -s http://$IP/../../etc/passwd | grep -i root && exit 1 || true
```

***Why DAST: Dynamic Application Security Testing?***
- SAST → code
- SCA → dependencies
- Image scan → container
- DAST → running application

This checks:
- App is reachable
- Basic misconfigurations
- Simple path traversal issues

Even though basic, it demonstrates **runtime security validation**.

### IP Extraction Command
```bash
IP=$(kubectl get svc shorturl-service \
  -o jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>/dev/null || true)
```

#### `kubectl get svc shorturl-service`
***What it does***
- Queries Kubernetes API
- Fetches the Service object named `shorturl-service`

*if:*
- Service exists → returns YAML/JSON
- Service does not exist → command fails

#### `-o jsonpath=...` — structured extraction
```bash
-o jsonpath='{.status.loadBalancer.ingress[0].ip}'
```
- Tells kubectl: “Don’t print the whole Service — give me only this field.”

This path means:
- `.status` → runtime status (not spec)
- `.loadBalancer` → LoadBalancer-related info
- `.ingress[0]` → first assigned ingress
- `.ip` → external IP address

So this extracts: `EXTERNAL_IP`. Nothing else.

#### `2>/dev/null` — suppress errors
***What it does***
- Redirects stderr (file descriptor 2)
- Sends errors to /dev/null (trash)

*Why needed:*
- Service may not exist yet
- IP may not be assigned yet
- kubectl prints noisy warnings

*We want:*
- Clean logs
- No scary red text

#### `|| true` — prevent failure

*What it does*
- If the kubectl command fails:
    - true runs
    - Overall command exits with status 0

*Why this matters:*
- GitHub Actions fails a step if a command exits non-zero
- We want to gracefully handle “IP not ready”

*So:*
- No IP → IP=""
- Script continues normally