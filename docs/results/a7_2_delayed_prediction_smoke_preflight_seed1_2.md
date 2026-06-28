# A7.2 Delayed Prediction Smoke Preflight, Seeds 1-2

Date: 2026-06-28.

## Scope

This was the preregistered tiny A7.2 single-hive smoke over the ten frozen
conditions and paired seeds `1,2`:

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

No dashboards, integrations, broad seed sweeps, parameter tuning, or multi-hive
mechanics were added.

## Commands

```bash
.venv-conda/bin/python -m ohdyn.compare_a7_2_delayed_prediction --seeds 1 2 --out runs/a7_2_delayed_prediction_compare_seed1_2
.venv-conda/bin/python -m ohdyn.analyze_a7_2_delayed_prediction --compare-dir runs/a7_2_delayed_prediction_compare_seed1_2 --out runs/a7_2_delayed_prediction_analysis_seed1_2
```

## Analyzer Result

The read-only analyzer inspected 20 run artifacts and closed fail-closed:

```text
status: fail_closed_residual_null_gate
schema/source pass rows: 20
forecast delay pass rows: 18
artifact delay pass rows: 20
residual row status: computed=140
null-contrast gate status:
  eligible_for_guardrail_and_cross_seed_review=45
  fail_closed_no_nonlinear_forecastability_advantage=25
  fail_closed_no_residual_autocorrelation_advantage=56
productivity guardrail status: pass=18
```

The schema/source-ledger and productivity preflight passed, but the candidate
positive condition did not beat every preregistered null on residual preflight
contrasts. This result does not support lobe-like, attractor-like,
semantic-dynamics, synchrony, or causal collective-structure claims.

## Interpretation Boundary

This is a smoke/preflight result, not a promotion result. It should be treated
as an A7.2 fail-closed signal under the current preregistered gate unless Ben
explicitly requests a new preregistration. Per the active roadmap, the next
scientific step after this A7.2 closure signal is a separate three-hive ring
preregistration, not tuning A7.2 or adding downstream multi-hive mechanics
inside the current gate.
