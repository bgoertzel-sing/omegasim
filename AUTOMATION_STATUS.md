# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be
checked from GitHub, including from a phone.

## Current Focus

Ben explicitly requested reopening the next scientific stage as A5
anticipatory predictive-control dynamics, overriding the earlier A5/A6/A7
closed/no-op posture for this bounded run.

The active A5 target is single-hive only: deterministic predictive/adaptive
controllers allocate attention or service priority from forecasts of future
task pressure while keeping task-arrival totals, service capacity, action
opportunity, and work budget matched. Prediction budget is a manipulated scarce
resource axis, not a free analytic overlay.

Do not add real LLM calls, dashboards, Lean, Slack, browser automation,
Atomspace integrations, live task boards, broad three-hive mechanics, or
downstream multi-hive coupling. Treat any strange-attractor/lobe-like language
as secondary and fail-closed unless residual structure survives the
preregistered accounting controls and timing-broken nulls. The external
strategic review dated for this run recommended an A7 implementation gate, but
that recommendation is deferred because this status file records Ben's newer
explicit A5 reopening and is the source of truth for bounded automation.

## Latest Changes

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
- `git diff --check` passed.

## Blockers

None for recording this bounded result. Scientifically, the eight-condition
confirmatory set does not support an attractor-like or residual lobe-grammar
claim.

## Recommended Next Step

Write a short A5 closure update that supersedes the older six-condition closure
note with the eight-condition confirmatory result, without new simulator
mechanics or additional runs.
