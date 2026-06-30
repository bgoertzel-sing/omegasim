# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be
checked from GitHub, including from a phone.

## Current Focus

Source-of-truth status: Ben's 2026-06-30 automation prompt explicitly reopened
the bounded A5 single-hive anticipatory predictive-control stage for the
preregistration/scaffold pass. That pass remains completed at the bounded
single-hive smoke/analyzer boundary.

The active A5 source of truth remains
`docs/a5_single_hive_anticipatory_predictive_control_preregistration.md`.
The existing deterministic single-hive smoke/pilot scaffold and read-only
residual accounting were verified. The result remains fail-closed for
residual-structure promotion: intermediate predictors improved forecast skill,
but no intermediate-budget condition passed all residual/null,
oracle-nontriviality, compression, and guardrail criteria.

Do not add broad A5 tuning, dashboards, external integrations, A7-family
mechanics, or three-hive delayed anticipatory coupling from this result.

The next bounded A5 design gate is now preregistered, but not implemented, in
`docs/a5_2_endogenous_delayed_prediction_spend_preregistration.md`. It asks
whether endogenous delayed prediction-spend decisions can produce useful,
partially predictable residual collective dynamics after matched spend,
work-budget, timing-broken, and accounting controls.

2026-06-30 04:06 PDT status check: the A5 single-hive preregistration and
minimal deterministic scaffold remain complete. No new simulator mechanics or
scientific runs were added because the guard still closes further A5 work until
Ben explicitly chooses whether to implement the preregistered A5.2 smoke
scaffold.

2026-06-30 05:06 PDT status check: the requested concise A5 preregistration
already exists and remains the active bounded source of truth. The existing
deterministic single-hive smoke/pilot scaffold was reverified under `/tmp`;
residual accounting again failed closed. No new simulator mechanics,
dashboards, integrations, broad seed sweeps, or multi-hive coupling were added.

2026-06-30 06:08 PDT status check: the bounded A5 preregistration/scaffold
surface was reverified without broadening scope. Forecast skill again improved
for intermediate predictors, but residual accounting failed closed under the
same preregistered null/accounting filters. No new simulator mechanics or
scientific claims were added.

2026-06-30 07:09 PDT status check: the concise A5 preregistration and
checked-in deterministic single-hive scaffold were reverified again. The guard
still closes further A5 expansion pending an explicit A5.2 decision. The fresh
seed `5,6` smoke/comparison/analyzer pass again failed closed for residual
promotion, so no structured-strange-attractor-like or lobe-like A5 claim is
supported.

2026-06-30 08:14 PDT status check: the bounded A5 comparison scaffold now
writes an explicit `predictive_control_accounting_locks.csv` audit. The audit
checks matched task-arrival streams, demand-share streams, service capacity,
action opportunity, pre-prediction work opportunity, and budget-matched null
prediction-spend rows before residual interpretation.

## Latest Changes

- 2026-06-30 02:05 PDT preregistration checkpoint: refreshed the concise A5
  single-hive anticipatory predictive-control preregistration with the current
  bounded-stage override and scope boundary.
- 2026-06-30 02:05 PDT guard checkpoint: wired the existing explicit bounded
  A5 override detector in `ohdyn.automation_guard` so the current scoped status
  can override the prior PAUSE-RECOVER recommendation only when the status does
  not itself close A5.
- 2026-06-30 02:05 PDT bounded smoke/analyzer: reran the single-hive linear
  smoke, paired seed `5,6` predictive-control comparison, and read-only
  residual-accounting analyzer under `/tmp`.
- 2026-06-30 03:06 PDT preregistration-only checkpoint: added the A5.2
  endogenous delayed prediction-spend preregistration as the next design gate,
  with no simulator mechanics or new scientific runs authorized.
- 2026-06-30 04:06 PDT guard/status checkpoint: confirmed the requested A5
  preregistration already exists, the checked-in deterministic scaffold remains
  the complete authorized implementation surface, and A5.2 remains a
  preregistered but unimplemented decision gate.
- 2026-06-30 05:06 PDT bounded verification checkpoint: reverified the existing
  A5 single-hive preregistration/scaffold surface and recorded no new mechanics
  because the guard remains closed pending an explicit A5.2 implementation
  decision.
- 2026-06-30 06:08 PDT bounded verification checkpoint: reverified the existing
  A5 single-hive smoke/analyzer surface and preserved the fail-closed A5
  interpretation boundary; A5.2 remains preregistered but unimplemented.
- 2026-06-30 07:09 PDT bounded verification checkpoint: reverified the existing
  A5 guard, smoke, paired comparison, and read-only residual accounting surface;
  no broad A5 mechanics, dashboards, integrations, seed sweeps, A7 mechanics,
  or multi-hive coupling were added.
- 2026-06-30 08:14 PDT scaffold hardening: added the A5 predictive-control
  accounting-lock audit artifact to the comparison runner and preregistration,
  without adding simulator mechanics, broader seeds, dashboards, integrations,
  A7 mechanics, or multi-hive coupling.

## Verification

- 2026-06-30 02:05 PDT guard check before smoke:
  `.venv-conda/bin/python -m ohdyn.automation_guard` reported `state=open`,
  `should_noop=false`, `repo_write_allowed=true`, and recommended the bounded
  A5 scaffold verification.
- 2026-06-30 02:05 PDT focused regression/smoke tests:
  `.venv-conda/bin/python -m pytest tests/test_run_harness.py::test_automation_guard_opens_for_explicit_bounded_a5_override tests/test_run_harness.py::test_automation_guard_closes_current_a5_when_latest_review_blocks_scaffold tests/test_run_harness.py::test_a5_predictive_control_smoke_records_forecast_metrics tests/test_run_harness.py::test_a5_predictive_control_comparison_runs_matched_conditions tests/test_run_harness.py::test_a5_residual_accounting_analyzes_existing_comparison -q`
  passed (`5 passed`).
- 2026-06-30 02:05 PDT single-run smoke:
  `.venv-conda/bin/python -m ohdyn.run --config configs/a5_predictive_linear_smoke.yaml --seed 5 --out /tmp/omegasim_a5_bounded_linear_smoke_seed5_20260630_0205`
  completed.
- 2026-06-30 02:05 PDT paired comparison:
  `.venv-conda/bin/python -m ohdyn.compare_predictive_control --seeds 5 6 --out /tmp/omegasim_a5_bounded_predictive_compare_seed5_6_20260630_0205`
  completed with 16 single-hive matched-demand run artifacts.
- 2026-06-30 02:05 PDT residual accounting:
  `.venv-conda/bin/python -m ohdyn.analyze_a5_residual_accounting --compare-dir /tmp/omegasim_a5_bounded_predictive_compare_seed5_6_20260630_0205 --out /tmp/omegasim_a5_bounded_residual_accounting_seed5_6_20260630_0205`
  completed with 1280 metric rows and 720 effect rows; promotion decision was
  fail closed for linear, nonlinear, and high-budget nonlinear predictors.
- 2026-06-30 02:05 PDT final guard regression slice:
  `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k automation_guard -q`
  passed (`29 passed, 651 deselected`).
- 2026-06-30 02:05 PDT syntax and whitespace checks:
  `.venv-conda/bin/python -m py_compile ohdyn/automation_guard.py tests/test_run_harness.py`
  passed, and `git diff --check` passed.
- 2026-06-30 02:05 PDT final guard state:
  `.venv-conda/bin/python -m ohdyn.automation_guard` reported
  `state=closed_awaiting_preregistration`, `should_noop=true`,
  `repo_write_allowed=false`, and
  `closed_reasons=["strategy_review_a5_recovery_required"]`.
- 2026-06-30 03:06 PDT guard check:
  `.venv-conda/bin/python -m ohdyn.automation_guard` reported
  `state=closed_awaiting_preregistration`, `should_noop=true`,
  `repo_write_allowed=false`, and recommended Ben decide whether to authorize
  the minimal deterministic A5.2 smoke scaffold.
- 2026-06-30 03:06 PDT focused guard regression slice:
  `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k automation_guard -q`
  passed (`29 passed, 651 deselected`).
- 2026-06-30 03:06 PDT whitespace check: `git diff --check` passed.
- 2026-06-30 04:06 PDT guard check:
  `.venv-conda/bin/python -m ohdyn.automation_guard` reported
  `state=closed_awaiting_preregistration`, `should_noop=true`,
  `repo_write_allowed=false`, and recommended Ben decide whether to authorize
  the minimal deterministic A5.2 smoke scaffold.
- 2026-06-30 04:06 PDT focused guard regression slice:
  `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k automation_guard -q`
  passed (`29 passed, 651 deselected`).
- 2026-06-30 04:06 PDT whitespace check: `git diff --check` passed.
- 2026-06-30 05:06 PDT guard check:
  `.venv-conda/bin/python -m ohdyn.automation_guard` reported
  `state=closed_awaiting_preregistration`, `should_noop=true`,
  `repo_write_allowed=false`, and recommended Ben decide whether to authorize
  the minimal deterministic A5.2 smoke scaffold.
- 2026-06-30 05:06 PDT focused regression/smoke tests:
  `.venv-conda/bin/python -m pytest tests/test_run_harness.py::test_automation_guard_opens_for_explicit_bounded_a5_override tests/test_run_harness.py::test_automation_guard_closes_current_a5_when_latest_review_blocks_scaffold tests/test_run_harness.py::test_a5_predictive_control_smoke_records_forecast_metrics tests/test_run_harness.py::test_a5_predictive_control_comparison_runs_matched_conditions tests/test_run_harness.py::test_a5_residual_accounting_analyzes_existing_comparison -q`
  passed (`5 passed`).
- 2026-06-30 05:06 PDT single-run smoke:
  `.venv-conda/bin/python -m ohdyn.run --config configs/a5_predictive_linear_smoke.yaml --seed 5 --out /tmp/omegasim_a5_bounded_linear_smoke_seed5_20260630_0506`
  completed.
- 2026-06-30 05:06 PDT paired comparison:
  `.venv-conda/bin/python -m ohdyn.compare_predictive_control --seeds 5 6 --out /tmp/omegasim_a5_bounded_predictive_compare_seed5_6_20260630_0506`
  completed with 16 single-hive matched-demand run artifacts.
- 2026-06-30 05:06 PDT residual accounting:
  `.venv-conda/bin/python -m ohdyn.analyze_a5_residual_accounting --compare-dir /tmp/omegasim_a5_bounded_predictive_compare_seed5_6_20260630_0506 --out /tmp/omegasim_a5_bounded_residual_accounting_seed5_6_20260630_0506`
  completed with 1280 metric rows and 720 effect rows; promotion decision was
  fail closed for linear, nonlinear, and high-budget nonlinear predictors.
- 2026-06-30 05:06 PDT final guard regression slice:
  `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k automation_guard -q`
  passed (`29 passed, 651 deselected`).
- 2026-06-30 05:06 PDT whitespace check: `git diff --check` passed.
- 2026-06-30 06:08 PDT guard check:
  `.venv-conda/bin/python -m ohdyn.automation_guard` reported
  `state=closed_awaiting_preregistration`, `should_noop=true`,
  `repo_write_allowed=false`, and recommended Ben decide whether to authorize
  the minimal deterministic A5.2 smoke scaffold.
- 2026-06-30 06:08 PDT focused regression/smoke tests:
  `.venv-conda/bin/python -m pytest tests/test_run_harness.py::test_automation_guard_opens_for_explicit_bounded_a5_override tests/test_run_harness.py::test_automation_guard_closes_current_a5_when_latest_review_blocks_scaffold tests/test_run_harness.py::test_a5_predictive_control_smoke_records_forecast_metrics tests/test_run_harness.py::test_a5_predictive_control_comparison_runs_matched_conditions tests/test_run_harness.py::test_a5_residual_accounting_analyzes_existing_comparison -q`
  passed (`5 passed`).
- 2026-06-30 06:08 PDT single-run smoke:
  `.venv-conda/bin/python -m ohdyn.run --config configs/a5_predictive_linear_smoke.yaml --seed 5 --out /tmp/omegasim_a5_bounded_linear_smoke_seed5_20260630_0608`
  completed.
- 2026-06-30 06:08 PDT paired comparison:
  `.venv-conda/bin/python -m ohdyn.compare_predictive_control --seeds 5 6 --out /tmp/omegasim_a5_bounded_predictive_compare_seed5_6_20260630_0608`
  completed with 16 single-hive matched-demand run artifacts.
- 2026-06-30 06:08 PDT residual accounting:
  `.venv-conda/bin/python -m ohdyn.analyze_a5_residual_accounting --compare-dir /tmp/omegasim_a5_bounded_predictive_compare_seed5_6_20260630_0608 --out /tmp/omegasim_a5_bounded_residual_accounting_seed5_6_20260630_0608`
  completed with 1280 metric rows and 720 effect rows; promotion decision was
  fail closed for linear, nonlinear, and high-budget nonlinear predictors.
- 2026-06-30 06:08 PDT final guard regression slice:
  `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k automation_guard -q`
  passed (`29 passed, 651 deselected`).
- 2026-06-30 06:08 PDT whitespace check: `git diff --check` passed.
- 2026-06-30 07:09 PDT guard check:
  `.venv-conda/bin/python -m ohdyn.automation_guard` reported
  `state=closed_awaiting_preregistration`, `should_noop=true`,
  `repo_write_allowed=false`, and recommended Ben decide whether to authorize
  the minimal deterministic A5.2 smoke scaffold.
- 2026-06-30 07:09 PDT focused regression/smoke tests:
  `.venv-conda/bin/python -m pytest tests/test_run_harness.py::test_automation_guard_opens_for_explicit_bounded_a5_override tests/test_run_harness.py::test_automation_guard_closes_current_a5_when_latest_review_blocks_scaffold tests/test_run_harness.py::test_a5_predictive_control_smoke_records_forecast_metrics tests/test_run_harness.py::test_a5_predictive_control_comparison_runs_matched_conditions tests/test_run_harness.py::test_a5_residual_accounting_analyzes_existing_comparison -q`
  passed (`5 passed`).
- 2026-06-30 07:09 PDT single-run smoke:
  `.venv-conda/bin/python -m ohdyn.run --config configs/a5_predictive_linear_smoke.yaml --seed 5 --out /tmp/omegasim_a5_bounded_linear_smoke_seed5_20260630_0709`
  completed.
- 2026-06-30 07:09 PDT paired comparison:
  `.venv-conda/bin/python -m ohdyn.compare_predictive_control --seeds 5 6 --out /tmp/omegasim_a5_bounded_predictive_compare_seed5_6_20260630_0709`
  completed with 16 single-hive matched-demand run artifacts.
- 2026-06-30 07:09 PDT residual accounting:
  `.venv-conda/bin/python -m ohdyn.analyze_a5_residual_accounting --compare-dir /tmp/omegasim_a5_bounded_predictive_compare_seed5_6_20260630_0709 --out /tmp/omegasim_a5_bounded_residual_accounting_seed5_6_20260630_0709`
  completed with 1280 metric rows and 720 effect rows; promotion decision was
  fail closed for linear, nonlinear, and high-budget nonlinear predictors.
- 2026-06-30 07:09 PDT final guard regression slice:
  `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k automation_guard -q`
  passed (`29 passed, 651 deselected`).
- 2026-06-30 07:09 PDT whitespace check: `git diff --check` passed.
- 2026-06-30 08:14 PDT focused A5 comparison/analyzer tests:
  `.venv-conda/bin/python -m pytest tests/test_run_harness.py::test_a5_predictive_control_comparison_runs_matched_conditions tests/test_run_harness.py::test_a5_1_charged_comparison_generates_cost_calibration_replay_nulls tests/test_run_harness.py::test_a5_residual_accounting_analyzes_existing_comparison -q`
  passed (`3 passed`).
- 2026-06-30 08:14 PDT guard check:
  `.venv-conda/bin/python -m ohdyn.automation_guard` reported
  `state=closed_awaiting_preregistration`, `should_noop=true`,
  `repo_write_allowed=false`, and recommended Ben decide whether to authorize
  the minimal deterministic A5.2 smoke scaffold.
- 2026-06-30 08:14 PDT focused A5/guard regression set:
  `.venv-conda/bin/python -m pytest tests/test_run_harness.py::test_automation_guard_opens_for_explicit_bounded_a5_override tests/test_run_harness.py::test_automation_guard_closes_current_a5_when_latest_review_blocks_scaffold tests/test_run_harness.py::test_a5_predictive_control_smoke_records_forecast_metrics tests/test_run_harness.py::test_a5_predictive_control_comparison_runs_matched_conditions tests/test_run_harness.py::test_a5_residual_accounting_analyzes_existing_comparison -q`
  passed (`5 passed`).
- 2026-06-30 08:14 PDT syntax check:
  `.venv-conda/bin/python -m py_compile ohdyn/compare_predictive_control.py tests/test_run_harness.py`
  passed.
- 2026-06-30 08:14 PDT single-run smoke:
  `.venv-conda/bin/python -m ohdyn.run --config configs/a5_predictive_linear_smoke.yaml --seed 5 --out /tmp/omegasim_a5_bounded_linear_smoke_seed5_20260630_0814`
  completed.
- 2026-06-30 08:14 PDT paired comparison:
  `.venv-conda/bin/python -m ohdyn.compare_predictive_control --seeds 5 6 --out /tmp/omegasim_a5_bounded_predictive_compare_seed5_6_20260630_0814`
  completed with 16 single-hive matched-demand run artifacts and 16/16
  passing accounting-lock audit rows.
- 2026-06-30 08:14 PDT residual accounting:
  `.venv-conda/bin/python -m ohdyn.analyze_a5_residual_accounting --compare-dir /tmp/omegasim_a5_bounded_predictive_compare_seed5_6_20260630_0814 --out /tmp/omegasim_a5_bounded_residual_accounting_seed5_6_20260630_0814`
  completed with 1280 metric rows and 720 effect rows; promotion decision was
  fail closed for linear, nonlinear, and high-budget nonlinear predictors.
- 2026-06-30 08:14 PDT final guard regression slice:
  `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k automation_guard -q`
  passed (`29 passed, 651 deselected`).
- 2026-06-30 08:14 PDT whitespace check: `git diff --check` passed.

## Blockers

Broader A5 work is blocked by the fail-closed residual/null promotion audit.
The A5.2 preregistration exists, but implementation remains blocked until Ben
explicitly authorizes that gate. Any broader seed sweep, A7-family extension,
or downstream multi-hive coupling still requires a separate preregistration.

## Recommended Next Step

- Recommended next step: Ben should decide whether to authorize the minimal
  deterministic A5.2 smoke scaffold from the preregistered design gate.
