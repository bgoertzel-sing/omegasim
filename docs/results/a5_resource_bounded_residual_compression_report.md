# A5 Resource-Bounded Residual-Compression Report

Date: 2026-06-27.

## Scope

This report completes the read-only diagnostic preregistered in
`docs/a5_resource_bounded_residual_compression_preregistration.md`.
It uses existing A5-family artifacts only. No simulator mechanics, configs,
simulation runs, dashboards, integrations, A7.2 mechanics, or multi-hive
coupling were added.

## Input Coverage

| artifact class | path | status |
| --- | --- | --- |
| reopened A5 comparison | `runs/a5_predictive_control_prereg_refresh_compare` | present; seeds `5,6`, six conditions |
| reopened A5 residual accounting | `runs/a5_residual_accounting_prereg_refresh` | present; includes full-accounting compression and predictability endpoints |
| confirmatory eight-condition comparison | `runs/a5_predictive_control_confirmatory_seed7_16_eight_condition_20260627` | present; seeds `7..16`, eight conditions |
| confirmatory eight-condition residual accounting | `runs/a5_residual_accounting_confirmatory_seed7_16_eight_condition_20260627` | present; includes full-accounting compression and predictability endpoints |
| A5.1a cost-calibration artifacts | `docs/results/a5_1a_cost_calibration_closure_note_seed5_6.md` | result-note coverage only; checked-in reusable run CSVs were not present under `runs/` |

The CSV-backed diagnostic therefore rests on the reopened seed `5,6` and
confirmatory seed `7..16` A5 residual-accounting outputs. A5.1a remains covered
by its existing closure note: charged predictors improved forecast skill over
spend-only replay nulls, but did not pass the full-accounting residual gate.

## Full-Accounting Compression Endpoints

Lower `compression_ratio` means the full-accounting residual state compressed
more under the existing deterministic zlib endpoint. `predictability_r2` is the
existing lag-1 residual-state predictability endpoint from the same analyzer.

| dataset | condition | compression_ratio | predictability_r2 | skill_per_budget |
| --- | --- | ---: | ---: | ---: |
| seed `5,6` | reactive | 0.412930 | -0.026977 | 0.000000 |
| seed `5,6` | linear | 0.409235 | -0.114194 | 2.617895 |
| seed `5,6` | nonlinear | 0.409882 | -0.092064 | 1.444177 |
| seed `5,6` | shuffled | 0.407409 | -0.298777 | 2.434204 |
| seed `5,6` | nonlinear shuffled | 0.407409 | -0.298777 | 1.310726 |
| seed `5,6` | oracle | 0.312165 | -0.360236 | 1.000000 |
| seed `7..16` | reactive | 0.410263 | -0.323080 | 0.000000 |
| seed `7..16` | linear | 0.408556 | -0.208131 | 2.617895 |
| seed `7..16` | nonlinear | 0.408879 | -0.245487 | 1.444177 |
| seed `7..16` | high-budget nonlinear | 0.408141 | -0.160965 | 1.118803 |
| seed `7..16` | shuffled | 0.409503 | -0.154153 | 2.434204 |
| seed `7..16` | nonlinear shuffled | 0.409503 | -0.154153 | 1.310726 |
| seed `7..16` | high-budget nonlinear shuffled | 0.409503 | -0.154153 | 1.002319 |
| seed `7..16` | oracle | 0.309994 | -0.122586 | 1.000000 |

## Preregistered Contrasts

| dataset | contrast | compression delta | positive rate | permutation status | pass |
| --- | --- | ---: | ---: | --- | --- |
| seed `5,6` | linear minus reactive | -0.003695 | 0.0 | outside interval, lower endpoint | no |
| seed `5,6` | nonlinear minus reactive | -0.003047 | 0.0 | outside interval, lower endpoint | no |
| seed `5,6` | linear minus shuffled | 0.001826 | 1.0 | outside interval, higher endpoint | no |
| seed `5,6` | nonlinear minus nonlinear shuffled | 0.002474 | 0.5 | inside interval | no |
| seed `5,6` | oracle minus linear | -0.097070 | 0.0 | outside interval, lower endpoint | no |
| seed `5,6` | oracle minus nonlinear | -0.097717 | 0.0 | outside interval, lower endpoint | no |
| seed `7..16` | linear minus reactive | -0.001706 | 0.4 | inside interval | no |
| seed `7..16` | nonlinear minus reactive | -0.001384 | 0.5 | inside interval | no |
| seed `7..16` | high-budget nonlinear minus reactive | -0.002121 | 0.3 | inside interval | no |
| seed `7..16` | linear minus shuffled | -0.000946 | 0.4 | inside interval | no |
| seed `7..16` | nonlinear minus nonlinear shuffled | -0.000624 | 0.6 | inside interval | no |
| seed `7..16` | high-budget nonlinear minus high-budget shuffled | -0.001361 | 0.3 | inside interval | no |
| seed `7..16` | oracle minus linear | -0.098563 | 0.0 | outside interval, lower endpoint | no |
| seed `7..16` | oracle minus nonlinear | -0.098885 | 0.0 | outside interval, lower endpoint | no |
| seed `7..16` | oracle minus high-budget nonlinear | -0.098148 | 0.0 | outside interval, lower endpoint | no |

The seed `5,6` intermediate compression deltas versus reactive are lower, but
they do not beat the matched timing-broken nulls. The confirmatory seed
`7..16` contrasts are smaller and inside the paired label-permutation interval.
Oracle is consistently much more compressible than the intermediate predictors,
which is consistent with smoothing rather than a resource-bounded residual
signal.

The full-accounting residual predictability audit agrees with closure. In the
seed `7..16` confirmatory set, linear, nonlinear, and high-budget nonlinear
predictability contrasts versus their matched shuffled/null controls were all
inside the paired label-permutation interval.

## GPT-5.5-Pro Recommendation Handling

Accepted as scientifically sensible: keep prediction spend, oracle smoothing,
and timing-broken or spend-only nulls central to interpretation; do not make
structured-dynamics claims from forecast skill alone.

Deferred: the A7.2 delayed artifact-mediated endogenous-prediction direction
and any three-hive ring remain non-active pending Ben's explicit decision and a
fresh preregistration.

Recorded notification issue: the latest external review says `notify_ben:
true`, even though `strategic_change_level: none`. Ben should be notified that
the existing A5-exit/A7.2 decision request remains the next governance action
after this now-completed read-only diagnostic.

## Decision

Outcome: `closure_confirmed`.

The existing artifacts do not contain a promotion-worthy resource-bounded
compression signal. Forecast skill gains remain real in A5-family artifacts,
but full-accounting residual compression does not beat reactive, oracle, and
matched timing-broken or spend-only null expectations in a way that supports
structured-dynamics language.

Do not broaden A5-family seeds, add rescue mechanics, or start A7.2 or
multi-hive work from this result.

## Next Step

Send Ben the existing A5-exit/A7.2 decision request and keep automation closed
to new simulations or mechanics until he chooses closure, A7.2 preregistration,
or a separate three-hive preregistration.
