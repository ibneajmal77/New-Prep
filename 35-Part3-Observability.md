# Part 3.5 - Observability

*Two layers: **Part A** is the build narrative. **Part B** is the complete reference. **Part C**
is the interview pressure test.*

---

# Part A - THE BUILD: Knowing What Production Is Doing

## Step 1. Logs alone are not observability

The platform has APIs, queues, AKS, APIM, databases and external systems. When users report
slow approvals, a log file from one service is not enough. We need traces, metrics and logs
linked by correlation/context.

> Reference: [3.5.1 OpenTelemetry](#351-opentelemetry)

## Step 2. Azure Monitor is the operational home

Application telemetry goes to Application Insights. AKS and infrastructure telemetry goes to
Azure Monitor/Container Insights. Logs are queried through Log Analytics using KQL.

> Reference: [3.5.2 Azure Monitor, Application Insights and Log Analytics](#352-azure-monitor-application-insights-and-log-analytics)

## Step 3. KQL becomes the incident language

KQL is used for Azure Monitor and also matters elsewhere in the Microsoft data ecosystem. We
need enough KQL to investigate errors, latency, dependencies, pod restarts and cost signals.

> Reference: [3.5.3 KQL](#353-kql)

## Step 4. Alerts should protect SLOs, not create noise

The team starts with CPU alerts and gets paged constantly. We move toward SLIs and SLOs:
availability, latency, error rate and workflow success. Error budgets help decide release
risk.

> Reference: [3.5.4 SLI, SLO, SLA and error budgets](#354-sli-slo-sla-and-error-budgets)

## Step 5. Operations need runbooks and reviews

Alerts must have owners, severity, action groups, runbooks and post-incident reviews. Otherwise
monitoring becomes notification noise.

> Reference: [3.5.5 Alerting, on-call, runbooks and post-incident reviews](#355-alerting-on-call-runbooks-and-post-incident-reviews)

## Step 6. Cost is telemetry

Cloud cost is not only finance. Engineers influence cost through AKS node sizes, log volume,
retention, overprovisioning, unused resources and scaling settings. FinOps makes cost visible
by team, workload and environment.

> Reference: [3.5.6 Cost observability and FinOps](#356-cost-observability-and-finops)

---

# Part B - THE REFERENCE

## 3.5.1 OpenTelemetry

OpenTelemetry is a vendor-neutral standard/toolkit for collecting and exporting telemetry.

Signals:

- traces,
- metrics,
- logs,
- baggage/context.

### 3.5.1.1 Traces

Traces show a request path through distributed systems.

Example:

```text
HTTP POST /leave-requests
  -> API validation
  -> SQL insert
  -> outbox write
  -> queue publish
  -> notification service
  -> external SMS provider
```

Each operation is a span. Spans include timing, status and attributes.

Use traces for:

- dependency latency,
- error causality,
- cross-service request flow,
- queue processing links,
- slow path investigation.

### 3.5.1.2 Metrics

Metrics are numeric measurements over time.

Examples:

- request count,
- latency histogram,
- error count,
- queue depth,
- CPU/memory,
- pod restarts,
- cache hit rate,
- DB connection pool usage.

Metrics are better than logs for alerting because they are cheaper to aggregate and easier to
threshold.

### 3.5.1.3 Logs

Logs are event records. Good logs are structured:

```json
{
  "level": "error",
  "message": "Leave request submission failed",
  "trace_id": "abc",
  "employee_id_hash": "f2a...",
  "request_id": "req-123",
  "error_code": "LEGACY_TIMEOUT"
}
```

Do:

- use structured logs,
- include correlation/trace ID,
- include business-safe identifiers,
- avoid secrets/PII,
- sample noisy logs,
- set retention by data classification.

### 3.5.1.4 Context Propagation

Context propagation carries trace/correlation context across service boundaries:

- HTTP headers,
- messaging metadata,
- background jobs,
- queue consumers.

Without propagation, traces break at service boundaries and incidents become guesswork.

### 3.5.1.5 Semantic Conventions

Semantic conventions standardize telemetry attributes:

- HTTP method/status,
- route,
- database system,
- messaging operation,
- service name,
- deployment environment.

Use them so dashboards and alerts work across Python, .NET and Node services.

### 3.5.1.6 Sampling And Cardinality

Sampling controls trace volume. Cardinality controls how many unique metric label combinations
exist.

Avoid high-cardinality labels:

- raw user ID,
- request ID,
- session ID,
- full URL with query string.

High cardinality can explode cost and hurt query performance.

## 3.5.2 Azure Monitor, Application Insights And Log Analytics

### Azure Monitor

Azure Monitor is Microsoft's observability platform for metrics, logs, traces and events across
Azure and hybrid environments.

Use for:

- resource metrics,
- alerts,
- dashboards/workbooks,
- activity logs,
- AKS monitoring,
- Application Insights,
- Log Analytics.

### Application Insights

Application Insights is Azure's application performance monitoring experience, now aligned with
OpenTelemetry collection approaches.

Use for:

- request telemetry,
- dependency telemetry,
- exceptions,
- traces,
- availability tests,
- performance investigations,
- application maps.

### Log Analytics

Log Analytics workspaces store logs/traces queried with KQL.

Design choices:

- workspace per region/environment or centralized workspace,
- retention by data type,
- RBAC/access controls,
- private link where required,
- data collection rules,
- ingestion cost controls.

### Container Insights

Container Insights for AKS provides:

- container logs,
- Kubernetes events,
- node/pod inventory,
- performance metrics,
- live logs/events,
- integration with Log Analytics.

Control cost:

- collect only needed tables,
- exclude noisy namespaces,
- tune collection interval,
- reduce debug log volume,
- set retention deliberately.

## 3.5.3 KQL

KQL is the query language used by Azure Monitor Logs and Azure Data Explorer.

### Basic Shape

```kusto
requests
| where timestamp > ago(1h)
| where cloud_RoleName == "portal-api"
| summarize count(), p95=percentile(duration, 95) by bin(timestamp, 5m)
| order by timestamp asc
```

### Useful Operators

| Operator | Use |
|---|---|
| `where` | filter rows |
| `project` | select columns |
| `extend` | compute new column |
| `summarize` | aggregate |
| `bin` | time bucket |
| `join` | combine tables |
| `parse` | extract fields |
| `order by` | sort |
| `take` | sample rows |

### Error Investigation

```kusto
exceptions
| where timestamp > ago(24h)
| summarize count() by type, outerMessage
| order by count_ desc
```

### Dependency Latency

```kusto
dependencies
| where timestamp > ago(2h)
| summarize p95=percentile(duration, 95), failures=countif(success == false)
  by target, type
| order by p95 desc
```

### AKS Pod Restarts

Table names depend on collection settings, but the investigation pattern is:

```kusto
KubePodInventory
| where TimeGenerated > ago(6h)
| summarize Restarts=max(ContainerRestartCount) by Name, Namespace
| order by Restarts desc
```

### Join Trace And Request Context

```kusto
requests
| where timestamp > ago(1h)
| where success == false
| join kind=leftouter traces on operation_Id
| project timestamp, name, resultCode, message, operation_Id
```

Senior answer: KQL is not just syntax. It is how you turn telemetry into incident evidence.

## 3.5.4 SLI, SLO, SLA And Error Budgets

### SLI

Service Level Indicator: measured signal.

Examples:

- request availability,
- p95 latency,
- workflow completion rate,
- queue processing delay,
- successful login rate.

### SLO

Service Level Objective: internal reliability target.

Examples:

- 99.9 percent of leave submission requests succeed monthly,
- p95 dashboard load under 1.5 seconds,
- 99 percent of notification jobs processed within 2 minutes.

### SLA

Service Level Agreement: external/customer commitment, often contractual.

SLAs should be lower or equal to SLOs because you need engineering buffer.

### Error Budget

Error budget is the allowed unreliability:

```text
99.9 percent monthly SLO = about 0.1 percent allowed failure time/events
```

Use it to decide:

- whether to keep shipping,
- whether reliability work takes priority,
- whether to freeze risky changes,
- whether incident follow-up is required.

### Good SLIs For This Platform

- login success rate,
- leave request submission success,
- p95/p99 API latency,
- approval workflow completion time,
- document generation success,
- queue age,
- external dependency failure rate,
- frontend Core Web Vitals.

## 3.5.5 Alerting, On-Call, Runbooks And Post-Incident Reviews

### Alert Design

Good alerts are:

- actionable,
- owned,
- tied to user impact,
- deduplicated,
- severity-based,
- linked to runbooks,
- routed to the right team.

Bad alerts:

- CPU high for five minutes with no user impact,
- every pod restart pages someone,
- warnings with no action,
- duplicate alerts from every layer.

### Azure Monitor Action Groups

Action groups define who is notified and what automation runs when an alert fires:

- email,
- SMS/voice/push where supported,
- webhook,
- Logic App,
- Azure Function,
- ITSM connector,
- runbook.

### Runbooks

Runbook structure:

1. Alert meaning.
2. Customer/user impact.
3. Dashboard links.
4. KQL queries.
5. Triage commands.
6. Safe mitigations.
7. Escalation path.
8. Rollback/fix-forward guidance.
9. Communication template.
10. Post-incident checklist.

### On-Call

On-call needs:

- rotation,
- severity definitions,
- escalation policy,
- access model,
- break-glass account,
- audit logging,
- handover notes,
- fatigue management.

### Post-Incident Review

Blameless review should capture:

- timeline,
- detection path,
- impact,
- root cause and contributing factors,
- what worked,
- what failed,
- action items with owners/dates,
- alert/runbook improvements.

Do not stop at "human error." Ask what system allowed the error to hurt production.

## 3.5.6 Cost Observability And FinOps

### Azure Cost Management

Use for:

- cost analysis,
- budgets,
- alerts,
- exports,
- anomaly detection,
- reservation/savings plan review,
- allocation by tag/subscription/resource group.

### Budgets

Budgets should be scoped:

- subscription,
- resource group,
- management group,
- department,
- project,
- workload.

Budget alerts should notify owners early enough to act, not after the invoice is already
surprising.

### Tagging

Cost tags:

- `Application`,
- `Environment`,
- `Owner`,
- `CostCenter`,
- `BusinessUnit`,
- `Criticality`.

Use Azure Policy to require tags. Understand that tag availability in cost records can vary by
resource type and timing.

### Rightsizing

Look for:

- oversized AKS nodes,
- over-requested Pods,
- idle databases,
- unused disks/IPs,
- excessive log ingestion,
- long retention on noisy tables,
- non-prod running 24/7,
- low reservation utilization.

### Cost In AKS

Cost controls:

- accurate requests/limits,
- separate node pools,
- autoscaling,
- spot for interruptible workloads,
- namespace/team cost allocation,
- log collection tuning,
- scale-down non-prod,
- use managed services where operational cost is lower.

### FinOps Conversation

Strong answer:

"I treat cost as an engineering signal. I need tagging and allocation to know who owns spend,
budgets and anomaly alerts to catch surprises, and rightsizing recommendations connected to
service reliability so cost cuts do not break SLOs."

---

# Part C - Interview Traps

## Trap 1. "We have logs, so we have observability."

Better answer: logs are one signal. Observability needs metrics, traces and logs correlated
through context propagation so we can explain system behavior.

## Trap 2. "Alert on CPU."

Better answer: CPU can be useful, but user-impact alerts should focus on SLIs: error rate,
latency, availability, queue delay and workflow success. CPU alerts are supporting signals.

## Trap 3. "SLA and SLO are the same."

Better answer: SLA is usually an external commitment. SLO is an internal reliability target.
SLIs are the measurements. Error budget is the allowed miss against the SLO.

## Trap 4. "KQL is just for logs."

Better answer: KQL is the investigation language across Azure Monitor logs, traces and many
Microsoft data/monitoring surfaces. It lets me turn telemetry into evidence.

## Trap 5. "FinOps means finance tells engineering to reduce cost."

Better answer: FinOps is shared accountability. Engineering controls architecture, sizing,
autoscaling, log volume and waste; finance provides allocation and governance; product decides
value tradeoffs.

