# A5 Single-Hive Guarded Verification, 2026-07-01 07:25 PDT

## Scope

This note records a bounded verification of the A5 single-hive anticipatory
predictive-control stage under the current automation request. It does not add
simulator mechanics, predictor families, broader seed sweeps, dashboards,
external integrations, A7-family work, A5.2 implementation, or downstream
three-hive coupling.

The active preregistration remains
`docs/a5_single_hive_anticipatory_predictive_control_preregistration.md`.
That document already defines the requested deterministic single-hive setup,
resource-bounded prediction hypothesis, none/low/medium/high/oracle prediction
budget axis, budget-matched surrogate nulls, accounting locks, residual
endpoints, guardrails, and fail-closed residual-structure policy.

## Fresh Verification

The fresh bounded run used only the checked-in A5 scaffold:

- focused A5 regression slice:
  `.venv-conda/bin/python3.11 -m pytest tests/test_run_harness.py::test_a5_predictive_control_smoke_records_forecast_metrics tests/test_run_harness.py::test_a5_predictive_control_comparison_runs_matched_conditions tests/test_run_harness.py::test_a5_residual_accounting_analyzes_existing_comparison -q`;
- deterministic single-run smoke:
  `runs/a5_predictive_linear_seed5_20260701_0725`;
- paired seed `5,6` comparison:
  `runs/a5_predictive_control_compare_seed5_6_20260701_0725`;
- read-only residual accounting:
  `runs/a5_residual_accounting_seed5_6_20260701_0725`;
- automation guard and guard regression slice.

The paired comparison produced 16 single-hive run artifacts and 16/16 passing
accounting-lock rows for matched task stream, demand stream, service capacity,
action opportunity, work opportunity, and budget-matched null prediction-spend
checks. The residual accounting analyzer produced 1280 metric rows and 720
effect rows.

## Interpretation

The result remains fail-closed. Forecast skill improved for the predictive
conditions, but no intermediate-budget condition satisfied the preregistered
combination of residual/null, oracle-nontriviality, compression, and guardrail
criteria. Residual-structure, phase-structure, lobe-like, or
strange-attractor-like claims remain unsupported.

The automation guard reported `state=closed_awaiting_preregistration`,
`should_noop=true`, `repo_write_allowed=false`, `strategic_change_level=major`,
and `notify_ben=true`. The single recommended next scientific step is to decide
whether to authorize a fresh A5.2 implementation gate for endogenous delayed
prediction-spend dynamics.
