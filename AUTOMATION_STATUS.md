# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be
checked from GitHub, including from a phone.

## Current Focus

This run reconciled the explicitly requested A5 anticipatory predictive-control
stage against the current repository state. The requested concise
single-hive preregistration already exists in
`docs/a5_anticipatory_predictive_control_preregistration.md`, and the minimal
deterministic scaffold already exists in the A5 smoke config,
`ohdyn.compare_predictive_control`, and `ohdyn.analyze_a5_residual_accounting`.

A5 remains closed conservatively by the seed `7..16` forecast-skill/residual-gap
evidence: bounded predictors improved forecast skill under matched deterministic
demand streams, but the promotion-relevant residual structure did not survive
load, service-capacity, action-opportunity, work-budget, and budget-matched
timing-broken null controls. Do not add new A5 mechanics, broad seed sweeps, or
downstream three-hive delayed anticipatory coupling without a fresh
preregistration.

The current post-A5 focus remains the accepted A6.1 source-accounting direction.
A6 is still smoke/analyzer-only, not promoted.

Do not add real LLM calls, dashboards, Lean, Slack, browser automation,
Atomspace integrations, live task boards, broad three-hive mechanics, or
downstream multi-hive coupling.

## Latest Changes

- Status: A5 preregistration/scaffold reconciliation completed, 2026-06-27.
- Confirmed: the A5 preregistration defines deterministic single-hive
  predictive control, reactive/linear/nonlinear/oracle/budget-matched
  timing-broken null conditions, matched task-arrival totals, service capacity,
  action opportunity, work budget, resource-bounded prediction budget, primary
  residual/accounting endpoints, guardrails, and fail-closed strange-attractor
  claim rules.
- Confirmed: the checked-in A5 scaffold can run the single-hive smoke fixture
  without real LLM calls, dashboards, Lean, Slack, browser automation, Atomspace
  integrations, live task boards, or multi-hive coupling.
- Confirmed: the existing A5 comparison/analyzer path covers the requested
  matched predictor conditions and read-only residual-accounting analysis.
- Result: no preregistration, simulator mechanics, analyzers, configs, tests,
  dashboards, external integrations, broader seeds, or multi-hive/downstream
  coupling were added in this run.
- Interpretation: the explicit A5 request is already satisfied by tracked
  artifacts and remains scientifically closed by the prior seed `7..16` report.
  The defensible A5 claim remains limited to forecast-skill manipulation, not
  accounting-robust residual lobe grammar, recurrence, strange-attractor
  structure, or nonlinear collective dynamics.
- Verification: `.venv-conda/bin/python -m py_compile
  ohdyn/compare_predictive_control.py ohdyn/analyze_a5_residual_accounting.py
  ohdyn/automation_guard.py` passed; `.venv-conda/bin/python -m pytest
  tests/test_run_harness.py -q -k 'a5 or automation_guard'` passed
  (`10 passed, 589 deselected`); `.venv-conda/bin/python -m ohdyn.run --config
  configs/a5_predictive_linear_smoke.yaml --seed 5 --out
  /tmp/omegasim_a5_reconcile_smoke_20260627_1206` passed;
  `.venv-conda/bin/python -m ohdyn.automation_guard` reported `state: open`,
  `should_noop: false`, `strategic_change_level: minor`, and
  `notify_ben: false`.
- Blockers: none.
- Recommended next step: preregister the smallest A6.1 pilot/null design that
  tests source-preserving nulls and backlog-adjusted productivity after source
  accounting, without broadening seeds or changing interpretation in the same
  run.
