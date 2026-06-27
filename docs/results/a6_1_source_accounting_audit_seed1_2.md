# A6.1 Source-Accounting Audit, Seeds 1-2

Run date: 2026-06-27.

This note records the bounded A6.1 read-only source-accounting audit over fresh
seed `1..2` smoke artifacts generated from the existing preregistered four A6
conditions. It is a schema/control audit, not promotion evidence.

## Inputs

```bash
.venv-conda/bin/python -m ohdyn.compare_a6_logistic_appraisal \
  --seeds 1 2 \
  --out runs/a6_1_source_schema_compare

.venv-conda/bin/python -m ohdyn.analyze_a6_logistic_appraisal \
  --compare-dir runs/a6_1_source_schema_compare \
  --out runs/a6_1_source_schema_analysis_v2
```

The comparison reran only the existing single-hive A6 smoke grid:
`logistic`, `linear`, `phase_shuffled`, and `threshold_shuffled`, crossed with
seeds `1` and `2`. No broader seeds, mechanisms, dashboards, external
integrations, real LLM calls, or multi-hive coupling were added.

## Generated Audit Artifact

The analyzer now writes:

```text
runs/a6_1_source_schema_analysis_v2/a6_logistic_appraisal_source_accounting.csv
```

Row counts, excluding headers:

```text
source_accounting: 80
artifact_provenance: 80
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

## Source-Accounting Status

Across all source-accounting rows:

```text
required_field_status:
  schema_pass: 80

reconstruction_status:
  schema_pass: 80

status:
  high_handoff_alias_risk: 16
  underdetermined_smoke_scale: 64
```

Logistic rows for the fields most relevant to interpretation:

```text
seed  field                       total_abs_delta  handoff_success_share  prediction_share  queue_work_share  status
1     artifact_readiness          0.697687         0.506529               0.0               0.0               underdetermined_smoke_scale
1     artifact_utility            0.576679         0.569412               0.0               0.0               underdetermined_smoke_scale
2     artifact_readiness          0.664480         0.415511               0.0               0.0               underdetermined_smoke_scale
2     artifact_utility            0.379809         0.494786               0.0               0.0               underdetermined_smoke_scale
```

## Interpretation

The A6.1 source schema is now analyzer-visible: required fields are present,
artifact-update source columns reconstruct total deltas, and source shares are
reported per condition, seed, and artifact field.

This does not promote A6. The audit remains smoke-scale and residual rows are
still underdetermined. Sixteen rows remain conservatively labeled
`high_handoff_alias_risk`, and even the logistic readiness/utility rows retain
large handoff-success shares. Treat A6 as schema/analyzer-only until a future
preregistered pilot tests source-preserving nulls and backlog-adjusted
productivity controls.
