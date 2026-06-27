# A6.2 Residual-Recurrence Gate, Seeds 1-2

Run date: 2026-06-27.

This note records the first bounded read-only A6.2 analyzer gate over the
existing A6.1 source-preserving null artifacts. It did not rerun simulations,
broaden seeds, add mechanisms, or promote A6.

## Inputs

```bash
.venv-conda/bin/python -m ohdyn.analyze_a6_2_residual_recurrence \
  --compare-dir runs/a6_1_pilot_null_compare \
  --out runs/a6_2_residual_recurrence_analysis_seed1_2
```

The analyzer consumed `runs/a6_1_pilot_null_compare`, which contains paired
seed `1..2` artifacts for the six preregistered A6.2 conditions:

```text
logistic
linear
phase_shuffled
threshold_shuffled
source_label_shuffled_within_tick
handoff_success_timing_broken_matched_counts
```

## Generated Analysis Artifacts

The ignored analysis directory contains:

```text
runs/a6_2_residual_recurrence_analysis_seed1_2/a6_2_manifest.csv
runs/a6_2_residual_recurrence_analysis_seed1_2/a6_2_paired_seed_completeness.csv
runs/a6_2_residual_recurrence_analysis_seed1_2/a6_2_residual_recurrence_metrics.csv
runs/a6_2_residual_recurrence_analysis_seed1_2/a6_2_residual_recurrence_deltas.csv
runs/a6_2_residual_recurrence_analysis_seed1_2/summary.md
```

Row counts, excluding headers:

```text
manifest: 1
paired_seed_completeness: 12
residual_recurrence_metrics: 156
residual_recurrence_deltas: 130
```

## Gate Result

All 12 run artifacts passed required metric/control/source-field completeness.
No required A6.2 fields were missing.

All 156 residual-recurrence metric rows were labeled `insufficient_horizon`.
All 130 paired delta rows were also labeled `insufficient_horizon`.

This is the correct fail-closed result for the existing 16-tick smoke artifacts:
the analyzer contract can read the source-preserving null comparison, check
paired completeness, check source/control field availability, and emit
recurrence/delta rows, but it refuses recurrence interpretation at smoke
horizon.

## Interpretation

A6.2 is not promoted. The seed `1..2` A6.1 artifacts are useful for validating
the analyzer schema and fail-closed status path only. They are too short for
the preregistered residual-recurrence claim, and this run does not authorize a
seed broadening, mechanism change, or multi-hive coupling.

The external strategy-review recommendation to publish actual A6 analyzer gate
status remains accepted and is extended here to the current A6.2 roadmap. No
scientifically sensible GPT-5.5-Pro recommendation was rejected.

The next scientific move should be a narrow design decision: either
preregister a longer-horizon A6.2 validation with the same source-preserving
null controls and no new mechanisms, or close the single-hive residual-
recurrence route. Do not implement that longer-horizon run without a fresh
preregistered design gate.
