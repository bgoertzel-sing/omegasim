# A2 Scheduler Ablation, Seeds 1-3

This is the compact checked-in result artifact for the preregistered
quota-balance versus seeded random-available scheduler ablation. The ignored
source artifacts were generated under:

- `runs/a2_scheduler_ablation_seed1_3_20260624/`

Command:

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
  --seeds 1 2 3 \
  --out runs/a2_scheduler_ablation_seed1_3_20260624
```

The generic comparison runner labels the second policy slot as
`research_heavy`. In this artifact that label means `random_available`, because
all variant config paths are the checked-in seeded random-available scheduler
fixtures.

## Primary Reading

Both schedulers show nearly identical high-minus-normal final queue-depth
pressure deltas:

- `quota_balance`: `21.333333 -> 44.666667 -> 62.666667`,
  high-minus-normal delta `41.333334`.
- `random_available`: `24 -> 52.333333 -> 65.333333`,
  high-minus-normal delta `41.333333`.

This small ablation therefore does not explain the frozen queue-depth pressure
effect as a quota-balancing-only artifact. Queue growth remains mostly driven by
task-creation pressure under these baseline attention shares, with scheduler
mechanics changing the curve shape rather than removing the backlog response.

The strongest full-seed pressure response in this ablation is
`random_available` value-weighted completed work under the medium-to-high
pressure interval:

- condition means: `46.333333 -> 45.666667 -> 26.666667`
- normal-to-medium slope: `-0.833333`
- medium-to-high slope: `-47.5`
- curvature: `-46.666667`
- high-minus-normal delta: `-19.666666`

This top response is not prefix-stable across seeds `1,2`: the two-seed prefix
selects `quota_balance` final queue depth medium-to-high slope instead. Treat
the value-weighted drop as an early ablation signal, not a stable interpretation
claim.

## Secondary Signals

- Value per completed task improves under `quota_balance` by `0.223848` from
  normal to extreme pressure, but declines under `random_available` by
  `-0.059508`.
- Value per work event declines under both schedulers:
  `quota_balance=-0.209362`, `random_available=-0.244285`.
- Final queued-task mean age rises less under `random_available`
  (`0.899482`) than under `quota_balance` (`1.30845`).
- Final max capture pressure declines much more under `quota_balance`
  (`-0.198887`) than under `random_available` (`-0.019568`).
- Both schedulers become less trajectory-variable under pressure:
  turning-point means drop by `-4.0` for `quota_balance` and `-3.0` for
  `random_available`; longest dwell runs increase by `2.666667` and `2.333334`.

## Strategic Note

The external strategic review at
`../outputs/strategy-reviews/omegasim/latest-review.md` is marked
`strategic_change_level: major` and `notify_ben: true`; Ben should be notified.
This run follows its recommendation to freeze the 69-seed pressure baseline and
move to mechanism-discriminating ablations instead of extending seed prefixes.

## Compact CSV

`docs/results/a2_scheduler_ablation_seed1_3.csv` records the primary
scheduler-level rows without requiring access to ignored `runs/` artifacts.
