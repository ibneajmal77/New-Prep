# Part 3.3 - CI/CD

*Two layers: **Part A** is the build narrative. **Part B** is the complete reference. **Part C**
is the interview pressure test.*

---

# Part A - THE BUILD: From Commit To Production

## Step 1. Build once, promote the same artifact

The platform should not rebuild a different image for every environment. CI builds, tests,
scans, signs and publishes an immutable artifact. CD promotes that artifact through dev, test,
staging and production with approvals.

> Reference: [3.3.1 CI/CD pipeline shape](#331-cicd-pipeline-shape)

## Step 2. Azure DevOps environments enforce change control

Government releases usually need manual approvals, gates, change windows and deployment
history. Azure DevOps YAML pipelines plus Environments, approvals/checks, variable groups,
service connections and self-hosted agents cover the enterprise path.

> Reference: [3.3.2 Azure DevOps Pipelines](#332-azure-devops-pipelines)

## Step 3. GitHub Actions can deploy without long-lived Azure secrets

GitHub Actions can use OIDC federation to Azure so workflows exchange short-lived tokens
instead of storing cloud credentials. Reusable workflows standardize deployment and reduce
copy/paste risk.

> Reference: [3.3.3 GitHub Actions](#333-github-actions)

## Step 4. Deployment strategy is a risk decision

Rolling updates are simple. Blue/green gives fast switchback. Canary reduces blast radius.
Feature flags decouple deployment from release. Database migration sequencing can make or break
all of them.

> Reference: [3.3.4 Deployment strategies](#334-deployment-strategies)

## Step 5. Pipeline security is part of production security

The pipeline can create production resources and deploy code. It must be least privilege,
auditable and hardened with secret scanning, dependency scanning, SAST, DAST, container scans,
SBOMs and artifact provenance.

> Reference: [3.3.5 Pipeline security](#335-pipeline-security)

---

# Part B - THE REFERENCE

## 3.3.1 CI/CD Pipeline Shape

CI answers: "Is this change safe enough to package?"

CD answers: "Should this packaged artifact be released into this environment now?"

Typical flow:

```text
Pull request
  -> lint/typecheck/unit tests
  -> SAST/dependency/secret scans
  -> build container image
  -> generate SBOM
  -> scan image
  -> sign/attest image
  -> push to ACR by digest
  -> deploy to dev
  -> integration/e2e/smoke tests
  -> approval/gates
  -> staging
  -> production strategy
  -> post-deploy verification
```

Principles:

- build once,
- promote immutable artifact,
- use environment-specific configuration outside the artifact,
- make approvals environment-based,
- keep deployment identity least privilege,
- record artifact digest, commit SHA and approver,
- automate rollback/fix-forward paths.

## 3.3.2 Azure DevOps Pipelines

### YAML Pipelines

YAML pipelines define stages/jobs/steps as code.

Example shape:

```yaml
stages:
- stage: Build
  jobs:
  - job: BuildImage
    steps:
    - script: docker build -t $(imageName):$(Build.SourceVersion) .

- stage: Deploy_Staging
  dependsOn: Build
  jobs:
  - deployment: Deploy
    environment: staging
    strategy:
      runOnce:
        deploy:
          steps:
          - script: echo Deploy immutable digest
```

Keep secrets out of YAML. Reference secured resources through service connections, variable
groups, Key Vault integration or managed identities where supported.

### Multi-Stage Pipelines

Stages map to lifecycle phases:

- build,
- test,
- package,
- deploy dev,
- deploy test,
- deploy staging,
- deploy production.

Benefits:

- visible promotion path,
- per-stage approvals,
- environment history,
- separation of duties.

### Environments

Azure DevOps Environments represent deployment targets such as AKS namespaces, VMs or abstract
environments.

Use for:

- deployment history,
- approvals/checks,
- environment security,
- traceability.

### Approvals And Gates

Approvals/checks can be attached to environments, service connections, variable groups, secure
files and agent pools. This is strong for government change control because approvals are
managed by resource owners, not only YAML authors.

Common checks:

- manual approval,
- business hours/change window,
- branch control,
- required template,
- Invoke REST/Azure Function check,
- exclusive lock,
- query Azure Monitor alerts.

### Variable Groups

Variable groups share configuration across pipelines. Secret variables are protected resources
and should have pipeline permissions and approvals where needed.

Rules:

- avoid open access for secret groups,
- do not echo variables,
- prefer Key Vault-backed secrets,
- separate environment variables by environment,
- keep nonsecret config in code where possible.

### Service Connections

Service connections let pipelines access Azure, container registries and other external
systems.

Security:

- least-privilege role assignment,
- scope to resource group/subscription as narrowly as possible,
- avoid broad owner permissions,
- use workload identity/federated credentials where possible,
- restrict which pipelines can use the connection,
- audit usage.

### Self-Hosted Agents

Use self-hosted agents when:

- private network access is required,
- private AKS API server must be reached,
- builds need special tools,
- compliance requires controlled runner hosts.

Risks:

- agents can retain workspace state,
- secrets may be exposed to untrusted jobs,
- patching is your responsibility,
- network access increases blast radius.

Control:

- ephemeral agents where possible,
- isolate by project/environment,
- harden base image,
- no untrusted PRs on privileged agents,
- monitor agent pool usage.

## 3.3.3 GitHub Actions

### Reusable Workflows

Reusable workflows reduce duplication:

```yaml
on:
  workflow_call:
    inputs:
      environment:
        required: true
        type: string
```

Use for:

- standardized build,
- standardized scanning,
- standardized Azure deployment,
- centralized security controls.

### OIDC Federation To Azure

OIDC lets GitHub Actions request a short-lived token from GitHub's OIDC provider. Azure trusts
that token through a federated identity credential on an Entra app registration or managed
identity.

Benefits:

- no long-lived Azure client secret in GitHub,
- tighter trust based on repo/branch/environment claims,
- auditable cloud role assignment,
- easier rotation because there is no stored password.

Workflow needs:

```yaml
permissions:
  id-token: write
  contents: read
```

Azure trust should restrict:

- organization/repository,
- branch or tag,
- environment,
- reusable workflow reference where possible.

### Environments

GitHub Environments can enforce:

- required reviewers,
- wait timers,
- environment secrets,
- deployment protection rules.

Use environment secrets cautiously. OIDC should replace cloud secrets where possible.

### Artifact Attestations

Artifact attestations establish build provenance: which workflow, repo, commit and environment
produced an artifact. They are not proof the artifact is vulnerability-free; they are evidence
for supply-chain policy.

Use for:

- released binaries,
- container images,
- SBOM association,
- admission-control policy.

## 3.3.4 Deployment Strategies

### Rolling Deployment

Gradually replaces old Pods with new Pods.

Pros:

- simple,
- native Kubernetes default,
- resource efficient.

Cons:

- old and new versions run together,
- rollback may be slower than switching traffic,
- database compatibility is required.

### Blue/Green

Two full environments exist: blue and green. Traffic switches from one to the other.

Pros:

- fast switchback,
- production-like validation before cutover,
- clear release boundary.

Cons:

- higher cost,
- database state is shared or complex,
- long-running sessions need handling.

### Canary

Small percentage of traffic goes to new version first.

Pros:

- low blast radius,
- real production signal,
- progressive confidence.

Cons:

- requires routing/metrics maturity,
- canary analysis can be noisy,
- user/session consistency may matter.

### Feature Flags

Feature flags decouple deployment from feature release.

Use for:

- gradual rollout,
- emergency disable,
- A/B tests,
- role/department-specific features.

Risks:

- stale flags,
- complex combinations,
- permission confusion,
- testing matrix growth.

Maintain flag ownership and expiry dates.

### Database Migration In The Pipeline

Database changes must be deployment-compatible.

Safe sequence:

1. Run backward-compatible schema expansion.
2. Deploy app that supports old and new schema.
3. Backfill idempotently.
4. Flip reads/writes.
5. Verify.
6. Contract old schema later.

Never let the pipeline casually run destructive migrations against production without approval,
backup/restore confidence and rollback/forward-fix plan.

## 3.3.5 Rollback, Release Notes And Change Windows

### Rollback

Rollback must include:

- app artifact rollback,
- config rollback,
- database compatibility,
- feature flag disable,
- traffic switchback,
- queue/message compatibility,
- audit of action taken.

Sometimes fix-forward is safer than rollback after schema changes. Say that explicitly.

### Release Notes

Good release notes include:

- change summary,
- affected services,
- user impact,
- risk level,
- migration steps,
- rollback/fix-forward plan,
- known issues,
- monitoring dashboard,
- support contact.

### Change-Freeze Windows

Government entities often have freeze windows around payroll, public launches, audits, major
events or holidays.

Pipeline design should support:

- environment locks,
- emergency exception process,
- documented approvers,
- release calendar,
- deployment evidence.

## 3.3.6 Pipeline Security

### Least-Privilege Service Principals

Deployment identities should have only the permissions they need:

- push to one ACR repository,
- deploy to one AKS namespace,
- read specific Key Vault secrets,
- apply specific resource group changes.

Avoid subscription Owner for normal pipelines.

### Secret Scanning

Use secret scanning on:

- pull requests,
- full repo history where possible,
- pipeline logs,
- container image layers,
- IaC files.

If a secret leaks:

1. revoke/rotate immediately,
2. remove from code,
3. investigate usage,
4. add detection/prevention,
5. document incident.

### Artifact Provenance

Track:

- commit SHA,
- build run ID,
- builder identity,
- image digest,
- SBOM,
- scan result,
- signature/attestation,
- approver,
- deployment time.

### SBOM

Generate SBOMs for:

- app packages,
- container images,
- release bundles.

Use SBOMs for vulnerability response and vendor assurance.

### Dependency Scanning

Run before build and periodically after release because new CVEs appear after deployment.

### SAST, DAST And Container Scan Placement

| Control | Where it runs | Finds |
|---|---|---|
| SAST | PR/CI | insecure code patterns |
| dependency scan | PR/CI/scheduled | vulnerable packages |
| secret scan | PR/CI/continuous | leaked secrets |
| container scan | image build/registry/admission | image CVEs/misconfig |
| DAST | deployed test/staging env | runtime web/API issues |
| IaC scan | PR/CI | insecure cloud/K8s config |

Do not rely on one scan type. They catch different classes of risk.

---

# Part C - Interview Traps

## Trap 1. "CI/CD means deploy every commit to production."

Better answer: CI/CD means changes are automatically built, tested and made deployable.
Production deployment still follows risk, approvals and change-control policy.

## Trap 2. "Approval in YAML is enough."

Better answer: YAML authors can modify YAML. For production, use environment/resource-level
approvals and checks controlled by resource owners.

## Trap 3. "Rollback is just redeploying the old image."

Better answer: rollback includes config, database compatibility, queue/message contracts and
feature flags. After schema changes, fix-forward may be safer.

## Trap 4. "OIDC means no secrets at all."

Better answer: OIDC removes long-lived cloud deployment secrets from GitHub, but the workflow
still needs careful permissions, environment protection and trust conditions.

## Trap 5. "Scanning in the pipeline means secure."

Better answer: scanning is one control. I also need least privilege, provenance, SBOMs,
runtime monitoring, admission policy, patching and a vulnerability SLA.

