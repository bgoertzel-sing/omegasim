# A2 Scheduler Ablation Synthesis

This synthesis compares the seed `1..3` pilot block with the seed `70..99`
holdout for the preregistered scheduler-mechanism ablation. The second generic
comparison-runner policy label, `research_heavy`, is normalized here to
`random_available`; the baseline label is normalized to `quota_balance`.

Source artifacts:

- `runs/a2_scheduler_ablation_seed1_3_20260624/`
- `runs/a2_scheduler_ablation_seed1_3_analysis_bootstrap_20260624/`
- `runs/a2_scheduler_ablation_holdout_seed70_99_20260624/`
- `runs/a2_scheduler_ablation_holdout_seed70_99_analysis_bootstrap_20260624/`

The compact machine-readable companion is
`docs/results/a2_scheduler_ablation_synthesis.csv`.

## Strategic Review Handling

The latest external review available at
`../outputs/strategy-reviews/omegasim/latest-review.md` is marked
`strategic_change_level: minor` and `notify_ben: false`. Its recommendation to
turn the pilot-vs-holdout comparison into paired scheduler-effect and
load-normalized backlog accounting is accepted as scientifically sensible. No
major direction shift was made in this run.

## Main Result

The holdout strengthens the conservative reading: creation pressure robustly
amplifies backlog under both schedulers, and the scheduler swap does not remove
the pressure response.

In the holdout, mean final queue depth rises:

- `quota_balance`: `21.5 -> 48.2 -> 57.733333`
- `random_available`: `21.6 -> 45.5 -> 56.166667`

The paired holdout scheduler effect, `random_available - quota_balance`, is
small compared with the pressure effect:

- normal pressure: `0.1` final queue-depth units, bootstrap interval
  `[-2.233333, 2.066667]`
- medium pressure: `-2.7`, bootstrap interval `[-4.833333, -0.766667]`
- high pressure: `-1.566667`, bootstrap interval `[-4.3, 0.833333]`
- high-minus-normal pressure delta: `-1.666667`, bootstrap interval
  `[-5.1, 1.633333]`

This means the holdout does not support a claim that quota balancing is causing
the raw backlog pressure response. It does support a narrower claim that
scheduler choice changes curve shape and secondary metrics.

## Load Accounting

Raw queue depth is close to a load/capacity outcome in this abstraction.
Created-task means and completion fractions make that explicit:

| block | scheduler | normal created | high created | normal completion fraction | high completion fraction |
| --- | --- | ---: | ---: | ---: | ---: |
| pilot `1..3` | `quota_balance` | 40 | 73.666667 | 0.485720 | 0.151448 |
| pilot `1..3` | `random_available` | 40 | 74.666667 | 0.405556 | 0.125074 |
| holdout `70..99` | `quota_balance` | 41.433333 | 71.233333 | 0.492230 | 0.193718 |
| holdout `70..99` | `random_available` | 41.466667 | 70.366667 | 0.493121 | 0.208362 |

Load-normalized normal-to-high queue growth is nearly identical in the holdout:

- `quota_balance`: `1.209774` final queue-depth units per added created task,
  bootstrap interval `[1.154681, 1.249447]`
- `random_available`: `1.200961`, bootstrap interval
  `[1.145654, 1.25936]`

This is the key accounting result. The backlog signal remains real as a
baseline observable, but it should not be treated as an emergent lobe-dynamics
finding by itself.

## Pilot Versus Holdout

The pilot and holdout agree on the important qualitative point: both scheduler
conditions accumulate substantially more queue under higher creation pressure.
They disagree on exact scheduler ranking:

- Pilot `1..3`: `random_available` has higher final queue depth at normal,
  medium, and high pressure, but the paired high-minus-normal queue-depth effect
  is exactly `0`.
- Holdout `70..99`: `quota_balance` has slightly higher mean final queue depth
  at medium and high pressure, and the paired high-minus-normal effect is
  `-1.666667` in favor of lower random-available backlog.

The ranking disagreement is not a failed replication of the mechanism claim.
It is evidence that scheduler rank is seed-sensitive while backlog amplification
under pressure is stable.

## Secondary Signals

The holdout secondary effects remain suggestive, not decisive:

- `random_available - quota_balance` high-minus-normal value per completed task:
  `0.106882`, bootstrap interval `[-0.057457, 0.286432]`
- `random_available - quota_balance` high-minus-normal value per work event:
  `0.083488`, bootstrap interval `[-0.053673, 0.208697]`
- `random_available - quota_balance` high-minus-normal max capture pressure:
  `0.069197`, bootstrap interval `[0.021344, 0.109437]`
- `random_available - quota_balance` high-minus-normal turning points:
  `-0.633333`, bootstrap interval `[-1.9, 0.566667]`
- `random_available - quota_balance` high-minus-normal longest dwell:
  `1.2`, bootstrap interval `[0.166667, 2.466667]`

The dwell result is the most relevant bridge back to lobe dynamics: pressure
appears to reduce trajectory variability and lengthen dwell runs, especially
under `random_available`. This should be tested directly with transition,
dwell, and entropy summaries before adding another seed-only scheduler sweep.

## Interpretation

Treat final queue depth as the baseline load observable. The scientifically
useful next mechanism question is not whether pressure creates backlog - it
does - but whether the simulator has residual dynamical structure after
normalizing for created load and service capacity.

The next preregistered experiment should therefore vary demand and service
capacity together before adding more scheduler seed extensions.
