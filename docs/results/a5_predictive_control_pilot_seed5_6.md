# A5 Predictive-Control Pilot, Seeds 5-6

## Scope

This bounded pilot ran the preregistered single-hive A5 predictive-control
comparison on paired seeds `5` and `6`, then applied the read-only residual
accounting analyzer. It did not add simulator mechanics, multi-hive coupling,
external services, dashboards, or new lobe architectures.

Commands:

```bash
.venv-conda/bin/python -m ohdyn.compare_predictive_control --seeds 5 6 --out runs/a5_predictive_control_pilot_seed5_6_20260626
.venv-conda/bin/python -m ohdyn.analyze_a5_residual_accounting --compare-dir runs/a5_predictive_control_pilot_seed5_6_20260626 --out runs/a5_residual_accounting_pilot_seed5_6_20260626
```

## Comparison Means

All conditions used matched task-arrival, action, service, and deterministic
demand-signal settings. Mean final task creation was matched at `78.5` tasks.

| condition | budget | forecast skill | skill per budget | completion fraction | queue depth |
| --- | ---: | ---: | ---: | ---: | ---: |
| reactive | 0.00 | 0.877957 | 0.000000 | 0.386416 | 48.0 |
| linear | 0.35 | 0.911474 | 2.604210 | 0.380463 | 48.5 |
| nonlinear | 0.65 | 0.961990 | 1.479985 | 0.380463 | 48.5 |
| oracle | 1.00 | 1.000000 | 1.000000 | 0.393265 | 47.5 |
| shuffled | 0.35 | 0.866049 | 2.474427 | 0.407861 | 46.5 |

## Residual Accounting Interpretation

The intermediate predictors improved forecast skill versus both reactive and
shuffled controls, but the primary full-accounting residual-structure endpoints
did not survive the paired label-permutation interval in this two-seed pilot:

| contrast | full-accounting endpoint | delta | interpretation |
| --- | --- | ---: | --- |
| linear minus reactive | residual state predictability R2 | -0.087217 | inside paired label-permutation interval |
| nonlinear minus reactive | residual state predictability R2 | -0.065087 | inside paired label-permutation interval |
| linear minus shuffled | residual state predictability R2 | 0.184583 | inside paired label-permutation interval |
| nonlinear minus shuffled | residual state predictability R2 | 0.206713 | inside paired label-permutation interval |

There are weak pilot-scale hints worth checking before any broader sweep:
nonlinear minus shuffled had higher full-accounting return distance
(`delta=0.270429`) outside the label-permutation interval, and oracle minus
nonlinear reduced full-accounting residual lag-1 autocorrelation and
predictability. These do not satisfy the preregistered promotion rule because
the primary intermediate-budget predictability contrasts remain inside the null
interval and the seed count is only two.

## Decision

Fail closed for promotion. Treat this as a reproducible smoke/pilot confirming
that the comparison and residual accounting pipeline runs, and that forecast
skill changes are measurable under matched demand streams. Do not add multi-hive
coupling or richer simulator mechanics from this result alone.

The scientifically sensible next step is a bounded read-only review of the A5
residual analyzer endpoints and promotion-rule mapping before deciding whether
the existing pilot should be extended to more paired seeds.
