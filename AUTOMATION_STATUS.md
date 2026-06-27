# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be
checked from GitHub, including from a phone.

## Current Focus

This run completed the accepted A6.2 96-tick long-horizon validation over
paired seeds `1` and `2`. The previous external strategy review header remains
`strategic_change_level: minor` and `notify_ben: false`; its recommendation to
publish actual A6 analyzer/gate status was accepted and extended through the
current preregistered A6.2 validation.

A0/A1 and A5 remain complete and should not be duplicated. A5 remains closed:
bounded predictors improved forecast skill, but the seed `7..16` evidence did
not pass the full-accounting residual structure gate. A6.2 now also closes
conservatively: the 96-tick validation passed schema/computation checks, but
logistic did not beat linear and both source-preserving nulls on the same
target with paired cross-seed agreement. The result is tracked in
`docs/results/a6_2_long_horizon_validation_seed1_2.md`.

Do not add real LLM calls, dashboards, Lean, Slack, browser automation,
Atomspace integrations, live task boards, broad three-hive mechanics, or
downstream multi-hive coupling. Do not broaden seeds, change A6 mechanisms, or
use attractor/lobe-like promotion language unless a later accepted
preregistration explicitly supersedes the conservative A6.2 closure.

## Latest Changes

- Added fixed 96-tick A6.2 validation configs:
  `configs/a6_2_long_horizon_logistic.yaml`,
  `configs/a6_2_long_horizon_linear.yaml`,
  `configs/a6_2_long_horizon_phase_shuffled.yaml`, and
  `configs/a6_2_long_horizon_threshold_shuffled.yaml`.
- Added `ohdyn.compare_a6_2_long_horizon`, a bounded wrapper that runs only
  paired seeds `1` and `2`, includes the two existing source-preserving null
  artifacts, and rejects seed broadening.
- Ran the fixed comparison and the existing read-only A6.2 analyzer, producing
  `runs/a6_2_long_horizon_compare_seed1_2` and
  `runs/a6_2_long_horizon_residual_recurrence_seed1_2`.
- Published `docs/results/a6_2_long_horizon_validation_seed1_2.md` and updated
  `README.md` with the completed conservative A6.2 validation status.
- Fixed one A6 long-horizon robustness bug: A6 softmax action selection can no
  longer choose unavailable `work_task` when the queue is empty. This matches
  the baseline selector's work availability behavior.
- Fixed one read-only A6.2 analyzer bookkeeping bug so artifact metric fields
  map to event source fields such as `artifact_readiness`, allowing dominant
  artifact-update source shares to be reported.
- Attempted the urgent strategy-review command because the validation changes
  the A6.2 decision state, but it was throttled:
  `strategy review skipped for omegasim: last failed attempt age 702s < 1800s`.
  No newer review superseded the existing minor recommendation.

## Verification

- `.venv-conda/bin/python -m ohdyn.automation_guard` passed and reported
  `state=open`, `should_noop=false`, `strategic_change_level=minor`, and
  `notify_ben=false`; its review text is stale relative to this completed
  A6.2 validation, but the prior recommendation has been satisfied.
- `.venv-conda/bin/python -m ohdyn.compare_a6_2_long_horizon --seeds 1 2
  --out runs/a6_2_long_horizon_compare_seed1_2` passed.
- `.venv-conda/bin/python -m ohdyn.analyze_a6_2_residual_recurrence
  --compare-dir runs/a6_2_long_horizon_compare_seed1_2 --out
  runs/a6_2_long_horizon_residual_recurrence_seed1_2` passed.
- The A6.2 analyzer wrote: `manifest=1`, `paired_seed_completeness=12`,
  `residual_recurrence_metrics=156`, and `residual_recurrence_deltas=130`
  rows. Status counts were `complete=12`, `computed=156`,
  `closure_no_recurrence_advantage=98`, and
  `eligible_for_cross_seed_direction_check=32`; overall status was
  `conservative_closure`.
- `.venv-conda/bin/python -m py_compile ohdyn/sim.py
  ohdyn/compare_a6_logistic_appraisal.py ohdyn/compare_a6_2_long_horizon.py
  ohdyn/analyze_a6_2_residual_recurrence.py` passed.
- `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k
  'a6_2_long_horizon or
  a6_1_comparison_derives_source_preserving_nulls_and_gate or
  a6_smoke_comparison_helper_runs_only_preregistered_fixtures'` passed:
  `3 passed, 600 deselected`.

## Blockers

None for the completed validation run. Scientifically, A6.2 did not pass its
promotion/eligibility gate and should not be broadened or reinterpreted without
a new accepted preregistration.

## Recommended Next Step

Create a short A6.2 closure addendum that freezes the conservative
interpretation and explicitly blocks further single-hive A6 seed broadening or
mechanism work unless Ben accepts a new preregistered direction.
