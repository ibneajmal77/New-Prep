# Part 1 - Application Engineering: The Map

*Read this file first. It is the index, the architecture, and the study order for files
11-17. Use file 18 after the reference files to practise spoken interview answers.*

---

## 1. How This Material Is Organised

Eight files. **File order = learning order**, while your original section numbers stay inside
the files.

| File | Section | What it adds to the system |
|---|---|---|
| `11-Part1-Python.md` | 1.1 | Service APIs, validation, async work, jobs, data scripts |
| `12-Part1-DotNet.md` | 1.2 | Enterprise application layer, EF Core, SignalR, Aspire/Dapr |
| `13-Part1-Node.md` | 1.3 | Integration edge services, NestJS, streams, supply-chain controls |
| `14-Part1-Frontend-React-Web.md` | 1.4 | React/Next.js portal, accessibility, Arabic/RTL |
| `15-Part1-API-Integration.md` | 1.5 | API contracts, APIM, webhooks, GraphQL, gRPC, legacy systems |
| `16-Part1-Architecture-Solution-Design.md` | 1.6 | System design, DDD, events, DR, architecture deliverables |
| `17-Part1-Databases-SQL.md` | 1.7 | SQL tuning, indexing, PostgreSQL, SQL Server, pgvector, migrations |
| `18-Part1-Interview-Questions-Model-Answers.md` | Drill | Tough panel questions and model spoken answers |

Every reference file has the same structure:

1. **Part A - The Build:** one realistic government platform built step by step.
2. **Part B - The Reference:** complete coverage of every bullet in your outline.
3. **Part C - Interview Traps:** the questions that usually separate senior answers from
   keyword-level answers.

### The System Being Built

We are building a **bilingual UAE government employee-services platform**:

- Employees use a React/Next.js portal in Arabic and English.
- APIs expose leave, letters, benefits, approvals, notifications, documents and search.
- Back-end services are a pragmatic mix of Python, .NET and Node.js.
- Some systems are modern APIs; others are SOAP services, SFTP file drops and an ESB.
- Data lives in SQL Server and PostgreSQL, with Redis for caching and queues for async work.
- The platform must be accessible, auditable, secure, resilient, and support future AI/RAG
  services from Part 8.

That one system touches every topic from 1.1 to 1.7.

---

## 2. Master Architecture

Use this as the mental map for whiteboard questions. If the panel asks about any technology,
place it on this architecture first, then discuss tradeoffs.

```text
                              USERS
        Arabic / English portal, mobile web, internal admin, partner systems
                                      |
                                      v
+--------------------------- FRONTEND LAYER ----------------------------+
| Next.js App Router, React 19, SSR/SSG/ISR, accessibility, RTL, i18n   |
| State: React Query/RTK Query for server state, local state for UI      |
+----------------------------------+------------------------------------+
                                   |
                                   v
+------------------------- API EDGE / GOVERNANCE -----------------------+
| Azure API Management: products, subscriptions, JWT validation,         |
| rate limits, policies, backend pools, self-hosted gateway              |
| OpenAPI contracts, versioning, throttling, logging                     |
+----------------+-----------------------+------------------------------+
                 |                       |
                 v                       v
+------------------------- APPLICATION SERVICES ------------------------+
| Python/FastAPI                 | .NET 8/9                      | Node |
| Pydantic v2 validation         | Minimal APIs/Controllers      | Nest |
| SQLAlchemy 2.0                 | Clean Architecture/CQRS       | Fast |
| Celery/jobs/data scripts       | EF Core/SignalR/Blazor        | API |
| async IO where useful          | Aspire/Dapr where justified   | edge |
+----------------+-----------------------+------------------------------+
                 |                       |
                 v                       v
+------------------------ INTEGRATION / ASYNC LAYER --------------------+
| Webhooks, queues, outbox, retries, idempotency keys, DLQs,             |
| SOAP adapters, file drops, SFTP, ESB integration, circuit breakers     |
+----------------+-----------------------+------------------------------+
                 |                       |
                 v                       v
+----------------------------- DATA LAYER ------------------------------+
| SQL Server: T-SQL, indexing, execution plans, isolation, deadlocks     |
| PostgreSQL: partitioning, pgvector, HNSW/IVFFlat, JSONB where useful   |
| Redis: cache-aside, rate limits, distributed locks where justified     |
+----------------+-----------------------+------------------------------+
                 |                       |
                 v                       v
+----------------------- OPERATIONS / ARCHITECTURE ---------------------+
| C4, HLD/LLD, DFD, ERD, interface specs, ADRs, NFRs, TOGAF awareness   |
| Observability, RTO/RPO, DR, blue/green releases, zero-downtime schema |
+-----------------------------------------------------------------------+
```

### The Senior-Level Story

For a government entity, the strong answer is rarely "use the newest framework." It is:

- Start with a **modular monolith or small number of services** until team boundaries,
  deployment independence and data ownership justify microservices.
- Put **Azure API Management** at the edge for policy enforcement, subscription control,
  identity validation and legacy shielding.
- Use **contract-first APIs** for integrations where multiple teams or vendors depend on the
  contract.
- Keep **data ownership explicit**: one service owns writes to one bounded context; other
  contexts consume events or APIs.
- Treat **Arabic/RTL, WCAG AA and auditability** as first-class requirements, not UI polish.
- Design for **failure**: retries, idempotency, timeouts, DLQs, backpressure, RTO/RPO.
- Prove decisions with **architecture artifacts**: C4, sequence diagrams, ERDs, interface
  specs, ADRs and NFR catalogues.

---

## 3. Study Order

1. Start with `11-Part1-Python.md` because Python appears first in the JD and will likely be
   used for APIs, automation, data preparation, AI integration and internal tooling.
2. Study `12-Part1-DotNet.md` next because many government and enterprise systems rely on
   .NET, SQL Server and Microsoft identity.
3. Use `13-Part1-Node.md` for NestJS, integration gateways and event-loop depth.
4. Move to `14-Part1-Frontend-React-Web.md` because Arabic/RTL and accessibility are likely
   high-value interview differentiators.
5. Study `15-Part1-API-Integration.md` before architecture because most design discussions
   become API and integration discussions.
6. Study `16-Part1-Architecture-Solution-Design.md` as the whiteboard layer.
7. Finish with `17-Part1-Databases-SQL.md`, then practise aloud with `18-Part1-Interview-Questions-Model-Answers.md`.

---

## 4. The 200 Percent Coverage Checklist

These are the topics from your outline that a panel can drill into hardest:

| Area | Must be able to explain |
|---|---|
| Python async | Why async improves IO concurrency but does not make CPU work faster; blocking-call failure modes |
| FastAPI | Dependency injection, Pydantic v2 validation, lifespan, middleware and background task limits |
| Jobs | Retries, idempotency, Celery workers, poison messages and DLQs |
| SQLAlchemy | Session per unit of work, loader strategies, N+1 avoidance |
| .NET DI | Singleton/scoped/transient, captive dependencies and request-scoped services |
| EF Core | Tracking vs no-tracking, split queries, compiled queries, migrations |
| Node | Event loop phases, libuv threadpool, worker threads, streams and backpressure |
| Frontend | React 19, Next.js 15 caching, hydration cost, server state vs client state |
| Accessibility | WCAG AA, POUR, keyboard nav, screen readers, ARIA only when semantic HTML is insufficient |
| Arabic/RTL | `dir`, logical CSS, mirrored icons, fonts, dates, numbers, Hijri calendar |
| APIs | Idempotency, pagination, versioning, OpenAPI 3.1, contract tests |
| Legacy integration | SOAP adapters, SFTP drops, ESB, reconciliation and operational runbooks |
| APIM | Policies, products, subscriptions, JWT validation, backend pools, self-hosted gateway |
| Architecture | Modular monolith vs microservices, DDD boundaries, SAGA, CAP, DR |
| Deliverables | HLD, LLD, SAD, C4, DFD, sequence, ERD, interface specs, ADR, NFR catalogue |
| SQL | Execution plans, indexes, statistics, parameter sniffing, deadlocks, isolation |
| Migrations | Expand/contract, backward-compatible deployments, online index rebuilds, blue/green data |

---

## 5. Official Docs To Re-Check Before Interview

Version-specific behavior changes. Re-check these close to the interview date:

- FastAPI dependencies, middleware and lifespan events: https://fastapi.tiangolo.com/
- Pydantic v2 validation: https://docs.pydantic.dev/
- SQLAlchemy 2.0 ORM/session docs: https://docs.sqlalchemy.org/en/20/
- ASP.NET Core and EF Core docs: https://learn.microsoft.com/aspnet/core/ and https://learn.microsoft.com/ef/core/
- NestJS docs: https://docs.nestjs.com/
- Node/libuv docs: https://nodejs.org/ and https://docs.libuv.org/
- React docs: https://react.dev/
- Next.js docs: https://nextjs.org/docs
- WCAG 2.2: https://www.w3.org/TR/WCAG22/
- Azure API Management docs: https://learn.microsoft.com/azure/api-management/
- OpenAPI: https://spec.openapis.org/oas/
- Pact contract testing: https://docs.pact.io/
- PostgreSQL docs: https://www.postgresql.org/docs/
- SQL Server performance docs: https://learn.microsoft.com/sql/relational-databases/performance/
- pgvector: https://github.com/pgvector/pgvector

