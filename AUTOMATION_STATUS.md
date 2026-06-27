# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be
checked from GitHub, including from a phone.

## Current Focus

A5.1 is the current bounded A5 follow-up gate for Ben's resource-bounded
prediction question. The prior A5 seed `7..16` result remains a conservative
forecast-skill/accounting result: deterministic predictors improved forecast
skill under matched single-hive demand streams, but residual structure did not
survive full accounting controls and budget-matched timing-broken nulls.

The newly preregistered A5.1 question is whether prediction expenditure that
competes directly with work opportunity creates richer but still partially
predictable residual collective dynamics at intermediate budgets than either
zero-spend reactivity or oracle-like smoothing.

A5.1 remains single-hive, deterministic, and abstract/numeric. It does not
authorize real LLM calls, dashboards, Lean, Slack, browser automation,
Atomspace integrations, live task boards, broad three-hive mechanics,
downstream multi-hive coupling, or promotion language before the preregistered
accounting/null gates pass.

The first A5.1 paired-seed smoke/pilot is a scaffold check only. It verifies
that prediction spend can be charged against work opportunity and analyzed with
full accounting controls; it does not support structured-dynamics promotion.

## Latest Changes

- Added `docs/a5_1_prediction_spend_competition_preregistration.md` as the
  next bounded A5 follow-up preregistration. It freezes a single-hive design in
  which prediction spend is deducted from explicit work opportunity, preserving
  matched task-arrival totals, class-demand streams, service capacity, action
  opportunity, and total decision budget across conditions.
- The A5.1 gate defines reactive, low-budget linear or short-memory,
  medium-budget nonlinear, high-budget nonlinear, oracle, and budget-matched
  timing-broken null conditions.
- Primary endpoints are forecast skill per prediction spend, lead-lag
  allocation to future demand, residual phase structure after full accounting,
  recurrence/return-map structure in residual predictive-state delay
  embeddings, high-level state predictability/compressibility, and guardrails
  for backlog, queued age, completion fraction, starvation, prediction-spend
  volatility, and work-budget volatility.
- Updated `README.md` to point at the A5.1 gate and clarify that the next
  prediction-resource question is direct spend/work-opportunity competition,
  not broad A5 seed extension or downstream multi-hive coupling.
- Added the smallest opt-in deterministic A5.1 scaffold: predictive-control
  configs can set `charge_prediction_to_work: true`, which accumulates a
  fractional prediction-cost bank and converts selected `work_task`
  opportunities into explicit `a5_prediction_spent` events counted as `idle`
  for the existing action schema.
- Added A5.1 prediction-spend metrics for charged-to-work status, charge
  target, charged work units, pre-charge work opportunity, and remaining work
  budget. Existing A5 configs keep the old manifest config shape because the
  new flag is omitted unless enabled.
- Added `configs/a5_1_prediction_spend_linear_smoke.yaml` and extended the A5
  comparison helper to aggregate charged-work and remaining-budget means.
- Extended the read-only A5 residual-accounting analyzer's full-accounting
  level with optional prediction-spend and remaining-work controls.
- Ran a paired-seed A5.1 smoke/pilot in `/tmp`. Forecast skill improved for
  intermediate predictors, but charged prediction spend sharply reduced work
  completion and the residual-accounting promotion audit failed closed with
  guardrails not satisfied.
- No dashboards, real integrations, broad seed sweeps, A6/A7 imports, or
  multi-hive mechanics were added.

## Verification

- `git status --short --branch` initially reported
  `main...origin/main [ahead 1]` with no uncommitted changes before this
  preregistration pass.
- `.venv-conda/bin/python -m ohdyn.automation_guard` passed. It reported
  state `open`, `should_noop: false`, no closed reasons, and recommended the
  A5.1 smoke scaffold as the next action from this status file.
- `.venv-conda/bin/python -m py_compile ohdyn/automation_guard.py
  ohdyn/compare_predictive_control.py ohdyn/analyze_a5_residual_accounting.py`
  passed.
- `.venv-conda/bin/python -m py_compile ohdyn/config.py ohdyn/sim.py
  ohdyn/io.py ohdyn/compare_predictive_control.py
  ohdyn/analyze_a5_residual_accounting.py ohdyn/automation_guard.py` passed
  after the A5.1 scaffold.
- `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k
  'a5_predictive_control or a5_residual_accounting or automation_guard'`
  passed: `12 passed, 605 deselected`.
- `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k
  'a5_predictive_control or a5_1_prediction_spend or a5_residual_accounting or
  automation_guard'` passed after the A5.1 scaffold: `13 passed, 605
  deselected`.
- `.venv-conda/bin/python -m ohdyn.run --config
  configs/a5_predictive_linear_smoke.yaml --seed 5 --out
  /tmp/omegasim_a5_predictive_linear_smoke_20260627_a5_1_prereg` passed.
- `.venv-conda/bin/python -m ohdyn.run --config
  configs/a5_1_prediction_spend_linear_smoke.yaml --seed 5 --out
  /tmp/omegasim_a5_1_prediction_spend_linear_smoke_20260627_final` passed. The
  final metric row recorded `a5_prediction_charged_to_work=true`,
  `a5_prediction_work_charge_target_tick=5.25`, and
  `a5_work_budget_remaining_tick=13`.
- `.venv-conda/bin/python -m ohdyn.compare_predictive_control --base-config
  configs/a5_1_prediction_spend_linear_smoke.yaml --seeds 5 6 --out
  /tmp/omegasim_a5_1_prediction_spend_compare_seed5_6_20260627_final` passed.
  The pilot wrote 16 run artifacts across the eight A5 conditions.
- `.venv-conda/bin/python -m ohdyn.analyze_a5_residual_accounting --compare-dir
  /tmp/omegasim_a5_1_prediction_spend_compare_seed5_6_20260627_final --out
  /tmp/omegasim_a5_1_prediction_spend_residual_accounting_seed5_6_20260627_final`
  passed. The analyzer reported fail-closed promotion status; all intermediate
  predictors failed the residual/null and guardrail gates.
- `git diff --check` passed.

## Blockers

There is no local environment blocker. The scientific blocker is that the first
A5.1 smoke/pilot is intentionally fail-closed: prediction spend is now charged
against work opportunity, but the paired-seed smoke degrades guardrails and does
not support residual structured-dynamics claims.

## Recommended Next Step

Review the A5.1 charged-spend pilot and preregister a gentler cost-scaling rule
before any broader prediction-spend run.
