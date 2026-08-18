# Authoring Rules — how every Stage file gets written or upgraded

*Companion to `00-MAP.md`. The Map is the index and the tier list — read it to know **what**
belongs where. This file is the production spec — read it to know **how** to write or upgrade
any section so it matches the standard Stage 1 was built to, including the completeness bar
established after Stage 1's Part C was rewritten for real interview-cram use.*

Apply this file to **every** stage (`02` through `07`), not just new material. Where an existing
section falls short of a rule here — most visibly, every Part C written before this file existed
— that section is a rule violation to fix, not a different acceptable style.

---

## 0. The one rule everything else serves

**Someone should be able to revise from Part C alone, the night before an interview, and never
need to flip back into Part B.** Every rule below exists to make that true. When a rule and a
shortcut conflict, the rule wins — this file was written *because* the shortcut (citations
instead of content) was tried first and failed.

---

## 1. The four-part contract every stage file follows

```
Stage N file
│
├─ Part A  — THE BUILD           narrative spine, "why does this topic exist"
├─ Part B  — THE REFERENCE       one card per topic, full depth
└─ Part C  — ASSEMBLED           the whole stage recombined, revision-ready
```

- **Part A** exists to motivate. It never teaches a mechanism in depth — it raises a problem and
  points at the Part B entry that solves it.
- **Part B** exists to teach. Every fact, number, table and failure mode for a topic lives here,
  in full, once.
- **Part C** exists to *compress Part B back down* without losing anything — one continuous
  trace, one comparison table, one handoff, one self-test. Part C is not a summary in the sense
  of "shorter and less detailed." It is shorter in *narrative* and undiminished in *fact*.

Only Stage 1 (`01-...md`) carries the file-format front matter (how to read this file, the
master diagram, the library map, the glossary) — those live once, globally, and Stage 1 doubles
as the place readers land first. Stage 2 onward skip straight to Part A, opening instead with a
short **"Where we are"** paragraph: one sentence on what the previous stage finished, one on the
problem this stage exists to solve. Never re-explain the master diagram or glossary per file —
point back at Stage 1's `A2`/`A4` instead.

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

Two card shapes, chosen by tier (tiers come from `00-MAP.md` §4 — CORE / WORKING / AWARENESS).
**Do not blend them**: a WORKING topic does not get a Perspectives grid; a CORE topic never gets
compressed to six fields just because it feels simple to write.

### 3.1 CORE topics — the nine-block card

Every CORE entry, in this exact order, with this exact intent per block:

1. **Definition** — lead with an ASCII box diagram where the mechanism has real internal
   structure (a pipeline, a decision, a transformation). The rule from Stage 1: *"the picture is
   the definition — every arrow carries the full meaning of the term it introduces."* Follow the
   diagram with two short paragraphs: **Plain English** (one sentence, no jargon) then
   **Precisely** (the technical formulation, referencing the diagram's boxes by name). If a topic
   genuinely has no internal mechanism worth diagramming (rare for CORE), a comparison table may
   substitute — never skip straight to prose.
2. **Scenario** — a concrete situation *from the running build* that makes the topic necessary.
   Never a generic "imagine you want to..." — it must be traceable to a Part A step.
3. **Example** — real, specific values. Real sentences, real token counts, real dollar amounts,
   real error messages. An example with a placeholder like `<value>` or `some text here` is not
   done.
4. **How it works** — the mechanism, taken apart far enough that a reader could reason about a
   *new* situation, not just recognise this one. This is where nested ASCII diagrams, worked
   maths (e.g. LoRA's rank arithmetic), and step-by-step gate sequences belong.
5. **Where it fits** — redraw the master pipeline vertically, mark the current box with
   `▶ THIS BOX ◀ you are here`, and annotate the boxes immediately before/after with what this
   topic changes about them.
6. **Libraries & code** — a table (Python / .NET / JavaScript columns, Python primary) naming
   the *exact* library for each sub-job, then one code block. Code is written to be **read, not
   run**: every non-obvious line gets an inline comment explaining *why*, never restating *what*
   the syntax does. Show at least one failure path being handled (a retry, a truncation check, a
   429), not just the golden path.
7. **Knobs & real numbers** — a table of settings/parameters with ranges, defaults, and the
   situation each value is right for. Anything price-, quota- or region-shaped gets a *verify*
   flag per the honesty rule below; anything else stated as a number is either a documented
   default (say so) or a "typical" value (say so) — never bare, unlabelled.
8. **Perspectives grid** — exactly these six rows, always, in this order: **Theory · Engineering
   · Operations · Cost · Security · Decision.** One or two sentences each. "Decision" must end in
   an actionable rule ("use X when Y"), not a restatement of the trade-off.
9. **Trade-offs & failure modes** — a bullet list, each bullet naming a *specific* wrong setup
   and its *specific* symptom (not "can be misused"). This list is the raw material `C4`'s
   self-test questions get built from — write it expecting that reuse.

Every CORE entry opens with `> **In the build:** Stage N, Step M — "the quoted symptom"` linking
back to Part A, and closes at a horizontal rule before the next entry.

### 3.2 WORKING and AWARENESS topics — the six-field card

```
Definition     One line. What it is.
Example        Concrete, with real values.
Where it fits  Which layer, at which step — what enters, what leaves.
Library        The exact library and call. Python primary, .NET/JS named.
Used when      The situation that makes you reach for it.
Fails when     The failure mode. Usually the real question an interviewer asks.
```

No ASCII diagram is required, but one is welcome if the topic has real internal structure. Never
pad a WORKING card to look like a CORE card — the tier signals how much depth to expect, and
inflating it defeats that signal.

### 3.3 Two honesty labels, used throughout Part B

- **`verify`** — for anything that changes outside this document's control: prices, quotas,
  region availability, product names, contractual terms. State the *shape* of the answer, flag
  it, move on.
- **`typical`** — for numbers that are common in practice but not a documented default. Never
  present a "typical" number as if it were a spec.

---

## 4. Part C — assembled (the section this file exists to fix)

Part C has four fixed subsections, `C1`–`C4`. This is the section most likely to be written thin
on a first pass — it looks like a summary, so it's tempting to write it like one. It is not a
summary. Treat each subsection as follows.

### C1. One request, end to end — three layers, all required

1. **The compact trace.** A single real request (or the same one Stage 1 used, carried forward
   with this stage's step inserted) walked through every numbered step it touches, each line
   ending in a bracketed topic tag `[8.x.y]`. This is the fast-recall skeleton — keep it, but
   never let it stand alone.
2. **"Before the trace starts" callout** (when applicable) — any standing architecture decision
   that shapes the request but isn't re-decided every call (Stage 1's examples: RAG-not-
   fine-tuning, managed-not-self-hosted). State the decision, the one-line reason, and what
   changes if the constraint flips.
3. **Every step, unpacked, as bullets — never as paragraphs.** For each numbered step in the
   trace: a bold `**N. Step name** — `[8.x.y]`` header, then flat bullets covering, in this
   order: (a) the mechanism, (b) the concrete config/numbers this request actually used, (c) one
   or more `⚠ **Owns:**` bullets for the failure mode this box is responsible for. Nest a nested
   bullet list where a step has sub-mechanics (e.g. "on 429, in order: 1) … 2) … 3) …"). **Bullets
   are a hard requirement, not a style preference** — a paragraph cannot be skimmed the night
   before an interview; a bulleted list can. If you catch yourself writing "X, which means Y,
   and therefore Z" as prose, break it into three bullets instead.
4. **Full cram reference — one subsection per topic in this stage, covering every fact in Part
   B.** This is the block that was missing from every Part C written before this file existed,
   and it is now mandatory. For every `8.x.y` topic in the stage (CORE *and* WORKING — AWARENESS
   topics get at least a one-bullet mention), reproduce, as bullets:
   - the definition's mechanism (condensed from block 1),
   - every worked number and named table from blocks 3/7 (condensed, not paraphrased away —
     if Part B says "~15× cost gap," C1 says "~15× cost gap," not "a large cost gap"),
   - any decision tree / diagnostic table from block 4 (these compress into bullets extremely
     well — keep the "if X then Y" shape),
   - the full failure-mode list from block 9.
   The test for whether this subsection is complete: **could a reader answer every `C4`
   self-test question for this topic using only this subsection, without opening Part B?** If
   not, it's missing something concrete — go back and add the number, table, or mechanism that's
   absent, don't just add more words.
5. Close with a short **"what this trace doesn't re-run, and why"** note for any topic in the
   stage that is a standing decision rather than a per-request step (mirrors Stage 1's treatment
   of 8.1.5/8.1.6), plus forward pointers to `C2` and `C3`.

### C2. The same request, four ways

One comparison table, same four columns every stage: **Cheapest / Fastest / Most private /
Highest quality** (a stage may rename a column if a different axis matters more there, but keep
four columns and keep them constraint-shaped, not model-shaped). Every row must be something
that actually changes between columns in *this* stage's material — don't repeat Stage 1's rows
verbatim; ask what this stage's topics add to each configuration (Stage 2's version adds
few-shot count, history strategy, caching — it doesn't re-litigate model tier).

### C3. What Stage N hands to Stage N+1 (and beyond)

A table: **Problem | Goes to.** Every row must trace to something the build narrative in Part A
explicitly left broken — never invent a forward-reference that Part A didn't set up. If a
problem is fixed by a *later*, non-adjacent stage (e.g. something Stage 2 leaves broken that only
Stage 5 fixes), say so explicitly rather than only pointing at the next file.

### C4. Self-test

10–25 questions, **numbered, answer-out-loud framed**. Every question must be answerable from
`C1`'s full cram reference alone (this is the enforcement mechanism for the C1 completeness
rule — if you can't write a self-test question because the fact isn't anywhere in C1, that's a
signal C1 is incomplete, not that the question is out of scope). Prefer questions shaped like an
interviewer's follow-up ("X happened — why?", "you have to choose between A and B — which, and
what do you give up?") over definition-recall questions ("what is X?"). Close with the one
diagnostic line Stage 1 uses: *if you can only recite the definition and not the failure mode, it
is not learned yet.*

---

## 5. Style rules that apply everywhere

- **Bullets over paragraphs, always, for anything enumerable** — lists of causes, steps, knobs,
  failure modes, comparisons. Reserve full paragraphs for the Definition block's "Plain English"
  /"Precisely" pair and for Part A's narrative prose. If Part A ever turns into a bullet list, or
  Part C ever turns into a paragraph, that's backwards — fix it.
- **⚠ marks a box's owned failure mode** inline, wherever a mechanism section names one, not just
  in the dedicated Trade-offs block — this is what lets `C1`'s unpacked steps carry failure modes
  without a separate lookup.
- **Bold the load-bearing noun phrase**, not whole sentences — `**answer field is nullable**`,
  not a bolded paragraph.
- **Numbers are never bare.** Every number in this document is either (a) a concrete example
  value from the running scenario, (b) labelled `typical`, (c) labelled a documented default, or
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
- Tier (CORE / WORKING / AWARENESS) is decided once, in `00-MAP.md`'s index, and drives which
  Part B card shape a topic gets (§3 above) and how much of a bullet block it earns in `C1`'s
  cram reference. If a topic feels like it's outgrown its tier while writing it, fix the tier in
  `00-MAP.md` rather than silently over-writing a WORKING card.

---

## 7. Completion checklist — run this before calling a stage file "done"

- [ ] Part A has a step for every CORE and WORKING topic in this stage's `00-MAP.md` index, and
      no step exists that doesn't link to a real Part B entry.
- [ ] Every CORE entry has all nine blocks, in order, with a real (non-placeholder) worked
      example and a Perspectives grid with exactly six rows.
- [ ] Every number in the file is labelled `verify`, `typical`, "documented default," or is a
      concrete example value — none are bare.
- [ ] `C1` contains the compact trace **and** the per-step bullet unpacking **and** the full
      per-topic cram reference. Spot-check: pick three `C4` questions at random and confirm each
      is answerable from `C1` alone.
- [ ] `C1`'s unpacked steps and cram reference are bullets, not paragraphs. Read it back looking
      specifically for any sentence containing "which means" or "and therefore" — rewrite those
      as bullets.
- [ ] `C2` has four constraint-shaped columns with rows specific to this stage's own topics.
- [ ] `C3` traces every row to something Part A explicitly left unresolved.
- [ ] `C4` has 10+ questions, each answerable from `C1`, phrased as interviewer follow-ups where
      possible.
- [ ] The running example (government entity, staff, leave policy, Arabic, residency) is the only
      scenario used — no orphan examples introduced for convenience.

---

*This file is itself subject to the same rule as everything else in this repository: if a future
session finds a gap between what's written here and what actually made Stage 1's Part C work,
fix this file rather than quietly deviating from it in the next stage.*
