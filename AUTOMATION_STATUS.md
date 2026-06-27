# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be
checked from GitHub, including from a phone.

## Current Focus

A5.1a is now closed conservatively for Ben's resource-bounded prediction
question. The prior A5 seed `7..16` result remains a conservative
forecast-skill/accounting result: deterministic predictors improved forecast
skill under matched single-hive demand streams, but residual structure did not
survive full accounting controls and budget-matched timing-broken nulls.
The current A5 anticipatory predictive-control loop is closed at the A5.1a
accounting boundary.

The preregistered A5.1 question was whether prediction expenditure
that competes directly with work opportunity creates richer but still partially
predictable residual collective dynamics at intermediate budgets than either
zero-spend reactivity or oracle-like smoothing. The A5.1a subgate calibrated
charged prediction cost and added spend-only replay nulls before any broader
A5.1 run. That gate failed closed: charged predictors improved forecast skill
against replay nulls, but did not beat replay nulls on full-accounting residual
structure.

A5.1a remains single-hive, deterministic, and abstract/numeric. It does not
authorize real LLM calls, dashboards, Lean, Slack, browser automation,
Atomspace integrations, live task boards, broad three-hive mechanics,
downstream multi-hive coupling, or promotion language before the preregistered
accounting/null gates pass. Those gates did not pass.

The first A5.1 paired-seed smoke/pilot is complete and fail-closed. It verified
that prediction spend can be charged against work opportunity and analyzed with
full accounting controls, but it degraded work-completion guardrails and does
not support structured-dynamics promotion.

External GPT-5.5-Pro strategy review on 2026-06-27 marked this as
`strategic_change_level: major` and `notify_ben: true`. This run completes the
scientifically sensible part of that recommendation: the A5.1a
cost-calibration/spend-only-null patch has been preregistered, implemented, and
closed conservatively. Ben should be notified that the active direction shifted
from the older A7 roadmap wording back to a narrow A5.1 accounting gate and
that this accounting gate has now failed closed.

## Latest Changes

- This bounded automation run re-read `README.md`, this status file, configs,
  tests, the provisional roadmap, and the latest GPT-5.5-Pro strategy review
  before choosing a next step. The guard and status file remain authoritative:
  A5.1a is already preregistered, implemented, tested, and closed
  conservatively, so no new simulator/analyzer mechanics or experiment runs
  were started.
- The external review still recommends A5.1a cost calibration and a
  spend-only replay null with `strategic_change_level: major` and
  `notify_ben: true`; this run records that the recommendation has already
  been incorporated and closed fail-closed, while Ben still needs notification
  about the direction shift and closure.
- This bounded automation run treated the status file and guard as authoritative:
  A5.1a remains closed conservatively, the older accepted A7 roadmap wording is
  still superseded by the newer A5.1a closure status, and no new simulations,
  analyzers, simulator mechanics, configs, dashboards, integrations, or
  multi-hive coupling were added.
- Re-read the external GPT-5.5-Pro strategy review. Its sensible
  cost-calibration/spend-only-null recommendation has already been completed;
  the remaining delayed semantic/logistic or multi-hive suggestions are
  deferred pending Ben's explicit preregistered decision.
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
- Added the A5.1a cost-calibration addendum to
  `docs/a5_1_prediction_spend_competition_preregistration.md`. It freezes
  `prediction_cost_scale`, `max_prediction_work_fraction_per_tick`, and a
  spend-only replay null as prerequisites before any larger A5.1
  prediction-spend run.
- Updated `README.md` to make A5.1a the current bounded cost-calibration
  subgate and clarify that it is not A5.1 seed broadening.
- Implemented the A5.1a cost-calibration scaffold in config, simulator,
  manifest, summary, and comparison outputs. Predictive-control configs now
  accept `prediction_cost_scale` and
  `max_prediction_work_fraction_per_tick`; the charged-work target is scaled
  and capped before entering the existing prediction-charge bank.
- Added `spend_only_replay` as a timing-broken predictive-control condition.
  When `compare_predictive_control` is run from a base config with
  `charge_prediction_to_work=true`, it now generates the preregistered A5.1a
  grid: harsh-cost linear, gentle-cost linear, capped-cost linear, matched
  spend-only replay nulls for each charged positive, and a no-cost diagnostic.
- Extended the read-only A5 residual-accounting analyzer to discover comparison
  conditions from `predictive_control_comparison_metrics.csv`, preserving the
  old eight-condition A5 promotion audit while adding an A5.1a-specific
  spend-only-replay audit.
- Ran the bounded A5.1a seed `5,6` cost-calibration smoke in `/tmp`. Harsh,
  gentle, and capped charged linear predictors beat their spend-only replay
  nulls on forecast skill, but none beat the replay null on full-accounting
  residual predictability. The A5.1a audit failed closed for all charged cost
  rules.
- Added `docs/results/a5_1a_cost_calibration_closure_note_seed5_6.md`
  documenting the A5.1a closure boundary. It records the three charged cost
  rules, spend-only replay nulls, full-accounting residual audit, external
  strategy-review handling, and the stop condition against broader A5.1 seed
  sweeps.
- No dashboards, real integrations, broad seed sweeps, A6/A7 imports, or
  multi-hive mechanics were added.

## Verification

- `git status --short --branch` passed at the start of this bounded no-op run
  and reported `main...origin/main` with no uncommitted changes.
- `.venv-conda/bin/python -m ohdyn.automation_guard` passed at the start of
  this bounded no-op run. It reported
  `state=closed_awaiting_preregistration`, `should_noop=true`, closed reason
  `automation_status_next_step_noop`, `strategic_change_level=major`,
  `notify_ben=true`, and the single next step to remain in no-op/awaiting-
  preregistration state pending Ben's decision.
- `tail -40 ../outputs/omegasim-cli-loop.log` showed recent automation loops
  completed successfully and that the latest strategy review still requested
  Ben notification.
- `git diff --check` passed after this bounded no-op status update.
- `.venv-conda/bin/python -m ohdyn.automation_guard` passed after this bounded
  no-op status update and still reported
  `state=closed_awaiting_preregistration`, `should_noop=true`,
  `strategic_change_level=major`, and `notify_ben=true`.
- `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k
  automation_guard` passed after this bounded no-op status update:
  `10 passed, 612 deselected`.
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
- `git status --short --branch` passed at the start of this run and reported
  `main...origin/main` with no uncommitted changes.
- `.venv-conda/bin/python -m ohdyn.automation_guard` passed at the start of
  this run. It reported state `open`, `should_noop: false`,
  `strategic_change_level: major`, `notify_ben: true`, and recommended the
  A5.1a cost-calibration/spend-only-null patch.
- `git diff --check` passed after the A5.1a preregistration/status patch.
- `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k
  'a5_1 or automation_guard'` passed after the A5.1a patch: `10 passed, 608
  deselected`.
- `.venv-conda/bin/python -m ohdyn.automation_guard` passed after the A5.1a
  patch. It reported state `open`, `should_noop: false`,
  `strategic_change_level: major`, `notify_ben: true`, and the exact next step
  to implement the A5.1a cost-calibration/spend-only replay-null scaffold.
- `.venv-conda/bin/python -m py_compile ohdyn/config.py ohdyn/sim.py
  ohdyn/io.py ohdyn/compare_predictive_control.py` passed after implementing
  the A5.1a scaffold.
- `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k
  'a5_1 or automation_guard'` passed after the scaffold implementation:
  `12 passed, 608 deselected`.
- `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k
  'a5_predictive_control or a5_residual_accounting'` passed after preserving
  the original non-charged A5 comparison path: `3 passed, 617 deselected`.
- `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k
  'a5_1 or a5_predictive_control or a5_residual_accounting or automation_guard'`
  passed after extending the analyzer for A5.1a: `16 passed, 605 deselected`.
- `.venv-conda/bin/python -m ohdyn.compare_predictive_control --base-config
  configs/a5_1_prediction_spend_linear_smoke.yaml --seeds 5 6 --out
  /tmp/omegasim_a5_1a_cost_calibration_compare_seed5_6_20260627` passed and
  wrote 14 run artifacts across seven A5.1a conditions.
- `.venv-conda/bin/python -m ohdyn.analyze_a5_residual_accounting --compare-dir
  /tmp/omegasim_a5_1a_cost_calibration_compare_seed5_6_20260627 --out
  /tmp/omegasim_a5_1a_cost_calibration_residual_accounting_seed5_6_20260627
  --overwrite` passed after the analyzer extension. The summary reported
  fail-closed promotion status for harsh, gentle, and capped charged-cost
  conditions against their spend-only replay nulls.
- `git status --short --branch` passed at the start of this closure-note run
  and reported `main...origin/main` with no uncommitted changes.
- `.venv-conda/bin/python -m ohdyn.automation_guard` passed at the start of
  this closure-note run. It reported state `open`, `should_noop: false`,
  `strategic_change_level: major`, `notify_ben: true`, and recommended the
  A5.1a closure note.
- `git diff --check` passed after the A5.1a closure note and status update.
- `.venv-conda/bin/python -m py_compile ohdyn/automation_guard.py` passed
  after updating the guard to let newer A5.1a closure status supersede the
  older accepted A7 roadmap.
- `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k
  'a5_1 or automation_guard'` passed after the closure/guard update:
  `14 passed, 608 deselected`.
- `.venv-conda/bin/python -m ohdyn.automation_guard` passed after the final
  status update. It reported state `closed_awaiting_preregistration`,
  `should_noop: true`, closed reason `automation_status_next_step_noop`,
  `strategic_change_level: major`, `notify_ben: true`, and the single next
  step to remain in no-op/awaiting-preregistration state while notifying Ben.
- `git diff --check` passed after the final status update.
- `git status --short --branch` passed at the start of this no-op guard run and
  reported `main...origin/main` with no uncommitted changes.
- `.venv-conda/bin/python -m ohdyn.automation_guard` passed at the start of
  this no-op guard run. It reported state `closed_awaiting_preregistration`,
  `should_noop: true`, closed reason `automation_status_next_step_noop`,
  `strategic_change_level: major`, `notify_ben: true`, and the single next
  step to remain in no-op/awaiting-preregistration state pending Ben's
  decision.
- `tail -40 ../outputs/omegasim-cli-loop.log` showed the recent automation loop
  had completed the A5.1a closure/status run and that the latest strategy
  review still requested Ben notification.
- `git diff --check` passed after this no-op guard status update.
- `.venv-conda/bin/python -m ohdyn.automation_guard` passed after this no-op
  guard status update and still reported `closed_awaiting_preregistration`,
  `should_noop: true`, `strategic_change_level: major`, and `notify_ben: true`.
- `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k
  automation_guard` passed after this no-op guard status update: `10 passed,
  612 deselected`.

## Blockers

There is no local environment blocker. The scientific blocker is strategic:
the first A5.1 smoke/pilot degraded guardrails, and the A5.1a
cost-calibration smoke still failed the spend-only replay-null residual gate.
The external review also marked the direction shift as major and said Ben
should be notified.

## Recommended Next Step

- Recommended next step: remain in no-op/awaiting-preregistration state pending Ben's decision on whether to stop A5-family work or preregister a new delayed semantic/logistic or multi-hive design.
