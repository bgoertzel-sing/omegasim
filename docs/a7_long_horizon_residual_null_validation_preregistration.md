# A7 Long-Horizon Residual/Null Validation Preregistration

Date: 2026-06-27.

This document preregisters the smallest longer-horizon validation that may
follow the completed A7 six-condition smoke/analyzer gate. It is a bounded
design gate only. It does not run simulations, change simulator mechanics,
broaden into downstream multi-hive coupling, or promote A7 semantic dynamics.

## Prior Result

The current A7 seed-1 six-condition smoke artifacts exercise the frozen schema
from `ohdyn/a7_semantic_field_contract.py` and the read-only analyzer
`ohdyn.analyze_a7_semantic_field`. The smoke result is intentionally
fail-closed:

```text
conditions: 6
seed count: 1
horizon: 16 ticks
source reconstruction: pass for all six conditions
field variation: pass for all six conditions
residual metrics: insufficient_horizon
null contrasts: insufficient_horizon
decision: fail_closed_insufficient_horizon
```

This validates schema, source-ledger reconstruction, and the fail-closed
analysis path. It does not test semantic residual structure scientifically
because the 16-tick smoke horizon is below the analyzer minimum.

## Scientific Question

The longer-horizon validation asks only whether the existing single-hive A7
logistic semantic-field condition produces source-accounted residual
semantic/artifact structure that survives the preregistered null controls when
the horizon is long enough for residual metrics and same-seed contrasts to
compute.

The validation cannot claim attractors, lobe grammar, synchrony, semantic
dynamics, causal support, or multi-hive coordination. A positive result only
permits a later preregistered mechanism pilot or a more explicit closure
decision.

## Frozen Scope

Keep the existing A7 mechanics and schema fixed:

```text
no new actions
no new semantic/artifact fields
no changed source-ledger components
no changed logistic or linear utility equations
no changed prediction-budget semantics
no real LLM, Lean, Slack, browser, dashboard, live task-board, or Atomspace integration
no downstream multi-hive coupling
```

The validation must derive mechanically from the six checked-in A7 smoke
fixtures:

```text
configs/a7_logistic_semantic_coupling_smoke.yaml
configs/a7_semantic_off_baseline_smoke.yaml
configs/a7_amplitude_matched_linear_semantic_coupling_smoke.yaml
configs/a7_source_preserving_semantic_label_shuffle_smoke.yaml
configs/a7_semantic_field_phase_shuffle_smoke.yaml
configs/a7_prediction_budget_timing_broken_matched_count_null_smoke.yaml
```

Only the run horizon and experiment IDs may change for validation configs. All
model and `semantic_field` parameters must remain identical to the source smoke
fixtures unless a future preregistration freezes a different value before any
run.

## Fixed Validation Design

Use paired deterministic seeds:

```text
seeds: 1, 2
horizon: 96 ticks
conditions: the six preregistered A7 conditions
minimum analyzer horizon: 24 rows
```

The 96-tick horizon is the first validation horizon because it is above the
current analyzer minimum while remaining bounded for a small implementation
run. Do not add seeds, parameter sweeps, or a second horizon in the same run.
If 96 ticks is still underdetermined after source/control residualization,
close or redesign before broadening.

The six conditions must preserve paired seed, horizon, action opportunity,
service capacity, source-accounting schema, and prediction/work-budget
accounting. Nulls must break the preregistered semantic/timing relationship
being tested rather than changing total opportunity or budget.

## Required Residual Controls

The analyzer must account for the frozen A7 controls:

```text
tick
queue_depth
queue_delta_tick
tasks_created_total
tasks_completed_total
a7_service_capacity_tick
a7_action_opportunity_tick
a7_work_budget_tick
a7_work_actions_tick
a7_prediction_actions_tick
a7_handoff_attempts_tick
a7_handoff_successes_tick
a7_handoff_failures_tick
```

The target residual endpoints are the six semantic/artifact fields:

```text
a7_semantic_novelty_tick
a7_semantic_coherence_tick
a7_semantic_contradiction_tick
a7_semantic_risk_tick
a7_artifact_readiness_tick
a7_trust_weighted_salience_tick
```

## Required Implementation Artifacts

The next implementation run may add only these artifact families unless a
minimal analyzer bug fix is required:

```text
configs/a7_long_horizon_*.yaml
runs/a7_long_horizon_compare_seed1_2/
runs/a7_long_horizon_residual_null_analysis_seed1_2/
docs/results/a7_long_horizon_residual_null_validation_seed1_2.md
```

The comparison directory must contain normal deterministic run artifacts for
each condition/seed. The analysis directory must be produced by the existing
read-only A7 analyzer unless a minimal analyzer bug fix is necessary to make
the preregistered fields compute correctly.

## Required Report Fields

The tracked report must publish:

```text
exact command bundle
config filenames and changed keys
run artifact count
condition/seed completeness
source reconstruction status counts
residualization status counts
null-contrast gate status counts
positive-vs-null deltas by target field and seed
backlog-adjusted productivity deltas
prediction/work-budget competition status
dominant source-ledger sanity check
decision status
```

## Decision Rules

Close the validation as schema/analyzer-only if any required metric field,
event field, source ledger component, condition, seed, or paired contrast is
missing, or if the analyzer still emits `insufficient_horizon`.

Close A7 conservatively if the logistic condition fails any of these checks for
the same target field:

```text
source schema passes
source delta reconstruction passes
residualization computes
positive beats semantic-off baseline
positive beats amplitude-matched linear
positive beats source-preserving semantic-label shuffle
positive beats semantic-field phase shuffle
positive beats prediction-budget timing-broken matched-count null
paired seed signs agree
backlog-adjusted productivity is not worse than paired controls
prediction/work-budget competition is present and accounted
```

The analyzer's current same-seed gate requires the logistic condition to have
higher residual lag-1 autocorrelation, lower nearest-neighbor forecast error,
and non-worse backlog-adjusted productivity than each paired control before it
is eligible for a cross-seed direction check. Eligibility is not promotion.
Promotion requires a later preregistered interpretation review.

If the effect is erased by source-preserving or timing-broken nulls, record A7
as source-ledger/action-accounting explained. If productivity falls below
controls, record the result as a prediction-cost/productivity tradeoff rather
than semantic structure.

## Next Implementation Step

Create the fixed 96-tick validation configs and the smallest comparison helper
needed to regenerate the six paired A7 conditions without changing simulator
mechanics. Then run only seeds `1` and `2`, run
`ohdyn.analyze_a7_semantic_field`, publish the tracked validation report,
update `AUTOMATION_STATUS.md`, and stop.
