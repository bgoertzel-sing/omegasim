# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be
checked from GitHub, including from a phone.

## Current Focus

This run reconciled the explicitly requested A5 anticipatory
predictive-control stage against the current repository. The requested concise
single-hive preregistration already exists in
`docs/a5_anticipatory_predictive_control_preregistration.md`, the smallest
deterministic smoke scaffold already exists in
`configs/a5_predictive_linear_smoke.yaml` plus `ohdyn.compare_predictive_control`
and `ohdyn.analyze_a5_residual_accounting`, and the later A5 closure/reopening
boundary is recorded in `docs/a5_post_closure_reopening_gate.md`.

A5 remains a useful but closed single-hive predictive-control result: bounded
predictors improved forecast skill under matched demand streams, but the seed
`7..16` evidence did not pass the preregistered full-accounting residual
structure gate. The explicit A5 prompt does not warrant duplicating the
preregistration, adding broader mechanics, broadening seeds, or starting
three-hive delayed anticipatory coupling in this run.

Do not add real LLM calls, dashboards, Lean, Slack, browser automation,
Atomspace integrations, live task boards, broad three-hive mechanics, or
downstream multi-hive coupling. Do not reopen A5 for new predictor mechanics,
new seed sweeps, or attractor/lobe-like promotion language without a fresh
preregistration that supersedes the post-closure gate.

## Latest Changes

- Updated this status file to record the A5 prompt reconciliation on
  2026-06-27T15:06:55Z.
- Confirmed the tracked A5 preregistration covers reactive, linear,
  deterministic nonlinear, oracle, and budget-matched shuffled/phase-randomized
  null conditions.
- Confirmed the tracked A5 design treats prediction expenditure as a scarce
  managed resource and requires matched task-arrival totals, service capacity,
  action opportunity, work budget, deterministic demand streams, guardrails,
  accounting controls, and surrogate nulls.
- No preregistration rules, simulator mechanics, analyzers, configs, tests,
  dashboards, external integrations, broad runs, or multi-hive coupling were
  added.

## Verification

- Documentation/status-only repository change; no simulator or analyzer code
  changed.
- `.venv-conda/bin/python -m py_compile ohdyn/compare_predictive_control.py
  ohdyn/analyze_a5_residual_accounting.py ohdyn/automation_guard.py` passed.
- `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k 'a5 or
  automation_guard'` passed: `10 passed, 592 deselected`.
- `.venv-conda/bin/python -m ohdyn.run --config
  configs/a5_predictive_linear_smoke.yaml --seed 5 --out
  /tmp/omegasim_a5_reconcile_smoke_20260627_1500` passed.
- `.venv-conda/bin/python -m ohdyn.automation_guard` reports `state=open`,
  `should_noop=false`, `strategic_change_level=minor`, and `notify_ben=false`.

## Blockers

None for the A5 reconciliation. Scientifically, A5 should remain closed unless
Ben requests a materially new anticipatory-prediction design and that design is
preregistered before implementation.

## Recommended Next Step

Create the fixed 96-tick A6.2 validation configs and the smallest comparison
helper needed to regenerate the six required paired conditions, then run only
seeds `1` and `2` and analyze them with the existing read-only A6.2 analyzer.
