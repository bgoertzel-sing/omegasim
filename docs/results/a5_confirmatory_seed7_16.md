# A5 Confirmatory Seed 7..16

## Scope

This bounded fresh A5 run uses seeds `7..16`, excluding the pilot/analyzer-development seeds `5,6`.
It follows `docs/a5_confirmatory_addendum.md`: single-hive only, matched demand streams,
budget-matched timing-broken nulls, and prospective practical guardrails.

Run artifacts are intentionally local under ignored `runs/` paths:

```bash
.venv-conda/bin/python -m ohdyn.compare_predictive_control \
  --seeds 7 8 9 10 11 12 13 14 15 16 \
  --out runs/a5_predictive_control_confirmatory_seed7_16_20260626

.venv-conda/bin/python -m ohdyn.analyze_a5_residual_accounting \
  --compare-dir runs/a5_predictive_control_confirmatory_seed7_16_20260626 \
  --out runs/a5_residual_accounting_confirmatory_seed7_16_20260626
```

## Comparison Summary

The comparison ran 60 deterministic simulations across reactive, linear, nonlinear,
oracle, linear-budget shuffled, and nonlinear-budget shuffled conditions.
Matched final task creation held at `74.2` mean tasks for every condition.

Condition means:

| condition | budget | forecast_skill | completion_fraction | queue_depth | queued_age_final |
| --- | ---: | ---: | ---: | ---: | ---: |
| reactive | 0.00 | 0.877957 | 0.434071 | 42.7 | 5.725288 |
| linear | 0.35 | 0.911474 | 0.428319 | 43.1 | 5.774823 |
| nonlinear | 0.65 | 0.961990 | 0.420349 | 43.7 | 5.801917 |
| oracle | 1.00 | 1.000000 | 0.426118 | 43.3 | 5.783507 |
| shuffled | 0.35 | 0.866049 | 0.436788 | 42.6 | 5.681533 |
| nonlinear_shuffled | 0.65 | 0.866049 | 0.436788 | 42.6 | 5.681533 |

Forecast skill improved for both intermediate predictors:

- linear minus reactive: `+0.033517`
- linear minus shuffled: `+0.045425`
- nonlinear minus reactive: `+0.084033`
- nonlinear minus nonlinear_shuffled: `+0.095941`

## Residual Accounting

The read-only residual accounting analyzer emitted `4800` metric rows and `480`
effect rows. Primary full-accounting residual-state predictability contrasts:

| contrast | mean_delta | positive_delta_rate | interpretation |
| --- | ---: | ---: | --- |
| linear minus reactive | 0.114949 | 0.5 | inside paired label-permutation interval |
| linear minus shuffled | -0.053977 | 0.5 | inside paired label-permutation interval |
| nonlinear minus reactive | 0.077593 | 0.7 | inside paired label-permutation interval |
| nonlinear minus nonlinear_shuffled | -0.091333 | 0.3 | inside paired label-permutation interval |

## Promotion Audit

The analyzer's preregistered promotion audit failed closed:

- linear: forecast-skill criteria passed, practical guardrails passed, but residual
  structure versus reactive and shuffled did not pass, and nontriviality versus
  oracle did not pass.
- nonlinear: forecast-skill criteria passed, but practical guardrails failed and
  residual structure versus reactive and nonlinear-budget shuffled did not pass.

Interpretation: the fresh 10-seed set supports the conservative A5 reading that
resource-bounded prediction improves forecast skill under matched demand streams,
but does not demonstrate promotion-worthy residual structured dynamics after
full accounting and budget-matched timing-broken nulls. Do not add multi-hive
coupling, richer lobe architecture, or external integrations from this result.
