# A6 Analysis Gate, Seeds 1-2

Run date: 2026-06-27.

This note records the bounded read-only A6 analyzer gate over the existing
seed `1..2` logistic-appraisal smoke artifacts. It resolves the strategy-review
request to publish the current analyzer outputs before adding seeds,
mechanisms, or interpretation. It is a control/accounting audit, not promotion
evidence.

## Inputs

```bash
.venv-conda/bin/python -m ohdyn.analyze_a6_logistic_appraisal \
  --compare-dir runs/a6_logistic_appraisal_compare \
  --out runs/a6_logistic_appraisal_analysis_gate_seed1_2_rerun_20260627
```

The analyzer consumed `runs/a6_logistic_appraisal_compare` without rerunning
simulations. The comparison directory contained all four preregistered smoke
conditions crossed with seeds `1` and `2`:

```text
logistic
linear
phase_shuffled
threshold_shuffled
```

## Generated Analysis Artifacts

The ignored analysis directory contains the current analyzer outputs:

```text
runs/a6_logistic_appraisal_analysis_gate_seed1_2_rerun_20260627/a6_logistic_appraisal_endpoints.csv
runs/a6_logistic_appraisal_analysis_gate_seed1_2_rerun_20260627/a6_logistic_appraisal_manifest.csv
runs/a6_logistic_appraisal_analysis_gate_seed1_2_rerun_20260627/a6_logistic_appraisal_control_deltas.csv
runs/a6_logistic_appraisal_analysis_gate_seed1_2_rerun_20260627/a6_logistic_appraisal_control_summary.csv
runs/a6_logistic_appraisal_analysis_gate_seed1_2_rerun_20260627/a6_logistic_appraisal_residual_preflight.csv
runs/a6_logistic_appraisal_analysis_gate_seed1_2_rerun_20260627/a6_logistic_appraisal_residual_timeseries.csv
runs/a6_logistic_appraisal_analysis_gate_seed1_2_rerun_20260627/a6_logistic_appraisal_residual_contrast_summary.csv
runs/a6_logistic_appraisal_analysis_gate_seed1_2_rerun_20260627/a6_logistic_appraisal_residual_contrast_rollup.csv
runs/a6_logistic_appraisal_analysis_gate_seed1_2_rerun_20260627/a6_logistic_appraisal_comparison_consistency.csv
runs/a6_logistic_appraisal_analysis_gate_seed1_2_rerun_20260627/a6_logistic_appraisal_effects_consistency.csv
runs/a6_logistic_appraisal_analysis_gate_seed1_2_rerun_20260627/a6_logistic_appraisal_artifact_provenance.csv
runs/a6_logistic_appraisal_analysis_gate_seed1_2_rerun_20260627/a6_logistic_appraisal_source_accounting.csv
runs/a6_logistic_appraisal_analysis_gate_seed1_2_rerun_20260627/a6_1_pilot_null_gate.csv
runs/a6_logistic_appraisal_analysis_gate_seed1_2_rerun_20260627/summary.md
```

Row counts, excluding header rows:

```text
endpoints: 8
manifest: 9
control_deltas: 6
control_summary: 42
residual_preflight: 112
residual_timeseries: 1792
residual_contrast_summary: 84
residual_contrast_rollup: 42
comparison_consistency: 4
effects_consistency: 3
artifact_provenance: 80
source_accounting: 80
A6.1 pilot null gate: 0
```

Required endpoint/control fields were present for the paired-delta and
residual-control gate. The residual-control preflight reported no missing
control fields.

The source-accounting rows are different: all 80 rows are marked
`missing_required_fields` because the canonical
`runs/a6_logistic_appraisal_compare` smoke artifacts were generated before the
A6.1 artifact-update source fields were added. Missing source-accounting
fields:

```text
a6_action_opportunity_tick
a6_artifact_delta_ambient
a6_artifact_delta_clip_residual
a6_artifact_delta_handoff_attempt
a6_artifact_delta_handoff_failure
a6_artifact_delta_handoff_success
a6_artifact_delta_noise
a6_artifact_delta_prediction_error
a6_artifact_delta_prediction_expenditure
a6_artifact_delta_queue_work_accounting
a6_artifact_delta_total
a6_artifact_delta_unclipped
a6_artifact_field
a6_artifact_update_source
a6_prediction_actions_tick
a6_prediction_budget_available_tick
a6_prediction_error_mean_tick
a6_queue_depth_tick
a6_service_capacity_tick
a6_work_actions_tick
```

The A6.1 pilot-null gate emitted zero rows because this older four-condition
comparison does not include the two source-preserving null conditions:
`source_label_shuffled_within_tick` and
`handoff_success_timing_broken_matched_counts`.

## Endpoint Means

```text
condition            artifact_utility   queue_depth   completion_fraction   action_opportunity
linear               0.319338           19.000        0.356897              240.0
logistic             0.321045           20.500        0.338710              240.0
phase_shuffled       0.155530           22.500        0.279166              240.0
threshold_shuffled   0.285925           22.000        0.277420              240.0
```

## Paired Control Deltas

Mean deltas are logistic minus the named control.

```text
contrast                         paired_seeds   artifact_utility_delta   queue_depth_delta   completion_fraction_delta
logistic_vs_linear               2              0.001707                 1.5                 -0.018187
logistic_vs_phase_shuffled       2              0.165515                 -2.0                0.059544
logistic_vs_threshold_shuffled   2              0.035120                 -1.5                0.061291
```

Per-seed logistic-versus-linear deltas disagree in sign:

```text
seed 1: artifact_utility_delta =  0.032000, queue_depth_delta = 0.0
seed 2: artifact_utility_delta = -0.028586, queue_depth_delta = 3.0
```

This keeps the logistic-versus-linear result in the accounting-risk category.
The tiny positive mean artifact-utility delta is accompanied by higher mean
queue depth and lower mean completion fraction.

## Residual Gate

All residual preflight, control-summary, and residual-rollup rows are marked
`underdetermined_smoke_scale`. These rows exercise the residual accounting path
but do not establish recurrence or nonlinear collective structure.

Artifact-utility residual rollup:

```text
contrast                         residual_variance_delta   residual_lag1_autocorrelation_delta
logistic_vs_linear               0.000024                  -0.026647
logistic_vs_phase_shuffled      -0.000092                  -0.015395
logistic_vs_threshold_shuffled   0.000044                  -0.198169
```

The comparison and effects consistency preflights were all `consistent` with
maximum absolute difference `0.0`, so the aggregate comparison/effects CSVs
match the run-directory-derived endpoint arithmetic.

## Provenance and Source Accounting

Artifact-provenance alias-risk rows from the old smoke artifacts:

```text
mixed_or_low_alias_risk_smoke: 6
high_action_alias_risk: 57
action_coupled_smoke: 2
no_change: 15
```

Source-accounting status over the old smoke artifacts:

```text
required_field_status:
  missing_required_fields: 80

reconstruction_status:
  missing_required_fields: 80

status:
  missing_required_fields: 80
```

This means the canonical seed `1..2` four-condition comparison directory is
adequate for endpoint/control-delta/residual smoke-gate validation, but not
adequate for interpreting A6.1 source accounting or source-preserving nulls.
The separate `docs/results/a6_1_pilot_null_gate_seed1_2.md` and
`docs/results/a6_2_residual_recurrence_gate_seed1_2.md` remain the relevant
tracked reports for source-field-complete artifacts and fail-closed recurrence
analysis.

## Interpretation

A6 has a read-only analysis gate that reports paired control deltas,
missing-field status, residual preflights, residual timeseries, residual
contrast summaries, comparison/effects consistency, artifact provenance, source
accounting, and pilot-null gate status from existing artifacts.

The seed `1..2` smoke artifacts do not promote A6. They are useful for
endpoint/control-delta/residual analyzer validation only. Logistic does not
cleanly beat the amplitude-matched linear control after accounting: the
artifact-utility mean delta is tiny, seed signs disagree, queue depth is
higher, and completion fraction is lower. The shuffle-control deltas remain
smoke-scale because the residual gate is underdetermined.

The analyzer/status mismatch identified by the external strategy review is
resolved for this gate. The scientifically sensible GPT-5.5-Pro recommendation
was accepted: no new seeds or mechanisms were added before publishing the
actual A6 analyzer output status. The next scientific move remains the accepted
A6.2 longer-horizon validation from
`docs/a6_2_long_horizon_validation_preregistration.md`; do not broaden seeds,
change mechanisms, add downstream coupling, or promote A6 in the same step.
