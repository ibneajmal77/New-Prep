# Part 1 - Application Engineering: Interview Questions And Model Answers

Use this after files `11` through `17`. Practise the answers aloud. The goal is not to memorize
exact wording; it is to build a reliable structure under pressure.

---

# 1.1 Python

## Q1. Why would you choose FastAPI for an internal government API?

I would choose FastAPI for an API-first service where typed request/response contracts,
OpenAPI generation, dependency injection and async IO support matter. It is especially useful
for services that sit near data, automation or AI. I would still check team experience and
operational standards; if the system needs a built-in admin and lots of conventional CRUD,
Django may be a better fit.

## Q2. Explain FastAPI dependency injection.

FastAPI dependencies are declared callables that provide request-scoped resources or checks:
current user, DB session, settings, permission checks, clients. A dependency can use `yield`
for setup/teardown, which is useful for closing sessions. The benefit is that endpoints stay
thin and tests can override dependencies cleanly.

## Q3. What changed conceptually in Pydantic v2?

The important point is explicit validation and serialization. `BaseModel` still defines data
models, but validators, `model_dump()`, stricter config and attribute-based serialization are
more deliberate. I use Pydantic at the boundary for shape and type validation, then keep
business invariants in the domain/service layer.

## Q4. When does async improve a Python API?

Async improves throughput when the request spends time waiting on IO and the libraries are
non-blocking: HTTP calls, async DB drivers, cache calls, message publishing. It does not make
CPU-heavy work faster. If I call blocking libraries like `requests` or run heavy Pandas work
inside `async def`, I can block the event loop and hurt all concurrent requests.

## Q5. What is the difference between `asyncio.gather` and a normal loop?

`gather` schedules independent awaitables concurrently and returns results in input order. It
is useful for independent IO calls, like fetching employee profile, balance and approvals at
the same time. I would add timeouts, handle cancellation and bound concurrency for large lists.

## Q6. FastAPI BackgroundTasks or Celery?

FastAPI `BackgroundTasks` is for small best-effort work after the response, such as a simple
notification or lightweight audit side effect. It is not durable. For business workflows,
imports, reports, retries or anything that must survive process restart, I would use Celery or
a proper queue with idempotency, retry policy, DLQ and monitoring.

## Q7. How do you avoid duplicate effects in Celery jobs?

Use idempotency. Store a request ID or idempotency key, use unique constraints, process by
state transitions, and make retries return the existing result instead of repeating the side
effect. For integration events, I often combine an outbox table with idempotent consumers.

## Q8. What is the SQLAlchemy 2.0 session lifecycle in a web app?

Open one session per request or unit of work, use it for queries and changes, commit once when
the use case succeeds, roll back on failure, and close it in `finally`. Avoid global sessions
and lazy-loading objects after the session is closed. Use explicit `select()` queries and
loader strategies to control SQL.

## Q9. What is the N+1 problem?

N+1 happens when I load N parent rows and then lazily load a relationship once per row. It
looks harmless in code but becomes many database queries. I fix it with `selectinload`,
`joinedload`, explicit joins, projections, and query-count tests on critical endpoints.

## Q10. Explain GIL, threading, async and multiprocessing.

In CPython, the GIL means one thread executes Python bytecode at a time. Threads and async are
still useful for IO because the program is mostly waiting. For CPU-bound Python code,
multiprocessing or native/vectorized libraries are better. For long business work, a queue is
usually better than doing it inside a request.

## Q11. How would you process a large HR Excel/CSV file in Python?

I would read only needed columns, define dtypes, process in chunks if the file is large,
validate rows into a quarantine/report process, avoid row-by-row loops, use vectorized Pandas
operations and make the import idempotent. For production I would also track file checksum,
schema version, processed status and reconciliation totals.

---

# 1.2 .NET

## Q12. Minimal APIs or Controllers?

Minimal APIs are great for small, focused APIs and can absolutely be production-grade.
Controllers are better when the API is large, versioned, convention-heavy, and uses filters or
complex model validation. I choose based on maintainability and team convention, not fashion.

## Q13. Explain Clean Architecture in a .NET API.

The API layer handles HTTP, the application layer handles use cases, the domain layer owns
business rules, and infrastructure handles EF Core, queues and external systems. The key rule
is dependency direction: domain/application should not depend on framework/database details.

## Q14. When would you use CQRS and MediatR?

CQRS is useful when commands and queries have different complexity, permissions or models.
MediatR can make request/handler boundaries and pipeline behaviors explicit. I would use them
where they clarify business use cases, not for every simple CRUD endpoint by default.

## Q15. Explain singleton, scoped and transient DI lifetimes.

Singleton lives for the application lifetime, scoped normally lives for one request, and
transient is created whenever requested. The classic bug is a singleton capturing a scoped
dependency like `DbContext`, causing disposed-object errors, state leaks or concurrency issues.

## Q16. When do you use EF Core `AsNoTracking`?

For read-only queries where I do not plan to update the entity. It reduces memory and tracking
overhead and avoids accidental updates. For update workflows, I usually keep tracking because
the unit of work needs change detection.

## Q17. What are split queries in EF Core?

Split queries load related collections using multiple SQL queries instead of one large join.
They help avoid cartesian explosion when including multiple collections. I still measure,
because split queries add round trips and can have consistency implications.

## Q18. Task vs ValueTask?

`Task` is the default async return type. `ValueTask` can reduce allocations when results often
complete synchronously, but it is more complex and should be used only on measured hot paths or
when implementing APIs that expect it.

## Q19. Why are cancellation tokens important?

They let work stop when the client disconnects, a timeout is hit, or the service is shutting
down. I pass cancellation tokens into database calls, HTTP calls and long-running operations so
the system does not waste resources.

## Q20. Blazor Server or WASM for government intranet?

Blazor Server can be strong for internal admin apps on reliable networks because the client is
light and the app runs centrally, but it needs persistent SignalR connections and server
resources per user. WASM is more client-side and avoids a constant server circuit, but has
larger downloads. I would compare scale, network, accessibility, SEO and operations.

## Q21. Aspire vs Dapr?

Aspire helps compose and observe cloud-native .NET apps with strong local developer experience
and service defaults. Dapr provides sidecar-based building blocks like service invocation,
pub/sub, state and secrets across languages. I would use either only when the benefits justify
the operational model.

---

# 1.3 Node.js

## Q22. Why NestJS instead of Express?

NestJS gives structure: modules, DI, controllers, providers, guards, interceptors and pipes.
That is useful for a larger TypeScript service owned by a team. Express is simpler and good for
small services, but larger Express apps need discipline to avoid inconsistent structure.

## Q23. Express vs Fastify vs NestJS?

Express is minimal and widely known. Fastify is performance-oriented with strong schema/plugin
patterns. NestJS is best when enterprise structure and testability matter. The choice depends
on team size, performance needs, maintainability and ecosystem requirements.

## Q24. Explain the Node.js event loop.

Node runs JavaScript callbacks on a main thread and uses the event loop to process ready work.
IO can be concurrent through OS/libuv facilities, but CPU-heavy JavaScript blocks the event
loop. That is why Node is excellent for IO-heavy services but needs worker threads or separate
processes for CPU-heavy work.

## Q25. What is libuv?

libuv is the cross-platform library behind Node's event loop and async IO abstractions. It
handles timers, async network integration, filesystem operations and a threadpool for some
operations. Knowing libuv helps explain why some "async" operations still use threads.

## Q26. What are streams and backpressure?

Streams process data in chunks instead of loading everything into memory. Backpressure is how
a slow consumer tells a fast producer to slow down. For large files, uploads or SFTP imports,
streams are a reliability requirement, not just a performance optimization.

## Q27. What npm security controls do you expect in CI?

Deterministic installs with a lockfile, `npm ci`, dependency scanning, vulnerability triage,
SBOM generation, secrets scanning, pinned Node/package-manager versions, and review of high
risk package changes. `npm audit` is useful, but it is only one control.

---

# 1.4 Frontend

## Q28. What are React Server Components?

Server Components render on the server and do not ship their component code to the browser.
They are useful for server-side data access, reducing client JavaScript and rendering stable
page structure. Client components are still needed for event handlers, browser APIs and local
interactive state.

## Q29. What does concurrent rendering mean?

It means React can interrupt, pause and prioritize rendering work to keep the UI responsive. It
does not mean my application JavaScript is running in parallel threads.

## Q30. When should you use `useMemo` and `useCallback`?

When profiling or component behavior shows a real need: expensive computation, stable
references for memoized children, or dependency-sensitive hooks. I do not use them everywhere
because unnecessary memoization makes code harder to read and can add overhead.

## Q31. Redux Toolkit, React Query, RTK Query or Context?

I classify the state first. Server state belongs in React Query or RTK Query. Complex shared
client workflow state may belong in Redux Toolkit. Stable app-wide values like locale/theme can
use Context. Local UI state should stay local.

## Q32. Explain Next.js SSR, SSG and ISR.

SSR renders at request time and fits user-specific authenticated pages. SSG pre-renders static
content. ISR lets static content be regenerated periodically or on demand. In a government
portal, user-specific dashboards usually need SSR/server components, while public service
catalogues may use SSG or ISR.

## Q33. What changed in Next.js 15 caching mindset?

The practical point is that caching is more explicit. I do not assume data is cached by
default; I define cache behavior based on whether data is public or user-specific, how stale it
can be, which layer owns invalidation and whether authorization affects the result.

## Q34. Why not micro-frontends?

Micro-frontends help when multiple teams need independent ownership and deployment. They also
add runtime integration, dependency governance, routing, auth propagation, observability,
design-system and accessibility complexity. A modular monolith SPA is often better until the
organizational need is real.

## Q35. What does WCAG AA mean in practice?

It means the system must be perceivable, operable, understandable and robust. Practically: real
keyboard access, focus indicators, semantic HTML, labels, error messages, contrast, screen
reader support, no color-only meaning, language attributes and testing with both automation
and assistive technologies.

## Q36. How do you design Arabic/RTL UI properly?

Set `lang` and `dir`, use logical CSS properties, test mixed Arabic/English text, mirror only
directional icons, choose Arabic-capable fonts, localize validation/messages, format dates and
numbers by locale, and consider Hijri calendar requirements. RTL is not just `text-align:
right`.

---

# 1.5 API Design And Integration

## Q37. What makes a good REST API?

A good REST-style API models resources clearly, uses HTTP methods and status codes
consistently, supports pagination/filtering/versioning, has idempotency for risky writes, and
does not expose database tables directly as the contract.

## Q38. How do you design idempotent POST?

Use an idempotency key. Store the key, request hash and result. If the same key is retried,
return the original result rather than repeating the side effect. This is critical for
approvals, payments, workflow submissions and external integrations.

## Q39. Contract-first OpenAPI or code-first?

For vendor and multi-team integration, I prefer contract-first because the API can be reviewed,
mocked, tested and generated before implementation. Code-first can be fine for smaller internal
APIs, but the contract still needs governance and breaking-change detection.

## Q40. What does Pact add beyond schema validation?

Schema validation checks shape. Pact verifies consumer-provider interactions: what the consumer
actually expects and what the provider actually supports. It is valuable when services are
owned and deployed independently.

## Q41. When would you use GraphQL?

For flexible read composition where clients need different shapes of related data. I would be
cautious with commands, public abuse surface, authorization, N+1 resolver behavior and query
cost. I would use DataLoader, depth/complexity limits and persisted queries.

## Q42. When is gRPC wrong?

It can be wrong for public/browser/vendor APIs where JSON/HTTP simplicity, debugging and
intermediary compatibility matter. gRPC is strong for internal strongly typed service calls and
streaming, but not automatically better than REST.

## Q43. Explain the outbox pattern.

Write the business change and the outgoing event into the same database transaction. A separate
publisher reads the outbox and sends the message, marking it sent after success. This prevents
the failure where the database changes but the event is never published.

## Q44. What is a proper legacy SFTP integration design?

Define file naming, schema version, checksum, encryption, atomic upload, processed/archive/error
folders, idempotent import, validation report, reconciliation totals, alerting for missing
files and a manual replay process.

## Q45. What does Azure API Management add?

APIM gives API governance at the edge: products, subscriptions, policies, JWT validation,
rate limits, quotas, transformation, backend routing, caching and self-hosted gateway for
private/on-prem scenarios. Backends still enforce business authorization.

---

# 1.6 Architecture And Solution Design

## Q46. Microservices or modular monolith?

I would start with business boundaries and team ownership. In many government contexts, a
modular monolith with strict internal boundaries is safer because domains are still evolving
and operations maturity may not justify distributed complexity. Extract services when
independent scaling, deployment or ownership becomes real.

## Q47. What is a bounded context?

A bounded context is where a domain model has a specific meaning. "Request" may mean leave
request in HR, document request in document services and procurement request in finance. DDD
prevents one confused universal model from spreading across all domains.

## Q48. Choreography or orchestration?

Choreography lets services react to events independently and is loosely coupled, but workflows
can become hard to understand. Orchestration uses a coordinator and is clearer for regulated,
long-running workflows with approvals, compensation and audit. I choose based on process
visibility and control needs.

## Q49. What is a SAGA?

A SAGA coordinates a long-running business transaction across services without a distributed
ACID transaction. It uses steps, state, idempotency and compensating actions. For example, if
legacy HR sync fails after reserving leave balance, the saga may release the reservation and
send the request to manual reconciliation.

## Q50. Explain CAP without the slogan.

The practical CAP question is what the system does during partial failure. For payroll, I may
prefer consistency and pause the operation. For a public status page, I may serve cached data
with a warning. The choice is per workflow, not a generic technology label.

## Q51. Exactly-once or at-least-once?

Across distributed systems I assume at-least-once delivery and design idempotent consumers so
the business effect happens once. That is more realistic than promising exactly-once end to
end.

## Q52. What makes caching dangerous?

Stale data, wrong invalidation, cache stampede and security leaks. If the cache key ignores
tenant/user permissions, one user can receive another user's data. Every cache needs an owner,
TTL, invalidation strategy and observability.

## Q53. RTO vs RPO?

RTO is how quickly we must restore service. RPO is how much data loss is acceptable. They are
business targets that drive architecture: replication, backups, failover, restore testing and
manual process design.

## Q54. What goes into a solution architecture document?

Purpose, scope, business drivers, stakeholders, current and target architecture, C4 diagrams,
integrations, data architecture, security, deployment topology, NFRs, risks, assumptions,
constraints, ADRs, migration plan and operations/support model.

## Q55. HLD vs LLD?

HLD explains the system at component, integration, data-flow, security and deployment level.
LLD goes into APIs, classes/modules, schema, sequence diagrams, validation rules, retries,
configuration and operational details.

## Q56. What is an ADR?

An Architecture Decision Record captures context, decision, alternatives, consequences, date,
status and owner. It keeps important design decisions auditable and prevents the team from
re-litigating choices without context.

---

# 1.7 Databases And SQL

## Q57. How do you tune a slow SQL query?

Capture the real query and parameters, inspect the actual execution plan, compare estimated
and actual rows, check indexes/statistics, reduce selected columns, rewrite poor predicates,
paginate, test with production-like data and measure before/after.

## Q58. Clustered vs non-clustered index?

In SQL Server, a clustered index defines the table's row order structure, while non-clustered
indexes are separate structures pointing to rows. PostgreSQL is heap-organized by default, so
I avoid assuming SQL Server index terminology applies everywhere.

## Q59. What is a covering index?

An index that contains all columns needed by a query, either as key columns or included
columns. It can avoid extra lookups, but increases storage and write cost. I use it for hot,
stable query shapes.

## Q60. What is parameter sniffing?

SQL Server optimizes a plan based on parameter values it sees and may reuse that plan for
different values. That is usually good, but with skewed data one plan can be terrible for
another parameter. Fixes include better indexes, updated stats, recompile, optimizing for
specific/unknown values or splitting query paths.

## Q61. How do you handle deadlocks?

Find the deadlock graph, identify the lock order and statements, then fix transaction design:
consistent table access order, shorter transactions, proper indexes, less work inside the
transaction and safe retries for deadlock victims.

## Q62. Normalization or denormalization?

Normalize the transactional write model for correctness and constraints. Denormalize
deliberately for read models, dashboards, reporting and search when performance requires it,
with clear refresh and ownership rules.

## Q63. Partitioning or sharding?

Partitioning splits one logical table inside the database, often by date or tenant, and helps
maintenance and pruning. Sharding splits data across databases or servers and adds major
operational complexity. I would consider partitioning, indexing, read replicas and read models
before sharding.

## Q64. HNSW vs IVFFlat in pgvector?

Both are approximate vector index options. HNSW usually gives strong recall/speed without a
training step but uses more memory. IVFFlat partitions vectors into lists and needs
representative data; probe count affects recall and latency. I choose based on data size,
recall target, latency and operational cost.

## Q65. How do you do zero-downtime schema changes?

Use expand/contract. Add backward-compatible schema first, deploy code that can read/write the
new structure, backfill idempotently, verify, then remove old schema later. Avoid risky locks,
use online operations where supported, and make rollback or forward-fix realistic.

