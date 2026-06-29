# A7.3 Long-Horizon Residual/Recurrence Validation, Seeds 1-2

Run date: 2026-06-29.

This report records the fixed A7.3 validation gate preregistered in
`docs/a7_3_long_horizon_residual_recurrence_preregistration.md`. It stayed
single-hive, used only paired seeds `1` and `2`, used the frozen `256`-tick
nine-condition validation grid, did not broaden seeds, did not add mechanisms,
and did not add external integrations.

This documentation pass did not rerun simulations or analyzers. It summarizes
the checked-in analyzer contract and the bounded verification output recorded
in `AUTOMATION_STATUS.md`.

## Command Bundle

The recorded artifact set corresponds to:

```bash
.venv-conda/bin/python -m ohdyn.compare_a7_3_dimensionless_delayed \
  --validation \
  --out /tmp/omegasim_a7_3_recurrence_eZSsUb/compare

.venv-conda/bin/python -m ohdyn.analyze_a7_3_preflight \
  --compare-dir /tmp/omegasim_a7_3_recurrence_eZSsUb/compare \
  --out /tmp/omegasim_a7_3_recurrence_eZSsUb/preflight

.venv-conda/bin/python -m ohdyn.analyze_a7_3_residual_recurrence \
  --compare-dir /tmp/omegasim_a7_3_recurrence_eZSsUb/compare \
  --preflight-dir /tmp/omegasim_a7_3_recurrence_eZSsUb/preflight \
  --out /tmp/omegasim_a7_3_recurrence_eZSsUb/analysis
```

The tracked README command uses the same fixed comparison, preflight, and
analyzer pair with repository-local output paths:

```bash
python -m ohdyn.compare_a7_3_dimensionless_delayed --validation --out runs/a7_3_dimensionless_validation_seed1_2
python -m ohdyn.analyze_a7_3_preflight --compare-dir runs/a7_3_dimensionless_validation_seed1_2 --out runs/a7_3_validation_preflight_seed1_2
python -m ohdyn.analyze_a7_3_residual_recurrence --compare-dir runs/a7_3_dimensionless_validation_seed1_2 --preflight-dir runs/a7_3_validation_preflight_seed1_2 --out runs/a7_3_residual_recurrence_validation_seed1_2
```

## Scope

The validation grid used the nine frozen A7.3 conditions:

```text
full_delayed_logistic
low_gain_contraction
no_delay_same_tick_blocked
amplitude_matched_linear
artifact_off
cost_free_prediction
spend_only_replay
phase_shuffled_lag
threshold_shuffled
```

The positive condition was `full_delayed_logistic`. The other eight conditions
were preregistered nulls or guardrail controls. The analyzer was read-only over
existing metrics, events, lifted-state, and source-ledger artifacts plus an
eligible preflight manifest.

## Artifact Inventory

The bounded verification emitted:

```text
9 conditions x 2 paired seeds = 18 validation run directories
256 ticks per run
144 residual/recurrence metric rows
128 null contrast rows
12 gate rows
```

The analyzer output contract is:

```text
a7_3_residual_recurrence_metrics.csv
a7_3_residual_recurrence_contrasts.csv
a7_3_residual_recurrence_gates.csv
a7_3_residual_recurrence_manifest.csv
summary.md
```

## Gate Counts

The recorded manifest status was:

```text
status: fail_closed_no_a7_3_promotion
run_count: 18
metric_rows: 144
contrast_rows: 128
gate_rows: 12
```

The preflight, condition/seed coverage, and minimum-row gates passed. All eight
preregistered null gates failed closed, and the low-gain local-divergence gate
also failed closed.

Because promotion is all-or-nothing, any failed null, surrogate, source,
guardrail, or divergence gate blocks A7.3 promotion.

## Interpretation Boundary

This result is a valid long-horizon analyzer exercise, not scientific
promotion. It shows that the A7.3 artifact/preflight/analyzer path is wired and
can compute the preregistered residual, recurrence, surrogate, local-divergence,
null-contrast, and gate rows over fixed validation artifacts.

It does not support A7.3 promotion, lobe-like dynamics, semantic dynamics,
strange-attractor-like behavior, synchrony, or causal collective-structure
claims. The current active interpretation is:

```text
fail_closed_no_a7_3_promotion
```

## Strategic Review Note

The latest external strategy review in
`../outputs/strategy-reviews/omegasim/latest-review.md` is marked
`strategic_change_level: major` and `notify_ben: true`. Its pause/recover
recommendation was superseded by Ben's newer 2026-06-29 instruction that A7.3
should proceed, and the committed status records that direction shift.

Ben should still be notified that the A7.3 validation gate completed
fail-closed and that no A7.3 promotion language is supported by this result.

## Decision

A7.3 long-horizon residual/recurrence validation closes conservatively for
seeds `1,2`. Do not broaden seeds, tune parameters, add mechanisms, rerun
artifact generation after inspecting this result, or move to downstream
multi-hive coupling from this gate without a fresh preregistered direction.
