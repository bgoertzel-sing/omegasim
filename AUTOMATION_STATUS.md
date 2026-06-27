# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be
checked from GitHub, including from a phone.

## Current Focus

Ben accepted proceeding to A7 on 2026-06-27, as recorded in
`docs/omegasim_provisional_experiment_roadmap.md`. A5 and A6/A6.1/A6.2 remain
closed under their preregistered decision rules and should not be broadened or
rescued by additional seed sweeps.

A7 is the current preregistered direction: a single-hive semantic-field design
gate for source-accounted semantic/artifact fields and logistic inter-agent
dependence. A minimal opt-in A7 simulator path now exists behind
`semantic_field`; it is a schema/mechanics smoke only, not evidence for
semantic dynamics, lobe structure, attractors, synchrony, or downstream
multi-hive coupling.

The latest external strategic review in
`../outputs/strategy-reviews/omegasim/latest-review.md` recommended a minimal
opt-in A7 delayed semantic-field mechanic with source ledger, costly
prediction, and threshold/fatigue state, followed by a seed-1 six-condition
schema smoke. That recommendation is incorporated. The review header says
`notify_ben: false` and `strategic_change_level: minor`; no Ben notification is
required from the review header.

Do not add real LLM calls, dashboards, Lean, Slack, browser automation,
Atomspace integrations, live task boards, broad three-hive mechanics, or
downstream multi-hive coupling. Do not make attractor, lobe, synchrony, or
semantic-dynamics claims from A7 placeholders.

## Latest Changes

- Added the smallest opt-in A7 simulator mechanics in `ohdyn/sim.py` for runs
  with `semantic_field`: bounded semantic/artifact fields, source-ledger update
  events, delayed logistic or amplitude-matched linear action gating, costly
  prediction that reduces per-tick work budget, and agent threshold/fatigue
  state. Existing A5/A6 mechanics were not broadened.
- Extended A7 run manifests in `ohdyn/io.py` to mark direct A7 simulator
  outputs as `real_simulator_schema_smoke` with
  `schema_complete_smoke_only_no_semantic_dynamics_claim`.
- Tightened `ohdyn/analyze_a7_semantic_field.py` so source reconstruction is
  checked from `events.csv`; the analyzer fails closed if A7 source components
  do not sum to `a7_delta_total`.
- Added a focused seed-1 test for the logistic A7 fixture asserting required
  A7 metric/event fields, exact source reconstruction, nonzero field variation,
  prediction/work-budget competition, and manifest status.
- Ran the six frozen A7 smoke fixtures at seed 1 into `/tmp`; all conditions
  emitted the required schema and passed source reconstruction. The analyzer
  still reports `schema_present_analysis_not_implemented`, so no A7 scientific
  interpretation is allowed.
- No real integrations, dashboards, LLM calls, seed sweeps, broad three-hive
  mechanics, or downstream multi-hive coupling were added.

## Verification

- `.venv-conda/bin/python -m ohdyn.run --config
  configs/a5_predictive_linear_smoke.yaml --seed 5 --out
  /tmp/omegasim_a5_predictive_linear_smoke_20260627` passed.
- `.venv-conda/bin/python -m py_compile ohdyn/compare_predictive_control.py
  ohdyn/analyze_a5_residual_accounting.py ohdyn/automation_guard.py` passed.
- `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k
  'a5_predictive_control or a5_residual_accounting or automation_guard'`
  passed: `12 passed, 600 deselected`.
- `.venv-conda/bin/python -m ohdyn.automation_guard` passed with `state: open`,
  `should_noop: false`, and `closed_reasons: []`.
- `.venv-conda/bin/python -m py_compile ohdyn/automation_guard.py
  ohdyn/a7_semantic_field_contract.py ohdyn/analyze_a7_semantic_field.py
  ohdyn/compare_a7_semantic_field.py` passed.
- `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k
  'a7 or automation_guard'` passed: `16 passed, 596 deselected`.
- `.venv-conda/bin/python -m ohdyn.compare_a7_semantic_field --seeds 1 2
  --out runs/a7_semantic_field_placeholder_smoke_20260627` passed and wrote
  12 config/manifest-only placeholder runs for six frozen A7 conditions.
- `.venv-conda/bin/python -m ohdyn.analyze_a7_semantic_field --compare-dir
  runs/a7_semantic_field_placeholder_smoke_20260627 --out
  runs/a7_semantic_field_analysis_smoke_20260627` passed with
  `status: fail_closed_missing_schema`, `run_count: 12`,
  `condition_count: 6`, and `seed_count: 2`.
- `.venv-conda/bin/python -m py_compile ohdyn/sim.py ohdyn/io.py
  ohdyn/analyze_a7_semantic_field.py tests/test_run_harness.py` passed.
- `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k
  'a7 or automation_guard'` passed: `17 passed, 596 deselected`.
- Six direct A7 seed-1 simulator runs passed:
  `configs/a7_logistic_semantic_coupling_smoke.yaml`,
  `configs/a7_semantic_off_baseline_smoke.yaml`,
  `configs/a7_amplitude_matched_linear_semantic_coupling_smoke.yaml`,
  `configs/a7_source_preserving_semantic_label_shuffle_smoke.yaml`,
  `configs/a7_semantic_field_phase_shuffle_smoke.yaml`, and
  `configs/a7_prediction_budget_timing_broken_matched_count_null_smoke.yaml`
  into `/tmp/omegasim_a7_semantic_field_seed1_smoke_20260627_r2`.
- `.venv-conda/bin/python -m ohdyn.analyze_a7_semantic_field --compare-dir
  /tmp/omegasim_a7_semantic_field_seed1_smoke_20260627_r2 --out
  /tmp/omegasim_a7_semantic_field_seed1_analysis_20260627_r2` passed with
  `status: schema_present_analysis_not_implemented`, `condition_count: 6`,
  `seed_count: 1`, `run_count: 6`, and per-condition
  `source_reconstruction_status: pass`.

## Blockers

None for this bounded A7 schema/mechanics smoke. Scientifically, A7 still has
no residual recurrence analysis, no null contrasts, and no positive evidence;
the new simulator path only proves that the frozen schema and source ledgers can
be emitted and reconstructed for seed 1.

## Recommended Next Step

Implement a read-only A7 seed-1 smoke report/analyzer extension that summarizes
source reconstruction, field variation, prediction/work-budget competition, and
near-threshold occupancy for the six existing A7 artifacts, while continuing to
fail closed on residual recurrence and scientific interpretation.
