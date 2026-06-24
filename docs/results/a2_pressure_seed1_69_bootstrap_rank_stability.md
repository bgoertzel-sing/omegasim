# A2 Pressure Bootstrap Rank Stability, Seeds 1-69

This is the compact checked-in uncertainty companion for the frozen A2
extreme-pressure baseline. The ignored source analysis was generated under:

- `runs/a2_attention_extreme_pressure_analysis_seed1_69_20260624T_bootstrap3_20260624/`

Command:

```bash
.venv-conda/bin/python -m ohdyn.analyze_pressure \
  --pressure-dir runs/a2_attention_extreme_pressure_compare_seed1_69_20260624T_run \
  --out runs/a2_attention_extreme_pressure_analysis_seed1_69_20260624T_bootstrap3_20260624 \
  --limit 10 \
  --bootstrap-resamples 200 \
  --bootstrap-seed 1
```

## Reading

The global top-response result is bootstrap-stable: internal-improvement final
queue depth, normal-to-medium slope, was selected as the top response in `193`
of `200` deterministic seed-level bootstrap resamples (`0.965`) with sign
stability `1.0`.

The class-specific capture-pressure top response is weaker: baseline peak
long-term-research capture pressure, normal-to-medium slope, was selected in
`80` of `200` resamples (`0.4`) with sign stability `1.0`. This supports keeping
class-specific capture pressure secondary until a mechanism-discriminating
ablation explains it.

The full-seed value-yield divergence winner is not bootstrap-favored. The
full-seed row remains research-heavy medium-to-high slope (`0.122085`), but it
was selected in only `15` of `200` resamples (`0.075`) with sign stability
`0.97`. The bootstrap-favored value-yield divergence row is
internal-improvement normal-to-medium slope (`0.111792`), selected in `128` of
`200` resamples (`0.64`) with sign stability `1.0`. Value-yield divergence
therefore remains a secondary, unstable interpretation target.

## Compact CSV

`docs/results/a2_pressure_seed1_69_bootstrap_rank_stability_top.csv` records the
top selected rows from the global, class-specific capture-pressure, and
value-yield divergence bootstrap scopes.
