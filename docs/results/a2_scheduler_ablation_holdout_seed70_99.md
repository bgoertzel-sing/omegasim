# A2 Scheduler Ablation Holdout, Seeds 70-99

This is the compact checked-in holdout result for the preregistered
quota-balance versus seeded random-available scheduler ablation. The ignored
source artifacts were generated under:

- `runs/a2_scheduler_ablation_holdout_seed70_99_20260624/`
- `runs/a2_scheduler_ablation_holdout_seed70_99_analysis_bootstrap_20260624/`

Commands:

```bash
.venv-conda/bin/python -m ohdyn.compare_pressure \
  --normal-baseline-config configs/a2_attention_smoke.yaml \
  --normal-variant-config configs/a2_attention_random_available.yaml \
  --normal-internal-improvement-config '' \
  --medium-pressure-baseline-config configs/a2_attention_high_pressure.yaml \
  --medium-pressure-variant-config configs/a2_attention_random_available_high_pressure.yaml \
  --medium-pressure-internal-improvement-config '' \
  --high-pressure-baseline-config configs/a2_attention_extreme_pressure.yaml \
  --high-pressure-variant-config configs/a2_attention_random_available_extreme_pressure.yaml \
  --high-pressure-internal-improvement-config '' \
  --seeds 70 71 72 73 74 75 76 77 78 79 80 81 82 83 84 85 86 87 88 89 90 91 92 93 94 95 96 97 98 99 \
  --out runs/a2_scheduler_ablation_holdout_seed70_99_20260624

.venv-conda/bin/python -m ohdyn.analyze_pressure \
  --pressure-dir runs/a2_scheduler_ablation_holdout_seed70_99_20260624 \
  --out runs/a2_scheduler_ablation_holdout_seed70_99_analysis_bootstrap_20260624 \
  --limit 10 \
  --bootstrap-resamples 200 \
  --bootstrap-seed 1
```

The generic comparison runner labels the second policy slot as
`research_heavy`. In this artifact that label means `random_available`, because
all variant config paths are the checked-in seeded random-available scheduler
fixtures.

## Primary Reading

The holdout block confirms that the pressure-amplified final queue-depth
response survives the scheduler ablation. The strongest full-holdout pressure
response is `quota_balance` final queue depth under the normal-to-medium
pressure interval:

- condition means: `21.5 -> 48.2 -> 57.733333`
- normal-to-medium slope: `33.375`
- medium-to-high slope: `23.833332`
- curvature: `-9.541668`
- high-minus-normal delta: `36.233333`

The seeded random-available scheduler is close but second:

- condition means: `21.6 -> 45.5 -> 56.166667`
- normal-to-medium slope: `29.875`
- medium-to-high slope: `26.666667`
- high-minus-normal delta: `34.566667`

Bootstrap rank stability selects the `quota_balance` final queue-depth
normal-to-medium slope in `192/200` resamples (`0.96`) with sign stability
`1.0`; `random_available` final queue-depth normal-to-medium slope is selected
in `8/200` resamples (`0.04`). This supports the conservative mechanism
reading: task-creation pressure drives the robust backlog response, and changing
from quota-balanced selection to seeded random available-task selection changes
curve shape and secondary metrics rather than removing the queue-depth effect.

## Secondary Signals

- Value-weighted completed work declines under both schedulers from normal to
  extreme pressure: `quota_balance=-20.366667`,
  `random_available=-16.6`.
- Completion-normalized and effort-normalized yield diverge under
  `random_available`: value per completed task rises by `0.050404`, while value
  per work event declines by `-0.13446`.
- The top value-yield divergence is not stable across ordered prefixes and has
  only diffuse bootstrap support; the largest bootstrap probability is
  `0.36` for `random_available` normal-to-medium divergence. Treat value-yield
  divergence as a candidate mechanism signal, not a settled finding.
- The strongest class-specific capture-pressure row is `random_available` peak
  near-term-external capture-pressure curvature, selected in `104/200`
  bootstrap resamples (`0.52`) with sign stability `1.0`. It remains secondary
  because top-selection probability is moderate.
- Both schedulers show less trajectory variability under pressure. Turning
  points fall by `-1.966666` for `quota_balance` and `-2.6` for
  `random_available`; longest dwell runs increase by `0.766667` and `1.966667`.

## Strategic Note

The external strategic review at
`../outputs/strategy-reviews/omegasim/latest-review.md` is marked
`strategic_change_level: major` and `notify_ben: true`; Ben should be notified.
This holdout follows its recommendation to stop two-seed prefix extension and
use a predefined holdout block with uncertainty analysis.

## Compact CSV

`docs/results/a2_scheduler_ablation_holdout_seed70_99_top.csv` records the
holdout rows most relevant for lightweight review without parsing ignored
`runs/` artifacts.
