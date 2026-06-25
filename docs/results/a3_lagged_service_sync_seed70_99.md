# A3 lagged service synchronization, seeds 70..99

This analysis-only check reads existing A2 service-capacity and
exogenous-arrival artifacts. It does not rerun simulations or add simulator
mechanics.

Command:

```bash
python -m ohdyn.analyze_lagged_service_sync \
  --service-capacity-dir runs/a2_service_capacity_holdout_seed70_99_20260624 \
  --exogenous-arrival-dir runs/a2_exogenous_arrival_holdout_seed70_99_20260625_v2 \
  --out runs/a3_lagged_service_sync_seed70_99_20260625
```

Artifacts:

- `runs/a3_lagged_service_sync_seed70_99_20260625/lagged_service_sync_metrics.csv`
- `runs/a3_lagged_service_sync_seed70_99_20260625/lagged_service_sync_effects.csv`
- `runs/a3_lagged_service_sync_seed70_99_20260625/summary.md`

Interpretation:

- Primary endpoints are lagged service/completion and service/load-change
  correlations at lag `-1` or `+1`.
- The same-tick created-completed balance versus queue-delta correlation is
  retained only as an artifact identity diagnostic; it is exactly `1.0` across
  the seed `70..99` condition means and is excluded from the primary
  synchronization endpoint.
- The strongest lagged service/completion shift is the normal-pressure
  low-service to high-service contrast: `0.16846`.
- The strongest lagged service/load-change shift is the normal-pressure
  high-service to extreme-pressure high-service contrast: `-0.096587`.
- These are modest synchronization diagnostics. They do not overturn the frozen
  A2 conclusion that current lobe evidence is load/action-accounting dominated
  and does not demonstrate independent residual lobe grammar.
