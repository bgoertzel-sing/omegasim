# A7 Implementation Gate

Status: frozen contract gate before simulator mechanics.

A7 may proceed only after code and tests agree on the contract below. This gate
does not authorize new simulator dynamics, seed broadening, dashboards, real LLM
calls, Lean, Slack, browser automation, Atomspace integrations, live task
boards, or multi-hive coupling.

## State Vector

The semantic/artifact activation field `A(t)` has six bounded field values:

```text
semantic_novelty
semantic_coherence
semantic_contradiction
semantic_risk
artifact_readiness
trust_weighted_salience
```

Per-agent prediction accounting has two additional state fields:

```text
prediction_budget_spent
prediction_error
```

Metrics must emit both tick-level and mean tick-level fields using the
`a7_<field>_tick` and `a7_<field>_mean_tick` naming pattern.

## Update Equations

Future simulator code must implement bounded source-accounted updates:

```text
A_k(t+1) = clip(rho_k * A_k(t) + sum_s delta_{k,s}(t) + epsilon_k(t))
Delta A_k(t) = sum_s delta_{k,s}(t) + clip_residual_k(t)
prediction_error_i(t) = target_peer_need_i(t + lead) - forecast_i(t)
prediction_budget_spent_i(t) <= prediction_budget_per_tick
```

Prediction spend competes with work budget in the first implementation so that
any productivity change is accounted rather than hidden as free computation.

## Utility Equations

The semantic-field conditions must share action opportunities and budget
accounting. They differ only in how semantic fields enter action utilities:

```text
linear: U_i(a,t) = b_a + w_a dot A(t-1) - c_pred spend_i(t) - c_fatigue fatigue_i(t)
logistic: P_i(a,t) = sigmoid(beta_a * (U_i(a,t) - theta_i(t)))
threshold: theta_i(t+1) = clip(theta_i(t) + eta_err * prediction_error_i(t) - eta_rest * idle_i(t))
```

The amplitude-matched linear condition must use matched semantic input scale and
the same queue, service, budget, action, and noise streams where applicable.

## Source Ledger

Every semantic-field delta must be decomposable into these components:

```text
ambient_decay
self_contribution
peer_contribution
artifact_handoff
prediction_expenditure
prediction_error
queue_work_accounting
semantic_noise
clip_residual
```

Events must emit one row per semantic-field update with `a7_delta_total` and one
`a7_delta_<source>` column for every source component. Positive A7 claims are
invalid if field deltas cannot be reconstructed from named source columns.

## Conditions And Nulls

The first paired smoke grid is exactly:

```text
a7_logistic_semantic_coupling
semantic_off_baseline
amplitude_matched_linear_semantic_coupling
source_preserving_semantic_label_shuffle
semantic_field_phase_shuffle
prediction_budget_timing_broken_matched_count_null
```

The label shuffle must preserve per-tick source totals while permuting semantic
field labels. The phase shuffle must preserve field trajectories but break
their timing against actions. The prediction-budget null must preserve matched
prediction-spend counts while breaking timing.

## Required Controls

The analyzer must residualize or otherwise account for:

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

## Analyzer Contract

`ohdyn.analyze_a7_semantic_field` is read-only. It must fail closed when runs,
conditions, source fields, metrics fields, event fields, residualization inputs,
or null artifacts are absent. It must not rerun simulations or infer missing
schema.

The first implementation gate is complete only when:

1. the frozen constants are imported by tests;
2. the fail-closed analyzer writes deterministic completeness and manifest
   artifacts;
3. simulator mechanics remain untouched;
4. `py_compile`, focused pytest, and `git diff --check` pass.
