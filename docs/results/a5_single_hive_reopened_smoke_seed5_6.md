# A5 Single-Hive Reopened Smoke, Seeds 5-6

## Scope

This records the bounded smoke/pilot allowed by
`docs/a5_single_hive_anticipatory_predictive_control_preregistration.md`.
It used the existing deterministic single-hive A5 scaffold only: no new
simulator mechanics, no real LLM calls, no dashboards, no integrations, no
broader seed sweep, and no multi-hive coupling.

Commands:

```bash
python -m ohdyn.run --config configs/a5_predictive_linear_smoke.yaml --seed 5 --out /tmp/omegasim_a5_reopened_linear_smoke_seed5_20260627
python -m ohdyn.compare_predictive_control --seeds 5 6 --out /tmp/omegasim_a5_reopened_predictive_compare_seed5_6_20260627
python -m ohdyn.analyze_a5_residual_accounting --compare-dir /tmp/omegasim_a5_reopened_predictive_compare_seed5_6_20260627 --out /tmp/omegasim_a5_reopened_residual_accounting_seed5_6_20260627
```

## Smoke Result

The paired comparison produced 16 run artifacts across reactive, linear,
nonlinear, high-budget nonlinear, oracle, and timing-broken shuffled/null
conditions.

Forecast skill improved over reactive and timing-broken nulls:

- linear forecast skill mean: `0.911474` versus reactive `0.877957` and
  shuffled `0.866049`;
- nonlinear forecast skill mean: `0.96199` versus reactive `0.877957` and
  nonlinear shuffled `0.866049`;
- high-budget nonlinear forecast skill mean: `0.972753` versus reactive
  `0.877957` and high-budget nonlinear shuffled `0.866049`;
- oracle forecast skill mean: `1.0`, as expected for the smoothing positive
  control.

The residual-accounting analyzer remained fail-closed. At full accounting:

- linear versus reactive: predictability delta `0.125`, inside the paired
  label-permutation interval;
- linear versus shuffled: predictability delta `0.038`, inside the paired
  label-permutation interval;
- nonlinear versus reactive: predictability delta `0.089`, inside the paired
  label-permutation interval;
- nonlinear versus nonlinear shuffled: predictability delta `0.003`, inside
  the paired label-permutation interval;
- high-budget nonlinear underperformed the relevant residual contrasts;
- no intermediate-budget condition satisfied all promotion criteria.

## Interpretation

This smoke verifies that the reopened A5 preregistration and existing
single-hive scaffold can still run deterministically with matched demand
streams and residual-accounting controls. It does not support a
strange-attractor-like, lobe-like, or residual phase-structure claim.

The scientific status is fail-closed pending a better preregistered mechanism
or diagnostic that can separate useful resource-bounded anticipation from
accounting/null effects.
