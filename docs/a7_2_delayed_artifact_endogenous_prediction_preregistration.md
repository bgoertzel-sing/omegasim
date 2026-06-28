# A7.2 Delayed Artifact-Mediated Endogenous Prediction Preregistration

Date: 2026-06-28.

Status: active preregistered implementation/smoke gate after Ben's 2026-06-28
A7.2-then-three-hive instruction.

This document freezes the A7.2 single-hive contract before any A7.2 simulator
mechanics or result-bearing runs. It supersedes neither the A5-family closure
evidence boundary nor the completed A7 long-horizon null validation. It
authorizes only a bounded implementation gate and tiny deterministic smoke
after the schema, configs, and tests match the contract below.

## Scientific Question

Does delayed, artifact-mediated, resource-bounded endogenous prediction create
residual prediction/artifact structure that survives full accounting and strong
null controls?

A positive A7.2 result would mean that an intermediate endogenous-prediction
condition beats all preregistered nulls on residual endpoints while preserving
productivity guardrails. Forecast skill, backlog changes, action-count shifts,
or raw semantic/artifact oscillations are insufficient.

## Scope Locks

Allowed in this gate:

- single-hive A7.2 mechanics only;
- deterministic paired seeds;
- frozen equations, costs, thresholds, delays, caps, schemas, configs, and
  analyzers before result interpretation;
- tiny smoke execution only after implementation contract tests pass.

Disallowed in this gate:

- broad seed sweeps or parameter sweeps;
- downstream multi-hive or three-hive coupling;
- real LLM, Lean, Slack, browser, Atomspace, dashboard, live task-board, or
  external notification integrations;
- promotion language about lobes, attractors, semantic dynamics, synchrony, or
  causal collective structure.

## State Vector

A7.2 records per tick and, where relevant, per agent:

```text
forecast_error_lag1
forecast_uncertainty_lag1
prediction_spend
lost_work_opportunity_from_prediction
fatigue
adaptive_prediction_threshold
adaptive_work_threshold
adaptive_review_threshold
adaptive_synthesis_threshold
artifact_readiness
artifact_coherence
artifact_contradiction
artifact_risk
artifact_revision_pressure
selected_action
predict_utility
work_utility
review_utility
synthesize_utility
delayed_forecast_update_queue
delayed_artifact_update_queue
source_ledger_forecast_error
source_ledger_artifact
source_ledger_queue_accounting
```

Queue, service, action-opportunity, work-budget, backlog, queued-age,
completion, starvation, and clock/demand-phase fields remain accounting
controls, not target evidence.

## Frozen Parameters

The first smoke uses:

```text
seeds: 1, 2
horizon_ticks: 48
forecast_delay_ticks: 2
artifact_delay_ticks: 3
prediction_cost_work_fraction: 0.25
max_prediction_work_fraction_per_tick: 0.40
fatigue_decay: 0.20
fatigue_increment_predict: 0.08
fatigue_increment_work: 0.05
fatigue_increment_review: 0.04
fatigue_increment_synthesize: 0.06
threshold_learning_rate_error: 0.05
threshold_recovery_rate: 0.02
threshold_min: -2.0
threshold_max: 2.0
utility_slope_predict: 1.20
utility_slope_work: 1.00
utility_slope_review: 1.10
utility_slope_synthesize: 1.15
artifact_clip_min: 0.0
artifact_clip_max: 1.0
artifact_decay: 0.10
```

These values are intentionally modest smoke constants. They may not be tuned
after inspecting A7.2 residual plots. If they are inadequate, close or write a
new preregistration before changing interpreted parameters.

## Action Utilities

Agents choose one action per opportunity from:

```text
predict
work
review
synthesize
```

All interpreted utilities use lagged or delayed inputs only:

```text
U_predict(t) =
  1.20 * sigmoid(forecast_error_lag1(t) + forecast_uncertainty_lag1(t)
                 + artifact_revision_pressure(t-1)
                 - adaptive_prediction_threshold(t)
                 - fatigue(t))

U_work(t) =
  1.00 * sigmoid(backlog_pressure_lag1(t)
                 + artifact_readiness(t-1)
                 - adaptive_work_threshold(t)
                 - fatigue(t))

U_review(t) =
  1.10 * sigmoid(artifact_contradiction(t-1) + artifact_risk(t-1)
                 - adaptive_review_threshold(t)
                 - fatigue(t))

U_synthesize(t) =
  1.15 * sigmoid(artifact_readiness(t-1) + artifact_coherence(t-1)
                 - artifact_contradiction(t-1)
                 - adaptive_synthesis_threshold(t)
                 - fatigue(t))
```

Selection is deterministic for a fixed seed by using the preregistered action
RNG stream to sample from normalized positive utilities. Same-tick A7.2 access
is allowed only in the explicit same-tick logistic control.

## Delay And Accounting Rules

Prediction is charged against work opportunity before it can help future work:

```text
prediction_work_cost(t) =
  min(prediction_cost_work_fraction * prediction_spend(t),
      max_prediction_work_fraction_per_tick * work_opportunity(t))
```

The charged cost reduces available work opportunity on the same tick. Forecast
updates produced by `predict` enter `delayed_forecast_update_queue` and become
visible after `forecast_delay_ticks`. Artifact updates produced by `review` or
`synthesize` enter `delayed_artifact_update_queue` and become visible after
`artifact_delay_ticks`.

No forecast or artifact update may affect an action utility on the tick that
created it in the positive condition.

## Artifact Updates

Artifact state is updated from delayed source components:

```text
artifact_readiness(t+1) =
  clip((1 - artifact_decay) * artifact_readiness(t)
       + delayed_synthesis_gain(t)
       + delayed_review_acceptance(t)
       - delayed_contradiction_penalty(t))

artifact_coherence(t+1) =
  clip((1 - artifact_decay) * artifact_coherence(t)
       + delayed_synthesis_gain(t)
       - delayed_risk_penalty(t))

artifact_contradiction(t+1) =
  clip((1 - artifact_decay) * artifact_contradiction(t)
       + delayed_review_discovery(t)
       + delayed_forecast_error_signal(t)
       - delayed_synthesis_resolution(t))

artifact_risk(t+1) =
  clip((1 - artifact_decay) * artifact_risk(t)
       + delayed_contradiction_penalty(t)
       - delayed_review_acceptance(t))

artifact_revision_pressure(t+1) =
  clip(artifact_contradiction(t+1) + artifact_risk(t+1)
       - artifact_readiness(t+1))
```

Every non-decay term must be written into a source ledger. The analyzer must
fail closed if artifact deltas cannot be reconstructed from source-ledger
components plus clipping residuals.

## Conditions

The first smoke must include these conditions with paired seeds and matched
base demand/service/opportunity streams:

```text
zero_budget_reactive
intermediate_endogenous_delayed_prediction
high_budget_oracle_smoothing
amplitude_matched_linear_delayed_prediction
same_tick_logistic_prediction
phase_shuffled_lag_input
threshold_shuffled
source_preserving_artifact_label_shuffle
spend_only_replay
artifact_off_source_ledger_null
```

`intermediate_endogenous_delayed_prediction` is the only candidate positive
condition. `high_budget_oracle_smoothing` is a positive control, not a
promotion target. `spend_only_replay` deducts identical prediction/work
opportunities at identical ticks while removing useful forecast timing.
`artifact_off_source_ledger_null` is required because artifact variables could
otherwise become relabeled queue/action accounting.

## Primary Endpoints

Primary endpoints are:

```text
forecast_skill_per_prediction_spend
full_accounting_residual_lag1_predictability
nearest_neighbor_residual_forecast_error
delay_embedding_recurrence_score
residual_transition_compressibility
lead_lag_mediation_error_to_spend_to_artifact_to_residual
source_ledger_reconstruction_status
```

Residual endpoints must control for:

```text
tick
demand_phase
task_arrivals
service_capacity
action_opportunity
work_budget
prediction_spend
remaining_work_budget
backlog
queued_age
completion_fraction
starvation
prediction_spend_volatility
work_budget_volatility
source_ledger_queue_accounting
```

## Productivity Guardrails

The candidate positive condition is ineligible for promotion if, relative to
paired null controls, it shows:

```text
completion_fraction_delta < -0.05
backlog_delta > 0.10
queued_age_delta > 0.10
starvation_delta > 0.03
prediction_spend_volatility_delta > 0.15
work_budget_volatility_delta > 0.15
```

These are smoke guardrails, not optimization targets.

## Closure Rules

Close A7.2 fail-closed if any of these hold:

- required schema, source-ledger, paired-seed, or null artifacts are missing;
- residualization cannot compute for all primary target fields;
- the candidate positive condition fails to beat any required null on the same
  residual endpoint and paired seed;
- paired seed signs disagree on the primary residual endpoints;
- productivity guardrails fail;
- residual effects are explained by source-ledger queue accounting, backlog
  dwell, spend-only timing, same-tick leakage, or artifact-off controls.

Do not tune slopes, delays, costs, caps, thresholds, source-ledger definitions,
or endpoint definitions after seeing A7.2 results. If A7.2 closes positive or
negative, the next phase is a separate three-hive ring preregistration, not
immediate multi-hive implementation.

## First Implementation Step

Implement only config/schema contract support for the conditions and fields
above, with deterministic tests that prove:

```text
all A7.2 configs load
all condition names are normalized
all required metric/event/source-ledger fields are declared
positive condition forbids same-tick forecast/artifact feedback
spend-only replay preserves prediction-work deductions
artifact-off null preserves queue/accounting controls
```

After those tests pass, run only the tiny paired smoke described here and the
read-only analyzer. Stop after updating `AUTOMATION_STATUS.md` and tracked
results.
