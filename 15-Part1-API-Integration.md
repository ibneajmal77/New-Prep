# Part 1.5 - API Design And Integration

*Two layers: **Part A** is the build narrative. **Part B** is the complete reference. **Part C**
is the interview pressure test.*

---

# Part A - THE BUILD: Contracts, Gateways And Legacy Systems

## Step 1. The portal needs stable APIs

The frontend needs leave balances, service requests, documents and approvals. Other
departments and vendors also need integration points. We design APIs as contracts, not as
controller methods exposed by accident.

> Reference: [1.5.1 REST API design](#151-rest-api-design)

## Step 2. The contract must be machine-readable

Multiple teams depend on these APIs: frontend, mobile, integration, testing, vendors and
future AI tools. We use OpenAPI 3.1 contract-first where stability matters, generate clients
where useful, and test compatibility with contract tests.

> Reference: [1.5.2 OpenAPI 3.1 and contract testing](#152-openapi-31-and-contract-testing)

## Step 3. Some clients need flexible reads

A dashboard wants employee summary, approvals and notifications in one round trip. GraphQL may
help for flexible read composition, but it introduces query cost, authorization and N+1 risks.

> Reference: [1.5.3 GraphQL](#153-graphql)

## Step 4. Some services need high-performance internal contracts

Internal service-to-service calls with strict schemas may use gRPC and protobuf. But gRPC is
not ideal for every public or browser-facing API.

> Reference: [1.5.4 gRPC and protobuf](#154-grpc-and-protobuf)

## Step 5. Integrations fail after you go home

Webhooks, SFTP imports and legacy systems fail at 2am. A senior integration design includes
retries, exponential backoff, idempotency, dead-letter queues, reconciliation and the outbox
pattern.

> Reference: [1.5.5 Webhooks, retries, DLQs and outbox](#155-webhooks-retries-dlqs-and-outbox)

## Step 6. The edge needs governance

Azure API Management sits at the API edge. It enforces identity, subscriptions, quotas,
policies, routing and operational visibility. It also helps protect internal services and
standardize vendor access.

> Reference: [1.5.8 Azure API Management](#158-azure-api-management)

---

# Part B - THE REFERENCE

## 1.5.1 REST API Design

REST is not "JSON over HTTP." Good REST-style APIs model resources and use HTTP semantics
consistently.

### 1.5.1.1 Resource Modeling

Prefer nouns:

```text
GET    /employees/{employeeId}
GET    /employees/{employeeId}/leave-balance
POST   /leave-requests
GET    /leave-requests/{requestId}
POST   /leave-requests/{requestId}/approval-decisions
```

Avoid RPC-shaped endpoints unless the operation truly is an action:

```text
/doLeave
/getEmployeeData
/approveRequestNow
```

Actions can be modeled as subresources:

```text
POST /leave-requests/{id}/cancellations
POST /salary-letter-requests/{id}/resubmissions
```

### 1.5.1.2 HTTP Methods

| Method | Meaning | Notes |
|---|---|---|
| GET | read | safe and should not mutate state |
| POST | create or command | not inherently idempotent |
| PUT | replace resource | idempotent by definition |
| PATCH | partial update | can be idempotent depending on design |
| DELETE | delete/cancel | should be idempotent from client view |

### 1.5.1.3 Idempotency

Idempotency protects against retries. It is critical for:

- request creation,
- payments,
- approvals,
- notifications,
- external submissions.

Common pattern:

```text
POST /leave-requests
Idempotency-Key: 8bd8b0...
```

Server stores the key, request hash and result. If the same key arrives again, the server
returns the original result instead of creating a duplicate.

### 1.5.1.4 Pagination

Offset pagination:

```text
GET /leave-requests?page=3&pageSize=25
```

Good for simple admin pages, but can drift when data changes.

Cursor pagination:

```text
GET /leave-requests?cursor=eyJsYXN0SWQiOjEyM30&pageSize=25
```

Better for large or changing datasets. Cursor must encode a stable sort position.

Rules:

- always define sort order,
- cap page size,
- include next cursor/link,
- do not allow unbounded list endpoints.

### 1.5.1.5 Filtering And Sorting

Design filters explicitly:

```text
GET /leave-requests?status=pending&departmentId=FIN&from=2026-01-01
```

Avoid exposing arbitrary database columns without governance. Filters must map to indexes and
authorization rules.

### 1.5.1.6 Versioning

Options:

- URI versioning: `/v1/leave-requests`
- header versioning: `Accept: application/vnd.entity.v1+json`
- query versioning: `?api-version=1.0`

Pragmatic answer:

- Use additive changes where possible.
- Do not break existing clients silently.
- Publish deprecation timelines.
- Version public/vendor APIs more strictly than internal APIs.
- Use APIM to route versions where useful.

## 1.5.2 OpenAPI 3.1 And Contract Testing

### 1.5.2.1 Contract-First

Contract-first means the OpenAPI spec is designed and reviewed before implementation.

Benefits:

- frontend can build against mocks,
- vendors know the exact contract,
- code generation becomes possible,
- breaking changes are detectable,
- security review can inspect the API surface.

Contract-first is especially useful in government/vendor environments because teams and
suppliers often work in parallel.

### 1.5.2.2 OpenAPI 3.1

OpenAPI 3.1 aligns more closely with JSON Schema. Use it to define:

- paths,
- operations,
- request bodies,
- response schemas,
- status codes,
- auth schemes,
- examples,
- callbacks/webhooks where relevant.

Good spec discipline:

- document error formats,
- include examples,
- define reusable components,
- name operation IDs consistently,
- avoid vague `object` schemas,
- review nullable/optional semantics carefully.

### 1.5.2.3 Code Generation

Generate:

- TypeScript API clients,
- .NET/Python client SDKs,
- server stubs where useful,
- typed models.

Risks:

- generated code can be ugly,
- regeneration can cause noisy diffs,
- hand-edited generated files become a maintenance problem,
- incorrect specs produce incorrect clients.

Treat generated code as build artifact or clearly owned source, depending on repo strategy.

### 1.5.2.4 Pact Contract Testing

Pact supports consumer-driven contract testing:

- consumer defines expected interactions,
- provider verifies it satisfies those expectations,
- CI catches breaking API changes before deployment.

Use when:

- consumer and provider deploy independently,
- multiple teams own different services,
- breaking changes are expensive,
- API behavior matters beyond schema shape.

Schema validation alone is not enough. Contract tests verify real interaction expectations.

## 1.5.3 GraphQL

GraphQL lets clients request exactly the fields they need. It can be valuable for complex read
composition, but it moves complexity into schema governance and query execution.

### 1.5.3.1 Federation

Federation composes multiple GraphQL subgraphs into one graph. Example:

- HR subgraph owns employee profile,
- workflow subgraph owns approvals,
- document subgraph owns generated letters.

Use federation when domain ownership is clear and teams can govern schema evolution.

Avoid federation when it becomes a thin wrapper over unclear service boundaries.

### 1.5.3.2 N+1 And DataLoader

GraphQL resolvers can accidentally issue one query per parent object.

Bad shape:

```text
Query approvals
  -> resolver loads 50 approvals
  -> employee resolver loads employee 50 times
```

DataLoader batches and caches loads per request:

```text
load employee 1
load employee 2
load employee 3
  -> one batched call: get employees [1,2,3]
```

### 1.5.3.3 Query Cost Limiting

GraphQL clients can ask expensive nested queries. Controls:

- depth limits,
- complexity scoring,
- field cost weights,
- timeout limits,
- persisted queries,
- rate limits by identity,
- pagination enforcement on list fields.

### 1.5.3.4 Persisted Queries

Persisted queries allow only pre-approved query hashes. Benefits:

- smaller requests,
- better caching,
- reduced abuse surface,
- stronger governance for public/mobile clients.

## 1.5.4 gRPC And Protobuf

gRPC uses HTTP/2 and protobuf by default for strongly typed service contracts.

Use when:

- internal service-to-service calls need low latency,
- streaming is useful,
- polyglot generated clients matter,
- schema evolution is controlled,
- clients are not ordinary browsers.

Avoid when:

- external vendors expect REST/JSON,
- browser support and debugging simplicity matter,
- API must be easily called with simple tools,
- human readability of payloads is important,
- intermediaries do not support HTTP/2 well.

### Protobuf

Protobuf defines messages and services:

```proto
message EmployeeRequest {
  string employee_id = 1;
}

message LeaveBalance {
  string employee_id = 1;
  int32 remaining_days = 2;
}
```

Schema evolution rules matter:

- never reuse field numbers,
- reserve removed fields,
- add optional fields carefully,
- maintain backward compatibility.

## 1.5.5 Webhooks, Retries, DLQs And Outbox

### 1.5.5.1 Webhooks

Webhooks are outbound HTTP callbacks when events happen.

Design requirements:

- signed payloads,
- timestamp/nonce to prevent replay,
- idempotency event IDs,
- retry policy,
- delivery logs,
- manual replay,
- secret rotation,
- endpoint verification where needed.

### 1.5.5.2 Retries And Exponential Backoff

Retries are for transient failures, not invalid requests.

Use:

- exponential backoff,
- jitter,
- max attempts,
- retry-after support,
- circuit breaking,
- DLQ after exhaustion.

Avoid synchronized retries that create a thundering herd.

### 1.5.5.3 Dead-Letter Queues

DLQ stores messages that cannot be processed after retries. A DLQ is useful only if there is an
operational process:

- alert,
- inspect error,
- fix root cause,
- replay or discard,
- audit decision.

### 1.5.5.4 Outbox Pattern

Problem:

```text
1. Write leave request to DB.
2. Publish "LeaveRequestCreated" event.
3. Process crashes between 1 and 2.
```

Now the database changed but no event was published.

Outbox solution:

- write business row and outbox event in the same DB transaction,
- separate publisher reads outbox table,
- publisher sends message,
- mark outbox row as sent,
- retry safely.

The outbox pattern is one of the strongest answers for reliable integration.

## 1.5.6 Rate Limiting, Throttling, Circuit Breakers, Bulkheads And Timeouts

### Rate Limiting vs Throttling

- **Rate limiting:** rejects or delays requests above a configured rate.
- **Throttling:** broader control of request flow, often dynamic under load.

Use at:

- API gateway,
- application service,
- per-user/per-tenant level,
- per vendor/integration level.

### Circuit Breakers

A circuit breaker stops repeatedly calling a failing dependency:

- closed: calls flow normally,
- open: calls fail fast,
- half-open: limited probe calls test recovery.

Use to protect both your service and the dependency.

### Bulkheads

Bulkheads isolate resources:

- separate connection pools,
- separate worker pools,
- separate queues,
- per-integration concurrency limits.

If the payroll integration is slow, it should not exhaust all resources needed for leave
requests.

### Timeouts

Every remote call needs a timeout. The timeout must fit the caller's deadline.

Bad:

```text
frontend waits 30s
API waits 60s
dependency waits forever
```

Good:

```text
frontend deadline 10s
API timeout 8s
dependency timeout 5s
fallback or async workflow after timeout
```

## 1.5.7 Legacy And On-Prem Integration

Government entities often have:

- SOAP services,
- SFTP file drops,
- ESBs,
- mainframe-like systems,
- scheduled batch exports,
- manually maintained Excel files,
- VPN/private network connectivity,
- vendor systems with weak documentation.

### SOAP

Design an adapter:

- hide WSDL/client details behind a modern interface,
- map SOAP faults to domain errors,
- enforce timeouts,
- log correlation IDs,
- validate XML safely,
- avoid leaking SOAP structures into the rest of the application.

### File Drops And SFTP

Production file integration needs:

- agreed file naming convention,
- schema/version in file,
- checksum,
- encryption where required,
- atomic upload pattern,
- processed/archive/error folders,
- idempotent imports,
- reconciliation report,
- alert on missing file.

### ESB

An ESB may handle routing, transformation and mediation. Senior answer:

"I would integrate through the ESB if it is the governed enterprise integration path, but I
would still keep a clear adapter boundary in my service and avoid spreading ESB-specific
formats through the domain."

## 1.5.8 Azure API Management

Azure API Management is an API gateway and management layer.

### 1.5.8.1 Policies

Policies can handle:

- JWT validation,
- header transformation,
- URL rewriting,
- rate limits,
- quotas,
- IP filtering,
- caching,
- backend selection,
- request/response transformation,
- logging/enrichment.

Policy order and scope matter: global, product, API, operation.

### 1.5.8.2 Products And Subscriptions

Products group APIs for consumers. Subscriptions control access.

Use cases:

- vendor product with strict quotas,
- internal department product,
- mobile app product,
- sandbox product.

### 1.5.8.3 JWT Validation

APIM can validate JWT claims before traffic reaches the backend:

- issuer,
- audience,
- signature,
- expiry,
- required claims,
- scopes/roles.

Backend services should still perform authorization for sensitive business decisions. Gateway
validation is not a replacement for domain authorization.

### 1.5.8.4 Backend Pools

Backend pools support routing and resilience across backend services. Use for:

- blue/green deployments,
- weighted routing,
- failover,
- regional backends,
- separating vendor/internal backends.

### 1.5.8.5 Self-Hosted Gateway

Self-hosted gateway is useful when APIs or backends are inside private/on-prem networks but
need APIM governance.

Use when:

- backends cannot be exposed publicly,
- private network access is required,
- consistent policies are needed across cloud/on-prem,
- regional or data-residency constraints matter.

Operational concerns:

- gateway deployment and patching,
- connectivity to Azure control plane,
- logging,
- scaling,
- secret management,
- network routing.

---

# Part C - Interview Traps

## Trap 1. "REST means every endpoint should map exactly to a database table."

Better answer: REST models resources from the client/domain view, not tables. Some actions are
subresources, some reads are projections, and internal persistence should not leak into the
API contract.

## Trap 2. "Retries make integrations reliable."

Better answer: retries without idempotency create duplicate effects. Reliable integration
needs idempotency keys, backoff, jitter, DLQs, outbox, reconciliation and operational replay.

## Trap 3. "GraphQL solves over-fetching, so use it for everything."

Better answer: GraphQL helps flexible reads, but adds schema governance, authorization,
query-cost and N+1 complexity. REST may be simpler for command workflows and vendor APIs.

## Trap 4. "gRPC is better than REST."

Better answer: gRPC is excellent for internal strongly typed service calls and streaming. REST
is usually better for public/vendor/browser-friendly APIs. The right choice depends on client
capability, debugging needs, network path and contract governance.

## Trap 5. "APIM authorization is enough."

Better answer: APIM can validate tokens and enforce coarse policies. Backends still need
business authorization because permissions often depend on resource ownership, workflow state
and domain rules.

