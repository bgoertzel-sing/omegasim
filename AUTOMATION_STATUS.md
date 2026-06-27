# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be
checked from GitHub, including from a phone.

## Current Focus

A5 is closed under its preregistered accounting evidence. The seed `7..16`
closure records in `docs/results/a5_eight_condition_closure_update_seed7_16.md`
and `docs/results/a5_closure_note_seed7_16.md` are the current A5
interpretation: prediction manipulations improved forecast skill, but residual
structure did not survive full accounting and paired null checks. Do not reopen
A5 for additional seeds, mechanics, or residual/lobe/attractor claims without a
new preregistration.

A7 is the active gated direction accepted by Ben on 2026-06-27. It is a
single-hive semantic-field design gate for source-accounted semantic/artifact
fields and logistic inter-agent dependence. Existing A7 artifacts are
schema/mechanics or validation-gate evidence only: they do not support semantic
dynamics, lobe structure, attractors, synchrony, or downstream multi-hive
coupling.

The latest urgent external strategic review in
`../outputs/strategy-reviews/omegasim/latest-review.md` reported
`strategic_change_level: major` and `notify_ben: true`. The direction shift is
to stop the A5 re-open loop, record A5 as closed/accounting-explained, restore
A7 as the active gated smoke/validation path, and notify Ben that the
status/README drift was corrected.

Do not add real LLM calls, dashboards, Lean, Slack, browser automation,
Atomspace integrations, live task boards, broad three-hive mechanics, or
downstream multi-hive coupling.

## Latest Changes

- This bounded automation run re-read the repository source of truth and the
  urgent external strategic review. It did not duplicate A0/A1, reopen A5,
  rerun A7 validation, broaden seeds, add mechanics, or add downstream
  multi-hive coupling.
- The current source of truth remains unchanged: A5 is closed under seed
  `7..16` accounting evidence, A7 is the active gated direction, and the
  completed A7 seed `1..2` long-horizon validation is
  `fail_closed_residual_null_gate`.
- Further experimental progress is blocked by research direction, not by the
  local environment: Ben's decision or a new preregistration is required before
  any A7 redesign, seed broadening, mechanism changes, or downstream
  multi-hive coupling.
- Added `docs/results/a7_ben_notification_status_20260627.md` as the bounded
  Ben-facing notification record requested by the current automation status and
  the urgent strategic review. It states that A5 is closed/accounting-explained,
  A7 seed `1..2` long-horizon validation is
  `fail_closed_residual_null_gate`, and a new preregistration is required
  before A7 redesign, seed broadening, mechanism changes, or downstream
  multi-hive coupling.
- No simulator mechanics, analyzer logic, configs, dashboards, real
  integrations, seed sweeps, A5 reruns, A7 reruns, broad three-hive mechanics,
  or downstream multi-hive coupling were added in this notification pass.
- Added `docs/results/a7_long_horizon_residual_null_validation_seed1_2.md`
  from the completed `/tmp/omegasim_a7_long_horizon_*_20260627` comparison and
  analysis artifacts. The report records the preregistered 96-tick, six-
  condition, paired-seed A7 validation as
  `fail_closed_residual_null_gate`: schema/source reconstruction, field
  variation, prediction/work-budget competition, and all residual rows
  computed, but the logistic condition did not beat all controls with
  paired-seed agreement and non-worse productivity.
- During the documentation pass, the comparison helper was not rerun because
  `/tmp/omegasim_a7_long_horizon_compare_20260627` already contained A7
  artifacts and refused overwrite. The existing analyzer summary was read
  directly.
- Created the fixed 96-tick A7 long-horizon validation configs for all six
  preregistered conditions under `configs/a7_long_horizon_*.yaml`. They derive
  mechanically from the smoke fixtures: only `run.experiment_id` and
  `run.ticks` change.
- Added the bounded A7 long-horizon comparison helper. `python -m
  ohdyn.compare_a7_long_horizon --seeds 1 2 --out
  runs/a7_long_horizon_compare_seed1_2` runs the six preregistered A7
  conditions for paired seeds `1` and `2`, writes normal deterministic
  simulator artifacts, and records an artifact manifest without changing
  simulator mechanics.
- Updated the A7 README command block to point at
  `ohdyn.compare_a7_long_horizon` plus the existing read-only
  `ohdyn.analyze_a7_semantic_field` analyzer.
- Verified the new long-horizon comparison and analyzer on `/tmp` artifacts.
  The result remains fail-closed as `fail_closed_residual_null_gate`: all
  source schemas and residual rows computed, but null/productivity gates block
  semantic-dynamics interpretation.
- No simulator mechanics, dashboards, real integrations, seed sweeps, broad
  three-hive mechanics, or downstream multi-hive coupling were added.

## Verification

- `git status --short` initially reported a clean worktree.
- Re-read `README.md`, `AUTOMATION_STATUS.md`, available configs/tests,
  `docs/omegasim_provisional_experiment_roadmap.md`, and
  `../outputs/strategy-reviews/omegasim/latest-review.md`.
- `.venv-conda/bin/python -m ohdyn.automation_guard` reported state `open`,
  `strategic_change_level: major`, `notify_ben: true`, and recommended next
  action: wait for Ben's decision or a new preregistration before any A7
  redesign, seed broadening, mechanism changes, or downstream multi-hive
  coupling.
- `tail -40 ../outputs/omegasim-cli-loop.log` showed recent loop completions
  and no newer local blocker than the current strategic hold.
- No simulator or analyzer code changed in this run, so no code test was
  required before stopping at the documented research-direction blocker.
- `git status --short --branch` initially reported a clean worktree on
  `main...origin/main`.
- `.venv-conda/bin/python -m ohdyn.automation_guard` reported state `open`,
  `strategic_change_level: major`, `notify_ben: true`, and recommended
  notifying Ben that A5 remains closed/accounting-explained, A7 is documented
  as `fail_closed_residual_null_gate` for the preregistered seed `1..2`
  long-horizon validation, and a new preregistration is required before A7
  redesign, seed broadening, or downstream multi-hive coupling.
- `tail -40 ../outputs/omegasim-cli-loop.log` showed recent loop completions
  and an older dirty-worktree snapshot from earlier A5 work; current git status
  remained clean before this run's edits.
- `.venv-conda/bin/python -m ohdyn.automation_guard` passed after the
  notification update. It reported state `open`, `strategic_change_level:
  major`, `notify_ben: true`, and the recommended next action: wait for Ben's
  decision or a new preregistration before any A7 redesign, seed broadening,
  mechanism changes, or downstream multi-hive coupling.
- `.venv-conda/bin/python -m py_compile ohdyn/automation_guard.py
  ohdyn/analyze_a7_semantic_field.py ohdyn/compare_a7_long_horizon.py
  ohdyn/a7_semantic_field_contract.py` passed.
- `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k
  'a7 or automation_guard'` passed: `21 passed, 596 deselected`.
- Previous A7 validation pass: `git status --short --branch` initially reported
  a clean worktree on
  `main...origin/main`.
- Previous A7 validation pass: `.venv-conda/bin/python -m
  ohdyn.automation_guard` reported state `open`, `strategic_change_level:
  major`, `notify_ben: true`, and recommended writing the A7 long-horizon
  validation report from the completed `/tmp` artifacts.
- `.venv-conda/bin/python -m ohdyn.compare_a7_long_horizon --seeds 1 2 --out
  /tmp/omegasim_a7_long_horizon_compare_20260627` was attempted for artifact
  verification and stopped before rerun with the expected refusal: the output
  path already contained A7 comparison artifacts.
- Read `/tmp/omegasim_a7_long_horizon_analysis_20260627/summary.md` and the
  analyzer CSVs. Summary status remained `fail_closed_residual_null_gate` with
  `12` runs inspected, source reconstruction pass rows `12`, field variation
  pass rows `12`, prediction/work-budget competition pass rows `12`, residual
  row status `computed=72`, and null-contrast gate status
  `eligible_for_cross_seed_direction_check=13`,
  `fail_closed_no_nonlinear_forecastability_advantage=7`,
  `fail_closed_no_residual_autocorrelation_advantage=22`,
  `fail_closed_productivity_degrades=18`.
- `.venv-conda/bin/python -m py_compile ohdyn/compare_a7_semantic_field.py
  ohdyn/compare_a7_long_horizon.py ohdyn/analyze_a7_semantic_field.py
  ohdyn/a7_semantic_field_contract.py` passed after adding the A7 validation
  report.
- `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k
  'a7 or automation_guard'` passed after adding the A7 validation report:
  `21 passed, 596 deselected`.
- `.venv-conda/bin/python -m ohdyn.compare_a7_long_horizon --seeds 1 2 --out
  /tmp/omegasim_a7_long_horizon_compare_20260627` passed and wrote 12 normal
  run artifact directories with 96 metric rows each.
- `.venv-conda/bin/python -m ohdyn.analyze_a7_semantic_field --compare-dir
  /tmp/omegasim_a7_long_horizon_compare_20260627 --out
  /tmp/omegasim_a7_long_horizon_analysis_20260627` passed. Analyzer summary:
  status `fail_closed_residual_null_gate`, runs inspected `12`, source
  reconstruction pass rows `12`, field variation pass rows `12`,
  prediction/work-budget competition pass rows `12`, residual row status
  `computed=72`, and null-contrast gate status
  `eligible_for_cross_seed_direction_check=13`,
  `fail_closed_no_nonlinear_forecastability_advantage=7`,
  `fail_closed_no_residual_autocorrelation_advantage=22`,
  `fail_closed_productivity_degrades=18`.

## Blockers

Ben notification has been packaged in
`docs/results/a7_ben_notification_status_20260627.md`, but further research
direction is intentionally blocked on Ben's decision or a new preregistration.
There is no code, test, or local environment blocker.

## Recommended Next Step

Wait for Ben's decision or a new preregistration before any A7 redesign, seed
broadening, mechanism changes, or downstream multi-hive coupling.
