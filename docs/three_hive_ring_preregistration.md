# Three-Hive Ring Preregistration

Date: 2026-06-28.

Status: frozen design preregistration for the post-A7.2 three-hive ring gate.
This document authorizes only a later contract/config-validation step after
this preregistration is committed. It does not authorize simulator mechanics,
result-bearing runs, broad seed sweeps, dashboards, or external integrations.

## Background

A5, A5.1, A6.2, A7, and A7.2 all closed conservatively. A7.2 exercised delayed
artifact-mediated endogenous prediction in one hive and emitted useful
schema/source-ledger artifacts, but the fixed paired-seed smoke failed the
residual/null promotion gate. No lobe-like, strange-attractor-like,
semantic-dynamics, synchrony, or causal collective-structure claim is carried
forward.

Ben's 2026-06-28 direction opens the next family after A7.2: a separate
three-hive ring. The ring is not framed as evidence that complex dynamics
require multiple hives. It is a relational diagnostic amplifier: three biased
hives create cleaner source attribution, target nulls, phase nulls, delayed
cross-hive mediation tests, and transfer-opportunity controls than a single
self-modulating hive can provide at smoke scale.

## Scientific Question

Does delayed, resource-bounded artifact transfer among three biased hives
produce residual cross-hive artifact/motif structure that survives target,
phase, transfer-opportunity, spend, source-ledger, and productivity controls?

The positive target is not global synchrony and not better throughput alone.
The target is phase-differentiated residual artifact grammar: recurring
lead-lag motifs in which exploration/research, formalization/implementation,
and synthesis/review hives transform each other's delayed artifact state after
accounting for queue load, transfer volume, transfer opportunity, prediction
spend, action opportunity, and service capacity.

## Scope Locks

Allowed after this preregistration:

- one isolated three-hive ring contract/constants file;
- config validation for the frozen conditions below;
- deterministic schema tests proving contracts and fixtures load;
- only later, a tiny fixed-seed smoke if the contract/config gate passes.

Disallowed in this gate:

- real LLM calls, Lean, Slack, browser, Atomspace, dashboards, live task boards,
  or notification integrations;
- implementation of multi-hive mechanics in the preregistration pass;
- broad seed sweeps, parameter sweeps, tuning, or result-rescue changes;
- downstream hives beyond the frozen three-hive ring;
- promotion language from raw backlog, throughput, transfer counts, action
  counts, or synchrony.

## Hives And Ring Topology

The ring has exactly three hives:

```text
hive_a_explore_research
hive_b_formalize_implement
hive_c_synthesize_review
```

Directed artifact transfer follows a ring:

```text
A -> B -> C -> A
```

Each hive has the same abstract action set:

```text
predict_cross_hive
work_local
review_inbound_artifact
synthesize_outbound_artifact
idle
```

Hive role bias changes utility weights, not available actions:

```text
A: novelty/exploration and contradiction discovery weighted higher
B: readiness/formalization and implementation progress weighted higher
C: coherence/review/risk resolution and synthesis weighted higher
```

## State Vector

Per hive, per tick:

```text
local_backlog
local_queued_age
local_service_capacity
local_action_opportunity
local_work_budget
local_prediction_spend
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
inbound_artifact_readiness_lag
inbound_artifact_coherence_lag
inbound_artifact_contradiction_lag
inbound_artifact_risk_lag
cross_hive_forecast_error_lag
cross_hive_forecast_uncertainty_lag
transfer_opportunity
accepted_transfer_count
rejected_transfer_count
selected_action
```

Per directed edge, per tick:

```text
source_hive
target_hive
proposed_transfer_volume
accepted_transfer_volume
transfer_opportunity
transfer_delay_ticks
membrane_acceptance
cross_hive_prediction_spend
cross_hive_prediction_error
artifact_payload_readiness
artifact_payload_coherence
artifact_payload_contradiction
artifact_payload_risk
source_ledger_transfer
source_ledger_prediction
source_ledger_queue_accounting
source_ledger_artifact_delta
```

Queue, action, transfer-opportunity, prediction-spend, service, and clock
fields are accounting controls. They are not evidence endpoints by themselves.

## Frozen Smoke Parameters

The first smoke, if implemented after a separate contract/config gate, uses:

```text
seeds: 1, 2
horizon_ticks: 72
ring_hives: 3
ring_edges: A_to_B, B_to_C, C_to_A
observation_delay_ticks: 1
transfer_delay_ticks: 3
forecast_delay_ticks: 2
artifact_relaxation_time_ticks: 6
artifact_decay: 0.12
prediction_cost_work_fraction: 0.25
max_prediction_work_fraction_per_tick: 0.35
transfer_cost_work_fraction: 0.15
max_transfer_work_fraction_per_tick: 0.25
fatigue_decay: 0.18
fatigue_increment_predict: 0.08
fatigue_increment_work: 0.05
fatigue_increment_review: 0.04
fatigue_increment_synthesize: 0.06
threshold_learning_rate_error: 0.05
threshold_recovery_rate: 0.02
threshold_min: -2.0
threshold_max: 2.0
utility_slope_cross_predict: 1.15
utility_slope_work: 1.00
utility_slope_review: 1.10
utility_slope_synthesize: 1.15
membrane_permeability: 0.55
artifact_clip_min: 0.0
artifact_clip_max: 1.0
```

These are smoke constants, not optimized values. If they fail, the correct
outcome is fail-closed or a new preregistration, not post-result tuning.

Dimensionless values recorded in manifest:

```text
coupling_gain = utility_slope_cross_predict * membrane_permeability
delay_relaxation_ratio = transfer_delay_ticks / artifact_relaxation_time_ticks
prediction_cost_ratio = prediction_cost_work_fraction
transfer_cost_ratio = transfer_cost_work_fraction
memory_persistence = 1 - artifact_decay
threshold_adaptation_ratio = threshold_learning_rate_error / threshold_recovery_rate
```

## Utility Equations

All interpreted utilities use lagged or delayed inputs only:

```text
U_predict_cross_hive(t, h) =
  utility_slope_cross_predict *
  sigmoid(cross_hive_forecast_error_lag(t, h)
          + cross_hive_forecast_uncertainty_lag(t, h)
          + inbound_artifact_contradiction_lag(t, h)
          + inbound_artifact_risk_lag(t, h)
          - adaptive_prediction_threshold(t, h)
          - fatigue(t, h))

U_work_local(t, h) =
  utility_slope_work *
  sigmoid(local_backlog_lag(t, h)
          + artifact_readiness(t - 1, h)
          - adaptive_work_threshold(t, h)
          - fatigue(t, h))

U_review_inbound_artifact(t, h) =
  utility_slope_review *
  sigmoid(inbound_artifact_contradiction_lag(t, h)
          + inbound_artifact_risk_lag(t, h)
          - adaptive_review_threshold(t, h)
          - fatigue(t, h))

U_synthesize_outbound_artifact(t, h) =
  utility_slope_synthesize *
  sigmoid(artifact_readiness(t - 1, h)
          + artifact_coherence(t - 1, h)
          + inbound_artifact_readiness_lag(t, h)
          - artifact_contradiction(t - 1, h)
          - adaptive_synthesis_threshold(t, h)
          - fatigue(t, h))
```

Role bias multiplies the relevant terms before normalization but does not
change the control fields required for analysis. Same-tick cross-hive access is
allowed only in the explicit same-tick control.

## Transfer And Accounting Rules

Cross-hive prediction and transfer both consume scarce work opportunity:

```text
prediction_work_cost(t, h) =
  min(prediction_cost_work_fraction * cross_hive_prediction_spend(t, h),
      max_prediction_work_fraction_per_tick * local_work_budget(t, h))

transfer_work_cost(t, edge) =
  min(transfer_cost_work_fraction * proposed_transfer_volume(t, edge),
      max_transfer_work_fraction_per_tick * local_work_budget(t, source_hive))
```

Costs are deducted on the tick where prediction or transfer is attempted.
Forecast updates become visible after `forecast_delay_ticks`. Artifact payloads
become visible to the target only after `transfer_delay_ticks`. No payload may
affect the target hive utility on the same tick that produced or transferred it
in the positive condition.

Transfer acceptance is gated by a membrane function:

```text
membrane_acceptance =
  sigmoid(membrane_permeability
          + target_review_capacity_lag
          + source_artifact_coherence_lag
          - source_artifact_risk_lag
          - target_fatigue)
```

The analyzer must reconstruct accepted/rejected transfer volume and artifact
deltas from source-ledger fields. Missing or inconsistent ledgers fail closed.

## Artifact Update Equations

Per hive:

```text
artifact_readiness(t+1) =
  clip((1 - artifact_decay) * artifact_readiness(t)
       + delayed_local_work_gain(t)
       + delayed_inbound_readiness_gain(t)
       + delayed_synthesis_gain(t)
       - delayed_contradiction_penalty(t))

artifact_coherence(t+1) =
  clip((1 - artifact_decay) * artifact_coherence(t)
       + delayed_synthesis_gain(t)
       + delayed_review_acceptance(t)
       - delayed_risk_penalty(t))

artifact_contradiction(t+1) =
  clip((1 - artifact_decay) * artifact_contradiction(t)
       + delayed_inbound_contradiction_signal(t)
       + delayed_review_discovery(t)
       + delayed_cross_hive_forecast_error_signal(t)
       - delayed_synthesis_resolution(t))

artifact_risk(t+1) =
  clip((1 - artifact_decay) * artifact_risk(t)
       + delayed_inbound_risk_signal(t)
       + delayed_contradiction_penalty(t)
       - delayed_review_acceptance(t))

artifact_revision_pressure(t+1) =
  clip(artifact_contradiction(t+1) + artifact_risk(t+1)
       - artifact_readiness(t+1))
```

Every non-decay term must have a source-ledger component. Clipping residuals
must be recorded separately.

## Conditions

The first smoke must include these paired-seed conditions with matched demand,
service, action-opportunity, work-budget, role-bias, and noise streams:

```text
no_coupling
delayed_logistic_ring
heterogeneous_delay_logistic_ring
amplitude_matched_linear_delayed_ring
same_tick_logistic_ring
target_shuffled_transfer
phase_shuffled_transfer
threshold_shuffled_ring
transfer_opportunity_matched_replay
spend_only_cross_hive_prediction_replay
artifact_off_source_ledger_null
source_preserving_artifact_label_shuffle
high_budget_oracle_smoothing
```

`delayed_logistic_ring` is the primary positive candidate.
`heterogeneous_delay_logistic_ring` is a robustness candidate, not a rescue
target. `high_budget_oracle_smoothing` is a positive control, not a promotion
target. `transfer_opportunity_matched_replay` preserves when transfer could
have occurred and how much could have moved while removing functional target
content. `spend_only_cross_hive_prediction_replay` deducts the same prediction
costs at the same ticks while removing useful forecast timing.

## Primary Endpoints

Primary endpoints:

```text
residual_cross_hive_delay_embedding_recurrence
residual_phase_differentiated_motif_score
lead_lag_mediation_neighbor_artifact_to_local_action_to_local_artifact
residual_target_predictability_from_lagged_neighbor_artifact
residual_transition_compressibility
source_ledger_reconstruction_status
productivity_guardrail_status
```

Required residual controls:

```text
tick
demand_phase
local_task_arrivals
local_service_capacity
local_action_opportunity
local_work_budget
local_backlog
local_queued_age
local_prediction_spend
lost_work_opportunity_from_prediction
proposed_transfer_volume
accepted_transfer_volume
transfer_opportunity
transfer_work_cost
role_bias
source_hive
target_hive
```

Promotion requires `delayed_logistic_ring` to beat all preregistered nulls on
the residual endpoints with paired-seed directional agreement, while passing
source-ledger and productivity guardrails. Better forecast skill, better queue
regulation, higher transfer volume, or stronger synchrony is insufficient.

## Productivity Guardrails

Fail closed if any positive candidate has:

```text
mean_completion_fraction < 0.80 * no_coupling_mean_completion_fraction
mean_backlog > 1.25 * no_coupling_mean_backlog
mean_queued_age > 1.25 * no_coupling_mean_queued_age
prediction_or_transfer_cost_fraction > 0.45
accepted_transfer_volume == 0 for any directed edge
source_ledger_reconstruction_status != pass
```

These guardrails prevent interpreting productivity collapse, zero transfer, or
accounting leakage as phase-differentiated dynamics.

## Closure Rules

Close positive only if all are true:

```text
source ledgers pass for every condition and seed
delayed_logistic_ring beats no_coupling on residual motif/recurrent endpoints
delayed_logistic_ring beats target_shuffled_transfer
delayed_logistic_ring beats phase_shuffled_transfer
delayed_logistic_ring beats transfer_opportunity_matched_replay
delayed_logistic_ring beats spend_only_cross_hive_prediction_replay
delayed_logistic_ring beats artifact_off_source_ledger_null
delayed_logistic_ring beats amplitude_matched_linear_delayed_ring
delayed_logistic_ring beats same_tick_logistic_ring
paired seeds agree on direction for primary residual endpoints
all productivity guardrails pass
```

Otherwise close fail-closed. A fail-closed result still supports the harness if
schemas and ledgers pass, but it does not support lobe-like,
strange-attractor-like, synchrony, semantic-dynamics, or causal
collective-structure claims.

## Next Authorized Step

The contract-only, config-validation, schema/source-ledger smoke, and read-only
preflight gates are complete. The current preflight analyzer inspects fixed
seed `1,2` schema/source-ledger artifacts for every preregistered condition and
fails closed as `fail_closed_no_metrics_events` until real simulator
metrics/events exist. It does not run the simulator, compute promotion
endpoints, or create three-hive scientific evidence.

The next authorized step is the smallest real three-hive mechanics gate:
implement deterministic ring mechanics that emit the frozen metrics/events and
source-ledger fields for the fixed paired-seed smoke only. Do not add broad
seed sweeps, dashboards, integrations, parameter sweeps, extra hives, or
promotion language.
