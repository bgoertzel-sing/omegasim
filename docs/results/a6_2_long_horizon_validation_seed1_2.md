# A6.2 Long-Horizon Validation, Seeds 1-2

Run date: 2026-06-27.

This report records the fixed 96-tick A6.2 validation preregistered in
`docs/a6_2_long_horizon_validation_preregistration.md`. It stayed single-hive,
used only paired seeds `1` and `2`, did not broaden seeds, did not add
mechanisms, and did not add any external integrations.

## Command Bundle

```bash
.venv-conda/bin/python -m ohdyn.compare_a6_2_long_horizon \
  --seeds 1 2 \
  --out runs/a6_2_long_horizon_compare_seed1_2

.venv-conda/bin/python -m ohdyn.analyze_a6_2_residual_recurrence \
  --compare-dir runs/a6_2_long_horizon_compare_seed1_2 \
  --out runs/a6_2_long_horizon_residual_recurrence_seed1_2
```

Verification commands run during the implementation:

```bash
.venv-conda/bin/python -m py_compile \
  ohdyn/sim.py \
  ohdyn/compare_a6_logistic_appraisal.py \
  ohdyn/compare_a6_2_long_horizon.py \
  ohdyn/analyze_a6_2_residual_recurrence.py

.venv-conda/bin/python -m pytest tests/test_run_harness.py \
  -k 'a6_2_long_horizon or a6_1_comparison_derives_source_preserving_nulls_and_gate or a6_smoke_comparison_helper_runs_only_preregistered_fixtures'
```

## Configs

The tracked validation configs are:

```text
configs/a6_2_long_horizon_logistic.yaml
configs/a6_2_long_horizon_linear.yaml
configs/a6_2_long_horizon_phase_shuffled.yaml
configs/a6_2_long_horizon_threshold_shuffled.yaml
```

They are mechanical derivatives of the existing A6 smoke fixtures. The only
intended changes are:

```text
run.experiment_id: a6_2_long_horizon_<condition>
run.ticks: 96
```

The two source-preserving null conditions are derived by
`ohdyn.compare_a6_2_long_horizon` from the paired logistic artifacts, using the
existing A6.1 null transforms:

```text
source_label_shuffled_within_tick
handoff_success_timing_broken_matched_counts
```

## Artifact Inventory

The comparison directory contains 12 deterministic run artifact directories:

```text
6 conditions x 2 paired seeds = 12 runs
```

The six observed conditions are:

```text
logistic
linear
threshold_shuffled
phase_shuffled
source_label_shuffled_within_tick
handoff_success_timing_broken_matched_counts
```

The analysis directory contains:

```text
runs/a6_2_long_horizon_residual_recurrence_seed1_2/a6_2_manifest.csv
runs/a6_2_long_horizon_residual_recurrence_seed1_2/a6_2_paired_seed_completeness.csv
runs/a6_2_long_horizon_residual_recurrence_seed1_2/a6_2_residual_recurrence_metrics.csv
runs/a6_2_long_horizon_residual_recurrence_seed1_2/a6_2_residual_recurrence_deltas.csv
runs/a6_2_long_horizon_residual_recurrence_seed1_2/summary.md
```

Row counts, excluding headers:

```text
manifest: 1
paired_seed_completeness: 12
residual_recurrence_metrics: 156
residual_recurrence_deltas: 130
```

## Gate Counts

All 12 run artifacts passed required metric/control/source-field completeness.
All 156 recurrence rows computed. All 130 paired delta rows computed.

```text
required field status: complete=12
recurrence row status: computed=156
delta gate status: closure_no_recurrence_advantage=98, eligible_for_cross_seed_direction_check=32
overall analyzer status: conservative_closure
```

## Endpoint Means

Condition means from `a6_logistic_appraisal_comparison_metrics.csv`:

| condition | artifact utility | readiness | completed | queue depth |
| --- | ---: | ---: | ---: | ---: |
| logistic | 0.640791 | 0.560987 | 104.5 | 26.0 |
| linear | 0.639317 | 0.561587 | 106.0 | 31.5 |
| threshold_shuffled | 0.606659 | 0.560987 | 102.5 | 26.0 |
| phase_shuffled | 0.607622 | 0.560609 | 101.5 | 34.5 |
| source_label_shuffled_within_tick | 0.640791 | 0.560987 | 104.5 | 26.0 |
| handoff_success_timing_broken_matched_counts | 0.655291 | 0.560987 | 104.5 | 26.0 |

Logistic minus linear endpoint deltas:

```text
artifact_utility: +0.001474
queue_depth: -5.5
completion_fraction: +0.025453
```

Logistic did not beat the source-preserving nulls on artifact utility:

```text
logistic - source_label_shuffled_within_tick: 0.0
logistic - handoff_success_timing_broken_matched_counts: -0.0145
```

## Recurrence Deltas

Selected delay-embedded recurrence-rate deltas:

| target | contrast | seed | recurrence delta | productivity delta | gate |
| --- | --- | ---: | ---: | ---: | --- |
| readiness | logistic_vs_linear | 1 | -0.002687 | +0.012075 | closure_no_recurrence_advantage |
| readiness | logistic_vs_linear | 2 | +0.010526 | +0.013984 | eligible_for_cross_seed_direction_check |
| readiness | logistic_vs_source_label_shuffled_within_tick | 1 | 0.0 | 0.0 | closure_no_recurrence_advantage |
| readiness | logistic_vs_source_label_shuffled_within_tick | 2 | 0.0 | 0.0 | closure_no_recurrence_advantage |
| readiness | logistic_vs_handoff_success_timing_broken_matched_counts | 1 | -0.014557 | 0.0 | closure_no_recurrence_advantage |
| readiness | logistic_vs_handoff_success_timing_broken_matched_counts | 2 | -0.004928 | 0.0 | closure_no_recurrence_advantage |
| implementation_maturity | logistic_vs_linear | 1 | -0.017021 | +0.012075 | closure_no_recurrence_advantage |
| implementation_maturity | logistic_vs_linear | 2 | -0.005375 | +0.013984 | closure_no_recurrence_advantage |
| latent_activation | logistic_vs_linear | 1 | -0.00224 | +0.012075 | closure_no_recurrence_advantage |
| latent_activation | logistic_vs_linear | 2 | +0.002912 | +0.013984 | eligible_for_cross_seed_direction_check |

Rows marked `eligible_for_cross_seed_direction_check` are not promotion
evidence. They only mean that a single paired row beat one control on the
analyzer's recurrence-rate field without productivity degradation. The
preregistered gate requires the same target variable to beat linear and both
source-preserving nulls with cross-seed agreement. That did not happen.

## Dominant Artifact-Update Sources

For the logistic condition, dominant source shares were:

| artifact target | seed 1 dominant source | seed 1 share | seed 2 dominant source | seed 2 share |
| --- | --- | ---: | --- | ---: |
| novelty | noise | 0.64967 | noise | 0.619294 |
| coherence | handoff_success | 1.0 | handoff_success | 0.666667 |
| actionability | handoff_success | 1.0 | handoff_success | 1.0 |
| provenance_debt | handoff_success | 0.504739 | handoff_success | 0.504375 |
| risk | handoff_success | 0.509804 | handoff_success | 0.508011 |
| contradiction | handoff_failure | 0.509289 | handoff_success | 0.49846 |
| readiness | handoff_success | 0.398327 | handoff_success | 0.413626 |
| implementation_maturity | handoff_success | 0.511811 | handoff_success | 0.515571 |
| communication_maturity | none | 0.0 | none | 0.0 |

This source profile reinforces the conservative decision: the most relevant
artifact endpoints remain substantially explained by handoff-success or
handoff-failure accounting, not by a source-independent residual recurrence
signal.

## Implementation Notes

The 96-tick validation exposed one simulator robustness bug: A6 softmax action
selection could still choose `work_task` when no queued task existed because
the action was heavily penalized but not impossible. The fix makes unavailable
`work_task` impossible in the A6 selector, matching the baseline selector's
availability behavior. No new A6 mechanisms, actions, artifact fields, seeds,
or external integrations were added.

The A6.2 analyzer also had a source-share naming bug:
`a6_artifact_readiness_tick` was mapped to `readiness` while event rows record
`artifact_readiness`. The fix is read-only analyzer bookkeeping and is covered
by the long-horizon test.

## Decision

A6.2 closes conservatively for this validation. The source schema passed and
the recurrence analyzer computed at 96 ticks, but logistic did not beat linear
and both source-preserving nulls on the same target variable with paired
cross-seed agreement. Source-preserving null deltas were zero or worse for the
sampled artifact targets, and dominant artifact-source shares remain tied to
handoff accounting.

Do not promote A6, broaden seeds, add mechanisms, or move to downstream
multi-hive coupling from this result.

The urgent strategy-review command was attempted because this validation
changes the research decision state, but it was throttled:

```text
strategy review skipped for omegasim: last failed attempt age 702s < 1800s
```

No newer strategy review superseded the existing minor review.
