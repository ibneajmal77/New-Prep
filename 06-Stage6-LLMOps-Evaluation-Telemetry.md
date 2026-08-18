# Stage 6 - LLMOps, Evaluation & Telemetry (8.5)

*Two layers: **Part A** is the build narrative. **Part B** is the complete reference. **Part C**
assembles it. Stage 5 defined the controls; Stage 6 proves whether the system is actually
working, safe, fast and affordable.*

**Where we are:** The assistant now has RAG, tools, approvals and guardrails. That is still not
production. Production needs evidence: regression tests, quality metrics, traces, cost
accounting, latency SLOs, feedback loops and controlled deployment of prompts and models.

---

# Part A - THE BUILD: Stage 6

## Step 1. "It seems better" is not an engineering statement

Someone changes chunk size, the prompt and the model in the same week. Complaints drop, but
cost doubles and Arabic answers get worse. We need eval-driven development: every change must
be judged against the same dataset and metrics.

> **-> [8.5.10 Eval-driven development](#8510-eval-driven-development-)**

## Step 2. Build the automated evaluation harness

The golden set from Stage 3 becomes a regression suite. It runs in CI for deterministic checks,
nightly for LLM-judged checks, and before every prompt/model release.

> **-> [8.5.1 Evaluation harness](#851-evaluation-harness)**

## Step 3. Decide which metrics matter

Groundedness, answer relevance, coherence, toxicity, task success, tool-call accuracy and
retrieval metrics measure different failures. A single score hides the diagnosis.

> **-> [8.5.2 Metrics](#852-metrics)**

## Step 4. Users say it is slow

Total latency is not enough. For streaming experiences, time to first token matters. For agents,
tool latency and step count matter. For operations, p95 and p99 matter more than averages.

> **-> [8.5.4 Latency telemetry](#854-latency-telemetry)**

## Step 5. Finance asks why the bill doubled

Token use must be attributed by user, tenant, feature, model, prompt version and route. Without
that, cost optimization is guessing.

> **-> [8.5.3 Cost & token monitoring](#853-cost--token-monitoring)**

## Step 6. One bad answer needs a trace

The complaint is one answer, not a dashboard. We need the full trace: request, retrieval,
reranker, prompt version, model call, tool calls, approval and validators.

> **-> [8.5.5 Tracing](#855-tracing)**

## Step 7. Define what reliability means for an AI system

Traditional uptime is not enough. The model can be up and still ungrounded, unsafe, too slow or
too expensive. AI SLOs must include quality and budget signals.

> **-> [8.5.8 SLOs for AI systems](#858-slos-for-ai-systems-)**
> **-> [8.5.9 Telemetry retention policy](#859-telemetry-retention-policy-)**

## Step 8. Learn from production without letting production train the model blindly

Thumbs up/down, incident triage and human review loops are evidence. They must feed the golden
set, prompt backlog and red-team suite. They should not become unfiltered training data.

> **-> [8.5.6 Feedback loops](#856-feedback-loops)**

## Step 9. Roll out prompts and models like software

Prompts, model deployments, embedding models and rerankers all need versioning, canaries,
shadow tests, rollback and deprecation handling.

> **-> [8.5.7 Canary, shadow deployment and version pinning](#857-canary-shadow-deployment-and-version-pinning)**

---

# Part B - THE REFERENCE

## 8.5.10 Eval-driven development `+`
> **In the build:** Stage 6, Step 1 - *"it seems better is not an engineering statement."*

### Definition

Eval-driven development is the practice of making every prompt, model, retrieval and tool
change pass a measurable evaluation before release. It is test-driven development adapted to
probabilistic systems: not "one expected string", but thresholds over a representative dataset.

### The loop

```
define behavior -> build golden set -> run baseline -> make one change
               -> compare metrics -> inspect failures -> ship or revert
```

### Rules

- Change one major variable at a time: model, prompt, chunking, top-k, reranker.
- Keep a baseline run for comparison.
- Split retrieval metrics from generation metrics.
- Include unanswerable, Arabic/bilingual and permission-sensitive cases.
- Add every production incident to the dataset permanently.

### Fails when

- The demo question set is treated as an evaluation set.
- A single LLM judge score decides release.
- Cost and latency are not part of the scorecard.
- Thresholds are lowered to make a release pass.

---

## 8.5.1 Evaluation harness
> **In the build:** Stage 6, Step 2 - *"build the automated evaluation harness."*

### 1. Definition

An evaluation harness is the repeatable system that runs test cases through the AI pipeline,
scores the result, compares it to baselines and blocks regressions.

### 2. Components

| Component | Purpose |
|---|---|
| Golden dataset | Questions, expected answers, gold chunks, users/permissions |
| Runner | Executes the same production path or a controlled offline copy |
| Scorers | Deterministic metrics plus LLM-as-judge where needed |
| Baseline store | Previous prompt/model/index results |
| CI gate | Blocks unsafe regressions |
| Review UI | Human review of ambiguous failures |

### 3. Offline vs online

| Mode | Use for | Weakness |
|---|---|---|
| Offline eval | Release gates, prompt/model comparison | Dataset can go stale |
| Online eval | Sampled production traffic, drift detection | Ground truth is delayed or absent |
| Human review | High-stakes and ambiguous cases | Expensive, slower |
| Pairwise comparison | Prompt/model A vs B | Needs consistent judge criteria |

### 4. LLM-as-judge

LLM judges are useful for relevance, groundedness and style. They are biased toward longer,
more confident and familiar outputs. Calibrate them against human labels and never use them as
the only gate for security-sensitive behavior.

### 5. Example

```python
def test_rag_release_candidate():
    records = run_golden_set(
        prompt_version="hr-rag-2.3.0",
        model_route="candidate",
    )
    metrics = score(records)

    assert metrics["retrieval_hit_rate_at_8"] >= 0.90
    assert metrics["context_recall"] >= 0.85
    assert metrics["faithfulness"] >= 0.90
    assert metrics["correct_abstention_rate"] >= 0.90
    assert metrics["permission_leak_count"] == 0
```

### 6. Fails when

- The harness bypasses production authorization or prompt assembly.
- Only happy-path answerable questions are included.
- Evaluation runs as an admin user.
- Golden answers are not reviewed when policies change.

---

## 8.5.2 Metrics
> **In the build:** Stage 6, Step 3 - *"decide which metrics matter."*

### 1. Definition

Metrics are the observable signals that tell you what failed and where to fix it. In LLM
systems, quality, safety, task success, retrieval, latency and cost all need separate measures.

### 2. Metric map

| Metric | Answers | Fix when low |
|---|---|---|
| Groundedness/faithfulness | Are claims supported by context? | grounding prompt, citations, validators |
| Answer relevance | Did it answer the question? | prompt, query rewrite |
| Coherence/fluency | Is it readable and internally consistent? | model/prompt |
| Toxicity/safety | Is content harmful or disallowed? | filters, policy, prompt |
| Task success | Did the workflow complete correctly? | orchestrator, tools, UX |
| Tool-call accuracy | Right tool, right args, right time? | tool schema/descriptions, examples |
| Retrieval hit rate | Did the gold chunk appear in top-k? | chunking, embeddings, search |
| Context precision/recall | Were retrieved chunks relevant and complete? | reranking, top-k, filters |
| Abstention rate | Did it say "I don't know" when appropriate? | grounding policy, thresholds |

### 3. The important split

```
Low retrieval recall + high faithfulness -> fix retrieval.
High retrieval recall + low faithfulness -> fix generation/validation.
Low tool-call accuracy -> fix tool schemas and orchestration.
Good quality + bad p95 latency -> fix routing, caching or tools.
```

### 4. Fails when

- One aggregate "AI quality" number hides the failure layer.
- Only user thumbs up/down are used; feedback is sparse and biased.
- Metrics are not segmented by language, tenant, channel and task type.

---

## 8.5.4 Latency telemetry
> **In the build:** Stage 6, Step 4 - *"users say it is slow."*

### 1. Definition

Latency telemetry measures where time is spent: request queueing, retrieval, reranking, model
prefill, time to first token, token streaming, tool calls, approvals and validators.

### 2. Metrics

| Metric | Meaning |
|---|---|
| TTFT | time to first token; user-perceived start of answer |
| Tokens/sec | generation throughput after first token |
| End-to-end latency | full user request duration |
| p50/p95/p99 | median, slow tail, extreme tail |
| Step count | number of agent iterations |
| Tool latency | time per external dependency |
| Timeout rate | requests terminated by limit |
| Fallback rate | primary model failed or was bypassed |

### 3. Pattern

```python
with tracer.start_as_current_span("rag_request") as span:
    t0 = now()
    chunks = timed("retrieval", retrieve)(question)
    ranked = timed("rerank", rerank)(chunks)
    stream = client.responses.create(..., stream=True)
    for event in stream:
        if first_token_not_seen and event.type == "output_text.delta":
            span.set_attribute("llm.ttft_ms", ms_since(t0))
        yield event
    span.set_attribute("llm.total_ms", ms_since(t0))
```

### 4. Fails when

- Average latency is reported instead of p95/p99.
- Model latency and retrieval/tool latency are not separated.
- Streaming is treated as lower total latency; it mainly improves perceived latency.
- Timeouts are not visible by feature and model route.

---

## 8.5.3 Cost & token monitoring
> **In the build:** Stage 6, Step 5 - *"finance asks why the bill doubled."*

### 1. Definition

Cost monitoring attributes token and service spend to the request, user, tenant, feature,
model, prompt version and agent run. Token monitoring records input, cached input, output,
reasoning tokens where exposed, embedding tokens and reranker/model calls.

### 2. What to record

| Field | Why |
|---|---|
| `tenant_id`, `user_id`, `feature` | chargeback and abuse detection |
| `model`, `deployment`, `route` | model-selection optimization |
| `prompt_version` | prompt regressions and cache misses |
| input/output/cached/reasoning tokens | actual cost drivers |
| agent steps/tool calls | multi-call multiplier |
| embedding/reranker calls | hidden RAG costs |
| estimated cost | budget alerts |

### 3. Optimization levers

| Lever | Saves |
|---|---|
| Model routing | frontier calls on easy tasks |
| Prompt caching | repeated stable prefixes |
| Context trimming | unnecessary history/chunks/tool results |
| Retrieval caching | repeated popular questions |
| Batching | embeddings and offline evals |
| Downgrading/fallback | non-critical tasks |
| Agent-to-workflow conversion | repeated multi-step cost |

### 4. Example

```python
emit_metric("llm.usage", {
    "tenant": tenant_id,
    "feature": "hr_rag",
    "model": response.model,
    "prompt_version": prompt_version,
    "input_tokens": usage.input_tokens,
    "cached_input_tokens": usage.cached_input_tokens,
    "output_tokens": usage.output_tokens,
    "agent_steps": state.steps,
    "estimated_usd": estimate_cost(usage, response.model),
})
```

### 5. Fails when

- Only the monthly cloud invoice is monitored.
- Cached tokens are not tracked, so broken prompt caching is invisible.
- Reasoning tokens are omitted from the cost model.
- Agent cost is counted as one model call.
- Budgets are per subscription but not per tenant or feature.

---

## 8.5.5 Tracing
> **In the build:** Stage 6, Step 6 - *"one bad answer needs a trace."*

### 1. Definition

Tracing records the path of one request across model calls, retrieval, reranking, tools,
approvals, validators and response rendering. Metrics tell you something is wrong; traces show
what happened in a specific case.

### 2. Tools

| Tool | Use |
|---|---|
| LangSmith | LangChain/LangGraph traces, datasets, prompt runs |
| OpenTelemetry GenAI conventions | vendor-neutral spans/attributes for LLM, retrieval, tools and agents |
| Azure AI Foundry tracing/monitoring | Foundry project traces, Application Insights integration, agent observability |
| Application Insights / Azure Monitor | production dashboards, alerts, KQL queries |

### 3. Span shape

```
request
  retrieval
    vector_search
    semantic_rerank
  model_call
  tool_call: check_leave_balance
  approval_request
  validator: citation_check
  response
```

### 4. Security rule

Trace data can contain prompts, completions, tool arguments, retrieved content and user data.
Treat it as production data: redact where possible, restrict access, define retention and avoid
logging secrets.

### 5. Fails when

- Traces are enabled only in development.
- Prompt/model versions are missing from spans.
- Retrieval IDs are missing, so citations cannot be reproduced.
- Tracing stores sensitive content with broad developer access.

---

## 8.5.8 SLOs for AI systems `+`
> **In the build:** Stage 6, Step 7 - *"define what reliability means."*

### Definition

An SLO is a target for user-visible service behavior. AI systems need ordinary operational SLOs
plus quality and safety SLOs.

| SLO | Example |
|---|---|
| Availability | 99.9% of chat requests receive a response or safe fallback |
| Latency | p95 non-agent answer under 4s; p95 TTFT under 1s |
| Groundedness | >= 90% on sampled answerable RAG traffic |
| Permission safety | zero known cross-user retrieval leaks |
| Tool accuracy | >= 95% correct tool selection on golden set |
| Cost | p95 cost/request below budget by feature |
| Abstention | >= 90% correct abstention on unanswerable golden set |

**What you cannot promise:** exact deterministic answers across model backend changes, perfect
truth if the source corpus is wrong, or zero hallucinations without an abstention/verification
path. State the control and the measured target, not impossible certainty.

---

## 8.5.9 Telemetry retention policy `+`
> **In the build:** Stage 6, Step 7 - *"telemetry is a compliance decision."*

### Definition

Telemetry retention defines what AI interaction data is stored, where, for how long, at what
granularity and who can access it.

| Data | Retention decision |
|---|---|
| Aggregated metrics | long-lived, low sensitivity |
| Trace metadata | medium retention for debugging |
| Raw prompts/responses | short or restricted retention |
| Retrieved chunks/tool results | often highly sensitive; minimize |
| Approval records | long retention if official action |
| Evaluation datasets | governed like source data |

**Fails when** - telemetry is treated as "just logs" and escapes the same DLP, residency,
access-control and deletion rules as the application.

---

## 8.5.6 Feedback loops
> **In the build:** Stage 6, Step 8 - *"learn from production."*

### Definition

Feedback loops turn production signals into controlled improvements: user ratings, corrections,
incident reports, human-review labels, support tickets and evaluator failures.

### Workflow

```
bad answer -> triage -> classify failure layer -> add to dataset
           -> fix prompt/retrieval/tool/control -> eval -> canary -> monitor
```

### Signals

| Signal | Bias |
|---|---|
| Thumbs up/down | sparse, negative-heavy, little context |
| Free-text feedback | useful but noisy and may contain PII |
| Support tickets | severe failures only |
| Human review labels | best quality, expensive |
| Automated eval failures | consistent, but judge-biased |

### Fails when

- Feedback trains or fine-tunes directly without filtering.
- Incidents are fixed but not added to regression tests.
- The failure layer is not classified, so everything becomes a prompt change.
- Product teams monitor satisfaction but not safety or groundedness.

---

## 8.5.7 Canary, shadow deployment and version pinning
> **In the build:** Stage 6, Step 9 - *"roll out prompts and models like software."*

### 1. Definition

Deployment discipline for AI means controlling which prompt, model, embedding model, reranker
and tool schema version serves which traffic, and rolling changes out with measurement and
rollback.

### 2. Patterns

| Pattern | Meaning | Use |
|---|---|---|
| Version pinning | Explicit model/prompt/deployment versions | Reproducibility |
| Canary | Small percentage of real users gets candidate | Safe rollout |
| Shadow | Candidate runs in parallel but does not answer user | Compare safely |
| A/B test | Variants compared on defined metrics | Product/prompt decisions |
| Rollback | Return route to prior known-good version | Incident response |

### 3. Example

```python
route = choose_route(user_id, feature="hr_rag")
config = CONFIGS[route]

answer = run_pipeline(
    model=config.model_deployment,
    prompt=config.prompt_version,
    embedding_index=config.index_version,
)

emit_metric("llm.route", {"route": route, **quality_and_cost(answer)})
```

### 4. Deprecation handling

Models and API versions are deprecated. Keep an inventory of every deployment, prompt, eval
baseline and expected retirement date. Run shadow tests against the replacement before forced
migration. The worst migration is one performed by a deadline without an evaluation baseline.

### 5. Fails when

- Model names are hardcoded across services.
- Prompt changes ship without version IDs in telemetry.
- Embedding model changes do not trigger re-embedding and index versioning.
- Canary success is judged on no complaints rather than metrics.
- Rollback cannot restore the previous prompt/model/index combination.

---

# Part B2 - DEEP INTERVIEW EXPANSION

This section is the slower pass for panel answers. It expands the compact reference into the
engineering system you would actually build and operate.

## D1. The LLMOps operating model

LLMOps is the discipline that makes a probabilistic application releasable and supportable. It
combines:

| Discipline | Question it answers |
|---|---|
| Evaluation | Should this prompt/model/retriever change ship? |
| Telemetry | What is happening in production? |
| Tracing | What happened on this one bad request? |
| Cost management | Who spent what, and why? |
| Deployment control | Which version served which users? |
| Feedback loops | How do production failures become tests? |
| Governance evidence | Can we prove the system is controlled? |

Do not collapse these into one dashboard. Each serves a different decision.

## D2. Eval-driven development - the release discipline

### Definition

Eval-driven development means behavior is specified as datasets and thresholds. You still read
outputs, but release decisions are not based on impressions.

### Scenario

The team changes the grounding prompt:

```
Old: "Answer using the documents."
New: "Answer only if the documents directly support the claim. Otherwise abstain."
```

The new prompt improves faithfulness from 0.89 to 0.95 but raises abstentions from 8% to 22%.
That might be correct if the old system guessed. It might be too conservative. You need the
unanswerable set and human review to know.

### Release scorecard

| Area | Gate |
|---|---|
| Retrieval | hit rate, context recall, context precision |
| Generation | groundedness, answer relevance, correct abstention |
| Agent tools | tool selection accuracy, argument validity, write approval |
| Safety | red-team pass, PII leakage, harmful content blocks |
| Arabic/bilingual | segmented quality and safety |
| Latency | p95/p99 and timeout rate |
| Cost | p50/p95 cost per request, cache hit ratio |

### One-change rule

Do not change model, prompt, chunking and top-k together unless you are doing a controlled
bundle release. If metrics move, you will not know why.

### What breaks

- The team accepts a better average score that hides worse Arabic performance.
- Prompt changes are shipped as "copy tweaks" without evaluation.
- The golden set contains only easy answerable questions, rewarding hallucination.

## D3. Evaluation harness architecture

### Definition

The harness is a pipeline that runs cases, captures artifacts, scores outputs and compares
against a baseline.

### Dataset row shape

```json
{
  "id": "hr-rag-094",
  "question": "Can Grade B employees carry leave into next year?",
  "question_ar": "...",
  "as_user": "employee-grade-b",
  "expected_behavior": "answer",
  "gold_answer": "Only up to 5 days may be carried over with manager approval.",
  "gold_chunk_ids": ["leave-policy-2026::s7.3"],
  "must_not_retrieve": ["exec-comp-policy::all"],
  "category": "entitlement-policy",
  "language": "bilingual",
  "difficulty": "medium"
}
```

A security-sensitive golden set must include the user identity. Without `as_user`, permission
failures are invisible.

### Harness flow

```python
def run_eval_case(case, config):
    with trace_eval(case["id"], config):
        session = login_as(case["as_user"])
        result = run_pipeline(
            question=case["question"],
            session=session,
            prompt_version=config.prompt_version,
            model_route=config.model_route,
            index_version=config.index_version,
        )

        return {
            "case_id": case["id"],
            "answer": result.answer,
            "retrieved_ids": [c.id for c in result.chunks],
            "tool_calls": result.tool_calls,
            "citations": result.citations,
            "usage": result.usage,
            "latency_ms": result.latency_ms,
            "safety": result.safety_decisions,
        }
```

### Scorer split

| Scorer type | Examples | Run cadence |
|---|---|---|
| Deterministic | schema, citation quote check, forbidden chunk, tool args | every commit |
| Retrieval math | hit rate, recall, precision, MRR/NDCG | every commit |
| LLM-as-judge | faithfulness, relevance, coherence | nightly/pre-release |
| Human review | policy correctness, fairness, edge cases | sampled/release |

### LLM-as-judge bias handling

| Bias | Symptom | Mitigation |
|---|---|---|
| Verbosity bias | longer answer scores higher | length-normalized rubric |
| Position bias | first answer wins in pairwise | randomize order |
| Self-preference | same model family favors itself | use independent judge, calibrate |
| Style bias | polished unsupported answer scores high | require citation evidence |
| Language bias | Arabic scored inconsistently | bilingual judge set + human calibration |

### What breaks

- The harness mocks retrieval in a way production does not.
- The eval user is an administrator.
- The judge sees the gold answer when measuring faithfulness and leaks correctness into score.
- The output is scored but traces are not saved, so failures cannot be debugged.

## D4. Metrics - diagnosis, not decoration

### Definition

A metric is useful only if it tells you what to change. For LLM systems, the right structure is
layered metrics.

### Layered metric map

```
User request
  -> input safety metrics
  -> retrieval metrics
  -> generation metrics
  -> tool/action metrics
  -> output safety metrics
  -> UX metrics
  -> cost/latency metrics
```

### Diagnostic patterns

| Observation | Likely cause | Fix |
|---|---|---|
| Low hit rate, high faithfulness | right docs not retrieved | chunking, embeddings, hybrid, filters |
| High hit rate, low faithfulness | model ignores context | grounding prompt, lower temp, validators |
| High relevance, low correctness | source wrong or gold stale | corpus governance |
| High abstention on answerable cases | relevance floor too strict, prompt too conservative | tune retrieval/prompt |
| Low abstention on unanswerable cases | model guessing | nullable schema, abstention reward |
| High tool arg validity, low task success | business workflow issue | validation, orchestration |
| Good p50, bad p99 | tail dependency | timeouts, circuit breakers |
| Quality up, cost up 4x | model or context too large | routing, caching, pruning |

### Segmentation

Always segment by:

- language: English, Arabic, mixed,
- tenant or department,
- channel: Teams, web, API,
- feature: RAG answer, agent action, summarization,
- model route,
- prompt version,
- document source,
- user role/risk class.

Without segmentation, averages lie.

### Metric definitions you should say cleanly

| Metric | Clean definition |
|---|---|
| Groundedness/faithfulness | every material claim is supported by provided context |
| Answer relevance | answer addresses the user's actual question |
| Context recall | required chunks retrieved / required chunks |
| Context precision | relevant retrieved chunks / retrieved chunks, with rank sensitivity |
| Hit rate @k | at least one gold chunk appeared in top-k |
| MRR | reciprocal rank of first relevant result |
| Tool-call accuracy | correct tool selected at the correct step with valid arguments |
| Task success | user goal completed under business rules |
| Correct abstention | system declines when evidence is insufficient |

## D5. Latency telemetry - measuring the path

### Definition

Latency telemetry breaks total time into pieces you can act on. "The model is slow" is often
wrong; retrieval, reranking, a tool API or an approval wait may be the cause.

### Request timeline

```
request received
  -> auth and policy lookup
  -> input guardrails
  -> query rewrite
  -> retrieval
  -> reranking
  -> context assembly/token count
  -> model prefill
  -> first token (TTFT)
  -> streaming decode
  -> output validation
  -> render response
```

For agents, multiply by steps and add tool calls:

```
step 1 model -> tool A -> step 2 model -> tool B -> approval pause -> resume -> step 3 model
```

### Metrics and causes

| Metric | High value usually means |
|---|---|
| Auth latency | identity provider or group expansion slow |
| Retrieval latency | index load, filters, vector parameters |
| Rerank latency | too many candidates, slow cross-encoder |
| TTFT | long input/prefix, model queueing, cold cache |
| Tokens/sec | model tier/capacity |
| p95/p99 | tail dependency or capacity issue |
| Timeout rate | dependency or prompt length beyond design |
| Agent step count | task design or tool failure |

### Controls

- stream human-readable long answers,
- do not stream machine-consumed JSON,
- cache stable prompt prefixes,
- cap retrieved chunks and tool result size,
- use smaller models for routing/classification,
- use parallel read-only tools,
- set timeouts and fallbacks per dependency,
- monitor p95/p99 by feature, not just globally.

### What breaks

- UI looks fast because of streaming, but validators fail after the user saw text.
- Average latency is fine while executives hit p99 timeouts.
- Agent approval wait is counted as model latency.
- Long Arabic prompts have worse tokenization cost and higher TTFT but are not segmented.

## D6. Cost and token monitoring - the unit economics

### Definition

Cost monitoring turns token usage and auxiliary AI calls into product unit economics. You need
to know cost per feature, per tenant, per successful task and per failed task.

### Full cost model

| Cost driver | Often forgotten? |
|---|---|
| Input tokens | no |
| Cached input tokens | yes |
| Output tokens | no |
| Reasoning tokens | yes |
| Embedding tokens at ingestion | yes |
| Query embedding tokens | yes |
| Reranker calls | yes |
| LLM-as-judge eval runs | yes |
| Agent step multiplier | yes |
| Tool/API costs | sometimes |
| Vector store/index capacity | often |
| Logging/tracing storage | often |

### Attribution dimensions

```json
{
  "tenant": "dept-hr",
  "feature": "policy_rag",
  "route": "small_model_answer",
  "prompt_version": "hr-rag-2.3.0",
  "model_deployment": "gpt4o-mini-uaenorth",
  "index_version": "policies-2026-08-01",
  "input_tokens": 5230,
  "cached_input_tokens": 1800,
  "output_tokens": 420,
  "reasoning_tokens": 0,
  "agent_steps": 1,
  "estimated_usd": 0.0041
}
```

### Optimization playbook

| Symptom | Fix |
|---|---|
| Frontier model used for easy tasks | route by task difficulty |
| Prompt cache hit drops | move volatile data later, stabilize schema serialization |
| Context tokens rising | summarize history, prune tools, lower top-k |
| Agent cost high | convert fixed paths to workflows |
| Eval cost high | deterministic retrieval checks in CI, full judge nightly |
| Embedding bill high | incremental sync and content hashes |
| Tenant cost spike | per-tenant quotas and alerts |

### What breaks

- Finance sees a bill but engineering cannot attribute it.
- Failed requests are expensive because retries and agent loops are not counted.
- A model upgrade increases hidden reasoning tokens.
- Popular repeated questions run full RAG every time.

## D7. Tracing - the forensic record

### Definition

Tracing captures the nested operations of a single request. A good trace lets an engineer
reconstruct the answer without guessing.

### Trace anatomy

```
trace: interaction hr-2026-08-17-0019
  span: auth.resolve_principals
  span: safety.input_scan
  span: rag.query_rewrite
  span: rag.vector_search
  span: rag.semantic_rerank
  span: context.assemble
  span: llm.generate
  span: validator.citation_check
  span: safety.output_scan
  span: response.render
```

For an agent:

```
trace
  step 1 llm.plan
  step 1 tool.check_balance
  step 2 llm.plan
  step 2 approval.request
  approval.resume
  step 3 tool.submit_leave
```

### Attributes to include

| Span | Attributes |
|---|---|
| model call | deployment, model, prompt version, token counts, finish reason |
| retrieval | query hash, index version, top-k, filters, chunk IDs |
| reranker | candidate count, selected count, scores |
| tool call | tool name, risk, args hash, auth result, latency |
| approval | approver, decision, evidence ID |
| validators | pass/fail reason, citation IDs |

### Security design

Use IDs, hashes and summaries unless raw content is required. Raw prompts and chunks should be
restricted, encrypted, retained for a defined period and excluded from broad developer access.

### What breaks

- A bad answer arrives and the only record is the final text.
- You know the model was wrong but not which chunks it saw.
- Tool arguments were redacted so aggressively that incident review is impossible.
- Traces are stored outside the required residency boundary.

## D8. SLOs and alerting for AI systems

### Definition

An SLO is a target users and operators can rely on. AI systems need SLOs for behavior, not only
uptime.

### Example SLO set

| Category | SLO |
|---|---|
| Availability | 99.9% requests receive answer, abstention or safe fallback |
| Latency | p95 RAG answer < 4s; p95 TTFT < 1s for streamed answers |
| Retrieval | hit rate @8 >= 0.90 on current golden set |
| Grounding | faithfulness >= 0.90 on sampled traffic |
| Permission safety | zero confirmed cross-user document disclosures |
| Tool safety | zero writes without approval |
| Cost | p95 cost/request under budget per feature |
| Evaluation freshness | golden set reviewed quarterly and after policy changes |

### Alert examples

| Alert | Likely cause |
|---|---|
| cache hit ratio drops below 50% | dynamic data entered prompt prefix |
| retrieval no-result rate spikes | index sync failure |
| p95 tool latency spikes | backend dependency degraded |
| abstention rate drops sharply | grounding prompt regression |
| prompt-injection detections spike | attack or poisoned source |
| cost/request doubles | model route or context regression |

### What breaks

- Availability is green while answers are ungrounded.
- Quality SLOs exist but are not tied to release gates.
- Alerts fire with no owner or runbook.

## D9. Telemetry retention and privacy

### Definition

Telemetry retention decides what gets stored and when it is deleted. AI telemetry is sensitive
because it contains user questions, retrieved content, tool arguments and model outputs.

### Retention tiers

| Tier | Contents | Retention |
|---|---|---|
| Aggregated metrics | counts, latency, cost | long-lived |
| Structured trace metadata | IDs, versions, timings, pass/fail | medium |
| Raw prompts/responses | full text | short, restricted |
| Tool results/retrieved chunks | source-system data | minimize or store IDs |
| Approval records | official action evidence | according to business/legal policy |
| Eval datasets | curated examples | governed like source data |

### Design choices

- redact before exporting telemetry,
- keep raw content sampling low and justified,
- separate audit retention from debug retention,
- honor deletion requests across traces and eval copies,
- store telemetry in approved regions,
- restrict who can query raw traces.

### What breaks

- Debug logs become a shadow database of HR records.
- Eval examples copied from production are kept forever.
- Deletion processes ignore telemetry and caches.

## D10. Feedback loops and incident management

### Definition

Feedback loops convert production evidence into improved systems. They are not the same as
training on user feedback automatically.

### Triage taxonomy

| Failure layer | Example | Owner |
|---|---|---|
| Source content | policy outdated | content owner |
| Ingestion | document missing or OCR bad | data pipeline |
| Retrieval | wrong chunk | search/RAG engineer |
| Generation | unsupported claim | prompt/model owner |
| Tool | wrong action proposed | agent/tool owner |
| Safety | false block or missed leak | security/RAI |
| UX | user misunderstood answer | product owner |

### Incident workflow

```
feedback/incident
  -> pull trace and audit record
  -> classify failure layer
  -> assess severity and data impact
  -> fix source/prompt/retriever/tool/control
  -> add regression case
  -> run eval
  -> deploy with canary
  -> close with evidence
```

### What breaks

- Every incident becomes "prompt needs improvement."
- Feedback is too sparse because the UI asks only thumbs up/down.
- Human corrections are not tied to the original trace.
- Support teams cannot see the evidence needed for triage.

## D11. Deployment discipline - prompts, models, indexes and tools

### Definition

AI deployment is not just application deployment. Four artifacts change independently:

1. prompt templates,
2. model deployments,
3. embedding/reranker/index versions,
4. tool schemas and orchestration logic.

### Version bundle

```yaml
release: hr-assistant-2026.08.17
app_version: 3.4.2
prompt_version: hr-rag-2.3.0
model_route:
  answer: gpt4o-mini-uaenorth-2026-07
  verifier: gpt4o-uaenorth-2026-07
embedding:
  model: multilingual-embed-v4
  index: policies-embed-v4-2026-08-01
reranker: semantic-ranker-v2
tool_schema_version: hr-tools-1.8.0
eval_baseline: eval-run-2026-08-16
```

### Canary vs shadow

| Pattern | User impact | Use when |
|---|---|---|
| Shadow | candidate runs but user sees old output | safety comparison, model migration |
| Canary | small user percentage sees candidate | real UX/product validation |
| A/B | controlled split to compare variants | enough traffic and clear metric |
| Rollback | return to known-good bundle | incident response |

### What breaks

- Model deployment changes but prompt stays tuned to old behavior.
- Embedding model changes but the index is not rebuilt.
- Tool schema changes invalidate prompt caching and tool selection.
- Rollback restores the app but not the index or prompt.

---

# Part C - Stage 6 assembled

## C1. One release, end to end

```
CHANGE: replace reranker and update grounding prompt.

1. Create candidate config with pinned versions                [8.5.7]
2. Run deterministic retrieval metrics in CI                   [8.5.1 / 8.5.2]
3. Run full LLM-judged eval nightly/pre-release                [8.5.1]
4. Compare quality, safety, latency and cost to baseline       [8.5.2 / 8.5.3 / 8.5.4]
5. Run red-team and permission-sensitive cases                 [8.6 / 8.5.1]
6. Shadow on sampled production traffic                        [8.5.7]
7. Canary to 5-10% if shadow is clean                          [8.5.7]
8. Watch dashboards and traces                                 [8.5.5]
9. Roll forward, roll back or fix                              [8.5.6 / 8.5.7]
```

## C2. Operational dashboard

| Panel | Signals |
|---|---|
| Quality | groundedness, relevance, abstention, task success |
| Retrieval | hit rate, context recall/precision, no-result rate |
| Safety | filter blocks, prompt-injection detections, red-team pass |
| Cost | tokens, cached tokens, cost/request, budget burn |
| Latency | TTFT, tokens/sec, p50/p95/p99, timeouts |
| Agents | steps/run, tool errors, approval waits, thrashing |
| Feedback | thumbs, incidents, human-review queue |

## C3. What Stage 6 hands to Stage 7

Stage 6 gives us the discipline of production AI. Stage 7 applies the same discipline to
classic ML: datasets, metrics, registries, deployment, drift, monitoring and lifecycle support.

## C4. Self-test

1. Offline vs online evaluation: what does each catch?
2. Why is LLM-as-judge useful and dangerous?
3. Context recall is low but faithfulness is high. What do you fix?
4. Define TTFT, tokens/sec, p95 and p99.
5. What fields are needed for per-tenant cost accounting?
6. What does a trace contain that a metric does not?
7. Give three AI SLOs that are not simple uptime.
8. Why is telemetry retention a data-protection issue?
9. What is the difference between canary and shadow deployment?
10. Why must embedding model upgrades version the index?

---

*End of Stage 6. Continue to `07-Stage7-Classic-ML-MLOps.md`.*
