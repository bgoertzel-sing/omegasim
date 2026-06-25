# A2 service-capacity decision synthesis, seeds 70..99

This synthesis combines the demand-vs-service-capacity holdout grid and the
follow-up lobe-trajectory analysis without rerunning simulations.

Source artifacts:

- `docs/results/a2_service_capacity_holdout_seed70_99_grid.csv`
- `docs/results/a2_service_capacity_holdout_seed70_99_effects.csv`
- `docs/results/a2_service_capacity_trajectory_holdout_seed70_99_metrics.csv`
- `docs/results/a2_service_capacity_trajectory_holdout_seed70_99_effects.csv`

External strategic review handling:

- `../outputs/strategy-reviews/omegasim/latest-review.md`
- `strategic_change_level: minor`
- `notify_ben: false`
- Accepted: turn the service-capacity result into a decision-oriented artifact
  before launching another experiment.
- Deferred: paired seed-bootstrap intervals, label-count null controls,
  load/action accounting panels, and queue-blind lobe labeling are not rejected;
  they are the next analysis layer after this synthesis.

## Decision summary

The current evidence supports a conservative interpretation. Raw final queue
depth should be treated as load accounting, not as the central emergent lobe
result. The stronger residual candidate is pressure-induced trajectory locking:
as creation pressure rises, lobe transitions become less diverse, dwell runs
lengthen, and `backlog_growth` occupies more of the run.

Additional service capacity partially counteracts that locking. At fixed
creation pressure, high-minus-low service capacity reduces queue per created
task in all three pressure rows, increases transition entropy in all three
rows, shortens max dwell, and reduces `backlog_growth` dwell share.

Creation pressure still dominates at fixed service capacity. Extreme-minus-
normal pressure increases queue per created task in all three service rows,
reduces transition entropy in all three rows, lengthens max dwell, and raises
`backlog_growth` dwell share.

## Decision table

| Claim | Evidence | Current decision | Confound | Next falsification test |
| --- | --- | --- | --- | --- |
| Queue depth is primarily load accounting. | `queue_depth_per_created_completed_balance_mean` is `1.0` in every grid cell, while queue per created rises with pressure and falls with service. | Treat raw queue depth as a baseline load observable, not an emergent lobe claim. | Creation pressure is implemented through `create_task` action weight, so demand and action mix may be coupled. | Add an action/load accounting panel with created tasks, completed tasks, completion fraction, create/work/idle/message counts, work events, and queue-per-created-completed balance. |
| Service capacity absorbs load at fixed pressure. | High-minus-low service capacity queue-per-created deltas are `-0.315145`, `-0.168067`, and `-0.151263` at normal, high, and extreme pressure. | Keep service capacity as a mechanism-discriminating axis. | Effects are point estimates over seeds `70..99`; paired uncertainty has not been reported. | Add paired seed-bootstrap intervals and sign stability while preserving each seed's full 3x3 grid. |
| Creation pressure still increases normalized backlog at fixed service. | Extreme-minus-normal pressure queue-per-created deltas are `0.20541`, `0.298512`, and `0.369292` at low, baseline, and high service. | Demand pressure remains a robust load driver after normalizing by created tasks. | Higher pressure may also change effective work opportunity through action competition. | Run a preregistered decoupling test only after analysis controls: vary exogenous arrivals independently from work-action opportunity. |
| Pressure induces lobe trajectory locking. | Extreme-minus-normal pressure transition-entropy deltas are `-1.166135`, `-1.292786`, and `-0.702994`; max-dwell deltas are `5.3`, `5.266667`, and `3`; backlog-growth dwell-share deltas are `0.255555`, `0.375`, and `0.427778`. | Treat this as the main residual candidate dynamics signal. | Lobe-label circularity: `backlog_growth` is partly derived from queue movement and action dominance. | Add a label-count-preserving null control, then compare observed-minus-null dwell, transition count, and entropy. |
| Service capacity partially unlocks trajectories. | High-minus-low service-capacity transition-entropy deltas are `0.337663`, `0.665824`, and `0.800804`; max-dwell deltas are `-1.533333`, `-3.933333`, and `-3.833333`; backlog-growth dwell-share deltas are `-0.322223`, `-0.213889`, and `-0.15`. | Keep the residual-locking hypothesis alive, but state it as partially load-mediated. | Raw and normalized entropy are sensitive to label prevalence and transition counts. | Report normalized entropy alongside a label-count null, then inspect whether observed locking survives. |

## Mechanism reading

The 3x3 grid separates two effects that were previously conflated in raw queue
depth. First, higher service capacity makes the system less backlogged at the
same demand level: completion fraction rises by `0.315145`, `0.168067`, and
`0.151263` across the normal, high, and extreme pressure rows. Second, stronger
creation pressure still pushes the system toward overload at every service
level: completion fraction falls by `0.20541`, `0.298512`, and `0.369292`
across low, baseline, and high service.

The trajectory fields add the more interesting dynamics claim. At high and
extreme pressure, all dominant-lobe counts collapse to `backlog_growth:30`
except high-pressure/high-service, which is `backlog_growth:30` in the
trajectory artifact and `backlog_growth:29|execution:1` in the grid summary.
This means pressure makes the emitted lobe process spend more time in one
state, but the interpretation remains partly circular until the null control
and queue-blind check are added.

## Recommended next analysis

Before running another experiment, add deterministic controls over the existing
service-capacity holdout artifacts:

1. Paired seed-bootstrap uncertainty for queue per created, transition entropy,
   normalized entropy, max dwell, and backlog-growth dwell share.
2. Label-count-preserving null trajectories for dwell length, transition count,
   and entropy.
3. A compact load/action accounting panel for created, completed, completion
   fraction, work events, create-task/work-task action counts, and idle/message
   counts.

The next experiment after those controls should be an exogenous-arrival
decoupling test that varies task arrivals independently from agent
`create_task` action choice and keeps work opportunity interpretable.
