# A2 Scheduler Ablation Bootstrap Rank Stability, Seeds 1-3

This is the compact checked-in uncertainty companion for the preregistered
quota-balance versus seeded random-available scheduler ablation. The ignored
source analysis was generated under:

- `runs/a2_scheduler_ablation_seed1_3_analysis_bootstrap_20260624/`

Command:

```bash
.venv-conda/bin/python -m ohdyn.analyze_pressure \
  --pressure-dir runs/a2_scheduler_ablation_seed1_3_20260624 \
  --out runs/a2_scheduler_ablation_seed1_3_analysis_bootstrap_20260624 \
  --limit 10 \
  --bootstrap-resamples 200 \
  --bootstrap-seed 1
```

The generic comparison runner labels the second policy slot as
`research_heavy`. In this artifact that label means `random_available`, because
the variant config paths are the checked-in seeded random-available scheduler
fixtures.

## Reading

The full-seed top pressure response from the ablation summary was
`random_available` value-weighted completed work, medium-to-high slope
`-47.5`. It was selected in `0` of `200` deterministic seed-level bootstrap
resamples. Treat that value-weighted drop as an unstable early signal, not as a
stable scheduler-mechanism finding.

The bootstrap-favored global response is instead `random_available` final queue
depth, normal-to-medium slope. It was selected in `193` of `200` resamples
(`0.965`) with sign stability `1.0`. This supports the conservative reading
from the compact ablation result: the backlog response remains pressure-driven
under both scheduler mechanics, while scheduler choice mainly changes curve
shape and secondary value/capture-pressure behavior.

The strongest class-specific capture-pressure response is baseline peak
near-term-external capture pressure curvature. It was selected in `122` of
`200` resamples (`0.61`) with sign stability `1.0`. This is stronger than the
class-specific uncertainty seen in the frozen 69-seed baseline, but the sample
size here is only three seeds, so it should remain secondary until the ablation
is expanded.

The top value-yield divergence row is baseline medium-to-high slope: completion
normalized yield improves by `0.23065` while effort-normalized yield declines by
`-0.74289`, a divergence of `0.97354`. It was selected in `100` of `200`
resamples (`0.5`) and was not stable across ordered prefixes; the two-seed
prefix selected `random_available` curvature instead. Keep this as a candidate
mechanism signal, not a settled interpretation.

## Compact CSV

`docs/results/a2_scheduler_ablation_seed1_3_bootstrap_rank_stability_top.csv`
records the bootstrap-selected rows most relevant for lightweight review
without parsing ignored `runs/` artifacts.
