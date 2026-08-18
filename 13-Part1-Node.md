# Part 1.3 - Node.js

*Two layers: **Part A** is the build narrative. **Part B** is the complete reference. **Part C**
is the interview pressure test.*

---

# Part A - THE BUILD: Node.js In The Platform

## Step 1. We need an integration edge service

The platform receives webhooks from vendors, publishes notifications, proxies some legacy
services and exposes lightweight APIs to the frontend. Node.js is a strong fit for IO-heavy
edge services, especially where TypeScript and the web ecosystem are already used.

For a large internal system, we use **NestJS** rather than unstructured Express because it gives
modules, dependency injection, guards, interceptors, pipes and a consistent architecture.

> Reference: [1.3.1 NestJS architecture](#131-nestjs-architecture)

## Step 2. Framework choice must match the risk

Express is flexible, Fastify is performance-oriented, and NestJS is structured. The right
choice depends on team size, maintainability, latency requirements and how much architecture
the framework should enforce.

> Reference: [1.3.2 Express vs Fastify vs NestJS](#132-express-vs-fastify-vs-nestjs)

## Step 3. The event loop is the real runtime model

The webhook receiver is fast until someone adds a CPU-heavy JSON transform and a synchronous
compression step. Suddenly all requests slow down. This is the Node.js interview classic:
Node can handle many concurrent IO operations, but CPU-bound JavaScript blocks the event loop.

> Reference: [1.3.3 Event loop, libuv and worker threads](#133-event-loop-libuv-and-worker-threads)

## Step 4. Streams prevent memory blowups

Legacy systems send large CSV files and document exports. Loading whole files into memory works
in a demo and fails in production. Node streams let us process data in chunks, but we must
respect backpressure.

> Reference: [1.3.4 Streams and backpressure](#134-streams-and-backpressure)

## Step 5. npm security is an architecture topic

Node services often have many transitive dependencies. In a government environment, dependency
security is not "run npm install and hope." We need lockfiles, audits, SBOMs, pinned build
images, vulnerability triage and package provenance controls.

> Reference: [1.3.5 npm supply-chain security](#135-npm-supply-chain-security)

---

# Part B - THE REFERENCE

## 1.3.1 NestJS Architecture

NestJS is an opinionated Node.js framework, usually used with TypeScript. It borrows concepts
from Angular and enterprise back-end frameworks.

Core building blocks:

- **Modules:** group related providers/controllers.
- **Controllers:** receive HTTP requests.
- **Providers:** injectable services, repositories, clients and helpers.
- **Guards:** decide whether a request can proceed.
- **Interceptors:** wrap execution for logging, transformation, timing or response shaping.
- **Pipes:** transform and validate incoming data.
- **Filters:** map exceptions to responses.

### 1.3.1.1 Modules

Modules define boundaries:

```typescript
@Module({
  imports: [DatabaseModule, NotificationsModule],
  controllers: [LeaveController],
  providers: [LeaveService, LeaveRepository],
  exports: [LeaveService],
})
export class LeaveModule {}
```

Good module design:

- group by business capability, not by technical file type only,
- export only what other modules need,
- avoid circular dependencies,
- keep shared modules small,
- avoid one giant `CommonModule` that becomes a dependency bucket.

### 1.3.1.2 Providers

Providers are classes registered in Nest's DI container:

```typescript
@Injectable()
export class LeaveService {
  constructor(private readonly repo: LeaveRepository) {}
}
```

Use providers for:

- application services,
- repositories,
- integration clients,
- configuration adapters,
- validators,
- policy checks.

Avoid providers that become god objects containing unrelated operations.

### 1.3.1.3 Guards

Guards answer: "Can this request proceed?"

Use cases:

- JWT validation,
- role checks,
- permission checks,
- tenant/department access,
- API key validation.

Guard design:

- authentication guard establishes identity,
- authorization guard checks capability,
- fine-grained business authorization still belongs near the use case.

### 1.3.1.4 Interceptors

Interceptors wrap handler execution. Use them for:

- logging,
- metrics,
- tracing,
- response mapping,
- caching where appropriate,
- timeout policies.

Do not hide business decisions in interceptors. If a rule affects the domain outcome, keep it
in the service/use-case layer.

### 1.3.1.5 Pipes

Pipes transform or validate input:

- parse integer route params,
- validate DTOs,
- trim/normalize input,
- reject malformed payloads.

Typical DTO validation uses `class-validator` and `class-transformer`, though some teams prefer
schema libraries such as Zod for explicit runtime schemas.

## 1.3.2 Express vs Fastify vs NestJS

| Framework | Best fit | Strengths | Risks |
|---|---|---|---|
| Express | small APIs, legacy apps, simple webhook receivers | huge ecosystem, minimal, familiar | easy to become inconsistent; middleware ordering mistakes |
| Fastify | high-throughput APIs, schema-driven validation, lower overhead | performance, plugin model, JSON schema support | smaller ecosystem than Express; team familiarity varies |
| NestJS | enterprise TypeScript services, larger teams, structured modules | DI, modules, guards, pipes, testing conventions | more ceremony; abstraction can hide simple HTTP behavior |

How to answer:

- Choose **Express** for small, low-ceremony services or legacy compatibility.
- Choose **Fastify** for performance-sensitive API services with clear schemas.
- Choose **NestJS** for larger codebases where consistency, testability and team structure
  matter.

Senior note: performance is rarely only framework choice. Payload size, database queries,
network calls, serialization, logging and event-loop blocking usually matter more.

## 1.3.3 Event Loop, libuv And Worker Threads

Node.js runs JavaScript on a single main thread, but uses libuv and the operating system for
asynchronous IO. Some work also uses a libuv threadpool.

### 1.3.3.1 Event Loop Model

At a high level:

```text
JavaScript call stack
  -> schedule async work
  -> event loop picks ready callbacks
  -> callbacks run to completion
  -> next ready callback
```

If a callback performs CPU-heavy synchronous work, no other JavaScript callback can run until
it finishes.

### 1.3.3.2 libuv

libuv provides:

- event loop implementation,
- async network IO integration,
- file-system operations,
- timers,
- threadpool for some operations,
- cross-platform abstractions.

Network IO is often handled by OS async facilities. Some operations, such as certain file
system calls, DNS calls and crypto/compression operations, may use the libuv threadpool.

### 1.3.3.3 Worker Threads

Use worker threads for CPU-heavy JavaScript work:

- parsing very large files,
- CPU-heavy transforms,
- image processing wrappers,
- compression/encryption tasks when not already offloaded efficiently.

Do not use worker threads for normal database or HTTP IO; async IO already handles that.

Operational risks:

- serialization cost between threads,
- memory overhead,
- worker pool management,
- error propagation,
- shutdown behavior.

### 1.3.3.4 Common Event-Loop Bugs

- `JSON.parse()` on huge payloads in request path,
- synchronous filesystem calls,
- CPU-heavy loops,
- regex catastrophic backtracking,
- unbounded Promise fan-out,
- logging too much synchronously,
- missing timeouts on outbound calls.

Mitigations:

- stream large data,
- bound concurrency,
- use worker threads for CPU work,
- add request body limits,
- add timeouts and abort signals,
- monitor event-loop lag.

## 1.3.4 Streams And Backpressure

Streams process data incrementally instead of loading everything into memory.

Use cases:

- file uploads,
- SFTP imports,
- CSV processing,
- large HTTP responses,
- compression,
- log pipelines.

### 1.3.4.1 Stream Types

- **Readable:** source of data.
- **Writable:** destination of data.
- **Duplex:** readable and writable.
- **Transform:** modifies data as it passes through.

### 1.3.4.2 Backpressure

Backpressure means the downstream consumer cannot process data as fast as the upstream producer
can provide it. If ignored, memory grows until the process slows or crashes.

Good pattern:

```typescript
import { pipeline } from "node:stream/promises";

await pipeline(
  sourceStream,
  csvParser,
  transformRows,
  destinationStream,
);
```

`pipeline()` handles error propagation and cleanup better than manually wiring events.

### 1.3.4.3 Interview Answer

"Streams are not only about speed; they are about bounded memory. Backpressure is the contract
that prevents a fast producer from overwhelming a slow consumer."

## 1.3.5 npm Supply-Chain Security

Node dependency risk matters because npm projects often carry large dependency graphs.

### 1.3.5.1 npm audit

`npm audit` checks dependency trees against known vulnerability advisories. It is useful, but
not sufficient.

Limitations:

- false positives,
- vulnerabilities in unused paths,
- no replacement for threat modeling,
- not all supply-chain attacks appear as known CVEs,
- automatic fixes can introduce breaking changes.

### 1.3.5.2 Lockfile Integrity

Use lockfiles:

- `package-lock.json`,
- `pnpm-lock.yaml`,
- `yarn.lock`.

Lockfiles pin transitive dependencies and include integrity hashes. In CI, use deterministic
install commands such as `npm ci` rather than `npm install`.

### 1.3.5.3 SBOM

An SBOM, or Software Bill of Materials, lists software components and dependency versions. For
government and enterprise platforms, SBOMs support:

- vulnerability response,
- license review,
- vendor risk management,
- incident investigation,
- release governance.

### 1.3.5.4 Practical Controls

- Commit lockfiles.
- Use `npm ci` in CI.
- Enable dependency scanning.
- Review high-risk package updates.
- Avoid abandoned packages.
- Pin Node and package manager versions.
- Use private registries or allowlists where required.
- Generate SBOMs for release artifacts.
- Use secrets scanning.
- Treat install scripts carefully.
- Review package ownership changes for critical dependencies.

---

# Part C - Interview Traps

## Trap 1. "Node is single-threaded, so it cannot scale."

Better answer: JavaScript runs on a single main thread, but Node handles async IO through the
event loop, OS facilities and libuv. It scales well for IO-heavy services. CPU-heavy work
should move to worker threads, processes or separate services.

## Trap 2. "Fastify is always better than Express because it is faster."

Better answer: Fastify can be faster and has strong schema support, but framework overhead is
only one factor. Team skill, ecosystem, observability, validation, deployment and database
behavior matter. For a large TypeScript team, NestJS may be the better maintainability choice.

## Trap 3. "Promises run in parallel."

Better answer: Promises represent async results. IO can happen concurrently, but JavaScript
callbacks still run on the event loop. CPU-heavy code inside Promise callbacks still blocks.

## Trap 4. "Streams are an optimization."

Better answer: Streams are often a reliability requirement. They prevent memory blowups when
handling large files or responses, and backpressure ensures slow consumers do not get
overwhelmed.

## Trap 5. "npm audit fixed means secure."

Better answer: Audit is one control. I also need lockfile integrity, deterministic CI
installs, SBOMs, dependency review, private registry policy, secrets scanning and runtime
monitoring.

