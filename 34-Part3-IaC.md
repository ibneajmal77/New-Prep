# Part 3.4 - Infrastructure As Code

*Two layers: **Part A** is the build narrative. **Part B** is the complete reference. **Part C**
is the interview pressure test.*

---

# Part A - THE BUILD: Reproducible Azure Infrastructure

## Step 1. ClickOps does not survive audit

The platform needs AKS, ACR, Key Vault, Log Analytics, managed identities, private endpoints,
APIM and databases. Creating them manually in the portal makes environments inconsistent and
hard to audit. We use Infrastructure as Code.

> Reference: [3.4.1 Terraform](#341-terraform)

## Step 2. State is the dangerous part

Terraform can recreate infrastructure only because it knows what exists. That knowledge lives
in state. In a team, local state is not acceptable for shared infrastructure. We need remote
state, locking, access control and state hygiene.

> Reference: [3.4.1.1 State management](#3411-state-management)

## Step 3. Plans need approval

For production, the pipeline should run `plan`, show what will change, require approval, then
apply using a controlled identity. Drift must be detected and reconciled deliberately.

> Reference: [3.4.1.4 Plan/apply approvals and drift](#3414-planapply-approvals-and-drift)

## Step 4. Bicep matters in Microsoft shops

Some Azure teams prefer Bicep because it is native to Azure Resource Manager, has strong Azure
tooling, supports modules, what-if and deployment stacks, and fits Microsoft governance
patterns.

> Reference: [3.4.2 Bicep and ARM](#342-bicep-and-arm)

## Step 5. Landing zones define the rules before workloads arrive

Azure Landing Zones set the enterprise structure: management groups, subscriptions, policies,
networking, naming, tagging and shared services. Workloads should land into governed
subscriptions, not invent their own foundation.

> Reference: [3.4.3 Azure Landing Zones](#343-azure-landing-zones)

---

# Part B - THE REFERENCE

## 3.4.1 Terraform

Terraform declares desired infrastructure and uses providers to create/update/delete real
resources.

Typical repo shape:

```text
infra/
  modules/
    aks/
    acr/
    key-vault/
    app-insights/
  envs/
    dev/
    test/
    prod/
```

Principles:

- separate reusable modules from environment composition,
- keep environment inputs explicit,
- pin provider versions,
- use remote state,
- review plans,
- protect production applies,
- detect drift.

### 3.4.1.1 State Management

Terraform state maps configuration resources to real cloud resources. It can contain sensitive
values, resource IDs and dependency metadata.

Do:

- use a remote backend for team work,
- enable locking if backend supports it,
- restrict state access,
- encrypt state at rest,
- avoid committing state to Git,
- avoid manually editing state,
- back up state where appropriate.

Azure common backend:

```hcl
terraform {
  backend "azurerm" {
    resource_group_name  = "rg-tfstate-prod"
    storage_account_name = "sttfstateprod001"
    container_name       = "tfstate"
    key                  = "employee-platform-prod.tfstate"
  }
}
```

### 3.4.1.2 Locking

State locking prevents two applies from modifying the same state at once. Without locking, two
engineers or pipelines can corrupt state or overwrite each other's changes.

If a lock is stuck:

- verify no run is active,
- identify the lock owner,
- use force-unlock only with strong evidence,
- record the incident.

### 3.4.1.3 Modules

Modules package repeatable infrastructure:

- AKS baseline,
- ACR with private endpoint,
- Key Vault with RBAC,
- Log Analytics workspace,
- APIM product,
- managed identity.

Good modules:

- expose meaningful inputs,
- set secure defaults,
- output only needed values,
- avoid excessive abstraction,
- version modules,
- include examples/tests where possible.

Bad modules:

- hide every Azure option behind generic maps,
- force all workloads into one pattern,
- expose secrets as outputs,
- mix environment-specific decisions with reusable logic.

### 3.4.1.4 Workspaces

Terraform workspaces can separate state for the same configuration.

Use carefully:

- good for simple environment separation,
- risky when environments need different topology,
- can hide which environment is active,
- CI must set workspace explicitly.

Many teams prefer separate environment directories because review is clearer.

### 3.4.1.5 Plan/Apply Approvals And Drift

Production pipeline:

```text
terraform fmt/check
terraform validate
terraform plan -out planfile
security/policy checks
manual approval
terraform apply planfile
post-apply verification
```

Drift happens when real infrastructure changes outside Terraform.

Controls:

- scheduled plan detection,
- Azure Policy,
- restricted portal permissions,
- activity log monitoring,
- import legitimate out-of-band changes,
- fix drift through code.

Do not auto-apply production drift corrections blindly.

## 3.4.2 Bicep And ARM

Bicep is a declarative language for Azure Resource Manager. It compiles to ARM JSON but is
more readable than raw ARM templates.

### 3.4.2.1 Bicep Modules

Modules let one Bicep file deploy another:

```bicep
module aks './modules/aks.bicep' = {
  name: 'aks-deploy'
  params: {
    clusterName: aksName
    location: location
  }
}
```

Use modules for:

- reusable platform resources,
- workload templates,
- secure defaults,
- standard naming/tagging,
- enterprise-approved patterns.

### 3.4.2.2 What-If

What-if previews changes before deployment. It is the Bicep/ARM equivalent of asking "What
will this deployment do?"

Use in pipeline:

```text
bicep build
az deployment group what-if
approval
az deployment group create
```

What-if is a prediction, not a substitute for review or testing.

### 3.4.2.3 Deployment Stacks

Deployment stacks manage a set of Azure resources as a unit. They help track resources managed
by a Bicep/ARM deployment and define behavior when resources are removed from the template.

Use when:

- resource lifecycle should be managed as one stack,
- unmanaged resources need clear detach/delete behavior,
- access to stack management should be RBAC-controlled,
- platform teams want stronger lifecycle governance.

### 3.4.2.4 Bicep vs Terraform

| Area | Terraform | Bicep |
|---|---|---|
| Cloud scope | multi-cloud/many providers | Azure-native |
| State | explicit state file/backend | ARM tracks deployments/resources |
| Azure feature freshness | sometimes provider lag | often fast for Azure |
| Team fit | common DevOps/IaC skill | common Microsoft/Azure platform skill |
| Governance | strong with pipelines/policy | strong with Azure-native what-if/stacks/policy |

Senior answer:

"If the organization is Azure-only and Microsoft-governed, Bicep can be the most natural
choice. If the platform spans clouds or many providers, Terraform may fit better. I can work
with either, but I care more about review, policy, drift control and repeatability than the
syntax."

## 3.4.3 Azure Landing Zones

Azure Landing Zones provide a scalable foundation for workloads.

Core elements:

- management group hierarchy,
- subscription structure,
- identity and RBAC,
- networking,
- security baseline,
- Azure Policy,
- logging/monitoring,
- naming and tagging,
- shared services,
- cost governance.

### 3.4.3.1 Management Groups

Management groups organize subscriptions and apply governance at scale.

Common structure:

```text
Tenant root
  -> Platform
      -> Identity
      -> Connectivity
      -> Management
  -> Landing Zones
      -> Corp
      -> Online
  -> Sandbox
  -> Decommissioned
```

Design points:

- do not model every department as a management group unless governance differs,
- use subscriptions for workload/environment boundaries,
- limit root-scope policy assignments,
- use PIM/JIT for privileged access,
- align with data residency and security requirements.

### 3.4.3.2 Azure Policy

Azure Policy evaluates resources against business rules and can audit, deny or remediate.

Use for:

- allowed regions,
- required tags,
- diagnostic settings,
- private endpoint requirements,
- disallowed public IPs,
- approved VM SKUs,
- AKS pod security controls,
- encryption requirements.

Concepts:

- policy definition,
- initiative/policy set,
- assignment scope,
- effect: audit, deny, append, modify, deployIfNotExists,
- remediation task.

Use audit mode before deny for broad policies.

### 3.4.3.3 Subscription Strategy

Subscriptions are security, billing and quota boundaries.

Possible separation:

- platform connectivity,
- platform management,
- identity,
- dev/test/prod workloads,
- sandbox,
- shared services.

Avoid putting every app in one subscription if blast radius, RBAC and cost allocation need
separation.

### 3.4.3.4 Naming Strategy

Naming should encode useful operational information without becoming unreadable.

Example:

```text
rg-emp-prod-uaen-001
aks-emp-prod-uaen-001
kv-emp-prod-uaen-001
```

Include:

- resource type,
- workload/application,
- environment,
- region,
- instance.

Respect Azure resource-specific naming limits.

### 3.4.3.5 Tagging Strategy

Tags support cost, operations and governance.

Common tags:

- `Application`,
- `BusinessUnit`,
- `CostCenter`,
- `Environment`,
- `Owner`,
- `DataClassification`,
- `Criticality`,
- `ManagedBy`,
- `SupportGroup`.

Enforce with Azure Policy. Remember: not all resources emit tags into cost data in the same
way, and tag inheritance/cost allocation settings may matter.

### 3.4.3.6 Drift Between IaC And Policy

Policy and IaC should complement each other:

- IaC declares desired workload resources.
- Policy sets enterprise guardrails.
- Drift detection finds out-of-band changes.
- Remediation corrects known safe non-compliance.

Do not rely on policy alone to design infrastructure. Do not rely on IaC alone for enterprise
governance.

---

# Part C - Interview Traps

## Trap 1. "Terraform state is just an implementation detail."

Better answer: state is critical. It maps config to real resources, can contain sensitive
values, and must be remote, locked, encrypted and access-controlled for team environments.

## Trap 2. "Workspaces are the best way to manage environments."

Better answer: workspaces can work for simple same-shape environments, but separate directories
or stacks are often clearer when environments differ. The key is explicit state and safe CI.

## Trap 3. "Bicep is only for people who do not know Terraform."

Better answer: Bicep is Azure-native and common in Microsoft-governed shops. Terraform is
excellent across providers. The right choice depends on organization standards, cloud scope and
governance needs.

## Trap 4. "What-if/plan means safe."

Better answer: plan/what-if shows expected changes, but humans still review risk. Some runtime
effects, policy interactions or data impacts require deeper validation.

## Trap 5. "Landing zone is just networking."

Better answer: landing zones include management groups, subscriptions, identity, policy,
networking, logging, naming, tagging, security baseline and cost governance.

