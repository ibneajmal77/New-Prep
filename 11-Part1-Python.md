# Part 1.1 - Python

*Two layers: **Part A** is the build narrative. **Part B** is the complete reference. **Part C**
is the interview pressure test.*

---

# Part A - THE BUILD: Python In The Platform

## Step 1. We need a fast internal API

The employee portal needs APIs for leave balances, salary letters, profile updates and
approval status. Python is a good fit for services that sit close to data, automation and AI,
so we start with **FastAPI**.

FastAPI gives us:

- automatic OpenAPI documentation,
- request/response validation through Pydantic,
- async endpoints for IO-heavy calls,
- dependency injection for auth, database sessions and settings,
- middleware for cross-cutting concerns,
- lifespan hooks for startup/shutdown resources.

> Reference: [1.1.1 FastAPI production shape](#111-fastapi-production-shape)

## Step 2. Validate everything at the boundary

The first serious bug is not in business logic; it is dirty input. A date arrives in the wrong
format, an employee ID is blank, and an optional field is treated as trusted. We put Pydantic
models at the API boundary and keep domain logic away from raw request dictionaries.

Pydantic v2 matters because validation and serialization are explicit concepts:

- `BaseModel` describes input and output contracts.
- `field_validator` and `model_validator` enforce business-adjacent rules.
- `model_dump()` controls serialization.
- `ConfigDict` controls behavior such as `from_attributes`.

> Reference: [1.1.1.2 Pydantic v2 validation](#1112-pydantic-v2-validation)

## Step 3. Make dependencies explicit

Every endpoint needs the current user, a database session and sometimes a permission check.
Do not instantiate those inside endpoints. Declare them as dependencies. This keeps testing
simple and prevents hidden coupling.

```python
from typing import Annotated
from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

app = FastAPI()

class LeaveRequestIn(BaseModel):
    employee_id: str = Field(min_length=1)
    days: int = Field(gt=0, le=30)
    reason: str | None = None

def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user() -> User:
    # In production this usually validates a JWT or an Entra ID token.
    ...

Db = Annotated[Session, Depends(get_db)]
CurrentUser = Annotated[User, Depends(get_current_user)]

@app.post("/leave-requests")
def create_leave_request(payload: LeaveRequestIn, db: Db, user: CurrentUser):
    if payload.employee_id != user.employee_id:
        raise HTTPException(status_code=403, detail="Cannot submit for another employee")
    return service_create_leave_request(db, payload, user)
```

> Reference: [1.1.1.1 Dependency injection](#1111-dependency-injection)

## Step 4. Async helps IO, not CPU

The API must call identity, document, notification and workflow services. These are IO-bound
operations, so async can improve throughput. But async does not make CPU-heavy Pandas
processing faster. A blocking call inside an async endpoint can freeze the event loop and hurt
every request sharing that worker.

> Reference: [1.1.3 Async internals](#113-async-internals)

## Step 5. BackgroundTasks are not a queue

FastAPI `BackgroundTasks` is useful for small post-response tasks such as writing a lightweight
audit row or sending a non-critical notification. It is not durable orchestration. If the worker
dies, the task can be lost.

For workflow steps, retries, external integrations and reports, use Celery or another durable
job system with:

- idempotency keys,
- retry policies,
- dead-letter handling,
- operational visibility,
- safe reprocessing.

> Reference: [1.1.5 Celery and background jobs](#115-celery-and-background-jobs)

## Step 6. Treat database sessions as units of work

SQLAlchemy 2.0 should be used with explicit `select()` statements, clear transaction scope and
one session per request or job unit. Most production bugs come from long-lived sessions,
lazy-load surprises and unbounded query counts.

> Reference: [1.1.6 SQLAlchemy 2.0 ORM patterns](#116-sqlalchemy-20-orm-patterns)

## Step 7. Lock quality into the workflow

For a senior Python role, "I write tests" is not enough. The expected answer is that quality is
automated:

- `ruff` for linting and import hygiene,
- `mypy` or `pyright` for type checks,
- `pytest` fixtures for isolated dependencies,
- parametrized tests for business rules,
- mocking only at boundaries,
- coverage thresholds for risky modules,
- CI that blocks merges on failures.

> Reference: [1.1.7 Typing, linting and testing](#117-typing-linting-and-testing)

## Step 8. Use Python for data without abusing memory

The platform will import legacy HR files and generate operational reports. Pandas is suitable,
but only if we avoid row-by-row loops and uncontrolled memory growth.

> Reference: [1.1.9 Python for data](#119-python-for-data)

---

# Part B - THE REFERENCE

## 1.1.1 FastAPI Production Shape

FastAPI is strongest when the service is API-first, validation-heavy, OpenAPI-driven and
IO-bound. A production FastAPI service usually has these layers:

```text
HTTP request
  -> middleware: correlation ID, logging, CORS, security headers
  -> routing: endpoint function
  -> dependencies: auth, settings, db session, permission checks
  -> Pydantic models: parse and validate input
  -> service/domain logic
  -> repository or data-access layer
  -> Pydantic response model / serializer
  -> middleware: logging, metrics, error handling
```

### 1.1.1.1 Dependency Injection

FastAPI dependencies are callable objects declared with `Depends`. They can:

- provide shared request resources such as DB sessions,
- enforce authentication and authorization,
- centralize tenant/department context,
- wrap setup/teardown using `yield`,
- be overridden in tests.

Good dependency design:

- Keep dependencies small and composable.
- Put authentication in one dependency, permission checks in narrower dependencies.
- Do not hide business writes inside dependencies.
- Use `Annotated[T, Depends(...)]` to make types readable.
- Use dependency overrides in tests instead of monkeypatching global state.

Bad dependency design:

- Opening DB sessions manually in every endpoint.
- Creating HTTP clients per request without pooling.
- Mixing request validation, authorization and business mutation in one dependency.
- Using dependencies as a hidden service locator for everything.

### 1.1.1.2 Pydantic v2 Validation

Pydantic v2 is used for data validation and serialization. Interview-level details:

- `BaseModel` validates structured inputs.
- Type hints are runtime validation instructions, not just editor hints.
- `Field()` adds constraints such as length, range and examples.
- `field_validator()` validates one field.
- `model_validator()` validates cross-field rules.
- `model_dump()` replaces old-style dictionary dumping patterns.
- `from_attributes=True` helps serialize ORM objects into response models.

Example:

```python
from datetime import date
from pydantic import BaseModel, ConfigDict, Field, model_validator

class LeaveRequestIn(BaseModel):
    employee_id: str = Field(min_length=1, max_length=30)
    start_date: date
    end_date: date
    leave_type: str

    @model_validator(mode="after")
    def dates_must_be_ordered(self) -> "LeaveRequestIn":
        if self.end_date < self.start_date:
            raise ValueError("end_date must be on or after start_date")
        return self

class LeaveRequestOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    status: str
    employee_id: str
```

The senior point: validation at the API boundary does not replace domain rules. Pydantic can
reject malformed payloads, but business invariants still belong in services/domain code.

### 1.1.1.3 Async/Await In FastAPI

Use `async def` when the endpoint awaits async IO:

- async HTTP client calls,
- async database driver calls,
- async cache calls,
- async message publishing.

Use plain `def` when most work is synchronous and you are using sync drivers. FastAPI can run
sync endpoints in a threadpool, which protects the event loop from being blocked by normal
sync code.

Avoid:

```python
@app.get("/bad")
async def bad_endpoint():
    requests.get("https://internal-system")  # blocks the event loop
```

Prefer:

```python
import httpx

@app.get("/good")
async def good_endpoint():
    async with httpx.AsyncClient(timeout=5) as client:
        response = await client.get("https://internal-system")
    return response.json()
```

### 1.1.1.4 Background Tasks

FastAPI `BackgroundTasks` runs work after the response is sent. It is suitable for:

- best-effort audit side effects,
- small notification calls,
- cleanup work that can be lost safely.

It is not suitable for:

- salary processing,
- payment workflows,
- long OCR/report jobs,
- tasks requiring guaranteed execution,
- tasks that need retries after process restart.

The interview answer: **BackgroundTasks is a convenience; Celery or a queue is an operational
system.**

### 1.1.1.5 Middleware

Middleware wraps requests and responses. Common production middleware:

- correlation/request ID,
- structured logging,
- metrics and latency,
- CORS,
- security headers,
- request body size limits,
- exception mapping,
- tenant context.

Be careful with middleware that reads the body: request bodies are streams, and naive reads can
break downstream handlers or increase memory usage.

### 1.1.1.6 Lifespan Events

Lifespan handles startup and shutdown:

- create connection pools,
- initialize clients,
- warm caches,
- load configuration,
- close resources gracefully.

Use lifespan for application-level resources. Do not use it for per-request resources like DB
sessions.

```python
from contextlib import asynccontextmanager
from fastapi import FastAPI

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.http_client = httpx.AsyncClient(timeout=5)
    yield
    await app.state.http_client.aclose()

app = FastAPI(lifespan=lifespan)
```

## 1.1.2 Django vs FastAPI vs Flask

| Framework | Best fit | Strengths | Risks |
|---|---|---|---|
| Django | Full internal apps, admin-heavy systems, relational CRUD | Batteries included, ORM, admin, auth, migrations, mature ecosystem | Heavier if only building APIs; async support exists but many apps remain sync |
| FastAPI | API-first services, async IO, OpenAPI contracts, AI/data service edge | Type-driven validation, excellent docs generation, modern async support | You must assemble admin, auth patterns, migrations and background jobs yourself |
| Flask | Small services, simple internal tools, legacy lightweight apps | Minimal, flexible, easy to learn | Can become inconsistent without strong project structure |

How to answer "Which would you pick?":

- **Django** for a back-office case management system where admin screens, ORM and built-in
  conventions matter more than raw API ergonomics.
- **FastAPI** for a contract-first API layer serving a modern portal or AI service where typed
  validation and OpenAPI are central.
- **Flask** for a small utility service, webhook receiver or legacy-compatible micro app.

Strong panel answer: "I would not choose by popularity. I would choose by the shape of the
system, the team's skills, operational maturity and whether the app is mainly a product with
screens or an API surface."

## 1.1.3 Async Internals

### 1.1.3.1 Event Loop

Python async is cooperative concurrency. The event loop runs tasks until they hit an `await`
that yields control. While one task waits on network IO, another task can run.

Core terms:

- **Coroutine:** an async function call that can be awaited.
- **Task:** a scheduled coroutine managed by the event loop.
- **Future:** a placeholder for a result that may arrive later.
- **Await:** the point where a coroutine can suspend and let other work run.

Async helps when requests spend time waiting on IO. It does not remove CPU cost.

### 1.1.3.2 `asyncio.gather`

`asyncio.gather()` runs awaitables concurrently and returns results in input order.

Use it when independent IO calls can happen at the same time:

```python
employee, balance, approvals = await asyncio.gather(
    identity_client.get_employee(user_id),
    leave_client.get_balance(user_id),
    workflow_client.get_pending(user_id),
)
```

Senior details:

- If one task fails, default behavior propagates the exception.
- Use timeouts; otherwise one slow dependency can hold the request.
- Bound concurrency for lists. Do not create 10,000 tasks blindly.
- Consider cancellation behavior when a client disconnects or deadline expires.

### 1.1.3.3 Blocking-Call Pitfalls

Blocking inside async code damages throughput:

- `requests` instead of `httpx.AsyncClient`,
- sync database driver inside async endpoint,
- CPU-heavy Pandas transformation,
- large file reads,
- password hashing or compression in request path,
- `time.sleep()` instead of `await asyncio.sleep()`.

Mitigations:

- use async libraries end to end,
- offload CPU work to a process pool or job queue,
- keep sync endpoints as `def` if the stack is sync,
- isolate slow calls behind timeouts and circuit breakers,
- monitor event-loop lag.

### 1.1.3.4 Sync vs Async DB Drivers

Do not mix styles casually.

| Stack | Endpoint style | DB access | Notes |
|---|---|---|---|
| Sync SQLAlchemy + sync driver | `def` endpoints | normal `Session` | simple and stable for many CRUD APIs |
| Async SQLAlchemy + async driver | `async def` endpoints | `AsyncSession` | useful when DB waits dominate and drivers are mature |
| Async endpoint + sync DB call | risky | blocks event loop | avoid unless offloaded |

The senior answer: async is an architectural choice across the call chain, not a keyword added
to endpoint definitions.

## 1.1.4 Packaging And Environments

The goal is reproducible builds. The tools differ, but the principles are the same:

- isolate environments,
- pin direct dependencies,
- lock transitive dependencies,
- separate runtime dependencies from dev dependencies,
- scan dependencies,
- avoid "works on my machine" installs.

| Tool | Best use | Interview note |
|---|---|---|
| `uv` | fast modern dependency/project management | strong for new Python workflows |
| Poetry | project metadata, dependency management, lockfile | common in application repos |
| pip-tools | compile pinned `requirements.txt` from `.in` files | excellent for simple deploy targets |
| virtualenv/venv | isolated Python environment | base requirement, not enough alone |
| constraints files | central version caps | useful across multiple services |

Good practice:

- Commit lockfiles for applications.
- Be careful committing lockfiles for reusable libraries; libraries should avoid over-pinning
  consumers unless there is a reason.
- Pin Python version in CI and container builds.
- Use hashes where supply-chain risk is high.
- Rebuild images from lockfiles, not ad hoc installs.

## 1.1.5 Celery And Background Jobs

Use Celery or a durable queue when work must survive process restarts, retry safely or run
outside the request path.

Common jobs in the platform:

- generate salary certificates,
- sync records from legacy systems,
- send notifications,
- import SFTP files,
- produce reports,
- run OCR or document parsing,
- reconcile failed integrations.

### 1.1.5.1 Retries

Retries must distinguish transient and permanent errors:

- transient: network timeout, 503, lock conflict,
- permanent: invalid employee ID, failed validation, forbidden operation.

Use:

- exponential backoff,
- jitter,
- max retry counts,
- dead-letter queues,
- alerting after repeated failures.

### 1.1.5.2 Idempotency

Idempotency means repeating the same operation does not create duplicate business effects.

Patterns:

- idempotency key table,
- unique constraints on external reference IDs,
- outbox table,
- status machine with legal transitions,
- compare-and-set updates,
- dedupe by message ID.

Example: if a "create leave request" job is retried after a timeout, it must not create two
leave requests. Store `request_id` or `idempotency_key` and return the existing result on retry.

### 1.1.5.3 Celery Operational Risks

- Tasks must be small enough to retry.
- Payloads should carry IDs, not huge objects.
- Workers need timeouts and memory limits.
- Poison messages need quarantine.
- Long tasks need progress state.
- Queue depth should be monitored.
- Scheduling and worker deployments must be compatible during rolling releases.

## 1.1.6 SQLAlchemy 2.0 ORM Patterns

### 1.1.6.1 Session Lifecycle

The SQLAlchemy session is a unit-of-work boundary. Typical web pattern:

- open a session per request,
- run queries and changes,
- commit once,
- rollback on error,
- close in `finally`.

Avoid:

- global sessions,
- long-lived sessions across requests,
- returning lazy-loaded ORM objects after session close,
- committing in multiple random repository methods without a transaction strategy.

### 1.1.6.2 SQLAlchemy 2.0 Query Style

Prefer explicit `select()`:

```python
from sqlalchemy import select

stmt = select(Employee).where(Employee.employee_id == employee_id)
employee = db.scalars(stmt).one_or_none()
```

This style is clearer, closer to SQL and aligned with SQLAlchemy 2.0.

### 1.1.6.3 N+1 Queries

N+1 happens when one query loads parent rows, then one additional query is issued per parent
to load related data.

Bad shape:

```python
employees = db.scalars(select(Employee)).all()
for employee in employees:
    print(employee.department.name)  # can trigger one query per employee
```

Mitigations:

- `selectinload()` for collections and many relationships,
- `joinedload()` when a join is appropriate and cardinality is controlled,
- explicit joins for report-style queries,
- query count assertions in tests for high-risk endpoints.

### 1.1.6.4 Repository And Service Boundaries

Good pattern:

- Endpoint handles HTTP concerns.
- Service enforces business rules.
- Repository/data-access module owns query details.
- Transaction scope is clear.

Do not create generic repositories that hide useful SQLAlchemy features without adding value.
In Python, explicit query functions are often clearer than a large abstraction.

## 1.1.7 Typing, Linting And Testing

### 1.1.7.1 Typing

Type hints improve maintainability and editor support. They are most valuable at:

- service boundaries,
- DTOs/Pydantic models,
- repository return types,
- public helper functions,
- integration clients.

Use `mypy` or `pyright` to make types enforceable. Without a checker, type hints are mostly
documentation.

### 1.1.7.2 Ruff

`ruff` can handle linting, formatting-adjacent checks and import ordering quickly. Use it in CI.

Common checks:

- unused imports,
- complexity smells,
- insecure patterns,
- import sorting,
- style consistency.

### 1.1.7.3 Pytest

Expected tools:

- fixtures for databases, clients and fake dependencies,
- `parametrize` for business-rule matrices,
- `monkeypatch` for environment/config only when appropriate,
- mocking external systems at the boundary,
- integration tests for API contracts,
- coverage thresholds for core business modules.

Example:

```python
import pytest

@pytest.mark.parametrize(
    ("days", "expected_status"),
    [(1, "auto_approved"), (15, "manager_review"), (31, "invalid")],
)
def test_leave_policy_thresholds(days: int, expected_status: str):
    assert classify_leave_request(days) == expected_status
```

### 1.1.7.4 Mocking

Mock:

- email gateways,
- external APIs,
- time,
- queues,
- filesystem boundaries.

Do not mock:

- simple pure functions,
- the ORM so heavily that query bugs disappear,
- the code under test.

Use fake clients where behavior matters. Use mocks where call verification matters.

## 1.1.8 GIL, Multiprocessing, Threading And Async

The **Global Interpreter Lock** means only one thread executes Python bytecode at a time in
the standard CPython runtime. It does not mean threads are useless.

| Workload | Best option | Why |
|---|---|---|
| Network IO | async or threads | waiting dominates |
| File IO | threads or async libraries | depends on library support |
| CPU-heavy Python code | multiprocessing/process pool | bypasses GIL with separate processes |
| CPU-heavy NumPy/Pandas operations | vectorized libs, sometimes threads | native code may release GIL |
| Web request fan-out | async with timeouts | many concurrent waits |
| Long business job | queue worker | reliability and isolation |

Classic answer:

- **Threading** helps overlap blocking IO.
- **Async** helps manage many IO waits with fewer threads, but requires non-blocking libraries.
- **Multiprocessing** helps CPU-bound Python code because each process has its own interpreter.
- **Queues** are often better than doing heavy work inside request handlers.

## 1.1.9 Python For Data

Python often appears in application engineering because business systems need imports,
reconciliation, reporting and data preparation.

### 1.1.9.1 Pandas Operations

Prefer vectorized operations:

```python
df["net_days"] = (df["end_date"] - df["start_date"]).dt.days + 1
df["requires_manager"] = df["net_days"] > 10
```

Avoid row loops:

```python
for _, row in df.iterrows():
    ...
```

Use joins/merges instead of nested loops:

```python
merged = requests.merge(employees, on="employee_id", how="left")
```

### 1.1.9.2 Memory

Common memory controls:

- read only required columns,
- specify dtypes,
- parse dates deliberately,
- process large files in chunks,
- use categorical columns for repeated labels,
- avoid keeping intermediate copies,
- use Parquet instead of CSV for repeated analytics work.

### 1.1.9.3 Data Quality

For government HR data, expect:

- duplicate employee IDs,
- Arabic and English name variations,
- old department codes,
- missing dates,
- Excel files with merged cells,
- manually edited CSVs,
- inconsistent encodings.

Production import jobs need validation reports, quarantine tables and reconciliation, not just
`read_excel()`.

---

# Part C - Interview Traps

## Trap 1. "FastAPI is async, so it is faster."

Better answer: FastAPI supports async, but performance depends on the whole call chain. Async
improves concurrency for IO-bound workloads when libraries are non-blocking. If I call sync
database drivers or CPU-heavy Pandas inside `async def`, I can block the event loop and make
the service worse.

## Trap 2. "BackgroundTasks can run my business workflow."

Better answer: I would use FastAPI `BackgroundTasks` only for small best-effort post-response
work. For durable workflows I would use Celery or a queue with retries, idempotency, DLQ,
monitoring and replay.

## Trap 3. "The ORM hides SQL."

Better answer: The ORM helps map objects and unit-of-work changes, but I still inspect SQL,
execution plans and query counts. I use eager-loading strategies to avoid N+1 and write
explicit SQL when the query is report-heavy.

## Trap 4. "High test coverage means quality."

Better answer: Coverage is a signal, not a guarantee. I care more about covering business
rules, integration boundaries, idempotency, database behavior and failure paths. Coverage can
be high while assertions are weak.

## Trap 5. "Use multiprocessing for everything because of the GIL."

Better answer: Multiprocessing is useful for CPU-bound Python work. It adds serialization,
memory and operational overhead. For IO, async or threads are usually better; for business
jobs, a queue is better; for vectorized data work, optimized native libraries may already
release the GIL.

