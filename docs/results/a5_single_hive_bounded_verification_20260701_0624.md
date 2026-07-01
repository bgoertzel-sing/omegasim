# A5 Single-Hive Bounded Verification, 2026-07-01 06:24 PDT

## Scope

This note records a current-run verification of the bounded A5 single-hive
anticipatory predictive-control stage. It does not add simulator mechanics,
new predictor families, broader seed sweeps, dashboards, external
integrations, A7-family work, A5.2 implementation, or downstream three-hive
coupling.

The active preregistration remains
`docs/a5_single_hive_anticipatory_predictive_control_preregistration.md`.
That document already satisfies the current A5 request: deterministic
single-hive setup, reactive baseline, low-budget linear or short-memory
prediction, medium-budget deterministic nonlinear prediction, high-budget
nonlinear prediction, oracle smoothing positive control, and budget-matched
shuffled or phase-randomized nulls.

## Verification Target

The checked-in scaffold is the only authorized implementation surface for this
pass:

- single-run deterministic smoke via `configs/a5_predictive_linear_smoke.yaml`;
- paired seed `5,6` comparison via `ohdyn.compare_predictive_control`;
- accounting-lock audit via `predictive_control_accounting_locks.csv`;
- read-only residual accounting via `ohdyn.analyze_a5_residual_accounting`;
- automation guard and focused regression tests.

The comparison design manifest is the required audit artifact for the
resource-bounded prediction hypothesis. It must preserve the none/low/medium/
high/oracle budget axis, budget-matched surrogate-null pairings, scarce
prediction-resource accounting, endpoint evidence map, fail-closed checklist,
cheap-high-level-regularities contract, comparison-readiness boundary, and
downstream three-hive exclusion.

## Current Interpretation

The scientific interpretation remains fail-closed. Existing bounded A5
artifacts show forecast-skill improvements for predictive conditions, but they
do not support residual-structure, lobe-like, phase-structure, or
strange-attractor-like claims after the preregistered accounting controls,
budget-matched surrogate nulls, oracle non-target rule, compression checks, and
guardrails.

The next scientific decision is not another unregistered A5 broadening pass.
It is whether to authorize a fresh A5.2 implementation gate for endogenous,
delayed prediction-spend decisions.
