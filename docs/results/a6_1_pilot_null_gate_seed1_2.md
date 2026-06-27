# A6.1 Pilot Null Gate, Seeds 1-2

Run date: 2026-06-27.

This note records the bounded A6.1 source-preserving null gate over paired
seeds `1` and `2`. It is a schema/analyzer pilot gate, not promotion evidence.
It adds no simulator mechanism, broad seed sweep, external integration,
dashboard, real LLM call, Lean, Slack, browser automation, Atomspace, or
multi-hive coupling.

## Inputs

```bash
.venv-conda/bin/python -m ohdyn.compare_a6_logistic_appraisal \
  --seeds 1 2 \
  --include-a6-1-nulls \
  --out runs/a6_1_pilot_null_compare

.venv-conda/bin/python -m ohdyn.analyze_a6_logistic_appraisal \
  --compare-dir runs/a6_1_pilot_null_compare \
  --out runs/a6_1_pilot_null_analysis
```

The comparison ran the existing four A6 smoke fixtures and derived only the
two preregistered source-preserving null artifact conditions:

```text
source_label_shuffled_within_tick
handoff_success_timing_broken_matched_counts
```

## Analyzer Outputs

Row counts, excluding headers:

```text
endpoints: 12
manifest: 9
control_deltas: 10
control_summary: 70
residual_preflight: 168
residual_timeseries: 2688
residual_contrast_summary: 140
residual_contrast_rollup: 70
comparison_consistency: 6
effects_consistency: 3
artifact_provenance: 120
source_accounting: 120
A6.1 pilot null gate: 8
```

All `120` source-accounting rows reported `schema_pass` for required fields
and `schema_pass` for artifact-delta reconstruction. Source-accounting status
counts were:

```text
underdetermined_smoke_scale: 95
high_handoff_alias_risk: 23
high_queue_work_alias_risk: 2
```

## Pilot Gate Result

All `8` A6.1 pilot null gate rows were labeled:

```text
null_removes_endpoint_advantage: 8
```

Selected paired endpoint deltas:

```text
contrast                                             seed  endpoint                    logistic_minus_control  backlog_adjusted_productivity_delta
logistic_vs_source_label_shuffled_within_tick        1     final_artifact_readiness    0.0                     0.0
logistic_vs_source_label_shuffled_within_tick        1     final_artifact_utility      0.0                     0.0
logistic_vs_handoff_success_timing_broken_matched_counts 1 final_artifact_readiness    0.0                     0.0
logistic_vs_handoff_success_timing_broken_matched_counts 1 final_artifact_utility      0.0                     0.0
logistic_vs_source_label_shuffled_within_tick        2     final_artifact_readiness    0.0                     0.0
logistic_vs_source_label_shuffled_within_tick        2     final_artifact_utility      0.0                     0.0
logistic_vs_handoff_success_timing_broken_matched_counts 2 final_artifact_readiness    0.0                     0.0
logistic_vs_handoff_success_timing_broken_matched_counts 2 final_artifact_utility     -0.008                   0.0
```

For comparison, logistic-versus-linear remained seed-inconsistent:

```text
seed  readiness_delta  utility_delta  completion_fraction_delta  queue_depth_delta
1     0.0              0.032          0.022581                   0.0
2    -0.0048          -0.028586      -0.058954                   3.0
```

## Interpretation

The A6.1 source schema and null artifact path are analyzer-visible: paired
seeds are complete, required source fields are present, and source deltas
reconstruct.

The scientific result is conservative closure at this gate. Logistic
readiness/utility advantages do not survive the two preregistered
source-preserving null checks on paired seeds `1` and `2`; the nulls match or
exceed the logistic endpoints, and backlog-adjusted productivity does not
rescue the result. Residual rows remain smoke-scale and underdetermined. Do not
interpret this as recurrence, attractors, lobe grammar, synchrony, causality,
or nonlinear collective structure.
