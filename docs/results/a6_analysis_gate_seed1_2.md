# A6 Analysis Gate, Seeds 1-2

Run date: 2026-06-27.

This note records the bounded read-only A6 analyzer gate over the existing
seed `1..2` logistic-appraisal smoke artifacts. It is a control/accounting
audit, not promotion evidence.

## Inputs

```bash
.venv-conda/bin/python -m ohdyn.analyze_a6_logistic_appraisal \
  --compare-dir runs/a6_logistic_appraisal_compare \
  --out runs/a6_logistic_appraisal_analysis
```

The analyzer consumed `runs/a6_logistic_appraisal_compare` without rerunning
simulations. The comparison directory contained all four preregistered smoke
conditions, crossed with seeds `1` and `2`:

```text
logistic
linear
phase_shuffled
threshold_shuffled
```

## Generated Analysis Artifacts

The ignored analysis directory now contains the current analyzer outputs:

```text
runs/a6_logistic_appraisal_analysis/a6_logistic_appraisal_endpoints.csv
runs/a6_logistic_appraisal_analysis/a6_logistic_appraisal_manifest.csv
runs/a6_logistic_appraisal_analysis/a6_logistic_appraisal_control_deltas.csv
runs/a6_logistic_appraisal_analysis/a6_logistic_appraisal_control_summary.csv
runs/a6_logistic_appraisal_analysis/a6_logistic_appraisal_residual_preflight.csv
runs/a6_logistic_appraisal_analysis/a6_logistic_appraisal_residual_timeseries.csv
runs/a6_logistic_appraisal_analysis/a6_logistic_appraisal_residual_contrast_summary.csv
runs/a6_logistic_appraisal_analysis/a6_logistic_appraisal_residual_contrast_rollup.csv
runs/a6_logistic_appraisal_analysis/a6_logistic_appraisal_comparison_consistency.csv
runs/a6_logistic_appraisal_analysis/a6_logistic_appraisal_effects_consistency.csv
runs/a6_logistic_appraisal_analysis/summary.md
```

Row counts, excluding header rows:

```text
comparison_metrics: 4
effects: 3
endpoints: 8
manifest: 7
control_deltas: 6
control_summary: 42
residual_preflight: 112
residual_timeseries: 1792
residual_contrast_summary: 84
residual_contrast_rollup: 42
comparison_consistency: 4
effects_consistency: 3
```

Required accounting fields were present. The analyzer reported no missing
required fields and no missing residual-control fields.

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
logistic_vs_threshold_shuffled   2              0.035120                 -1.5                0.061290
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

## Interpretation

A6 now has a read-only analysis gate that reports paired control deltas,
missing-field status, residual preflights, residual timeseries, residual
contrast summaries, and comparison/effects consistency checks from the existing
smoke artifacts.

The seed `1..2` smoke artifacts do not promote A6. They are useful for schema
and analyzer validation only. Logistic does not cleanly beat the
amplitude-matched linear control after accounting: the artifact-utility mean
delta is tiny, seed signs disagree, queue depth is higher, and completion
fraction is lower. The shuffle-control deltas remain smoke-scale because the
residual gate is underdetermined.

Next scientific move should be schema/provenance strengthening before any
larger A6 run: add an artifact-update provenance audit that attributes each
artifact-field change to action/event sources, so artifact utility and
readiness can be tested for action-count/queue aliases before any A6.1 pilot.
