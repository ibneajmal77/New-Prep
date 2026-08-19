# Stage 7 - Classic ML & MLOps (8.7)

*Three parts: **Part A** is the build narrative. **Part B** is the complete reference — every
fact for a topic lives there, in full, once. **Part C** assembles it into a revision-ready
whole. This stage covers the half of the job that is not generative: prediction, scoring and
the MLOps lifecycle around it.*

*Order note: the topics appear here in lifecycle order, not numeric order — 8.7.10, 8.7.9 and
8.7.11 (fairness, explainability, model cards) are pulled forward next to 8.7.3 because they are
validation gates on the data and the model, and 8.7.4/8.7.5 (Azure ML, MLflow) follow because
they are where the result gets recorded. The numbers themselves never change.*

---

# Part A - THE BUILD: Stage 7

## Step 1. The business asks for prediction, not generation

HR wants to predict which service tickets will breach SLA. There is no need for a frontier
model to write prose. We need labelled historical data and a classifier.

> **→ [8.7.1 ML fundamentals](#871-ml-fundamentals)**

## Step 2. Pick the metric before building the model

Accuracy looks good because only 8% of tickets breach SLA. A model that predicts "no breach"
for everything is 92% accurate and useless. We need precision, recall, F1, ROC-AUC or
regression metrics depending on the business cost of each error.

> **→ [8.7.2 Metrics](#872-metrics)**

## Step 3. The dataset is leaking the answer

The training table includes `closed_late = true`, a field only known after the SLA breach. The
model scores beautifully offline and fails in production. This is leakage, and it is the classic
ML version of an overly helpful prompt.

> **→ [8.7.3 Data and features](#873-data-and-features)**

## Step 4. The model is accurate overall and unfair for one group

The model misses Arabic-language tickets and over-prioritizes one department. In a public-sector
system, aggregate accuracy is not enough.

> **→ [8.7.10 Fairness and bias testing](#8710-fairness-and-bias-testing-)**
> **→ [8.7.9 Explainability](#879-explainability-)**
> **→ [8.7.11 Model cards](#8711-model-cards-)**

## Step 5. Put the training pipeline somewhere real

Notebooks do not make production. We need Azure ML workspaces, compute, pipelines, model
registry, managed online endpoints for real-time scoring and batch endpoints for scheduled
jobs.

> **→ [8.7.4 Azure ML](#874-azure-ml)**
> **→ [8.7.5 MLflow](#875-mlflow)**

## Step 6. Production data changes

Departments reorganize, ticket categories change, and the model silently decays. We need data
drift, concept drift, model performance monitoring, retraining triggers, shadow deployment and
A/B tests.

> **→ [8.7.6 Deployment and monitoring](#876-deployment-and-monitoring)**

## Step 7. Tell the lifecycle as one story

The JD names the full lifecycle. You need to narrate it end to end using a real example, not as
a memorized list.

> **→ [8.7.7 End-to-end lifecycle](#877-end-to-end-lifecycle)**
> **→ [8.7.8 Telling the narrative](#878-telling-the-narrative)**

---

# Part B — THE REFERENCE

## 8.7.1 ML fundamentals `[WORKING]`
> **In the build:** Stage 7, Step 1 — *"prediction, not generation."*

**Definition** — Classic machine learning learns a **repeatable mapping** from input features to
an output target, used for prediction, scoring, ranking, clustering and anomaly detection. **It
does not generate grounded prose from a context window.**

```
   CLASSIC ML :  features available NOW  →  prediction or score  →  business action
   LLM        :  instructions + context  →  generated text or tool proposal
```

**The first question is therefore not "which model?"** It is ***"what is the business decision,
and what information is available at decision time?"***

**Core concepts**

| Concept | Meaning |
|---|---|
| Supervised learning | Train on labelled examples: features → target |
| Unsupervised learning | Find structure without labels: clusters, anomalies |
| Train / validation / test | Fit, tune, then estimate real performance |
| Overfitting | The model memorizes training data and fails on new data |
| Cross-validation | Repeated train/test splits for a more stable estimate |
| Baseline | A simple model or rule to beat — without one, "good" is undefined |

**Example**
```
Task: predict SLA breach for a service ticket.
Features available AT TICKET CREATION:
  category, channel, language, department, priority, requester type,
  text length, day/time, previous backlog, assigned team load.
Target:
  breached_sla = true/false
```
**If the target is known only after the event, downstream fields cannot be features.**

**Where it fits** — before any modelling: it is the framing step that decides whether this is a
Stage 7 problem at all, or a Stage 3/4 one.

**Library** — `scikit-learn` for the fundamentals; `pandas` for the data; the split utilities
matter more than the algorithms at this stage.

**Used when** — the output is a number, a class or a rank, and the decision is repeatable.

**Fails when**
- **A generative model is used where a classifier or regressor is cheaper and more testable.**
- The test set is touched during feature or model selection.
- **Time-based data is split randomly**, leaking future patterns into training.

---

## 8.7.2 Metrics
> **In the build:** Stage 7, Step 2 — *"pick the metric before building the model."*

### 1. Definition

```
   THE CONFUSION MATRIX IS THE ROOT. Every classification metric is a ratio from it.
                     ┌──────────────────────┬──────────────────────┐
                     │   ACTUAL BREACH      │  ACTUAL NO BREACH    │
   ┌─────────────────┼──────────────────────┼──────────────────────┤
   │ PREDICTED       │   TRUE POSITIVE      │   FALSE POSITIVE     │
   │ BREACH          │   (caught it)        │   (wasted review)    │
   ├─────────────────┼──────────────────────┼──────────────────────┤
   │ PREDICTED       │   FALSE NEGATIVE     │   TRUE NEGATIVE      │
   │ NO BREACH       │   ★ (missed breach)  │                      │
   └─────────────────┴──────────────────────┴──────────────────────┘

   PRECISION = TP / predicted positives
       "Of the tickets we flagged, how many really breach?"   → cost of FALSE POSITIVES
   RECALL    = TP / actual positives
       "Of the real breaches, how many did we catch?"         → cost of FALSE NEGATIVES

   ┌────────────────────────────────────────────────────────────────────┐
   │ THE BUSINESS DECIDES WHICH ERROR IS WORSE. THE METRIC FOLLOWS.     │
   │ SLA breach: missing a real breach is worse than a wasted review    │
   │ → optimize RECALL at an acceptable PRECISION                       │
   │ → then set the THRESHOLD from capacity: how many tickets can       │
   │   supervisors actually review per day?                             │
   └────────────────────────────────────────────────────────────────────┘

   ⚠ ACCURACY ON IMBALANCED DATA IS A TRAP. If 3% of tickets breach,
     "predict no breach always" scores 97% accuracy and is worthless.
```

**Plain English:** decide what "good" means — in business terms — before you train anything.

**Precisely:** metrics define what "good" means for the business problem. **Pick the metric
before training, or the team will optimize whatever looks best after the fact.**

### 2. Scenario

Two failure costs, and they are not symmetric. A **missed breach** means a citizen or employee
waits past the promised service window and the entity is in breach of its own SLA. A **false
flag** means a supervisor reviews a ticket that was fine — a few minutes wasted.

So recall matters more than precision here. But not infinitely: **if the model flags 400 tickets
a day and supervisors can review 60, recall on paper is irrelevant.** The threshold is a capacity
decision, not a statistical one.

### 3. Example — a segment table that changes the conclusion

Overall recall of 0.85 looks acceptable. Segmented, it is not:

| Segment | Recall |
|---|---|
| English tickets | 0.90 |
| **Arabic tickets** | **0.68** |
| Web channel | 0.88 |
| **Phone-transcribed tickets** | **0.63** |

The aggregate metric passed. **Two groups are being systematically under-served**, and no
overall number would ever have shown it (→ 8.7.10).

### 4. How it works

**Classification metrics:**

| Metric | Formula idea | Use when |
|---|---|---|
| Accuracy | correct ÷ total | Classes balanced, errors cost roughly the same |
| **Precision** | TP ÷ predicted positives | **False positives are expensive** |
| **Recall** | TP ÷ actual positives | **False negatives are expensive** |
| F1 | Harmonic mean of precision and recall | Both matter and you need one number |
| ROC-AUC | Ranking positives above negatives | Broad ranking quality across thresholds |
| **PR-AUC** | Area under precision-recall | **Rare positive class — more informative than ROC-AUC** |
| **Calibration** | A predicted 0.8 means ~80% risk | Needed whenever the score is shown as a *risk* |
| Confusion matrix | The raw counts | Explaining error types to business users |

**Regression metrics:**

| Metric | Meaning | Use |
|---|---|---|
| MAE | Average absolute error | Easiest to explain |
| RMSE | Punishes large misses | Capacity planning |
| MAPE | Percentage error | **Fails near zero** |
| R² | Variance explained | Never sufficient alone |
| Pinball loss | Quantile forecast error | Staffing for the worst case |

**Threshold tuning is a separate decision from model quality.** A model with excellent ROC-AUC
can be operationally useless if the threshold that achieves acceptable precision flags more
tickets than the team can process. Choose the model on ranking quality; choose the threshold on
capacity and error cost.

⚠ **Calibration matters the moment a score is presented as a risk.** If the output is displayed
or acted on as "80% likely to breach", an uncalibrated 0.8 is a misleading statement, not just a
suboptimal one.

### 5. Where it fits

```
   business objective
        │
▶  PICK THE METRIC  ◀ ─── you are here, BEFORE any modelling
        │                  (choose it after training and you will rationalise)
        ▼
   baseline → features → model → evaluate ON THIS METRIC → threshold from capacity
        │
        └──► the same metric governs monitoring (8.7.6) and fairness segments (8.7.10)
```

### 6. Libraries & code

| Job | Library |
|---|---|
| Metrics | `sklearn.metrics` — `precision_recall_fscore_support`, `roc_auc_score`, `average_precision_score` |
| Calibration | `sklearn.calibration` `CalibratedClassifierCV`, calibration curves |
| Confusion matrix | `sklearn.metrics.confusion_matrix`, plotted for business review |
| Threshold selection | Precision-recall curve plus an operational capacity constraint |
| Segmented metrics | Your own — group by language, channel, department, then recompute |

### 7. Knobs & real numbers

| Knob | Typical | Notes |
|---|---|---|
| Target metric | recall at acceptable precision (this build) | Set by which error costs more |
| Example gate | recall ≥ 0.85, precision ≥ 0.55 | The registration gate in 8.7.4 |
| Threshold | from **review capacity**, not from the F1 peak | An operational constraint |
| PR-AUC vs ROC-AUC | PR-AUC when positives are rare | ROC-AUC flatters imbalanced problems |
| Calibration check | required if the score is shown as risk | Reliability curve by group |
| Segments | language, channel, department, requester type | Minimum four |

### 8. Perspectives grid

| Lens | What matters here |
|---|---|
| **Theory** | Every classification metric is a ratio drawn from the confusion matrix; choosing a metric is choosing which cell of that matrix you are willing to pay for. |
| **Engineering** | Pick the metric before training. Compute it segmented from day one. Keep threshold selection as a separate, documented, business-owned decision. |
| **Operations** | The threshold is a capacity decision that changes as staffing changes — review it when the team size changes, not only when the model changes. |
| **Cost** | False positives consume human review time; false negatives consume service-level credibility. Both are real costs, and the ratio between them *is* the metric choice. |
| **Security** | Segmented metrics are how disparity becomes visible. An aggregate number can conceal systematic under-service of a protected or language group (8.7.10). |
| **Decision** | Name the more expensive error, choose the metric that measures it, then set the threshold from operational capacity. Never optimise accuracy on imbalanced data. |

### 9. Trade-offs & failure modes

- **Accuracy used on imbalanced data.** "Always predict no breach" wins.
- **ROC-AUC high but the chosen threshold operationally useless.**
- **Metrics not segmented** by language, department, geography or user group.
- **The metric chosen after training**, which guarantees post-hoc rationalisation.
- **Uncalibrated scores presented as risk percentages.**
- **MAPE used on values near zero.**
- **Threshold set at the F1 peak** rather than from review capacity.

---

## 8.7.3 Data and features
> **In the build:** Stage 7, Step 3 — *"the dataset is leaking the answer."*

### 1. Definition

```
   LEAKAGE = a feature contains information not available at PREDICTION TIME.
   The model looks brilliant offline and collapses in production, because in
   production that column is empty, or does not exist yet.

   THE FEATURE-AVAILABILITY TABLE — build this before building the model
   ┌────────────────────────┬──────────────────┬─────────────────────────────┐
   │ FEATURE                │ AVAILABLE WHEN?  │ VALID AT CREATION TIME?     │
   ├────────────────────────┼──────────────────┼─────────────────────────────┤
   │ category               │ ticket creation  │ yes                         │
   │ priority               │ ticket creation  │ yes, if set before scoring  │
   │ assigned team backlog  │ scoring time     │ yes                         │
   │ escalation flag        │ maybe later      │ only for a refresh-time model│
   │ resolution notes       │ AFTER closure    │ ✗ NO                        │
   │ final resolution time  │ AFTER closure    │ ✗ NO                        │
   │ closed_late            │ AFTER closure    │ ✗ NO — this IS the target   │
   └────────────────────────┴──────────────────┴─────────────────────────────┘

   THE SIX-QUESTION LEAKAGE CHECKLIST
     1. Was the field created AFTER prediction time?
     2. Was it edited by a human who already knew the outcome?
     3. Is it a PROXY for the target?
     4. Was preprocessing fit on ALL data before the split?
     5. Are duplicates or near-duplicates crossing splits?
     6. Does the target definition use FUTURE policy not known at the time?

   ⚠ QUESTION 4 IS THE SUBTLE ONE: fitting a scaler or encoder on the full
     dataset before splitting leaks test-set statistics into training.
```

**Plain English:** turn raw data into inputs the model can use, without accidentally handing it
the answer.

**Precisely:** feature engineering turns raw data into model inputs. **Leakage** occurs when a
feature contains information that would not be available at prediction time. **Class imbalance**
occurs when one class is much rarer than the other — and both are properties of the *data*, not
of the algorithm, which is why no model choice fixes them.

### 2. Scenario

The first model scores 0.94 PR-AUC. Everyone is pleased for about a day, until someone asks
which features matter most and the answer is `resolution_time_hours`.

That field is populated **when the ticket closes**. At prediction time — ticket creation — it is
null for every real ticket. The model learned to read the future from a column that will never
be there. **The offline number was real and the model is worthless.**

### 3. Example

**Feature engineering by source:**

| Data | Feature examples |
|---|---|
| Ticket text | Length, language, embedding, keyword flags |
| Ticket metadata | Category, channel, priority, department |
| Time | Hour, day of week, holiday flag |
| Operations | Team backlog, open ticket count, historical SLA rate |

**Leakage examples, and why each is invalid:**

| Leaky feature | Why invalid |
|---|---|
| `resolution_time_hours` | Known only after closure |
| `closed_late` | **This is the target itself** |
| `escalated_by_manager` | May happen after breach risk appears |
| Future backlog | Not known at prediction time |

### 4. How it works

**Class imbalance controls, in the order to try them:**

| Control | Use |
|---|---|
| **Stratified or time-aware split** | First — before anything else |
| **Class weights** | Penalize rare-class mistakes more |
| **PR-AUC, recall, precision at threshold** | Metrics that do not hide rare-class failure |
| **Threshold tuning** | Change the decision threshold after training |
| Calibrated probabilities | If the score is presented as risk |
| Resampling | **Only inside training folds** — never before the split |

⚠ **Resampling before the split is a leakage bug wearing an imbalance costume.** Oversampling the
minority class first, then splitting, puts duplicates of the same record on both sides — the test
set contains rows the model trained on.

**Time-based splitting is mandatory for time-ordered data.** A random split lets the model learn
from December to predict November, which is a capability it will not have in production.

**Preprocessing must be fit inside the pipeline, on the training fold only** — `sklearn`'s
`Pipeline` exists precisely to make this hard to get wrong.

### 5. Where it fits

```
   raw data
      │
▶  DATA AND FEATURES  ◀ ─── the real work: typically most of the project
      │
      ├── feature availability table  → decides what may be used at all
      ├── leakage checklist           → run BEFORE training, and again on any new feature
      ├── split (time-aware)          → then, and only then
      └── preprocessing inside the pipeline, fit on the training fold
      │
   model training (8.7.1) → evaluation (8.7.2) → fairness segments (8.7.10)
```

### 6. Libraries & code

| Job | Library |
|---|---|
| Pipelines that prevent leakage | `sklearn.pipeline.Pipeline`, `ColumnTransformer` |
| Time-aware splitting | `sklearn.model_selection.TimeSeriesSplit` |
| Class weights | `class_weight="balanced"` on most estimators |
| Resampling inside folds | `imbalanced-learn` `Pipeline` (not plain resampling) |
| Data validation | Great Expectations, `pandera` — schema, nulls, ranges, categories |
| Feature availability | Documentation — there is no library for this, and it is the important one |

### 7. Knobs & real numbers

| Knob | Typical | Notes |
|---|---|---|
| Split strategy | **time-based** for time-ordered data | Random splits leak the future |
| Test set | touched **once**, at the end | Any reuse invalidates the estimate |
| Class weights | `balanced` as a starting point | Cheaper and safer than resampling |
| Resampling | inside training folds only | Otherwise duplicates cross the split |
| Rare-class metric | PR-AUC and recall at threshold | Not accuracy, not ROC-AUC |
| Data quality checks | nulls, schema, category drift, ranges | Run on every training run *and* in production |

### 8. Perspectives grid

| Lens | What matters here |
|---|---|
| **Theory** | A model can only learn from information present in the training data. Leakage adds information that will be absent at inference, so the learned mapping does not exist in production. |
| **Engineering** | Build the feature-availability table first. Put preprocessing inside a pipeline. Split by time. Resample only within folds. Validate schema and ranges automatically. |
| **Operations** | Data quality checks must run in production too — a renamed category field silently degrades a model that reports no error at all. |
| **Cost** | This is where most project time goes, and under-investing here is the most expensive mistake available, because every downstream metric inherits the damage. |
| **Security** | Features derived from personal data inherit its classification and residency constraints (8.6.7). A training set is a derived copy of the source data. |
| **Decision** | Before any feature enters the model, answer one question: *would this value exist, with this value, at the moment we score?* If not — or if unsure — leave it out. |

### 9. Trade-offs & failure modes

- **Feature availability time not documented.** The root cause of most leakage.
- **Text fields including agent notes written after the outcome.**
- **Resampling applied before the train/test split**, leaking duplicate records.
- **Data quality checks skipped** for nulls, schema changes and category drift.
- **Preprocessing fit on all data before splitting**, leaking test statistics.
- **Random splits on time-ordered data.**
- **A proxy for the target** used as a feature — subtler than the obvious leaks and just as fatal.

---

## 8.7.10 Fairness and bias testing `+`
> **In the build:** Stage 7, Step 4 — *"accurate overall and unfair for one group."*

### 1. Definition

```
   OVERALL RECALL 0.85  ← passes the gate
   ┌───────────────────────────┬────────┐
   │ English tickets           │  0.90  │
   │ ARABIC tickets            │  0.68  │ ★ systematically under-served
   │ Web channel               │  0.88  │
   │ PHONE-TRANSCRIBED tickets │  0.63  │ ★ systematically under-served
   └───────────────────────────┴────────┘
   The aggregate concealed both. No overall number would ever have shown it.

   THE FIVE CHECKS — each asks a different question
   ┌──────────────────────┬─────────────────────────────────────────────────┐
   │ Performance parity   │ Does recall/precision differ by group?           │
   │ Error disparity      │ Are FALSE NEGATIVES higher for Arabic tickets?   │
   │ Outcome disparity    │ Does one department get more high-risk flags?    │
   │ Calibration by group │ Does a 0.8 score mean the same risk in each?     │
   │ PROXY FEATURES       │ Is department or language standing in for a      │
   │                      │ protected attribute?                             │
   └──────────────────────┴─────────────────────────────────────────────────┘

   ⚠ THE PARADOX: you cannot measure disparity across a protected attribute
     without holding that attribute for evaluation. Discarding it entirely
     does not create fairness — it makes unfairness UNMEASURABLE.
```

**Plain English:** check whether the model works as well for every group it affects — and if it
does not, that is a finding, not a rounding error.

**Precisely:** fairness testing checks whether model **performance** or **outcomes** differ
materially across groups or protected attributes. **In public-sector systems this is not
optional** if the model affects access, priority, eligibility or service quality.

### 2. Scenario

The SLA-breach model passes its gate at 0.85 recall and goes to validation. A reviewer asks for
the numbers by language.

Arabic recall is **0.68**. Phone-transcribed tickets are **0.63**. Both make sense in hindsight —
the Arabic text features are weaker (8.3.1.4) and transcription introduces noise — and both mean
the same thing operationally: **Arabic-speaking staff are systematically less likely to have
their at-risk ticket caught before it breaches.** In a government entity that is a service-equity
problem with a complaint attached, not a modelling curiosity.

### 3. Example — the fairness metrics, stated precisely

| Metric | Meaning |
|---|---|
| **Demographic parity** | Similar positive prediction *rates* across groups |
| **Equal opportunity** | Similar **true positive rates (recall)** across groups |
| **Equalized odds** | Similar true *and* false positive rates |
| **Calibration by group** | The same score means the same risk in each group |
| **Disparate impact ratio** | Comparison of outcome rates between groups |

These are not interchangeable, and **they can conflict** — satisfying demographic parity and
calibration simultaneously is generally impossible when base rates differ. Choosing which one
applies is a policy decision made with legal and governance input, not an engineering
preference.

### 4. How it works

**The mitigations, in order of preference:**

- **Improve data coverage for the underperforming group** — usually the right first move, and the
  only one that makes the model genuinely better rather than differently calibrated.
- **Remove or transform proxy features** where appropriate.
- **Add human review** for high-impact automated decisions affecting the affected group.
- **Segment thresholds — only with legal and governance review.** Different thresholds by group
  can be lawful and appropriate, or unlawful discrimination, depending on jurisdiction and
  context. This is never an engineer's unilateral call.
- **Monitor fairness metrics after deployment**, because disparity can appear as the population
  drifts even when it was absent at launch (8.7.6).

⚠ **Proxy features are the hard part.** `department`, `channel` and `language` are legitimate
operational features that can also stand in for nationality, seniority or disability. Feature
importance alone will not tell you which — that requires domain knowledge and a deliberate look.

### 5. Where it fits

```
   evaluation (8.7.2) computed OVERALL
        │
▶  FAIRNESS AND BIAS TESTING  ◀ ─── recompute EVERY metric, per segment
        │
        ├── before release      → a validation gate, with SME and legal review
        ├── in the model card   → recorded, with limitations (8.7.11)
        └── AFTER deployment    → monitored, because disparity drifts (8.7.6)
        │
   feeds explainability (8.7.9): a person affected may ask why
```

### 6. Libraries & code

| Job | Library |
|---|---|
| Fairness metrics | **Fairlearn**, Azure ML responsible-AI dashboard, `aif360` |
| Segment evaluation | Your own — group by attribute and recompute the primary metric |
| Calibration by group | `sklearn.calibration` reliability curves, computed per segment |
| Proxy investigation | SHAP (8.7.9) plus domain review — no library decides this |
| Monitoring | Segment metrics on the production monitoring loop (8.7.6) |

### 7. Knobs & real numbers

| Knob | Typical | Notes |
|---|---|---|
| Segments evaluated | language, channel, department, requester type, minimum | Add any group the decision affects |
| Disparity threshold | agreed with governance, e.g. ratio ≥ 0.8 | A policy number, not a statistical one |
| Re-check cadence | every retrain, plus scheduled monitoring | Fairness drifts with the population |
| Minimum segment size | large enough for a stable estimate | Tiny segments produce noisy disparity |
| Threshold segmentation | **only with legal and governance sign-off** | Never a unilateral engineering choice |

### 8. Perspectives grid

| Lens | What matters here |
|---|---|
| **Theory** | Fairness definitions are mutually incompatible in general — parity, equal opportunity and calibration cannot all hold when base rates differ. Choosing one is a policy act. |
| **Engineering** | Recompute every primary metric per segment. Keep protected attributes available for evaluation even when they are excluded from features. Watch for proxies. |
| **Operations** | Monitor fairness after deployment. Disparity that did not exist at launch appears as the population and processes drift. |
| **Cost** | Improving coverage for an under-served group costs data work, which is the honest fix. Threshold tweaking is cheaper and frequently the wrong answer. |
| **Security** | Protected attributes held for evaluation are sensitive data with their own access, retention and residency rules (8.6.7). Hold them deliberately, not casually. |
| **Decision** | If the model affects access, priority, eligibility or service quality, segment every metric and record the result in the model card. Escalate any material disparity to governance rather than fixing it quietly. |

### 9. Trade-offs & failure modes

- **Protected attributes ignored entirely, making disparity unmeasurable.** Discarding the
  attribute does not create fairness.
- **Fairness checked once before launch and never again.**
- **The model "fair" overall but failing Arabic users or low-volume groups.**
- **Threshold segmentation applied without legal review.**
- **Proxy features unexamined**, so department or language silently encodes a protected
  attribute.
- **Disparity found and quietly tuned away** rather than escalated and recorded.

---

## 8.7.9 Explainability `+`
> **In the build:** Stage 7, Step 4 — *"why was I refused?"*

### 1. Definition

```
   DIFFERENT AUDIENCES NEED DIFFERENT EXPLANATIONS OF THE SAME PREDICTION
   ┌──────────────────┬───────────────────────────────────────────────────┐
   │ Data scientist   │ debug features and model behaviour                 │
   │ Operator         │ know why THIS ticket was flagged                   │
   │ AFFECTED USER    │ an understandable reason AND an appeal path        │
   │ Auditor          │ evidence of control and consistency                │
   └──────────────────┴───────────────────────────────────────────────────┘

   GLOBAL  : what generally drives the model?      → feature importance, PDP
   LOCAL   : why did THIS ticket get THIS score?   → SHAP, LIME

   ⚠ FOR A DECISION ABOUT A PERSON, NEVER SAY "THE AI DECIDED."
     Provide, in this order:
        1. the POLICY or business rule basis
        2. the relevant INPUT FACTS
        3. the model score, where appropriate
        4. the main CONTRIBUTING FACTORS
        5. the APPEAL or human-review path
     Note that the model score is third, not first — and the appeal path is
     not optional in a public entity.
```

**Plain English:** be able to say, in terms a person can act on, why the system produced this
result — and tell them how to challenge it.

**Precisely:** explainability provides understandable reasons for a model's output.
**Global** explanations describe what drives the model generally; **local** explanations describe
why one particular prediction happened.

### 2. Scenario

A supervisor asks why a ticket was flagged high-risk, and an employee whose request was
deprioritised asks the harder version of the same question: *"why me?"*

Feature importance says `assigned_team_backlog` and `channel` are the top drivers. That is a true
statement about the model and **a useless answer to the employee** — it explains the mechanism
without giving them anything they can act on or contest. The gap between those two things is what
this topic is about.

### 3. Example — the tools and what each actually does

| Tool | How it explains |
|---|---|
| **SHAP** | Attributes a prediction to features using game-theoretic contribution values |
| **LIME** | Fits a simple local surrogate model around one prediction |
| Feature importance | Global ranking of influential features |
| Partial dependence | How the prediction changes as one feature varies |

**SHAP vs LIME in one line each:** SHAP attributes the *actual* prediction to features with
consistency guarantees and costs more compute; LIME approximates the model *locally* with a
simpler one and is faster but less stable across runs.

### 4. How it works

**The public-sector answer format** is the examinable content here. For a decision affecting a
person, provide: the **policy or business rule basis** · the **relevant input facts** · the model
score where appropriate · the **main contributing factors** · the **appeal or human review
path**.

The ordering matters. Leading with the model score frames the decision as machine-made; leading
with the policy basis frames it correctly, as a human decision informed by a score.

⚠ **Chain-of-thought from an LLM is not an audit explanation.** It is a plausible narrative, not
a guaranteed causal account of why the output occurred (8.2.2). For decisions about people, an
explanation must be derived from the actual model, not generated as prose.

⚠ **Feature importance without proxy analysis can mislead.** "The main factor was `channel`"
sounds neutral until `channel` turns out to correlate with a protected characteristic (8.7.10).

### 5. Where it fits

```
   model prediction
        │
▶  EXPLAINABILITY  ◀
        │
        ├── to the DATA SCIENTIST  → SHAP global, debugging
        ├── to the OPERATOR        → local factors, in the queue UI
        ├── to the AFFECTED USER   → policy basis + facts + factors + APPEAL PATH
        └── to the AUDITOR         → evidence that the control existed and was applied
        │
   recorded in the model card (8.7.11); required by governance (8.6.9)
```

### 6. Libraries & code

| Job | Library |
|---|---|
| Local and global attribution | `shap` |
| Local surrogates | `lime` |
| Partial dependence, permutation importance | `sklearn.inspection` |
| Managed dashboard | Azure ML responsible-AI dashboard |
| User-facing explanation | Your own template — the model output is one input to it, not the whole thing |

### 7. Knobs & real numbers

| Knob | Typical | Notes |
|---|---|---|
| Explanation type by audience | global for debugging, local for decisions | Different questions |
| SHAP compute cost | material on large models and datasets | Sample, or use tree-optimised variants |
| Factors shown to a user | 3–5 | More is not clearer |
| Appeal path | **always, for decisions about people** | Not a feature — an obligation |
| Proxy review | on every explanation set | A factor can be neutral-sounding and not neutral |

### 8. Perspectives grid

| Lens | What matters here |
|---|---|
| **Theory** | An explanation is a model of a model. SHAP gives consistent attributions of the actual prediction; LIME approximates locally. Both explain the model, not the world. |
| **Engineering** | Compute local explanations at scoring time where decisions affect people, and store them with the prediction — reconstructing them later is expensive and sometimes impossible. |
| **Operations** | Operators need the local factors in the queue UI, or they cannot act on a flag they do not understand — and unexplained flags get ignored. |
| **Cost** | SHAP on large models is not free. Sample for monitoring; compute in full for high-impact individual decisions. |
| **Security** | An explanation can leak feature values and thresholds. Show the affected user what they need, not the model's internals. |
| **Decision** | For any decision about a person: policy basis, input facts, contributing factors, appeal path. Never "the AI decided", and never an LLM's narrative as the audit record. |

### 9. Trade-offs & failure modes

- **Chain-of-thought from an LLM treated as an audit explanation.**
- **Feature importance shown without checking whether features are proxies.**
- **Explanations technically correct but useless to the affected user.**
- **No appeal path offered**, which makes the explanation decorative.
- **Explanations computed only offline**, so the operator sees a score with no reason.
- **Leading with the model score**, framing a human decision as a machine one.

---

## 8.7.11 Model cards `+` `[WORKING]`
> **In the build:** Stage 7, Step 4 — *"document the model like a governed asset."*

**Definition** — A model card is **structured documentation for a model**: intended use, data,
metrics, limitations, risks, fairness results, deployment constraints and monitoring plan. It is
the artifact that makes a model reviewable by someone who did not build it — and the Stage 7
counterpart of Stage 5's AI register entry (8.6.9).

**Example — the contents:**

| Section | Example |
|---|---|
| **Intended use** | Predict SLA breach risk for internal service tickets |
| **Out-of-scope use** | **Employee performance evaluation** |
| Training data | Tickets from 2024–2026, excluding post-resolution notes |
| Metrics | Recall, precision, PR-AUC, calibration |
| **Segments** | **Arabic/English, departments, channels** — with the numbers |
| Limitations | Low confidence on rare categories |
| Human oversight | Supervisor reviews every high-risk flag |
| Monitoring | Drift, performance, fairness, data quality |
| Owner | Service operations analytics team |

The **out-of-scope** row is the one that does the most work: it is what stops a model approved
for ticket triage being quietly repurposed for something about people's careers — the same
purpose-limitation control as 8.6.9, at the model level.

**Where it fits** — produced at validation, attached to the registered model version, and updated
on **every retrain or replacement**.

**Library** — no library required; the discipline is keeping it in version control beside the
model and linking it from the registry entry (8.7.5).

**Used when** — any model that affects a person, and any model a governance process must approve.

**Fails when** — documentation is **written once for approval and not updated after retraining or
model replacement**, so the card describes a model that is no longer running.

---

## 8.7.4 Azure ML `[WORKING]`
> **In the build:** Stage 7, Step 5 — *"put the training pipeline somewhere real."*

**Definition** — Azure Machine Learning provides managed infrastructure for ML development and
operations: workspaces, compute, data assets, pipelines, model registry and managed online and
batch endpoints. Its value is **not the compute** — it is that data, code, environment and model
version become **linked, versioned artifacts** instead of a notebook someone ran once.

**Components**

| Component | Use |
|---|---|
| Workspace | Boundary for assets, jobs, models, endpoints |
| Compute | CPU/GPU clusters or instances for training |
| Data asset | **Versioned** dataset reference |
| Pipeline | Reproducible multi-step training/evaluation workflow |
| Model registry | Versioned model artifact with metadata |
| **Managed online endpoint** | Real-time HTTPS scoring — score one ticket now |
| **Batch endpoint** | Scheduled/offline scoring at scale — score all open tickets hourly |

**Online vs batch is a product decision, not an infrastructure one:** real-time scoring when the
decision happens at ticket creation; batch when the decision is a periodic sweep of everything
open. Many systems need both — and if they do, **both must share the same preprocessing code**,
or the two paths silently disagree.

**Example — registration gated on validation:**
```python
# The model is registered ONLY if it clears the business metric gate (8.7.2).
# Registration is a promotion decision, not a save operation.
if metrics["recall"] >= 0.85 and metrics["precision"] >= 0.55:
    ml_client.models.create_or_update(Model(
        name="sla-breach-classifier",
        version=build_version,
        path="./model",
        tags={"recall": metrics["recall"], "data_version": data_version},
    ))
```

**Where it fits** — the build, test and deploy stages of the lifecycle (8.7.7); it is where
8.7.5's tracked experiments become a governed, deployable asset.

**Library** — `azure-ai-ml` (v2 SDK); MLflow integrates natively for tracking (8.7.5).

**Used when** — any model that must be reproducible, reviewable and deployable by someone other
than its author.

**Fails when**
- **Notebook output is manually copied into production.**
- Data, environment and code versions are **not tied to the registered model**, so the running
  model cannot be reproduced.
- **Real-time and batch scoring paths use different preprocessing** — the classic source of
  "it scores differently in production" with no error anywhere.

---

## 8.7.5 MLflow `[WORKING]`
> **In the build:** Stage 7, Step 5 — *"track experiments and versions."*

**Definition** — MLflow tracks experiments, parameters, metrics, artifacts and model versions.
It is **the common language between data-science experiments and production model management** —
the thing that lets you answer "which run produced the model currently serving traffic?"

**What to log — and the last three are the ones that get omitted:**

| Item | Example |
|---|---|
| Parameters | Algorithm, `max_depth`, `class_weight` |
| Metrics | Precision, recall, F1, PR-AUC |
| Artifacts | Plots, confusion matrix, model file |
| **Data version** | Dataset hash or data asset version |
| **Code version** | Git commit |
| **Environment** | Package versions, image |
| **Model signature** | Expected inputs and outputs |

**A good run record** carries: `run_id` · `git_commit` · `data_version` (e.g.
`tickets-2026q2-v3`) · params · metrics · artifacts (confusion matrix, calibration plot) ·
model signature · environment. **Reproducibility that omits the data version is not
reproducibility** — the same code on different data is a different model.

**Example**
```python
with mlflow.start_run():
    mlflow.log_params(params)
    model.fit(X_train, y_train)
    scores = evaluate(model, X_val, y_val)
    mlflow.log_metrics(scores)
    mlflow.sklearn.log_model(
        model,
        artifact_path="model",
        registered_model_name="sla-breach-classifier",
    )
```

**Promotion** is the step after logging: a run becomes a *registered version*, and a version is
promoted through stages or aliases (e.g. `staging` → `production`). **Logging without promotion
leaves you with a pile of experiments and no answer to "which one is live?"**

**Where it fits** — wraps every training run; its registry entry is what 8.7.4 deploys and what
8.7.6 monitors.

**Library** — `mlflow`, natively integrated with Azure ML.

**Fails when** — runs are logged but **no model version is promoted** through stages or aliases ·
**the production endpoint cannot be traced back to a run** · reproducibility omits the data
version.

---

## 8.7.6 Deployment and monitoring
> **In the build:** Stage 7, Step 6 — *"production data changes."*

### 1. Definition

```
   A DEPLOYED MODEL IS A DEPRECIATING ASSET. The world moves; the weights do not.

   SIX KINDS OF DRIFT, AND HOW EACH IS DETECTED
   ┌──────────────────┬────────────────────────────┬──────────────────────────┐
   │ Schema drift     │ column renamed or missing  │ schema validation        │
   │ Data drift       │ category distribution moves│ distribution distance,PSI│
   │ Prediction drift │ risk scores shift          │ output distribution      │
   │ CONCEPT drift    │ features no longer predict │ ★ DELAYED GROUND-TRUTH   │
   │                  │ the target                 │   PERFORMANCE            │
   │ Label drift      │ target DEFINITION changes  │ policy/process review    │
   │ Fairness drift   │ one segment worsens        │ segment metrics (8.7.10) │
   └──────────────────┴────────────────────────────┴──────────────────────────┘

   THE MONITORING LOOP — and note where the delay is
   log prediction → ⏳ WAIT FOR OUTCOME → join label → compute performance
                 → compare to baseline → alert → investigate → retrain or roll back
                       ▲
                       └─ this wait is why data and prediction drift matter:
                          they are the EARLY signals available before the
                          ground truth arrives.

   ⚠ RETRAINING CAN BE AUTOMATED. PROMOTION MUST NOT BE.
```

**Plain English:** serve the model, then keep checking that the world it was trained on still
exists.

**Precisely:** ML deployment is serving a trained model for online or batch inference.
Monitoring checks that the model continues to **receive valid data** and **produce useful
predictions** after launch — two separate questions with two separate detection methods.

### 2. Scenario

The model launched at 0.87 recall. Six months later nobody has changed anything and recall is
0.71.

Three unrelated things happened: the service desk **added two ticket categories** the model has
never seen (data drift) · a **field was renamed** in an upstream system and now arrives null
(schema drift) · and the **SLA policy changed**, so the definition of a breach is no longer what
the labels encoded (label drift, which no distribution test detects). **None of them raised an
error.** The model kept scoring, confidently, on inputs that no longer meant what it learned.

### 3. Example — deployment patterns

| Pattern | Use |
|---|---|
| **Blue/green** | Swap traffic between deployments |
| **Canary** | A small percentage to the new model |
| **Shadow** | Score with the new model but **do not act on it** |
| **A/B test** | Compare business outcomes, not just metrics |
| **Batch scoring** | Periodic large-scale predictions |

These are the same patterns as 8.5.7, applied to a model artifact instead of a prompt bundle —
and for the same reason: **you cannot know how a change behaves until it meets real data.**

### 4. How it works

**The retraining triggers:**

- Performance below threshold **when ground truth arrives**
- Significant data or prediction drift
- **Policy or process change** (which is the trigger nobody automates, because it arrives as an
  email rather than a metric)
- New labelled data volume
- **Fairness metric regression** (8.7.10)
- Model or dependency deprecation

**Retraining is not automatic shipping.** Retraining can and should be automated; **promotion
must still pass gates**:

- Data checks passed
- Metrics passed
- **Fairness did not regress**
- Explainability reviewed if high impact
- **Model card updated** (8.7.11)
- Canary or shadow deployment completed

⚠ **The ground-truth delay is the defining operational property.** For SLA breach you learn the
truth when the ticket closes — hours or days later. That lag is why data and prediction drift
matter: they are the **only** signals available before the labels arrive, and they are leading
indicators rather than proof.

⚠ **Drift alerts without an owner and a runbook are noise.** A fired alert that nobody is
accountable for trains the team to ignore the channel.

### 5. Where it fits

```
   registered model (8.7.4/8.7.5)
        │
▶  DEPLOYMENT AND MONITORING  ◀
        │
        ├── shadow → canary → blue/green         ← same discipline as 8.5.7
        ├── online endpoint (real-time) AND/OR batch endpoint
        │     └─ both MUST share preprocessing code
        │
        └── MONITOR: schema · data · prediction · concept · label · fairness
              │
              └──► retraining trigger → retrain (auto) → PROMOTION GATES (manual)
                    → model card update → canary → back to serving
```

### 6. Libraries & code

| Job | How |
|---|---|
| Endpoints | Azure ML managed online and batch endpoints |
| Schema validation | `pandera`, Great Expectations — run in the scoring path, not only in training |
| Drift detection | Azure ML data drift monitors; PSI or distribution distance computed yourself |
| Delayed-label joins | A scheduled job joining predictions to outcomes when they arrive |
| Segment monitoring | Fairlearn metrics recomputed on production slices (8.7.10) |
| Alerting | Azure Monitor, with a named owner and a runbook per alert |

### 7. Knobs & real numbers

| Knob | Typical | Notes |
|---|---|---|
| Ground-truth lag | hours to days (this build) | Determines how fast performance drift is detectable |
| Drift check cadence | daily on inputs, weekly on performance | Inputs are the early signal |
| PSI alert threshold | ~0.1 moderate, ~0.25 significant (`typical`) | Calibrate to your own data |
| Canary share | 5–10% | Same as 8.5.7 |
| Retraining | automated | **Promotion is not** |
| Performance floor | the registration gate (recall ≥ 0.85) | Falling below it is a retraining trigger |
| Alert ownership | one named owner per alert | Plus a runbook, or it is noise |

### 8. Perspectives grid

| Lens | What matters here |
|---|---|
| **Theory** | A model encodes a relationship observed in a past distribution. Drift is not a defect — it is the world changing out from under a fixed function. |
| **Engineering** | Validate schema in the scoring path. Share preprocessing between online and batch. Join predictions to delayed labels automatically rather than by hand. |
| **Operations** | Input drift is the leading indicator; performance is the lagging truth. Every alert needs an owner and a runbook, and every retrain needs promotion gates. |
| **Cost** | Batch scoring is far cheaper than real-time for periodic decisions. Retraining costs compute and review time — trigger it on signals, not on a calendar alone. |
| **Security** | Prediction logs and joined labels are personal data derived from the source (8.6.7). They inherit its retention and access rules. |
| **Decision** | Automate retraining; never automate promotion. Monitor inputs daily and performance as ground truth arrives, and treat a policy change as a retraining trigger even when no metric has moved. |

### 9. Trade-offs & failure modes

- **Ground truth arriving late and nobody closing the loop.**
- **Drift alerts existing but no owner or runbook responds.**
- **Retraining happening automatically without validation and approval.**
- **Shadow deployment skipped for high-impact models.**
- **Label drift undetected** because distribution tests cannot see a changed *definition*.
- **Online and batch preprocessing diverging.**
- **Schema validation only in training**, so a renamed field silently produces nulls in
  production.

---

## 8.7.7 End-to-end lifecycle
> **In the build:** Stage 7, Step 7 — *"walk the JD lifecycle."*

### 1. Definition

```
   THE LIFECYCLE IS AN OPERATING SYSTEM, NOT A VOCABULARY LIST.
   Every stage has an owner, an artifact and a gate.

   ASSESSMENT   business objective · AI suitability · risk · owner · success metric
        │       ⚠ "should we use ML at all?" is a real outcome here
        ▼
   DATA PREP    source access · quality · labels · privacy · FEATURE AVAILABILITY
        │       (8.7.3 — most of the project's real time)
        ▼
   BUILD        baseline first · feature engineering · training · experiment tracking
        │       (8.7.5 — a model that cannot beat a rule is not ready)
        ▼
   TEST         offline metrics · SEGMENT metrics · leakage checks
        │       (8.7.2, 8.7.10)
        ▼
   VALIDATE     SME review · fairness · explainability · security · APPROVAL
        │       (8.7.9, 8.7.11, 8.6.9)
        ▼
   DEPLOY       registry · endpoint · canary/shadow · rollback
        │       (8.7.4, 8.7.6)
        ▼
   MONITOR      performance · drift · data quality · fairness · cost
        │       ⚠ planned HERE means planned too late — design it at assessment
        ▼
   SUPPORT      incidents · retraining · model card updates · deprecation

   ⚠ THE MOST COMMON FAILURE: the lifecycle starts at BUILD.
     Everything upstream of it is then reconstructed under deadline pressure.
```

**Plain English:** the controlled path from idea to a supported production system that somebody
owns.

**Precisely:** the AI use-case lifecycle runs **assessment → data prep → build → test → validate
→ deploy → monitor → support**, with a named owner and an artifact at each stage.

### 2. Scenario

A stakeholder asks for "an AI model to predict SLA breaches." The tempting response is to start
modelling — the data exists, `scikit-learn` is one import away, and a first result is achievable
in an afternoon.

Every question that later blocks deployment is upstream of that afternoon: what business action
follows a prediction? who acts on it? what does success mean numerically? which fields exist at
prediction time? who owns the model in production? what happens when an employee disputes a
deprioritised ticket? **Starting at build means answering all of those retrospectively, under
deadline pressure, with a model already built that may not fit the answers.**

### 3. Example — the lifecycle table

| Stage | What happens |
|---|---|
| **Assessment** | Business objective, AI suitability, risk, owner, success metric |
| **Data prep** | Source access, quality, labels, privacy, feature availability |
| **Build** | Baseline, feature engineering, model training, experiment tracking |
| **Test** | Offline metrics, segment metrics, leakage checks |
| **Validate** | SME review, fairness, explainability, security, approval |
| **Deploy** | Registry, endpoint, canary/shadow, rollback |
| **Monitor** | Performance, drift, data quality, fairness, cost |
| **Support** | Incidents, retraining, model card updates, deprecation |

### 4. How it works

**Assessment decides whether to proceed at all.** "Do not use ML" is a legitimate and frequently
correct outcome: if the rule is `flag anything older than 4 hours in category X`, that rule is
cheaper, fully explainable and instantly auditable. **A model must beat the baseline to justify
its operational cost** — and the baseline is a rule, not a worse model.

**Validation is where a public-sector project differs most from a commercial one.** SME review,
fairness results, explainability and a model card are gates, not documentation produced
afterwards. This is the same intake and approval discipline as 8.6.9, applied to a model.

**Support is the stage that is planned last and lasts longest.** Incidents, retraining, model
card updates and eventual deprecation are the majority of a model's life.

### 5. Where it fits

```
   ▶ THE LIFECYCLE ◀ is the frame for every other topic in this stage
        │
        ├── assessment ....... 8.7.1 (is this even an ML problem?)
        ├── data prep ........ 8.7.3
        ├── build ............ 8.7.1, 8.7.5
        ├── test ............. 8.7.2, 8.7.10
        ├── validate ......... 8.7.9, 8.7.11, and 8.6.9's approval
        ├── deploy ........... 8.7.4, 8.7.6
        ├── monitor .......... 8.7.6, 8.7.10
        └── support .......... 8.7.6, 8.7.11
```

### 6. Libraries & code

| Job | How |
|---|---|
| Pipeline orchestration | Azure ML pipelines, or any workflow engine |
| Experiment record | MLflow (8.7.5) |
| Gates | Automated metric thresholds in CI, plus human review checkpoints |
| Documentation | Model card in version control (8.7.11) |
| Governance | The AI register entry and approval (8.6.9) |

### 7. Knobs & real numbers

| Knob | Typical | Notes |
|---|---|---|
| Baseline requirement | always, before any model | A rule or a trivial model |
| Test set usage | **once** | Any reuse invalidates the estimate |
| Validation gates | metrics + fairness + explainability + model card | All four, before approval |
| Review cadence in support | quarterly, or on policy change | Same as 8.6.9 |
| Time distribution | data prep dominates | Modelling is rarely the long pole |

### 8. Perspectives grid

| Lens | What matters here |
|---|---|
| **Theory** | The lifecycle exists because a model is a claim about a distribution, and every stage either establishes or re-verifies a condition under which that claim holds. |
| **Engineering** | Start at assessment. Build a baseline first. Keep the test set untouched. Put gates in CI where they can be automated and in review where they cannot. |
| **Operations** | Design monitoring at assessment time, not after deployment — what you can monitor constrains what you should deploy. |
| **Cost** | Data prep dominates the effort. A project that budgets for modelling and not for data preparation has budgeted for the wrong thing. |
| **Security** | Validation is where security, privacy and fairness reviews attach. Skipping it in a public entity is not a shortcut; it is a governance failure (8.6.9). |
| **Decision** | Do not start at build. Establish the business decision, the success metric, the feature availability and the owner first — and be willing to conclude that a rule is the right answer. |

### 9. Trade-offs & failure modes

- **The lifecycle starting at model training instead of business assessment.**
- **Monitoring planned after deployment.**
- **Support ownership unclear**, so the model quietly decays with nobody accountable.
- **No baseline**, so "good" is never defined.
- **Validation treated as documentation** produced after the decision rather than as a gate.

---

## 8.7.8 Telling the narrative
> **In the build:** Stage 7, Step 7 — *"tell it as one continuous story."*
>
> *Every other topic in this stage is knowledge. This one is delivery — and in an interview,
> delivery is what is actually being assessed.*

### 1. Definition

```
   THE SAME MATERIAL, TWO WAYS OF SAYING IT

   ❌ VOCABULARY MODE                      ✅ OPERATING-SYSTEM MODE
   "I know precision, recall, PR-AUC,      "Missing a breach costs more than a
    SHAP, drift detection, MLflow,          wasted review, so I optimise recall at
    Azure ML endpoints, fairness            acceptable precision, then set the
    metrics..."                             threshold from how many tickets
                                            supervisors can actually review."
   → a list. The panel cannot tell         → a decision, with a reason and a
     whether you have operated one.          constraint. Unmistakably operated.

   THE SPINE — eight beats, in lifecycle order, each carrying ONE decision
   ┌────────────┬──────────────────────────────────────────────────────────┐
   │ ASSESSMENT │ the business goal, and what success means NUMERICALLY     │
   │ DATA PREP  │ feature availability + leakage removal + time-based split │
   │ BUILD      │ baseline FIRST, then stronger models, tracked            │
   │ TEST       │ the metric, plus SEGMENTS                                 │
   │ VALIDATE   │ SME + fairness + explainability + model card             │
   │ DEPLOY     │ registry, endpoint, canary or shadow                      │
   │ MONITOR    │ drift + DELAYED ground truth + fairness                   │
   │ SUPPORT    │ retraining triggers, rollback, ownership, review          │
   └────────────┴──────────────────────────────────────────────────────────┘

   ⚠ THE TELL: candidates who have only read about this describe stages.
     Candidates who have done it describe DECISIONS AND CONSTRAINTS.
```

**Plain English:** being able to walk one real example from business question to supported
production system, in one continuous answer, without reciting a glossary.

**Precisely:** the narrative is the lifecycle (8.7.7) delivered as a single spoken answer on one
concrete use case, where each stage is represented by **the decision made there and the
constraint that drove it**, rather than by its name.

### 2. Scenario

The panel asks a deliberately open question: *"Walk me through how you would build and run a
machine-learning model for us."*

There is no correct set of words. What is being assessed is whether the lifecycle is something
you have **operated** or something you have **read about** — and the two sound completely
different. The first names constraints, trade-offs and things that went wrong; the second names
stages and tools.

### 3. Example — the full answer

> "For SLA breach prediction, I would start with **assessment**: confirm the business goal is
> early intervention, define success as high recall at workable precision, and complete risk and
> data classification.
>
> In **data prep**, I would use only fields available at ticket creation, remove post-resolution
> leakage, label historical breaches, split by time, and check Arabic/English coverage.
>
> I would **build** a baseline logistic regression or tree model, then compare stronger models
> with MLflow tracking.
>
> I would **test** recall, precision, PR-AUC, calibration and segment performance.
>
> **Validation** would include SMEs, fairness checks, explainability and a model card.
>
> **Deployment** would use Azure ML managed online or batch endpoints, with a canary or shadow
> run.
>
> In production I would **monitor** data drift, prediction drift, delayed ground-truth
> performance, fairness, latency and incidents.
>
> **Support** means retraining triggers, rollback, ownership and periodic review."

**The short version, when time is limited:** *"Assessment defines the decision and the metric.
Data prep decides what is available at prediction time. Build starts from a baseline. Test
segments the metric. Validation adds fairness, explainability and a model card. Deployment is
canary or shadow. Monitoring watches drift and delayed ground truth. Support owns retraining and
retirement."*

### 4. How it works

**Why this structure works, beat by beat** — each one answers a question the panel has not asked
yet:

- **Assessment** signals that you know a model is a business decision, not a modelling exercise.
- **Feature availability at prediction time** is the single strongest signal of practical
  experience in the whole answer — it is the mistake everyone makes once and never again.
- **A baseline first** signals you are not solving a rule-shaped problem with gradient boosting.
- **Segment metrics** signal fairness awareness before anyone asks about fairness.
- **A model card and SME review** signal that you have worked somewhere with governance.
- **Delayed ground truth** signals you have actually operated a model, because it is invisible
  until you have waited for labels that arrive days later.
- **Retraining triggers and ownership** signal you know models decay and someone has to own that.

**Three things to say without being asked**, because they convert a good answer into a
public-sector-credible one: the **appeal path** for anyone affected by a decision; **Arabic and
bilingual coverage** as a first-class evaluation segment; and **"we might conclude a rule is
better than a model"**, which demonstrates judgement rather than enthusiasm.

⚠ **Do not lead with algorithms.** The algorithm choice is the least interesting decision in the
whole lifecycle and the one candidates over-rehearse. Name it in one clause and move on.

### 5. Where it fits

```
   ▶ TELLING THE NARRATIVE ◀ is the delivery layer over 8.7.1 - 8.7.7
        │
        ├── it IS the lifecycle (8.7.7), spoken
        ├── it carries the metric decision (8.7.2) as a business trade-off
        ├── it carries the leakage insight (8.7.3) as its credibility anchor
        ├── it carries fairness (8.7.10) and explainability (8.7.9) unprompted
        └── it ends where governance begins (8.6.9): owner, review, retirement
```

### 6. Libraries & code

None. The artifact here is a rehearsed spoken answer on **one** example, carried consistently —
the same government HR/service-desk scenario used throughout this material, so that every detail
you add reinforces the others rather than introducing a new context.

### 7. Knobs & real numbers

| Knob | Typical | Notes |
|---|---|---|
| Full answer length | 60–90 seconds | Long enough for eight beats, short enough to hold attention |
| Short version | 20–30 seconds | For when the panel signals time pressure |
| Examples used | **one**, carried throughout | Switching examples costs the listener the thread |
| Concrete numbers included | 2–3 | "recall ≥ 0.85", "0.68 on Arabic" — specifics prove experience |
| Time spent on algorithms | one clause | The least interesting decision |
| Unprompted additions | appeal path, bilingual coverage, "maybe a rule" | The three that signal public-sector fit |

### 8. Perspectives grid

| Lens | What matters here |
|---|---|
| **Theory** | The lifecycle has a natural narrative order because each stage's output is the next stage's input — which is why it can be told as a story at all. |
| **Engineering** | Anchor the story to one concrete example with real numbers. Abstract answers are indistinguishable from memorised ones. |
| **Operations** | The stages that prove operational experience are monitoring and support — most candidates stop at deployment, which is where the work actually begins. |
| **Cost** | Mentioning that a rule might beat a model, and that data prep dominates the effort, demonstrates the cost judgement panels are probing for. |
| **Security** | Fairness, explainability and the appeal path are the public-sector differentiators. Volunteer them; do not wait to be asked. |
| **Decision** | Tell it as decisions and constraints, in lifecycle order, on one example, ending with ownership and retirement — not as a list of tools you have used. |

### 9. Trade-offs & failure modes

- **Reciting vocabulary instead of decisions.** The most common failure, and immediately audible.
- **Starting at model training**, which skips the half of the lifecycle that shows judgement.
- **Stopping at deployment**, leaving out monitoring and support — where real experience shows.
- **Switching examples mid-answer**, costing the listener the thread.
- **Over-indexing on algorithms**, the least interesting decision in the story.
- **No numbers**, making the answer indistinguishable from something read in a blog post.
- **Never mentioning that ML might be the wrong tool**, which reads as enthusiasm rather than
  judgement.

---

# Part C — Stage 7 assembled

## C1. One model, end to end

Everything in this file, in the order it executes, on a single real model: **SLA breach
prediction for internal service tickets**. As in Stages 1–6, this section is self-contained —
each step carries its mechanism, its numbers and its failure mode inline.

**Before the trace starts, three decisions are already locked in:**

- **This is a prediction problem, not a generation problem** [8.7.1]. Classic ML learns
  `features available now → score → business action`; an LLM does `instructions + context →
  generated text`. If this is confused, you get a generative model doing a classifier's job:
  more expensive, less testable, and impossible to calibrate. **The first question is never
  "which model?" — it is "what is the business decision, and what information exists at decision
  time?"**
- **The metric was chosen before any modelling** [8.7.2]. Missing a real breach costs more than a
  wasted review, so the target is **recall at acceptable precision**. If this flips — metric
  chosen after training — the team optimises whatever looks best in hindsight.
- **A rule is the baseline, and the model must beat it** [8.7.7]. "Flag anything older than four
  hours in category X" is cheaper, fully explainable and instantly auditable. **"Do not use ML"
  is a legitimate outcome of assessment**, and a model that cannot beat the rule is not ready.

```
MODEL: predict SLA breach risk for a service ticket.

 1. ASSESSMENT                                                   [8.7.7]
    business goal · AI suitability · risk rating · owner
    · success metric defined NUMERICALLY
    → "should we use ML at all?" is a real outcome

 2. FRAME THE PREDICTION                                  [8.7.1 / 8.7.2]
    unit = one ticket · prediction time = creation, refreshed hourly
    · target = breached SLA within the policy window
    · action = supervisor review · human role = supervisor decides

 3. DATA PREP — FEATURE AVAILABILITY AND LEAKAGE                  [8.7.3]
    build the availability table · run the six-question leakage
    checklist · TIME-BASED split · preprocessing inside the pipeline

 4. BUILD — BASELINE FIRST, THEN TRACK                    [8.7.1 / 8.7.5]
    a rule, then logistic regression, then stronger models
    · MLflow: params, metrics, artifacts, DATA VERSION, git commit

 5. TEST — THE METRIC, THEN THE SEGMENTS                 [8.7.2 / 8.7.10]
    recall · precision · PR-AUC · calibration
    → then recompute EVERY metric per segment

 6. VALIDATE — THE PUBLIC-SECTOR GATES           [8.7.9 / 8.7.11 / 8.6.9]
    SME review · fairness · explainability · model card · approval

 7. DEPLOY — REGISTER, THEN ROLL OUT GRADUALLY            [8.7.4 / 8.7.6]
    register only if the gate passes · online and/or batch endpoint
    · shadow → canary → blue/green · rollback ready

 8. MONITOR — SIX DRIFTS AND A DELAYED TRUTH                      [8.7.6]
    schema · data · prediction · concept · label · fairness
    → log prediction, WAIT for outcome, join label, compare, alert

 9. SUPPORT — RETRAIN, RE-GATE, RETIRE                   [8.7.6 / 8.7.11]
    retraining automated · PROMOTION never · model card updated
```

### Every step, unpacked — the crux of each topic, as points, in execution order

**1. Assessment** — `[8.7.7]`
- Establishes: business objective · AI suitability · risk rating · named owner · **success metric
  in numbers**.
- **"Do not use ML" is a legitimate and frequently correct outcome.** If a rule solves it, the
  rule is cheaper, fully explainable and instantly auditable.
- **Monitoring must be designed here, not after deployment** — what you can monitor constrains
  what you should deploy.
- ⚠ **Owns:** the lifecycle starting at *build*. Every question that later blocks deployment —
  what action follows a prediction, who acts on it, what success means, who owns it in production
  — then gets answered retrospectively, under deadline pressure, with a model already built.

**2. Frame the prediction** — `[8.7.1] [8.7.2]`
- The framing table, decided before any code: **prediction** = probability a ticket will breach ·
  **prediction time** = at creation, refreshed hourly · **unit** = one ticket · **target** =
  breached SLA within the policy window · **features** = fields known at creation/update time ·
  **metric** = high recall at acceptable precision · **action** = supervisor review or priority
  boost · **human role** = the supervisor decides the intervention.
- **Prediction time is the load-bearing entry.** It determines which features are legal, which is
  why it precedes feature engineering rather than following it.
- **The metric follows from which error costs more**, and the threshold follows from **capacity**:
  if the model flags 400 tickets a day and supervisors can review 60, paper recall is irrelevant.
- ⚠ **Owns:** a generative model used where a classifier is cheaper and more testable.

**3. Data prep — feature availability and leakage** — `[8.7.3]`
- **The feature-availability table comes first:** category (creation → valid) · priority (creation
  → valid if set before scoring) · assigned team backlog (scoring time → valid) · escalation flag
  (maybe later → only for a refresh-time model) · **resolution notes, final resolution time,
  `closed_late` (after closure → invalid; the last one *is* the target)**.
- **The six-question leakage checklist:** was the field created after prediction time? · was it
  edited by a human who already knew the outcome? · **is it a proxy for the target?** · **was
  preprocessing fit on all data before the split?** · are duplicates crossing splits? · does the
  target definition use future policy?
- **Question four is the subtle one:** fitting a scaler or encoder on the full dataset before
  splitting leaks test-set statistics into training. `sklearn`'s `Pipeline` exists to make this
  hard to get wrong.
- **Split by time** for time-ordered data. A random split lets the model learn from December to
  predict November — a capability it will not have in production.
- **Imbalance, in order:** stratified/time-aware split → class weights → PR-AUC and recall at
  threshold → threshold tuning → calibrated probabilities → **resampling only inside training
  folds**.
- ⚠ **Owns:** resampling before the split — a leakage bug wearing an imbalance costume, putting
  duplicates of the same record on both sides.
- ⚠ **Owns:** the 0.94 PR-AUC model whose top feature is `resolution_time_hours`. **The offline
  number was real and the model is worthless**, because that column is null at prediction time.

**4. Build — baseline first, then track** — `[8.7.1] [8.7.5]`
- **A baseline is mandatory**, and it is a *rule*, not a worse model. Without one, "good" is
  undefined.
- Algorithm choice is the least interesting decision: logistic regression (fast, interpretable
  baseline; linear boundaries) · decision tree (explainable rules; overfits) · random forest
  (strong tabular baseline; less interpretable) · **gradient boosting (often best for tabular
  data; tuning and monitoring complexity)** · SVM · k-means (clustering) · Isolation Forest
  (anomaly detection) · ARIMA/Prophet (time series) · neural nets (high capacity, more data, ops
  and explainability burden).
- **MLflow logs seven things, and the last four are the ones omitted:** parameters · metrics ·
  artifacts · **data version** · **code version (git commit)** · **environment** · **model
  signature**. **Reproducibility that omits the data version is not reproducibility.**
- **Promotion is the step after logging** — a run becomes a registered version, and a version is
  promoted through stages or aliases. Logging without promotion leaves a pile of experiments and
  no answer to "which one is live?"
- ⚠ **Owns:** the production endpoint that cannot be traced back to a run.

**5. Test — the metric, then the segments** — `[8.7.2] [8.7.10]`
- **The confusion matrix is the root**; every classification metric is a ratio from it.
  **Precision** = TP ÷ predicted positives ("of flagged tickets, how many really breach?");
  **recall** = TP ÷ actual positives ("of real breaches, how many did we catch?").
- **Accuracy on imbalanced data is a trap:** if 3% of tickets breach, "predict no breach always"
  scores 97% and is worthless. Use **PR-AUC** for rare positives, not ROC-AUC.
- **Calibration matters the moment a score is shown as a risk.** An uncalibrated 0.8 presented as
  "80% likely" is a misleading statement, not merely suboptimal.
- **Then segment — and this is where the conclusion changes.** Overall recall 0.85 concealed:
  English **0.90** · **Arabic 0.68** · web **0.88** · **phone-transcribed 0.63**. Two groups are
  systematically under-served, and **no aggregate number would ever have shown it**.
- **The test set is touched once.** Any reuse invalidates the estimate.
- ⚠ **Owns:** metrics not segmented by language, department, geography or user group.
- ⚠ **Owns:** ROC-AUC high while the chosen threshold is operationally useless.

**6. Validate — the public-sector gates** — `[8.7.9] [8.7.11] [8.6.9]`
- **Fairness metrics, and they can conflict:** demographic parity (similar positive rates) ·
  **equal opportunity** (similar recall) · equalized odds (similar TPR *and* FPR) · **calibration
  by group** · disparate impact ratio. Satisfying parity and calibration simultaneously is
  generally impossible when base rates differ — **choosing which applies is a policy decision
  with legal input, not an engineering preference**.
- **The fairness paradox:** you cannot measure disparity across a protected attribute without
  holding it for evaluation. **Discarding it does not create fairness — it makes unfairness
  unmeasurable.**
- **Mitigations, in order of preference:** improve data coverage for the under-performing group
  (the only fix that makes the model genuinely better) · remove or transform proxy features · add
  human review for high-impact decisions · **segment thresholds only with legal and governance
  review** · monitor fairness after deployment.
- **Explainability by audience:** the data scientist debugs; the operator needs to know why *this*
  ticket was flagged; the **affected user needs an understandable reason and an appeal path**; the
  auditor needs evidence of control. **SHAP** attributes the actual prediction with consistency
  guarantees; **LIME** fits a local surrogate, faster but less stable.
- **For a decision about a person, never say "the AI decided."** Give, in this order: the policy
  or business rule basis · the relevant input facts · the model score where appropriate · the main
  contributing factors · **the appeal or human review path**. The score is third, not first.
- **The model card** records intended use, **out-of-scope use** (e.g. *not* employee performance
  evaluation), training data, metrics, **segments with their numbers**, limitations, human
  oversight, monitoring plan and owner. The out-of-scope row is the purpose-limitation control at
  model level.
- ⚠ **Owns:** chain-of-thought from an LLM treated as an audit explanation. It is a plausible
  narrative, not a causal account.
- ⚠ **Owns:** proxy features unexamined, so `department`, `channel` or `language` silently encodes
  a protected attribute.

**7. Deploy — register, then roll out gradually** — `[8.7.4] [8.7.6]`
- **Registration is a promotion decision, not a save operation**: register only if
  `recall >= 0.85 and precision >= 0.55`, tagged with the metrics and the data version.
- **Online vs batch is a product decision:** managed online endpoint scores one ticket in real
  time; batch endpoint scores all open tickets hourly or nightly. **If both exist, both must share
  the same preprocessing code**, or the two paths silently disagree.
- **The rollout ladder is the same discipline as Stage 6's:** shadow (score, do not act) → canary
  (5–10%) → blue/green, with rollback ready.
- ⚠ **Owns:** notebook output manually copied into production.
- ⚠ **Owns:** data, environment and code versions not tied to the registered model, so the running
  model cannot be reproduced.

**8. Monitor — six drifts and a delayed truth** — `[8.7.6] [8.7.10]`
- **Six drift types, each detected differently:** **schema drift** (column renamed → schema
  validation) · **data drift** (category distribution moves → distribution distance, PSI) ·
  **prediction drift** (scores shift → output distribution) · **concept drift** (features no
  longer predict the target → **delayed ground-truth performance**) · **label drift** (the target
  *definition* changes → policy and process review, which **no distribution test detects**) ·
  **fairness drift** (one segment worsens → segment metrics).
- **The monitoring loop:** log prediction → **wait for the outcome** → join label → compute
  performance → compare to baseline → alert → investigate → retrain or roll back.
- **The ground-truth delay is the defining operational property.** You learn the truth when the
  ticket closes — hours or days later. That lag is exactly why data and prediction drift matter:
  they are the **only** signals available before labels arrive.
- **The worked decay:** launched at 0.87 recall, six months later 0.71, with nothing changed —
  two new ticket categories (data drift), a renamed upstream field arriving null (schema drift),
  and a changed SLA policy (label drift). **None of them raised an error.**
- ⚠ **Owns:** drift alerts with no owner and no runbook — a fired alert nobody is accountable for
  trains the team to ignore the channel.
- ⚠ **Owns:** ground truth arriving late and nobody closing the loop.

**9. Support — retrain, re-gate, retire** — `[8.7.6] [8.7.11]`
- **Retraining triggers:** performance below threshold when ground truth arrives · significant
  data or prediction drift · **policy or process change** (the trigger nobody automates, because
  it arrives as an email rather than a metric) · new labelled data volume · **fairness metric
  regression** · model or dependency deprecation.
- **Retraining can be automated. Promotion must not be.** The gates: data checks passed · metrics
  passed · **fairness did not regress** · explainability reviewed if high impact · **model card
  updated** · canary or shadow completed.
- **Support is planned last and lasts longest** — incidents, retraining, card updates and eventual
  retirement are the majority of a model's life.
- ⚠ **Owns:** retraining that ships automatically without validation and approval.
- ⚠ **Owns:** a model card written once for approval and never updated, so it describes a model
  that is no longer running.
### Full cram reference — every topic in this file, fact by fact

Every definition, mechanism, table and failure mode from Part B (8.7.1–8.7.11), in bullet form.

#### 8.7.1 — ML fundamentals `[WORKING]`

- **Classic ML:** `features available NOW → prediction or score → business action`. **LLM:**
  `instructions + context → generated text or tool proposal`. **The first question is not "which
  model?" but "what is the business decision, and what information is available at decision
  time?"**
- **Core concepts:** supervised (labelled examples) · unsupervised (structure without labels) ·
  train/validation/test (fit, tune, estimate) · overfitting (memorises training data) ·
  cross-validation (repeated splits, stabler estimate) · **baseline** (a simple rule to beat —
  without one, "good" is undefined).
- **Failure modes:** a generative model used where a classifier is cheaper and more testable ·
  the test set touched during feature/model selection · **time-based data split randomly**.

#### 8.7.2 — Metrics `[CORE]`

- **Pick the metric before training**, or the team optimises whatever looks best afterwards.
- **The confusion matrix is the root.** Precision = TP ÷ predicted positives ("of flagged
  tickets, how many really breach?") · Recall = TP ÷ actual positives ("of real breaches, how
  many did we catch?").
- **Classification:** accuracy (balanced classes, symmetric costs) · precision (**false positives
  expensive**) · recall (**false negatives expensive**) · F1 (balance) · ROC-AUC (ranking across
  thresholds) · **PR-AUC (rare positives — more informative than ROC-AUC)** · **calibration (a
  0.8 means ~80% risk)** · confusion matrix (explaining error types to business users).
- **Regression:** MAE (easiest to explain) · RMSE (punishes large misses; capacity planning) ·
  MAPE (**fails near zero**) · R² (never sufficient alone) · pinball loss (quantile forecasts,
  worst-case staffing).
- **The business decides which error is worse; the metric follows.** For SLA breach: optimise
  **recall at acceptable precision**, then set the **threshold from review capacity** — 400 flags
  a day against 60 reviewable tickets makes paper recall irrelevant.
- ⚠ **Accuracy on imbalanced data is a trap:** at a 3% base rate, "always predict no breach"
  scores 97%.
- **Failure modes:** accuracy on imbalanced data · ROC-AUC high with an operationally useless
  threshold · **metrics not segmented** · the metric chosen after training · uncalibrated scores
  presented as risk · MAPE near zero · threshold set at the F1 peak rather than from capacity.

#### 8.7.3 — Data and features `[CORE]`

- **Leakage = a feature contains information not available at prediction time.** The model looks
  brilliant offline and collapses in production.
- **The feature-availability table:** category (creation ✓) · priority (creation ✓ if set before
  scoring) · assigned team backlog (scoring time ✓) · escalation flag (only for a refresh-time
  model) · **resolution notes ✗ · final resolution time ✗ · `closed_late` ✗ (it IS the target)**.
- **The six-question leakage checklist:** created after prediction time? · edited by a human who
  knew the outcome? · **a proxy for the target?** · **preprocessing fit on all data before the
  split?** · duplicates crossing splits? · target definition using future policy?
- **Imbalance controls, in order:** stratified/time-aware split → class weights → PR-AUC and
  recall at threshold → threshold tuning → calibrated probabilities → **resampling only inside
  training folds**.
- ⚠ **Resampling before the split** puts duplicates on both sides — a leakage bug in imbalance
  clothing. ⚠ **Random splits on time-ordered data** let the model learn from the future.
- **Failure modes:** feature availability time undocumented · text fields including
  post-outcome agent notes · resampling before the split · data quality checks skipped (nulls,
  schema, category drift) · preprocessing fit before splitting · random splits on time data · a
  proxy for the target used as a feature.

#### 8.7.10 — Fairness and bias testing `+` `[CORE]`

- Checks whether **performance** or **outcomes** differ materially across groups. **Not optional**
  where the model affects access, priority, eligibility or service quality.
- **The worked disparity:** overall recall 0.85 → English **0.90**, **Arabic 0.68**, web 0.88,
  **phone-transcribed 0.63**. The aggregate passed; two groups are systematically under-served.
- **Five checks:** performance parity · error disparity (**are false negatives higher for
  Arabic?**) · outcome disparity · calibration by group · **proxy features**.
- **The metrics:** demographic parity (similar positive rates) · **equal opportunity** (similar
  recall) · equalized odds (similar TPR and FPR) · calibration by group · disparate impact ratio.
  **They can conflict** — parity and calibration cannot both hold when base rates differ, so
  choosing is a policy act.
- **The paradox:** you cannot measure disparity without holding the protected attribute for
  evaluation. **Discarding it makes unfairness unmeasurable, not absent.**
- **Mitigations in order:** improve data coverage for the under-performing group · remove or
  transform proxies · human review for high-impact decisions · **segment thresholds only with
  legal and governance review** · monitor after deployment.
- **Failure modes:** protected attributes ignored entirely · fairness checked once before launch ·
  "fair" overall but failing Arabic or low-volume groups · threshold segmentation without legal
  review · proxies unexamined · **disparity quietly tuned away rather than escalated**.

#### 8.7.9 — Explainability `+` `[CORE]`

- **Global** = what drives the model generally (feature importance, partial dependence).
  **Local** = why this prediction (SHAP, LIME).
- **Audiences need different things:** data scientist (debug) · operator (why THIS ticket) ·
  **affected user (an understandable reason AND an appeal path)** · auditor (evidence of control).
- **SHAP** attributes the actual prediction using game-theoretic contribution values, consistent
  but costlier. **LIME** fits a simple local surrogate — faster, less stable across runs.
- **For a decision about a person, never say "the AI decided."** Provide: **policy or business
  rule basis** → **relevant input facts** → model score where appropriate → **main contributing
  factors** → **appeal or human review path**. The score is third, not first.
- **Failure modes:** LLM chain-of-thought treated as an audit explanation · feature importance
  shown without proxy analysis · explanations technically correct but useless to the affected
  user · **no appeal path**, making the explanation decorative · explanations only offline, so the
  operator sees a score with no reason.

#### 8.7.11 — Model cards `+` `[WORKING]`

- **Structured documentation** making a model reviewable by someone who did not build it — the
  Stage 7 counterpart of 8.6.9's AI register entry.
- **Contents:** intended use · **out-of-scope use** (e.g. not employee performance evaluation) ·
  training data · metrics · **segments, with the numbers** · limitations · human oversight ·
  monitoring · owner.
- **The out-of-scope row does the most work** — it is purpose limitation at model level, stopping
  a triage model being repurposed for something about people's careers.
- **Fails when** written once for approval and **not updated after retraining or replacement**,
  so it describes a model that is no longer running.

#### 8.7.4 — Azure ML `[WORKING]`

- Managed infrastructure whose value is **not compute** but that data, code, environment and model
  version become **linked, versioned artifacts**.
- **Components:** workspace · compute · **versioned data asset** · pipeline · **model registry** ·
  **managed online endpoint** (score one ticket now) · **batch endpoint** (score all open tickets
  hourly).
- **Online vs batch is a product decision**, and if both exist **both must share preprocessing
  code**.
- **Registration is a promotion decision**, gated on the business metric:
  `if recall >= 0.85 and precision >= 0.55: register(...)` with metrics and data version as tags.
- **Fails when** notebook output is copied into production · data/environment/code versions are
  not tied to the registered model · **real-time and batch preprocessing diverge**.

#### 8.7.5 — MLflow `[WORKING]`

- The common language between experiments and production model management — it answers "which run
  produced the model currently serving traffic?"
- **Log seven things; the last four get omitted:** parameters · metrics · artifacts · **data
  version** · **git commit** · **environment** · **model signature**. **Reproducibility that omits
  the data version is not reproducibility.**
- **A good run record:** `run_id` · `git_commit` · `data_version` (`tickets-2026q2-v3`) · params ·
  metrics · artifacts (confusion matrix, calibration plot) · signature · environment.
- **Promotion follows logging** — a run becomes a registered version, promoted through
  stages/aliases. Logging without promotion leaves experiments and no live answer.
- **Fails when** runs are logged but no version is promoted · **the endpoint cannot be traced back
  to a run** · reproducibility omits the data version.

#### 8.7.6 — Deployment and monitoring `[CORE]`

- **A deployed model is a depreciating asset.** The world moves; the weights do not.
- **Six drifts and their detection:** schema (renamed column → schema validation) · data
  (distribution → PSI/distance) · prediction (scores shift → output distribution) · **concept**
  (features stop predicting → **delayed ground-truth performance**) · **label** (target
  *definition* changes → policy review; **no distribution test sees this**) · fairness (segment
  metrics).
- **The monitoring loop:** log prediction → **wait for outcome** → join label → compute
  performance → compare to baseline → alert → investigate → retrain or roll back.
- **Deployment patterns:** blue/green · canary · **shadow (score, do not act)** · A/B (business
  outcomes) · batch scoring. Same discipline as 8.5.7, applied to a model artifact.
- **Retraining triggers:** performance below threshold when ground truth arrives · data or
  prediction drift · **policy/process change** · new labelled data · **fairness regression** ·
  deprecation.
- **Retraining can be automated; promotion must not be.** Gates: data checks · metrics ·
  **fairness did not regress** · explainability if high impact · **model card updated** ·
  canary/shadow completed.
- **The worked decay:** 0.87 → 0.71 over six months with nothing changed — new categories, a
  renamed field arriving null, and a changed SLA policy. **None raised an error.**
- **Knobs (`typical`):** ground-truth lag hours to days · drift checks daily on inputs, weekly on
  performance · PSI ~0.1 moderate, ~0.25 significant · canary 5–10% · one named owner per alert.
- **Failure modes:** ground truth late and the loop never closed · **drift alerts with no owner or
  runbook** · retraining shipping without validation · shadow skipped for high-impact models ·
  label drift undetected · online/batch preprocessing diverging · schema validation only in
  training.

#### 8.7.7 — End-to-end lifecycle `[CORE]`

- **assessment → data prep → build → test → validate → deploy → monitor → support**, each with an
  owner, an artifact and a gate.
- **Assessment:** business objective, AI suitability, risk, owner, success metric. **"Do not use
  ML" is a legitimate outcome** — a rule is cheaper, explainable and auditable, and **the model
  must beat the baseline to justify its operational cost**.
- **Data prep:** source access, quality, labels, privacy, **feature availability** — and it
  dominates the effort.
- **Build:** baseline first, then stronger models, tracked.
- **Test:** offline metrics, **segment metrics**, leakage checks. The test set is touched **once**.
- **Validate:** SME review, fairness, explainability, security, approval — **gates, not
  documentation produced afterwards**.
- **Deploy:** registry, endpoint, canary/shadow, rollback.
- **Monitor:** performance, drift, data quality, fairness, cost — **designed at assessment time**,
  because what you can monitor constrains what you should deploy.
- **Support:** incidents, retraining, model card updates, deprecation — **planned last, lasts
  longest**.
- **Failure modes:** starting at model training · monitoring planned after deployment · unclear
  support ownership · no baseline · validation treated as documentation rather than a gate.

#### 8.7.8 — Telling the narrative `[CORE]`

- The lifecycle delivered as **one continuous spoken answer on one concrete example**, where each
  stage is represented by **the decision made and the constraint that drove it** — not by its
  name.
- **The tell:** candidates who have read about this describe *stages*; candidates who have done it
  describe **decisions and constraints**.
- **What each beat signals:** assessment → a model is a business decision · **feature availability
  at prediction time → the strongest signal of practical experience in the whole answer** ·
  baseline first → not solving a rule-shaped problem with gradient boosting · segment metrics →
  fairness awareness before being asked · model card and SME review → experience of governance ·
  **delayed ground truth → you have actually operated a model** · retraining triggers and
  ownership → you know models decay.
- **Three things to volunteer unasked:** the **appeal path** · **Arabic and bilingual coverage** ·
  **"we might conclude a rule is better than a model."**
- **Knobs (`typical`):** full answer 60–90 s · short version 20–30 s · **one example, carried
  throughout** · 2–3 concrete numbers · algorithms get one clause.
- **Failure modes:** reciting vocabulary instead of decisions · starting at model training ·
  **stopping at deployment**, omitting monitoring and support · switching examples mid-answer ·
  over-indexing on algorithms · no numbers · never mentioning that ML might be the wrong tool.

### What this trace doesn't re-run, and why

- **8.7.8 (telling the narrative)** is not a step in the model's life — it is the delivery layer
  over the other ten, and its "execution" happens in an interview room rather than in production.
- **8.7.11 (model cards)** is produced once at validation and then **updated at every retrain**,
  so it appears at steps 6 and 9 rather than as a stage of its own.
- **8.7.4 and 8.7.5 (Azure ML, MLflow)** are the substrate rather than steps: they are where steps
  4, 7 and 9 record and deploy their artifacts. Choosing them is a platform decision taken once.
- **8.7.1 (fundamentals)** is not a step because it is the framing that decides whether any of
  this applies — the "is this an ML problem at all?" question inside assessment.
- See **C2** for when to reach for classic ML versus an LLM at all, and **C3** for how this model
  becomes one tool inside the Stage 1–6 assistant.

Nine steps, each with mechanism, number and failure mode — and the **Full cram reference** means
this one C1 section carries every fact in the file.

## C2. Classic ML vs LLM — the first decision

Before any of C1 runs, one question decides whether it runs at all. **Generation and prediction
are different problems**, and using the wrong tool is expensive in both directions:

| Need | Better first choice | Why |
|---|---|---|
| Predict SLA breach | **Classic ML classifier** | Repeatable mapping, calibratable, cheap per call, fully testable |
| Forecast call volume | Time-series / regression model | The output is a number over time, not language |
| Detect anomalous claims | Anomaly detection | No labels required, and the pattern is statistical |
| Answer a policy question with citations | **RAG** (Stage 3) | The answer exists in documents and must be attributable |
| Summarize a ticket | **LLM** | Language in, language out |
| Extract fields from free text | LLM or an NLP extractor, then a **structured workflow** | Extraction is language; what follows is deterministic |
| Route tickets by category | Small classifier **or** small LLM | Genuinely a toss-up — decide on measured cost and quality |

**The distinguishing question:** is the output a **score or a class over known features**, or is
it **language generated from context**? The first is Stage 7; the second is Stages 1–6. The last
row exists because that boundary is genuinely blurred for short classification tasks — and there
the answer is to measure both rather than to argue.

## C3. How it connects back to the GenAI system

The classifier does not live alone. **It becomes one tool inside the agentic assistant**, which
is the point at which all seven stages become one system:

```
   User asks: "Which open tickets need attention?"
   Assistant:
     1. queries open tickets                              [8.4.2 tool call]
     2. calls the SLA RISK CLASSIFIER endpoint            [8.7.4 — this stage]
     3. summarizes the top risks with explanations        [8.7.9 + generation]
     4. creates draft follow-up actions                   [8.4.2 draft, not write]
     5. REQUIRES HUMAN APPROVAL before changing priority  [8.4.4]

   The classifier is governed by Stage 7.
   The assistant wrapping it is governed by Stages 1-6.
```

⚠ **The combined failure mode is the one worth naming:** the LLM may **overstate what the
classifier means**. A risk score is not a decision. The final answer must **preserve uncertainty**,
cite the model version where relevant, and **route high-impact actions to a human** — which is
exactly 8.4.4's approval gate doing a job that no amount of model accuracy removes.

| Stage 7 concept | Its Stage 1–6 counterpart |
|---|---|
| Train/validation/test split | Golden set and eval harness (8.5.1) |
| Precision, recall, PR-AUC | Groundedness, relevance, abstention (8.5.2) |
| Model registry, MLflow runs | Prompt/model/index version pinning (8.5.7) |
| Shadow and canary deployment | Shadow and canary for prompts (8.5.7) |
| Drift detection, retraining triggers | Feedback loops and incident triage (8.5.6) |
| Fairness and bias testing | Red-team and permission-sensitive cases (8.6.10) |
| Model card | AI register entry (8.6.9) |

## C4. Self-test

Answer out loud. Every question here is answerable from `C1` alone.

1. When is classic ML the better first choice than an LLM? Give the distinguishing question.
2. Your model scores 0.94 PR-AUC and its top feature is `resolution_time_hours`. What happened?
3. Give the six-question leakage checklist. Which one is the subtle one, and why?
4. Why is accuracy a trap on imbalanced data? Use numbers.
5. Precision or recall for SLA breach prediction — which, and what sets the threshold?
6. Overall recall is 0.85 and the model passes its gate. Why might it still be unfit to deploy?
7. Why can you not measure fairness if you discard protected attributes entirely?
8. Name three fairness metrics and explain why they can conflict.
9. A person asks "why was my ticket deprioritised?" What exactly do you provide, and in what
   order?
10. What is the difference between SHAP and LIME?
11. Name the six drift types. Which one cannot be detected by any distribution test, and why?
12. Why is the ground-truth delay the defining operational property of monitoring?
13. Retraining can be automated. What must not be, and what are the gates?
14. What does "reproducibility" require beyond the code and the model file?
15. Your model launched at 0.87 recall and is now at 0.71 with no code change. Give three
    explanations.
16. Why must online and batch scoring share preprocessing code?
17. What does the "out-of-scope use" row of a model card actually control?
18. Why must a model beat a rule, and what does it mean if it cannot?
19. Where does the lifecycle most commonly start, and where should it start?
20. Your assistant calls the classifier and tells the user "this ticket will breach." What is
    wrong with that sentence?

*If you can only recite the definition and not the failure mode, it is not learned yet.*

---

*End of Stage 7 — and of the seven-stage build. Return to `00-MAP.md` for the index, or
`08-Interview-Questions-Model-Answers.md` for the consolidated question bank.*
