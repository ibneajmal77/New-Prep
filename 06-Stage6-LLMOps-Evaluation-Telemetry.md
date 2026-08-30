# Stage 6 - LLMOps, Evaluation & Telemetry (8.5)

**Rules status:** legacy v1 shape, migration debt tracked in §8

*Three parts: **Part A** is the build narrative. **Part B** is the complete reference — every
fact for a topic lives there, in full, once. **Part C** assembles it into a revision-ready
whole. Stage 5 defined the controls; Stage 6 proves whether the system is actually working,
safe, fast and affordable.*

**Where we are:** The assistant now has RAG, tools, approvals and guardrails. That is still not
production. Production needs evidence: regression tests, quality metrics, traces, cost
accounting, latency SLOs, feedback loops and controlled deployment of prompts and models.

*Order note: the topics appear here in the order a release encounters them, not in numeric order
— 8.5.10 comes first because it frames everything else, 8.5.4 precedes 8.5.3 because latency is
what users report and cost is what finance reports, and 8.5.7 comes last because deployment is
what all the preceding measurement is for. The numbers themselves never change.*

---

# Part A - THE BUILD: Stage 6

## Step 1. "It seems better" is not an engineering statement

Someone changes chunk size, the prompt and the model in the same week. Complaints drop, but
cost doubles and Arabic answers get worse. We need eval-driven development: every change must
be judged against the same dataset and metrics.

> **→ [8.5.10 Eval-driven development](#8510-eval-driven-development-)**

## Step 2. Build the automated evaluation harness

The golden set from Stage 3 becomes a regression suite. It runs in CI for deterministic checks,
nightly for LLM-judged checks, and before every prompt/model release.

> **→ [8.5.1 Evaluation harness](#851-evaluation-harness)**

## Step 3. Decide which metrics matter

Groundedness, answer relevance, coherence, toxicity, task success, tool-call accuracy and
retrieval metrics measure different failures. A single score hides the diagnosis.

> **→ [8.5.2 Metrics](#852-metrics)**

## Step 4. Users say it is slow

Total latency is not enough. For streaming experiences, time to first token matters. For agents,
tool latency and step count matter. For operations, p95 and p99 matter more than averages.

> **→ [8.5.4 Latency telemetry](#854-latency-telemetry)**

## Step 5. Finance asks why the bill doubled

Token use must be attributed by user, tenant, feature, model, prompt version and route. Without
that, cost optimization is guessing.

> **→ [8.5.3 Cost & token monitoring](#853-cost--token-monitoring)**

## Step 6. One bad answer needs a trace

The complaint is one answer, not a dashboard. We need the full trace: request, retrieval,
reranker, prompt version, model call, tool calls, approval and validators.

> **→ [8.5.5 Tracing](#855-tracing)**

## Step 7. Define what reliability means for an AI system

Traditional uptime is not enough. The model can be up and still ungrounded, unsafe, too slow or
too expensive. AI SLOs must include quality and budget signals.

> **→ [8.5.8 SLOs for AI systems](#858-slos-for-ai-systems-)**
> **→ [8.5.9 Telemetry retention policy](#859-telemetry-retention-policy-)**

## Step 8. Learn from production without letting production train the model blindly

Thumbs up/down, incident triage and human review loops are evidence. They must feed the golden
set, prompt backlog and red-team suite. They should not become unfiltered training data.

> **→ [8.5.6 Feedback loops](#856-feedback-loops)**

## Step 9. Roll out prompts and models like software

Prompts, model deployments, embedding models and rerankers all need versioning, canaries,
shadow tests, rollback and deprecation handling.

> **→ [8.5.7 Canary, shadow deployment and version pinning](#857-canary-shadow-deployment-and-version-pinning)**

---

# Part B — THE REFERENCE

## 8.5.10 Eval-driven development `+`
> **In the build:** Stage 6, Step 1 — *"it seems better is not an engineering statement."*

### 1. Definition

```
   TEST-DRIVEN DEVELOPMENT          EVAL-DRIVEN DEVELOPMENT
   ───────────────────────          ───────────────────────
   one expected string              THRESHOLDS over a representative DATASET
   pass / fail                      a scorecard that can move in two directions
   deterministic                    probabilistic — the same input can vary

   THE LOOP
   define behavior → build golden set → RUN BASELINE → make ONE change
        → compare metrics → inspect failures → ship or revert
                                                    │
                          ┌─────────────────────────┘
                          ▼
   ⚠ THE TRAP THAT MAKES THIS NECESSARY:
     grounding prompt changed from "answer using the documents"
                               to "answer only if directly supported, else abstain"
        faithfulness   0.89 → 0.95    ← looks like a clear win
        abstention      8%  →  22%    ← is this CORRECT, or too conservative?
     You cannot tell from the average. You need the UNANSWERABLE set
     (did it correctly decline?) and human review (was the 22% right?).

   THE ONE-CHANGE RULE
     model · prompt · chunking · top-k · reranker
     Change these TOGETHER and metrics move for reasons you cannot attribute.
```

**Plain English:** every prompt, model, retrieval or tool change must pass a measurable
evaluation before release — not an impression.

**Precisely:** eval-driven development specifies behaviour **as datasets and thresholds**. It is
test-driven development adapted to probabilistic systems: not "one expected string", but
thresholds over a representative dataset. You still read outputs — but **release decisions are
not based on impressions**.

### 2. Scenario

Someone changes chunk size, the prompt and the model in the same week. Complaints drop, cost
doubles, and **Arabic answers get worse**. Three questions have no answer:

- Which change caused the improvement?
- Which caused the cost rise?
- Did anyone notice the Arabic regression, and against what baseline?

The average moved favourably, so the change shipped. **A better average score that hides worse
Arabic performance is the exact failure this practice exists to prevent.**

### 3. Example — the release scorecard

Every gate below must be read before shipping. A single number cannot represent this:

| Area | Gate |
|---|---|
| Retrieval | Hit rate, context recall, context precision |
| Generation | Groundedness, answer relevance, **correct abstention** |
| Agent tools | Tool selection accuracy, argument validity, write approval |
| Safety | Red-team pass, PII leakage, harmful content blocks |
| **Arabic / bilingual** | **Segmented quality and safety** |
| Latency | p95 / p99 and timeout rate |
| Cost | p50 / p95 cost per request, cache hit ratio |

### 4. How it works

**The rules, and each closes a specific way teams fool themselves:**

- **Change one major variable at a time** — model, prompt, chunking, top-k, reranker. If metrics
  move after a bundle change, you have learned nothing about which lever did it.
- **Keep a baseline run** for comparison. "Better" is meaningless without a stored prior.
- **Split retrieval metrics from generation metrics** (8.5.2). One aggregate quality number
  destroys the diagnosis.
- **Include unanswerable, Arabic/bilingual and permission-sensitive cases.** A set of easy
  answerable questions **rewards hallucination**, because guessing scores well.
- **Add every production incident to the dataset, permanently.** The set should grow
  monotonically and become the institutional memory of everything that has gone wrong.

⚠ **Cost and latency belong on the scorecard.** A change that is 3% better and 40% more expensive
is a business decision, not an automatic win — and if cost is not on the card, nobody makes that
decision consciously.

### 5. Where it fits

```
▶  EVAL-DRIVEN DEVELOPMENT  ◀ ─── the frame around every other topic in this stage
        │
        ├── needs a golden set ............ 8.3.8.10 (built in Stage 3)
        ├── run by the harness ............ 8.5.1
        ├── scored by metrics ............. 8.5.2
        ├── gated on latency and cost ..... 8.5.4, 8.5.3
        ├── debugged through traces ....... 8.5.5
        └── released through canary ....... 8.5.7
```

### 6. Libraries & code

| Job | How |
|---|---|
| Dataset | Version-controlled JSONL beside the prompts (8.2.3) |
| Runner and scorers | RAGAS, Azure AI Evaluation SDK, DeepEval, promptfoo |
| Baseline store | A named eval run ID recorded in the release bundle |
| CI gate | `pytest` asserting thresholds; deterministic checks on every commit |
| Comparison | Pairwise A/B with randomized order to defeat position bias |

### 7. Knobs & real numbers

| Knob | Typical | Notes |
|---|---|---|
| Variables changed per release | **1** | Or an explicitly controlled bundle |
| Deterministic checks | every commit | Free and fast |
| LLM-judged checks | nightly + pre-release | Slower, noisier, costs money |
| Golden set size | 200–500 working (8.3.8.10) | 50 to start is better than none |
| Unanswerable share | ~15% | The category that catches guessing |
| Bilingual share | ~15% | Or you measure half the service |
| Threshold movement | ratchet **up** only | Lowering a threshold to pass is the anti-pattern |

### 8. Perspectives grid

| Lens | What matters here |
|---|---|
| **Theory** | A probabilistic system has no single correct output, so correctness must be defined statistically — as thresholds over a distribution of representative cases. |
| **Engineering** | One change at a time. Keep the baseline. Split retrieval from generation. Put cost and latency on the same card as quality. |
| **Operations** | The golden set rots as policies change. Re-review it quarterly — a stale set reports confident passes against wrong answers. |
| **Cost** | Deterministic scorers are free; LLM judges are not. Run the free ones constantly and the expensive ones on a cadence. |
| **Security** | Permission-sensitive and red-team cases belong in the same gate as quality, or safety regressions ship on a green build. |
| **Decision** | No prompt, model, index or tool change ships without a scorecard comparison against a stored baseline. If there is no baseline, creating one is the first task. |

### 9. Trade-offs & failure modes

- **The demo question set treated as an evaluation set.**
- **A single LLM judge score deciding release.**
- **Cost and latency missing from the scorecard.**
- **Thresholds lowered to make a release pass.** The metric now measures nothing.
- **A better average hiding worse Arabic performance.**
- **Prompt changes shipped as "copy tweaks" without evaluation.**
- **A golden set of only easy answerable questions**, which rewards hallucination.

---

## 8.5.1 Evaluation harness
> **In the build:** Stage 6, Step 2 — *"build the automated evaluation harness."*

### 1. Definition

```
   GOLDEN DATASET ──┐
   (with as_user!)  │
                    ▼
              ┌──────────┐   runs the SAME production path — auth, prompt
              │  RUNNER  │   assembly, retrieval filters and all
              └────┬─────┘   (a harness that mocks retrieval tests a system
                   │          that does not exist)
                   ▼
   ┌───────────────────────────────────────────────────────────────┐
   │ SCORERS — split by cost and determinism, not by importance     │
   ├────────────────────┬────────────────────────┬─────────────────┤
   │ DETERMINISTIC      │ RETRIEVAL MATH         │ LLM-AS-JUDGE    │
   │ schema · citation  │ hit rate · recall ·    │ faithfulness ·  │
   │ quote check ·      │ precision · MRR/NDCG   │ relevance ·     │
   │ forbidden chunk ·  │                        │ coherence       │
   │ tool args          │                        │                 │
   │ EVERY COMMIT       │ EVERY COMMIT           │ NIGHTLY + REL.  │
   │ free               │ free                   │ costs money     │
   └────────────────────┴────────────────────────┴─────────────────┘
                   │              plus HUMAN REVIEW, sampled, for
                   ▼              policy correctness and fairness
            ┌──────────────┐
            │ BASELINE     │  compare candidate vs stored prior
            │ STORE        │
            └──────┬───────┘
                   ▼
            ┌──────────────┐
            │  CI GATE     │  blocks regressions; thresholds ratchet UP
            └──────────────┘

   ⚠ THE GOLDEN SET ROW MUST CARRY `as_user`.
     Without an identity, permission failures are STRUCTURALLY INVISIBLE —
     and an eval run as an administrator can never catch a trimming bug.
```

**Plain English:** the machinery that runs your test cases through the real pipeline, scores
what comes out, compares it to last time, and stops a bad change from shipping.

**Precisely:** an evaluation harness is the repeatable system that runs test cases through the
AI pipeline, scores the result, compares against baselines and **blocks regressions**.

### 2. Scenario

The golden set from Stage 3 (8.3.8.10) exists. It now has to become an operational gate — which
raises questions the dataset alone does not answer: which path does it run through? who is it
run *as*? what is compared against what? which failures block a release and which are logged?

And the trap: a harness that mocks retrieval, bypasses authorization or assembles the prompt
differently from production **tests a system that does not exist**. Its green build means
nothing.

### 3. Example — the dataset row, and the CI gate

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

`must_not_retrieve` is the field that turns a quality dataset into a **security** dataset: it
asserts a negative, which is the only way a permission-trimming regression gets caught
automatically.

```python
def test_rag_release_candidate():
    records = run_golden_set(prompt_version="hr-rag-2.3.0", model_route="candidate")
    metrics = score(records)

    assert metrics["retrieval_hit_rate_at_8"]   >= 0.90
    assert metrics["context_recall"]            >= 0.85
    assert metrics["faithfulness"]              >= 0.90
    assert metrics["correct_abstention_rate"]   >= 0.90
    assert metrics["permission_leak_count"]     == 0     # not a threshold — a zero
```

### 4. How it works

**The six components:**

| Component | Purpose |
|---|---|
| Golden dataset | Questions, expected answers, gold chunks, **users and permissions** |
| Runner | Executes the **same production path**, or a controlled offline copy of it |
| Scorers | Deterministic metrics, plus LLM-as-judge where needed |
| Baseline store | Previous prompt/model/index results |
| CI gate | Blocks unsafe regressions |
| Review UI | Human review of ambiguous failures |

**Four evaluation modes, each catching what the others miss:**

| Mode | Use for | Weakness |
|---|---|---|
| Offline eval | Release gates, prompt/model comparison | **The dataset goes stale** |
| Online eval | Sampled production traffic, drift detection | Ground truth is delayed or absent |
| Human review | High-stakes and ambiguous cases | Expensive, slower |
| Pairwise comparison | Prompt/model A vs B | Needs consistent judge criteria |

**LLM-as-judge is useful and biased**, and naming the biases is the examinable part:

| Bias | Symptom | Mitigation |
|---|---|---|
| **Verbosity** | Longer answers score higher | Length-normalized rubric |
| **Position** | The first answer wins in pairwise | **Randomize order** |
| **Self-preference** | A model family favours its own outputs | Independent judge, calibrate to human labels |
| **Style** | A polished but unsupported answer scores well | **Require citation evidence** |
| **Language** | Arabic scored inconsistently | Bilingual judge set + human calibration |

⚠ **Never use an LLM judge as the only gate for security-sensitive behaviour.** Permission leaks
and unapproved writes are deterministic checks with a threshold of zero.

⚠ **Do not let the judge see the gold answer when measuring faithfulness** — it leaks
correctness into a score that is supposed to measure support-by-context.

### 5. Where it fits

```
   ▶ THE HARNESS ◀ wraps the ENTIRE pipeline, which is why it must not shortcut it
        │
   golden set → login_as(case.as_user) → run_pipeline(prompt_v, model_route, index_v)
        │                                       │
        │                              the real auth, the real filters,
        │                              the real prompt assembly
        ▼
   artifacts: answer · retrieved_ids · tool_calls · citations · usage
              · latency_ms · safety decisions   ← save ALL of it, or failures
        │                                          cannot be debugged later
        ▼
   scorers → baseline comparison → CI gate → release (8.5.7)
```

### 6. Libraries & code

| Job | Library |
|---|---|
| RAG metrics | **RAGAS** (faithfulness, answer relevance, context precision/recall) |
| Managed evaluation | **Azure AI Evaluation SDK** (`azure-ai-evaluation`) |
| General frameworks | DeepEval, TruLens, promptfoo |
| Datasets and tracing | LangSmith, Azure AI Foundry evaluation |
| CI | `pytest` + any of the above |
| Human review | A simple queue UI over failed and ambiguous cases |

### 7. Knobs & real numbers

| Knob | Typical | Notes |
|---|---|---|
| Retrieval hit rate @8 | ≥ 0.90 | The ceiling on everything downstream |
| Context recall | ≥ 0.85 | Low → chunking and retrieval |
| Faithfulness | ≥ 0.90 | Low → grounding prompt |
| Correct abstention | ≥ 0.90 on the unanswerable set | Frequently the worst-performing metric |
| Permission leak count | **exactly 0** | A zero, never a threshold |
| Deterministic scorers | every commit | Free and fast |
| LLM-judged scorers | nightly + release candidates | A few dollars per full run |
| Judge calibration | spot-check against human labels | Otherwise you are trusting a biased rater |

### 8. Perspectives grid

| Lens | What matters here |
|---|---|
| **Theory** | Evaluation estimates a distribution from a sample. The sample's composition therefore determines what you can detect — omit a category and it is invisible, not merely under-weighted. |
| **Engineering** | Run the production path. Carry `as_user` on every row. Save all artifacts, not just the answer. Assert zeros for security properties and thresholds for quality ones. |
| **Operations** | Free scorers on every commit, expensive scorers on a cadence. Review the golden set quarterly, because gold answers go stale when policy changes. |
| **Cost** | Retrieval metrics are free and deterministic; LLM-judged runs cost a few dollars. That asymmetry should drive the cadence, not convenience. |
| **Security** | Evaluate **as different users**. A harness run as an administrator will never catch a permission-trimming failure, and that failure is the one that becomes an incident. |
| **Decision** | Gate CI on the cheap deterministic checks, gate release on the full run, and never lower a threshold to make a build green. |

### 9. Trade-offs & failure modes

- **The harness bypassing production authorization or prompt assembly.**
- **Only happy-path answerable questions included.**
- **Evaluation running as an admin user.** Permission failures become structurally invisible.
- **Golden answers not reviewed when policies change.**
- **Retrieval mocked in a way production is not.**
- **The judge seeing the gold answer while measuring faithfulness.**
- **Outputs scored but traces not saved**, so failures cannot be debugged.

---

## 8.5.2 Metrics
> **In the build:** Stage 6, Step 3 — *"decide which metrics matter."*

### 1. Definition

```
   A METRIC IS USEFUL ONLY IF IT TELLS YOU WHAT TO CHANGE.

   User request
     ├─► INPUT SAFETY metrics    · injection detections, filter blocks
     ├─► RETRIEVAL metrics       · hit rate, context recall, context precision, MRR
     ├─► GENERATION metrics      · groundedness, relevance, coherence, abstention
     ├─► TOOL / ACTION metrics   · tool-call accuracy, argument validity, task success
     ├─► OUTPUT SAFETY metrics   · PII leaks, harmful content, protected material
     ├─► UX metrics              · thumbs, escalation rate, abandonment
     └─► COST / LATENCY metrics  · tokens, cost/request, TTFT, p95, p99

   THE SPLIT THAT MAKES DIAGNOSIS POSSIBLE — read the PAIR, never the average
   ┌──────────────────────────────┬─────────────────────────────────────────┐
   │ low recall + HIGH faithful   │ → the right docs were not retrieved.     │
   │                              │   FIX RETRIEVAL. A better model changes  │
   │                              │   almost nothing.                        │
   ├──────────────────────────────┼─────────────────────────────────────────┤
   │ HIGH recall + low faithful   │ → it had the context and ignored it.     │
   │                              │   FIX GENERATION: grounding prompt,      │
   │                              │   temperature, validators.               │
   ├──────────────────────────────┼─────────────────────────────────────────┤
   │ low tool-call accuracy       │ → FIX TOOL SCHEMAS AND ORCHESTRATION     │
   ├──────────────────────────────┼─────────────────────────────────────────┤
   │ good quality + bad p95       │ → FIX ROUTING, CACHING OR TOOLS          │
   └──────────────────────────────┴─────────────────────────────────────────┘

   ⚠ ONE AGGREGATE "AI QUALITY" NUMBER DESTROYS EXACTLY THE INFORMATION
     YOU NEED TO ACT. And without SEGMENTATION, averages lie.
```

**Plain English:** the signals that tell you not just *that* something is wrong but *which layer*
is wrong.

**Precisely:** metrics are the observable signals that identify the failing layer. In LLM
systems, quality, safety, task success, retrieval, latency and cost all need **separate**
measures, because they fail independently and are fixed independently.

### 2. Scenario

Quality is disappointing. Three plausible proposals land in the same meeting: increase chunk
size, use a better model, retrieve more chunks. Each takes days to try, and each is a guess.

With the metrics split, the diagnosis takes minutes — and frequently the expensive proposal is
the wrong one. A better model changes almost nothing when the right chunk was never retrieved.

### 3. Example — the metric map

| Metric | Answers | Fix when low |
|---|---|---|
| Groundedness / faithfulness | Are claims supported by context? | Grounding prompt, citations, validators |
| Answer relevance | Did it answer the question asked? | Prompt, query rewrite |
| Coherence / fluency | Is it readable and internally consistent? | Model / prompt |
| Toxicity / safety | Is content harmful or disallowed? | Filters, policy, prompt |
| Task success | Did the workflow complete correctly? | Orchestrator, tools, UX |
| Tool-call accuracy | Right tool, right args, right time? | Tool schemas and descriptions, examples |
| Retrieval hit rate | Did the gold chunk appear in top-k? | Chunking, embeddings, search |
| Context precision / recall | Were retrieved chunks relevant and complete? | Reranking, top-k, filters |
| Abstention rate | Did it say "I don't know" when it should? | Grounding policy, thresholds |

### 4. How it works

**The definitions to be able to state cleanly** — imprecision here is what makes dashboards
uninterpretable:

| Metric | Clean definition |
|---|---|
| Groundedness / faithfulness | Every material claim is supported by the provided context |
| Answer relevance | The answer addresses the user's actual question |
| Context recall | Required chunks retrieved ÷ required chunks |
| Context precision | Relevant retrieved chunks ÷ retrieved chunks, **with rank sensitivity** |
| Hit rate @k | At least one gold chunk appeared in top-k |
| MRR | Reciprocal rank of the first relevant result |
| Tool-call accuracy | Correct tool selected at the correct step with valid arguments |
| Task success | The user's goal completed under business rules |
| Correct abstention | The system declines when evidence is insufficient |

**The diagnostic patterns — this table is the working content of the section:**

| Observation | Likely cause | Fix |
|---|---|---|
| Low hit rate, high faithfulness | Right docs not retrieved | Chunking, embeddings, hybrid, filters |
| High hit rate, low faithfulness | Model ignores the context | Grounding prompt, lower temperature, validators |
| High relevance, low correctness | Source is wrong, or the gold answer is stale | Corpus governance |
| High abstention on **answerable** cases | Relevance floor too strict, prompt too conservative | Tune retrieval and prompt |
| Low abstention on **unanswerable** cases | The model is guessing | Nullable schema, reward abstention |
| High tool-arg validity, low task success | Business workflow issue | Validation, orchestration |
| Good p50, bad p99 | A tail dependency | Timeouts, circuit breakers |
| Quality up, cost up 4× | Model or context too large | Routing, caching, pruning |

**Segmentation is not optional — always segment by:** language (English, Arabic, mixed) ·
tenant or department · channel (Teams, web, API) · feature (RAG answer, agent action,
summarization) · model route · prompt version · document source · user role or risk class.
**Without segmentation, averages lie** — and the specific lie in a bilingual entity is that
overall quality improves while Arabic quality falls.

### 5. Where it fits

```
   ▶ METRICS ◀ are computed at every boundary the request crosses
        │
   input scan ─► retrieval ─► generation ─► tools ─► output scan ─► response
        │            │             │           │          │            │
        ▼            ▼             ▼           ▼          ▼            ▼
     blocks      hit rate     groundedness  accuracy   PII leaks    latency
                 recall       relevance     task       harmful      cost
                 precision    abstention    success    content      tokens
        │
        └──► fed by the harness offline (8.5.1) AND sampled online from traces (8.5.5)
```

### 6. Libraries & code

| Job | Library |
|---|---|
| RAG metric set | RAGAS |
| Managed evaluators | Azure AI Evaluation SDK |
| Retrieval math | Your own — hit rate, recall, precision, MRR are a few lines and free |
| Safety metrics | Content Safety categories and severities (8.6.3) |
| Dashboards | Application Insights / Azure Monitor, KQL over emitted metrics |
| Segmentation | Emit dimensions on every metric — language, tenant, route, prompt version |

### 7. Knobs & real numbers

| Metric | Reasonable target | Notes |
|---|---|---|
| Retrieval hit rate @8 | > 0.90 | The ceiling on everything downstream |
| Context recall | > 0.85 | Low → chunking and retrieval |
| Context precision | > 0.75 | Low → reranking and top-k |
| Faithfulness | > 0.90 | Low → grounding prompt |
| Answer relevance | > 0.85 | Low → query rewriting |
| Correct abstention | > 0.90 on unanswerable | Often the worst-performing metric |
| Tool-call accuracy | ≥ 0.95 on the golden set | Low → schemas and descriptions |
| Segmentation dimensions | 8 (listed above) | Missing one hides a regression |

### 8. Perspectives grid

| Lens | What matters here |
|---|---|
| **Theory** | Retrieval and generation fail independently and are fixed independently, so any single "quality score" destroys the information required to act. |
| **Engineering** | Compute deterministic retrieval metrics yourself — they are free. Reserve LLM judging for generation. Emit segmentation dimensions on every metric at write time. |
| **Operations** | Read metrics in *pairs*, not individually: recall-with-faithfulness is a diagnosis, either one alone is a number. Alert on abstention rate falling — it usually means retrieval broke. |
| **Cost** | Retrieval metrics cost nothing. Judged metrics cost a few dollars a run — trivial against shipping a regression, so the constraint is cadence, not budget. |
| **Security** | Permission leaks and unapproved writes are metrics too, and their target is zero rather than a threshold. Keep them on the same dashboard as quality. |
| **Decision** | Pick the metric that names the layer you would fix. If a proposed metric would not change any decision, it is decoration. |

### 9. Trade-offs & failure modes

- **One aggregate "AI quality" number** hiding the failure layer.
- **Only user thumbs up/down used** — sparse, biased and without context.
- **Metrics not segmented** by language, tenant, channel and task type.
- **Reading recall or faithfulness alone** rather than as a pair.
- **Correctness confused with faithfulness** — a perfectly faithful answer is wrong if the source
  document is wrong. Faithfulness is what the system is responsible for; correctness depends on
  the corpus.
- **No abstention metric**, so guessing is silently rewarded.

---

## 8.5.4 Latency telemetry
> **In the build:** Stage 6, Step 4 — *"users say it is slow."*

### 1. Definition

```
   "THE MODEL IS SLOW" IS USUALLY WRONG. Break the path into pieces you can act on.

   request received
     → auth and policy lookup      ← identity provider / group expansion
     → input guardrails
     → query rewrite
     → retrieval                   ← index load, filters, vector parameters
     → reranking                   ← candidate count, cross-encoder speed
     → context assembly / token count
     → model PREFILL               ← driven by INPUT length
     → ★ FIRST TOKEN (TTFT)        ← what the user actually perceives as "start"
     → streaming decode            ← tokens/sec, driven by OUTPUT length
     → output validation
     → render response

   FOR AGENTS, MULTIPLY BY STEPS AND ADD TOOLS AND WAITS:
     step 1 model → tool A → step 2 model → tool B
       → ⚠ APPROVAL PAUSE (hours) → resume → step 3 model
     Counting the approval wait as model latency makes the model look broken.

   ⚠ STREAMING IMPROVES PERCEIVED LATENCY, NOT TOTAL LATENCY.
     Sometimes total is marginally worse.
   ⚠ REPORT p95/p99, NOT AVERAGES. The average is fine while executives time out.
```

**Plain English:** measure where the time actually goes, in pieces, so you fix the slow part
rather than the visible part.

**Precisely:** latency telemetry measures time spent in request queueing, retrieval, reranking,
model prefill, time to first token, token streaming, tool calls, approvals and validators —
separately, and at the tail rather than the mean.

### 2. Scenario

Users say the assistant is slow. The dashboard shows average end-to-end latency of 2.1 seconds,
which looks acceptable, and nobody can reproduce the complaint.

Three things are true simultaneously: **p99 is 14 seconds** for a subset of requests; the slow
part is the **reranker**, not the model; and one team's "slow" is actually an **agent approval
wait** being counted as latency. The average concealed all three.

### 3. Example

```python
with tracer.start_as_current_span("rag_request") as span:
    t0 = now()
    chunks = timed("retrieval", retrieve)(question)
    ranked = timed("rerank", rerank)(chunks)
    stream = client.responses.create(..., stream=True)
    for event in stream:
        if first_token_not_seen and event.type == "output_text.delta":
            # TTFT is the number the user experiences as "it started answering".
            span.set_attribute("llm.ttft_ms", ms_since(t0))
        yield event
    span.set_attribute("llm.total_ms", ms_since(t0))
```

### 4. How it works

**The metrics, and what a high value usually means:**

| Metric | Meaning | High value usually means |
|---|---|---|
| **TTFT** | Time to first token — user-perceived start | Long input/prefix, model queueing, cold cache |
| **Tokens/sec** | Generation throughput after first token | Model tier or capacity |
| End-to-end latency | Full user request duration | — |
| **p50 / p95 / p99** | Median, slow tail, extreme tail | Tail dependency or capacity issue |
| Step count | Agent iterations | Task design or tool failure (8.4.1) |
| Tool latency | Time per external dependency | A degraded backend |
| Timeout rate | Requests terminated by a limit | Dependency, or prompt length beyond design |
| Fallback rate | Primary model failed or was bypassed | Capacity or provider issue |
| Auth latency | Identity provider, group expansion | Transitive membership resolution (8.3.5.8) |
| Retrieval latency | Index load, filters, vector parameters | An unindexed filter forcing a scan (8.3.4) |
| Rerank latency | Too many candidates, slow cross-encoder | 50–300 ms for 30 candidates is `typical` |

**The controls, in rough order of leverage:**

- **Stream long human-readable answers; do not stream machine-consumed JSON** (8.1.10) — the
  latter gets all the complexity and none of the benefit.
- **Cache stable prompt prefixes** (8.2.5) — TTFT improvement is often 30–80% on long prefixes.
- **Cap retrieved chunks and tool result size** (8.2.4).
- **Use smaller models for routing and classification** (8.1.3).
- **Parallelise read-only tools** — never writes (8.4.2).
- **Set timeouts and fallbacks per dependency.**
- **Monitor p95/p99 by feature**, not globally.

⚠ **Arabic prompts carry a latency cost that is easy to miss:** 2–3× the tokens for the same
meaning (8.1.1) means longer prefill and higher TTFT — and if latency is not segmented by
language, that regression is invisible.

### 5. Where it fits

```
   ▶ LATENCY TELEMETRY ◀ instruments every span in the trace (8.5.5)
        │
        ├── auth · guardrails · rewrite · retrieval · rerank · assembly
        ├── model: PREFILL → TTFT → decode (tokens/sec)
        ├── tools, and for agents the step multiplier
        ├── approval waits — measured SEPARATELY, never as model latency
        └── validation · render
        │
        └──► SLOs (8.5.8) are set on these numbers, at p95, per feature
```

### 6. Libraries & code

| Job | How |
|---|---|
| Spans and attributes | OpenTelemetry, GenAI semantic conventions (8.5.5) |
| Dashboards and alerting | Application Insights / Azure Monitor, KQL |
| TTFT capture | Instrument the first `output_text.delta` in the stream |
| Percentiles | Your metrics backend — store distributions, not averages |
| Per-dependency timeouts | Client configuration on every external call |

### 7. Knobs & real numbers

| Knob | Typical | Notes |
|---|---|---|
| p95 TTFT target | < 1 s for streamed answers | The user-perceived start |
| p95 end-to-end (non-agent) | < 4 s | An SLO, per feature |
| Rerank latency | 50–300 ms for 30 candidates | The main retrieval-side cost |
| Query rewrite | ~100–300 ms | One small-model call |
| Retrieval target | < 100 ms for top-20 | Before reranking (8.3.4) |
| Agent step count | median 3–6 | A median of 9 means task design is wrong |
| Timeout | set per dependency, always | An unset timeout is an outage waiting |
| Reporting statistic | **p95 and p99** | Averages conceal the complaint |

### 8. Perspectives grid

| Lens | What matters here |
|---|---|
| **Theory** | Prefill is driven by input length and determines TTFT; decode is driven by output length and determines tokens/sec. They are two different numbers with two different fixes. |
| **Engineering** | Instrument each stage separately. Capture TTFT explicitly. Set a timeout on every dependency. Never count an approval wait as model latency. |
| **Operations** | Report p95/p99 by feature and by language. The average is the number that makes a real complaint unreproducible. |
| **Cost** | Latency work and cost work share levers — caching, routing to smaller models, trimming context all improve both at once. |
| **Security** | Timeouts and fallbacks are availability controls; without them a degraded dependency becomes an outage, which is an availability incident. |
| **Decision** | Stream prose a human reads live; do not stream anything a validator must check first. Fix the slowest *measured* stage, not the most visible one. |

### 9. Trade-offs & failure modes

- **Average latency reported instead of p95/p99.**
- **Model latency not separated from retrieval and tool latency.**
- **Streaming treated as lower total latency** — it mainly improves *perceived* latency.
- **Timeouts not visible by feature and model route.**
- **The UI looking fast because of streaming while validators fail after the user saw text**
  (8.6.4).
- **Agent approval waits counted as model latency.**
- **Long Arabic prompts not segmented**, hiding a real tokenization-driven TTFT regression.

---

## 8.5.3 Cost & token monitoring
> **In the build:** Stage 6, Step 5 — *"finance asks why the bill doubled."*

### 1. Definition

```
   THE FULL COST MODEL — the right-hand column is where the surprises live
   ┌────────────────────────────────┬──────────────────┐
   │ COST DRIVER                    │ OFTEN FORGOTTEN? │
   ├────────────────────────────────┼──────────────────┤
   │ input tokens                   │ no               │
   │ CACHED input tokens            │ ★ YES            │
   │ output tokens                  │ no               │
   │ REASONING tokens               │ ★ YES            │
   │ embedding tokens at ingestion  │ ★ YES            │
   │ query embedding tokens         │ ★ YES            │
   │ reranker calls                 │ ★ YES            │
   │ LLM-as-judge eval runs         │ ★ YES            │
   │ AGENT STEP MULTIPLIER          │ ★ YES (10-50×)   │
   │ tool / API costs               │ sometimes        │
   │ vector store / index capacity  │ often            │
   │ logging / tracing storage      │ often            │
   └────────────────────────────────┴──────────────────┘

   ATTRIBUTION IS THE WHOLE POINT. Without these dimensions on every record,
   "why did the bill double?" has no answer:
     tenant · feature · route · prompt_version · model_deployment · index_version

   ⚠ THE MONTHLY CLOUD INVOICE IS NOT COST MONITORING.
     It tells you the total, four weeks after you could have acted.
```

**Plain English:** know exactly which user, feature and version spent what — before the invoice
arrives.

**Precisely:** cost monitoring attributes token and service spend to the request, user, tenant,
feature, model, prompt version and agent run. Token monitoring records input, **cached input**,
output, **reasoning tokens where exposed**, embedding tokens, and reranker/model calls.

### 2. Scenario

The bill doubled. Engineering cannot say why, because spend is recorded per subscription and the
questions are all per-something-else: which tenant? which feature? did the prompt cache break?
did a model upgrade start emitting reasoning tokens? are failed requests being retried?

**Every one of those is unanswerable without attribution dimensions written at request time.**
They cannot be reconstructed afterwards.

### 3. Example

```python
emit_metric("llm.usage", {
    "tenant": tenant_id,
    "feature": "hr_rag",
    "route": "small_model_answer",
    "model": response.model,
    "prompt_version": prompt_version,          # cache misses trace back to here (8.2.5)
    "index_version": index_version,
    "input_tokens": usage.input_tokens,
    "cached_input_tokens": usage.cached_input_tokens,   # broken caching is SILENT
    "output_tokens": usage.output_tokens,
    "reasoning_tokens": getattr(usage, "reasoning_tokens", 0),
    "agent_steps": state.steps,                # the 10-50× multiplier (8.4.1)
    "estimated_usd": estimate_cost(usage, response.model),
})
```

A full attribution record, as JSON:

```json
{"tenant": "dept-hr", "feature": "policy_rag", "route": "small_model_answer",
 "prompt_version": "hr-rag-2.3.0", "model_deployment": "gpt4o-mini-uaenorth",
 "index_version": "policies-2026-08-01", "input_tokens": 5230,
 "cached_input_tokens": 1800, "output_tokens": 420, "reasoning_tokens": 0,
 "agent_steps": 1, "estimated_usd": 0.0041}
```

### 4. How it works

**What to record, and why each field exists:**

| Field | Why |
|---|---|
| `tenant_id`, `user_id`, `feature` | Chargeback and abuse detection |
| `model`, `deployment`, `route` | Model-selection optimization |
| `prompt_version` | Prompt regressions **and cache misses** |
| Input / output / cached / reasoning tokens | The actual cost drivers |
| Agent steps, tool calls | The multi-call multiplier |
| Embedding and reranker calls | Hidden RAG costs |
| Estimated cost | Budget alerts |

**The optimization levers, and what each one saves:**

| Lever | Saves |
|---|---|
| **Model routing** | Frontier calls on easy tasks — usually the largest single lever (8.1.3) |
| **Prompt caching** | Repeated stable prefixes — 50–90% on cached input (8.2.5) |
| Context trimming | Unnecessary history, chunks and tool results (8.2.4) |
| Retrieval caching | Repeated popular questions (8.3.10) |
| Batching | Embeddings and offline evals |
| Downgrading / fallback | Non-critical tasks |
| **Agent-to-workflow conversion** | Repeated multi-step cost — 10–50× → 1× (8.4.3.7) |

**The symptom-to-fix playbook:**

| Symptom | Fix |
|---|---|
| Frontier model used for easy tasks | Route by task difficulty |
| **Prompt cache hit drops** | Move volatile data later; stabilize schema serialization |
| Context tokens rising | Summarize history, prune tool results, lower top-k |
| Agent cost high | Convert fixed paths to workflows |
| Eval cost high | Deterministic retrieval checks in CI, full judge nightly |
| Embedding bill high | Incremental sync and content hashes (8.3.1.2) |
| Tenant cost spike | Per-tenant quotas and alerts (8.6.12) |

⚠ **Failed requests are expensive.** Retries and agent loops are paid for and produce nothing —
so cost per *failed* task is a real unit-economics number, not an accounting curiosity.

### 5. Where it fits

```
   every model, embedding and reranker call emits a usage record
        │
▶  COST & TOKEN MONITORING  ◀
        │
        ├── per request  → unit economics: cost per successful and FAILED task
        ├── per tenant   → chargeback, quotas, abuse detection (8.6.12)
        ├── per feature  → budget alerts and SLOs (8.5.8)
        └── per version  → did this prompt/model/index change cost more? (8.5.7)
```

### 6. Libraries & code

| Job | How |
|---|---|
| Usage capture | The `usage` object on every response — input, cached, output, reasoning |
| Price table | Config, never inline in business logic — prices change (`verify`) |
| Aggregation | Application Insights / Azure Monitor; KQL by tenant, feature, route |
| Budget alerts | Threshold alerts per tenant and feature, not per subscription |
| Cache health | `cached_tokens / prompt_tokens` as a first-class metric with an alert |

### 7. Knobs & real numbers

| Knob | Typical | Notes |
|---|---|---|
| Cache hit ratio | 70–95% well-structured | **Alert below ~0.5** — a broken cache is silent |
| Agent vs single answer | **10–50×** | The number to quote before "make everything an agent" |
| Model tier gap | ~15× small vs frontier | The largest single cost lever (8.1.3) |
| Cached-token discount | 50–90% (`verify`) | Input only — output is never cached |
| Reasoning tokens | can be 1,000–20,000+ on hard prompts | Bill can land ~20× above visible tokens |
| Budget scope | per tenant **and** per feature | Per-subscription budgets do not localise a spike |
| Alert on cost/request | doubling | Usually a model route or context regression |

### 8. Perspectives grid

| Lens | What matters here |
|---|---|
| **Theory** | Cost is a function of tokens crossing a boundary, and every architectural choice — context size, model tier, agent steps, cache structure — is a token decision in disguise. |
| **Engineering** | Emit attribution dimensions at request time; they cannot be reconstructed later. Keep the price table in config. Track cached tokens explicitly. |
| **Operations** | Budget alerts belong per tenant and per feature. A subscription-level budget tells you that something spiked, not what. |
| **Cost** | The largest levers in order: routing, agent-to-workflow conversion, caching, context trimming. Micro-optimising embeddings is almost always the wrong place to start. |
| **Security** | Cost telemetry is an abuse-detection signal. A single tenant's spend spiking is how denial of wallet first shows up (8.6.12). |
| **Decision** | Instrument attribution before optimising anything. Without it, every optimisation is a guess and no saving can be attributed to the change that produced it. |

### 9. Trade-offs & failure modes

- **Only the monthly cloud invoice monitored.**
- **Cached tokens not tracked**, so broken prompt caching is invisible — nothing errors, the bill
  just stops falling.
- **Reasoning tokens omitted from the cost model.**
- **Agent cost counted as one model call.**
- **Budgets per subscription but not per tenant or feature.**
- **Finance seeing a bill that engineering cannot attribute.**
- **Failed requests not counted**, though retries and agent loops are fully paid for.
- **Popular repeated questions running full RAG every time** (8.3.10).

---

## 8.5.5 Tracing
> **In the build:** Stage 6, Step 6 — *"one bad answer needs a trace."*

### 1. Definition

```
   METRICS tell you something is wrong.  TRACES show what happened in ONE case.
   A complaint is one answer, not a dashboard.

   trace: interaction hr-2026-08-17-0019
     span auth.resolve_principals      user, groups, latency
     span safety.input_scan            categories, decision
     span rag.query_rewrite            original → rewritten
     span rag.vector_search            query hash, index version, top-k, filters
     span rag.semantic_rerank          candidate count, selected, scores
     span context.assemble             token counts by component
     span llm.generate                 deployment, model, PROMPT VERSION,
                                       tokens, finish_reason
     span validator.citation_check     pass/fail reason, citation IDs
     span safety.output_scan           categories, decision
     span response.render

   FOR AN AGENT, the trace is the only record of a path chosen at runtime:
     step 1 llm.plan → step 1 tool.check_balance
     step 2 llm.plan → step 2 approval.request
     ⏸ approval.resume (hours later)
     step 3 tool.submit_leave

   ⚠ WITHOUT chunk IDs, you know the model was wrong but not WHAT IT SAW.
   ⚠ WITHOUT prompt/model version, the answer cannot be reproduced.
   ⚠ Trace data holds prompts, completions, tool args and retrieved content —
     it is PRODUCTION DATA, and often the least-protected copy of it.
```

**Plain English:** the full, nested record of one request, so an engineer can reconstruct what
happened without guessing.

**Precisely:** tracing records the path of a single request across model calls, retrieval,
reranking, tools, approvals, validators and response rendering. **Metrics tell you something is
wrong; traces show what happened in a specific case** — and for agents, where control flow is
chosen at runtime, the trace is the *only* record of the path taken.

### 2. Scenario

A complaint arrives: one answer, from one user, three weeks ago, that cited a policy incorrectly.

The dashboard is green. Aggregate faithfulness is 0.94. **None of that helps**, because the
question is not "how is the system doing?" but "what happened in *this* case?" Answering it
requires the retrieved chunk IDs, the prompt version, the model version, the reranker scores and
the validator outcome — all captured at the time, because none of them can be reconstructed now.

### 3. Example — attributes worth capturing per span

| Span | Attributes |
|---|---|
| Model call | Deployment, model, **prompt version**, token counts, `finish_reason` |
| Retrieval | Query hash, **index version**, top-k, filters, **chunk IDs** |
| Reranker | Candidate count, selected count, scores |
| Tool call | Tool name, risk class, args hash, **auth result**, latency |
| Approval | Approver, decision, **evidence ID** |
| Validators | Pass/fail reason, citation IDs |

### 4. How it works

**The tooling landscape:**

| Tool | Use |
|---|---|
| **LangSmith** | LangChain/LangGraph traces, datasets, prompt runs |
| **OpenTelemetry GenAI conventions** | Vendor-neutral spans and attributes for LLM, retrieval, tools and agents |
| **Azure AI Foundry tracing** | Foundry project traces, Application Insights integration, agent observability |
| Application Insights / Azure Monitor | Production dashboards, alerts, KQL queries |

**The security design, which is where tracing goes wrong.** Trace data can contain prompts,
completions, tool arguments, retrieved content and user data. **Treat it as production data:**

- Use **IDs, hashes and summaries** unless raw content is genuinely required.
- Restrict access — raw prompts and chunks should not be broadly readable by developers.
- Define retention, and honour deletion requests across traces (8.3.9, 8.6.7).
- Store within the required residency boundary.

⚠ **The balance is real in both directions.** Redact too aggressively and incident review becomes
impossible — "tool arguments were redacted so thoroughly that we cannot tell what was
submitted" is as much a failure as storing everything.

**Traces are also the source of online evaluation** (8.5.1): sampled production traces, scored
continuously, are how you detect drift away from a golden set that was built months ago.

### 5. Where it fits

```
   ▶ TRACING ◀ spans the ENTIRE request, and joins to audit (8.6.6) by trace ID
        │
        ├── one trace ID shared with the AUDIT record
        │     audit answers "who saw what" (a formal question, years of retention)
        │     tracing answers "what happened here" (an engineering question, days)
        │     ── different questions, different retention, different access control
        │
        ├── feeds incident triage (8.5.6) — pull the trace, classify the layer
        └── feeds online evaluation (8.5.1) — sample traces, score them, detect drift
```

### 6. Libraries & code

| Job | How |
|---|---|
| Instrumentation | OpenTelemetry SDK, GenAI semantic conventions |
| Framework-native | LangSmith for LangChain/LangGraph; Foundry tracing for Azure agents; LangFuse and Helicone as self-hostable alternatives; `openllmetry` for an OTel-native drop-in |
| Correlation | Propagate one trace ID across model, retrieval, tool and approval spans |
| Storage | Application Insights / Azure Monitor, in the approved region |
| Redaction | Hash or ID substitution at span-write time, not afterwards |

### 7. Knobs & real numbers

| Knob | Typical | Notes |
|---|---|---|
| Sampling rate | 100% of errors and high-stakes; 5–20% of routine (`typical`) | Full-fidelity everywhere is expensive |
| Raw content storage | minimised, sampled, justified | Prefer IDs and hashes |
| Trace retention | days to weeks | Distinct from audit retention (often years) |
| Required attributes | prompt version + model version + index version + chunk IDs | The four that make reproduction possible |
| Access | restricted, and log who queried raw traces | The trace store aggregates everything |
| Residency | the approved region | The classic leak: app is private, telemetry exports out |

### 8. Perspectives grid

| Lens | What matters here |
|---|---|
| **Theory** | An agent's control flow is chosen at runtime, so the trace is not a debugging convenience — it is the only existing record of the program that actually ran. |
| **Engineering** | Emit version fields on every span. Capture chunk IDs. Share a trace ID with the audit record. Redact at write time, and not so hard that triage is impossible. |
| **Operations** | Enable tracing in production, not just development. Sample routine traffic and keep 100% of errors. Traces are the input to both incident triage and online evaluation. |
| **Cost** | Trace storage is a real line item at full fidelity. Sample deliberately rather than discovering the bill. |
| **Security** | The trace store often becomes the largest, least-protected copy of sensitive data in the system. It needs residency, retention, redaction and access control like any production data store. |
| **Decision** | Instrument for the question "could I reconstruct this specific answer?" If the answer is no, the missing field is what to add. |

### 9. Trade-offs & failure modes

- **Traces enabled only in development.**
- **Prompt and model versions missing from spans**, making reproduction impossible.
- **Retrieval IDs missing**, so citations cannot be reproduced — you know it was wrong, not what
  it saw.
- **Tracing storing sensitive content with broad developer access.**
- **Arguments redacted so aggressively that incident review is impossible.**
- **Traces stored outside the required residency boundary.**
- **A bad answer arriving when the only record is the final text.**

---

## 8.5.8 SLOs for AI systems `+` `[WORKING]`
> **In the build:** Stage 6, Step 7 — *"define what reliability means."*

**Definition** — An SLO is a target for user-visible service behaviour. **AI systems need
ordinary operational SLOs plus quality and safety SLOs**, because the model can be perfectly *up*
and still ungrounded, unsafe, too slow or too expensive. Availability alone is a green light on a
broken system.

**Example — an SLO set that covers behaviour, not just uptime:**

| Category | SLO |
|---|---|
| Availability | 99.9% of requests receive an answer, an abstention or a safe fallback |
| Latency | p95 RAG answer < 4 s; p95 TTFT < 1 s for streamed answers |
| Retrieval | Hit rate @8 ≥ 0.90 on the current golden set |
| Grounding | Faithfulness ≥ 0.90 on sampled traffic |
| **Permission safety** | **Zero** confirmed cross-user document disclosures |
| **Tool safety** | **Zero** writes without approval |
| Tool accuracy | ≥ 95% correct tool selection on the golden set |
| Cost | p95 cost per request under budget, **per feature** |
| Abstention | ≥ 90% correct abstention on the unanswerable set |
| Evaluation freshness | Golden set reviewed quarterly and after policy changes |

Note that two rows are **zeros, not thresholds**. Permission disclosure and unapproved writes are
not quality metrics to be traded off — they are binary properties.

**Alerts, and what each usually means:**

| Alert | Likely cause |
|---|---|
| Cache hit ratio drops below 50% | Dynamic data entered the prompt prefix (8.2.5) |
| Retrieval no-result rate spikes | Index sync failure (8.3.9) |
| p95 tool latency spikes | Backend dependency degraded |
| **Abstention rate drops sharply** | **Grounding prompt regression — the model started guessing** |
| Prompt-injection detections spike | An attack, or a poisoned source |
| Cost per request doubles | Model route or context regression |

**What you cannot promise** — and saying so plainly is the mark of someone who has operated one
of these: exact deterministic answers across model backend changes · perfect truth when the
source corpus is wrong · zero hallucinations without an abstention and verification path.
**State the control and the measured target, not impossible certainty.**

**Where it fits** — over the metrics from 8.5.2, 8.5.3 and 8.5.4, and tied to the release gates
in 8.5.1 and 8.5.7.

**Library** — Azure Monitor / Application Insights alert rules over emitted metrics; the eval
harness for the quality SLOs.

**Fails when** — availability is green while answers are ungrounded · quality SLOs exist but are
**not tied to release gates**, so a build can regress them and still ship · alerts fire with no
owner and no runbook.

---

## 8.5.9 Telemetry retention policy `+` `[WORKING]`
> **In the build:** Stage 6, Step 7 — *"telemetry is a compliance decision."*

**Definition** — Telemetry retention defines what AI interaction data is stored, where, for how
long, at what granularity, and who can access it. **AI telemetry is sensitive because it contains
user questions, retrieved content, tool arguments and model outputs** — it is not "just logs".

**Example — retention tiers, because one policy for everything is always wrong:**

| Tier | Contents | Retention |
|---|---|---|
| Aggregated metrics | Counts, latency, cost | Long-lived, low sensitivity |
| Structured trace metadata | IDs, versions, timings, pass/fail | Medium |
| **Raw prompts / responses** | Full text | **Short and restricted** |
| **Tool results / retrieved chunks** | Source-system data | **Minimize, or store IDs only** |
| Approval records | Evidence of official action | Per business and legal policy — often long |
| Evaluation datasets | Curated examples, often from real traffic | **Governed like source data** |

**The design choices that follow:** redact before exporting telemetry · keep raw-content sampling
low and justified · **separate audit retention from debug retention** (different questions,
different obligations) · honour deletion requests across traces *and* eval copies · store
telemetry in approved regions · restrict who can query raw traces.

**Where it fits** — wraps 8.5.5's traces and 8.5.3's usage records, and inherits its rules from
8.6.7's data-protection boundary.

**Library** — retention policies on your telemetry backend; a deletion routine that walks traces,
caches and eval datasets alongside the index (8.3.9).

**Used when** — always. In a public entity, the retention position must be written down **before**
the data protection officer asks, not derived afterwards.

**Fails when** — telemetry is treated as "just logs" and **escapes the same DLP, residency,
access-control and deletion rules as the application** · debug logs become a shadow database of
HR records · **eval examples copied from production are kept forever** · deletion processes ignore
telemetry and caches.

---

## 8.5.6 Feedback loops `[WORKING]`
> **In the build:** Stage 6, Step 8 — *"learn from production."*

**Definition** — Feedback loops turn production signals into controlled improvements: user
ratings, corrections, incident reports, human-review labels, support tickets and evaluator
failures. **They are not the same as training on user feedback automatically** — the loop runs
through triage, a fix and an evaluation, not straight into the model.

**Example — the workflow:**

```
   bad answer or feedback
     → pull the TRACE and the AUDIT record        (8.5.5 / 8.6.6)
     → classify the FAILURE LAYER                 ← the step that is skipped
     → assess severity and data impact
     → fix source / prompt / retriever / tool / control
     → ADD A REGRESSION CASE to the golden set    (permanently)
     → run eval                                   (8.5.1)
     → deploy with canary                         (8.5.7)
     → close with evidence
```

**The triage taxonomy — classifying the layer is what stops every incident becoming a prompt
change:**

| Failure layer | Example | Owner |
|---|---|---|
| Source content | Policy outdated | Content owner |
| Ingestion | Document missing, OCR bad | Data pipeline |
| Retrieval | Wrong chunk | Search / RAG engineer |
| Generation | Unsupported claim | Prompt / model owner |
| Tool | Wrong action proposed | Agent / tool owner |
| Safety | False block, or a missed leak | Security / RAI |
| UX | User misunderstood a correct answer | Product owner |

**The signals, and the bias in each:**

| Signal | Bias |
|---|---|
| Thumbs up/down | Sparse, negative-heavy, little context |
| Free-text feedback | Useful but noisy, and **may contain PII** |
| Support tickets | Severe failures only |
| Human review labels | Best quality, expensive |
| Automated eval failures | Consistent, but judge-biased |

**Where it fits** — consumes traces and audit records; produces golden-set rows, prompt-backlog
items and red-team cases. It is the mechanism by which the golden set **grows monotonically**.

**Library** — your feedback UI, an incident tracker, and the eval dataset in version control.

**Fails when** — feedback trains or fine-tunes directly without filtering (**you teach the model
the mistakes of whoever complained loudest**) · incidents are fixed but not added to regression
tests · **the failure layer is not classified, so everything becomes a prompt change** · product
teams monitor satisfaction but not safety or groundedness · human corrections are not tied back
to the original trace · the UI asks only for thumbs, so feedback is too sparse to act on.

---

## 8.5.7 Canary, shadow deployment and version pinning
> **In the build:** Stage 6, Step 9 — *"roll out prompts and models like software."*

### 1. Definition

```
   AI DEPLOYMENT IS NOT APPLICATION DEPLOYMENT.
   FOUR ARTIFACTS CHANGE INDEPENDENTLY, and each can break the others:

     1. prompt templates
     2. model deployments
     3. embedding / reranker / index versions
     4. tool schemas and orchestration logic

   → so the unit of release is a BUNDLE, and rollback must restore ALL FOUR
   ┌──────────────────────────────────────────────────────────────────────┐
   │ release: hr-assistant-2026.08.17                                      │
   │ app_version:        3.4.2                                             │
   │ prompt_version:     hr-rag-2.3.0                                      │
   │ model_route:  answer   gpt4o-mini-uaenorth-2026-07                    │
   │               verifier gpt4o-uaenorth-2026-07                         │
   │ embedding:    model    multilingual-embed-v4                          │
   │               index    policies-embed-v4-2026-08-01                   │
   │ reranker:           semantic-ranker-v2                                │
   │ tool_schema_version: hr-tools-1.8.0                                   │
   │ eval_baseline:      eval-run-2026-08-16                               │
   └──────────────────────────────────────────────────────────────────────┘

   THE ROLLOUT LADDER — user impact increases down the list
   ┌──────────┬──────────────────────────────┬──────────────────────────────┐
   │ SHADOW   │ candidate runs, user sees    │ safety comparison, model      │
   │          │ the OLD output               │ migration                     │
   │ CANARY   │ a small % of real users see  │ real UX / product validation  │
   │          │ the candidate                │                               │
   │ A/B      │ controlled split, compared   │ enough traffic, a clear metric│
   │ ROLLBACK │ return to a known-good BUNDLE│ incident response             │
   └──────────┴──────────────────────────────┴──────────────────────────────┘
```

**Plain English:** control which prompt, model, index and tool version serves which traffic, and
change them the way you would change code — measured, gradual and reversible.

**Precisely:** deployment discipline for AI means controlling which prompt, model, embedding
model, reranker and tool schema version serves which traffic, and rolling changes out **with
measurement and rollback**.

### 2. Scenario

Four independent changes are queued: a new grounding prompt, a model version upgrade, a better
embedding model, and a tool schema revision. Each is individually reasonable.

Shipped together and unpinned, they produce failures that are indistinguishable from one another:
the model changes while the prompt stays tuned to old behaviour · the embedding model changes but
the index is not rebuilt, so **query and index vectors are in different spaces and retrieval
silently becomes random** (8.3.3) · the tool schema changes and **invalidates the prompt cache**
plus tool-selection accuracy (8.2.5, 8.4.2) · and a rollback restores the app but not the index,
leaving a combination that was never tested.

### 3. Example

```python
route = choose_route(user_id, feature="hr_rag")   # hash the USER, not the request
config = CONFIGS[route]

answer = run_pipeline(
    model=config.model_deployment,
    prompt=config.prompt_version,
    embedding_index=config.index_version,     # pinned TOGETHER — they are one unit
)

emit_metric("llm.route", {"route": route, **quality_and_cost(answer)})
```

### 4. How it works

**The five patterns:**

| Pattern | Meaning | Use |
|---|---|---|
| **Version pinning** | Explicit model/prompt/deployment versions | Reproducibility |
| **Canary** | A small percentage of real users get the candidate | Safe rollout |
| **Shadow** | The candidate runs in parallel but does not answer the user | Compare safely |
| **A/B test** | Variants compared on defined metrics | Product and prompt decisions |
| **Rollback** | Return the route to the prior known-good version | Incident response |

**Shadow before canary** is the ordering that matters for model migrations: shadow costs money
and no user risk; canary costs user risk. Run shadow to compare quality and safety on real
traffic, then canary to validate the actual user experience.

**Deprecation handling.** Models and API versions are deprecated **on the provider's schedule,
not yours**. Keep an inventory of every deployment, prompt, eval baseline and expected retirement
date. Run shadow tests against the replacement *before* forced migration. ⚠ **The worst migration
is one performed to a deadline without an evaluation baseline** — you cannot tell whether the new
model is worse, only that it is different.

**Canary success must be judged on metrics, not on silence.** "No complaints" measures how likely
users are to complain, not whether quality regressed.

### 5. Where it fits

```
   candidate config (a BUNDLE, all four artifacts pinned)
        │
        ├─► CI: deterministic checks              (8.5.1)
        ├─► nightly / pre-release: full eval      (8.5.1, 8.5.2)
        ├─► red-team + permission cases           (8.6.10)
        │
        ├─► SHADOW on sampled production traffic  ← no user impact
        ├─► CANARY 5-10%                          ← real user impact, watched
        │        │
        │        └── dashboards + traces (8.5.5), quality/cost/latency deltas
        │
        └─► roll forward · roll back · fix        (8.5.6)
```

### 6. Libraries & code

| Job | How |
|---|---|
| Version pinning | Deployment names, not model names (8.1.8); prompt versions in the repo (8.2.3) |
| Routing | A config-driven route table, hashed by user for consistency |
| Shadow | Duplicate the request to the candidate; discard its output; score it offline |
| Canary | Percentage routing at the gateway or in application config |
| Rollback | Restore the whole bundle — app, prompt, model route, index, tool schema |
| Deprecation | An inventory with retirement dates and a named owner (8.6.9) |

### 7. Knobs & real numbers

| Knob | Typical | Notes |
|---|---|---|
| Canary share | 5–10% | Enough traffic for signal, small enough to bound harm |
| Shadow share | 5–20% of traffic | Costs double for those requests, zero user risk |
| Randomization unit | **the user**, not the request | Consistency within a session (8.2.3) |
| Bake time before promotion | hours to days, by traffic volume | Long enough to see the tail |
| Rollback target | the **whole bundle** | App + prompt + model + index + tool schema |
| Eval baseline | pinned per release | Named run ID, stored |
| Deprecation lead time | provider-dependent (`verify`) | Plan before the notice arrives |

### 8. Perspectives grid

| Lens | What matters here |
|---|---|
| **Theory** | Four artifacts change independently but their behaviour is coupled — the release unit must therefore be their combination, not any one of them. |
| **Engineering** | Pin everything. Call deployments, not models. Rebuild the index when the embedding model changes. Make rollback restore the bundle. |
| **Operations** | Shadow first, canary second, judged on metrics rather than silence. Keep a deprecation inventory with named owners and dates. |
| **Cost** | Shadow doubles the cost of sampled traffic for its duration — budget it deliberately as the price of a safe model migration. |
| **Security** | A prompt or tool-schema change can regress a safety control, so red-team and permission cases belong in the same gate as quality metrics. |
| **Decision** | No AI artifact ships unpinned, unmeasured or unrollbackable. If you cannot restore the previous prompt/model/index combination, you do not have a rollback. |

### 9. Trade-offs & failure modes

- **Model names hardcoded across services.**
- **Prompt changes shipped without version IDs in telemetry.**
- **Embedding model changes not triggering re-embedding and index versioning** — retrieval
  silently becomes random.
- **Canary success judged on no complaints rather than metrics.**
- **Rollback that cannot restore the previous prompt/model/index combination.**
- **Model deployment changed while the prompt stays tuned to old behaviour.**
- **Tool schema changes invalidating prompt caching and tool selection.**
- **A forced deprecation migration performed without an evaluation baseline.**

---

## 8.5.11 AI gateway — centralizing routing, auth, cost and observability across apps `+`

> **In the build:** Stage 6 (companion) — everything above this line was written as if one
> application calls one model. The moment a **second** GenAI application ships, every one of
> those concerns — rate limits, cost attribution, model routing, audit logging — either gets
> duplicated per app or centralized. This is the centralized shape.

**Definition** — An AI gateway is a single proxy that every GenAI application in the
organisation calls *through*, instead of calling model providers directly. It is the same idea
as an API gateway (8.6.5's on-behalf-of pattern, 8.6.12's rate limiting) applied specifically to
LLM traffic, and it exists because per-request-billed, provider-diverse, high-volume LLM traffic
has operational needs a generic API gateway wasn't built for.

**Example — what moves behind the gateway, and why:**

| Concern | Without a gateway | With a gateway |
|---|---|---|
| Provider credentials | Every app holds its own API keys | One place holds keys; apps authenticate to the gateway |
| Cost attribution | Reconstructed after the fact from scattered logs (8.5.3) | Tagged per app/team at the point of the call — the source of truth |
| Rate limits / quota | Enforced (or not) per app, inconsistently (8.6.12) | Enforced once, consistently, per app and per tenant |
| Model routing / fallback | Each app hardcodes its provider (8.1.3) | Centrally configured: route by cost/latency, fail over on outage |
| Caching | Each app builds its own prompt/semantic cache (8.2.5, 8.3.10) | Shared cache layer, higher hit rate across apps |
| Audit logging | Each app logs (or doesn't) independently (8.6.6) | One consistent, complete record of every model call org-wide |
| PII / content filtering | Each app integrates its own (8.6.3, 8.6.4) | Enforced as a shared, non-optional layer |

**Where it fits** — sits in front of every application in this entire body of material, at the
point where a request would otherwise go straight to a model provider. It does not replace
per-application guardrails (8.6.1–8.6.13) — it is where org-wide policy is enforced consistently,
while each application still owns its own prompt, retrieval and agent-specific controls.

**Library** — Azure API Management with its AI gateway capabilities (token metering, semantic
caching, load balancing across deployments); `LiteLLM` proxy; Portkey; Kong AI Gateway. All solve
the same problem at different levels of managed-ness — `verify` current feature parity before
choosing.

**Used when** — more than one GenAI application exists, or will soon; especially wherever cost
attribution to a specific team or product must be defensible, or a single provider outage must
not take down every application at once.

**Fails when**
- Adopted for a single application, where it adds a hop and an operational dependency for no
  benefit — the threshold is "more than one app," not "day one."
- Treated as a substitute for application-level guardrails rather than a *complement* to them —
  a shared filter catches org-wide policy violations, not a specific application's business
  rules.
- Becomes an unowned, unmonitored single point of failure for every GenAI app in the
  organisation — it needs the same SLOs (8.5.8) and on-call ownership as any other shared
  platform dependency.
- API keys are moved behind the gateway but per-app scoping is not enforced, so a single
  compromised app can exhaust another app's quota or budget.

---

# Part C — Stage 6 assembled

## C1. One release, end to end

Stages 1–5 traced a *request*. This stage traces a **release**, because that is the unit LLMOps
operates on. As before, this section is self-contained: each step carries its mechanism, its
numbers and its failure mode inline.

**Before the trace starts, three decisions are already locked in:**

- **Behaviour is specified as datasets and thresholds, not impressions** [8.5.10]. If this flips,
  every release argument becomes a debate about anecdotes, and the team ships the change that
  demos best rather than the one that measures best.
- **The release unit is a bundle of four artifacts** — prompt, model route, embedding/index,
  tool schema [8.5.7]. They change independently and their behaviour is coupled. If this flips
  to shipping them separately, a rollback restores the app and leaves an untested combination.
- **Telemetry is production data, governed like the corpus** [8.5.9, 8.6.7]. If this flips to
  "it's just logs", the trace store becomes a shadow database of HR records with broad developer
  access.

```text
CHANGE: replace the reranker and update the grounding prompt.

HOW TO SKIM THIS MAP
  DO       = what runs
  TOOLS    = techniques / frameworks / implementation pieces
  REMEMBER = the main exam / interview point
  NUMBERS  = values worth memorising
  WATCH    = failure mode or control you must not miss
  SUMMARY  = the one thing to keep long-term if you forget everything else

  1. CREATE A CANDIDATE CONFIG WITH PINNED VERSIONS         [8.5.7 / 8.5.10]
     DO: Bundle prompt + model route + embedding/index + tool schema + eval baseline into one
         versioned candidate config; change ONE thing at a time.
     TOOLS: Versioned config file (app_version, prompt_version, model_route,
            embedding.model+index, reranker, tool_schema_version, eval_baseline); deployment
            naming, not model naming.
     THIS RUN: Candidate = new reranker + updated grounding prompt -- two changes bundled
               deliberately, tracked as one release unit.
     REMEMBER: The release unit is the BUNDLE, not any single artifact, because the four
               artifacts' behaviour is coupled. One-change rule: don't change model + prompt +
               chunking + top-k together unless deliberately shipping a controlled bundle, or you
               won't know why metrics moved.
     WATCH: Model names hardcoded across services instead of calling deployments. An embedding
            model change that doesn't trigger re-embedding/index versioning -- query and index
            vectors land in different spaces, nothing errors, retrieval goes silently random. A
            tool schema change invalidating both prompt caching and tool-selection accuracy.
     SUMMARY: Treat a release as one versioned bundle (prompt, model route, embedding/index, tool
              schema, eval baseline) and change only what you mean to change at once, because
              these four artifacts' behaviour is coupled -- an embedding change without
              re-embedding/index versioning silently randomizes retrieval with no error, and
              stacking changes together destroys your ability to attribute a metric move to a
              cause.

  2. RUN DETERMINISTIC RETRIEVAL METRICS IN CI              [8.5.1 / 8.5.2]
     DO: Run free, fast checks (schema, citation quote check, forbidden chunk, tool args, hit
         rate, recall, precision, MRR) against the production path on every commit.
     TOOLS: CI eval harness; golden dataset rows carrying as_user + must_not_retrieve;
            deterministic scorers.
     THIS RUN: Candidate config run through the CI gate before anything nightly or pre-release
               happens.
     REMEMBER: The gate asserts thresholds AND zeros: retrieval_hit_rate_at_8>=0.90,
               context_recall>=0.85, faithfulness>=0.90, correct_abstention_rate>=0.90,
               permission_leak_count==0. The harness must run the REAL auth, filters and prompt
               assembly -- a harness that mocks retrieval tests a system that doesn't exist.
               Every golden row needs as_user or permission failures are structurally invisible.
     NUMBERS: permission_leak_count == 0 is a hard zero, not a tunable threshold.
     WATCH: Thresholds lowered to make a build green -- the metric now measures nothing. Only
            happy-path answerable questions, which rewards hallucination because guessing scores
            well.
     SUMMARY: Run the free, fast, deterministic checks (schema, citation, hit rate/recall/MRR)
              through the real production path on every commit, gated on both thresholds and
              hard zeros like permission_leak_count==0 -- without as_user on every golden row,
              permission failures are structurally invisible, and a harness that mocks retrieval
              or auth is testing a system that doesn't exist.

  3. RUN THE FULL LLM-JUDGED EVAL NIGHTLY / PRE-RELEASE      [8.5.1]
     DO: Run the slower, costlier LLM-judged metrics (faithfulness, relevance, coherence, correct
         abstention) nightly and before release, with judge biases controlled for.
     TOOLS: LLM-as-judge scorers; length-normalized rubric; randomized pairwise order;
            independent/calibrated judge model; bilingual judge set + human calibration.
     THIS RUN: Candidate scored on faithfulness/relevance/coherence/abstention against the golden
               set, judge blind to the gold answer.
     REMEMBER: Five named judge biases: verbosity, position, self-preference, style, language --
               each needs its own countermeasure. Never use an LLM judge as the ONLY gate for
               security-sensitive behaviour -- those stay deterministic checks with a threshold
               of zero. Never let the judge see the gold answer when measuring faithfulness, or
               it leaks correctness into a score meant to measure support-by-context.
     NUMBERS: Four evaluation modes: offline (release gates, dataset goes stale), online (sampled
              production, drift detection), human review (high-stakes, expensive), pairwise
              (A vs B).
     WATCH: Outputs scored but traces not saved, so failures can't be debugged afterwards.
     SUMMARY: Score faithfulness, relevance, coherence and abstention with an LLM judge nightly
              and pre-release, actively countering its five known biases (verbosity, position,
              self-preference, style, language) and never letting it see the gold answer while
              judging faithfulness -- and never let a judge alone gate anything
              security-sensitive, since that needs a deterministic zero-threshold check instead.

  4. COMPARE QUALITY, SAFETY, LATENCY AND COST TO BASELINE   [8.5.2 / 8.5.3 / 8.5.4]
     DO: Read the whole scorecard against baseline, segmented across 8 dimensions, in diagnostic
         pairs rather than as averages.
     TOOLS: Diagnostic pattern table (recall+faithfulness pairs point to retrieval vs generation
            fixes); segmentation by language/tenant/channel/feature/model route/prompt
            version/document source/user role; latency read at p95/p99 per stage; cost read with
            full attribution (cached input, reasoning, embedding, reranker, agent step
            multiplier).
     THIS RUN: New reranker + grounding prompt compared to baseline across quality, safety,
               latency, cost, segmented by language to check Arabic didn't regress.
     REMEMBER: Read metrics in PAIRS, never as an average, and segment by all 8 dimensions or
               averages lie -- the classic bilingual trap is overall quality rising while Arabic
               quality falls underneath it. A 3% quality gain at 40% more cost is a DECISION, not
               an automatic win.
     NUMBERS: Rerank 50-300ms/30 candidates; retrieval <100ms target; agent step cost multiplier
              10-50x. The worked trap: faithfulness 0.89->0.95 while abstention 8%->22% -- only
              the unanswerable set plus human review can tell if that's correct or
              over-conservative.
     WATCH: Cost and latency missing from the scorecard, so an expensive change ships without
            anyone deciding. Cached tokens untracked, so broken prompt caching is invisible --
            nothing errors, the bill just stops falling.
     SUMMARY: Read the whole scorecard (quality, safety, latency, cost) against baseline in
              diagnostic pairs and segmented across 8 dimensions, never as one average, since a
              bilingual system can show rising overall quality while Arabic quality falls
              underneath it -- and treat a quality gain bought with a big cost or abstention
              swing as a decision requiring the unanswerable set and human review, not an
              automatic win.

  5. RUN RED-TEAM AND PERMISSION-SENSITIVE CASES            [8.6.10 / 8.5.1]
     DO: Run the red-team suite and permission-sensitive golden cases as part of the SAME release
         gate as quality.
     TOOLS: Red-team regression suite (Stage 5); permission-sensitive golden rows.
     THIS RUN: Candidate config run against the same adversarial and permission-sensitive cases
               used every release.
     REMEMBER: Stage 5's controls become Stage 6's measurements -- a control without a
               measurement is an assertion, not a fact. Score OUTCOMES not blocked/not-blocked:
               correct abstention, safe refusal, routed-to-human all count as successes; unsafe
               answer, unauthorized tool call, disclosure, excessive cost are failures.
     NUMBERS: permission_leak_count == 0, same hard zero as step 2.
     WATCH: A prompt change silently regressing a safety control, which is exactly why red-team
            pass rate belongs IN the same gate as quality, not in a separate quarterly exercise.
     SUMMARY: Run the red-team and permission-sensitive suites in the SAME gate as quality every
              release, scoring outcomes (safe refusal, correct abstention count as wins) rather
              than blocked/not-blocked, because Stage 5's controls only become real once they're
              measured here -- a safety regression caught quarterly instead of per-release is a
              safety regression that already shipped.

  6. SHADOW ON SAMPLED PRODUCTION TRAFFIC                   [8.5.7]
     DO: Run the candidate in parallel on sampled real traffic while the user still sees the old
         output.
     TOOLS: Shadow deployment infrastructure; sampled request duplication.
     THIS RUN: Reranker+prompt candidate shadow-run against real HR queries with zero
               user-facing risk.
     REMEMBER: Real traffic, real distribution, ZERO user risk -- it just costs double for
               sampled requests. Shadow before canary is the ordering for model migrations:
               shadow costs money, canary costs user risk.
     WATCH: A forced deprecation migration run to a provider's deadline WITHOUT an evaluation
            baseline -- you can only tell the new model is different, not whether it's worse.
     SUMMARY: Run the candidate on sampled real traffic in parallel while the user still sees the
              old output, so you get a real-distribution comparison at zero user risk -- shadow
              always comes before canary in a model migration, since shadow only costs money
              while canary costs user risk, and skipping it before a forced deprecation deadline
              means shipping blind.

  7. CANARY TO 5-10% IF SHADOW IS CLEAN                     [8.5.7]
     DO: Route a small percentage of real users to the candidate, once shadow results are clean.
     TOOLS: User-hash-based traffic splitting; canary metrics dashboard.
     THIS RUN: 5-10% of real users routed to the candidate for a bake period.
     REMEMBER: Hash the USER, not the request, so one person gets a consistent experience within
               a session. Judge on METRICS, not silence -- "no complaints" measures how likely
               users are to complain, not whether quality regressed.
     NUMBERS: Canary 5-10%; bake hours to days.
     WATCH: Canary success declared on absence of complaints instead of on the measured
            scorecard.
     SUMMARY: Route 5-10% of real users to the candidate, split by hashed user ID so each
              person's experience stays consistent, and bake for hours to days -- judge success
              on the measured scorecard, never on the absence of complaints, since silence
              measures complaint tolerance, not quality.

  8. WATCH DASHBOARDS AND TRACES                            [8.5.5 / 8.5.8]
     DO: Monitor quality/retrieval/safety/cost/latency/agent/feedback dashboards and pull
         individual traces when something looks wrong.
     TOOLS: Dashboards; distributed tracing (OpenTelemetry GenAI spans, LangSmith, Azure AI
            Foundry tracing); AI SLOs with alert thresholds.
     THIS RUN: Canary watched against the AI SLO set; traces available to explain any individual
               bad answer.
     REMEMBER: Metrics tell you SOMETHING is wrong; traces show what happened in ONE case -- a
               complaint is one answer, not a dashboard. AI SLOs cover behaviour, not just
               uptime, and two are ZEROS: zero confirmed cross-user disclosures, zero writes
               without approval -- availability can be green while answers are ungrounded. For an
               agent, the trace is the ONLY record of the path, since control flow was chosen at
               runtime.
     NUMBERS: Alert causes: cache hit ratio <50% -> dynamic data in the prefix; retrieval
              no-result spike -> index sync failure; p95 tool latency spike -> degraded
              dependency; abstention dropping sharply -> grounding regression; injection
              detections spiking -> attack or poisoned source; cost per request doubling ->
              route/context regression.
     WATCH: Traces enabled only in development. Sensitive content stored with broad developer
            access, or outside the residency boundary. Alerts that fire with no owner and no
            runbook.
     SUMMARY: Watch the full dashboard set (quality, retrieval, safety, cost, latency, agents,
              feedback) against AI SLOs that include two hard zeros (cross-user disclosure,
              writes without approval), and pull the actual trace -- carrying prompt/model/index
              version and chunk IDs -- whenever a metric or a complaint needs explaining, since
              for an agent the trace is the only record of what path was actually taken.

  9. ROLL FORWARD, ROLL BACK OR FIX                         [8.5.6 / 8.5.7]
     DO: Decide to keep, revert or patch, restoring the WHOLE bundle on rollback, and run every
         incident through triage before touching the model.
     TOOLS: Bundle-level rollback; triage taxonomy (source content, ingestion, retrieval,
            generation, tool, safety, UX) with named owners; regression-case addition to the
            golden set.
     THIS RUN: If canary metrics hold, roll forward to 100%; if not, roll back the entire bundle
               (app+prompt+model route+index+tool schema) together, not just the app.
     REMEMBER: Rollback restores the WHOLE BUNDLE -- restoring only the app produces a
               combination that was never tested. The feedback loop runs through TRIAGE, not
               straight into the model: pull the trace -> classify the failure layer -> assess
               severity -> fix the right layer -> add a regression case permanently -> eval ->
               canary -> close with evidence. Without failure-layer classification, every
               incident becomes "the prompt needs improvement."
     WATCH: Feedback used to fine-tune directly without filtering -- you teach the model the
            mistakes of whoever complained loudest. Incidents fixed but never added to
            regression tests, so they recur.
     SUMMARY: On rollback restore the WHOLE bundle together, never just the app, since a partial
              restore creates an untested combination -- and route every production failure
              through triage (classify the failure layer, assign an owner, fix the right layer,
              add a permanent regression case) rather than straight into a prompt tweak, or every
              incident becomes "the prompt needs improvement" and nothing actually gets fixed.

  TOPICS THAT ARE PART OF THIS STAGE BUT NOT DIRECT STEPS IN THIS REQUEST

  N1. SLOs FOR AI SYSTEMS                                    [8.5.8]
     WHERE: Standing definitions that step 8's dashboards and alerts are measured against, not a
            release action itself.
     WHY NOT A STEP: SLOs are set once (and revisited), not re-decided release by release; step 8
                     watches against thresholds already fixed here.
     TOOLS: Availability + quality + safety SLO set together; alert-to-cause mapping.
     REMEMBER: Ordinary operational SLOs PLUS quality and safety SLOs, because the model can be
               up and still ungrounded, unsafe, slow or expensive. Two rows are ZEROS, not
               thresholds: cross-user disclosure and unapproved writes are binary, not a
               percentage target.
     NUMBERS: Availability 99.9% receive an answer/abstention/fallback; p95 RAG answer <4s, p95
              TTFT <1s; hit rate@8 >=0.90; faithfulness >=0.90; tool selection >=95%; correct
              abstention >=90%; golden set reviewed quarterly.
     WATCH: Availability green while answers are ungrounded. Quality SLOs not tied to release
            gates. Alerts firing with no owner or runbook.
     SUMMARY: SLOs for an AI system must cover behaviour, not just uptime, including two hard
              zeros (cross-user disclosure, unapproved writes) alongside the usual
              availability/latency/quality targets -- otherwise a dashboard can stay green while
              the system is quietly ungrounded, and an alert with no owner or runbook is not
              really a control.

  N2. TELEMETRY RETENTION POLICY                             [8.5.9]
     WHERE: Governs what step 8's traces (and every other stage's logs) may contain and for how
            long -- a standing policy, not a release action.
     WHY NOT A STEP: Retention rules are set once per data class and enforced continuously, not
                     decided per release.
     TOOLS: Tiered retention (aggregated metrics long-lived/low sensitivity; raw
            prompts/responses short/restricted; tool results and chunks minimized or IDs-only;
            eval datasets governed like source data); export redaction.
     REMEMBER: AI telemetry contains user questions, retrieved content, tool arguments and model
               outputs -- it is NOT "just logs." Audit retention is separate from debug retention
               and is often years, not weeks.
     WATCH: Telemetry escaping the application's DLP/residency/access-control/deletion rules.
            Debug logs becoming a shadow database of HR records. Eval examples copied from
            production and kept forever. Deletion requests that ignore telemetry and caches.
     SUMMARY: Treat telemetry as governed production data with tiered retention (short and
              restricted for raw prompts/tool results, long only for aggregated metrics and
              approval records), since it contains real user questions and retrieved content --
              without deliberate rules, debug logs quietly become an ungoverned shadow database
              of the same sensitive records the corpus was protecting.

  N3. FEEDBACK LOOPS                                         [8.5.6]
     WHERE: Runs continuously in production, not at release time -- its output (new golden-set
            rows, prompt backlog, red-team cases) is the INPUT to the next release's step 1.
     WHY NOT A STEP: It's an always-on production process, not something executed once per
                     release cycle.
     TOOLS: Triage taxonomy with named owners (source content, ingestion, retrieval, generation,
            tool, safety, UX); signal sources (thumbs, free text, tickets, human labels,
            automated eval failures).
     REMEMBER: Turns production signals into CONTROLLED improvements -- explicitly not the same
               as training on feedback automatically. Signal biases matter: thumbs are sparse and
               negative-heavy, free text is noisy and may contain PII, tickets capture only
               severe failures.
     WATCH: Feedback used to fine-tune directly without filtering -- teaches the model the
            mistakes of whoever complained loudest. The failure layer not classified, so
            everything becomes "the prompt needs improvement." Corrections not tied back to the
            original trace.
     SUMMARY: Feedback loops run continuously in production and feed the NEXT release's candidate
              config, not this one -- every signal must go through triage with a named owner per
              failure layer before it becomes a fix, because unfiltered feedback teaches the
              model the loudest complainer's mistakes instead of the actual problem.

  N4. EVAL-DRIVEN DEVELOPMENT                                [8.5.10]
     WHERE: The frame underneath every numbered step -- not a step itself, but the reason
            releases are decided on measurement instead of impression.
     WHY NOT A STEP: It's the governing principle the whole trace implements, already reflected
                     in the "before the trace starts" callout.
     TOOLS: Golden set + baseline run + one-change-at-a-time discipline; release scorecard
            spanning retrieval, generation, agent tools, safety, Arabic/bilingual, latency, cost.
     REMEMBER: TDD adapted to probabilistic systems -- not one expected string, but thresholds
               over a representative dataset. The loop: define behaviour -> build golden set ->
               run baseline -> make ONE change -> compare metrics -> inspect failures -> ship or
               revert.
     NUMBERS: Golden set 200-500; ~15% unanswerable; ~15% bilingual; thresholds ratchet UP only,
              never down.
     WATCH: The demo set treated as an eval set. A single judge score deciding a release.
            Thresholds lowered just to pass. A better average hiding worse Arabic underneath it.
     SUMMARY: Every step in this trace exists because eval-driven development replaces impression
              with measurement -- define behaviour, build a golden set, run one change against a
              pinned baseline, and only ratchet thresholds up, since a demo that looks good or a
              single judge score deciding a release both defeat the entire discipline this stage
              is built on.
```

### Every step, unpacked — the crux of each topic, as points, in execution order

**1. Create a candidate config with pinned versions** — `[8.5.7] [8.5.10]`
- **Four artifacts change independently and their behaviour is coupled:** prompt templates ·
  model deployments · embedding/reranker/index versions · tool schemas and orchestration logic.
  The release unit is therefore the **bundle**.
- The bundle is a versioned file: `app_version` · `prompt_version` · `model_route` (answer and
  verifier) · `embedding.model` **and** `embedding.index` · `reranker` · `tool_schema_version` ·
  `eval_baseline`.
- **The one-change rule** [8.5.10]: do not change model, prompt, chunking and top-k together
  unless you are deliberately shipping a controlled bundle. If metrics move, you will not know
  why.
- ⚠ **Owns:** model names hardcoded across services. Call **deployments**, not models (8.1.8).
- ⚠ **Owns:** an embedding model change that does not trigger re-embedding and index versioning.
  Query and index vectors land in **different spaces**, nothing errors, and retrieval silently
  becomes random (8.3.3).
- ⚠ **Owns:** a tool schema change invalidating both prompt caching and tool-selection accuracy.

**2. Run deterministic retrieval metrics in CI** — `[8.5.1] [8.5.2]`
- **The scorer split is by cost and determinism, not importance:** deterministic checks (schema,
  citation quote check, forbidden chunk, tool args) and retrieval math (hit rate, recall,
  precision, MRR/NDCG) are **free and fast — run them on every commit**.
- The gate asserts thresholds *and* zeros: `retrieval_hit_rate_at_8 >= 0.90` ·
  `context_recall >= 0.85` · `faithfulness >= 0.90` · `correct_abstention_rate >= 0.90` ·
  **`permission_leak_count == 0`**.
- **The harness must run the production path** — the real auth, the real filters, the real prompt
  assembly. A harness that mocks retrieval tests a system that does not exist.
- **Every golden row carries `as_user`.** Without an identity, permission failures are
  structurally invisible, and an eval run as an administrator can never catch a trimming bug.
  `must_not_retrieve` asserts the negative that catches a trimming regression automatically.
- ⚠ **Owns:** thresholds lowered to make a build green. The metric now measures nothing.
- ⚠ **Owns:** only happy-path answerable questions, which **rewards hallucination** because
  guessing scores well.

**3. Run the full LLM-judged eval** — `[8.5.1]`
- LLM judges are useful for relevance, groundedness and style, and **biased in five named ways**:
  **verbosity** (longer scores higher → length-normalized rubric) · **position** (first wins in
  pairwise → randomize order) · **self-preference** (a family favours itself → independent judge,
  calibrate) · **style** (polished but unsupported scores well → require citation evidence) ·
  **language** (Arabic scored inconsistently → bilingual judge set and human calibration).
- **Never use an LLM judge as the only gate for security-sensitive behaviour.** Those are
  deterministic checks with a threshold of zero.
- **Do not let the judge see the gold answer when measuring faithfulness** — it leaks correctness
  into a score meant to measure support-by-context.
- Four evaluation modes, each catching what the others miss: **offline** (release gates; the
  dataset goes stale) · **online** (sampled production, drift detection; ground truth is delayed
  or absent) · **human review** (high-stakes and ambiguous; expensive) · **pairwise** (A vs B;
  needs consistent criteria).
- ⚠ **Owns:** outputs scored but traces not saved, so failures cannot be debugged afterwards.

**4. Compare quality, safety, latency and cost to baseline** — `[8.5.2] [8.5.3] [8.5.4]`
- **Read metrics in pairs, never as an average.** The diagnostic table is the working content:
  - low recall + high faithfulness → **fix retrieval**; a better model changes almost nothing
  - high recall + low faithfulness → **fix generation**: grounding prompt, temperature, validators
  - high relevance + low correctness → **the source is wrong or the gold answer is stale**
  - high abstention on *answerable* → relevance floor too strict, prompt too conservative
  - low abstention on *unanswerable* → the model is guessing
  - high tool-arg validity + low task success → a business workflow issue
  - good p50 + bad p99 → a tail dependency
  - quality up + cost up 4× → model or context too large
- **Segment by eight dimensions or averages lie:** language (English/Arabic/mixed) · tenant ·
  channel · feature · model route · prompt version · document source · user role. The specific
  lie in a bilingual entity is overall quality rising while Arabic quality falls.
- **The worked trap:** a grounding-prompt change moves faithfulness 0.89 → 0.95 while abstention
  goes 8% → 22%. That may be correct (the old system guessed) or too conservative. **You need the
  unanswerable set and human review to tell** — the average cannot.
- **Latency is read at the tail, per stage:** TTFT (input length, prefill, cold cache) ·
  tokens/sec (model tier) · p95/p99 · rerank 50–300 ms for 30 candidates · retrieval < 100 ms
  target · agent step count. **Streaming improves perceived, not total, latency.**
- **Cost is read with attribution:** input, **cached input**, output, **reasoning**, embedding,
  reranker, **agent step multiplier (10–50×)**, eval runs, index capacity, trace storage.
- ⚠ **Owns:** cost and latency missing from the scorecard, so a 3%-better-40%-more-expensive
  change ships without anyone deciding.
- ⚠ **Owns:** cached tokens untracked, so broken prompt caching is invisible — nothing errors,
  the bill just stops falling.

**5. Run red-team and permission-sensitive cases** — `[8.6.10] [8.5.1]`
- Stage 5's controls become Stage 6's measurements. **A control without a measurement is an
  assertion.**
- Score **outcomes, not blocked/not-blocked**: allowed safe answer · correct abstention · safe
  refusal · routed to human are all successes; unsafe answer · unauthorized tool call · sensitive
  disclosure · excessive cost are failures.
- ⚠ **Owns:** a prompt change silently regressing a safety control, which is why red-team pass
  rate belongs in the same gate as quality — not in a separate quarterly exercise.

**6. Shadow on sampled production traffic** — `[8.5.7]`
- The candidate runs in parallel; **the user sees the old output**. Real traffic, real
  distribution, **zero user risk** — it costs double for sampled requests and nothing else.
- **Shadow before canary** is the ordering for model migrations: shadow costs money, canary costs
  user risk.
- ⚠ **Owns:** a forced deprecation migration run to a provider's deadline **without an evaluation
  baseline** — you cannot tell whether the new model is worse, only that it is different.

**7. Canary to 5–10%** — `[8.5.7]`
- A small percentage of real users see the candidate. **Randomize by user, not by request**, so
  one person gets a consistent experience within a session.
- **Judge on metrics, not silence.** "No complaints" measures how likely users are to complain,
  not whether quality regressed.
- ⚠ **Owns:** canary success declared on absence of complaints.

**8. Watch dashboards and traces** — `[8.5.5] [8.5.8]`
- **Metrics tell you something is wrong; traces show what happened in one case.** A complaint is
  one answer, not a dashboard.
- The trace must carry **prompt version, model version, index version and chunk IDs**, or the
  answer cannot be reproduced and you know it was wrong without knowing what it saw.
- For an agent the trace is the **only** record of the path, because control flow was chosen at
  runtime — including the approval pause and resume hours later.
- **AI SLOs cover behaviour, not just uptime**, and two of them are **zeros**: zero confirmed
  cross-user disclosures, zero writes without approval. Availability can be green while answers
  are ungrounded.
- **Alerts and their usual causes:** cache hit ratio < 50% → dynamic data entered the prefix ·
  retrieval no-result spike → index sync failure · p95 tool latency spike → degraded dependency ·
  **abstention rate dropping sharply → grounding regression, the model started guessing** ·
  injection detections spiking → an attack or a poisoned source · cost per request doubling →
  route or context regression.
- ⚠ **Owns:** traces enabled only in development; sensitive content stored with broad developer
  access; traces outside the residency boundary.
- ⚠ **Owns:** alerts that fire with no owner and no runbook.

**9. Roll forward, roll back or fix** — `[8.5.6] [8.5.7]`
- **Rollback restores the whole bundle** — app, prompt, model route, index and tool schema. If it
  restores only the app, you have produced a combination that was never tested.
- **The feedback loop runs through triage, not straight into the model:** pull the trace and
  audit record → **classify the failure layer** → assess severity and data impact → fix the right
  layer → **add a regression case permanently** → run eval → canary → close with evidence.
- **The triage taxonomy assigns an owner:** source content (content owner) · ingestion (data
  pipeline) · retrieval (search/RAG) · generation (prompt/model) · tool (agent owner) · safety
  (security/RAI) · UX (product). **Without this step, every incident becomes "the prompt needs
  improvement."**
- Signal biases: thumbs are sparse and negative-heavy · free text is noisy and **may contain
  PII** · tickets capture only severe failures · human labels are best and expensive · automated
  eval failures are consistent but judge-biased.
- ⚠ **Owns:** feedback used to fine-tune directly without filtering — **you teach the model the
  mistakes of whoever complained loudest**.
- ⚠ **Owns:** incidents fixed but never added to regression tests, so they recur.
### Full cram reference — every topic in this file, fact by fact

Every definition, mechanism, table and failure mode from Part B (8.5.1–8.5.10), in bullet form,
so this one section is enough to revise from.

#### 8.5.10 — Eval-driven development `+` `[CORE]`

- **Behaviour specified as datasets and thresholds**, not impressions. TDD adapted to
  probabilistic systems: not one expected string, but thresholds over a representative dataset.
- **The loop:** define behaviour → build golden set → **run baseline** → make ONE change →
  compare metrics → inspect failures → ship or revert.
- **The rules:** one major variable at a time (model, prompt, chunking, top-k, reranker) · keep a
  baseline run · **split retrieval from generation metrics** · include unanswerable,
  Arabic/bilingual and permission-sensitive cases · **add every production incident permanently**.
- **The worked trap:** grounding prompt changed → faithfulness 0.89 → 0.95, abstention 8% → 22%.
  Correct if the old system guessed; too conservative otherwise. **Only the unanswerable set plus
  human review can tell you which.**
- **The release scorecard:** retrieval (hit rate, recall, precision) · generation (groundedness,
  relevance, correct abstention) · agent tools (selection accuracy, argument validity, write
  approval) · safety (red-team pass, PII leakage, harmful content) · **Arabic/bilingual segmented**
  · latency (p95/p99, timeout rate) · cost (p50/p95 per request, cache hit ratio).
- **Knobs (`typical`):** 1 variable per release · deterministic checks every commit · LLM-judged
  nightly and pre-release · golden set 200–500 · ~15% unanswerable · ~15% bilingual · **thresholds
  ratchet up only**.
- **Failure modes:** the demo set treated as an eval set · a single judge score deciding release ·
  cost and latency off the scorecard · **thresholds lowered to pass** · a better average hiding
  worse Arabic · prompt changes shipped as "copy tweaks" · a set of only easy answerable questions.

#### 8.5.1 — Evaluation harness `[CORE]`

- **The repeatable system** that runs cases through the pipeline, scores results, compares to
  baselines and **blocks regressions**.
- **Six components:** golden dataset (with **users and permissions**) · runner (**the production
  path**) · scorers · baseline store · CI gate · review UI.
- **The dataset row:** `id` · `question` · `question_ar` · **`as_user`** · `expected_behavior` ·
  `gold_answer` · `gold_chunk_ids` · **`must_not_retrieve`** · `category` · `language` ·
  `difficulty`. **Without `as_user`, permission failures are structurally invisible**;
  `must_not_retrieve` asserts the negative that catches a trimming regression.
- **Four modes:** offline (release gates; **the dataset goes stale**) · online (sampled traffic,
  drift; ground truth delayed or absent) · human review (high-stakes; expensive) · pairwise (A vs
  B; needs consistent criteria).
- **Scorer split by cost and determinism:** deterministic (schema, citation quote, forbidden
  chunk, tool args) and retrieval math (hit rate, recall, precision, MRR/NDCG) → **every commit,
  free**. LLM-as-judge (faithfulness, relevance, coherence) → **nightly and pre-release, costs
  money**. Human review → sampled, at release.
- **LLM-judge biases:** **verbosity** (length-normalized rubric) · **position** (randomize order)
  · **self-preference** (independent judge, calibrate) · **style** (require citation evidence) ·
  **language** (bilingual judge set + human calibration).
- **The CI gate:** `hit_rate@8 >= 0.90` · `context_recall >= 0.85` · `faithfulness >= 0.90` ·
  `correct_abstention_rate >= 0.90` · **`permission_leak_count == 0`** — a zero, not a threshold.
- **Failure modes:** the harness bypassing production authorization or prompt assembly · only
  happy-path questions · **evaluation running as an admin user** · golden answers not reviewed
  when policy changes · retrieval mocked unlike production · **the judge seeing the gold answer
  while measuring faithfulness** · traces not saved, so failures cannot be debugged.

#### 8.5.2 — Metrics `[CORE]`

- **A metric is useful only if it tells you what to change.** Layered: input safety → retrieval →
  generation → tool/action → output safety → UX → cost/latency.
- **Clean definitions:** groundedness/faithfulness = every material claim supported by provided
  context · answer relevance = addresses the actual question · context recall = required chunks
  retrieved ÷ required · context precision = relevant retrieved ÷ retrieved, **rank-sensitive** ·
  hit rate @k = at least one gold chunk in top-k · MRR = reciprocal rank of the first relevant
  result · tool-call accuracy = correct tool, correct step, valid arguments · task success = goal
  completed under business rules · correct abstention = declines when evidence is insufficient.
- **The diagnostic patterns:** low hit rate + high faithfulness → chunking/embeddings/hybrid ·
  high hit rate + low faithfulness → grounding prompt, temperature, validators · high relevance +
  low correctness → **corpus governance; the source or the gold answer is wrong** · high
  abstention on answerable → floor too strict · low abstention on unanswerable → **guessing** ·
  high arg validity + low task success → orchestration · good p50 + bad p99 → tail dependency ·
  quality up + cost 4× → routing, caching, pruning.
- **Segment by eight dimensions:** language · tenant/department · channel · feature · model route
  · prompt version · document source · user role. **Without segmentation, averages lie.**
- **Targets (`typical`):** hit rate @8 > 0.90 · context recall > 0.85 · precision > 0.75 ·
  faithfulness > 0.90 · relevance > 0.85 · correct abstention > 0.90 · tool-call accuracy ≥ 0.95.
- **Failure modes:** one aggregate "AI quality" number · only thumbs up/down · no segmentation ·
  reading recall or faithfulness alone rather than as a pair · **correctness confused with
  faithfulness** (a faithful answer is wrong if the source is wrong) · no abstention metric, so
  guessing is rewarded.

#### 8.5.4 — Latency telemetry `[CORE]`

- **"The model is slow" is usually wrong.** The request timeline: auth and policy lookup → input
  guardrails → query rewrite → retrieval → reranking → context assembly → **model prefill** →
  **first token (TTFT)** → streaming decode → output validation → render. For agents, multiply by
  steps, add tool calls, and **measure approval pauses separately**.
- **Metrics and their usual causes:** TTFT (long input/prefix, queueing, cold cache) · tokens/sec
  (model tier/capacity) · p50/p95/p99 (tail dependency or capacity) · step count (task design or
  tool failure) · tool latency (degraded backend) · timeout rate · fallback rate · auth latency
  (group expansion) · retrieval latency (**an unindexed filter forcing a scan**) · rerank latency
  (candidate count, cross-encoder speed).
- **Controls:** stream long human-read answers, **never machine-consumed JSON** · cache stable
  prefixes (TTFT −30–80%) · cap chunks and tool-result size · small models for routing · parallel
  read-only tools · per-dependency timeouts and fallbacks · **monitor p95/p99 by feature**.
- **Knobs (`typical`):** p95 TTFT < 1 s streamed · p95 end-to-end < 4 s non-agent · rerank
  50–300 ms for 30 candidates · rewrite ~100–300 ms · retrieval < 100 ms for top-20 · agent median
  3–6 steps · **report p95 and p99, never averages**.
- **Failure modes:** averages instead of p95/p99 · model latency not separated from
  retrieval/tool · **streaming treated as lower total latency** (it is *perceived*) · timeouts not
  visible by feature and route · the UI fast while validators fail after the user saw text ·
  **approval waits counted as model latency** · long Arabic prompts not segmented, hiding a
  tokenization-driven TTFT regression.

#### 8.5.3 — Cost & token monitoring `[CORE]`

- Attributes spend to request, user, tenant, feature, model, prompt version and agent run.
- **The full cost model, with the forgotten ones marked:** input · **cached input** ★ · output ·
  **reasoning** ★ · **embedding tokens at ingestion** ★ · **query embedding tokens** ★ ·
  **reranker calls** ★ · **LLM-judge eval runs** ★ · **agent step multiplier (10–50×)** ★ ·
  tool/API costs · vector store capacity · logging and tracing storage.
- **Attribution dimensions, written at request time** (they cannot be reconstructed later):
  `tenant` · `feature` · `route` · `prompt_version` · `model_deployment` · `index_version` ·
  token counts · `agent_steps` · `estimated_usd`.
- **Optimization levers, by size:** **model routing** (~15× tier gap) · **agent-to-workflow
  conversion** (10–50× → 1×) · **prompt caching** (50–90% on cached input) · context trimming ·
  retrieval caching · batching · downgrading/fallback.
- **Symptom → fix:** frontier on easy tasks → route by difficulty · **cache hit drops** → move
  volatile data later, stabilize schema serialization · context rising → summarize, prune, lower
  top-k · agent cost high → convert to workflow · eval cost high → deterministic in CI, judge
  nightly · embedding bill high → incremental sync and content hashes · tenant spike → per-tenant
  quotas.
- **Knobs (`typical`):** cache hit ratio 70–95%, **alert below ~0.5** · agent 10–50× a single
  answer · tier gap ~15× · cached-token discount 50–90% (`verify`) · reasoning tokens can be
  1,000–20,000+ · **budgets per tenant and per feature**.
- **Failure modes:** only the monthly invoice monitored · **cached tokens untracked, so broken
  caching is invisible** · reasoning tokens omitted · agent cost counted as one call · budgets per
  subscription only · finance seeing a bill engineering cannot attribute · **failed requests not
  counted** though retries and loops are paid for · popular questions running full RAG every time.

#### 8.5.5 — Tracing `[CORE]`

- **Metrics say something is wrong; traces say what happened in one case.** A complaint is one
  answer, not a dashboard.
- **The span shape:** auth.resolve_principals → safety.input_scan → rag.query_rewrite →
  rag.vector_search → rag.semantic_rerank → context.assemble → llm.generate →
  validator.citation_check → safety.output_scan → response.render. **For an agent:** step 1
  plan/tool → step 2 plan/approval.request → ⏸ approval.resume → step 3 tool.
- **Attributes per span:** model call (deployment, model, **prompt version**, tokens,
  `finish_reason`) · retrieval (query hash, **index version**, top-k, filters, **chunk IDs**) ·
  reranker (candidates, selected, scores) · tool (name, risk, args hash, **auth result**,
  latency) · approval (approver, decision, **evidence ID**) · validators (pass/fail reason,
  citation IDs).
- **Tools:** LangSmith · **OpenTelemetry GenAI semantic conventions** (vendor-neutral) · Azure AI
  Foundry tracing · Application Insights / Azure Monitor.
- **Security design:** use IDs, hashes and summaries unless raw content is required; restrict
  access; define retention; honour deletion; store in-region. **The balance cuts both ways** —
  redact so aggressively that incident review is impossible and you have also failed.
- **Traces feed online evaluation** — sampled production traces scored continuously are how you
  detect drift from a golden set built months ago.
- **Knobs (`typical`):** 100% of errors and high-stakes, 5–20% of routine · trace retention days
  to weeks (**distinct from audit retention, often years**) · four attributes make reproduction
  possible: prompt version, model version, index version, chunk IDs.
- **Failure modes:** tracing only in development · **prompt/model versions missing from spans** ·
  retrieval IDs missing, so citations cannot be reproduced · sensitive content with broad
  developer access · **over-redaction making review impossible** · traces outside the residency
  boundary · a bad answer whose only record is the final text.

#### 8.5.8 — SLOs for AI systems `+` `[WORKING]`

- Ordinary operational SLOs **plus quality and safety SLOs**, because the model can be up and
  still ungrounded, unsafe, slow or expensive.
- **The set:** availability 99.9% receive an answer, abstention or safe fallback · p95 RAG answer
  < 4 s, p95 TTFT < 1 s · hit rate @8 ≥ 0.90 · faithfulness ≥ 0.90 on sampled traffic ·
  **zero confirmed cross-user disclosures** · **zero writes without approval** · tool selection
  ≥ 95% · p95 cost/request under budget per feature · correct abstention ≥ 90% · golden set
  reviewed quarterly.
- **Two rows are zeros, not thresholds** — permission disclosure and unapproved writes are binary.
- **Alerts → causes:** cache hit < 50% → dynamic data in the prefix · retrieval no-result spike →
  index sync failure · p95 tool latency spike → degraded dependency · **abstention dropping
  sharply → grounding regression** · injection detections spiking → attack or poisoned source ·
  cost/request doubling → route or context regression.
- **What you cannot promise:** deterministic answers across backend changes · perfect truth when
  the corpus is wrong · zero hallucinations without abstention and verification. **State the
  control and the measured target, not impossible certainty.**
- **Fails when** availability is green while answers are ungrounded · quality SLOs are not tied to
  release gates · alerts fire with no owner or runbook.

#### 8.5.9 — Telemetry retention policy `+` `[WORKING]`

- What is stored, where, how long, at what granularity, and who can access it. **AI telemetry
  contains user questions, retrieved content, tool arguments and model outputs — it is not "just
  logs".**
- **Retention tiers:** aggregated metrics (long-lived, low sensitivity) · structured trace
  metadata (medium) · **raw prompts/responses (short, restricted)** · **tool results and retrieved
  chunks (minimize, or IDs only)** · approval records (per business/legal policy, often long) ·
  **eval datasets (governed like source data)**.
- **Design choices:** redact before export · keep raw-content sampling low and justified ·
  **separate audit retention from debug retention** · honour deletion across traces and eval
  copies · store in approved regions · restrict who can query raw traces.
- **Fails when** telemetry escapes the application's DLP, residency, access-control and deletion
  rules · debug logs become a shadow database of HR records · **eval examples copied from
  production are kept forever** · deletion ignores telemetry and caches.

#### 8.5.6 — Feedback loops `[WORKING]`

- Turns production signals into **controlled** improvements. **Not the same as training on
  feedback automatically.**
- **The workflow:** bad answer → pull trace and audit record → **classify the failure layer** →
  assess severity and data impact → fix the right layer → **add a regression case permanently** →
  run eval → canary → close with evidence.
- **The triage taxonomy, with owners:** source content (content owner) · ingestion (data
  pipeline) · retrieval (search/RAG engineer) · generation (prompt/model owner) · tool (agent
  owner) · safety (security/RAI) · UX (product owner).
- **Signal biases:** thumbs (sparse, negative-heavy, no context) · free text (noisy, **may contain
  PII**) · support tickets (severe only) · human labels (best, expensive) · automated eval
  failures (consistent, judge-biased).
- **Fails when** feedback trains or fine-tunes directly without filtering · incidents fixed but
  not added to regression tests · **the failure layer is not classified, so everything becomes a
  prompt change** · satisfaction monitored but not safety or groundedness · corrections not tied
  to the original trace.

#### 8.5.7 — Canary, shadow deployment and version pinning `[CORE]`

- **Four artifacts change independently and are behaviourally coupled:** prompt templates · model
  deployments · embedding/reranker/index versions · tool schemas and orchestration. **The release
  unit is the bundle.**
- **The bundle:** `app_version` · `prompt_version` · `model_route` (answer + verifier) ·
  `embedding.model` and `embedding.index` · `reranker` · `tool_schema_version` · `eval_baseline`.
- **Five patterns:** **version pinning** (reproducibility) · **shadow** (candidate runs, user sees
  old output — safety comparison and model migration) · **canary** (small % see the candidate —
  real UX validation) · **A/B** (controlled split, clear metric) · **rollback** (return to a
  known-good **bundle**).
- **Shadow before canary:** shadow costs money and no user risk; canary costs user risk.
- **Deprecation handling:** models and API versions are deprecated **on the provider's schedule**.
  Keep an inventory of deployments, prompts, eval baselines and retirement dates; shadow-test the
  replacement before forced migration. **The worst migration is one performed to a deadline
  without an evaluation baseline.**
- **Knobs (`typical`):** canary 5–10% · shadow 5–20% · **randomize by user, not request** · bake
  hours to days · rollback target is the whole bundle · eval baseline pinned per release.
- **Failure modes:** model names hardcoded across services · prompt changes without version IDs in
  telemetry · **embedding model changed without re-embedding and index versioning** · canary
  judged on no complaints rather than metrics · rollback that cannot restore the previous
  prompt/model/index combination · model changed while the prompt stays tuned to old behaviour ·
  tool schema changes invalidating prompt caching and tool selection.

### What this trace doesn't re-run, and why

- **8.5.8 (SLOs) and 8.5.9 (retention)** are standing definitions, not release steps. They set the
  thresholds step 8 watches against and the rules governing what step 8's traces may contain.
- **8.5.6 (feedback loops)** runs continuously in production rather than at release time. Its
  output is the *input* to the next release: new golden-set rows, prompt backlog items and
  red-team cases.
- **8.5.10 (eval-driven development)** is not a step but the frame — every numbered step exists
  because releases are decided on measurement rather than impression.
- See **C2** for the dashboard these steps feed, and **C3** for what carries into Stage 7.

Nine steps, each with mechanism, number and failure mode — and the **Full cram reference** means
this one C1 section carries every fact in the file.

## C2. The operational dashboard

What a production AI system's dashboard actually shows, and the decision each panel drives:

| Panel | Signals | The decision it drives |
|---|---|---|
| **Quality** | Groundedness, relevance, abstention, task success | Ship, hold or roll back |
| **Retrieval** | Hit rate, context recall/precision, no-result rate | Fix chunking/embeddings vs fix the prompt |
| **Safety** | Filter blocks, injection detections, red-team pass | Tune thresholds, or investigate an attack |
| **Cost** | Tokens, cached tokens, cost/request, budget burn | Route, cache, trim, or convert an agent to a workflow |
| **Latency** | TTFT, tokens/sec, p50/p95/p99, timeouts | Which stage to optimise — and it is rarely the model |
| **Agents** | Steps/run, tool errors, approval waits, thrashing | Task design, tool error quality, harness limits |
| **Feedback** | Thumbs, incidents, human-review queue | What goes into the next golden-set update |

**Read the panels in pairs, not individually.** Quality-with-retrieval localises the failing
layer; cost-with-latency shows whether an optimisation traded one for the other; safety-with-
feedback distinguishes an attack from a threshold that is simply too tight.

## C3. What Stage 6 hands to Stage 7

Stage 6 gives the discipline of production AI. **Stage 7 applies the same discipline to classic
ML** — and the parallels are exact, which is the point:

| Stage 6 (LLM systems) | Stage 7 (classic ML) |
|---|---|
| Golden set and eval harness | Train/validation/test split and held-out evaluation |
| Groundedness, relevance, abstention | Precision, recall, F1, ROC-AUC, RMSE |
| Prompt/model/index version pinning | Model registry and experiment tracking |
| Canary and shadow deployment | Shadow deployment and A/B testing |
| Cost and latency telemetry | Endpoint monitoring and resource cost |
| Feedback loops and incident triage | Drift detection and retraining triggers |
| Red-team and permission cases | Fairness and bias testing |

The unresolved problem Stage 6 hands forward is the one it cannot answer: **some questions are
predictions, not generations.** *"How many staff will take leave in December?"* and *"is this
claim likely to be fraudulent?"* are not retrieval or generation problems at all — and that is
where Stage 7 starts.

## C4. Self-test

Answer out loud. Every question here is answerable from `C1` alone.

1. Offline vs online evaluation: what does each catch that the other cannot?
2. Why is LLM-as-judge useful and dangerous? Name three biases and their mitigations.
3. Context recall is low but faithfulness is high. What do you fix, and what would a better model
   change?
4. Define TTFT, tokens/sec, p95 and p99 — and say which is driven by input length and which by
   output length.
5. What fields are needed for per-tenant cost accounting, and why can they not be added later?
6. What does a trace contain that a metric does not?
7. Give three AI SLOs that are not simple uptime, and name the two that should be zeros.
8. Why is telemetry retention a data-protection issue rather than an ops one?
9. What is the difference between canary and shadow deployment, and which comes first?
10. Why must an embedding model upgrade version the index? What is the symptom if it does not?
11. Your grounding prompt change improves faithfulness and triples abstention. Is that a win?
12. Cache hit ratio drops from 90% to 40% and nothing errors. What happened, and how would you
    have found out?
13. Why must the eval harness run as a non-admin user?
14. Every incident on your team gets fixed with a prompt change. What is wrong with that?
15. Your average latency is 2.1s and users say it is slow. Give three explanations.
16. What is the one-change rule, and what does violating it cost you?
17. A release is 3% better on quality and 40% more expensive. What do you do?
18. Which metrics are free, which cost money, and how should that shape your CI cadence?
19. Your abstention rate dropped sharply overnight. What is the most likely cause?
20. What are the four artifacts in a release bundle, and what breaks if rollback restores only
    the app?

*If you can only recite the definition and not the failure mode, it is not learned yet.*

---

*End of Stage 6. Continue to `07-Stage7-Classic-ML-MLOps.md`.*
