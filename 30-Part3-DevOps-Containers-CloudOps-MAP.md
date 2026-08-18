# Part 3 - DevOps, Containers And Cloud Ops: The Map

*Read this first. It is the index, the architecture, and the study order for files 31-35.
Use file 36 after the reference files to practise spoken interview answers.*

---

## 1. How This Material Is Organised

Seven files. **File order = learning order**, while your original section numbers stay inside
the files.

| File | Section | What it adds to the platform |
|---|---|---|
| `31-Part3-Docker.md` | 3.1 | Secure, small, repeatable container images |
| `32-Part3-Kubernetes-AKS.md` | 3.2 | AKS runtime, scheduling, networking, scaling, security and debugging |
| `33-Part3-CICD.md` | 3.3 | Pipelines, gates, deployment strategies and supply-chain controls |
| `34-Part3-IaC.md` | 3.4 | Terraform, Bicep, landing zones, policy and drift control |
| `35-Part3-Observability.md` | 3.5 | OpenTelemetry, Azure Monitor, KQL, SLOs and FinOps |
| `36-Part3-Interview-Questions-Model-Answers.md` | Drill | Panel questions and spoken model answers |

Every reference file uses the same pattern:

1. **Part A - The Build:** one production deployment story.
2. **Part B - The Reference:** complete topic coverage.
3. **Part C - Interview Traps:** senior-level questions and wrong turns to avoid.

---

## 2. The System Being Operated

We are operating the same bilingual government employee-services platform from Part 1:

- React/Next.js frontend.
- Python, .NET and Node.js services.
- SQL Server, PostgreSQL, Redis and queues.
- Integrations with Entra ID, APIM, Key Vault, legacy systems and future AI services.
- AKS as the main container runtime.
- Azure DevOps or GitHub Actions as CI/CD.
- Terraform/Bicep for infrastructure.
- Azure Monitor, Application Insights, Log Analytics and KQL for operations.

The platform must support secure releases, government change windows, auditability,
least-privilege access, private networking, rollback, cost control and incident response.

---

## 3. Master Architecture

```text
                         SOURCE CONTROL
           app code, Dockerfiles, Helm/Kustomize, IaC, policies
                                  |
                                  v
+----------------------------- CI PIPELINE -----------------------------+
| build -> unit tests -> SAST/dependency scan -> container build         |
| multi-stage Docker, SBOM, image scan, signing/attestation              |
+----------------------------------+------------------------------------+
                                   |
                                   v
+--------------------------- ARTIFACT LAYER ----------------------------+
| Azure Container Registry, immutable digests, retention, quarantine     |
| provenance, Cosign/Notary transition awareness, registry hygiene       |
+----------------------------------+------------------------------------+
                                   |
                                   v
+--------------------------- CD / GITOPS LAYER -------------------------+
| Azure DevOps/GitHub environments, approvals, gates, change windows     |
| Argo CD/Flux reconciliation, Helm/Kustomize, SOPS/Sealed Secrets       |
+----------------------------------+------------------------------------+
                                   |
                                   v
+----------------------------- AKS RUNTIME -----------------------------+
| private cluster, Azure CNI Overlay, ingress, network policies          |
| system/user node pools, HPA/VPA/KEDA/cluster autoscaler, PDBs          |
| Workload Identity, Key Vault CSI, policy/admission, pod security       |
+----------------------------------+------------------------------------+
                                   |
                                   v
+------------------------ PLATFORM / LANDING ZONE ----------------------+
| management groups, subscriptions, naming, tagging, Azure Policy        |
| hub/spoke networking, private endpoints, managed identities, budgets   |
+----------------------------------+------------------------------------+
                                   |
                                   v
+----------------------------- OBSERVABILITY ---------------------------+
| OpenTelemetry traces/metrics/logs, Application Insights, Azure Monitor |
| Container Insights, Log Analytics, KQL, SLOs, alerts, runbooks, FinOps |
+-----------------------------------------------------------------------+
```

### The Senior-Level Story

The strong answer in a DevOps/cloud ops interview is:

- Build small, non-root, signed/scanned images from reproducible Dockerfiles.
- Deploy them to AKS with explicit requests/limits, probes, disruption budgets and safe
  rollout strategies.
- Use Workload Identity and Key Vault CSI instead of long-lived Kubernetes secrets where
  possible.
- Put deployment changes through environments, approvals and gates that match government
  change control.
- Manage infrastructure with remote state, approvals and drift detection.
- Use Azure Policy and landing-zone standards to make compliance repeatable.
- Monitor user outcomes through SLOs, not only CPU and pod counts.
- Treat cost as an operational signal through tagging, budgets and rightsizing.

---

## 4. The 200 Percent Checklist

| Area | Must be able to explain |
|---|---|
| Docker | Multi-stage builds, cache invalidation, base-image choice, distroless/chiseled images |
| Container runtime security | Non-root users, read-only filesystems, dropped capabilities, no secrets in images |
| Image supply chain | Trivy/Defender scanning, SBOM, signing, provenance, ACR retention and quarantine |
| Kubernetes objects | Pod, Deployment, StatefulSet, DaemonSet, Job/CronJob, Service, Ingress, ConfigMap, Secret |
| Scheduling | requests/limits, QoS, affinity, taints/tolerations, PDBs, topology spread |
| Autoscaling | HPA, VPA, KEDA, cluster autoscaler, AKS system/user pools, spot nodes |
| Networking | kubenet vs Azure CNI/Overlay, Network Policies, ingress controllers, private clusters |
| AKS specifics | managed identity, Workload Identity, Key Vault CSI, Entra RBAC, Azure Policy, Container Insights |
| Upgrades | node image upgrades, Kubernetes upgrades, PDB/probe readiness, maintenance windows |
| GitOps | Helm vs Kustomize, Argo CD/Flux reconciliation, drift, SOPS/Sealed Secrets |
| Debugging | CrashLoopBackOff, OOMKilled, ImagePullBackOff, evictions, `kubectl` triage flow |
| CI/CD | Azure DevOps YAML, environments, approvals, service connections, GitHub Actions OIDC |
| Deployment | rolling, blue/green, canary, feature flags, DB migration sequencing, rollback |
| Pipeline security | least privilege, secret scanning, SAST/DAST, container scans, SBOM, provenance |
| IaC | Terraform state/locking/modules/workspaces, Bicep modules/what-if/deployment stacks |
| Landing zones | management groups, subscriptions, naming, tagging, Azure Policy |
| Observability | OTel traces/metrics/logs, context propagation, Azure Monitor, App Insights, KQL |
| Operations | SLI/SLO/SLA, error budgets, alerting, on-call, runbooks, post-incident reviews |
| FinOps | Azure Cost Management, budgets, tagging, rightsizing, shared-cost allocation |

---

## 5. Official Docs To Re-Check

These areas change often; verify details close to the interview:

- Docker build best practices: https://docs.docker.com/build/building/best-practices/
- Docker build cache: https://docs.docker.com/build/cache/
- AKS docs: https://learn.microsoft.com/azure/aks/
- Kubernetes docs: https://kubernetes.io/docs/
- AKS Workload Identity and Key Vault CSI: https://learn.microsoft.com/azure/aks/csi-secrets-store-identity-access
- AKS Automatic: https://learn.microsoft.com/azure/aks/intro-aks-automatic
- Azure DevOps Pipelines: https://learn.microsoft.com/azure/devops/pipelines/
- GitHub Actions OIDC: https://docs.github.com/actions/deployment/security-hardening-your-deployments/about-security-hardening-with-openid-connect
- Terraform state: https://developer.hashicorp.com/terraform/language/state
- Bicep: https://learn.microsoft.com/azure/azure-resource-manager/bicep/
- Azure landing zones: https://learn.microsoft.com/azure/cloud-adoption-framework/ready/landing-zone/
- OpenTelemetry: https://opentelemetry.io/docs/
- Azure Monitor: https://learn.microsoft.com/azure/azure-monitor/
- Microsoft Cost Management: https://learn.microsoft.com/azure/cost-management-billing/costs/

