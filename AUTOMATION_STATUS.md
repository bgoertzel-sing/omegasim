# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be
checked from GitHub, including from a phone.

## Current Focus

Ben explicitly requested A5 anticipatory predictive-control dynamics as the
current bounded scientific stage. This overrides the prior closed/no-op A4
boundary for the purpose of the A5 preregistration and small smoke scaffold,
while preserving the A2/A3/A4 lessons about load, service capacity, action
opportunity, and accounting confounds.

The active gate is the single-hive preregistration in
`docs/a5_anticipatory_predictive_control_preregistration.md`. Later A6/A7
documents and mechanics remain historical follow-on branches for this run and
must not be imported into A5. The A5 path should stay deterministic,
single-hive, and free of real LLM calls, dashboards, Lean, Slack, browser
automation, Atomspace integrations, live task boards, broad three-hive
mechanics, or downstream multi-hive coupling.

The current A5 question is whether resource-bounded prediction creates richer
but still partly predictable residual collective dynamics than zero-budget
reactivity or oracle-like smoothing, after matched accounting controls and
surrogate nulls. Prediction budget is an experimental axis and a scarce managed
resource, not a free analytic overlay.

## Latest Changes

- Marked the A5 preregistration as the current automation gate for Ben's
  explicit 2026-06-27 request, while keeping A6/A7 as historical context only.
- Clarified in the README that A5 is the active bounded stage for this run and
  that the checked-in scaffold is intentionally deterministic and single-hive.
- Confirmed that the existing A5 scaffold already covers the minimal smoke
  surface: reactive, linear, nonlinear, high-budget nonlinear, oracle, and
  budget-matched timing-broken null predictor conditions over matched demand
  streams.
- No broad mechanics, multi-hive coupling, real integrations, dashboards, seed
  sweeps, or attractor/lobe claims were added.

## Verification

- `.venv-conda/bin/python -m py_compile ohdyn/compare_predictive_control.py
  ohdyn/analyze_a5_residual_accounting.py ohdyn/automation_guard.py` passed.
- `.venv-conda/bin/python -m ohdyn.run --config
  configs/a5_predictive_linear_smoke.yaml --seed 5 --out
  /tmp/omegasim_a5_predictive_linear_smoke_20260627_a5_restart` passed.
- `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k
  'a5_predictive_control or a5_residual_accounting or automation_guard'`
  passed: `12 passed, 602 deselected`.
- `.venv-conda/bin/python -m ohdyn.automation_guard` passed with
  `state: open`, `should_noop: false`, and `closed_reasons: []`.
- `git diff --check` passed.

## Blockers

None for the preregistration/status correction or existing A5 smoke scaffold.
Scientifically, A5 still has no new evidence in this run beyond the ability to
run the deterministic scaffold; any structured strange-attractor-like
interpretation remains secondary and fail-closed pending accounting controls and
surrogate nulls.

## Recommended Next Step

Run the smallest paired-seed A5 pilot comparison and residual-accounting
analysis against the frozen single-hive preregistration, then decide whether
intermediate prediction budgets show residual structure beyond matched nulls.
