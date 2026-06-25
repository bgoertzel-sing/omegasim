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

The read-only analyzer was first run, then regenerated after paired-bootstrap
uncertainty fields were added:

```bash
python -m ohdyn.analyze_a4_holdout \
  --holdout-dir runs/a4_two_hive_holdout_seed100_129 \
  --out-dir runs/a4_two_hive_holdout_seed100_129_analysis \
  --seeds 100..129 \
  --overwrite
```

The local ignored `runs/` artifacts contain 120 run directories and the
analysis files:

- `a4_holdout_hive_endpoints.csv`
- `a4_holdout_cross_hive_endpoints.csv`
- `a4_holdout_effects.csv`, including deterministic paired-bootstrap fields
- `summary.md`

## Analyzer Summary

The analyzer consumed 30 paired seeds, four modes, 240 per-hive endpoint rows,
and 120 cross-hive endpoint rows.

Transfer-volume effects with deterministic paired-bootstrap mean-delta
intervals:

| comparison | paired seeds | mean delta | bootstrap mean-delta CI | positive delta rate | bootstrap sign stability |
| --- | ---: | ---: | ---: | ---: | ---: |
| direct minus none | 30 | 865.333333 | [857.700000, 873.533333] | 1.000000 | 1.000000 |
| delayed minus none | 30 | 865.900000 | [857.066667, 874.733333] | 1.000000 | 1.000000 |
| shuffled minus none | 30 | 865.333333 | [857.200000, 873.733333] | 1.000000 | 1.000000 |
| direct minus shuffled | 30 | 0.000000 | [0.000000, 0.000000] | 0.000000 | 0.000000 |

Selected preregistered cross-hive endpoint effects:

| comparison | endpoint | mean delta | bootstrap mean-delta CI | positive delta rate | bootstrap sign stability |
| --- | --- | ---: | ---: | ---: | ---: |
| direct minus none | queued-age divergence final | -0.037139 | [-0.749722, 0.614859] | 0.533333 | 0.550000 |
| direct minus none | completion-fraction divergence final | -0.007746 | [-0.030303, 0.013791] | 0.366667 | 0.750000 |
| direct minus none | load-backlog corr lag 0 | -0.654804 | [-0.817661, -0.488024] | 0.133333 | 1.000000 |
| direct minus none | completion-fraction corr lag 0 | -0.019374 | [-0.226735, 0.201847] | 0.433333 | 0.563000 |
| delayed minus none | queued-age divergence final | 0.518094 | [-0.177632, 1.251056] | 0.666667 | 0.933000 |
| delayed minus none | completion-fraction divergence final | -0.005065 | [-0.031765, 0.022916] | 0.500000 | 0.650000 |
| delayed minus none | load-backlog corr lag 0 | 0.325600 | [0.118204, 0.517629] | 0.700000 | 0.999000 |
| delayed minus none | completion-fraction corr lag 0 | 0.678330 | [0.494969, 0.857877] | 0.966667 | 1.000000 |
| delayed minus none | completion-fraction corr lag 2 | 0.619752 | [0.416347, 0.802583] | 0.900000 | 1.000000 |
| direct minus shuffled | all listed cross-hive endpoints | 0.000000 | [0.000000, 0.000000] | 0.000000 | 0.000000 |

## Interpretation Boundary

This is an analyzer record, not a final A4 interpretation. The immediate
robust finding is transfer-volume accounting: direct, delayed, and shuffled all
add full-transfer coupling versus none. Deterministic paired-bootstrap fields
now confirm positive mean-delta intervals for delayed-minus-none load-backlog
lag-0 correlation and completion-fraction lag-0/lag-2 correlations, but this
should be taken through a conservative A4 decision note before any follow-up
mechanism design.

The two-hive shuffled control remains structurally equivalent to direct target
assignment because each source hive has only one legal non-source target. Treat
`direct minus shuffled` as a schema/conservation and source-opportunity check,
not as a meaningful phase-randomization null. Lobe diagnostics are not promoted
to mechanism evidence.

## Verification

```bash
.venv-conda/bin/pytest -q tests/test_run_harness.py \
  -k 'a4_holdout_analyzer or a4_holdout_config_bundle or a4_smoke_contract_preflight'
.venv-conda/bin/ruff check ohdyn tests
.venv-conda/bin/pytest -q tests/test_run_harness.py
```

Result: focused A4 tests passed with 5 selected tests, lint passed, and the
full harness file passed with 572 tests.
