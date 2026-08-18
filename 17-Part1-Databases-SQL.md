# Part 1.7 - Databases And SQL

*Two layers: **Part A** is the build narrative. **Part B** is the complete reference. **Part C**
is the interview pressure test.*

---

# Part A - THE BUILD: Data Under The Platform

## Step 1. The database is part of the architecture

The employee-services platform stores employees, requests, approvals, documents, audit logs,
notifications and integration state. Some data is in SQL Server because of enterprise
Microsoft systems. Some newer services use PostgreSQL. Search and future AI features may use
pgvector or a dedicated vector store.

> Reference: [1.7.4 PostgreSQL vs SQL Server](#174-postgresql-vs-sql-server)

## Step 2. Queries must match indexes

The first performance issue is predictable: an admin page filters by status and department,
sorts by created date, and times out when the table grows. Fixing it requires execution plans,
statistics and the right index shape, not random indexes.

> Reference: [1.7.1 Indexing, execution plans and statistics](#171-indexing-execution-plans-and-statistics)

## Step 3. Concurrency is a business issue

Two managers approve the same request. A report reads while updates are in progress. A batch
job locks a table during working hours. Isolation levels, locking and deadlocks affect user
trust, not just database internals.

> Reference: [1.7.2 Query tuning, parameter sniffing, deadlocks and isolation](#172-query-tuning-parameter-sniffing-deadlocks-and-isolation)

## Step 4. Model data for correctness first

Normalize the core transactional model so rules are enforceable. Denormalize deliberately for
read models, reporting and search. Partition or shard only when scale and operations justify
it.

> Reference: [1.7.3 Normalization, denormalization, partitioning and sharding](#173-normalization-denormalization-partitioning-and-sharding)

## Step 5. Vector search changes the indexing conversation

If the platform later supports semantic document search, embeddings may live in pgvector.
HNSW and IVFFlat are approximate-nearest-neighbor index choices with different build, memory
and recall tradeoffs.

> Reference: [1.7.5 pgvector and vector indexes](#175-pgvector-and-vector-indexes)

## Step 6. Schema changes must not take the system down

Changing a column or index in production can be riskier than changing application code. We use
expand/contract migrations, backward-compatible releases, online operations where supported,
and clear rollback/forward-fix plans.

> Reference: [1.7.6 Migration strategy and zero-downtime schema changes](#176-migration-strategy-and-zero-downtime-schema-changes)

---

# Part B - THE REFERENCE

## 1.7.1 Indexing, Execution Plans And Statistics

### 1.7.1.1 What An Index Does

An index is a data structure that helps the database find rows without scanning everything.
Indexes speed reads for specific query shapes but add cost to writes and storage.

Do not ask "Should this table have an index?" Ask:

- Which query must be fast?
- What are the filter predicates?
- What is the sort order?
- What columns are returned?
- How selective are the predicates?
- How often is the table written?
- Does the index support constraints as well as performance?

### 1.7.1.2 Clustered vs Non-Clustered

SQL Server:

- **Clustered index:** defines physical/logical row order of the table structure.
- **Non-clustered index:** separate structure with keys and row locators.

PostgreSQL:

- tables are heap-organized by default,
- indexes point to heap tuples,
- `CLUSTER` can physically reorder a table but does not maintain clustering automatically.

Interview caution: clustered/non-clustered language is SQL Server-centric. Explain vendor
differences instead of assuming all databases behave the same.

### 1.7.1.3 Covering Indexes

A covering index contains all columns needed by a query, so the engine may avoid extra lookups.

SQL Server example:

```sql
CREATE INDEX IX_LeaveRequests_Status_Department_Created
ON dbo.LeaveRequests (Status, DepartmentId, CreatedAt DESC)
INCLUDE (EmployeeId, RequestType);
```

Use when a hot query repeatedly filters/sorts by key columns and returns a small set of
additional columns.

Risk:

- bigger index,
- slower writes,
- more maintenance,
- duplicated storage.

### 1.7.1.4 Filtered / Partial Indexes

SQL Server filtered index:

```sql
CREATE INDEX IX_LeaveRequests_Pending
ON dbo.LeaveRequests (DepartmentId, CreatedAt)
WHERE Status = 'Pending';
```

PostgreSQL partial index:

```sql
CREATE INDEX ix_leave_requests_pending
ON leave_requests (department_id, created_at)
WHERE status = 'Pending';
```

Use when a small subset of rows is queried often, such as pending approvals.

### 1.7.1.5 Execution Plans

Execution plans show how the database intends to run a query:

- scans,
- seeks,
- joins,
- sort operations,
- key lookups,
- memory grants,
- parallelism,
- estimated vs actual row counts.

Look for:

- table scans on large tables,
- wrong row estimates,
- missing index suggestions,
- expensive sorts,
- nested loops over large inputs,
- hash spills,
- key lookup storms.

Senior answer: "I inspect actual execution plans with realistic parameters and row counts, not
only estimated plans on empty dev data."

### 1.7.1.6 Statistics

Statistics tell the optimizer about data distribution. Bad or stale statistics can cause bad
plans even when indexes exist.

Watch for:

- skewed data,
- outdated stats after large imports,
- ascending-key problems,
- parameter-sensitive plans.

Maintenance:

- auto-update stats where appropriate,
- scheduled maintenance for large systems,
- analyze/vacuum behavior in PostgreSQL,
- index rebuild/reorganize decisions in SQL Server.

## 1.7.2 Query Tuning, Parameter Sniffing, Deadlocks And Isolation

### 1.7.2.1 Query Tuning Process

1. Capture the slow query and parameters.
2. Check actual execution plan.
3. Compare estimated vs actual rows.
4. Check indexes and predicates.
5. Check whether functions prevent index use.
6. Reduce selected columns.
7. Add pagination.
8. Avoid unnecessary joins.
9. Test with production-like data.
10. Measure before and after.

Common fixes:

- add/adjust index,
- rewrite predicate,
- split query,
- precompute read model,
- update statistics,
- avoid scalar functions in predicates,
- fix ORM-generated query shape.

### 1.7.2.2 Parameter Sniffing

Parameter sniffing occurs when SQL Server optimizes a plan for one parameter value and reuses
it for another value where the plan is poor.

Example:

- `DepartmentId = 'HR'` returns 10 rows.
- `DepartmentId = 'PUBLIC_SERVICES'` returns 500,000 rows.
- One cached plan cannot be ideal for both.

Mitigations:

- better indexes,
- update statistics,
- `OPTION (RECOMPILE)` for selected queries,
- optimize for specific/unknown value,
- split procedure paths for high-skew cases,
- parameter-sensitive plan features where available,
- avoid local-variable hacks unless understood.

Senior point: parameter sniffing is not always bad; plan reuse is normally good. It becomes a
problem with skewed distributions and mismatched plans.

### 1.7.2.3 Deadlocks

A deadlock happens when transactions wait on each other in a cycle.

Example:

```text
Transaction A locks LeaveRequest then EmployeeBalance.
Transaction B locks EmployeeBalance then LeaveRequest.
Each waits for the other.
```

Prevention:

- access tables in consistent order,
- keep transactions short,
- use proper indexes to avoid wide locks,
- avoid user interaction inside transactions,
- choose isolation level deliberately,
- retry deadlock victims safely.

Deadlock retries must be idempotent.

### 1.7.2.4 Isolation Levels

Common concepts:

- read uncommitted: dirty reads possible,
- read committed: avoids dirty reads,
- repeatable read: protects rows read from changing,
- serializable: strongest isolation, more blocking/conflicts,
- snapshot/MVCC: readers see a versioned snapshot.

SQL Server and PostgreSQL implement details differently. Always check the specific database.

Business examples:

- approval status update needs correctness,
- dashboard counts may tolerate slight staleness,
- financial/payroll operations need stronger consistency.

### 1.7.2.5 Locking

Locking protects consistency but can block users.

Common causes of blocking:

- long transactions,
- missing indexes,
- batch updates during business hours,
- table scans,
- schema changes,
- report queries against transactional tables.

Mitigations:

- right indexes,
- shorter transactions,
- batching,
- read replicas/reporting stores,
- snapshot isolation where appropriate,
- online schema operations where supported.

## 1.7.3 Normalization, Denormalization, Partitioning And Sharding

### 1.7.3.1 Normalization

Normalization reduces duplication and protects data integrity.

Use in transactional core:

- employees,
- departments,
- requests,
- approvals,
- documents,
- audit entries.

Benefits:

- fewer update anomalies,
- cleaner constraints,
- clearer relationships,
- better correctness.

### 1.7.3.2 Denormalization

Denormalization duplicates or precomputes data for read performance.

Use for:

- dashboards,
- reporting,
- search views,
- analytics,
- event projections.

Risks:

- stale data,
- synchronization complexity,
- unclear source of truth.

Senior answer: normalize the write model; denormalize deliberately for read models with clear
refresh and ownership.

### 1.7.3.3 Partitioning

Partitioning splits one logical table into physical partitions.

Use when:

- table is very large,
- data naturally partitions by date or tenant,
- maintenance should target partitions,
- old data can be archived efficiently,
- queries commonly filter by partition key.

Examples:

- audit logs by month,
- notifications by creation date,
- document events by year.

Risks:

- wrong partition key gives little benefit,
- global indexes/constraints vary by database,
- query must include partition key to prune partitions,
- operational complexity increases.

### 1.7.3.4 Sharding

Sharding splits data across databases/servers.

Use only when:

- one database cannot handle load/size,
- tenant isolation requires it,
- team can operate distributed data,
- cross-shard queries are rare or handled deliberately.

Risks:

- cross-shard transactions,
- reporting complexity,
- rebalancing,
- tenant movement,
- operational tooling,
- backup/restore complexity.

For most government internal systems, partitioning/read replicas/read models should be
considered before sharding.

## 1.7.4 PostgreSQL vs SQL Server

### 1.7.4.1 PostgreSQL Strengths

- strong SQL compliance,
- MVCC,
- rich indexing options,
- extensions such as pgvector and PostGIS,
- JSONB support,
- open-source ecosystem,
- strong concurrency for many workloads.

Operational topics:

- vacuum/autovacuum,
- analyze/statistics,
- bloat,
- connection pooling,
- transaction ID wraparound,
- WAL and replication.

### 1.7.4.2 SQL Server Strengths

- deep Microsoft ecosystem integration,
- mature enterprise tooling,
- T-SQL,
- strong optimizer,
- columnstore indexes,
- Always On availability groups,
- SQL Server Agent in many environments,
- integration with Windows/Entra-centered enterprises.

Operational topics:

- tempdb,
- parameter sniffing,
- execution plan cache,
- indexing maintenance,
- transaction log management,
- isolation options such as read committed snapshot.

### 1.7.4.3 T-SQL Window Functions

Window functions compute values across a set of rows without collapsing rows like `GROUP BY`.

```sql
SELECT
    EmployeeId,
    DepartmentId,
    CreatedAt,
    ROW_NUMBER() OVER (
        PARTITION BY DepartmentId
        ORDER BY CreatedAt DESC
    ) AS RowInDepartment
FROM dbo.LeaveRequests;
```

Use for:

- ranking,
- running totals,
- latest record per group,
- percentiles,
- deduplication.

### 1.7.4.4 CTEs

Common Table Expressions make complex queries readable:

```sql
WITH Pending AS (
    SELECT *
    FROM dbo.LeaveRequests
    WHERE Status = 'Pending'
)
SELECT DepartmentId, COUNT(*) AS PendingCount
FROM Pending
GROUP BY DepartmentId;
```

CTEs are not automatically materialized optimization barriers in SQL Server. Understand how the
optimizer treats them.

### 1.7.4.5 MERGE

`MERGE` can combine insert/update/delete logic, often used for upserts.

Use carefully:

- concurrency behavior must be understood,
- triggers and constraints can surprise,
- bugs/caveats have existed in some SQL Server versions,
- simpler `UPDATE` then `INSERT` or database-specific upsert may be clearer.

Interview answer:

"I know `MERGE`, but I do not use it blindly for critical paths. I evaluate concurrency,
locking and database-version behavior."

## 1.7.5 pgvector And Vector Indexes

pgvector stores embedding vectors inside PostgreSQL. It is useful when semantic search is close
to relational data and PostgreSQL operations are already strong.

### 1.7.5.1 Exact vs Approximate Search

Exact nearest-neighbor search compares against all vectors. It has high recall but can be slow
at scale.

Approximate nearest-neighbor indexes trade some recall for speed.

### 1.7.5.2 HNSW

HNSW builds a graph-like index for approximate nearest-neighbor search.

Strengths:

- strong recall/speed tradeoff,
- no training step,
- often good query performance.

Costs:

- memory usage,
- index build time,
- tuning parameters,
- write/update overhead.

### 1.7.5.3 IVFFlat

IVFFlat partitions vectors into lists. Search probes some lists.

Strengths:

- can be efficient at scale,
- index size can be manageable.

Costs:

- needs representative data before building,
- probe count affects recall/latency,
- poor training/data distribution hurts quality.

### 1.7.5.4 Filters And Hybrid Search

Vector search often needs relational filters:

```sql
WHERE department_id = 'HR'
  AND classification <= 'Internal'
```

For RAG systems, permission-aware filters are essential. Do not retrieve documents first and
filter permissions later in application code if restricted content can reach the model/context.

## 1.7.6 Migration Strategy And Zero-Downtime Schema Changes

### 1.7.6.1 Expand/Contract

Zero-downtime migrations often use expand/contract:

1. **Expand:** add new nullable column/table/index while old code still works.
2. **Dual write or backfill:** populate new structure safely.
3. **Deploy code:** read from new structure.
4. **Verify:** compare old and new data.
5. **Contract:** remove old column/table only after all code paths are migrated.

### 1.7.6.2 Backward-Compatible Changes

Usually safe:

- add nullable column,
- add new table,
- add new index online where supported,
- add optional API field,
- widen column carefully.

Risky:

- drop column,
- rename column,
- change type,
- add non-null column without default strategy,
- rewrite huge table,
- lock table during business hours.

### 1.7.6.3 Blue/Green Data

Blue/green application deployment is easy compared with blue/green data. Data changes persist
across versions.

Rules:

- new app version must run against old-compatible schema during rollout,
- old app version must survive while new version is partially deployed,
- rollback should not require restoring the whole database except in disaster scenarios,
- prefer forward fixes for schema mistakes after deployment.

### 1.7.6.4 Backfills

Backfill large tables carefully:

- batch updates,
- sleep between batches if needed,
- track progress,
- make job restartable,
- avoid long transactions,
- monitor locks, log growth and replication lag.

### 1.7.6.5 Migration Review Checklist

- What lock does the operation take?
- How long on production-sized data?
- Is it backward compatible?
- Does it need online index build?
- What is rollback/forward-fix?
- Is there a backfill?
- Is the backfill idempotent?
- Are reports/ETL affected?
- Have backups and restore been tested?
- Is the change scheduled outside peak hours if risky?

---

# Part C - Interview Traps

## Trap 1. "Add an index to make it faster."

Better answer: I start with the query shape and actual execution plan. The right index depends
on filters, sorting, selectivity and returned columns. Indexes also slow writes and add
maintenance cost.

## Trap 2. "Parameter sniffing is always bad."

Better answer: plan reuse is usually good. Parameter sniffing becomes a problem when a plan
optimized for one parameter performs badly for another, usually because data distribution is
skewed.

## Trap 3. "Deadlocks mean the database is broken."

Better answer: deadlocks are usually a transaction design issue: inconsistent access order,
long transactions, missing indexes or too much work inside a transaction. Handle with design
and safe retries.

## Trap 4. "Denormalization is bad design."

Better answer: denormalization is bad when accidental. It is good when used deliberately for
read models, reporting or search, with clear ownership and refresh rules.

## Trap 5. "Zero downtime means deploy app and DB together."

Better answer: zero-downtime schema changes require backward-compatible expand/contract
migrations, rolling deployment compatibility, restartable backfills, and delayed removal of old
schema.

