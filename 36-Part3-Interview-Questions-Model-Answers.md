# Part 3 - DevOps, Containers And Cloud Ops: Interview Questions And Model Answers

Use this after files `31` through `35`. Practise aloud. The goal is to answer from first
principles, then name tools.

---

# 3.1 Docker

## Q1. Why use multi-stage Docker builds?

To separate build/test dependencies from runtime dependencies. The build stage can contain SDKs,
compilers and test tools; the final stage contains only the runtime artifacts. This reduces
image size, pull time, attack surface and vulnerability noise.

## Q2. How do you make Docker builds cache efficiently?

Copy stable dependency manifests first, restore/install dependencies, then copy frequently
changing source. Use `.dockerignore`, keep the build context small, use BuildKit cache mounts
where useful, and avoid invalidating expensive layers with every source change.

## Q3. Distroless, chiseled, Alpine or slim?

I choose the smallest supported runtime that the team can patch and operate. Distroless and
chiseled images reduce attack surface but make interactive debugging harder. Alpine is small
but can have musl compatibility issues. Slim images are often a practical default.

## Q4. What hardening do you expect for containers?

Run as non-root, disable privilege escalation, drop Linux capabilities, avoid privileged mode,
use read-only root filesystem where possible, mount only required writable paths, set
requests/limits, avoid secrets in images and enforce policies in Kubernetes.

## Q5. How do image scanning and signing fit together?

Scanning finds known vulnerabilities and misconfigurations. Signing or attestation proves image
origin/integrity and build provenance. They answer different questions. A signed vulnerable
image is still vulnerable, and a clean unsigned image is still weak for supply-chain assurance.

## Q6. Why deploy by digest instead of tag?

Tags are mutable. A digest identifies exact image content. For audit, rollback and incident
response, production should record or deploy immutable digests even if human-readable tags are
also used.

---

# 3.2 Kubernetes And AKS

## Q7. Explain Pod, Deployment, StatefulSet and DaemonSet.

A Pod is the smallest schedulable unit. A Deployment manages stateless replicated Pods and
rollouts. A StatefulSet manages Pods with stable identity and storage. A DaemonSet runs one Pod
per node or selected nodes, usually for agents.

## Q8. Requests vs limits?

Requests are used for scheduling and capacity planning. Limits cap runtime usage. CPU limit
causes throttling when exceeded; memory limit can cause OOMKilled. Every production workload
should have realistic requests. Limits should be set deliberately, especially CPU limits.

## Q9. What are Kubernetes QoS classes?

Guaranteed means requests equal limits for CPU and memory. Burstable means some requests or
limits exist but not all are equal. BestEffort has no requests/limits and is first to be
evicted under pressure.

## Q10. Taints/tolerations vs node affinity?

Taints repel Pods from nodes; tolerations allow Pods onto those nodes. Affinity attracts or
requires Pods to run on nodes with specific labels. For dedicated node pools, I often use both:
taint the pool and add toleration plus affinity to the intended workload.

## Q11. What does a PDB do?

A Pod Disruption Budget limits voluntary disruptions during node drains, upgrades and
maintenance. It protects availability only when there are enough replicas and schedulable
capacity. It does not save a single-replica app from downtime.

## Q12. HPA, VPA, KEDA and cluster autoscaler?

HPA changes pod replicas based on metrics. VPA recommends or changes resource requests. KEDA
scales based on event sources like queue length. Cluster autoscaler adds/removes nodes when
pods cannot schedule or nodes are underused. They solve different layers of scaling.

## Q13. System node pool vs user node pool?

System node pools host critical cluster pods such as CoreDNS and metrics-server. User node
pools host application workloads. Applications should not normally run on system pools, because
they can destabilize the cluster foundation.

## Q14. What is your AKS networking choice today?

For new AKS designs I would usually evaluate Azure CNI Overlay first because it scales better
with VNet IP space and avoids kubenet's legacy limitations. kubenet has an AKS retirement date
of March 31, 2028, so I would not choose it for a new long-lived design.

## Q15. How do Network Policies help?

They restrict pod ingress/egress and reduce lateral movement. By default, pod communication can
be broad. Network policies enforce service-to-service boundaries, namespace isolation and
zero-trust style cluster communication.

## Q16. NGINX ingress or AGIC?

NGINX is portable and flexible inside Kubernetes. AGIC integrates Azure Application Gateway and
WAF with AKS, which can fit Microsoft/government standards. I choose based on WAF placement,
private/public ingress, operational ownership, routing needs and platform standards.

## Q17. What is a private AKS cluster?

The API server endpoint is private, so management traffic must come through private network
paths. It improves control-plane exposure but requires private DNS, private CI/CD agents or
connectivity, firewall planning and a break-glass process.

## Q18. Workload Identity vs Kubernetes secrets?

Workload Identity federates a Kubernetes service account with Microsoft Entra ID so the Pod can
obtain Azure tokens without stored client secrets. I prefer it for Azure resource access. I use
Kubernetes secrets only when needed and protect them with RBAC, encryption and rotation.

## Q19. What is Key Vault CSI driver used for?

It mounts secrets, keys or certificates from Azure Key Vault into Pods. It is useful when apps
need file-based secrets or certificates and the organization wants centralized rotation and
Key Vault governance.

## Q20. How do you debug CrashLoopBackOff?

Check scope, describe the pod, read current and previous logs, inspect exit code, probes,
config, secrets, recent rollout, dependencies, resources and events. A common issue is a
liveness probe killing an app before it finishes startup.

## Q21. How do you debug OOMKilled?

Check the pod's last state, exit code 137, memory limit, usage trend, traffic/input size,
recent changes and node pressure. Fix by reducing memory use, streaming large data, right-sizing
requests/limits, scaling horizontally or moving batch work off the request path.

## Q22. How do you debug ImagePullBackOff?

Verify image name, tag/digest, registry existence, ACR permissions, managed identity/pull
secret, network path/private endpoint, registry firewall and platform architecture.

## Q23. What causes evictions?

Node pressure: memory, disk, PID, NotReady conditions or taints. I check node describe,
events, ephemeral storage, logs filling disk, QoS class, requests/limits and autoscaler
behavior.

## Q24. Should we add service mesh?

Only if we need mesh-level mTLS, traffic policy, retries and telemetry at scale and the
platform team can operate it. I would be honest if my experience is awareness/skills-only and
compare it with simpler controls like APIM, ingress, network policy and OpenTelemetry.

---

# 3.3 CI/CD

## Q25. What is your ideal CI/CD flow?

Build once, test, scan, generate SBOM, sign/attest, push immutable artifact, deploy to lower
environment, run smoke/integration tests, then promote the same artifact through approved
environments into production with recorded digest and approver.

## Q26. Azure DevOps environments and approvals?

Environments represent deployment targets and provide deployment history, permissions and
approvals/checks. In production, approvals should be attached to environments or protected
resources, not only embedded in YAML controlled by developers.

## Q27. Why use GitHub Actions OIDC to Azure?

OIDC avoids long-lived Azure secrets in GitHub. The workflow requests a short-lived OIDC token,
and Azure trusts it through a federated identity credential scoped to repo, branch, tag or
environment. It still needs least-privilege roles and protected environments.

## Q28. Rolling vs blue/green vs canary?

Rolling is simple and resource-efficient. Blue/green provides fast switchback with two
environments. Canary sends small production traffic first to reduce blast radius. The right
choice depends on risk, routing capability, observability and database compatibility.

## Q29. How do feature flags fit deployment?

Feature flags decouple deployment from release. I can deploy code safely and enable features
for selected users/tenants later. But flags need ownership, expiry, testing and permission
review or they become technical debt.

## Q30. What makes database migration hard in CI/CD?

Data persists and old/new app versions may run together during rollout. Use expand/contract:
add compatible schema, deploy compatible code, backfill idempotently, verify, then remove old
schema later. Rollback may be impossible after destructive schema changes, so fix-forward may
be safer.

## Q31. What scans belong in the pipeline?

Secret scanning, dependency scanning, SAST, IaC scan, container image scan, SBOM generation and
DAST against deployed test/staging environments. Each catches different risk.

---

# 3.4 IaC

## Q32. Why is Terraform state important?

State maps declared resources to real infrastructure and can contain sensitive values. In a
team it must be remote, encrypted, access-controlled and locked. Never commit state to Git or
edit it manually.

## Q33. What is state locking?

Locking prevents concurrent writes to the same state. Without it, two applies can corrupt state
or overwrite each other's changes. Force unlock only after confirming no legitimate run still
owns the lock.

## Q34. Terraform modules?

Modules package reusable infrastructure such as AKS, ACR, Key Vault or Log Analytics. Good
modules expose meaningful inputs, set secure defaults and avoid leaking secrets as outputs.
Over-abstracted modules can hide important Azure behavior.

## Q35. Workspaces or separate directories?

Workspaces can separate same-shaped environments, but they can hide active state and become
risky if environments differ. Separate directories/stacks are often clearer for production
review. The key is explicit state, clear approvals and consistent promotion.

## Q36. Why learn Bicep if you know Terraform?

Bicep is Azure-native and common in Microsoft-governed shops. It has Azure-focused tooling,
modules, what-if and deployment stacks. Terraform is strong for multi-cloud and provider-rich
environments. The organization standard matters more than personal preference.

## Q37. What is Azure Policy used for?

Azure Policy enforces or audits organizational standards at scale: allowed regions, required
tags, diagnostic settings, private endpoint requirements, encryption, AKS pod security and
approved SKUs. Use audit before deny for broad rollout.

## Q38. What belongs in an Azure Landing Zone?

Management groups, subscriptions, identity/RBAC, networking, security baseline, Azure Policy,
logging, naming, tagging, shared services and cost governance. It is not only network design.

---

# 3.5 Observability

## Q39. Logs vs metrics vs traces?

Logs are event records, metrics are numeric time-series, and traces show a request path across
services. Production observability needs all three correlated with context propagation.

## Q40. What is OpenTelemetry?

OpenTelemetry is a vendor-neutral standard/toolkit for collecting telemetry: traces, metrics,
logs and context. It helps instrument Python, .NET and Node consistently and export to systems
such as Azure Monitor/Application Insights.

## Q41. What is context propagation?

It carries trace/correlation context across HTTP calls, queues and background jobs. Without it,
traces break between services and incidents become much harder to investigate.

## Q42. Why does high-cardinality telemetry hurt?

Labels like raw user ID, request ID or full URL can create huge numbers of unique metric series.
That increases cost and can slow queries/alerts. Put high-cardinality values in logs/traces,
not metric labels unless deliberately controlled.

## Q43. What is KQL used for?

KQL queries Azure Monitor/Log Analytics data. I use it to investigate errors, latency,
dependency failures, pod restarts, deployment impact and cost/usage signals.

## Q44. SLI, SLO and SLA?

SLI is the measurement, such as availability or p95 latency. SLO is the internal target. SLA is
the external commitment. Error budget is the allowed miss against the SLO.

## Q45. What makes an alert good?

It is actionable, owned, tied to user impact, severity-based, deduplicated and linked to a
runbook. CPU-only alerts can be useful supporting signals, but user-impact SLIs should drive
page-level alerts.

## Q46. What should a runbook contain?

Alert meaning, user impact, dashboard links, KQL queries, triage commands, safe mitigations,
rollback/fix-forward guidance, escalation path, communication template and post-incident
checklist.

## Q47. How do you approach FinOps?

Treat cost as engineering telemetry. Use tags and allocation to identify owners, budgets and
alerts for surprises, rightsizing for waste, log-ingestion controls and SLO-aware decisions so
cost savings do not damage reliability.

