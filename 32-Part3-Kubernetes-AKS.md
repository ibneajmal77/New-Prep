# Part 3.2 - Kubernetes And AKS

*Two layers: **Part A** is the build narrative. **Part B** is the complete reference. **Part C**
is the live-debug interview flow.*

---

# Part A - THE BUILD: Running The Platform On AKS

## Step 1. The image needs an orchestrator

Docker gives us a runnable image. Kubernetes gives us scheduling, scaling, service discovery,
rollouts, storage, configuration, security policy and operational control.

The platform runs on AKS because the organization is Azure-heavy and needs managed control
plane operations, Entra integration, managed identity, Azure Monitor, Azure Policy, Key Vault
integration and private networking.

> Reference: [3.2.1 Core Kubernetes objects](#321-core-kubernetes-objects)

## Step 2. YAML is capacity planning

The first AKS incident is self-inflicted: a pod has no memory limit, consumes a node, and
causes evictions. Kubernetes scheduling depends on resource requests, limits, node constraints,
disruption budgets and topology rules.

> Reference: [3.2.2 Scheduling](#322-scheduling)

## Step 3. Scaling happens at multiple layers

The portal API has traffic peaks around HR deadlines. We use HPA for pod count, KEDA for queue
and event-driven scale, VPA carefully for right-sizing, and cluster autoscaler/node
autoprovisioning for nodes.

> Reference: [3.2.3 Autoscaling](#323-autoscaling)

## Step 4. Networking decides whether the design can grow

AKS networking is not a footnote. It affects IP planning, private access, ingress, network
policy, on-prem connectivity, ExpressRoute and security review. For new designs, Azure CNI
Overlay is often the right default; kubenet is legacy and has a retirement timeline.

> Reference: [3.2.4 Networking](#324-networking)

## Step 5. Azure identity replaces static secrets

The service needs Key Vault, Storage and database access. Avoid long-lived credentials in
Kubernetes secrets when possible. Use AKS managed identity for the cluster and Workload
Identity for pods, with Key Vault CSI where secrets/certs must be mounted.

> Reference: [3.2.5 AKS-specific platform features](#325-aks-specific-platform-features)

## Step 6. Security must be enforced before admission

Security cannot rely on developers remembering every YAML control. Use Pod Security Admission,
policy/admission controllers, image policies, secrets controls and namespace standards.

> Reference: [3.2.7 Security](#327-security)

## Step 7. GitOps keeps desired state honest

Helm packages the platform. Kustomize overlays environment differences. Argo CD or Flux
reconciles the desired state from Git and detects drift. Secrets in Git require encryption
strategy, not plain YAML.

> Reference: [3.2.8 Helm, Kustomize and GitOps](#328-helm-kustomize-and-gitops)

## Step 8. Debugging is expected live

The panel may ask: "A pod is CrashLoopBackOff. Walk us through it." You need a calm `kubectl`
flow: inspect, describe, logs, events, probes, image, resources, config, dependencies, nodes.

> Reference: [3.2.9 Debugging AKS](#329-debugging-aks)

---

# Part B - THE REFERENCE

## 3.2.1 Core Kubernetes Objects

### Pod

A Pod is the smallest schedulable unit. It contains one or more containers sharing network
namespace and volumes.

Use cases:

- one app container,
- sidecar container for proxy/logging where justified,
- init container for startup preparation.

Pods are usually not managed directly in production; Deployments, StatefulSets, Jobs or
DaemonSets create them.

### Deployment

A Deployment manages stateless replicated Pods through ReplicaSets.

Use for:

- APIs,
- web frontends,
- stateless workers,
- integration adapters.

It supports rolling updates, rollback and replica management.

Key fields:

- `replicas`,
- `selector`,
- Pod template,
- rollout strategy,
- readiness/liveness/startup probes,
- resource requests/limits.

### StatefulSet

StatefulSet manages Pods that need stable identity and stable storage.

Use for:

- databases only when you are intentionally self-operating them,
- brokers or stateful middleware where managed services are not used,
- apps requiring stable network identity.

Properties:

- stable pod names,
- ordered startup/shutdown,
- volumeClaimTemplates,
- stable persistent volume association.

Senior answer: on AKS, prefer managed Azure services for databases unless there is a strong
reason to self-host stateful systems in Kubernetes.

### DaemonSet

DaemonSet runs one Pod per node or selected nodes.

Use for:

- log agents,
- monitoring agents,
- node-level networking/security agents,
- storage drivers.

### Job And CronJob

Job runs a task to completion:

- migration check,
- one-time import,
- batch reconciliation.

CronJob runs Jobs on a schedule:

- nightly cleanup,
- daily SFTP import,
- report generation.

Controls:

- concurrency policy,
- backoff limit,
- starting deadline,
- history limits,
- idempotency.

### Service

Service provides stable networking for Pods.

Types:

- `ClusterIP`: internal cluster access.
- `NodePort`: exposes on node ports; usually not preferred directly.
- `LoadBalancer`: creates cloud load balancer.
- `ExternalName`: DNS alias.

### Ingress

Ingress routes HTTP/HTTPS traffic into services. It requires an ingress controller.

Common AKS options:

- NGINX Ingress Controller,
- Application Gateway Ingress Controller (AGIC),
- Gateway API implementations,
- service mesh ingress gateways where adopted.

Ingress design includes TLS, host/path routing, WAF placement, private/public exposure and
identity integration.

### ConfigMap

ConfigMap stores non-secret configuration:

- feature flags,
- endpoint names,
- log levels,
- non-sensitive settings.

ConfigMaps are not a substitute for typed application configuration validation.

### Secret

Kubernetes Secret stores sensitive values, but by default it is not the same as an enterprise
secret vault. Treat it carefully:

- enable encryption at rest where supported,
- restrict RBAC,
- prefer external secret management where possible,
- avoid printing secrets into logs,
- rotate secrets.

On AKS, prefer Workload Identity and Key Vault integration when feasible.

## 3.2.2 Scheduling

### Requests And Limits

Requests tell Kubernetes what resources a Pod needs for scheduling. Limits cap usage.

```yaml
resources:
  requests:
    cpu: "250m"
    memory: "256Mi"
  limits:
    cpu: "1"
    memory: "512Mi"
```

CPU:

- request influences scheduling,
- limit throttles CPU usage.

Memory:

- request influences scheduling,
- exceeding limit can cause OOMKilled.

Senior answer: set requests for every workload. Set memory limits carefully. CPU limits can
cause throttling; use them deliberately.

### QoS Classes

Kubernetes assigns QoS based on requests/limits:

- **Guaranteed:** every container has CPU/memory request equal to limit.
- **Burstable:** at least one request/limit, but not all equal.
- **BestEffort:** no requests/limits.

During resource pressure, BestEffort pods are most likely to be evicted, then Burstable, then
Guaranteed.

### Node Affinity

Node affinity influences where Pods run based on node labels.

Use for:

- scheduling workloads onto user node pools,
- separating GPU/CPU workloads,
- placing Windows/Linux workloads,
- compliance-specific node pools.

Prefer:

- required rules only when placement must happen,
- preferred rules when placement is desirable but not mandatory.

### Taints And Tolerations

Taints repel Pods from nodes. Tolerations allow Pods to schedule onto tainted nodes.

Use cases:

- system node pool reserved for system pods,
- GPU node pool only for GPU workloads,
- spot node pool only for interruptible workloads,
- dedicated high-security workload pool.

Remember: toleration allows scheduling; it does not force scheduling. Combine with affinity
when needed.

### Pod Disruption Budgets

PDBs limit voluntary disruptions during upgrades, drains and maintenance.

```yaml
apiVersion: policy/v1
kind: PodDisruptionBudget
spec:
  minAvailable: 2
  selector:
    matchLabels:
      app: portal-api
```

Use with multiple replicas and topology spread. A PDB cannot save a single-replica workload
from downtime during node drain.

### Topology Spread

Topology spread constraints distribute Pods across zones, nodes or other topology domains.

Use for:

- avoiding all replicas on one node,
- zone resilience,
- reducing correlated failures.

Example domains:

- `kubernetes.io/hostname`,
- `topology.kubernetes.io/zone`.

## 3.2.3 Autoscaling

### HPA

Horizontal Pod Autoscaler changes replica count based on metrics.

Common metrics:

- CPU,
- memory,
- custom metrics,
- external metrics.

Requirements:

- resource requests for CPU-based scaling,
- metrics pipeline,
- realistic min/max replicas,
- scale-up/down behavior tuned to workload.

HPA does not help if:

- pods cannot start due to missing nodes,
- application has internal bottlenecks,
- database is saturated,
- requests lack useful metrics.

### VPA

Vertical Pod Autoscaler recommends or changes resource requests/limits.

Use cases:

- right-sizing services,
- learning realistic resource needs,
- non-HPA workloads.

Be cautious with automatic mode for latency-sensitive workloads because changing resources can
restart pods. HPA and VPA can conflict if both modify CPU/memory behavior without planning.

### KEDA

KEDA scales workloads based on events:

- queue length,
- Kafka/Event Hub lag,
- Service Bus messages,
- Prometheus metrics,
- cron triggers.

Best for:

- background workers,
- event-driven imports,
- async processing.

KEDA can scale to zero where supported, but cold-start and dependency readiness must be
acceptable.

### Cluster Autoscaler

Cluster autoscaler changes node count when Pods cannot schedule due to insufficient resources
or nodes are underused.

It reacts to pending Pods; it does not know business intent. Pod requests must be accurate.

### AKS Node Pools

System node pools:

- host critical system pods such as CoreDNS and metrics-server,
- should not run normal applications,
- at least one required.

User node pools:

- host application workloads,
- can be separated by OS, VM size, workload, compliance or cost.

Spot node pools:

- cheaper interruptible capacity,
- suitable for retryable workers and non-critical workloads,
- need taints/tolerations and graceful interruption handling,
- not for critical system components.

### AKS Automatic

AKS Automatic provides stronger managed defaults for cluster operations: managed system node
pools, node provisioning, autoscaling features, automatic cluster upgrades and node image
updates. It reduces operational burden but gives less direct control than AKS Standard.

Interview answer:

"For a team that wants sane managed defaults and does not need deep cluster customization, AKS
Automatic can be attractive. For regulated or highly customized networking/runtime designs, I
would compare AKS Standard because it exposes more direct control."

## 3.2.4 Networking

### kubenet vs Azure CNI

Current AKS guidance treats kubenet as legacy. Microsoft has announced kubenet retirement for
AKS on **March 31, 2028**. For new designs, discuss Azure CNI options first.

| Model | How Pod IPs work | Use today |
|---|---|---|
| kubenet | Pods get IPs from a separate logical range and use route tables | legacy; migrate before retirement |
| Azure CNI node subnet | Pods receive VNet IPs from node subnet | useful when direct VNet pod addressing is required and IP space is available |
| Azure CNI Overlay | Nodes get VNet IPs; Pods get overlay CIDR IPs | recommended for many new AKS clusters, especially when VNet IP space is limited |
| Azure CNI powered by Cilium | Cilium data plane with Azure CNI modes | useful for advanced networking/security/performance scenarios |

### Azure CNI Overlay

Benefits:

- better IP scalability than legacy kubenet,
- avoids assigning VNet IP to every Pod,
- simpler route management,
- strong fit when VNet IP space is constrained,
- supports network policy engines depending on configuration.

Planning:

- pod CIDR must not overlap with VNet, peered networks, VPN or ExpressRoute ranges,
- service CIDR must not overlap,
- node subnets need room for node growth,
- max pods per node affects pod CIDR sizing.

### Network Policies

By default, Pods can often communicate broadly unless network policy is enforced. Network
policies define allowed ingress/egress.

Use to:

- restrict service-to-service traffic,
- isolate namespaces,
- prevent lateral movement,
- protect databases/internal services,
- enforce zero-trust style cluster networking.

Policy engines:

- Cilium,
- Calico,
- Azure network policy options, noting retirement/migration guidance for older Azure NPM on
  Linux.

### Ingress Controllers

| Option | Best fit | Notes |
|---|---|---|
| NGINX Ingress | flexible Kubernetes-native ingress | common, portable, needs operation/tuning |
| AGIC | Azure Application Gateway integration | useful when Application Gateway/WAF is standard |
| Gateway API | newer Kubernetes API for traffic routing | increasingly important; know concepts |
| Service mesh gateway | mesh-managed ingress | only when mesh is already justified |

Design checks:

- TLS termination,
- certificate management,
- WAF placement,
- internal vs public ingress,
- path/host routing,
- request size/timeouts,
- private DNS,
- health probes,
- source IP preservation requirements.

### Private Clusters

Private AKS clusters keep the API server endpoint private.

Use when:

- control plane access must stay on private networks,
- organization uses hub/spoke and private connectivity,
- regulatory requirements restrict public endpoints.

Operational needs:

- private DNS,
- jump host or private runner/agent,
- connectivity from CI/CD,
- firewall/egress planning,
- break-glass process,
- monitoring access.

## 3.2.5 AKS-Specific Platform Features

### Managed Identity

AKS uses managed identities for cluster resource operations. Prefer managed identities over
service principal secrets where possible.

Use:

- cluster identity for Azure resource operations,
- kubelet identity for pulling from ACR,
- workload identity for Pods accessing Azure resources.

### Workload Identity

Microsoft Entra Workload ID lets a Kubernetes service account federate with Microsoft Entra ID.
The pod receives a projected service-account token, Entra validates it through OIDC federation,
and the workload obtains Azure tokens without storing client secrets.

Use for:

- Key Vault access,
- Storage access,
- Azure SQL with Entra auth,
- Service Bus/Event Hubs access,
- calling Azure APIs.

Current point: Workload Identity replaces the older pod-managed identity approach.

### Azure Key Vault CSI Driver

The Secrets Store CSI driver with Azure provider can mount secrets, keys and certificates from
Key Vault into Pods.

Use when:

- app needs certificate files,
- app cannot call Key Vault SDK directly,
- secrets need centralized rotation,
- Kubernetes secrets should be minimized.

Design points:

- authenticate with Workload Identity,
- use least-privilege Key Vault RBAC,
- understand rotation behavior,
- avoid logging mounted secret values,
- decide whether to sync into Kubernetes Secrets only if required.

### Entra RBAC Integration

AKS can integrate with Microsoft Entra ID for cluster authentication and authorization.

Design:

- Entra groups for human access,
- Azure RBAC/Kubernetes RBAC mapped deliberately,
- no shared kubeconfigs with admin credentials,
- just-in-time privileged access where possible,
- separate dev/test/prod cluster roles.

### Azure Policy For AKS

Azure Policy can audit or deny Kubernetes/AKS configurations:

- disallow privileged containers,
- require resource limits,
- restrict hostPath,
- require approved registries,
- enforce labels,
- require network policy,
- enforce Pod Security baseline/restricted standards.

Use audit first, then deny after measuring impact.

### Container Insights

Container Insights collects cluster/container telemetry into Azure Monitor/Log Analytics.

Use for:

- pod/container logs,
- node health,
- Kubernetes events,
- controller status,
- resource usage,
- troubleshooting.

Control cost through data collection rules, namespace filtering and retention strategy.

### Node Image And Cluster Upgrades

You must keep both Kubernetes versions and node OS images current.

Upgrade strategy:

- track AKS support window,
- review deprecated API usage,
- test in non-prod,
- confirm PDBs and probes,
- use maintenance windows,
- upgrade control plane and node pools safely,
- monitor after upgrade,
- have rollback/mitigation plan.

AKS provides automatic upgrade channels and node image upgrade channels. AKS Automatic
preconfigures more of this; AKS Standard requires more explicit decisions.

## 3.2.6 Storage

### PV And PVC

PersistentVolume is storage in the cluster. PersistentVolumeClaim is a workload's request for
storage.

Typical flow:

```text
StorageClass -> PVC -> dynamically provisioned PV -> mounted into Pod
```

### Azure Disk vs Azure Files

| Storage | Best fit | Notes |
|---|---|---|
| Azure Disk | single-node mounted block storage | good for stateful workloads needing disk semantics |
| Azure Files | shared file storage | supports multi-pod shared mounts; higher latency than local/block-style storage |

Use managed databases/storage services when possible. Running databases on AKS requires backup,
restore, upgrades, performance and failover discipline.

### StatefulSet Volumes

StatefulSets use `volumeClaimTemplates` to give each Pod stable storage.

Risks:

- pod replacement keeps volume,
- data migration is harder,
- backups must be explicit,
- zone/node constraints matter,
- storage class reclaim policy matters.

## 3.2.7 Security

### Pod Security Admission

Pod Security Admission enforces Pod Security Standards at namespace level:

- privileged,
- baseline,
- restricted.

Use labels to enforce/warn/audit standards per namespace. Start with audit/warn, then enforce
after workload fixes.

### Admission Controllers

Admission controllers intercept requests to the Kubernetes API before persistence. They can
validate or mutate objects.

Use for:

- requiring labels,
- blocking privileged pods,
- enforcing image registries,
- injecting sidecars,
- validating resource requests,
- policy enforcement.

### OPA/Gatekeeper And Kyverno

OPA/Gatekeeper:

- policy as Rego,
- strong for expressive policies,
- steeper learning curve.

Kyverno:

- Kubernetes-native YAML policy style,
- validate/mutate/generate/verify images,
- often easier for platform teams.

Choose based on team skill, policy complexity and ecosystem fit.

### Secrets Management

Do:

- prefer Workload Identity over stored secrets,
- use Key Vault for real secret storage,
- restrict Kubernetes Secret RBAC,
- encrypt secrets at rest,
- rotate,
- avoid env-var secrets for highly sensitive values when mounted files or SDK calls are safer,
- never put secrets in Git.

### Image Pull Policy

Common values:

- `IfNotPresent`: default for non-`:latest` tags; avoids pulling every time.
- `Always`: useful when tags are mutable, but production should avoid mutable tags.
- `Never`: local-only/testing cases.

Production:

- use immutable digests,
- define allowed registries,
- use image scanning/signing policies,
- grant `AcrPull` with managed identity.

## 3.2.8 Helm, Kustomize And GitOps

### Helm

Helm packages Kubernetes resources into charts.

Use for:

- reusable deployments,
- third-party packages,
- templated app releases,
- versioned chart releases.

Risks:

- over-templating,
- values sprawl,
- secret leakage in values files,
- hard-to-review rendered manifests.

### Kustomize

Kustomize overlays patches on base manifests without templates.

Use for:

- environment overlays,
- small configuration differences,
- simple manifest customization.

Example:

```text
base/
  deployment.yaml
overlays/dev/
  kustomization.yaml
overlays/prod/
  kustomization.yaml
```

### Helm vs Kustomize

| Need | Better fit |
|---|---|
| package reusable app with parameters | Helm |
| maintain environment overlays for owned manifests | Kustomize |
| install third-party platform components | Helm |
| simple patching without templating | Kustomize |
| Helm chart with per-env patches | Helm + Kustomize can be combined carefully |

### GitOps With Argo CD Or Flux

GitOps means Git is the desired state. A controller reconciles cluster state toward Git.

Benefits:

- drift detection,
- audit trail,
- pull-based deployment,
- declarative rollback,
- consistent promotion flow.

Core loop:

```text
Git desired state -> GitOps controller -> Kubernetes API -> observe drift -> reconcile
```

### Secrets In Git

Never commit plaintext secrets.

Options:

- SOPS with Key Vault/KMS-backed encryption,
- Sealed Secrets,
- External Secrets Operator,
- Key Vault CSI,
- secret references rather than secret values.

Interview answer:

"GitOps does not mean all secrets are plain YAML in Git. The desired state can include encrypted
secrets or references to a real secret manager."

## 3.2.9 Debugging AKS

### General Triage Flow

```text
1. kubectl get pods -n <ns> -o wide
2. kubectl describe pod <pod> -n <ns>
3. kubectl logs <pod> -n <ns> --previous
4. kubectl get events -n <ns> --sort-by=.lastTimestamp
5. check probes, env/config, secrets, image, resources
6. check service/endpoints/ingress if traffic issue
7. check node pressure and scheduling if pending/evicted
8. check recent rollout and ReplicaSet history
9. correlate in Azure Monitor/Container Insights
```

### CrashLoopBackOff

Meaning: container starts, exits, Kubernetes restarts it with backoff.

Check:

- current logs,
- previous logs,
- exit code,
- command/args,
- missing config/secrets,
- app startup error,
- failed database connection,
- liveness probe killing app too early,
- dependency timeout,
- recent image/config change.

Commands:

```text
kubectl logs pod-name -n ns --previous
kubectl describe pod pod-name -n ns
kubectl rollout history deployment/app -n ns
```

### OOMKilled

Meaning: container exceeded memory limit or node memory pressure killed it.

Check:

- `Last State`,
- exit code 137,
- memory limit,
- memory usage trend,
- traffic spike,
- memory leak,
- large payload/import,
- VPA recommendations.

Fix:

- reduce memory use,
- stream large files,
- right-size requests/limits,
- scale horizontally if workload supports it,
- move batch work off request path.

### ImagePullBackOff

Meaning: node cannot pull image.

Check:

- image name/tag/digest,
- ACR permissions,
- image exists,
- pull secret/managed identity,
- network path/private endpoint,
- registry firewall,
- rate limits,
- architecture mismatch.

### Evictions

Pods can be evicted because of node pressure:

- memory pressure,
- disk pressure,
- PID pressure,
- node not ready,
- taints.

Check:

- node describe,
- kubelet events,
- requests/limits,
- ephemeral storage,
- log growth,
- BestEffort pods,
- cluster autoscaler behavior.

### Pending Pods

Causes:

- insufficient CPU/memory,
- unsatisfied affinity,
- missing toleration,
- PVC not bound,
- quota limit,
- PDB/rollout constraints,
- max pods per node,
- autoscaler unable to add node.

### Service/Ingress Not Working

Check:

- Service selector matches Pod labels,
- endpoints exist,
- Pod readiness,
- Ingress class,
- TLS secret,
- backend service port,
- health probe path,
- NetworkPolicy,
- DNS,
- Application Gateway/NGINX events,
- private/public IP routing.

## 3.2.10 Service Mesh Awareness

Be honest if your experience is skills-only. Good phrasing:

"I understand where a service mesh fits, but I would not claim deep production ownership unless
I had operated it. Istio or Linkerd can provide mTLS, traffic policy, retries, observability
and canary controls, but they add complexity. I would first ask whether the platform actually
needs mesh-level controls beyond what ingress, APIM, network policy, OpenTelemetry and app
libraries already provide."

Use service mesh when:

- service-to-service mTLS is required,
- traffic splitting/retries need central policy,
- large microservice estate needs consistent telemetry,
- platform team can operate it.

Avoid when:

- small service count,
- team lacks mesh operations experience,
- debugging complexity outweighs benefits,
- simpler controls satisfy requirements.

---

# Part C - Live Debug Flow

## "The Pod Is CrashLoopBackOff. What Do You Do?"

Answer:

1. Identify scope: one pod, one deployment, one namespace or cluster-wide?
2. Run `kubectl describe pod` to inspect events, exit codes, probes and mounts.
3. Run `kubectl logs --previous` because the current container may already have restarted.
4. Check recent rollout: image digest, config, secrets, Helm values, GitOps sync.
5. Check startup dependencies: database, Key Vault, service endpoints, DNS.
6. Check liveness/startup probe timing; a liveness probe can kill a slow-starting app.
7. Check resource limits and OOMKilled state.
8. Roll back or fix forward depending on blast radius and change-control rules.
9. Add regression prevention: startup probe, config validation, better health check, pipeline
   smoke test.

## "The Deployment Is Healthy But Users Get 502."

Answer:

1. Check Ingress/Application Gateway/NGINX health.
2. Verify Service selector and endpoints.
3. Verify Pod readiness, not only running state.
4. Check target port vs service port.
5. Check NetworkPolicy.
6. Check TLS/cert and host/path routing.
7. Check backend app logs with correlation IDs.
8. Check recent config or DNS changes.

## "AKS Upgrade Caused Downtime. Why?"

Likely causes:

- single replica workloads,
- missing PDBs,
- readiness probes incorrect,
- pods cannot reschedule due to requests/affinity/PVC,
- node pool capacity too small,
- deprecated APIs,
- disruption budget too strict or too loose,
- app not graceful on SIGTERM,
- no maintenance-window testing in non-prod.

---

# Part D - Interview Traps

## Trap 1. "Kubernetes will scale it automatically."

Better answer: Kubernetes can scale if HPA/KEDA/VPA/cluster autoscaler are configured and
metrics/requests are accurate. It cannot fix database saturation, bad app concurrency or
incorrect resource requests.

## Trap 2. "A Pod is running, so the app is healthy."

Better answer: running only means the container process exists. Readiness, liveness, startup
probes, service endpoints and real user checks tell whether it can serve traffic.

## Trap 3. "Use kubenet because it is simple."

Better answer: kubenet is legacy in AKS and has a retirement timeline. For new clusters, I
would look at Azure CNI Overlay or another supported Azure CNI mode based on IP planning,
security and connectivity needs.

## Trap 4. "Kubernetes Secrets are enough."

Better answer: Kubernetes Secrets need RBAC, encryption and rotation. In Azure, I prefer
Workload Identity and Key Vault integration so workloads do not carry long-lived cloud
credentials.

## Trap 5. "Service mesh should be added for microservices."

Better answer: mesh adds value for mTLS, traffic policy and uniform telemetry at scale, but it
also adds operational complexity. I would add it only when simpler controls are insufficient
and the platform team can operate it.

