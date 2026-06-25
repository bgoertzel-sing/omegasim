# A4 Two-Hive Holdout, Seeds 100..129

Run date: 2026-06-25.

This records the first preregistered A4 two-hive holdout after external review
approval. The latest review at
`../outputs/strategy-reviews/omegasim/latest-review.md` was marked
`strategic_change_level: minor` and `notify_ben: false`; no Ben notification
was required. The review approved running the existing seed `100..129` bundle
and read-only analyzer, without changing configs or broadening scope.

## Commands

The holdout output root was absent before execution:

```bash
test ! -e runs/a4_two_hive_holdout_seed100_129
```

The four preregistered configs were run for paired seeds `100..129`:

- `configs/a4_two_hive_none_holdout.yaml`
- `configs/a4_two_hive_direct_holdout.yaml`
- `configs/a4_two_hive_delayed_holdout.yaml`
- `configs/a4_two_hive_shuffled_holdout.yaml`

The read-only analyzer was then run:

```bash
python -m ohdyn.analyze_a4_holdout \
  --holdout-dir runs/a4_two_hive_holdout_seed100_129 \
  --out-dir runs/a4_two_hive_holdout_seed100_129_analysis \
  --seeds 100..129
```

The local ignored `runs/` artifacts contain 120 run directories and the
analysis files:

- `a4_holdout_hive_endpoints.csv`
- `a4_holdout_cross_hive_endpoints.csv`
- `a4_holdout_effects.csv`
- `summary.md`

## Analyzer Summary

The analyzer consumed 30 paired seeds, four modes, 240 per-hive endpoint rows,
and 120 cross-hive endpoint rows.

Transfer-volume effects:

| comparison | paired seeds | high mean | low mean | mean delta | positive delta rate |
| --- | ---: | ---: | ---: | ---: | ---: |
| direct minus none | 30 | 865.333333 | 0.000000 | 865.333333 | 1.000000 |
| delayed minus none | 30 | 865.900000 | 0.000000 | 865.900000 | 1.000000 |
| shuffled minus none | 30 | 865.333333 | 0.000000 | 865.333333 | 1.000000 |
| direct minus shuffled | 30 | 865.333333 | 865.333333 | 0.000000 | 0.000000 |

Selected preregistered cross-hive endpoint effects:

| comparison | endpoint | mean delta | median delta | positive delta rate |
| --- | --- | ---: | ---: | ---: |
| direct minus none | queued-age divergence final | -0.037139 | 0.094428 | 0.533333 |
| direct minus none | completion-fraction divergence final | -0.007746 | -0.005891 | 0.366667 |
| direct minus none | load-backlog corr lag 0 | -0.654804 | -0.723427 | 0.133333 |
| direct minus none | completion-fraction corr lag 0 | -0.019374 | -0.027728 | 0.433333 |
| delayed minus none | queued-age divergence final | 0.518094 | 0.478835 | 0.666667 |
| delayed minus none | completion-fraction divergence final | -0.005065 | -0.000045 | 0.500000 |
| delayed minus none | load-backlog corr lag 0 | 0.325600 | 0.374553 | 0.700000 |
| delayed minus none | completion-fraction corr lag 0 | 0.678330 | 0.723718 | 0.966667 |
| delayed minus none | completion-fraction corr lag 2 | 0.619752 | 0.635627 | 0.900000 |
| direct minus shuffled | all listed cross-hive endpoints | 0.000000 | 0.000000 | 0.000000 |

## Interpretation Boundary

This is an analyzer record, not a final A4 interpretation. The immediate
robust finding is transfer-volume accounting: direct, delayed, and shuffled all
add full-transfer coupling versus none. Delayed coupling shows sign-stable
completion-fraction correlation increases in the analyzer's paired effects, but
paired bootstrap intervals have not yet been added to this A4 analyzer record.

The two-hive shuffled control remains structurally equivalent to direct target
assignment because each source hive has only one legal non-source target. Treat
`direct minus shuffled` as a schema/conservation and source-opportunity check,
not as a meaningful phase-randomization null. Lobe diagnostics are not promoted
to mechanism evidence.

## Verification

```bash
pytest -q tests/test_run_harness.py \
  -k 'a4_holdout_analyzer or a4_holdout_config_bundle or a4_smoke_contract_preflight'
```

Result: 5 passed, 567 deselected.
