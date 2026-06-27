# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be
checked from GitHub, including from a phone.

## Current Focus

Ben explicitly requested reopening the next scientific stage as A5
anticipatory predictive-control dynamics. That bounded reopening is now closed
with the eight-condition seed `7..16` confirmatory result and closure update.

The closed A5 target was single-hive only: deterministic predictive/adaptive
controllers allocated attention or service priority from forecasts of future
task pressure while keeping task-arrival totals, service capacity, action
opportunity, and work budget matched. Prediction budget was a manipulated
scarce resource axis, not a free analytic overlay.

Do not add real LLM calls, dashboards, Lean, Slack, browser automation,
Atomspace integrations, live task boards, broad three-hive mechanics, or
downstream multi-hive coupling. Treat any strange-attractor/lobe-like language
as secondary and fail-closed unless residual structure survives the
preregistered accounting controls and timing-broken nulls. The external
strategic review dated for this run recommended an A7 implementation gate, but
that recommendation was deferred for this bounded run because this status file
recorded Ben's newer explicit A5 reopening and the next required action was the
A5 closure update.

## Latest Changes

- Added `docs/results/a5_eight_condition_closure_update_seed7_16.md`, which
  supersedes the older six-condition closure note for current A5
  interpretation without rerunning simulations or changing simulator mechanics.
- Ran the preregistered eight-condition A5 confirmatory paired-seed set for
  seeds `7..16` with no simulator mechanics changes:
  `reactive`, `linear`, `nonlinear`, `nonlinear_high_budget`, `oracle`,
  `shuffled`, `nonlinear_shuffled`, and
  `nonlinear_high_budget_shuffled`.
- Ran the read-only A5 residual accounting analyzer over that fresh
  eight-condition comparison. The analyzer emitted `6400` metric rows and
  `720` effect rows.
- Recorded the result in
  `docs/results/a5_eight_condition_confirmatory_seed7_16.md`. Forecast skill
  improved for all predictor conditions versus reactive or their
  budget-matched timing-broken nulls, including
  `nonlinear_high_budget_minus_nonlinear_high_budget_shuffled = +0.106704`.
- The promotion audit still failed closed: all primary full-accounting
  residual-state predictability contrasts were inside paired
  label-permutation intervals, and both nonlinear conditions failed practical
  guardrails.

## Verification

- `.venv-conda/bin/python -m ohdyn.automation_guard` passed before the closure
  update with `state: open`, `a5_preregistration_active: true`, and recommended
  this A5 closure update.
- `.venv-conda/bin/python -m ohdyn.automation_guard` passed after the closure
  update with `state: closed_awaiting_preregistration`, `should_noop: true`,
  and `closed_reasons: ["automation_status_noop_guard",
  "automation_status_a5_closed"]`.
- `.venv-conda/bin/python -m ohdyn.automation_guard` passed with
  `state: open`, `a5_preregistration_active: true`, and recommended the
  eight-condition A5 confirmatory paired-seed set.
- `.venv-conda/bin/python -m ohdyn.compare_predictive_control --seeds 7 8 9
  10 11 12 13 14 15 16 --out
  runs/a5_predictive_control_confirmatory_seed7_16_eight_condition_20260627`
  passed and generated 80 deterministic runs across 8 matched conditions.
- `.venv-conda/bin/python -m ohdyn.analyze_a5_residual_accounting
  --compare-dir
  runs/a5_predictive_control_confirmatory_seed7_16_eight_condition_20260627
  --out
  runs/a5_residual_accounting_confirmatory_seed7_16_eight_condition_20260627`
  passed. Promotion decision: fail closed; no intermediate-budget condition
  satisfied all preregistered criteria.
- `.venv-conda/bin/python -m py_compile ohdyn/compare_predictive_control.py
  ohdyn/analyze_a5_residual_accounting.py ohdyn/automation_guard.py` passed.
- `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k
  'a5_predictive_control or a5_residual_accounting or automation_guard'`
  passed: `11 passed, 600 deselected`.
- `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k
  'automation_guard'` passed after the closure update: `8 passed, 603
  deselected`.
- `git diff --check` passed.

## Blockers

None for recording this bounded result. Scientifically, the eight-condition
confirmatory set does not support an attractor-like or residual lobe-grammar
claim. Do not reopen A5 without a new preregistration.

## Recommended Next Step

Remain in no-op/awaiting-preregistration state for A5 unless Ben explicitly
requests a new preregistered A5 design.
