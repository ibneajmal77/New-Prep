# Part 1.6 - Architecture And Solution Design

*Two layers: **Part A** is the build narrative. **Part B** is the complete reference. **Part C**
is the interview pressure test.*

---

# Part A - THE BUILD: Designing The Whole Platform

## Step 1. Start with boundaries, not microservices

The platform includes HR services, approvals, documents, notifications, identity integration
and reporting. The first design decision is not "microservices or not"; it is **where the
business boundaries are** and who owns them.

For many government entities, a modular monolith or a small number of services is safer than
starting with many microservices. Microservices require mature DevOps, observability, service
ownership, data ownership and incident response.

> Reference: [1.6.1 Microservices vs modular monolith](#161-microservices-vs-modular-monolith)

## Step 2. Use DDD to find the seams

HR, approvals, documents and notifications do not speak the same language. "Request",
"case", "approval", "employee" and "document" may mean different things in different contexts.
DDD helps define bounded contexts and avoid one giant shared model.

> Reference: [1.6.2 DDD](#162-ddd)

## Step 3. Decide where events make sense

When a leave request is submitted, the system may notify a manager, update a dashboard, create
an audit entry and sync with a legacy HR system. Events are useful here, but they introduce
eventual consistency and duplicate delivery risk.

> Reference: [1.6.3 Event-driven architecture](#163-event-driven-architecture)

## Step 4. Design for failure explicitly

Distributed systems do not give exactly-once behavior end to end. We design for at-least-once
delivery with idempotent consumers, clear transaction boundaries, outbox, retries and
reconciliation.

> Reference: [1.6.4 CAP, idempotency and delivery semantics](#164-cap-idempotency-and-delivery-semantics)

## Step 5. Cache only with ownership and invalidation rules

The dashboard is slow because every request calls HR, workflow, documents and notifications.
Caching helps, but stale employee or approval data can create operational mistakes. Each cache
must have an owner, TTL, invalidation trigger and security model.

> Reference: [1.6.5 Caching strategies](#165-caching-strategies)

## Step 6. DR is not a diagram checkbox

Government platforms need explicit RTO/RPO, backup, restore testing, regional strategy,
dependency mapping and failover runbooks. Multi-region design without data and operational
readiness can create false confidence.

> Reference: [1.6.6 Resilience and disaster recovery](#166-resilience-and-disaster-recovery)

## Step 7. Produce architecture artifacts

The JD asks for solution design deliverables. The expected senior answer is not just "I can
draw diagrams"; it is knowing which artifact answers which question.

> Reference: [1.6.7 Solution design deliverables](#167-solution-design-deliverables)

---

# Part B - THE REFERENCE

## 1.6.1 Microservices vs Modular Monolith

### Modular Monolith

A modular monolith is one deployable application with strong internal boundaries.

Use when:

- one or two teams own the platform,
- domain boundaries are still evolving,
- shared transactions are important,
- deployment maturity is limited,
- operations team is small,
- latency between modules should be simple,
- the system can scale vertically/horizontally as one unit.

Good modular monolith design:

- modules by business capability,
- internal APIs between modules,
- no direct cross-module table access,
- clear ownership of data,
- tests around module boundaries,
- architecture checks to prevent dependency drift.

### Microservices

Microservices are independently deployable services owned by teams, usually with separate data
ownership.

Use when:

- domains are stable and clearly bounded,
- teams can own services end to end,
- independent deployment is valuable,
- scaling needs differ materially,
- failure isolation is required,
- integration maturity is high,
- observability and incident response are mature.

Costs:

- distributed transactions,
- network latency,
- versioning,
- observability complexity,
- CI/CD complexity,
- local development complexity,
- data duplication,
- eventual consistency,
- more security surface.

### Government-Specific Answer

"In a government entity I would be cautious about starting with many microservices unless the
organization has mature DevOps, monitoring, service ownership and change governance. A modular
monolith with clear bounded contexts is often the safer first step. If a module later needs
independent deployment or scaling, it can be extracted with less risk."

## 1.6.2 DDD

DDD, or Domain-Driven Design, is useful when business rules and language are complex.

### 1.6.2.1 Bounded Contexts

A bounded context is a boundary where a model has a specific meaning.

Example:

| Context | Meaning of "request" |
|---|---|
| Leave | employee asks for time off |
| Documents | employee asks for a generated letter |
| Procurement | department asks to buy something |
| IT Service Desk | user asks for support |

Do not force one universal `Request` table/model if the concepts behave differently.

### 1.6.2.2 Aggregates

An aggregate is a consistency boundary. It protects invariants.

Example: `LeaveRequest` aggregate may enforce:

- start date <= end date,
- only manager can approve,
- request cannot be approved after cancellation,
- balance must be checked before submission,
- status transitions are legal.

Aggregate rules:

- modify aggregate through methods/use cases,
- avoid exposing setters for invalid states,
- keep aggregates small enough to load and update,
- use domain events for side effects outside the aggregate boundary.

### 1.6.2.3 Ubiquitous Language

Use the business language in code, documents and discussions. If the HR team says "annual
leave entitlement", do not call it `VacationQuota` in code and `TimeOffBalance` in APIs unless
there is a reason.

Benefits:

- fewer translation errors,
- better stakeholder validation,
- clearer tests,
- more meaningful diagrams.

### 1.6.2.4 Context Mapping

Bounded contexts need relationships:

- upstream/downstream,
- shared kernel,
- customer/supplier,
- anti-corruption layer,
- conformist integration,
- published language.

For legacy HR integration, use an anti-corruption layer so old codes and SOAP objects do not
leak into the modern domain.

## 1.6.3 Event-Driven Architecture

### 1.6.3.1 Choreography vs Orchestration

**Choreography:** services react to events without a central coordinator.

Example:

```text
LeaveRequestSubmitted
  -> Notification service sends message
  -> Audit service records event
  -> Reporting service updates projection
```

Pros:

- loose coupling,
- easy to add listeners,
- resilient to some service failures.

Cons:

- harder to understand full process,
- hidden coupling through events,
- debugging spans multiple services.

**Orchestration:** a coordinator controls workflow steps.

Example:

```text
Workflow service:
  1. validate request
  2. reserve balance
  3. request manager approval
  4. update HR system
  5. notify employee
```

Pros:

- easier process visibility,
- central retry/compensation logic,
- better for regulated workflows.

Cons:

- coordinator can become complex,
- more central coupling.

### 1.6.3.2 SAGA

A SAGA manages a long-running business transaction across services without a distributed ACID
transaction.

Example:

```text
Submit leave
  -> reserve balance
  -> create approval task
  -> send notification
  -> sync legacy HR
```

If sync legacy HR fails, compensating actions may:

- release balance reservation,
- cancel approval task,
- mark request for manual reconciliation.

SAGA design needs:

- clear state machine,
- idempotent steps,
- compensating actions,
- timeout handling,
- audit trail,
- manual intervention path.

### 1.6.3.3 Event Sourcing

Event sourcing stores changes as a sequence of events rather than only current state.

Use when:

- audit history is central,
- reconstructing past state matters,
- domain changes are naturally event-based,
- temporal analysis is important.

Avoid when:

- team lacks experience,
- query needs are simple,
- event schema evolution is not understood,
- it is being used only because it sounds advanced.

For government audit, event sourcing may be useful in selected domains, but append-only audit
logs are often enough.

### 1.6.3.4 Eventual Consistency

Eventual consistency means different parts of the system may temporarily disagree but converge
later.

Example:

- leave request saved immediately,
- notification sent seconds later,
- reporting projection updated after event processing.

UX must make this clear. Do not show "completed" if downstream sync is still pending.

## 1.6.4 CAP, Idempotency And Delivery Semantics

### 1.6.4.1 CAP

CAP says that during a network partition, a distributed system must choose between consistency
and availability. In interviews, avoid oversimplified "choose two" answers. The practical
question is: what does the system do under partial failure?

Examples:

- Payroll approval may prefer consistency: reject or pause if required checks cannot run.
- Public service-status page may prefer availability: show cached status with warning.
- Notification delivery can be eventually consistent.

### 1.6.4.2 Idempotency

Idempotency is central to safe retries.

Patterns:

- idempotency keys,
- unique business IDs,
- dedupe tables,
- idempotent consumers,
- upserts with constraints,
- state machines that reject invalid repeated transitions.

### 1.6.4.3 Exactly-Once vs At-Least-Once

End-to-end exactly-once is rarely guaranteed across real distributed systems.

Pragmatic design:

- assume messages can be delivered more than once,
- consumers are idempotent,
- side effects use unique keys,
- operations are auditable,
- reconciliation catches mismatches.

Interview answer:

"I design for at-least-once delivery and exactly-once business effect."

## 1.6.5 Caching Strategies

### 1.6.5.1 Cache-Aside

Application checks cache first. On miss, it reads database and writes cache.

Use for:

- reference data,
- service catalogue,
- configuration,
- read-heavy endpoints.

Risks:

- stale data,
- cache stampede,
- inconsistent invalidation,
- security leaks if cache key ignores user/tenant.

### 1.6.5.2 Write-Through

Writes go to cache and database together, often through a caching layer.

Benefits:

- cache stays warm,
- simpler reads.

Risks:

- write latency,
- failure coordination,
- harder operational model.

### 1.6.5.3 Invalidation

Hardest part of caching. Options:

- TTL,
- event-driven invalidation,
- versioned cache keys,
- manual purge,
- write-through updates.

Rules:

- never cache permission-sensitive data without permission in the key,
- define acceptable staleness,
- monitor hit rate and error rate,
- protect against cache stampede with locks or request coalescing.

### 1.6.5.4 Redis Patterns

Redis can be used for:

- cache,
- rate limiting,
- distributed locks with caution,
- session-like temporary state,
- pub/sub for lightweight notifications,
- queue backing in some architectures.

Use caution:

- Redis is not a relational database,
- persistence settings matter,
- eviction policy matters,
- key design matters,
- distributed locks are easy to misuse.

## 1.6.6 Resilience And Disaster Recovery

### 1.6.6.1 RTO And RPO

- **RTO:** Recovery Time Objective - how quickly the service must be restored.
- **RPO:** Recovery Point Objective - how much data loss is acceptable.

Example:

```text
Employee self-service portal:
RTO: 4 hours
RPO: 15 minutes

Payroll approval:
RTO: 1 hour during payroll window
RPO: near-zero
```

Design follows the business target, not the other way around.

### 1.6.6.2 Active-Active vs Active-Passive

| Strategy | Meaning | Pros | Costs |
|---|---|---|---|
| Active-passive | one region active, standby ready | simpler data consistency, lower cost | failover time, standby testing |
| Active-active | multiple regions serve traffic | high availability, lower regional latency | complex data consistency, conflict resolution, cost |

Government systems also need data residency and regulatory constraints in region design.

### 1.6.6.3 Multi-Region

Multi-region readiness requires:

- replicated data strategy,
- identity availability,
- DNS/front-door failover,
- secrets/config replication,
- queue/event strategy,
- runbooks,
- failover tests,
- dependency mapping,
- observability in both regions.

A diagram is not DR. A tested restore is DR.

### 1.6.6.4 Resilience Patterns

- timeouts,
- retries with backoff,
- circuit breakers,
- bulkheads,
- fallback responses,
- queues for async work,
- graceful degradation,
- health checks,
- load shedding.

## 1.6.7 Solution Design Deliverables

### 1.6.7.1 HLD vs LLD

**High-Level Design (HLD):**

- business context,
- system context,
- major components,
- integrations,
- data flows,
- security zones,
- deployment topology,
- NFRs,
- major technology choices,
- risks and assumptions.

**Low-Level Design (LLD):**

- API contracts,
- class/module design,
- database schema,
- sequence diagrams,
- validation rules,
- error handling,
- retry logic,
- detailed configuration,
- deployment scripts,
- operational runbooks.

### 1.6.7.2 Solution Architecture Document Structure

Typical SAD:

1. Purpose and scope.
2. Business goals and drivers.
3. Stakeholders.
4. Current-state architecture.
5. Target architecture.
6. C4/context/container/component diagrams.
7. Integration architecture.
8. Data architecture.
9. Security architecture.
10. Deployment architecture.
11. NFRs.
12. Risks, assumptions, constraints and dependencies.
13. Architecture decisions.
14. Migration and rollout plan.
15. Operations and support model.

### 1.6.7.3 Data Flow Diagrams

DFD Level 0:

- one process,
- external entities,
- major data flows.

DFD Level 1:

- decomposes the main process into major sub-processes.

DFD Level 2:

- decomposes one sub-process into detailed flows.

Use DFDs when the panel cares about data movement, trust boundaries and privacy.

### 1.6.7.4 C4 Model

C4 levels:

- **Context:** system, users, external systems.
- **Container:** applications, databases, queues, gateways.
- **Component:** major internal components inside a container.
- **Code:** classes/modules for selected complex parts.

Strong whiteboard approach:

1. Draw context first.
2. Draw containers second.
3. Zoom into one high-risk component only if asked.

### 1.6.7.5 Sequence Diagrams

Use sequence diagrams for workflows:

- submit leave request,
- approve request,
- webhook delivery,
- legacy sync,
- login/token validation.

Include:

- actors,
- services,
- database,
- queue,
- external systems,
- success path,
- failure/retry path where important.

### 1.6.7.6 ERDs

ERDs show data relationships:

- entities,
- primary keys,
- foreign keys,
- cardinality,
- optional relationships,
- lookup/reference tables.

Use ERDs to validate data ownership, normalization and query design.

### 1.6.7.7 Interface Specification Documents

An interface spec should include:

- purpose,
- owner,
- consumers,
- endpoint/message/file location,
- auth method,
- request schema,
- response schema,
- error codes,
- timeout,
- retry policy,
- idempotency rules,
- rate limits,
- versioning,
- sample payloads,
- data classification,
- audit/logging requirements,
- support contacts,
- SLA/SLO.

### 1.6.7.8 ADRs

Architecture Decision Records capture decisions:

- context,
- decision,
- alternatives considered,
- consequences,
- date,
- status,
- owners.

Example:

```text
ADR-004: Use modular monolith for employee services phase 1
Status: Accepted
Context: one team, evolving domain boundaries, shared transactional workflows
Decision: build modules in one deployable with strict internal boundaries
Consequences: simpler deployment now, extraction possible later if boundaries stabilize
```

### 1.6.7.9 NFR Catalogue

NFRs include:

- availability,
- performance,
- scalability,
- security,
- privacy,
- accessibility,
- auditability,
- maintainability,
- observability,
- data residency,
- recoverability,
- usability,
- interoperability.

Make NFRs measurable:

```text
"Search should be fast" -> weak
"p95 search response under 1.5s for 10,000 concurrent users" -> measurable
```

### 1.6.7.10 TOGAF Awareness

TOGAF is an enterprise architecture framework. You do not need to recite it, but know the
practical point:

- align technology with business capability,
- document current and target architecture,
- manage architecture decisions and governance,
- consider data, application, technology and business architecture.

Interview phrasing:

"I use TOGAF-level thinking where enterprise governance matters, but for delivery teams I
translate it into concrete artifacts: C4 diagrams, ADRs, interface specs, NFRs and roadmaps."

---

# Part C - Whiteboard Answer

If asked "Design an employee services platform," answer in this order:

1. Clarify users, services, data sensitivity, languages, channels, scale and availability.
2. Draw system context: employees, managers, HR, identity, legacy HR, notification, document
   system, payment/payroll if relevant.
3. Draw containers: Next.js frontend, APIM, application service, workflow service, database,
   queue, Redis, integration adapters, observability.
4. State initial architecture: modular monolith or small service set, not many microservices
   until ownership and operational maturity justify it.
5. Explain data ownership and bounded contexts.
6. Show one workflow sequence: submit leave -> validate -> persist -> outbox -> approval task
   -> notify -> sync legacy.
7. Cover security: identity, authorization, audit, data classification, API gateway.
8. Cover NFRs: p95 latency, availability, RTO/RPO, WCAG AA, Arabic/RTL, observability.
9. Cover failure: retries, idempotency, DLQ, reconciliation, manual support path.
10. Name deliverables: HLD, LLD, C4, DFD, ERD, interface specs, ADRs and NFR catalogue.

---

# Part D - Interview Traps

## Trap 1. "Microservices are more modern."

Better answer: microservices are useful when team ownership, deployment independence and
scaling needs justify distributed complexity. For many government systems, a modular monolith
with strong boundaries is safer initially.

## Trap 2. "Event-driven means loosely coupled."

Better answer: events reduce direct calls, but services can still be coupled through event
schemas, ordering assumptions and hidden workflows. Event governance, schema versioning and
observability are required.

## Trap 3. "Exactly-once messaging solves duplicates."

Better answer: end-to-end exactly-once is rarely the practical assumption. I design for
at-least-once delivery and idempotent business effects.

## Trap 4. "Caching is just adding Redis."

Better answer: caching needs ownership, TTL, invalidation, security-aware keys, stampede
protection and observability. Redis is the tool, not the strategy.

## Trap 5. "DR means we have backups."

Better answer: DR means tested restoration against RTO/RPO, failover runbooks, dependency
mapping, monitoring and regular exercises. Backups are only one input.

