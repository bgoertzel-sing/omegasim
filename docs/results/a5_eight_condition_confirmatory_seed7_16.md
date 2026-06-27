# A5 Eight-Condition Confirmatory Seed 7..16

## Scope

This bounded A5 run repeats the fresh confirmatory seed `7..16` set after the
eight-condition scaffold was frozen. It adds the preregistered
`nonlinear_high_budget` condition and its budget-matched timing-broken null,
`nonlinear_high_budget_shuffled`, to the earlier six-condition confirmatory
set.

No simulator mechanics, multi-hive coupling, lobe labels, dashboards, real LLM
calls, Lean, Slack, browser automation, Atomspace integration, or external
services were added.

External strategic review handling:

- `../outputs/strategy-reviews/omegasim/latest-review.md`
- `strategic_change_level: none`
- `notify_ben: false`
- Deferred: the review recommended an A7 implementation gate. This was not
  followed in this run because `AUTOMATION_STATUS.md` is the source of truth
  and records Ben's newer explicit A5 reopening plus the next step to run the
  eight-condition A5 confirmatory set.

## Commands

```bash
.venv-conda/bin/python -m ohdyn.compare_predictive_control \
  --seeds 7 8 9 10 11 12 13 14 15 16 \
  --out runs/a5_predictive_control_confirmatory_seed7_16_eight_condition_20260627

.venv-conda/bin/python -m ohdyn.analyze_a5_residual_accounting \
  --compare-dir runs/a5_predictive_control_confirmatory_seed7_16_eight_condition_20260627 \
  --out runs/a5_residual_accounting_confirmatory_seed7_16_eight_condition_20260627
```

## Comparison Summary

The comparison ran 80 deterministic simulations across the eight matched A5
conditions. Final task creation remained matched at `74.2` mean tasks for every
condition.

| condition | budget | forecast_skill | completion_fraction | queue_depth | queued_age_final | capture_pressure_peak |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| reactive | 0.00 | 0.877957 | 0.434071 | 42.7 | 5.725288 | 0.101995 |
| linear | 0.35 | 0.911474 | 0.428319 | 43.1 | 5.774823 | 0.095788 |
| nonlinear | 0.65 | 0.961990 | 0.420349 | 43.7 | 5.801917 | 0.095494 |
| nonlinear_high_budget | 0.85 | 0.972753 | 0.419240 | 43.8 | 5.819492 | 0.092729 |
| oracle | 1.00 | 1.000000 | 0.426118 | 43.3 | 5.783507 | 0.091573 |
| shuffled | 0.35 | 0.866049 | 0.436788 | 42.6 | 5.681533 | 0.117635 |
| nonlinear_shuffled | 0.65 | 0.866049 | 0.436788 | 42.6 | 5.681533 | 0.117635 |
| nonlinear_high_budget_shuffled | 0.85 | 0.866049 | 0.436788 | 42.6 | 5.681533 | 0.117635 |

Forecast skill improved for all predictor conditions versus their required
comparators:

| contrast | forecast_skill_delta |
| --- | ---: |
| linear minus reactive | 0.033517 |
| nonlinear minus reactive | 0.084033 |
| nonlinear_high_budget minus reactive | 0.094796 |
| linear minus shuffled | 0.045425 |
| nonlinear minus nonlinear_shuffled | 0.095941 |
| nonlinear_high_budget minus nonlinear_high_budget_shuffled | 0.106704 |

## Residual Accounting

The read-only residual accounting analyzer emitted `6400` metric rows and
`720` effect rows. Primary full-accounting residual-state predictability
contrasts all remained inside paired label-permutation intervals:

| contrast | mean_delta | positive_delta_rate | interpretation |
| --- | ---: | ---: | --- |
| linear minus reactive | 0.114949 | 0.5 | inside paired label-permutation interval |
| nonlinear minus reactive | 0.077593 | 0.7 | inside paired label-permutation interval |
| nonlinear_high_budget minus reactive | 0.162115 | 0.6 | inside paired label-permutation interval |
| linear minus shuffled | -0.053977 | 0.5 | inside paired label-permutation interval |
| nonlinear minus nonlinear_shuffled | -0.091333 | 0.3 | inside paired label-permutation interval |
| nonlinear_high_budget minus nonlinear_high_budget_shuffled | -0.006811 | 0.5 | inside paired label-permutation interval |

## Decision

The eight-condition A5 confirmatory set fails closed. The high-budget nonlinear
condition improves forecast skill, including versus its own budget-matched
timing-broken null, but it does not pass the preregistered residual-structure
criteria or practical guardrails.

The conservative A5 interpretation is unchanged: this scaffold supports a
narrow forecast-skill manipulation under matched deterministic demand streams,
not a claim of residual lobe grammar, attractor-like collective dynamics, or a
mechanism that survives full accounting controls.
