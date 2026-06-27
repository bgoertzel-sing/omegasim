# A6 Smoke Schema Gate, Seeds 1-2

Run date: 2026-06-27.

This note records the bounded A6 smoke comparison requested by the current
automation status. It is a schema and analyzer exercise only, not evidence for
promotion beyond the A6 smoke scaffold.

## Commands

```bash
.venv-conda/bin/python -m ohdyn.compare_a6_logistic_appraisal \
  --seeds 1 2 \
  --out runs/a6_logistic_appraisal_compare

.venv-conda/bin/python -m ohdyn.analyze_a6_logistic_appraisal \
  --compare-dir runs/a6_logistic_appraisal_compare \
  --out runs/a6_logistic_appraisal_analysis
```

The generated artifacts live under ignored `runs/` paths.

## Smoke Outputs

The comparison produced eight run artifacts: four preregistered single-hive A6
conditions crossed with seeds `1` and `2`.

Condition means from
`runs/a6_logistic_appraisal_compare/a6_logistic_appraisal_comparison_metrics.csv`:

```text
condition            readiness   artifact_utility   handoff_successes   queue_depth
logistic             0.427342    0.321045           45.0                20.5
linear               0.429742    0.319338           40.5                19.0
threshold_shuffled   0.426742    0.285925           42.0                22.0
phase_shuffled       0.373478    0.155530           35.0                22.5
```

Effect summaries:

```text
logistic minus linear:
  artifact_utility_delta = 0.001707
  handoff_success_delta = 4.5
  queue_depth_delta = 1.5
  interpretation = artifact utility improves with higher queue load; treat as accounting risk

logistic minus phase_shuffled:
  artifact_utility_delta = 0.165515
  handoff_success_delta = 10.0
  queue_depth_delta = -2.0
  interpretation = smoke guardrails improve, but residual recurrence remains unanalyzed

logistic minus threshold_shuffled:
  artifact_utility_delta = 0.035120
  handoff_success_delta = 3.0
  queue_depth_delta = -1.5
  interpretation = smoke guardrails improve, but residual recurrence remains unanalyzed
```

## Analyzer Gate

The read-only analyzer consumed the existing A6 comparison artifacts and wrote:

```text
runs/a6_logistic_appraisal_analysis/a6_logistic_appraisal_endpoints.csv
runs/a6_logistic_appraisal_analysis/a6_logistic_appraisal_manifest.csv
runs/a6_logistic_appraisal_analysis/summary.md
```

It observed all four required conditions and both seeds. All control levels are
still marked `skeleton_pending_confirmatory_comparison`, including load/service
accounting, clock/queue residualization, amplitude-matched linear control,
phase-shuffled control, threshold-shuffled control, paired-seed uncertainty,
and promotion/closure rules.

## Interpretation

The A6 smoke artifact and analyzer contracts are exercised successfully on the
canonical ignored paths. The seed `1..2` outputs do not justify a scientific
promotion claim. Logistic-versus-linear remains especially conservative because
the tiny artifact-utility difference occurs with higher queue depth.

The next implementation step should strengthen the read-only A6 analyzer's
control calculations before any broader seed run or promotion discussion.
