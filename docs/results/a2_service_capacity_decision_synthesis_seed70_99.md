# A2 service-capacity decision synthesis, seeds 70..99

This synthesis combines the demand-vs-service-capacity holdout grid, the lobe-trajectory analysis, paired bootstrap controls when present, label-count null controls when present, and load/action accounting from existing run artifacts.

Source artifacts:

- `runs/a2_service_capacity_holdout_seed70_99_20260624/service_capacity_comparison_metrics.csv`
- `runs/a2_service_capacity_holdout_seed70_99_20260624/service_capacity_effects.csv`
- `runs/a2_service_capacity_trajectory_holdout_seed70_99_controls_20260625/service_capacity_trajectory_metrics.csv`
- `runs/a2_service_capacity_trajectory_holdout_seed70_99_controls_20260625/service_capacity_trajectory_effects.csv`

External strategic review handling:

- `../outputs/strategy-reviews/omegasim/latest-review.md`
- `strategic_change_level: minor`
- `notify_ben: false`
- Accepted: add a decision-oriented synthesis with action/load accounting, paired bootstrap, and label-count null controls before launching another experiment.
- Deferred: queue-blind lobe labeling is not rejected; it remains the next analysis-only robustness check after this synthesis.

## Decision summary

The current evidence supports a conservative interpretation. Raw final queue depth should be treated as load accounting. Pressure-induced trajectory locking remains the residual candidate signal, but the label-count null control makes the independent lobe-grammar claim more cautious because observed-minus-null dwell and entropy differences are small.

## Decision table

| Claim | Evidence | Current decision | Confound | Next falsification test |
| --- | --- | --- | --- | --- |
| Queue depth is primarily load accounting | queue_depth_per_created_completed_balance_mean is 1.0 in every grid cell; queue per created rises with pressure and falls with service | Treat raw queue depth as a baseline load observable, not an emergent lobe claim | Creation pressure is implemented through create_task action weight, so demand and action mix may be coupled | Use the load/action accounting panel before preregistering an exogenous-arrival decoupling test |
| Service capacity absorbs load at fixed pressure | High-minus-low service-capacity queue-per-created deltas: -0.315145, -0.168067, -0.151263 | Keep service capacity as a mechanism-discriminating axis | Effects depend on paired seed uncertainty and label controls | Preserve paired bootstrap and null-control reporting in future grids |
| Creation pressure increases normalized backlog at fixed service | Extreme-minus-normal pressure queue-per-created deltas: 0.20541, 0.298512, 0.369292 | Demand pressure remains a robust load driver after normalizing by created tasks | Higher pressure also changes effective work opportunity | Run a preregistered exogenous-arrival decoupling test after analysis controls |
| Pressure induces candidate lobe trajectory locking | Extreme-minus-normal pressure transition-entropy deltas: -1.166135, -1.292786, -0.702994 | Treat trajectory locking as a candidate residual signal, not an independent lobe grammar finding yet | backlog_growth labels are partly derived from queue movement | Compare trajectory deltas against label-count nulls and queue-blind labels |
| Service capacity partially unlocks trajectories | High-minus-low service-capacity transition-entropy deltas: 0.337663, 0.665824, 0.800804 | Keep residual-locking hypothesis alive as load-mediated | Raw and normalized entropy are sensitive to label prevalence | Report normalized entropy, null-adjusted dwell, and action accounting together |

## Load/action accounting panel

| Pressure | Service | Created | Completed | Completion fraction | Create actions | Work actions | Work events | Idle actions | Message actions | Queue/balance |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| normal_pressure | low_service | 44.833333 | 14.566667 | 0.334003 | 44.833333 | 35.6 | 35.6 | 34.533333 | 65.033333 | 1 |
| normal_pressure | baseline_service | 41.433333 | 19.933333 | 0.49223 | 41.433333 | 45.966667 | 45.966667 | 32.866667 | 59.733333 | 1 |
| normal_pressure | high_service | 38.4 | 24.566667 | 0.649148 | 38.4 | 53.666667 | 53.666667 | 32.133333 | 55.8 | 1 |
| high_pressure | low_service | 66.9 | 11.633333 | 0.176149 | 66.9 | 29.866667 | 29.866667 | 30.066667 | 53.166667 | 1 |
| high_pressure | baseline_service | 63.6 | 15.4 | 0.247199 | 63.6 | 38.8 | 38.8 | 28.066667 | 49.533333 | 1 |
| high_pressure | high_service | 58.566667 | 19.833333 | 0.344216 | 58.566667 | 48.666667 | 48.666667 | 26.266667 | 46.5 | 1 |
| extreme_pressure | low_service | 74.633333 | 9.466667 | 0.128593 | 74.633333 | 27.5 | 27.5 | 27.833333 | 50.033333 | 1 |
| extreme_pressure | baseline_service | 71.233333 | 13.5 | 0.193718 | 71.233333 | 36.266667 | 36.266667 | 26.2 | 46.3 | 1 |
| extreme_pressure | high_service | 66.5 | 18.233333 | 0.279856 | 66.5 | 45.766667 | 45.766667 | 24.633333 | 43.1 | 1 |

The panel confirms the mechanism confound: task creation pressure changes created-task counts and the action mix, while service capacity changes work-task opportunity. That supports the load-accounting interpretation and motivates an exogenous-arrival decoupling test before stronger claims.

## Trajectory controls

- grid rows: 9
- trajectory rows: 9
- paired bootstrap rows: 30; sign-stable rows at >=0.95: 29
- strongest observed-minus-null dwell locking: extreme_pressure / baseline_service dwell_length_max_observed_minus_null=0.203

## Recommended next analysis

Run the queue-blind lobe labeling pass as an analysis-only robustness check over the same holdout artifacts. Do not replace the default lobe labeler or launch a new experiment until that check says whether pressure locking survives without queue-depth and queue-delta fields.
