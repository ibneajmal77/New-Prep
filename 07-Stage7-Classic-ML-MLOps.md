# Stage 7 - Classic ML & MLOps (8.7)

*Two layers: **Part A** is the build narrative. **Part B** is the complete reference. **Part C**
assembles it. This is the non-LLM half of the AI interview, and it closes the full lifecycle:
assessment -> data prep -> build -> test -> validate -> deploy -> monitor -> support.*

**Where we are:** Stages 1-6 built a generative AI assistant. Some problems in the same
organization are not generative AI problems. Forecasting demand, classifying tickets, detecting
fraud, predicting churn, scoring risk and finding anomalies are usually classic ML problems.
The senior answer is knowing when not to use an LLM.

---

# Part A - THE BUILD: Stage 7

## Step 1. The business asks for prediction, not generation

HR wants to predict which service tickets will breach SLA. There is no need for a frontier
model to write prose. We need labelled historical data and a classifier.

> **-> [8.7.1 ML fundamentals](#871-ml-fundamentals)**

## Step 2. Pick the metric before building the model

Accuracy looks good because only 8% of tickets breach SLA. A model that predicts "no breach"
for everything is 92% accurate and useless. We need precision, recall, F1, ROC-AUC or
regression metrics depending on the business cost of each error.

> **-> [8.7.2 Metrics](#872-metrics)**

## Step 3. The dataset is leaking the answer

The training table includes `closed_late = true`, a field only known after the SLA breach. The
model scores beautifully offline and fails in production. This is leakage, and it is the classic
ML version of an overly helpful prompt.

> **-> [8.7.3 Data and features](#873-data-and-features)**

## Step 4. The model is accurate overall and unfair for one group

The model misses Arabic-language tickets and over-prioritizes one department. In a public-sector
system, aggregate accuracy is not enough.

> **-> [8.7.10 Fairness and bias testing](#8710-fairness-and-bias-testing-)**
> **-> [8.7.9 Explainability](#879-explainability-)**
> **-> [8.7.11 Model cards](#8711-model-cards-)**

## Step 5. Put the training pipeline somewhere real

Notebooks do not make production. We need Azure ML workspaces, compute, pipelines, model
registry, managed online endpoints for real-time scoring and batch endpoints for scheduled
jobs.

> **-> [8.7.4 Azure ML](#874-azure-ml)**
> **-> [8.7.5 MLflow](#875-mlflow)**

## Step 6. Production data changes

Departments reorganize, ticket categories change, and the model silently decays. We need data
drift, concept drift, model performance monitoring, retraining triggers, shadow deployment and
A/B tests.

> **-> [8.7.6 Deployment and monitoring](#876-deployment-and-monitoring)**

## Step 7. Tell the lifecycle as one story

The JD names the full lifecycle. You need to narrate it end to end using a real example, not as
a memorized list.

> **-> [8.7.7 End-to-end lifecycle](#877-end-to-end-lifecycle)**
> **-> [8.7.8 Telling the narrative](#878-telling-the-narrative)**

---

# Part B - THE REFERENCE

## 8.7.1 ML fundamentals
> **In the build:** Stage 7, Step 1 - *"prediction, not generation."*

### Definition

Classic machine learning learns a mapping from input features to an output target. It is used
for prediction, scoring, ranking, clustering and anomaly detection. It does not generate
grounded prose from a context window.

### Core concepts

| Concept | Meaning |
|---|---|
| Supervised learning | Train on labelled examples: features -> target |
| Unsupervised learning | Find structure without labels: clusters, anomalies |
| Train/validation/test | Fit, tune, then estimate real performance |
| Overfitting | Model memorizes training data and fails on new data |
| Cross-validation | Repeated train/test splits for more stable estimates |
| Baseline | Simple model or rule to beat |

### Example

```
Task: predict SLA breach for a ticket.

Features available at ticket creation:
  category, channel, language, department, priority, requester type,
  text length, day/time, previous backlog, assigned team load.

Target:
  breached_sla = true/false.
```

If the target is known only after the event, do not include downstream fields as features.

### Fails when

- A generative model is used where a classifier or regressor is cheaper and more testable.
- The test set is touched during feature/model selection.
- Time-based data is split randomly, leaking future patterns into training.

---

## 8.7.2 Metrics
> **In the build:** Stage 7, Step 2 - *"pick the metric before building the model."*

### 1. Definition

Metrics define what "good" means for the business problem. Pick the metric before training, or
the team will optimize whatever looks best after the fact.

### 2. Classification metrics

| Metric | Use when |
|---|---|
| Accuracy | Classes are balanced and errors cost roughly the same |
| Precision | False positives are expensive |
| Recall | False negatives are expensive |
| F1 | Need balance between precision and recall |
| ROC-AUC | Ranking quality across thresholds |
| PR-AUC | Rare positive class; more informative than ROC-AUC |
| Confusion matrix | Explains error types to business users |

### 3. Regression metrics

| Metric | Use when |
|---|---|
| MAE | Easy-to-explain average absolute error |
| RMSE | Penalize large errors more heavily |
| MAPE | Percentage error, but fails near zero |
| R-squared | Variance explained; not enough alone |

### 4. Business choice

For SLA breach prediction, missing a real breach is worse than falsely flagging a ticket for
review. Optimize for recall at an acceptable precision. Then set the decision threshold from
business capacity: how many tickets can supervisors actually review?

### 5. Fails when

- Accuracy is used on imbalanced data.
- ROC-AUC is high but the chosen threshold is operationally useless.
- Metrics are not segmented by language, department, geography or user group.

---

## 8.7.3 Data and features
> **In the build:** Stage 7, Step 3 - *"the dataset is leaking the answer."*

### 1. Definition

Feature engineering turns raw data into model inputs. Leakage occurs when a feature contains
information that would not be available at prediction time. Class imbalance occurs when one
class is much rarer than the other.

### 2. Feature engineering

| Data | Feature examples |
|---|---|
| Ticket text | length, language, embedding, keyword flags |
| Ticket metadata | category, channel, priority, department |
| Time | hour, day of week, holiday flag |
| Operations | team backlog, open ticket count, historical SLA rate |

### 3. Leakage examples

| Leaky feature | Why invalid |
|---|---|
| `resolution_time_hours` | known only after closure |
| `closed_late` | the target itself |
| `escalated_by_manager` | may happen after breach risk appears |
| future backlog | not known at prediction time |

### 4. Class imbalance controls

| Control | Use |
|---|---|
| Class weights | Penalize rare-class mistakes more |
| Resampling | oversample minority or undersample majority |
| Threshold tuning | change decision threshold after training |
| PR-AUC/F1/recall | metrics that do not hide rare-class failure |

### 5. Fails when

- Feature availability time is not documented.
- Text fields include agent notes written after the outcome.
- Resampling is applied before train/test split, leaking duplicate records.
- Data quality checks are skipped for nulls, schema changes and category drift.

---

## 8.7.10 Fairness and bias testing `+`
> **In the build:** Stage 7, Step 4 - *"accurate overall and unfair for one group."*

### Definition

Fairness testing checks whether model performance or outcomes differ materially across groups
or protected attributes. In public-sector systems, this is not optional if the model affects
access, priority, eligibility or service quality.

### Checks

| Check | Question |
|---|---|
| Performance parity | Does recall/precision differ by group? |
| Error disparity | Are false negatives higher for Arabic tickets? |
| Outcome disparity | Does one department get more high-risk flags? |
| Calibration | Does a 0.8 score mean similar risk across groups? |
| Proxy features | Is department/language acting as proxy for protected status? |

### Mitigations

- Improve data coverage for underperforming groups.
- Segment thresholds only with legal and governance review.
- Remove or transform proxy features where appropriate.
- Add human review for high-impact automated decisions.
- Monitor fairness metrics after deployment.

### Fails when

- Protected attributes are ignored entirely, making disparity unmeasurable.
- Fairness is checked once before launch and never again.
- The model is "fair" overall but fails Arabic users or low-volume groups.

---

## 8.7.9 Explainability `+`
> **In the build:** Stage 7, Step 4 - *"why was I refused?"*

### Definition

Explainability provides understandable reasons for a model's output. In classic ML, common
tools include SHAP and LIME. Explanations can be global (what drives the model generally) or
local (why this prediction happened).

### Tools

| Tool | Meaning |
|---|---|
| SHAP | Feature contribution values based on game-theoretic attribution |
| LIME | Local surrogate model around one prediction |
| Feature importance | Global ranking of influential features |
| Partial dependence | How prediction changes as one feature changes |

### Public-sector answer

For a decision affecting a person, do not say "the AI decided." Provide:

- the policy/business rule basis,
- the relevant input facts,
- the model score where appropriate,
- the main contributing factors,
- the appeal or human review path.

### Fails when

- Chain-of-thought from an LLM is treated as an audit explanation.
- Feature importance is shown without checking whether features are proxies.
- Explanations are technically correct but useless to the affected user.

---

## 8.7.11 Model cards `+`
> **In the build:** Stage 7, Step 4 - *"document the model like a governed asset."*

### Definition

A model card is structured documentation for a model: intended use, data, metrics, limitations,
risks, fairness results, deployment constraints and monitoring plan.

### Contents

| Section | Example |
|---|---|
| Intended use | Predict SLA breach risk for internal service tickets |
| Out-of-scope use | Employee performance evaluation |
| Training data | Tickets from 2024-2026, excluding post-resolution notes |
| Metrics | recall, precision, PR-AUC, calibration |
| Segments | Arabic/English, departments, channels |
| Limitations | Low confidence on rare categories |
| Human oversight | Supervisor reviews high-risk flag |
| Monitoring | drift, performance, fairness, data quality |
| Owner | Service operations analytics team |

**Fails when** - documentation is written once for approval but not updated after retraining or
model replacement.

---

## 8.7.4 Azure ML
> **In the build:** Stage 7, Step 5 - *"put the training pipeline somewhere real."*

### Definition

Azure Machine Learning provides managed infrastructure for ML development and operations:
workspaces, compute, data assets, pipelines, model registry and managed online/batch endpoints.

### Components

| Component | Use |
|---|---|
| Workspace | Boundary for assets, jobs, models, endpoints |
| Compute | CPU/GPU clusters or instances for training |
| Data asset | Versioned dataset reference |
| Pipeline | Reproducible multi-step training/evaluation workflow |
| Model registry | Versioned model artifact with metadata |
| Managed online endpoint | Real-time HTTPS scoring |
| Batch endpoint | Scheduled/offline scoring at scale |

### Example shape

```python
# Training job writes metrics and registers a model only if validation passes.
if metrics["recall"] >= 0.85 and metrics["precision"] >= 0.55:
    ml_client.models.create_or_update(Model(
        name="sla-breach-classifier",
        version=build_version,
        path="./model",
        tags={"recall": metrics["recall"], "data_version": data_version},
    ))
```

### Fails when

- Notebook output is manually copied into production.
- Data, environment and code versions are not tied to the registered model.
- Real-time and batch scoring paths use different preprocessing.

---

## 8.7.5 MLflow
> **In the build:** Stage 7, Step 5 - *"track experiments and versions."*

### Definition

MLflow tracks experiments, parameters, metrics, artifacts and model versions. It is the common
language between data science experiments and production model management.

### What to log

| Item | Example |
|---|---|
| Parameters | algorithm, max_depth, class_weight |
| Metrics | precision, recall, F1, PR-AUC |
| Artifacts | plots, confusion matrix, model file |
| Data version | dataset hash or data asset version |
| Code version | git commit |
| Environment | package versions, image |
| Model signature | expected inputs and outputs |

### Example

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

### Fails when

- Runs are logged but no model version is promoted through stages/aliases.
- The production endpoint cannot be traced back to a run.
- Reproducibility omits the data version.

---

## 8.7.6 Deployment and monitoring
> **In the build:** Stage 7, Step 6 - *"production data changes."*

### 1. Definition

ML deployment is serving a trained model for online or batch inference. Monitoring checks that
the model continues to receive valid data and produce useful predictions after launch.

### 2. Drift types

| Type | Meaning | Example |
|---|---|---|
| Data drift | Input distribution changes | new ticket categories |
| Prediction drift | Output distribution changes | many more tickets flagged high risk |
| Concept drift | relationship between features and target changes | new SLA policy changes breach logic |
| Data quality drift | nulls, invalid types, out-of-range values | category field renamed |
| Model decay | business value declines over time | recall drops as processes change |

### 3. Deployment patterns

| Pattern | Use |
|---|---|
| Blue/green | swap traffic between deployments |
| Canary | small percentage to new model |
| Shadow | score with new model but do not act |
| A/B test | compare business outcomes |
| Batch scoring | periodic large-scale predictions |

### 4. Retraining triggers

- performance below threshold when ground truth arrives,
- significant data or prediction drift,
- policy/process change,
- new labelled data volume,
- fairness metric regression,
- model or dependency deprecation.

### 5. Fails when

- Ground truth arrives late and nobody closes the loop.
- Drift alerts exist but no owner or runbook responds.
- Retraining happens automatically without validation and approval.
- Shadow deployment is skipped for high-impact models.

---

## 8.7.7 End-to-end lifecycle
> **In the build:** Stage 7, Step 7 - *"walk the JD lifecycle."*

### Definition

The AI use-case lifecycle is the controlled path from idea to supported production system:
assessment -> data prep -> build -> test -> validate -> deploy -> monitor -> support.

### The lifecycle

| Stage | What happens |
|---|---|
| Assessment | business objective, AI suitability, risk, owner, success metric |
| Data prep | source access, quality, labels, privacy, feature availability |
| Build | baseline, feature engineering, model training, experiment tracking |
| Test | offline metrics, segment metrics, leakage checks |
| Validate | SME review, fairness, explainability, security, approval |
| Deploy | registry, endpoint, canary/shadow, rollback |
| Monitor | performance, drift, data quality, fairness, cost |
| Support | incidents, retraining, model card updates, deprecation |

### Fails when

- The lifecycle starts at model training instead of business assessment.
- Monitoring is planned after deployment.
- Support ownership is unclear.

---

## 8.7.8 Telling the narrative
> **In the build:** Stage 7, Step 7 - *"tell it as one continuous story."*

### Example answer

"For SLA breach prediction, I would start with assessment: confirm the business goal is early
intervention, define success as high recall at workable precision, and complete risk and data
classification. In data prep, I would use only fields available at ticket creation, remove
post-resolution leakage, label historical breaches, split by time, and check Arabic/English
coverage. I would build a baseline logistic regression or tree model, then compare stronger
models with MLflow tracking. I would test recall, precision, PR-AUC, calibration and segment
performance. Validation would include SMEs, fairness checks, explainability and a model card.
Deployment would use Azure ML managed online or batch endpoints, with a canary or shadow run.
In production I would monitor data drift, prediction drift, delayed ground-truth performance,
fairness, latency and incidents. Support means retraining triggers, rollback, ownership and
periodic review."

### Why this works

It shows you understand the lifecycle as an operating system, not as vocabulary. It also shows
you can choose classic ML over an LLM when the task is structured prediction.

---

# Part B2 - DEEP INTERVIEW EXPANSION

This section is the slower pass. It turns the compact ML notes into the kind of explanations
you can use when the panel asks for a real project walkthrough.

## D1. Classic ML mental model

Classic ML is about learning a repeatable mapping:

```
features available now -> prediction or score -> business action
```

LLMs are usually about:

```
instructions + context -> generated text/tool proposal
```

The first question is therefore not "which model?" The first question is "what is the business
decision and what information is available at decision time?"

## D2. Problem framing - before algorithms

### Definition

Problem framing converts a business request into a machine-learning task, target, prediction
time, metric and action.

### Example

Business request:

```
"We want AI to reduce service ticket SLA breaches."
```

ML framing:

| Decision | Choice |
|---|---|
| Prediction | probability a ticket will breach SLA |
| Prediction time | at creation, then refresh every hour |
| Unit | one ticket |
| Target | breached SLA within policy window |
| Features | fields known at creation/update time |
| Metric | high recall at acceptable precision |
| Action | supervisor review or priority boost |
| Human role | supervisor decides intervention |

### Bad framings

- "Use AI to improve tickets" - no target.
- "Predict late tickets" but only after closure - no useful decision time.
- "Optimize accuracy" on rare breaches - wrong metric.
- "Automatically reprioritize all tickets" - action too risky without validation.

## D3. Train, validation and test - what each is for

### Definition

The split protects the estimate of future performance:

| Split | Used for |
|---|---|
| Training | fit model parameters |
| Validation | tune features, thresholds and hyperparameters |
| Test | final unbiased estimate before release |

### Time-based split

For operational data, split by time more often than by random rows:

```
Train: Jan 2024 - Dec 2025
Validation: Jan 2026 - Mar 2026
Test: Apr 2026 - Jun 2026
```

Random splits can leak future policies, categories and operational patterns into training.

### Cross-validation

Cross-validation is useful when data is limited and independent. For time-series or evolving
operations, use time-aware cross-validation or rolling windows.

### What breaks

- The test set is used repeatedly until the model looks good.
- Duplicates appear in train and test.
- Future data leaks through random split.
- Preprocessing is fit on all data before splitting.

## D4. Metrics - confusion matrix first

### Confusion matrix

For SLA breach prediction:

| | Actual breach | Actual no breach |
|---|---|---|
| Predicted breach | true positive | false positive |
| Predicted no breach | false negative | true negative |

Business meaning:

- **False negative:** a ticket will breach but nobody intervenes.
- **False positive:** staff review a ticket that would have been fine.

If false negatives are more costly, optimize recall first. If staff capacity is limited, set a
precision floor.

### Classification metrics

| Metric | Formula idea | Interview use |
|---|---|---|
| Precision | TP / predicted positives | "Of flagged tickets, how many really breach?" |
| Recall | TP / actual positives | "Of real breaches, how many did we catch?" |
| F1 | harmonic mean of precision/recall | balance when both matter |
| ROC-AUC | ranking positive over negative | broad ranking measure |
| PR-AUC | precision-recall curve | better for rare positives |
| Calibration | predicted 0.8 means about 80% risk | needed for risk scores |

### Threshold tuning

Most classifiers output a probability. The threshold turns it into an action.

```
threshold 0.30 -> high recall, many false positives
threshold 0.70 -> high precision, misses more breaches
```

Pick threshold from operational capacity and risk tolerance, not from the default 0.5.

### Regression metrics

For forecasting service volume:

| Metric | Meaning | Use |
|---|---|---|
| MAE | average absolute error | easiest to explain |
| RMSE | punishes large misses | capacity planning |
| MAPE | percent error | avoid near zero |
| Pinball loss | quantile forecast error | staffing for worst-case |

### What breaks

- Accuracy hides rare-class failure.
- ROC-AUC looks good but precision at the operating threshold is poor.
- A model is well-ranked but poorly calibrated, so scores are misused.

## D5. Data and feature engineering - the real work

### Feature availability

Every feature needs an "available at" timestamp:

| Feature | Available when? | Valid for creation-time prediction? |
|---|---|---|
| category | ticket creation | yes |
| priority | ticket creation | yes, if set before scoring |
| assigned team backlog | scoring time | yes |
| resolution notes | after closure | no |
| escalation flag | maybe later | only if refresh-time model |
| final resolution time | after closure | no |

### Preprocessing pipeline

```python
numeric = ["team_backlog", "requester_open_tickets", "text_length"]
categorical = ["category", "channel", "department", "language"]

preprocess = ColumnTransformer([
    ("num", StandardScaler(), numeric),
    ("cat", OneHotEncoder(handle_unknown="ignore"), categorical),
])

model = Pipeline([
    ("preprocess", preprocess),
    ("classifier", LogisticRegression(class_weight="balanced")),
])
```

Putting preprocessing in the pipeline prevents train/serving skew and ensures validation uses
the same transformations as production.

### Leakage checklist

- Was the field created after prediction time?
- Was it edited by a human who already knew the outcome?
- Is it a proxy for the target?
- Was preprocessing fit on all data before split?
- Are duplicates or near-duplicates crossing splits?
- Does the target definition use future policy not known at the time?

### Imbalance handling

For rare events, start with:

1. stratified/time-aware split,
2. class weights,
3. PR-AUC and recall/precision at threshold,
4. threshold tuning,
5. calibrated probabilities,
6. resampling only inside training folds.

### What breaks

- Oversampling before split duplicates minority examples into test.
- Category encoding fails when a new department appears.
- Training features are richer than production features.

## D6. Algorithms - enough to choose sensibly

You do not need to list every algorithm. You need to know the common trade-offs.

| Algorithm | Strength | Weakness |
|---|---|---|
| Logistic regression | fast, interpretable baseline | linear boundaries |
| Decision tree | explainable rules | overfits easily |
| Random forest | strong tabular baseline | less interpretable, larger |
| Gradient boosting | often best for tabular data | tuning and monitoring complexity |
| SVM | good on smaller high-dimensional data | scaling, calibration |
| k-means | simple clustering | assumes cluster shape/count |
| Isolation Forest | anomaly detection | threshold selection |
| ARIMA/Prophet | time series baseline | limited complex feature handling |
| Neural nets | high capacity | more data/ops/explainability burden |

### Interview rule

Start with a simple baseline. If a complex model wins, ship it only if the measured gain is
worth the cost in explainability, monitoring and operations.

## D7. Fairness and bias - public-sector depth

### Definition

Fairness testing asks whether the model performs differently across groups and whether those
differences create unacceptable outcomes.

### Example

The SLA model has 0.86 recall overall, but:

| Segment | Recall |
|---|---|
| English tickets | 0.90 |
| Arabic tickets | 0.68 |
| Web channel | 0.88 |
| Phone-transcribed tickets | 0.63 |

The average is not deployable because service quality is worse for Arabic and transcribed
cases.

### Metrics

| Metric | Meaning |
|---|---|
| Demographic parity | similar positive prediction rates |
| Equal opportunity | similar true positive rates/recall |
| Equalized odds | similar true/false positive rates |
| Calibration by group | same score means same risk |
| Disparate impact ratio | outcome rate comparison |

No metric is universally "the fairness metric." Choose based on the decision and legal/policy
context.

### Mitigations

- improve labels/data for weak segments,
- add language-specific features or models if justified,
- calibrate by segment where permitted,
- add human review before adverse actions,
- monitor after deployment,
- document residual risk in the model card.

### What breaks

- The team avoids collecting protected/segment attributes and therefore cannot measure harm.
- Fairness is measured only on training data.
- A proxy feature recreates a removed protected attribute.
- Overall gain is used to justify segment regression.

## D8. Explainability - what to show and to whom

### Definition

Explainability translates model behavior into reasons humans can inspect. It has different
audiences:

| Audience | Needs |
|---|---|
| Data scientist | debug features and model behavior |
| Operator | know why a ticket was flagged |
| Affected user | understandable reason and appeal path |
| Auditor | evidence of control and consistency |

### Global vs local

| Type | Question |
|---|---|
| Global | What generally drives the model? |
| Local | Why did this ticket get this score? |

### SHAP vs LIME

| Tool | How to explain |
|---|---|
| SHAP | attributes prediction to features using contribution values |
| LIME | fits a simple local surrogate around one prediction |

### Example local explanation

```
Ticket risk score: 0.82
Main factors:
  + current team backlog high
  + category historically breaches SLA often
  + ticket created before weekend
  - priority marked normal

Action: supervisor review, not automatic penalty.
```

### What breaks

- Explanation is used as proof of causality when it is only attribution.
- LLM chain-of-thought is presented as model explainability.
- Explanations expose sensitive features to unauthorized users.
- Operators get scores without guidance on action.

## D9. Model cards and documentation

### Definition

A model card is the controlled record of what the model is for, how it was built, how it was
validated and how it should be monitored.

### Full model card outline

```
1. Model name, version and owner
2. Intended use and users
3. Out-of-scope use
4. Data sources and time period
5. Label definition
6. Feature availability and leakage controls
7. Train/validation/test split
8. Metrics overall and by segment
9. Fairness and bias findings
10. Explainability method
11. Human oversight and appeal
12. Deployment endpoint and dependencies
13. Monitoring plan
14. Retraining triggers
15. Known limitations
16. Approval record
```

### What breaks

- Nobody knows whether the model may be used for a new purpose.
- A retrained model keeps the old documentation.
- Metrics are reported without segment or threshold details.

## D10. Azure ML production path

### Definition

Azure ML gives a managed path from experiment to endpoint. The important interview point is the
asset lineage:

```
code version + data version + environment + parameters
  -> training job
  -> metrics/artifacts
  -> registered model
  -> endpoint deployment
  -> monitored production predictions
```

### Architecture

```
Azure ML workspace
  data assets
  compute cluster
  training pipeline
  MLflow tracking
  model registry
  managed online endpoint
  batch endpoint
  monitoring
```

### Online vs batch

| Endpoint | Use |
|---|---|
| Managed online | score one ticket in real time |
| Batch endpoint | score all open tickets hourly/nightly |

### Deployment example

```python
# Shape only: register and deploy a model with explicit versioning.
model = ml_client.models.create_or_update(Model(
    name="sla-breach-classifier",
    version="2026-08-17",
    path="./outputs/model",
    tags={
        "data_version": "tickets-2026q2",
        "recall": "0.87",
        "precision": "0.61",
    },
))

deployment = ManagedOnlineDeployment(
    name="blue",
    endpoint_name="sla-risk",
    model=model,
    instance_type="Standard_DS3_v2",
    instance_count=2,
)
```

### What breaks

- Training notebook cannot be reproduced.
- Production preprocessing differs from training preprocessing.
- Endpoint uses "latest" model instead of pinned version.
- Batch and online paths drift apart.

## D11. MLflow - experiment tracking and reproducibility

### Definition

MLflow records the evidence behind a model: parameters, metrics, artifacts, code, data version,
environment and model artifact.

### Good run record

| Field | Example |
|---|---|
| run_id | `b1f...` |
| git_commit | app/training code version |
| data_version | `tickets-2026q2-v3` |
| params | model type, hyperparameters |
| metrics | recall, precision, PR-AUC |
| artifacts | confusion matrix, calibration plot |
| model signature | input schema and output schema |
| environment | package/image version |

### Promotion

```
experiment run -> candidate model -> validation approval -> production alias
```

Use aliases or deployment config to know exactly which version is live.

### What breaks

- MLflow logs exist but production endpoint cannot be linked to a run.
- The model artifact is reproducible but the dataset is not.
- Metrics are logged without the threshold used for classification.

## D12. Deployment and monitoring - drift and decay

### Definition

Monitoring answers whether the model is still receiving the data it was trained for and still
producing useful predictions.

### Drift types

| Drift | Example | Detection |
|---|---|---|
| Schema drift | column renamed or missing | schema validation |
| Data drift | category distribution changes | distribution distance, PSI |
| Prediction drift | risk scores shift | output distribution |
| Concept drift | features no longer predict target | delayed ground truth performance |
| Label drift | target definition changes | policy/process review |
| Fairness drift | one segment worsens | segment metrics |

### Monitoring loop

```
log prediction -> wait for outcome -> join label -> compute performance
              -> compare to baseline -> alert -> investigate -> retrain or rollback
```

### Retraining is not automatic shipping

Retraining can be automated. Promotion should still require validation gates:

- data checks passed,
- metrics passed,
- fairness did not regress,
- explainability reviewed if high impact,
- model card updated,
- deployment canary/shadow completed.

### What breaks

- Drift alert fires but no one owns it.
- No ground-truth join, so performance is never known.
- New model is trained on poisoned or broken recent data.
- Monitoring only checks infrastructure, not model behavior.

## D13. End-to-end lifecycle - one defensible answer

Use this structure when asked to "walk us through an AI use case."

### 1. Assessment

Clarify the decision, impact, users, risk, metric, data availability and whether AI is needed.
For SLA breach prediction, AI is justified only if earlier intervention changes outcomes.

### 2. Data prep

Collect historical tickets, define breach labels, remove leakage, document feature timing,
handle missing values, encode categories, process text, split by time and check segments.

### 3. Build

Create a baseline, train candidate models, track with MLflow, use pipelines for preprocessing
and model training, and compare against business metrics.

### 4. Test

Evaluate on validation/test sets: recall, precision, PR-AUC, calibration, segment metrics,
confusion matrix and operational capacity.

### 5. Validate

SMEs review errors, security/privacy reviews data use, fairness is checked, explanations are
validated, model card is completed and governance approval is obtained.

### 6. Deploy

Register the model, deploy to Azure ML online or batch endpoint, pin versions, canary/shadow,
define rollback and connect application telemetry.

### 7. Monitor

Track latency, errors, input schema, drift, prediction distribution, delayed performance,
fairness, business outcomes and support tickets.

### 8. Support

Operate runbooks, incident triage, retraining, model card updates, deprecation handling and
periodic risk review.

### Short interview version

"I start with the decision and metric, not the algorithm. I build from time-valid data, prevent
leakage, choose metrics that match error cost, track experiments and data versions, validate
fairness and explainability, deploy a pinned model through Azure ML, monitor drift and delayed
ground truth, and feed incidents into retraining and governance review."

## D14. How classic ML connects to the GenAI system

Classic ML can be one tool inside the agentic assistant:

```
User asks: "Which open tickets need attention?"
Assistant:
  1. queries open tickets
  2. calls SLA risk classifier endpoint
  3. summarizes top risks with explanations
  4. creates draft follow-up actions
  5. requires human approval before changing priority
```

The classifier is governed by Stage 7. The assistant wrapping it is governed by Stages 1-6.

### Combined failure mode

The LLM may overstate what the classifier means. A risk score is not a decision. The final
answer must preserve uncertainty, cite the model version where needed, and route high-impact
actions to a human.

---

# Part C - Stage 7 assembled

## C1. Classic ML vs LLM decision

| Need | Better first choice |
|---|---|
| Predict SLA breach | Classic ML classifier |
| Forecast call volume | Time-series/regression model |
| Detect anomalous claims | Anomaly detection |
| Answer policy question with citations | RAG |
| Summarize a ticket | LLM |
| Extract fields from free text | LLM or NLP extractor, then structured workflow |
| Route tickets by category | Small classifier or small LLM, evaluated by cost/quality |

## C2. One model, end to end

```
USE CASE: predict service tickets likely to breach SLA.

1. Assessment: define intervention goal and metric             [8.7.7]
2. Data prep: labels, feature timing, leakage checks           [8.7.3]
3. Build: baseline + candidate models, tracked in MLflow       [8.7.5]
4. Test: recall, precision, PR-AUC, segment metrics            [8.7.2 / 8.7.10]
5. Validate: SME review, SHAP explanations, model card         [8.7.9 / 8.7.11]
6. Deploy: Azure ML endpoint or batch job                      [8.7.4]
7. Monitor: drift, performance, fairness, data quality         [8.7.6]
8. Support: retraining, incident review, deprecation           [8.7.7]
```

## C3. How it connects back to the GenAI system

Classic ML models can be tools inside the agentic architecture. The HR assistant may call an
SLA-risk endpoint just like it calls a leave-balance tool. The same rules still apply: scoped
permission, versioned model, telemetry, drift monitoring, audit and human oversight for
high-impact decisions.

## C4. Self-test

1. Supervised vs unsupervised: give one government example of each.
2. Why is accuracy dangerous on imbalanced data?
3. Precision vs recall: which matters more for SLA breach prediction and why?
4. Give three examples of feature leakage.
5. What is concept drift, and how is it different from data drift?
6. What should be in a model card?
7. How do SHAP and LIME differ?
8. What does MLflow log that makes a model reproducible?
9. Azure ML online endpoint vs batch endpoint: when use each?
10. Walk assessment -> support for one real use case.

---

*End of Stage 7. Return to `00-MAP.md` for the complete architecture.*
