---
name: genai-stage-review
description: 360-degree critical review, fix, and authoring skill for any GenAI curriculum stage file (01–07) in this repo. Checks authoring-rules v2.0 compliance, map coverage, internal consistency, technical accuracy, security, pedagogy, and production rigor; drafts new or missing topic cards in the shape that topic actually needs; calibrated to the generalized Stage 2 pattern without copying Stage 2 content. Use for "review stage N", "audit 0X-StageX-...md", "apply the Stage 2 pattern to Stage X", "write/draft topic 8.x.y", "draft the ◇ proposed topics", or "critique this GenAI file".
allowed-tools:
  - Read
  - Grep
  - Glob
  - Bash
  - Edit
---

# GenAI Stage Review & Authoring — calibrated to the generalized Stage 2 precedent

## What this skill is for

This repo is a seven-stage GenAI/LLM engineering curriculum (`01-Stage1-...md` through
`07-Stage7-...md`), governed by two spec files: `00-MAP.md` (the index, the master architecture,
the topic list with tiers) and `00-Authoring-Rules.md` (the production spec for how every Part
A/B/C gets written). `02-Stage2-Prompt-Context-Engineering.md` is the file this skill was
extracted from, after a full critical-review-then-fix pass — treat its **current, fixed state**
as the calibration example for rules v2.0. Use it for three separate things: what good looks
like, how a fix gets made, and — this is the part that's easy to oversimplify — **what range of
shapes a good topic card is allowed to take.** Stage 2 is a reference example, not a template to
copy. Matching Stage 2 means matching its adaptive pattern, not cloning one topic's exact block
sequence onto every other topic.

This skill has two modes:

- **Review mode** (Phases 1–4 below): audit an existing stage file and fix what's wrong.
- **Authoring mode** (its own section below): draft a new topic card — either one that's missing
  from a file entirely, or one of `00-MAP.md`'s `◇`-marked proposed topics that doesn't exist in
  any file yet.

Invoke Review mode on a target stage file (e.g. `03-Stage3-RAG.md`) to run the same process that
produced Stage 2's fixes: **review it from every angle below, present the findings and a
concrete numbered change list, wait for the user to confirm, then implement.** If the invocation
explicitly says to skip confirmation (e.g. "review and apply", "--apply"), go straight to
implementation but still report findings before editing.

Never run this against `00-MAP.md` or `00-Authoring-Rules.md` themselves without the user
explicitly asking — they are the spec other files are measured against, not curriculum content.

---

## Before starting: read the current sources of truth

From the New-Prep repo root, run `python stage_conformance_check.py` first. Treat its output as
the mechanical baseline for status, C headings, label counts/example markers, and map-to-heading
sync; if it exits non-zero, include the table in the review context and spend the 10 detailed
findings on judgment issues the script cannot see instead of repeating every mechanical row. Use
`--strict` only when you intentionally want tracked legacy heading debt to fail the run too. If you
need to save the table to a file on Windows, use `python stage_conformance_check.py --output <path>`
instead of PowerShell redirection.

1. **`00-MAP.md`** — pull the target stage's row from the "complete index" (§6): the exact topic
   list, each topic's tier (CORE / WORKING / AWARENESS / ADVANCED), and any `+`-prefixed (already
   drafted, missing from the map) or `◇`-prefixed (not drafted anywhere yet) additions. This is
   the ground truth for "is anything missing," not a guess from the file's table of contents.
   Do not assume file number equals topic number: Stage 5 is section `8.6`, and Stage 6 is section
   `8.5`.
2. **`00-Authoring-Rules.md`** — read the rules version, the current Part A/B/C contract, the §7
   completion checklist, and the §8 conformance ledger. Compare the target stage's rules-status
   line to the rules version. If the stage is marked legacy, report v2.0 gaps as migration debt
   instead of pretending they are surprising regressions.
3. **The target stage file itself.** Read Part A and Part C in full. Read Part B topic card by
   topic card, using the map row as the checklist. Use `rg`/search for repeated numbers, claims,
   examples, and cross-references before editing. Do not review from isolated grep fragments, but
   do not exhaust the whole context window before producing findings either.

Use a practical stopping condition: prioritize high-severity correctness, security, map/rules
drift, and internal-consistency findings first. For a normal review report, cap findings at the
highest-value 10 unless the user asks for an exhaustive audit. If there are more than 10 real
findings, report the top 10 fully and list the rest as one-line titles under "Not detailed".

Do not skip re-reading `00-MAP.md` and `00-Authoring-Rules.md` on the assumption they're
"already known" from a prior session — they are the source of truth and must be re-verified
against the current files on disk each time, per the project's own rule that memory of past
state is not the same as current state.

---

## Baseline non-negotiables — apply to every topic, in either mode, regardless of shape

These are not part of the shape a topic gets. They are the floor every shape sits on, whether the
topic gets nine blocks or three paragraphs. Stage 2 is the current reference example for this
floor, but re-read the file before relying on a prior session's memory of it.

- **A beginner entry point before any mechanism.** A one-sentence plain-English "simple idea" or
  definition a newcomer can grasp, plus the recurring "for a web developer, think of X as Y"
  bridge (or whatever the nearest "translate to something the reader already knows" device is for
  that specific topic type — see the shape table for what that device is per type).
- **Escalation all the way to senior nuance.** The card must not stop at "here's what it is." It
  has to reach cost, security, production failure modes, and "when *not* to use this" before it
  ends — the beginner-to-senior arc is the whole point of the card, not an optional tail section.
- **Senior perspective as judgment, not just facts.** A "use X when Y" decision rule and honest
  trade-offs are required content. Where the shape includes a dedicated Perspectives grid, it
  lives there; where the shape doesn't (the lean and menu shapes), it's folded into
  practical-rules / senior-metrics / fails-when instead — but it must be present somewhere. A
  card that only states facts with no judgment attached has failed this regardless of shape.
- **Implementation evidence in the right form.** Use Python, .NET/C#, and JavaScript/TypeScript
  examples where the concept can reasonably be implemented in app code. For governance, policy,
  compliance, or process topics, the better deliverable may be a schema, config, audit-log shape,
  release gate, evaluation row, or approval workflow instead of three SDK snippets. At least one
  relevant failure path should be handled where the concept has a runtime failure mode.
- **The mechanical authoring-rules floor**: `[8.x.y]` cross-reference tags inline, `verify`/
  `typical`/`documented default` labels for changing or general numbers, block/table-level example
  markers for worked scenario values, the same running
  example's nouns (government entity, bilingual Arabic/English staff, leave policy, residency
  constraint), bullets over paragraphs for anything enumerable.

## Topic-shape classification — decide this before reviewing depth or drafting anything

Stage 2 itself proves depth and block sequence should vary by topic type. Classify the topic
first (checking `00-MAP.md`'s tier for it is part of this, but tier alone — CORE/WORKING/
AWARENESS/ADVANCED — doesn't fully determine shape; two CORE topics can legitimately take
different shapes, exactly as `8.2.1` and `8.2.4` do despite both being CORE).

| Topic type | Reference example | Shape |
|---|---|---|
| Procedural pattern/technique | `8.2.1`, `8.2.2`, `8.2.6` | Lean sequence: simple idea → why it matters → concrete example → where it is used → implementation → practical rules → library/ecosystem table → senior metrics → fails-when or trade-offs. Judgment folds into practical rules, senior metrics, and the closing failure block. |
| Quantifiable mechanism (has real cost/latency/ratio math) | `8.2.4`, `8.2.5` | Deep sequence: everything in the lean shape, plus worked arithmetic, mechanism rules, a resolved tension with adjacent topics where relevant, and optionally a Perspectives grid when it clarifies the engineering judgment. |
| Lifecycle/process | `8.2.3` | Process-shaped: the lifecycle's own stages as sub-sections, ending in implementation, practical rules, metrics and failure modes. |
| Optional/advanced extension (tier `[ADVANCED]`) | `8.2.7` | Menu shape: several sub-techniques, each given a compact mini-treatment. Breadth across options matters more than depth on any single one, because the entry is reached for only once the core techniques stop being enough. |
| **Protocol/standard** | `8.4.10` A2A, if present in the current stage file | Contract-first: what problem it solves versus sibling protocols/standards, the actual message or handshake shape, where it sits on the master architecture diagram (`00-MAP.md` §2), current adoption maturity, then integration code or schema/config. Less mechanism math than the quantifiable-mechanism shape. |
| **Compliance/governance/framework** *(new)* | no drafted example checked yet — proposed by reasoning about the content type, not observed | What's actually required and by when, who inside the org is accountable, which existing architecture-diagram box is where this gets enforced, then a structural (not just a sentence) `verify`-heavy framing — this content moves faster than engineering mechanics do. |
| **Emerging/proposed** (`◇` in `00-MAP.md`) *(new)* | whichever topics carry `◇` in the map's index at the time — check the map, don't assume a fixed count | "State of the field, as of [date]" framing up front: what's genuinely live vs. merely announced, named real adopters, then the rest of whichever shape above fits the topic's actual nature (a proposed protocol still gets the protocol shape; a proposed governance framework still gets the governance shape) — but with heavier, more frequent `verify` labelling throughout than a settled-engineering topic needs, because the underlying facts (adoption %, fines, launch partners) are genuinely time-sensitive in a way prompt-caching mechanics are not. |

**Evidence level differs by row, and that matters when you rely on one.** Add an evidence note in
the review when a shape is observed in Stage 2, observed once elsewhere, or proposed by reasoning
from the topic type. Do not write first-person claims such as "I checked"; future agents need a
repeatable instruction, not a stale session memory.

When reviewing, the check is: **was the shape that was chosen the right one for what this topic
actually is** — not "does it have exactly nine blocks." Flag a quantifiable-mechanism topic that
was written without the worked numbers a reader needs, and flag a procedural-pattern topic bloated
into the deep shape for no reason (padding, not rigor). When authoring, this table is what you
pick from *before* drafting a single block.

---

## Review mode

Phases 1–4 below. This is one of the skill's two parallel modes (see "Authoring mode" further
down for the other) — it does not lead into or depend on Authoring mode running afterward; they
are two separate entry points into the same skill, chosen by what was actually asked for.

## Phase 1 — Review, across every lens below

Work through all nine lenses. Not every lens will surface a finding in every file — say so
rather than inventing filler. For each finding, cite the exact section (`[8.x.y]`) and, where
useful, an approximate line reference, exactly as the Stage 2 review did.

### A. Authoring-rules structural compliance
Run the `00-Authoring-Rules.md` §7 completion checklist against the file, read together with the
"Topic-shape classification" table above. Also check the target file's rules-status line against
the §8 conformance ledger:
- Does every Part A step link to a real Part B entry, and does every CORE/WORKING topic in this
  stage's `00-MAP.md` row have a Part A step raising it?
- Does every topic use the shape appropriate to *its own type*, per the classification table —
  not "does it have exactly nine blocks." Flag a mismatch either direction. The baseline
  non-negotiables apply no matter which shape was chosen.
- Is every number labelled `verify`, `typical`, `documented default`, covered by an
  Example/worked-example block or table, or clearly explained as a mechanism/derived value?
- Does v2.0 Part C have `C0` through `C6`: production map, trace/cram reference, four-way
  comparison, handoff, ecosystem map, self-test, and answer key? For a legacy stage, report the
  missing subsections as known migration debt if they match the ledger.
- Does `C1` contain the compact trace **and** the per-step bullet unpacking (mechanism / concrete
  numbers used / `⚠ **Owns:**` failure-mode bullets where relevant) **and** a full per-topic cram
  reference covering every topic in the stage? Spot-check: pick three self-test questions at
  random and confirm each is answerable from `C1` alone without opening Part B.
- Is `C1` written in bullets, not paragraphs? Flag any "X, which means Y, and therefore Z" prose.
- Does `C2` have four constraint-shaped columns (or a stage-appropriate renamed variant) with rows
  specific to *this* stage's own topics, not Stage 1's rows repeated?
- Does `C3` trace every row to something Part A explicitly left unresolved, with non-adjacent
  hand-offs called out explicitly (e.g. "this isn't fixed by the next stage, it's fixed three
  stages later")?
- Does the self-test section exist, and does the answer key exist when the target status is v2.0?
- Cross-reference tags are `[8.x.y]` inline, never "see above"; numbers are never renumbered to
  read better (reorder narrative, not numbers); the running example (government entity, bilingual
  Arabic/English staff, leave policy, residency constraint, per-employee data isolation,
  human-approval-only actions) is the only scenario used — flag any orphan example invented for
  convenience.

### B. Map coverage
Cross-check every topic number in this stage's `00-MAP.md` row is actually present in the file,
correctly tiered (a WORKING topic given a CORE card, or vice versa, is a defect either
direction), and that `+`-prefixed additions are marked as such in the file's own heading, not
just in the map. For a `◇`-marked topic, the check runs the other way: its absence from the file
is *correct* by definition — flag it only if the file actually *does* contain that topic now
(meaning Authoring mode drafted it at some point and the map's marker was never updated from `◇`
to `+`, which is a real defect to report and fix, per the map-sync step in Authoring mode below).

### C. Internal consistency — the highest-value check
This is what produced most of the Stage 2 fixes. Every fact that appears in more than one place
(Part A's callout, Part B's full entry, C1's compact trace, C1's cram reference, C2's comparison
table, a self-test question) must state the **same number, the same mechanism, the same outcome**
everywhere. Concretely:
- Grep every worked number, worked example's answer, and named cost/ratio figure across the whole
  file. If it appears 2+ times, diff the surrounding claims by hand.
- Check that a narrative claim about *how* something works (e.g. "a parameter does X") is
  actually reflected in the code sample shown for it, not contradicted by it. (Stage 2's bug: the
  prose asserted a native multi-sample API parameter billed input once; the actual code shown was
  a manual loop of N separate calls — the two told different stories about the same mechanism.)
- Check that an "alert at threshold T" recommendation doesn't contradict a "this metric is
  expected to be low/zero under condition C" statement made elsewhere in the same entry.
- Check that a worked example's "before" (wrong/naive) state and "after" (correct) state actually
  differ for a *demonstrable reason* tied to the technique being taught — not coincidentally
  identical inputs that happen to produce the same output regardless of which technique is used.
  (Stage 2's bug: two "grades" used the identical rate, so splitting by grade changed nothing
  mathematically, and the asserted wrong answer had no derivation at all.)

### D. Technical accuracy & currency
- Any code sample presenting a method/type name as if it's a real, current SDK surface should be
  checked for plausibility; where the name is clearly an invented convenience wrapper (a pattern
  this whole series uses on purpose — see `00-Authoring-Rules.md` §3.1 implementation pattern),
  that should already be disclaimed once, not per-block. If the target file lacks that disclaimer,
  add it once near the top of Part B rather than repeating it per sample.
- Any claim asserted as a permanent law that is actually an empirically observed, model/version-
  dependent finding (e.g. attention behavior over long context, a specific provider's discount or
  TTL) should carry a `verify`/hedge per the honesty-label rule — check it's not just *labelled*
  `typical`/`verify` but that the surrounding prose doesn't still read as an absolute rule two
  sentences later.
- Billing/mechanism claims for multi-call patterns (batch APIs, `n`-style sampling, streaming,
  parallel tool calls) should match what the code sample actually does, reconciled through caching
  or batching mechanics where the two differ — don't leave a narrative claim that the code doesn't
  substantiate.

### E. Security & trust-boundary review
This system's own constraints (`00-MAP.md` §1) are the checklist, not generic best practice:
**data may not leave the country** (residency), **one employee must never see another's data**
(per-tenant/per-user isolation), **actions require human approval** (no autonomous side effects),
**answers must be auditable**, **bilingual Arabic/English**. For the target stage, check:
- Every place untrusted data (user input, retrieved documents, tool output, uploaded files,
  another system's API response) enters context is delimited/labelled as data, and that any
  escaping/sanitization shown is checked for the obvious bypasses (case variation, whitespace,
  encoding) rather than an exact-string match presented as sufficient.
- Any technique that multiplies per-request cost (sampling, branching, multi-agent fan-out,
  re-ranking passes) has a cost-abuse/rate-limit consideration, not just a quality framing.
- Any caching, storage, logging, or cross-service data flow introduced by this stage is checked
  against residency and per-tenant isolation — "access-controlled" and "region/tenant-scoped" are
  different guarantees; don't let one stand in for the other.
- Any deferred-to-a-later-stage security claim (e.g. "real defence is Stage 5") is checked against
  whether that stage actually covers it — if Stage 5 doesn't, say so rather than assuming the
  forward reference resolves cleanly.

### F. Pedagogical integrity of worked examples
For every worked example with a "before" (wrong/naive) and "after" (correct/improved) pair:
confirm the wrong state has a stated, plausible mechanism (not just an asserted wrong number), and
that the two states actually differ *because of* the technique being taught, not by coincidence or
unrelated scenario changes. Confirm numbers used in a worked example are arithmetically correct
end to end (recompute them by hand).

### G. Production/ops rigor
Every CORE entry's "Trade-offs & failure modes" bullets name a specific wrong setup and its
specific symptom — flag generic ones ("can be misused," "may cause issues"). If a Perspectives
grid is present, its Decision row must end in an actionable "use X when Y" rule, not a restated
trade-off. Senior metrics/telemetry fields are named concretely (not "monitor performance").

### H. Code-sample quality & audience fit
Python primary, .NET/C#, and JavaScript/TypeScript examples belong inside the concept they
implement when the concept is app-code implementable. Check that code-bearing CORE topics do not
silently drop a relevant language without reason. For governance/process topics, accept schemas,
config, audit logs, eval rows, release gates, or approval flows when they are the more honest
implementation artifact. Check for at least one relevant failure path where the concept has a
runtime failure mode.

### I. Cross-file consistency
Skim (don't deep-read) the already-written adjacent stage files for the same running-example
facts referenced by the target file (entity name if any, leave-policy numbers, employee IDs,
residency/language requirements) and flag drift — the same noun set must mean the same thing
everywhere per `00-Authoring-Rules.md` §5's "one running example, one set of nouns" rule.

---

## Phase 2 — Present the plan, then wait

Before editing anything, give the user a numbered list of concrete changes, each naming the exact
section(s) and what will change — mirroring the Stage 2 pattern: *"Fix the self-consistency
billing contradiction (3 spots: ...); Fix the cache-hit alert threshold contradiction (...); ..."*
Explicitly call out anything you are **intentionally not changing** because it's a deliberate
design choice already documented in the file or the authoring rules (e.g. non-monotonic topic
ordering that the file itself explains, or Part C's required duplication of Part B — that
duplication is mandated by `00-Authoring-Rules.md` §4, not a bug to remove).

Wait for explicit confirmation unless the invocation already said to proceed.

---

## Phase 3 — Implement

1. **Find every copy before fixing one.** A fact fixed in Part B but left stale in Part A's
   callout, C1's trace, C1's cram reference, or a self-test question is a new inconsistency, not
   a fix. `Grep` for the specific numbers/claims across the whole file before editing, exactly as
   done for Stage 2's leave-balance example (5 locations) and self-consistency billing claim (2
   locations).
2. **Fix, don't delete, specificity.** Add `verify`/hedge language or a disclaimer; don't strip a
   concrete number down to vague prose to make a problem go away — that violates the "numbers are
   never bare" rule in reverse.
3. **Match the existing register and format.** Bullets over paragraphs for anything enumerable;
   bold the load-bearing noun phrase, not full sentences; `⚠ **Owns:**` for a box's failure mode
   inline; new content folds into existing bullet lists/production-notes blocks rather than
   arriving as a new bolted-on subsection, unless the finding genuinely warrants a new subsection
   (e.g. Stage 2's missing self-test answer key did — call this out explicitly as a deliberate
   v2.0 Part C addition when migrating a legacy stage).
4. **Preserve intentional redundancy; eliminate accidental divergence.** Part C's cram reference
   is supposed to restate Part B's facts — the fix target is making the restatement *correct and
   identical*, never collapsing it into a cross-reference to "save space."
5. **Never renumber `[8.x.y]` tags or reorder sections to "clean up" non-monotonic ordering** that
   the file's own order note explains — that's a documented, intentional authoring choice.
6. **Don't invent new running-example nouns.** Any new example needed to illustrate a fix must
   reuse the existing entity/staff/policy/language/residency scenario, per §5 of the authoring
   rules — never a fresh "imagine a retailer..." example.

---

## Phase 4 — Report

Close with a short, numbered summary of what changed (matching the style of the Stage 2 wrap-up):
one line per fix, plus an explicit "not changing" list for anything flagged in Phase 1 but left
alone by design. Do not re-paste the edited prose back into chat — the user can read the file;
summarize what and why.

---

## Authoring mode

Its own step-by-step flow, parallel to Review mode above — not a continuation of it, and not
dependent on a Review pass having run first. Use this when explicitly asked to write/draft a topic (e.g. "write `8.3.7.1` GraphRAG," "draft
the `◇` proposed topics from the map"), not as a side effect of a review pass.

**Two different weights of work live under this mode — pick the right one before starting:**
- **Whole missing topic card** (steps 1–7 below): a topic has no card anywhere — either a `+`
  topic the map says is drafted but isn't, or a `◇` topic that's a genuinely new proposal.
- **Enrichment to an existing card** (its own lighter flow, right after step 7): the map carries
  a "Proposed enrichment, not yet drafted in the file" call-out (e.g. `8.1.6`'s DPO note, `8.6.2`'s
  EchoLeak note) — a single fact or paragraph that belongs *inside* an already-written card, not a
  new card. Running the full seven-step flow on one of these is the wrong weight; use the
  lighter flow instead.

**Scope boundary — read this before touching an already-written topic.** By default, only draft
content that is genuinely missing: a topic listed in `00-MAP.md` but absent from its file, or one
of the `◇`-marked proposed topics that exists nowhere yet. Do **not** restructure an
already-written topic's shape unless a Review-mode pass specifically flagged it as a shape
mismatch (see lens A above) and the user has agreed to the fix — never silently rewrite existing
content into a "better" shape as an unprompted side effect of being asked to draft something else
nearby.

1. **Classify.** Look up the topic's tier in `00-MAP.md` (or, for a `◇` topic, its provisional
   tier from the map). Pick its shape from the "Topic-shape classification" table above. State
   the classification and shape choice as part of the plan you present — this is a judgment call,
   not a mechanical lookup, so show the reasoning (e.g. "this is a protocol topic like `8.4.10`,
   not a quantifiable mechanism, so it gets contract-first treatment, not a cost worked-example").
   **If the requested topic has no row in `00-MAP.md` at all** (neither `+` nor `◇`), stop here —
   adding a brand-new topic number is a map-ownership decision outside this skill's default scope.
   Flag it and ask whether to add the map row first, rather than inventing a topic number.
2. **Present the plan before drafting.** Name: the shape chosen and why, which Part A step (if
   any) needs a new build-narrative moment to introduce it, where in Part B it's inserted relative
   to neighbouring topics, and which Part C subsections need updating (does `C1`'s cram reference
   gain a new bullet block? does `C2`'s comparison table gain a row? does `C3` need a new
   hand-off? does `C4`'s ecosystem map gain a tool row? does `C5` gain self-test questions and
   `C6` gain answers?). Wait for confirmation.
3. **Draft**, applying, in order: the chosen shape's block sequence, the baseline non-negotiables
   checklist in full (beginner entry point, escalation to senior nuance, judgment content, and the
   right implementation evidence for the topic type), and the running example's existing nouns —
   never a new scenario.
   - For a topic classified **emerging/proposed**, open with an explicit "state of the field, as
     of [today's date]" framing and use `verify` labelling more heavily than a settled-engineering
     topic would need, exactly as `00-MAP.md`'s own `◇` topics were written with that caveat baked
     in rather than added as an afterthought.
   - For a topic classified **compliance/governance**, name what's actually required, by when, and
     who is accountable, before naming any framework by its title — a name without a concrete
     requirement attached is trivia, not a lesson.
4. **Self-check against both tables** (shape classification + baseline non-negotiables) before
   presenting the draft — this is the same check Review-mode lens A would run on this content if
   it were reviewed tomorrow, so run it now rather than let a future review catch it.
5. **Update Part A and Part C to match**, per the plan from step 2 — a topic drafted into Part B
   without a Part A step or a `C1` cram-reference bullet is exactly the "map promises what the
   file doesn't deliver" failure mode this skill exists to prevent, just moved one level down from
   map-to-file into file-internal Part-B-to-Part-C.
6. **Present the finished draft and wait for confirmation before writing it into the actual stage
   file** — drafting is not the same action as committing it, and a new topic changes `C1`'s
   completeness claim for the whole stage.
7. **If the topic was `◇`-marked, fold a `00-MAP.md` marker update into the same step-6 plan and
   confirmation — never leave it stale.** A `◇` means "not yet drafted anywhere"; the moment that
   stops being true, the marker has to change to `+` (matching how the other already-drafted
   additions are shown), or the map goes back to actively misdescribing the file it's supposed to
   index. This is still covered by the top-level "don't touch the map without being asked" rule —
   it isn't an exception to it — because step 6's confirmation *is* the ask, as long as you name
   the marker change explicitly as part of what you're asking to commit, not as a silent add-on
   after the fact.

**The lighter flow, for a "proposed enrichment" call-out instead of a whole topic:**

a. Read the existing card the enrichment targets, and place the new fact/paragraph where it fits
   the card's existing shape (fold it into an existing block — e.g. a fact belongs in "Practical
   rules" or "Trade-offs," not a new heading) rather than appending a disconnected new section.
b. Apply the same `verify`/hedge discipline the map's own call-out already carries — an enrichment
   sourced from external research needs the same currency caveat inside the file that it had in
   the map, not a confidence upgrade just because it moved into "real" content.
c. Present the proposed insertion point and wording, wait for confirmation, then write it.
d. **Remove the "Proposed enrichment" call-out from `00-MAP.md` in the same confirmed action** —
   the same staleness risk as step 7 above, just for a smaller unit of content: once the fact is
   in the file, a call-out saying it's "not yet drafted" is now wrong and has to go, named
   explicitly as part of the commit, not silently.

---

## Calibration reference: the fixes already made to Stage 2

Use these as the concrete bar for "what counts as a finding worth fixing" versus "cosmetic
nitpick not worth raising":

- Reconciled a narrative claim about a billing mechanism with the code sample that contradicted
  it (self-consistency `n`-parameter vs. an actual N-call loop), tying the resolution back to
  prompt caching rather than just picking one version to keep.
- Reconciled a fixed global alert threshold with an earlier admission that the same metric is
  expected to sit low on some routes by design — changed to "alert on drift from that route's own
  baseline."
- Rebuilt a worked example so the "before" and "after" states differ for a real, stated reason
  (two rates instead of one identical rate used twice), and propagated the corrected numbers
  through every one of its five occurrences (Part A callout wording untouched since it had none;
  C1 trace ×2, cram section ×2, one self-test question).
- Added a security caveat plus a concrete code upgrade (case-insensitive, whitespace-tolerant
  matching) for a delimiter-escaping function that only handled one exact byte sequence.
- Added a trust-boundary note distinguishing an internal, trusted tool source (safe to paste
  straight into context) from general tool output (untrusted, needs the same delimiting as any
  other document).
- Added a cost-abuse framing next to an existing multiplier-cost warning (self-consistency/ReAct/
  ToT already flagged as 3–10× cost; the missing piece was framing repeated triggering of that
  path as a denial-of-wallet vector, not only a quality/cost trade-off).
- Added one residency/compliance line to an existing privacy-and-logging table and to the
  relevant topic's security framing, rather than a new section — tied to this system's own
  residency constraint from `00-MAP.md` §1.
- Added a single disclaimer paragraph once (top of Part B) covering every illustrative
  wrapper/method name used throughout, instead of repeating a caveat per code block.
- Softened an absolute-sounding empirical claim (attention weakening in the middle of long
  contexts) to note it is benchmark-derived and model/version-dependent.
- Added a gap note about a cost category the budget table didn't account for (hidden reasoning
  tokens on reasoning models being billed as output despite being invisible).
- Added a short caveat that a text-token budget doesn't generalize to multimodal input.
- Added a full answer key for the self-test section, since none existed anywhere in the file —
  flagged explicitly as an addition beyond the base Part C contract, not a silent structural
  change.

These are illustrative of scope and tone, not a checklist to reproduce verbatim on another stage
— Stage 3 (RAG), for instance, will surface its own failure modes around chunking math, retrieval
metrics, and permission-trimmed retrieval that have no Stage 2 analogue.
