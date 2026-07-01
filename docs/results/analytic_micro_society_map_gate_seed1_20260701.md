# Analytic Micro-Society Map Gate Seed-1 Smoke

Date: 2026-07-01.

Status: diagnostic standalone analytic mechanism screen only. This result does
not support lobe-like, semantic-dynamics, chaotic, or strange-attractor-like
claims.

## Scope

This smoke implements the preregistered
`docs/analytic_micro_society_map_preregistration.md` gate. It stays outside the
OmegaSim simulator and emits only summary diagnostics for exactly four
conditions:

- `active_delayed_micro_society`
- `no_delay`
- `linearized_response`
- `delay_shuffled_history`

The four exposed dimensionless controls are locked across conditions except
for the intended null manipulation: `rho`, `delta`, `mu`, `kappa`, and `nu`.
The state variables are `artifact_readiness`, `prediction_spend`,
`prediction_error`, and `fatigue_threshold`.

## Smoke Command

```bash
python -m ohdyn.analytic_micro_society_map \
  --config configs/analytic_micro_society_map.yaml \
  --out runs/analytic_micro_society_map_seed1_20260701_1430
```

## Result

The active condition was bounded and unsaturated, but the gate still closed
conservatively:

- active boundedness: `pass`
- active saturation fraction: `0.0`
- active recurrence-surrogate delta: `0.076096`
- active finite-time local divergence: `-0.171099`
- active status: `fail_closed_mixed_or_null_equivalent`

The recurrence and local-divergence deltas did not separate from all three
nulls in the same diagnostic direction, and the finite-time local divergence
remained negative. Therefore this smoke is best read as another conservative
mechanism-screen closure, not as a phase-diagram launch result.

## Boundary

No simulator `metrics.csv` or `events.csv` artifacts were written. No A5/A7
helper, real LLM call, dashboard, browser/Slack/Atomspace integration, broad
seed sweep, or multi-hive coupling was added or run.
