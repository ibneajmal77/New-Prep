# Authoring Rules — how every Stage file gets written or upgraded

**Rules version:** v2.0 (2026-08-28)  
**Reference example:** `02-Stage2-Prompt-Context-Engineering.md` after its Stage 2 rewrite.

*Companion to `00-MAP.md`. The Map is the index and the tier list — read it to know **what**
belongs where. This file is the production spec — read it to know **how** to write or upgrade
any section so it matches the current stage-file standard.*

Stage 2 (`02-Stage2-Prompt-Context-Engineering.md`) is now the reference example for the format.
Do not copy Stage 2's topic content into other stages. Extract its teaching pattern and apply it
to each stage's own topics: beginner-simple explanation first, exact examples next, practical
implementation inside the relevant concept, then senior production metrics, tools, trade-offs and
failure modes.

Apply this file to **every stage file** (`01` through `07`) when it is newly written or migrated.
Where an existing stage falls short of v2.0, record that as migration debt in §8 instead of
pretending it already conforms. The non-stage files (`08`, `10`–`18`, `30`–`36`, `40`–`41`) are
not governed by this spec unless they explicitly opt into it. Repo-root tooling files such as
`stage_conformance_check.py` are governance tooling, not curriculum content.

`08-Interview-Questions-Model-Answers.md` is a deliberate exception worth naming: it restates
stage facts but carries no `[8.x.y]` tags and no rules-status line, so nothing links a corrected
stage number back to it and no checker can reach it. Treat it as an **untracked derivative** —
when a stage fact changes, grep `08` for the same claim by hand in the same change, or give it
`[8.x.y]` tags and opt it into this spec.

---

## 0. The one rule everything else serves

**Someone should be able to revise from Part C alone, the night before an interview, and never
need to flip back into Part B.** Every rule below exists to make that true. When a rule and a
shortcut conflict, the rule wins — this file was written *because* the shortcut (citations
instead of content) was tried first and failed.

---

## 1. The three-part contract every stage file follows

```
Stage N file
│
├─ Part A  — THE BUILD           narrative spine, "why does this topic exist"
├─ Part B  — THE REFERENCE       one card per topic, full depth
└─ Part C  — ASSEMBLED           the whole stage recombined, revision-ready
```

Every stage file also carries a short rules-status line near the top:

Legal values:

- `v2.0 reference`
- `v2.0 migrated`
- `legacy v1 shape, migration debt tracked in §8`

- **Part A** exists to motivate. It never teaches a mechanism in depth — it raises a problem and
  points at the Part B entry that solves it.
- **Part B** exists to teach. Every fact, number, table and failure mode for a topic lives here,
  in full, once.
- **Part C** exists to *compress Part B back down* without losing the facts that matter for
  revision — one continuous trace, one comparison table, one handoff, one self-test. Part C is not
  a weak summary. It is shorter in *narrative* and undiminished in *fact* as defined by §4's
  compression contract.

Only Stage 1 (`01-...md`) carries global curriculum front matter such as how to read the files,
the master diagram, the library map, and the glossary. Stage 2 onward skip straight to Part A,
opening instead with a short **"Where we are"** paragraph: one sentence on what the previous stage
finished, one on the problem this stage exists to solve. Never re-explain the master diagram or
glossary per file; point back to the named Stage 1 sections instead of ambiguous shorthand like
`A2`.

### 1.1 Required skeleton

Use this skeleton unless a stage-status line says the file is still legacy debt:

```markdown
# Stage N — Stage Title (8.x)

**Rules status:** v2.0 migrated
**Where we are:** ...

# Part A — THE BUILD: Stage N

*Order note, when numeric order is not build order: ...*

## Step 1. Concrete symptom in plain words

> **→ [8.x.y Topic](#anchor-to-topic)**

# Part B — THE REFERENCE

## 8.x.y Topic title `[CORE]`

> **In the build:** Stage N, Step M — "the quoted symptom"

### 1. Simple idea

...

# Part C — Stage N assembled
```

Topic tags may have any valid depth from the map, such as `[8.3.1.4]` or `[8.6.15]`, not only
three-level tags. `+` additions keep the plus marker in both `00-MAP.md` and the topic heading.
Heading level follows role and nesting, not only number depth: CORE topics and standalone topic
cards usually use `##`; nested WORKING/AWARENESS subtopics inside a parent topic usually use `###`.
Part A still closes with an **End of Stage N** paragraph, and CORE entries still close before the
next topic.

---

## 2. Part A — the build narrative

- One running example system, identical across all seven files (see `00-MAP.md` §1 for its
  description). Never invent a new example mid-file — every step is something *that same
  government-assistant build* hit.
- Structure: `## Step N. <a question or symptom, in plain words>`, then 1–3 short paragraphs
  telling what broke or what was noticed, then one or more `> **→ [8.x.y Topic]**` links into
  Part B. Steps do not explain the mechanism — that is Part B's job. A step earns its place only
  if it names a *concrete symptom* ("the same question answered differently twice"), never an
  abstract topic intro ("now let's discuss temperature").
- End every Part A with a short **"End of Stage N"** paragraph: what the build can now do, what
  it still can't, and which stage fixes what's left — this is the sentence Part C's `C3` will
  expand into a table.
- Topics may appear in Part A out of their numeric order if the build order reads better that
  way (Stage 2 does this deliberately — see its file's order note). When you do this, say so in
  one line, the way Stage 2 does.

---

## 3. Part B — the reference entries

Tiers come from `00-MAP.md` §4: CORE / WORKING / AWARENESS / ADVANCED. Tier controls expected
depth, but topic type controls shape. A protocol, a lifecycle, a quantifiable mechanism, and a
governance framework should not be forced into identical headings. The non-negotiable coverage
set is §3.1's nine perspectives; use that list rather than maintaining a second copy here.

Do not pad WORKING or AWARENESS topics into fake CORE entries. Do not compress CORE topics so far
that a reader cannot implement or defend them.

### 3.1 CORE topics — the generalized Stage 2 card

Every CORE entry uses the Stage 2 teaching pattern. The exact heading names may change when the
topic naturally needs sub-concepts, but the entry must cover every perspective below.

1. **Simple idea**
   - Explain the concept for a strong web developer who is new to GenAI.
   - Start with plain words before technical terms.

2. **Why it exists**
   - Tie the concept to a concrete symptom from the running build.
   - Show what breaks, becomes expensive, becomes unsafe, or becomes hard to operate without it.

3. **Exact example**
   - Use real request text, payloads, schemas, token/cost examples, failure messages, tables, or
     configuration values.
   - Avoid placeholders like `<value>`, `some text`, or fake generic output.

4. **Where it fits in the system**
   - Name the owning layer: frontend, API, orchestration layer, model provider, retrieval layer,
     evaluation pipeline, release process, or operations.
   - Say what enters that layer, what leaves it, and what this topic changes.

5. **Implementation pattern**
   - Teach from local app code to production use.
   - Include Python, .NET/C#, and JavaScript/TypeScript examples where the concept can reasonably
     be implemented in app code.
   - Put each language example inside the concept subsection it implements. Do not dump all
     language examples into a separate appendix.
   - If two concepts are normally coupled in code, combine them only there and explain the coupling.
   - If the snippet uses an application wrapper such as `llmClient`, `promptRegistry`, or
     `extractToolCalls`, say it is an application wrapper unless the code is using an official SDK.
   - Show at least one relevant runtime failure path where the concept has one: retry, timeout,
     rate limit, schema validation failure, permission denial, truncation, cache miss, or safe
     refusal. Do not force a fake failure path into a pure policy/table example.

6. **Practical rules**
   - Give decision rules a developer can use during implementation.
   - Prefer "use X when Y" or "avoid X when Y" wording.

7. **Libraries, tools, and cloud ecosystem**
   - List relevant Python, .NET/C#, and JavaScript/TypeScript libraries.
   - Include Azure, AWS, Google Cloud, and other major managed services only when they directly
     support the topic.
   - For each service or tool, explain where it is used, what it manages, what the application
     still owns, and what should be logged or measured.
   - Do not add random tool catalogs. Tool coverage must teach implementation for this topic.

8. **Senior metrics**
   - Include what a senior engineer would measure: quality, latency, cost, reliability, security,
     release impact, and operational behavior where relevant.
   - Metric names alone are not enough; explain what the metric proves or catches.
   - A six-row Perspectives grid (Theory / Engineering / Operations / Cost / Security / Decision)
     is optional, not mandatory. Use it when it improves a complex topic; otherwise fold that
     judgment into practical rules, senior metrics, and failure modes.

9. **Trade-offs and failure modes**
   - Name the wrong setup and the visible symptom.
   - Include production consequences such as bad answers, injection risk, cost spikes, latency
     spikes, cache misses, evaluation blind spots, regressions, or support incidents.

Every CORE entry opens with `> **In the build:** Stage N, Step M — "the quoted symptom"` linking
back to Part A, and closes at a horizontal rule before the next entry.

### 3.2 WORKING, AWARENESS and ADVANCED topics

```
Simple idea          What it is, in plain words.
Exact example        Concrete, with real values.
Where it fits        Which layer owns it, what enters, what leaves.
Implementation note  The exact library, API, service or small code pattern.
Used when            The situation that makes you reach for it.
Fails when           The wrong setup and visible symptom.
Senior note          Metric, release concern, cost/security issue or production limit.
```

Never pad a WORKING or AWARENESS card to look like a CORE card. The tier controls depth, not the
need for clarity.

ADVANCED topics are allowed to be longer than WORKING topics when they introduce reliability,
cost, orchestration or production trade-offs. Treat them like Stage 2's advanced reliability
section: explain when the technique is worth the extra complexity, show code-shaped examples where
useful, and separate it clearly from the core path.

### 3.3 Language examples stay with the concept

Language examples must be placed where the reader needs them.

Good:

```text
Context compaction
- Python implementation
- .NET/C# implementation
- TypeScript implementation
```

Bad:

```text
Appendix: all Python examples
Appendix: all .NET examples
Appendix: all JavaScript examples
```

The reader should learn the concept and immediately see how that exact concept is implemented.

### 3.4 Cloud and tool examples must teach implementation

Mention cloud tools, SDKs, libraries and managed services only when they help implement, operate,
evaluate, secure or release the topic being taught.

For every cloud or managed-service mention, answer:

- What part of the system does it help with?
- What does the service manage for us?
- What does our application still own?
- What would we log or measure in production?
- What changes if we switch provider?

### 3.5 Number and currency labels, used throughout Part B

The label form is literal and checkable: write labels in backticks as `verify`, `typical`,
`documented default` or `example`. Plain prose uses of those words are not labels.

- **`verify`** — for anything that changes outside this document's control: prices, quotas,
  region availability, product names, SDK method names, model names, service features, cloud
  availability, contractual terms. State the *shape* of the answer, flag it, move on.
- **`typical`** — for numbers that are common in practice but not a documented default. Never
  present a `typical` number as if it were a spec.
- **`documented default`** — for a number copied from a stable product or library default that
  does not move between releases. Use `documented default` next to the number so it is checkable.
  **`verify` wins over `documented default` whenever the owner can change it.** A model provider's
  temperature default, cache TTL, minimum cacheable prefix or rate limit is a moving product
  detail, so it takes `typical`, `verify` — not `documented default`. A near-zero
  `documented default` count in a stage file is therefore normal, not a gap; only flag it when a
  genuinely stable default is sitting bare.
- **`example`** — for a value invented only for the running example. Prefer block-level coverage:
  put example values inside an explicitly labelled `Example`, `Exact example`, `worked example`,
  or table column named `example`. Use inline `example` only when one invented value appears
  outside a labelled example block/table and could otherwise be mistaken for a documented default
  or general recommendation.

Do not label mechanism facts or derived results as `example`. If a number is the mechanism itself
(`token 1` in prefix matching) or a computed consequence (`0%` when the first token changes every
request), explain the mechanism or derivation in words instead of pretending the value was invented
for the running example.

---

## 4. Part C — assembled

Part C is not a weak summary. It is the stage recombined for revision, interview recall and
production reasoning. Use the generalized Stage 2 shape below unless a later stage has a clear
reason to rename a label while preserving the same function.

Compression contract: Part C must preserve every key number, decision rule, failure mode, metric,
tool role, and operational consequence. It does not need to repeat full code samples, long prose
derivations, every library table, or every intermediate explanation from Part B unless the
self-test depends on that exact detail. This is how Part C can be shorter than Part B while still
being useful for interview-cram recall.

### C0. Simple production map

Show the stage as a production flow.

Include:

- The main request or build path.
- The stage's main control points.
- What is owned by app code, provider code, retrieval/data systems, release process and operations.

### C1. One request, end to end

Use one realistic request and walk it through the stage.

Required layers:

1. **Standing decisions before the trace**
   - Decisions that shape every request but are not re-decided every call.

2. **Compact trace**
   - Numbered steps.
   - Each step ends with `[8.x.y]` topic tags.

3. **Every step unpacked**
   - Flat bullets.
   - Cover the mechanism, concrete config or values, and owned failure modes.
   - Use bullets for revision. Avoid long paragraphs here.

4. **Full cram reference**
   - One subsection per Part B topic.
   - Include the definition mechanism, exact examples, key numbers, decision rules, metrics, tool
     names, cloud-service roles and failure modes.
   - A reader should be able to answer the self-test from this section alone.

5. **What this trace does not re-run**
   - Name standing decisions or release-time work that does not happen on every request.

### C2. The same request, four ways

Use four constraint-shaped columns, usually:

```text
Cheapest | Fastest | Most private | Highest quality
```

Rows must be specific to the stage's own topics. Do not repeat earlier-stage comparisons unless
the current stage changes the decision.

### C3. What Stage N hands to later stages

Use a table:

```text
Problem | Goes to
```

Every row must trace to something Part A explicitly left unresolved. If the answer is a later
non-adjacent stage, say that directly.

### C4. Stage implementation ecosystem map

Summarize the stage's practical implementation ecosystem.

Include:

- App-code libraries by language.
- Cloud services and managed tooling.
- Evaluation, logging, security, deployment and monitoring tools where relevant.
- What each tool is used for in this stage.

This section is a cross-topic map. Topic-specific tool explanations still belong inside Part B.

### C5. Self-test

Use 10–25 numbered questions.

Questions should sound like interview follow-ups or production-debugging prompts:

- "This happened — why?"
- "You must choose between A and B — which one and what do you give up?"
- "Where would you log this?"
- "Which part of the system owns this failure?"

Every question must be answerable from `C1`'s full cram reference.

### C6. Self-test answer key

Provide concise answers for every C5 question.

The answer key should:

- Explain the reason, not just name the topic.
- Reference `[8.x.y]` tags when useful.
- Include the operational consequence where relevant.

---

## 5. Style rules that apply everywhere

- **Bullets over paragraphs, always, for anything enumerable** — lists of causes, steps, knobs,
  metrics, tools, failure modes and comparisons. Reserve full paragraphs for Part A's narrative
  prose and Part B's concept explanation. If Part A ever turns into a table dump, or Part C ever
  turns into long paragraphs, fix it.
- **`⚠ **Owns:**` marks an owned failure mode** inline, especially in `C1`'s unpacked steps. A
  "box" means a named request-flow step, stage, system layer, or pipeline component, not
  necessarily a drawn diagram.
- **Bold the load-bearing noun phrase**, not whole sentences — `**answer field is nullable**`,
  not a bolded paragraph.
- **Numbers are never bare.** Every number in this document is either (a) a concrete example
  value from the running scenario, (b) labelled `typical`, (c) labelled `documented default`, or
  (d) flagged `verify`. A number with none of these is a number nobody can trust six months from
  now.
- **Cross-reference with the bracket tag**, `[8.x.y]`, inline — never "see above" or "as
  discussed earlier." The tag is what makes the document greppable and what C1's cram reference
  is built from.
- **Code is commented for *why*, never *what*.** A comment restating the line above it in English
  is deleted, not kept "for clarity."
- **One running example, one set of nouns.** The government entity, its staff, its leave policy,
  its Arabic-language requirement, its residency constraint — reuse these across all seven files
  rather than inventing a new scenario per topic. This is what makes the seven files read as one
  system instead of seven unrelated tutorials.

---

## 6. Numbering and tiering — inherited from `00-MAP.md`, not restated here

- Section numbers (`8.x.y`) are fixed by the original outline and never renumbered to make an
  ordering read better — reorder the *narrative*, not the numbers.
- `+` prefix marks a topic added beyond the original outline (a gap a technical or public-sector
  panel would reach for). Keep the `+` visible in both `00-MAP.md`'s index and the topic's own
  heading — it's a flag for "this earns its place, it just wasn't in the original spec."
- Tier (CORE / WORKING / AWARENESS / ADVANCED) is decided once, in `00-MAP.md`'s index, and drives
  topic depth in Part B and how much detail it earns in `C1`'s cram reference. If a topic feels
  like it has outgrown its tier while writing it, fix the tier in `00-MAP.md` rather than silently
  changing only the stage file.

---

## 7. Completion checklist — run this before calling a stage file "done"

This checklist is for files marked `v2.0 reference` or `v2.0 migrated`. Legacy files are measured
against §8's ledger until they are migrated.

- [ ] The file has a rules-status line near the top.
- [ ] Stage 2 onward has a **Where we are** opener; Stage 1 has clear global front matter and does
      not use ambiguous references like `A2` when a named section is safer.
- [ ] Part headings follow the skeleton: `# Part A`, `# Part B`, `# Part C`.
- [ ] Part A has a concrete symptom for every CORE and WORKING topic in this stage's `00-MAP.md`
      index, and no step links to a missing Part B entry.
- [ ] If Part A teaches topics out of numeric order, the file has an order note explaining why.
- [ ] Part A ends with what the stage can now do, what remains broken, and where the remaining
      problem goes.
- [ ] Every Part B topic heading matches the map number, tier, and `+` marker status.
- [ ] Every CORE topic opens with `> **In the build:** Stage N, Step M — "quoted symptom"`.
- [ ] Every CORE Part B topic includes simple idea, why it exists, exact example, where it fits,
      implementation pattern, practical rules, ecosystem/tools/cloud map, senior metrics and
      failure modes.
- [ ] Python, .NET/C# and JavaScript/TypeScript examples are placed inside the related concept
      sections where the concept can reasonably be implemented in app code.
- [ ] Code examples include a relevant failure path when the concept has a runtime failure path.
- [ ] Cloud services, SDKs and managed tools are topic-specific and explain what the app still
      owns, what the service manages, what to log/measure, and what changes if the provider changes.
- [ ] Every changing service, model, SDK, quota, price, feature, region or product detail is marked
      `verify`.
- [ ] Every number is labelled `typical`, `documented default` or `verify`, appears inside an
      explicitly labelled `Example` / `Exact example` / `worked example` block or `example` table
      column, or is a mechanism/derived value whose explanation makes that status clear. Use
      inline `example` only for an invented example value outside those blocks.
- [ ] Code blocks use real syntax and do not contain fake imports, secret values or unexplained
      missing logic.
- [ ] Senior metrics are present for every major topic and are tied to real production behavior.
- [ ] Failure modes name the wrong setup and the visible symptom.
- [ ] Part C has `C0` through `C6`, including the ecosystem map, self-test and answer key.
- [ ] `C1` contains the compact trace, unpacked steps and full per-topic cram reference.
- [ ] `C2` compares four constraint-shaped versions of the same request.
- [ ] `C3` only lists unresolved problems that Part A actually set up.
- [ ] `C4` is the stage implementation ecosystem map, not the self-test.
- [ ] `C5` questions are answerable from `C1`.
- [ ] `C6` answers every `C5` question with reasoning, not just topic names.
- [ ] Cross-references use `[8.x.y]` or deeper valid map tags such as `[8.3.1.4]`; no vague
      "see above" references.
- [ ] `+` additions are visible in both `00-MAP.md` and the stage heading.
- [ ] The stage tiering matches `00-MAP.md`; if the tier changed, the map was updated too.
- [ ] The running example stays consistent across the file.

---

## 8. Conformance ledger

This ledger prevents silent drift. A legacy row is not a condemnation; it is known migration debt.
When a stage is migrated, update this table and the stage's rules-status line in the same change.
Regenerate the mechanical facts with `python stage_conformance_check.py` before editing
this table by hand. If you need a UTF-8 Markdown file on Windows, use
`python stage_conformance_check.py --output stage_conformance_check_output.md` instead of shell
redirection. The default exit code fails only for invalid status, v2.0 drift, or untracked legacy
drift; use `python stage_conformance_check.py --strict` when you want every legacy heading issue to
fail too. Last manual review: 2026-08-28 (Stage 1 migrated in that pass). Owner: whoever
migrates the next stage.
The script derives rules status validity, C-heading labels, Where-we-are count, backticked
number-label counts, `example` block/table markers, and map-to-heading sync. The Part C shape
notes, nonstandard C2/C3 calls, answer-key debt and running-example constraint coverage are
manual review fields.

**Language coverage is a v2.0 checklist item and Stages 5–7 still fail it.** §3.1 requires
Python, .NET/C# and JavaScript/TypeScript wherever a concept is app-code implementable. Measured
2026-08-28: Stage 1 (14/12/12), Stage 2 (30/21/20), Stage 3 (14/12/12) and Stage 4 (12/11/11) carry
the trio; **Stages 5, 6 and 7 have zero C# and zero TypeScript**. Close it per stage as each is
migrated, not as a separate sweep — the counterpart has to be written against the concept, not
translated mechanically.

Running-example constraint coverage is not mechanical — a word count proves presence, not
grounding — but a zero is still a finding. Measured 2026-08-28, the bilingual Arabic/English
constraint appears in every stage except Stage 4, and the residency constraint is thinnest in
Stages 3, 4 and 7. Re-ground a missing constraint where it actually changes behaviour in that
stage; do not satisfy it by adding a mention.

When migrating a legacy Part C, the self-test usually moves from `C4` to `C5`, and the answer key
becomes `C6`. Sweep every in-file `C4`/`C5` reference in the same change; do not only rename the
heading.

| File | Rules status | Part C shape | Known debt |
|---|---|---|---|
| `01-Stage1-LLM-Fundamentals.md` | v2.0 migrated | C0–C6 | Migrated 2026-08-28. Global front matter renumbered `F1`–`F4` so it no longer collides with `Part A`; `C0` production map, `C4` ecosystem map and `C6` answer key added; self-test moved `C4`→`C5`; tier badges aligned to the map (`8.1.6` WORKING, `8.1.11`/`8.1.12` AWARENESS). Stage 1 still writes every card at full depth regardless of tier — deliberate, explained in Part B's opening note, not a tier defect. Residual: per-employee data isolation is named in the running-example description but is not yet grounded in a topic where it changes behaviour. |
| `02-Stage2-Prompt-Context-Engineering.md` | v2.0 reference | C0–C6 | Reference example. Keep future edits aligned with this file's generalized pattern, not its exact topic content. Number-label sweep should prefer explicit `example` / `documented default` markers when touching numeric sections. |
| `03-Stage3-RAG.md` | v2.0 migrated | C0–C6 | Migrated 2026-08-28. `C0` production map (two-clock index-time/query-time shape with owners), `C4` ecosystem map and `C6` answer key added; self-test moved `C4`→`C5`; tier badges aligned to the map; honesty-label sweep took `verify` from 1 to 14. Content fixes: the cache-key "permission class" resolution was identical to the option it claimed to improve on (now an explicit intersection with the corpus ACL-group set, reconciled across `8.3.5.8`/`8.3.10`/`C2`/answer key); ten dangling four-level cross-references repointed to real parent topics; `Grade A` entitlement reconciled with Stage 2's accrual rate. Second review pass same day (lens E/F): `8.3.6`'s showcase citation object would have been rejected by its own verifier (quote absent from the corpus, cited to the lead-in chunk not the table, claim unqualified against a grade-dependent corpus, two claims and one citation) — rebuilt, and the chunk-level citation example corrected in three places; `8.3.5.8`'s `secure_retrieve` fail-closed guard was dead code and `get_user_principals` hardcoded `+ ["all-staff"]`, a fail-open on the corpus's broadest scope in the one topic whose rule is fail closed — both fixed, with the accidental-fail-open pattern added to the failure modes and `C1`; the ACL OData filter is now escaped rather than string-concatenated. Full Python/C#/TypeScript parity added (12 concepts × 3, 2026-08-28) — closing the §3.1/§7 language-coverage item for this file. Residual: residency is still named only twice in the stage that decides where vectors and embedding calls live — re-ground it in `8.3.3`/`8.3.4` where it changes the decision, not by adding a mention. |
| `04-Stage4-Agentic-AI.md` | v2.0 migrated | C0–C6 | Migrated 2026-08-28. `C0` production map (read-pipeline → write-path shape, with both trust boundaries), `C4` ecosystem map and `C6` answer key added; self-test `C4`→`C5`; 11 tier badges set; label sweep took `verify` 7→13. Content fixes: **`8.4.10` (A2A) was orphaned at both ends** — no Part A step and no `C1` cram entry, with the completeness claim scoped to "8.4.1 through 8.4.9" to conceal it; now has Step 11 and a full cram entry. Ten dangling four-level cross-references repointed. Bilingual constraint re-grounded from **zero** occurrences where it changes behaviour: tool descriptions as a bilingual routing surface (8.4.2), approval cards rendering in the *approver's* language (8.4.4), Agent Card language in cross-team handoff (8.4.10). Full Python/C#/TypeScript parity added (11 concepts × 3). |
| `05-Stage5-Guardrails-AI-Security.md` | legacy v1 shape | C1–C4 with nonstandard C2 | Needs C0, C4 ecosystem map, C5/C6 split, heading tier-badge sweep, number/honesty-label sweep, and a decision on whether C2's government-panel shape should remain as a stage-specific adaptation. |
| `06-Stage6-LLMOps-Evaluation-Telemetry.md` | legacy v1 shape | C1–C4 with nonstandard C2 | Needs C0, C4 ecosystem map, C5/C6 split, heading tier-badge sweep, number/honesty-label sweep, and a decision on whether C2's dashboard shape should remain as a stage-specific adaptation. |
| `07-Stage7-Classic-ML-MLOps.md` | legacy v1 shape | C1–C4 with nonstandard C2 and C3 | Needs Where-we-are opener, number/honesty-label sweep, C0, C4 ecosystem map, C5/C6 split, heading tier-badge sweep, and decisions on whether C2's Classic ML vs LLM shape and terminal-stage C3 should remain as stage-specific adaptations. |

### Consumers of this spec

- `C:\Users\ibnea\OneDrive\Pictures\New-Prep\.claude\skills\genai-stage-review\SKILL.md`
- `C:\Users\ibnea\Final-Lesson-Implementation\generate-ai-industry-lesson\SKILL.md`

---

*This file is itself subject to the same rule as everything else in this repository: if a future
session finds a gap between what's written here and the strongest completed stage-file format,
fix this file rather than quietly deviating from it in the next stage.*
