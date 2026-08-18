# Part 1.2 - .NET

*Two layers: **Part A** is the build narrative. **Part B** is the complete reference. **Part C**
is the interview pressure test.*

---

# Part A - THE BUILD: .NET In The Platform

## Step 1. The enterprise core needs strong boundaries

The government platform has HR, finance, approvals and notifications. These domains are full
of rules, long-lived records and Microsoft ecosystem integrations. .NET is a strong fit for
this layer because it gives mature web APIs, dependency injection, EF Core, identity
integration, background services, SignalR, Blazor and strong tooling.

For production in 2026, check the official support lifecycle before choosing a target. The JD
mentions **.NET 8/9**; both are still relevant interview topics, while production selection
should normally prefer a supported LTS or organization-standard runtime.

> Reference: [1.2.1 .NET 8/9 API architecture](#121-net-89-api-architecture)

## Step 2. Choose Minimal APIs or Controllers deliberately

The leave-balance read API is small and simple, so Minimal APIs are clean. The approval case
management API has validation, filters, versioning, response conventions and many operations,
so Controllers may be clearer.

> Reference: [1.2.1.1 Minimal APIs vs Controllers](#1211-minimal-apis-vs-controllers)

## Step 3. Keep business rules out of endpoints

We use Clean Architecture ideas: API layer receives requests, application layer handles use
cases, domain layer owns rules, infrastructure layer talks to databases and external systems.

For workflows such as "submit leave request" or "approve exception", CQRS and MediatR can
make request/handler boundaries explicit. But they are tools, not mandatory ceremony.

> Reference: [1.2.1.2 Clean Architecture, CQRS and MediatR](#1212-clean-architecture-cqrs-and-mediatr)

## Step 4. DI lifetime mistakes are production bugs

The first hard-to-find bug appears when a singleton service captures a scoped `DbContext`.
Everything works locally, then concurrent requests leak state or throw disposed-object errors.

> Reference: [1.2.2 Dependency injection lifetimes](#122-dependency-injection-lifetimes)

## Step 5. EF Core must be used with SQL awareness

EF Core is not magic. It tracks entities, generates SQL, manages migrations and supports
performance features, but senior engineers still inspect generated SQL and execution plans.

> Reference: [1.2.3 EF Core](#123-ef-core)

## Step 6. Async is about scalability and cancellation

Government portals call many dependencies. Async prevents threads from being wasted while IO
waits. But async must carry cancellation tokens, avoid sync-over-async deadlocks, and use
`ValueTask` only where measurement justifies it.

> Reference: [1.2.4 Async/await in .NET](#124-asyncawait-in-net)

## Step 7. Real-time updates need SignalR, not polling

Approvers should see a new request arrive without refreshing. Employees should see approval
status change. SignalR gives real-time channels over WebSockets with fallbacks.

> Reference: [1.2.8 SignalR](#128-signalr)

## Step 8. Aspire and Dapr need justification

The platform may use Aspire for local orchestration, service defaults and cloud-native .NET
composition. It may use Dapr for sidecar-based service invocation, pub/sub, state and secrets
across polyglot services. Neither should be added just to sound modern.

> Reference: [1.2.9 .NET Aspire and Dapr](#129-net-aspire-and-dapr)

---

# Part B - THE REFERENCE

## 1.2.1 .NET 8/9 API Architecture

Modern ASP.NET Core is built around:

- dependency injection,
- middleware pipeline,
- endpoint routing,
- model binding,
- validation,
- filters,
- logging,
- configuration,
- hosted services,
- OpenAPI integration.

In interviews, be careful with version statements. .NET releases and support dates change.
Say: "I would verify the current lifecycle and target the organization's supported runtime.
For the design discussion, the important points are ASP.NET Core, DI, EF Core, async,
observability and deployment strategy."

### 1.2.1.1 Minimal APIs vs Controllers

| Option | Best fit | Strengths | Tradeoffs |
|---|---|---|---|
| Minimal APIs | small APIs, internal services, simple endpoints, gateway-style services | low ceremony, clear route definitions, fast to build | can become scattered if the API grows without grouping |
| Controllers | large domain APIs, versioned APIs, complex filters/model validation, conventional teams | familiar MVC structure, filters, action conventions, good organization | more ceremony |

Good answer:

- Minimal APIs are not "toy APIs"; they are production-capable.
- Controllers are not obsolete; they are still useful for complex APIs.
- I choose based on complexity, team convention, API size, cross-cutting needs and maintainability.

### 1.2.1.2 Clean Architecture, CQRS And MediatR

Typical layers:

```text
Web/API
  -> Application use cases
  -> Domain model and rules
  -> Infrastructure: EF Core, HTTP clients, queues, file storage
```

**Clean Architecture** protects the domain/application logic from framework and database
details. The rule is dependency direction: inner layers should not depend on outer layers.

**CQRS** separates commands that change state from queries that read state:

- Command: `SubmitLeaveRequestCommand`
- Query: `GetLeaveBalanceQuery`

CQRS is useful when:

- writes have complex validation and side effects,
- reads need different optimized models,
- audit and workflow are important,
- permissions differ between read and write operations.

CQRS can be overkill when CRUD is simple.

**MediatR** is an in-process mediator library often used to implement command/query handlers.
It can add clean boundaries and pipeline behaviors, but excessive handler indirection can make
simple code harder to navigate.

Senior answer: "I would use CQRS/MediatR where it clarifies use cases and cross-cutting
behaviors, not as a blanket rule for every endpoint."

## 1.2.2 Dependency Injection Lifetimes

ASP.NET Core DI has three common lifetimes:

| Lifetime | Meaning | Common use |
|---|---|---|
| Singleton | one instance for the application lifetime | stateless services, configuration, caches, clients designed for reuse |
| Scoped | one instance per request scope | `DbContext`, unit-of-work services, current-user context |
| Transient | new instance each time requested | lightweight stateless services |

### Captive Dependency Bug

A captive dependency happens when a longer-lived service captures a shorter-lived service.

Bad:

```csharp
services.AddDbContext<AppDbContext>();       // scoped
services.AddSingleton<ReportCache>();        // singleton captures DbContext
```

Why it is bad:

- the singleton may use a disposed scoped object,
- request-specific state can leak,
- concurrency issues appear under load,
- `DbContext` is not intended as an application-wide singleton.

Fix:

- change lifetime to scoped if the service needs scoped dependencies,
- use `IServiceScopeFactory` carefully for background services,
- pass data into singleton methods instead of scoped services,
- use factories for short-lived resources.

Interview phrasing:

"A singleton can depend on another singleton. A scoped service can depend on scoped or
singleton. A transient can depend on anything, but if a singleton captures a transient with
state, it can effectively make it singleton. The dangerous case is longer-lived services
holding shorter-lived dependencies."

## 1.2.3 EF Core

EF Core is the default ORM for many .NET applications. Senior-level EF Core means knowing when
tracking helps, when it hurts, and how queries translate to SQL.

### 1.2.3.1 Change Tracking

EF Core tracks entity instances returned by tracking queries. It detects changes and writes
them during `SaveChangesAsync()`.

Useful for:

- update workflows,
- aggregate modifications,
- domain logic that changes multiple properties,
- unit-of-work patterns.

Cost:

- memory overhead,
- identity resolution overhead,
- unexpected updates if entities are modified accidentally.

### 1.2.3.2 `AsNoTracking`

Use `AsNoTracking()` for read-only queries:

```csharp
var employees = await db.Employees
    .AsNoTracking()
    .Where(e => e.DepartmentId == departmentId)
    .ToListAsync(cancellationToken);
```

Benefits:

- less memory,
- faster read queries,
- avoids accidental updates.

Do not use it when you intend to update the entity directly.

### 1.2.3.3 Migrations

EF Core migrations track schema changes. Production discipline:

- review generated migration SQL,
- separate schema migration from risky data migration,
- test rollback or forward-fix plans,
- avoid table-locking operations during peak hours,
- coordinate with zero-downtime deployment strategy.

### 1.2.3.4 Compiled Queries

Compiled queries can reduce query translation overhead on hot paths:

```csharp
private static readonly Func<AppDbContext, string, Task<Employee?>> GetEmployeeByNumber =
    EF.CompileAsyncQuery((AppDbContext db, string employeeNo) =>
        db.Employees.SingleOrDefault(e => e.EmployeeNo == employeeNo));
```

Use only after measuring. Database IO often dominates; compiled queries do not fix bad
indexes, poor query shapes or large result sets.

### 1.2.3.5 Split Queries

Large include graphs can create cartesian explosions. Split queries load related collections
using multiple SQL queries instead of one huge join.

Use split queries when:

- multiple collections are included,
- result duplication is high,
- one joined query creates too many rows.

Be aware:

- multiple queries can have consistency implications,
- additional round trips may matter,
- always measure with realistic data.

### 1.2.3.6 EF Core Performance Checklist

- Use projections for read models instead of loading full entities.
- Use `AsNoTracking()` for read-only paths.
- Avoid N+1 by inspecting generated SQL.
- Use indexes that match filters and sort order.
- Avoid unbounded `Include()` chains.
- Paginate large results.
- Use bulk operations carefully where supported.
- Add query tags for tracing high-risk queries.

## 1.2.4 Async/Await In .NET

### 1.2.4.1 Task vs ValueTask

`Task<T>` is the normal async return type.

`ValueTask<T>` can reduce allocations when a result is often already available synchronously,
but it adds complexity and misuse risks. Use it only for high-throughput measured paths or APIs
where it is already idiomatic.

### 1.2.4.2 ConfigureAwait

In ASP.NET Core, there is no classic ASP.NET synchronization context, so `ConfigureAwait(false)`
is less critical than it was in older app models. In reusable libraries, it can still be used
to avoid capturing context.

Panel answer: know the history, but do not cargo-cult it.

### 1.2.4.3 Deadlocks

Classic deadlocks come from sync-over-async:

```csharp
var result = SomeAsyncCall().Result;
```

or:

```csharp
SomeAsyncCall().Wait();
```

Avoid blocking on async. Make the call chain async all the way and `await` tasks.

### 1.2.4.4 Cancellation Tokens

Every external call and database call should receive a cancellation token where possible:

```csharp
app.MapGet("/employees/{id}", async (
    string id,
    AppDbContext db,
    CancellationToken cancellationToken) =>
{
    return await db.Employees
        .AsNoTracking()
        .SingleOrDefaultAsync(e => e.EmployeeNo == id, cancellationToken);
});
```

Why it matters:

- client disconnected,
- request timeout,
- deployment shutdown,
- upstream workflow cancellation,
- protecting resources under load.

## 1.2.5 Middleware, Filters, Model Binding And Validation

### Middleware Pipeline

Middleware runs in order and wraps the request:

```text
Exception handling
  -> HTTPS/security headers
  -> routing
  -> authentication
  -> authorization
  -> endpoints
```

Ordering matters. Authentication must run before authorization. Exception handling should be
early enough to catch downstream failures.

### Filters

Filters apply around controller actions:

- authorization filters,
- resource filters,
- action filters,
- exception filters,
- result filters.

Use middleware for broad pipeline concerns. Use filters for MVC/controller-specific concerns.

### Model Binding

Model binding maps route values, query strings, headers and bodies into parameters or models.
Be explicit about where data comes from when ambiguity is risky.

### Validation

Use:

- data annotations for basic rules,
- FluentValidation or custom validators for richer rules where standard,
- domain validation for business invariants.

Do not rely only on UI validation.

## 1.2.6 Performance

### Span<T>

`Span<T>` and `ReadOnlySpan<T>` provide allocation-friendly views over contiguous memory. They
are useful in parsing, serialization and high-performance libraries.

Do not introduce them into normal business code unless profiling shows allocations matter.

### Memory Pooling

Pools reduce allocations for frequently reused buffers. Common tools include `ArrayPool<T>` and
pooled serializers/clients.

Risks:

- returning buffers late,
- leaking sensitive data in reused buffers,
- making code more complex without measurable benefit.

### GC Modes

Know the high-level distinction:

- workstation GC: optimized for client apps,
- server GC: optimized for throughput on server workloads,
- low-latency modes: useful for specific pause-sensitive scenarios.

Do not tune GC blindly. Use metrics and profiling.

### Benchmarking

Use BenchmarkDotNet for microbenchmarks, but remember:

- microbenchmarks do not replace production telemetry,
- test realistic payload sizes,
- avoid optimizing code paths that are not hot,
- database/network latency often dominates application code.

## 1.2.7 Blazor

| Model | Best fit | Strengths | Risks |
|---|---|---|---|
| Blazor Server | intranet apps, controlled networks, fast initial load, central execution | small client download, server-side access, good for internal admin | needs persistent SignalR connection; server resource use grows with users |
| Blazor WebAssembly | richer client-side apps, offline-ish behavior, public apps where server connection should not hold UI state | runs in browser, can use static hosting | larger download, browser resource limits, API security still required |

Government intranet answer:

"For internal admin tools on reliable networks, Blazor Server can be very productive. For
public-facing high-scale sites, I would be more cautious and compare download size,
accessibility, SEO, CDN behavior and operational profile against React/Next.js or MVC."

## 1.2.8 SignalR

SignalR provides real-time communication:

- WebSockets when available,
- fallbacks where necessary,
- hubs for server/client methods,
- groups for targeted messages,
- scale-out through backplanes or managed services.

Use cases:

- approval notifications,
- dashboard updates,
- chat/support,
- document processing progress,
- operational alerts.

Design points:

- authorize hub connections,
- use groups based on permissions,
- do not send sensitive data to broad groups,
- handle reconnects,
- make messages idempotent if clients can receive duplicates,
- do not use SignalR as the system of record.

## 1.2.9 .NET Aspire And Dapr

### .NET Aspire

Aspire is useful for composing cloud-native .NET applications:

- local orchestration,
- service discovery patterns,
- telemetry defaults,
- health checks,
- configuration and resource modeling.

Use it when the platform has multiple .NET services and the team wants consistent local
developer experience and operational defaults.

### Dapr

Dapr is a sidecar-based runtime for distributed applications:

- service invocation,
- pub/sub,
- state stores,
- secrets,
- bindings,
- actor model.

Use it when:

- services are polyglot,
- infrastructure abstraction is valuable,
- pub/sub and state patterns repeat across services,
- sidecar operations are acceptable to the platform team.

Avoid it when:

- the app is a simple monolith,
- the team cannot operate sidecars,
- direct cloud SDK usage is clearer,
- abstraction hides important provider-specific behavior.

Senior comparison:

- Aspire improves the .NET developer and app composition experience.
- Dapr abstracts distributed system building blocks across languages.
- They can complement each other, but neither removes the need for clear boundaries,
  observability, security and failure design.

---

# Part C - Interview Traps

## Trap 1. "Should every new .NET API use Minimal APIs?"

No. Minimal APIs are excellent for small, focused APIs and can be production-grade. Controllers
are still valuable for complex, versioned, convention-heavy APIs. The decision should follow
API complexity and team maintainability.

## Trap 2. "Why is injecting DbContext into a singleton bad?"

`DbContext` is normally scoped to a request/unit of work. A singleton holding it can use a
disposed context, leak request state or create concurrency bugs. The fix is to align lifetimes,
use a scope factory carefully in hosted services, or change the design.

## Trap 3. "When would you use AsNoTracking?"

For read-only queries where I do not plan to modify the entity. It reduces tracking overhead
and avoids accidental updates. I would not use it for aggregate update workflows that rely on
change tracking.

## Trap 4. "Is ValueTask always faster?"

No. `ValueTask` can avoid allocations in specific hot paths where results often complete
synchronously, but it adds complexity. `Task` is the default. I use `ValueTask` only after
measurement or when implementing an API that expects it.

## Trap 5. "Should we add Dapr?"

Only if the distributed building blocks and polyglot abstraction are worth the operational
cost. For a simple modular monolith or small .NET-only service set, direct platform services
and Aspire may be simpler.

