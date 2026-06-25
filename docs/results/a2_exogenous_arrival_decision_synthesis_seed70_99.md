# A2 exogenous-arrival decision synthesis, seeds 70..99

This synthesis compares the coupled-pressure, scheduler-ablation, service-capacity, queue-blind, exogenous-arrival holdout, paired bootstrap, and label-count null-control evidence already archived under `docs/results/`. It does not add a new simulation grid.

Source artifacts:

- `docs/results/a2_pressure_seed1_69.md`
- `docs/results/a2_scheduler_ablation_synthesis.md`
- `docs/results/a2_service_capacity_decision_synthesis_seed70_99.md`
- `docs/results/a2_queue_blind_lobes_holdout_seed70_99.md`
- `docs/results/a2_exogenous_arrival_holdout_seed70_99.md`
- `docs/results/a2_exogenous_arrival_controls_seed70_99.md`

External strategic review handling:

- `../outputs/strategy-reviews/omegasim/latest-review.md`
- `strategic_change_level: major`
- `notify_ben: true`
- Accepted: write the A2 decision synthesis now, freeze the A2 conclusion as load/action-accounting dominated, and stop broad residual-lobe mechanism sweeps unless the synthesis identifies a concrete artifact bug.
- Direction shift: the earlier A2 residual-lobe search is now closed as a negative/clarifying mechanism result. Ben should be notified because the review requested notification for this major shift.
- Deferred: stronger queue-blind trajectory nulls or first-order Markov-preserving nulls are scientifically sensible, but they are analysis-only follow-ups and not required before freezing the A2 conclusion.
- Rejected: no recommendation was rejected.

## Decision summary

A2 should be frozen as a mechanism-discriminating result. The simulator shows robust load pressure and action-budget-mediated trajectory changes, but the current evidence does not support an independent emergent lobe-grammar claim.

The decisive control is the exogenous-arrival holdout. It raises demand while holding agent `task_creation_pressure` fixed. Under high exogenous arrivals, total created tasks rise from `41.433333` to `78.266667`, while agent-created tasks remain near the endogenous control at `41.433333` to `40.166667`. Load grows strongly: high exogenous `queue_depth_per_created_task` delta is `0.241756`, CI `[0.209972, 0.276361]`, sign stability `1.0`.

The residual lobe claim weakens under this decoupling. High exogenous queue-blind entropy delta is `-0.098668`, CI `[-0.239733, 0.029129]`, sign stability `0.885`; queue-blind task-generation dwell-share delta is `-0.002778`, CI `[-0.036111, 0.030556]`, sign stability `0.575`. The stable execution dwell-share increase of `0.036111`, CI `[0.008333, 0.069445]`, sign stability `0.995`, is more naturally interpreted as increased work opportunity.

Label-count-preserving null controls also keep baseline-lobe claims conservative. High exogenous baseline transition-entropy observed-minus-null is only `0.019209`, high exogenous dwell-length-max observed-minus-null is `-0.020334`, and the strongest dwell observed-minus-null is `0.053` at medium exogenous arrivals.

## Decision table

| Claim | Evidence | Current decision | Confound | Next falsification test |
| --- | --- | --- | --- | --- |
| Demand can be raised without raising agent create-task pressure | Exogenous high raises total created mean from `41.433333` to `78.266667` while agent-created tasks remain near control at `41.433333` to `40.166667` | Accept the exogenous-arrival holdout as the decisive A2 demand decoupling control | Exogenous arrivals still change task availability and work opportunity | Do not run another broad A2 demand sweep unless a concrete artifact bug is found |
| Load growth is robust under exogenous demand | High exogenous queue-depth-per-created-task delta is `0.241756`, CI `[0.209972, 0.276361]`, sign stability `1.0` | Classify backlog and queued-age effects as load/accounting findings | Queue depth is mechanically tied to arrivals and finite service capacity | Use load-normalized queue-flow and service synchronization as primary endpoints in any next-stage preregistration |
| Queue-blind residual entropy is weak | High exogenous queue-blind entropy delta is `-0.098668`, CI `[-0.239733, 0.029129]`, sign stability `0.885` | Classify this as a weak residual point estimate, not a stable lobe-grammar result | Queue-blind labels still depend on action counts and work opportunity | Only revisit with a stronger trajectory null or non-action-derived lobe observable |
| Exogenous demand does not reproduce task-generation locking | High exogenous queue-blind task-generation dwell-share delta is `-0.002778`, CI `[-0.036111, 0.030556]`, sign stability `0.575` | Reject the stronger A2 claim that demand alone produces independent task-generation lobe locking | Prior coupled-pressure result changed action mix as well as load | Stop broad residual-lobe mechanism sweeps for A2 |
| Execution dwell increase is accounting-consistent | High exogenous queue-blind execution dwell-share delta is `0.036111`, CI `[0.008333, 0.069445]`, sign stability `0.995` | Treat the execution dwell change as work-opportunity mediated | More queued work makes execution labels more likely without implying independent grammar | Report it as an action-budget-mediated trajectory finding |
| Label-count nulls make baseline lobe claims conservative | High exogenous baseline entropy observed-minus-null is `0.019209` and dwell-length-max observed-minus-null is `-0.020334`; strongest dwell observed-minus-null is `0.053` at medium | Freeze A2 as load/action-accounting dominated and do not promote baseline lobe dwell as independent emergence | The null is label-count preserving rather than first-order Markov preserving | A future analysis-only check may use stronger nulls, but it should not block the A2 conclusion |

## Evidence integration

Coupled pressure established that increasing `model.task_creation_pressure` produces large backlog growth and trajectory changes. The scheduler ablation showed the backlog pressure response survives a `quota_balance` versus `random_available` scheduler swap, so the effect is not mainly an artifact of quota balancing.

The service-capacity holdout then separated demand pressure from service capacity. Higher service capacity reduced load-normalized backlog at fixed pressure and increased transition entropy, while higher creation pressure increased normalized backlog and reduced transition entropy. This supported a load-mediated trajectory interpretation, but creation pressure still directly changed action mix.

The queue-blind analysis showed pressure structure even after removing queue depth, queue delta, and the baseline lobe labeler. That kept a residual trajectory hypothesis alive, especially the coupled-pressure task-generation dwell-share increase. The exogenous-arrival holdout is the more discriminating test because it raises demand without increasing agent create-task pressure. It preserves robust load growth but does not reproduce the task-generation dwell-share locking.

## Frozen A2 conclusion

Classify A2 results as follows:

| Classification | Supported claim |
| --- | --- |
| Robust load/accounting finding | Demand and finite service capacity control backlog, queued age, completion fraction, and queue-per-created measures. |
| Action-budget-mediated trajectory finding | Changing create/work opportunity changes action-derived dwell and entropy summaries. |
| Weak residual point estimate | Exogenous load lowers queue-blind entropy in point estimate, but the interval crosses zero and sign stability is below the stable-effect threshold. |
| Unsupported lobe-grammar claim | The current simulator and label scheme do not demonstrate independent residual lobe grammar. |

## Recommendation

Stop broad A2 residual-lobe sweeps. Do not add simulator mechanisms to rescue the residual-lobe hypothesis. If OmegaSim proceeds toward a next phase, preregister queue-flow, service-capacity, and synchronization endpoints as primary; introduce any new lobe observables only if they are not mechanically derived from queue and action counts.
