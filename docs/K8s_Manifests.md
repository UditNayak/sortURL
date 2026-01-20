# Kubernetes Deployment

A Deployment is a higher-level Kubernetes object used to **manage Pods reliably over time**.

It ensures the application is running, updated safely, and recovered automatically if something fails.

## Pod vs ReplicaSet vs Deployment

### Pod
- The smallest deployable unit in Kubernetes.
- Runs one or more containers
- Has no self-healing guarantees
- No scaling
- No updates

***Used for***: experiments, one-off jobs

### ReplicaSet
- Ensures N identical Pods are running
- Self-healing: replaces failed Pods
- Scaling: can increase/decrease replicas
- No updates: requires manual Pod template changes

***Used for***: internal mechanism (rarely created directly)

### Deployment
- Manages ReplicaSets
- Handles rolling updates
- Supports rollback

## Resource Management
```yaml
          resources:
            requests:
              cpu: "100m"
              memory: "256Mi"
            limits:
              cpu: "250m"
              memory: "512Mi"
```
***Why resource requests***
- Used by Kubernetes scheduler
- Ensures node has enough capacity
- Guarantees minimum resources

***Why resource limits***
- Prevents a Pod from consuming too much
- Protects other workloads
- Prevents node crashes

***What happens if limits are exceeded?***
- CPU → throttled
- Memory → Pod killed

## Readiness Probe
```yaml
          readinessProbe:
            httpGet:
              path: /api/health
              port: 8001
            initialDelaySeconds: 5
            periodSeconds: 10
```
***What is readiness?***

> “Is the app ready to receive traffic?”

**Why it exists**
- Prevents traffic to unready Pods
- Used by Services and LoadBalancers

**If readiness fails:**
- Pod stays running
- Traffic is stopped

**Why /api/health?**
- Lightweight
- Fast
- Designed for health checks

## Liveness Probe
```yaml
            httpGet:
              path: /api/health
              port: 8001
            initialDelaySeconds: 15
            periodSeconds: 20
```

***What is liveness?***
> “Is the app still alive?”

***Why it exists***
- Detects deadlocks or hung apps
- Automatically restarts the Pod

***If liveness fails:***
- Pod is killed
- New Pod is created

### Readiness vs Liveness
| Probe     | Purpose             | Action       |
| --------- | ------------------- | ------------ |
| Readiness | Can I send traffic? | Stop traffic |
| Liveness  | Is app healthy?     | Restart Pod  |

### Why are delays different?
```
readiness initialDelaySeconds: 5
liveness initialDelaySeconds: 15
```
- App may be slow to fully stabilize
- Avoids premature restarts
- Readiness first, liveness later

### What is `periodSeconds`?
- How often to check the probe
- Too low → overhead
- Too high → slow failure detection

---

# Kubernetes Service

```yaml
apiVersion: v1
kind: Service
metadata:
  name: shorturl-service
spec:
  type: LoadBalancer
  selector:
    app: shorturl
  ports:
    - port: 80
      targetPort: 8001
```

## Why do we need a Service at all?

#### The core problem

***Pods are ephemeral:***
- Pods can die
- Pods can be recreated
- Pod IPs change frequently

#### What a Service solves
> A Service provides a stable network identity for a set of Pods.

It gives:
- Stable DNS name
- Stable virtual IP
- Automatic load balancing across Pods

So the flow becomes:
```
Client → Service → Pod(s)
```

## How does the Service know which Pods to send traffic to?
```yaml
selector:
  app: shorturl
```
***Why this exists***
- Service selects Pods using labels
- It matches:
```yaml
labels:
  app: shorturl
```
in your  `deployment.yaml`.

## Ports explained
```yaml
  ports:
    - port: 80
      targetPort: 8001
```

#### `targetPort`
- Port inside the container
- Your app listens on 8001

#### `port`
- Port exposed by the Service
- Clients talk to port 80

## Why `type: LoadBalancer`?
> Kubernetes asks the cloud provider (Azure) to create a cloud load balancer.

***In AKS:***
- Azure creates an external Load Balancer
- Assigns a public IP
- Routes traffic to your Service

## Why not ClusterIP?

***What ClusterIP does***
- Exposes the Service inside the cluster only
- No external access

Used when:
- Internal microservices
- Backend-only components

***Why not suitable here?***

- You want to access the app from:

  - Browser
  - curl

## Why not NodePort?

#### What NodePort does
- Exposes service on a port like 30000–32767
- Accessible via: `<NodeIP>:NodePort`

#### Problems with NodePort
- Exposes every node
- Random high ports
- Less secure
- Not cloud-native

#### When NodePort is used
- Local clusters
- Learning
- Debugging

#### Why not used here?
- AKS provides proper LoadBalancer
- LoadBalancer is cleaner and safer

### LoadBalancer vs NodePort vs ClusterIP
| Type         | Scope            | Use case       |
| ------------ | ---------------- | -------------- |
| ClusterIP    | Internal only    | Microservices  |
| NodePort     | External (basic) | Dev / learning |
| LoadBalancer | External (cloud) | Production     |

