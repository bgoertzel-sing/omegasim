# A2 Service-Capacity Holdout, Seeds 70..99

This holdout runs the preregistered demand-vs-service-capacity grid with
baseline attention shares and the `quota_balance` scheduler. It crosses
creation pressure `1.0`, `1.8`, and `2.2` with work service capacity `0.7`,
`1.0`, and `1.3`.

Source artifact:

- `runs/a2_service_capacity_holdout_seed70_99_20260624/`

Compact companions:

- `docs/results/a2_service_capacity_holdout_seed70_99_grid.csv`
- `docs/results/a2_service_capacity_holdout_seed70_99_effects.csv`

## Strategic Review Handling

The latest external review at
`../outputs/strategy-reviews/omegasim/latest-review.md` is marked
`strategic_change_level: minor` and `notify_ben: false`. Its recommendation to
move from scheduler seed extension to demand-vs-service-capacity analysis is
accepted as scientifically sensible. No GPT-5.5-Pro recommendation was rejected
or deferred in this run.

## Main Result

The service-capacity holdout supports a narrower mechanism reading than raw
queue depth alone. More service capacity reduces load-normalized backlog at
each fixed creation-pressure level, but higher creation pressure still
increases load-normalized backlog at every fixed service level.

High-minus-low service-capacity effects at fixed pressure:

| fixed pressure | queue depth delta | queue per created delta | completion fraction delta | queued age delta | value per work event delta | transition delta | longest dwell delta |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| normal `1.0` | -16.433334 | -0.315145 | 0.315145 | -1.601838 | 0.161858 | 2.266667 | -1.533333 |
| high `1.8` | -16.533334 | -0.168067 | 0.168067 | -0.760996 | 0.053512 | 2.866667 | -3.933333 |
| extreme `2.2` | -16.9 | -0.151263 | 0.151263 | -0.633885 | 0.159035 | 2.6 | -3.833333 |

Extreme-minus-normal creation-pressure effects at fixed service capacity:

| fixed service | queue depth delta | queue per created delta | completion fraction delta | queued age delta | value per work event delta | transition delta | longest dwell delta |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| low `0.7` | 34.9 | 0.20541 | -0.20541 | 0.769206 | -0.19278 | -4.033333 | 5.3 |
| baseline `1.0` | 36.233333 | 0.298512 | -0.298512 | 1.165276 | -0.217948 | -4.833333 | 5.266667 |
| high `1.3` | 34.433334 | 0.369292 | -0.369292 | 1.737159 | -0.195603 | -3.7 | 3 |

## Interpretation

Raw final queue depth remains mostly load accounting: more tasks are created
than completed, and `queue_depth_per_created_completed_balance_mean` is `1.0`
in every grid cell. The residual signal is in the normalized and trajectory
fields.

The strongest fixed-pressure service-capacity effect is at normal pressure:
raising service capacity from `0.7` to `1.3` lowers queue depth per created task
by `0.315145`, lowers final queued age by `1.601838`, raises value per work
event by `0.161858`, and increases lobe transitions by `2.266667`.

The strongest fixed-service demand-pressure effect is at high service capacity:
raising creation pressure from `1.0` to `2.2` increases queue depth per created
task by `0.369292`, raises final queued age by `1.737159`, lowers value per work
event by `0.195603`, and lengthens the longest lobe dwell by `3` ticks.

The lobe result is the bridge back to the original dynamics question. Under
pressure, every service-capacity row shifts toward fewer transitions and longer
`backlog_growth` dwell. Additional service partially offsets that locking, but
does not remove it at high or extreme demand.

## Next Step

Add a deterministic transition-entropy and dwell-distribution analysis over
the existing service-capacity holdout artifacts, then compare those trajectory
metrics against load-normalized backlog before running another experiment.
