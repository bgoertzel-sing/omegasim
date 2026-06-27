# A7 Long-Horizon Residual/Null Validation, Seeds 1-2

Run date: 2026-06-27.

This report records the fixed 96-tick A7 validation preregistered in
`docs/a7_long_horizon_residual_null_validation_preregistration.md`. It stayed
single-hive, used only paired seeds `1` and `2`, did not broaden seeds, did not
add mechanisms, and did not add external integrations.

The artifacts inspected here are the completed `/tmp` comparison and analysis
directories referenced by `AUTOMATION_STATUS.md`:

```text
/tmp/omegasim_a7_long_horizon_compare_20260627
/tmp/omegasim_a7_long_horizon_analysis_20260627
```

During this documentation pass, the comparison command was not rerun because
the comparison directory already contained A7 artifacts and the helper refused
to overwrite them.

## Command Bundle

The recorded artifact set corresponds to:

```bash
.venv-conda/bin/python -m ohdyn.compare_a7_long_horizon \
  --seeds 1 2 \
  --out /tmp/omegasim_a7_long_horizon_compare_20260627

.venv-conda/bin/python -m ohdyn.analyze_a7_semantic_field \
  --compare-dir /tmp/omegasim_a7_long_horizon_compare_20260627 \
  --out /tmp/omegasim_a7_long_horizon_analysis_20260627
```

The tracked README command uses the same fixed comparison/analyzer pair with
`runs/a7_long_horizon_compare_seed1_2` and
`runs/a7_long_horizon_residual_null_analysis_seed1_2` as repository-local
output paths.

## Configs

The tracked validation configs are:

```text
configs/a7_long_horizon_logistic_semantic_coupling.yaml
configs/a7_long_horizon_semantic_off_baseline.yaml
configs/a7_long_horizon_amplitude_matched_linear_semantic_coupling.yaml
configs/a7_long_horizon_source_preserving_semantic_label_shuffle.yaml
configs/a7_long_horizon_semantic_field_phase_shuffle.yaml
configs/a7_long_horizon_prediction_budget_timing_broken_matched_count_null.yaml
```

They are mechanical derivatives of the checked-in A7 smoke fixtures. The only
intended changes are:

```text
run.experiment_id: a7_long_horizon_<condition>
run.ticks: 96
```

## Artifact Inventory

The comparison directory contains 12 deterministic run artifact directories:

```text
6 conditions x 2 paired seeds = 12 runs
```

Each run artifact has 96 metric rows. The six observed conditions are:

```text
a7_logistic_semantic_coupling
semantic_off_baseline
amplitude_matched_linear_semantic_coupling
source_preserving_semantic_label_shuffle
semantic_field_phase_shuffle
prediction_budget_timing_broken_matched_count_null
```

The analysis directory contains:

```text
/tmp/omegasim_a7_long_horizon_analysis_20260627/a7_semantic_field_completeness.csv
/tmp/omegasim_a7_long_horizon_analysis_20260627/a7_semantic_field_manifest.csv
/tmp/omegasim_a7_long_horizon_analysis_20260627/a7_semantic_field_residual_metrics.csv
/tmp/omegasim_a7_long_horizon_analysis_20260627/a7_semantic_field_null_contrasts.csv
/tmp/omegasim_a7_long_horizon_analysis_20260627/a7_semantic_field_smoke_report.csv
/tmp/omegasim_a7_long_horizon_analysis_20260627/summary.md
```

Row counts, excluding headers:

```text
manifest: 1
completeness: 12
smoke_report: 12
residual_metrics: 72
null_contrasts: 60
```

## Gate Counts

All 12 run artifacts passed required field and source-reconstruction checks.
All 12 smoke-report rows showed field variation and prediction/work-budget
competition. All 72 residual rows computed.

```text
overall analyzer status: fail_closed_residual_null_gate
required field status: pass=12
source reconstruction status: pass=12
field variation status: pass=12
prediction/work-budget competition status: pass=12
residualization status: computed=72
null contrast status: computed=60
null contrast gate status:
  eligible_for_cross_seed_direction_check=13
  fail_closed_no_nonlinear_forecastability_advantage=7
  fail_closed_no_residual_autocorrelation_advantage=22
  fail_closed_productivity_degrades=18
```

Rows marked `eligible_for_cross_seed_direction_check` are not promotion
evidence. They only mean that one same-seed, same-target, positive-vs-control
row passed the analyzer's local lag-1, nearest-neighbor forecastability, and
productivity checks. The preregistered gate requires the same target to beat
all controls with paired seed agreement and non-worse backlog-adjusted
productivity. That did not happen.

## Backlog-Adjusted Productivity

Backlog-adjusted productivity from the residual metrics was:

| condition | seed 1 | seed 2 |
| --- | ---: | ---: |
| a7_logistic_semantic_coupling | 0.716667 | 0.654321 |
| semantic_off_baseline | 1.543478 | 0.707865 |
| amplitude_matched_linear_semantic_coupling | 0.689655 | 0.650000 |
| source_preserving_semantic_label_shuffle | 0.854167 | 0.628205 |
| semantic_field_phase_shuffle | 0.661290 | 0.629630 |
| prediction_budget_timing_broken_matched_count_null | 0.537313 | 0.511628 |

The positive condition degraded relative to the semantic-off baseline in both
seeds and relative to the source-preserving label shuffle in seed 1. Those
rows correctly block interpretation as semantic residual structure.

## Selected Eligible Rows

The 13 locally eligible rows were scattered across targets and controls:

| seed | control | target | lag-1 delta | nearest-neighbor MAE delta | productivity delta |
| --- | --- | --- | ---: | ---: | ---: |
| 1 | semantic_field_phase_shuffle | a7_semantic_novelty_tick | 0.057376 | -0.000644 | 0.055377 |
| 1 | prediction_budget_timing_broken_matched_count_null | a7_semantic_novelty_tick | 0.040192 | -0.003517 | 0.179354 |
| 1 | prediction_budget_timing_broken_matched_count_null | a7_semantic_coherence_tick | 0.015378 | -0.001101 | 0.179354 |
| 1 | amplitude_matched_linear_semantic_coupling | a7_semantic_contradiction_tick | 0.007517 | -0.002089 | 0.027012 |
| 1 | semantic_field_phase_shuffle | a7_semantic_contradiction_tick | 0.082259 | -0.002028 | 0.055377 |
| 1 | prediction_budget_timing_broken_matched_count_null | a7_semantic_risk_tick | 0.044425 | -0.015508 | 0.179354 |
| 1 | semantic_field_phase_shuffle | a7_artifact_readiness_tick | 0.002141 | -0.000403 | 0.055377 |
| 1 | semantic_field_phase_shuffle | a7_trust_weighted_salience_tick | 0.010660 | -0.002266 | 0.055377 |
| 2 | source_preserving_semantic_label_shuffle | a7_semantic_novelty_tick | 0.136470 | -0.000576 | 0.026116 |
| 2 | semantic_field_phase_shuffle | a7_semantic_novelty_tick | 0.017828 | -0.004278 | 0.024691 |
| 2 | prediction_budget_timing_broken_matched_count_null | a7_semantic_coherence_tick | 0.008470 | -0.000100 | 0.142693 |
| 2 | prediction_budget_timing_broken_matched_count_null | a7_semantic_risk_tick | 0.007668 | -0.011147 | 0.142693 |
| 2 | semantic_field_phase_shuffle | a7_trust_weighted_salience_tick | 0.036232 | -0.000218 | 0.024691 |

No target passed against all five controls in both seeds.

## Dominant Source-Ledger Sanity Check

For the logistic condition, dominant absolute update sources by field were:

| target | seed 1 dominant source | seed 1 share | seed 2 dominant source | seed 2 share |
| --- | --- | ---: | --- | ---: |
| artifact_readiness | clip_residual | 0.436866 | clip_residual | 0.434450 |
| semantic_coherence | semantic_noise | 0.647572 | semantic_noise | 0.627229 |
| semantic_contradiction | artifact_handoff | 0.653452 | artifact_handoff | 0.626390 |
| semantic_novelty | semantic_noise | 0.441712 | semantic_noise | 0.453464 |
| semantic_risk | artifact_handoff | 0.624471 | artifact_handoff | 0.604389 |
| trust_weighted_salience | ambient_decay | 0.385095 | ambient_decay | 0.402680 |

This profile reinforces the fail-closed decision. Several endpoints are still
dominated by ledger components such as noise, handoff accounting, ambient
decay, or clipping residuals, so the result should not be described as
source-independent semantic dynamics.

## Decision

A7 long-horizon validation closes conservatively for seeds `1..2`. The source
schema passed, residualization computed, field variation was present, and
prediction/work-budget competition was measurable. However, the logistic
semantic-field condition did not beat the semantic-off baseline,
amplitude-matched linear control, source-preserving label shuffle, phase
shuffle, and prediction-budget timing-broken null on the same target with
paired-seed agreement and non-worse productivity.

Do not promote A7 semantic dynamics, broaden seeds, add mechanisms, or move to
downstream multi-hive coupling from this result. The active interpretation is
`fail_closed_residual_null_gate`: the current single-hive scaffold is useful as
a source-accounted analyzer path, not as evidence for semantic lobe structure,
attractors, synchrony, or multi-hive grammar.
