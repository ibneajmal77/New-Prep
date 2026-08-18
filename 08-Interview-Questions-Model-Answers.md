# Part 8 - Interview Questions & Model Answers

*Use this after files 01-07. The goal is not to memorize every sentence. The goal is to learn
the answer shape: decision first, mechanism second, trade-off third, production control last.*

---

## 1. The 90-second architecture answer

**Question:** Walk me through the architecture of a secure internal GenAI assistant for a
government entity.

**Model answer:**

I would design it as layers. The user comes through an authenticated channel such as web or
Teams. The orchestrator first classifies the task and decides whether this is a simple RAG
answer, a deterministic workflow, or a constrained agent. The context layer assembles the
system prompt, prompt version, user question, conversation summary, retrieved documents and
tool schemas within a token budget.

For knowledge, documents are ingested from systems like SharePoint with ACLs, sensitivity
labels, modified dates and document versions. Scanned and Arabic documents go through
document intelligence/OCR and layout-aware extraction. Chunks are embedded with a pinned
multilingual embedding model and indexed in a vector store such as Azure AI Search or
pgvector. At query time, retrieval is hybrid: BM25 plus vector search, with metadata filtering,
permission-aware pre-filtering and reranking.

The model generates only from retrieved evidence and must cite sources or abstain. If tools are
needed, the model only proposes tool calls. Application code validates arguments, authorizes as
the authenticated user, requires human approval for writes and records the audit trail. Around
the system I would add guardrails: prompt-injection defenses, output validation, content safety,
DLP, PII redaction, scoped tools, private networking, data residency controls and retention
policy. Finally, I would operate it with evaluation and telemetry: golden datasets, RAG metrics,
LLM-as-judge with calibration, traces, per-tenant token cost, TTFT/p95 latency, feedback loops,
and canary or shadow deployment for prompts and models.

**Follow-up points to volunteer if needed:**

- Permission trimming is enforced inside retrieval, not after generation.
- The model is not the security boundary; code, identity, filters and approval gates are.
- For fixed business processes, deterministic workflows beat agents.
- Logs and traces are sensitive data and must follow residency/retention rules.

---

## 2. LLM Fundamentals

### Q1. Explain transformers, attention, tokenization and context window.

**Model answer:**

A transformer is the architecture behind modern LLMs. Text is first split into tokens by a
tokenizer. Those tokens are converted into vectors, passed through transformer blocks, and
self-attention lets each token weigh other tokens in the context to decide what information is
relevant. The context window is the maximum number of input plus output tokens the model can
handle in one call.

The practical point is that the context window is a budget. System prompts, history, retrieved
chunks, tool schemas and the final answer all compete for it, and all of it costs money. A large
window does not remove the need for retrieval because long contexts are expensive, slower and
can suffer lost-in-the-middle behavior.

**Trap to avoid:** Do not say the model reads words. It reads tokens.

### Q2. Embeddings vs generation: what is the difference?

**Model answer:**

A generation model produces text or tool-call output token by token. An embedding model turns a
piece of text into a fixed-length vector so we can compare meaning using distance or cosine
similarity. In RAG, embeddings are used to find relevant chunks; the generation model then uses
those chunks to answer.

Embeddings are not anonymous. The vector store should be treated as sensitive because vectors
can reveal meaning and are linked to source content.

### Q3. Temperature, top-p, max tokens, stop sequences and seeds.

**Model answer:**

Temperature controls how sharp or random the token probability distribution is. Low temperature
is better for extraction and factual tasks; higher temperature is useful for brainstorming.
Top-p restricts sampling to the smallest set of likely tokens whose cumulative probability
reaches p. Max tokens caps the generated output. Stop sequences end generation when a specific
string appears. Seeds can improve repeatability, but determinism is best-effort because backend
changes, hardware and tie-breaking can still change outputs.

For production extraction or tool use, I would use low temperature, structured outputs, max
token limits and validation rather than trusting seed-based determinism.

### Q4. How do you choose a model?

**Model answer:**

I start with constraints: data residency, privacy, latency, budget and required capability. Then
I route tasks to the cheapest model that passes evaluation. Classification, rewriting and simple
extraction can often use small models. Hard reasoning, complex synthesis or high-risk answers
may need frontier or reasoning models. Open-weight/self-hosted models help with residency or
control, but they shift serving, security, patching and evaluation responsibility to us.

The production answer is usually a routing layer, not one model for everything.

### Q5. Structured outputs and invalid JSON: what do you do?

**Model answer:**

I use native structured output or function-call mode where available, backed by JSON Schema or
a typed schema such as Pydantic/Zod. Constrained decoding can prevent many syntax errors by
restricting valid next tokens. Then I still validate the parsed object in code because valid
JSON can still be wrong.

If output is invalid, I use bounded retries with the validation error fed back to the model. I
also design schemas with nullable fields so "unknown" is representable. For machine consumers,
I do not stream partial JSON.

### Q6. Fine-tuning vs RAG vs prompting vs distillation.

**Model answer:**

Prompting is right when the behavior can be changed by instructions or examples. RAG is right
when the model needs current or private knowledge, especially policies and internal documents.
Fine-tuning is right when I need consistent style, format or behavior across many examples, not
when I need the model to memorize frequently changing facts. Distillation is right when a large
model performs well but is too expensive or slow, so we train a smaller model to imitate it on a
filtered dataset.

For policy documents, I would choose RAG first, not fine-tuning, because policies change and
citations matter.

### Q7. PEFT/LoRA, quantization and self-hosting.

**Model answer:**

PEFT means parameter-efficient fine-tuning. LoRA is the common method: freeze the base model and
train small low-rank adapter matrices, so the trainable part may be less than 1% of the model.
Quantization stores weights at lower precision such as 8-bit or 4-bit to reduce memory. Ollama
is useful for local development; vLLM or similar servers are better for production serving
because they handle throughput, batching and KV cache more seriously.

Self-hosting can help with residency and control, but we then own GPU capacity, scaling,
monitoring, safety filters, patching, model evaluation and supply-chain risk.

### Q8. Hallucination: causes and mitigations.

**Model answer:**

Hallucination is unsupported but fluent output. Causes include missing context, stale model
knowledge, ambiguous prompts, retrieval failure, pressure to answer, high temperature and lack
of validation. Mitigations are RAG with high-quality retrieval, grounding prompts, citations,
explicit abstention, low temperature for factual tasks, structured outputs, quote/citation
verification, answer verification and human review for high-impact decisions.

The key sentence is: "I don't know" is a designed behavior, not something we hope the model
does by itself.

### Q9. Azure OpenAI / Azure AI Foundry production concerns.

**Model answer:**

In Azure OpenAI, we call deployments, not raw model names. That gives us versioning, routing and
capacity control. I would consider pay-as-you-go for variable or early workloads and PTU for
steady high-volume workloads after measuring utilization. I would track TPM/RPM limits, quota
by region and model family, 429 rates, p95 latency and content-filter blocks.

For government use, region and deployment type matter for residency. I would use private
endpoints where required, managed identity instead of keys, content filters/content safety, and
verify model availability by region. Azure AI Foundry sits above this as the platform for
projects, model catalog, agents, evaluation, tracing and governance workflows.

---

## 3. Prompt & Context Engineering

### Q10. System vs user vs assistant roles.

**Model answer:**

The system role carries standing behavior and constraints, the user role carries user input,
and the assistant role carries previous model turns. Tool messages carry tool results in APIs
that support tools. Role separation improves structure, but it is not a hard security boundary.
Prompt injection can still influence the model, so real enforcement must happen in retrieval,
tool authorization, validation and guardrails.

### Q11. Few-shot, chain-of-thought, ReAct and self-consistency.

**Model answer:**

Few-shot prompting gives examples when the format or classification boundary is unstable.
Chain-of-thought or structured reasoning helps multi-step reasoning, especially when the
intermediate work must be inspected. ReAct interleaves reasoning and tool use: think, act,
observe, repeat. Self-consistency samples multiple answers and looks for agreement, trading
cost for confidence.

I would not apply all of them everywhere. Format problem: few-shot. Information problem: RAG or
tools. Multi-step reasoning: structured reasoning. High-stakes uncertainty: self-consistency or
human review.

### Q12. What is context engineering?

**Model answer:**

Context engineering is deciding what goes into the model window, in what order, with what budget
and what gets summarized or dropped. The window contains system prompt, examples, tools,
memory, history, retrieved chunks and the question. All of it costs money and affects quality.

I would budget context explicitly, keep recent turns verbatim, compact older history into a
task-focused summary, prune tool results, place important retrieved chunks at strong positions,
and keep stable prompt prefixes cacheable.

### Q13. Lost-in-the-middle and retrieval placement.

**Model answer:**

Models tend to use content at the beginning and end of long contexts more reliably than content
in the middle. For retrieved chunks, I would usually place the best chunk first and the
second-best last, with less important chunks in the middle. But prompt caching wants stable
content first, so I keep the stable prefix first and put volatile retrieved documents later,
using the final positions carefully.

### Q14. Prompt caching and cost.

**Model answer:**

Prompt caching reuses computation for repeated prompt prefixes. It works only when the prefix is
stable and exactly matches. That means system prompt, examples and tool schemas should come
before volatile values like timestamp, user name, retrieved documents and current question.

I would monitor cached input tokens or cache-hit ratio. A timestamp in the first line of the
prompt can silently destroy caching and increase both cost and TTFT.

### Q15. Output formatting, delimiters and refusal handling.

**Model answer:**

For output formatting, I prefer structured outputs where the consumer is code, and few-shot
examples where the consumer is human text. Delimiters separate user input and retrieved
documents from instructions, but delimiter strings must be escaped from injected values.
Refusal handling should distinguish a safety refusal, a model error, an abstention due to
missing evidence and a system failure. Each has a different user experience and audit meaning.

---

## 4. RAG

### Q16. Walk me through a production RAG pipeline.

**Model answer:**

At ingestion, I connect to sources like SharePoint, file shares or databases and capture text,
document version, modified date, ACLs, sensitivity labels and source URI. Scanned PDFs and
tables go through document intelligence/OCR and layout extraction, with special handling for
Arabic and bilingual documents. Then I chunk by structure where possible, attach metadata, embed
with a pinned multilingual model and index in Azure AI Search, pgvector or another vector store.

At query time, I resolve the user's permissions, rewrite the query if needed, run hybrid BM25
plus vector retrieval with permission pre-filters, rerank candidates, place the best chunks in
context and generate a grounded answer with citations. Then I verify citations and log the
retrieved chunk IDs, model/prompt versions and metrics.

### Q17. Arabic document handling.

**Model answer:**

Arabic adds difficulty at OCR, extraction, tokenization, normalization and retrieval. OCR must
support Arabic script. RTL and mixed Arabic/English layouts must preserve reading order.
Normalization may strip diacritics and unify letter forms, and the same normalization must be
applied to documents and queries. Arabic can consume more tokens for the same meaning, so chunk
by tokens, not characters. Embedding models must be tested on our Arabic and bilingual corpus,
not assumed multilingual from a benchmark.

### Q18. Chunking strategies and trade-offs.

**Model answer:**

Fixed chunking is simple but cuts through meaning. Recursive chunking respects paragraphs and
sentences and is a good baseline. Semantic chunking splits where meaning changes, but costs
more. Layout-aware chunking uses headings, sections, tables and pages, and is usually best for
policy or government documents. Parent-child or small-to-big retrieval embeds smaller chunks for
precision but sends a larger parent section for context.

Bad chunking sets a ceiling no reranker can fix because the correct answer may be split away
from its context.

### Q19. Embedding model choice.

**Model answer:**

I choose embeddings by language coverage, retrieval quality on our corpus, dimensions, cost,
latency and deployment constraints. For Arabic/bilingual RAG I need cross-lingual behavior:
Arabic questions should retrieve English documents and vice versa. I pin the embedding model
version in index metadata. If the embedding model changes, I re-embed the corpus and cut over to
a new index; mixing old document vectors with new query vectors breaks retrieval.

### Q20. Azure AI Search vs pgvector, HNSW vs IVFFlat.

**Model answer:**

Azure AI Search is strong when we want managed hybrid search, BM25, vector search, semantic
ranking, filters and enterprise integration. pgvector is strong when data is already in
Postgres, cost matters and we can assemble hybrid search ourselves.

HNSW is usually the default ANN index because it gives strong recall and speed at the cost of
memory. IVFFlat can be useful when memory is constrained and the dataset is more stable, but it
needs training and can degrade as data distribution changes.

### Q21. Hybrid retrieval and reranking.

**Model answer:**

BM25 finds exact terms, identifiers and rare keywords. Vector search finds semantic matches.
They fail in different ways, so production RAG usually uses both and fuses by rank, often with
reciprocal rank fusion, because BM25 scores and cosine scores are not directly comparable. Then
a reranker, such as a cross-encoder or semantic ranker, examines query and candidate text
together to decide which chunks actually answer the question.

The pattern is retrieve wide and cheap, rerank narrow and accurate.

### Q22. Security trimming / permission-aware retrieval.

**Model answer:**

Security trimming means retrieval only returns documents the current user is allowed to see. It
must happen as a pre-filter inside the search query, not after generation and not only after
retrieval. ACLs and sensitivity labels must be captured at ingestion. At query time, I resolve
the user's effective permissions, including transitive group membership, and apply those filters
in the vector/keyword query.

I also re-check permissions after fusion, reranking, parent expansion and cache lookup. Caches
must be keyed by permission scope or user context, otherwise one user's allowed result can be
served to another user.

**Strong follow-up:** Post-filtering is unsafe because forbidden documents can influence ranking,
leak through logs/tool results, and create side-channel or caching leaks.

### Q23. Grounding, citations and "I don't know".

**Model answer:**

The generation prompt should instruct the model to answer only from provided sources, cite the
specific chunks and abstain when evidence is insufficient. Then code verifies that citations
refer to retrieved chunks and quoted text actually appears in those chunks. "I don't know" must
be represented in the schema so abstention is a valid successful output, not a failure.

### Q24. GraphRAG, agentic RAG, table RAG and SQL RAG.

**Model answer:**

GraphRAG is useful when relationships matter, such as policies referencing committees,
exceptions and delegations. Agentic RAG treats retrieval as a tool and lets the model search
iteratively for multi-hop questions. Table RAG preserves tables as structured rows rather than
flattened prose. SQL RAG or text-to-SQL is for questions where the answer is in a database, not
a document.

For text-to-SQL I would use schema allowlists, read-only credentials, query validation, row
limits, timeout limits and approval for risky queries.

### Q25. RAG evaluation.

**Model answer:**

I separate retrieval metrics from generation metrics. Retrieval hit rate asks whether the gold
chunk appeared in top-k. Context recall asks whether the needed chunks were retrieved. Context
precision asks whether retrieved chunks were relevant and ranked well. Groundedness or
faithfulness checks whether the answer is supported by the context. Answer relevance checks
whether it answered the question.

The golden set should include answerable, unanswerable, Arabic/bilingual, exact identifier,
multi-hop and permission-sensitive cases. Tools like RAGAS and Azure AI Evaluation SDK can help,
but deterministic retrieval and citation checks should run in CI.

---

## 5. Agentic AI

### Q26. What is an agent?

**Model answer:**

An agent is a loop where the model decides the next step at runtime: plan or reason, call a tool,
observe the result, then repeat until done or stopped. The key difference from a workflow is
control flow. In a workflow, code owns the path. In an agent, the model chooses the path within
the limits we enforce.

### Q27. ReAct, plan-and-execute and reflection.

**Model answer:**

ReAct interleaves reasoning, action and observation one step at a time. Plan-and-execute first
creates a plan, then executes it; this is useful where the plan can be approved before actions.
Reflection asks the model or another process to critique and improve the output. Reflection can
improve quality but costs extra calls and can create loops if not bounded.

### Q28. Tool/function calling.

**Model answer:**

Tool calling is structured output for actions. We describe tools with names, descriptions and
JSON schemas. The model returns a proposed tool call and arguments. It does not execute the
tool. Our code validates schema, applies business rules, authorizes as the session user, checks
approval requirements, executes the tool and returns a pruned result to the model.

Tool descriptions are prompts. They should say what the tool does, when to use it and when not
to use it.

### Q29. When does a deterministic workflow beat an agent?

**Model answer:**

If I can draw the flowchart in advance, I prefer a deterministic workflow. For example, leave
submission is always validate dates, check balance, request approval, create record and notify
manager. A model can extract the dates, but code should own the process. Agents are justified
when the next step depends on runtime information in a way we cannot enumerate, such as planning
around calendars, holidays and user preferences.

In regulated systems, being able to choose not to use an agent is the senior answer.

### Q30. Human-in-the-loop and Power Automate approvals.

**Model answer:**

HITL is a durable approval gate before execution of risky actions. The agent proposes a write
tool, code validates and authorizes it, then the orchestrator checkpoints state and sends an
approval request. In a Microsoft environment, that approval can be a Power Automate approval
card in Teams or Outlook. When the decision comes back, the orchestrator reloads the checkpoint,
revalidates business rules and permissions, then executes or rejects.

The audit must record who approved, what exact action and arguments they saw, what evidence was
shown, when they approved and which run it belonged to.

### Q31. State and memory.

**Model answer:**

State is what the current run needs to continue: current step, messages, observations, pending
tool, approval ID and cost so far. Memory is information intentionally reused across turns or
sessions, such as conversation summary or user preferences. They should be separate. Checkpoints
need expiry, access controls and reauthorization on resume. Long-term memory must not become
"store everything forever."

### Q32. Agentic harness.

**Model answer:**

The harness is the control shell around an agent: tool registry, tool permission scope,
sandboxing, step caps, loop caps, timeouts, token/cost budget, result-size limits, approval
gates, rate limits, tracing and replayability. It must be enforced in code, not merely written
in the prompt. The harness is what makes an agent operable.

### Q33. Multi-agent systems.

**Model answer:**

Multi-agent systems split work across specialist agents, often with a supervisor. They help
when domains and tool permissions are genuinely separate, like HR, IT and facilities. They hurt
when used for simple tasks because every handoff adds cost, latency, shared-state complexity and
failure modes. The supervisor should route and compose, not become a superuser with every tool.

### Q34. MCP.

**Model answer:**

MCP, Model Context Protocol, standardizes how model hosts connect to external tools, resources
and prompts exposed by MCP servers. A server can advertise a tool like `create_ticket` or a
resource like a schema. MCP standardizes the integration surface, but it does not solve
authorization, data classification, output validation or approval. Those remain the host and
enterprise system's responsibility.

### Q35. Agent failure modes.

**Model answer:**

Main failures include infinite loops, tool thrashing, prompt injection through tool output,
over-agency, context bloat, goal drift, permission drift and hidden partial failures. Controls
include step caps, repeated-call detection, actionable sanitized tool errors, scoped tools,
approval gates, context pruning, final status schemas and traces.

---

## 6. LLMOps, Evaluation & Telemetry

### Q36. What is an automated evaluation harness?

**Model answer:**

It is a repeatable pipeline that runs golden cases through the AI system, captures outputs and
scores them against thresholds. It includes datasets, a runner, deterministic checks, LLM judge
checks, human review and baseline comparison. It should run cheap deterministic checks in CI and
heavier LLM-judged evaluations nightly or before release.

### Q37. LLM-as-judge and biases.

**Model answer:**

LLM judges are useful for relevance, groundedness and qualitative comparisons, but they have
biases: verbosity bias, position bias, self-preference, style bias and language bias. I would
use rubrics, randomize pairwise order, calibrate against human labels, segment by language and
avoid using judge scores as the only gate for security-sensitive behavior.

### Q38. Metrics.

**Model answer:**

I track groundedness, relevance, coherence, toxicity, task success, tool-call accuracy,
retrieval hit rate, context precision/recall, abstention rate, cost and latency. The point is
diagnosis. Low context recall with high faithfulness means retrieval is the bottleneck. High
retrieval recall with low faithfulness means generation or validation is the issue.

### Q39. Cost and token monitoring.

**Model answer:**

I record tokens and cost per request, user, tenant, feature, model route and prompt version.
That includes input tokens, cached input tokens, output tokens, reasoning tokens when exposed,
embedding tokens, reranker calls and agent steps. Then I set budget alerts and optimization
levers: model routing, caching, batching, context trimming, downgrading and converting fixed
agents into workflows.

### Q40. Latency telemetry.

**Model answer:**

I break latency into retrieval, reranking, context assembly, model prefill, TTFT, tokens/sec,
tool calls, validation and total request time. I monitor p50, p95 and p99, not just average.
Streaming improves perceived latency by lowering time to first visible output, but total work is
mostly unchanged and strict validation may require buffering.

### Q41. Tracing.

**Model answer:**

Tracing gives the forensic record for a single request: auth, retrieval, reranking, prompt
version, model call, tool calls, approvals, validators and final answer. LangSmith is common for
LangChain/LangGraph. OpenTelemetry GenAI semantic conventions help standardize traces. Azure AI
Foundry and Azure Monitor/Application Insights can provide tracing and monitoring in Azure
environments. Trace data is sensitive and must follow retention and residency controls.

### Q42. Feedback loops.

**Model answer:**

Feedback should turn production failures into controlled improvements. A bad answer creates a
triage item. We pull the trace, classify the failure layer, fix the source/retriever/prompt/tool
or guardrail, add a regression case, run evals and deploy through canary. We should not blindly
train on thumbs-down feedback because feedback is sparse, biased and may contain PII.

### Q43. Canary, shadow deployment and version pinning.

**Model answer:**

Version pinning means every response can be traced to a prompt version, model deployment, tool
schema and index version. Shadow deployment runs a candidate in parallel without showing it to
users. Canary sends a small percentage of traffic to the candidate. Both need quality, safety,
latency and cost metrics. Rollback must restore the full bundle, not only application code.

---

## 7. AI Guardrails & Security

### Q44. OWASP Top 10 for LLM apps.

**Model answer:**

The major risks are prompt injection, sensitive information disclosure, supply chain risk, data
and model poisoning, improper output handling, excessive agency, system prompt leakage, vector
and embedding weaknesses, misinformation and unbounded consumption. For each, I map a control:
prompt-injection defenses, DLP, dependency and model review, ingestion provenance, output
validation, scoped tools, no secrets in prompts, treating vectors as sensitive, grounding and
citations, and rate/budget limits.

### Q45. Direct vs indirect prompt injection.

**Model answer:**

Direct injection comes from the user, such as "ignore instructions." Indirect injection comes
from retrieved documents, emails, tickets, tool output, OCR text or images. Indirect is often
more dangerous because the system itself brought the hostile text into context. Defenses are
input/output separation, spotlighting untrusted content, prompt shields, least-privilege tools,
authorization, deterministic post-checks and never trusting model output as code or commands.

### Q46. Content filtering.

**Model answer:**

Content filtering should happen at multiple points: input, retrieved content, tool outputs and
final output. In Azure-heavy systems I would consider Azure AI Content Safety, Azure OpenAI
content filters, Prompt Shields, groundedness detection, protected material detection, custom
categories and blocklists. Thresholds need tuning and human review, especially for legitimate HR
or incident-reporting topics that may contain sensitive language.

### Q47. Output validation and safe rendering.

**Model answer:**

Output validation checks schema, business rules, citations, PII, safety and rendering. Valid
JSON is not enough. A model answer may be schema-valid but cite a nonexistent source or include
raw HTML. The UI should sanitize markdown/HTML, verify links and avoid rendering untrusted model
output directly.

### Q48. Tool permission scoping.

**Model answer:**

Each agent gets only the tools it needs. Tools are split by risk and action. Identity comes from
the authenticated session, never model arguments. Where possible tools call source systems
on-behalf-of the user with scoped tokens. Writes require approval. Broad admin tools or SQL
tools should not be exposed casually. This limits blast radius when the model or prompt is
manipulated.

### Q49. Audit logging.

**Model answer:**

Audit logs should answer who asked what, what documents were retrieved, what the model answered,
what tool calls were proposed/executed, who approved what, what safety filters triggered and
which model/prompt/index versions were used. Logs need access control, immutability where
required, retention policy and PII minimization. Logs and traces can become a data leak if they
store raw sensitive prompts broadly.

### Q50. Data protection and residency.

**Model answer:**

Data protection covers prompts, completions, embeddings, vectors, tool args/results, traces,
logs, caches and eval datasets. I would verify no training on tenant data, choose the correct
region/deployment type for residency, use private endpoints where required, use managed identity
instead of keys, redact before model calls where possible and ensure deletion touches vectors,
caches and telemetry, not only source documents.

### Q51. Responsible AI frameworks and governance.

**Model answer:**

I use frameworks to operationalize controls, not just name-drop them. NIST AI RMF gives govern,
map, measure and manage. ISO/IEC 42001 frames an AI management system. Microsoft Responsible AI
guides accountability, transparency, fairness, reliability/safety, privacy/security and
inclusiveness. For UAE/Dubai government context, I would align with national AI strategy and
Dubai ethics principles around public benefit, fairness, transparency and accountability.

Governance means use-case intake, data classification, risk rating, approval process, model and
vendor risk review, AI register, monitoring plan and periodic review.

---

## 8. Classic ML & MLOps

### Q52. Supervised vs unsupervised learning.

**Model answer:**

Supervised learning uses labelled examples, such as ticket features with a label showing whether
the ticket breached SLA. Unsupervised learning finds structure without labels, such as clustering
similar service requests or detecting anomalous claims. The choice depends on whether we have a
target label and a prediction decision.

### Q53. Train/validation/test, overfitting and cross-validation.

**Model answer:**

The training set fits the model, validation tunes features and hyperparameters, and the test set
estimates final performance. Overfitting happens when the model learns training noise and fails
on new data. Cross-validation gives more stable estimates when data is limited, but for
time-dependent data I prefer time-based splits or rolling validation to avoid future leakage.

### Q54. Precision, recall, F1, ROC-AUC, RMSE and MAE.

**Model answer:**

Precision asks: of what we flagged, how much was truly positive? Recall asks: of all true
positives, how much did we catch? F1 balances them. ROC-AUC measures ranking across thresholds,
but PR-AUC is often better for rare positives. RMSE and MAE are regression metrics: MAE is
easier to explain, RMSE penalizes large errors more.

For SLA breach prediction, recall may matter more because missing a breach is costly, but the
threshold must respect how many tickets supervisors can review.

### Q55. Feature engineering, leakage and class imbalance.

**Model answer:**

Feature engineering creates inputs from raw data. Leakage happens when a feature contains
information not available at prediction time, such as resolution time or escalation notes added
after the breach. Class imbalance happens when one class is rare, making accuracy misleading.
Controls include feature availability timestamps, time-based splits, class weights, threshold
tuning, PR-AUC, and resampling only inside training folds.

### Q56. Azure ML.

**Model answer:**

Azure ML provides workspaces, compute, data assets, pipelines, model registry and managed online
or batch endpoints. The production path is code version plus data version plus environment plus
parameters into a training job, logged metrics, registered model, deployment and monitoring.
Online endpoints serve real-time predictions; batch endpoints score large sets on a schedule.

### Q57. MLflow.

**Model answer:**

MLflow tracks experiment parameters, metrics, artifacts, model signatures, code versions, data
versions and model artifacts. It gives reproducibility and lineage from production model back to
the training run. Without data version and code version, experiment tracking is incomplete.

### Q58. Drift, model decay and retraining.

**Model answer:**

Data drift means input distributions change. Concept drift means the relationship between
features and target changes. Prediction drift means model outputs shift. Model decay is the
business result getting worse over time. I would monitor input schema, data distributions,
prediction distribution, delayed ground-truth performance, fairness segments and business
outcomes. Retraining should be triggered by measured degradation or major process change, then
validated before promotion.

### Q59. End-to-end ML lifecycle.

**Model answer:**

For SLA breach prediction: assessment defines the objective, risk and metric. Data prep gathers
historical tickets, labels breaches, removes leakage and splits by time. Build trains baselines
and candidates with tracked experiments. Test measures recall, precision, PR-AUC, calibration
and segment performance. Validate includes SME review, fairness, explainability, security and a
model card. Deploy uses Azure ML online or batch endpoints with canary or shadow. Monitor tracks
drift, performance, fairness and incidents. Support handles retraining, rollback, model card
updates and periodic review.

---

## 9. High-Pressure Follow-Ups

### "Why not fine-tune on policy documents?"

Because policy knowledge changes, needs citations and must respect permissions. RAG is better
for current, source-grounded, permission-filtered knowledge. Fine-tuning may help tone or
format, but it is not the right primary mechanism for mutable policy facts.

### "Why is post-filtering RAG permissions unsafe?"

Because forbidden documents may influence ranking, logs, caches, reranker inputs or the model
before you remove them. Permission filtering must happen inside retrieval as a pre-filter and be
rechecked after fusion, reranking, parent expansion and cache lookup.

### "What is the one sentence for agent safety?"

The model proposes; code validates, authorizes, approves and executes.

### "What is the difference between observability and audit?"

Observability tells operators how the system behaves. Audit tells investigators who did what,
who saw what, what evidence was used and who approved which action.

### "What is your answer when someone wants agents everywhere?"

If the flowchart is knowable, use a deterministic workflow and model-powered steps. Use agents
only when runtime branching genuinely requires delegated control flow, and only with a harness.

### "What would you say to a government AI review board?"

I would present the use case, data classes, affected users, model/provider, region and
residency, permission model, guardrails, HITL, audit logging, evaluation results, red-team
results, monitoring plan, owner, rollback plan and AI register entry.

---

## 10. Phrases To Use

- "The model is not the enforcement point."
- "Permission trimming must happen before retrieval results enter the context."
- "Valid JSON is syntax, not correctness."
- "A prompt is a behavioral specification and should be versioned like code."
- "A golden set without unanswerable, Arabic and permission-sensitive cases is incomplete."
- "A deterministic workflow beats an agent when the flowchart is known."
- "HITL is a checkpointed state transition, not a chat message."
- "Tool descriptions are prompts, but tool authorization is code."
- "Telemetry is sensitive data."
- "I choose the metric from the business cost of errors."

## 11. Phrases To Avoid

- "The system prompt prevents prompt injection."
- "We can fine-tune the model on the documents so it knows the policies."
- "The model will decide whether the user is allowed."
- "We use accuracy for imbalanced classification."
- "We keep all prompts forever for debugging."
- "We use the newest model for everything."
- "The agent executes the tool."
- "A vector database is anonymized."
- "If the answer has citations, it is grounded."
- "Streaming makes the model faster."

---

*End of interview drill file.*
