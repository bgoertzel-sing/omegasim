# A3 queue-flow/service synthesis, seeds 70..99

This synthesis freezes the current A3 interpretation using existing artifacts
only:

- `runs/a3_queue_flow_service_analysis_seed70_99_20260625/summary.md`
- `runs/a3_queue_flow_service_analysis_seed70_99_20260625/queue_flow_service_metrics.csv`
- `runs/a3_queue_flow_service_analysis_seed70_99_20260625/queue_flow_service_effects.csv`
- `runs/a3_lagged_service_sync_seed70_99_20260625/summary.md`
- `runs/a3_lagged_service_sync_seed70_99_20260625/lagged_service_sync_metrics.csv`
- `runs/a3_lagged_service_sync_seed70_99_20260625/lagged_service_sync_effects.csv`

No simulations were rerun. No simulator mechanics, dashboards, LLM calls, Lean,
Slack, browser automation, Atomspace integration, or multi-hive coupling were
added.

External strategic review handling:

- `../outputs/strategy-reviews/omegasim/latest-review.md`
- `strategic_change_level: minor`
- `notify_ben: false`
- Accepted: write the A3 synthesis now, keep queue-flow/service accounting
  frozen, treat lagged synchronization as modest and exploratory, and add
  seed-level uncertainty caveats before any later multi-hive preregistration
  uses queue-flow/service endpoints.
- Deferred: a temporal-shift or block-shuffle null for lagged synchronization
  remains scientifically sensible, but it is not needed to freeze this A3
  interpretation because the observed lagged effects are not promoted to
  mechanism claims.
- Rejected: no recommendation was rejected.

## Decision summary

A3 supports a mechanism-clean queue-flow/service interpretation. Demand pressure
raises total task inflow, load-normalized backlog, and queued-task age. Higher
service capacity reduces backlog and improves completion fraction at fixed
pressure. Exogenous arrivals reproduce backlog pressure while agent-created
tasks remain near the endogenous control.

Lagged service/completion and service/load-change correlations are retained as
secondary synchronization diagnostics only. Their condition-mean shifts are
modest, and seed-level signs are not strong enough to justify a new
synchronization mechanism claim. Same-tick created-completed balance versus
queue-delta correlation is an identity-like accounting diagnostic, not evidence
of synchronization.

The A2 residual lobe-grammar hypothesis remains closed under the current
single-hive simulator and label scheme. Baseline and queue-blind lobe summaries
are useful diagnostics, not primary evidence for independent lobe dynamics.

## Claim classification

| Classification | Frozen claim | Evidence | Interpretation |
| --- | --- | --- | --- |
| Load accounting | Demand pressure increases load-normalized backlog | Extreme-minus-normal pressure queue-depth-per-created deltas are `0.205410`, `0.298512`, and `0.369292` at low, baseline, and high service | The pressure axis increases task inflow relative to finite service; this is accounting, not lobe grammar |
| Load accounting | Exogenous arrivals decouple demand load from agent create pressure | High exogenous arrivals raise total created tasks from `41.433333` to `78.266667`, while agent-created tasks stay near control at `41.433333` to `40.166667` | Backlog pressure can be induced by external demand without raising agent create-task pressure |
| Service-capacity response | Higher service capacity reduces backlog at fixed pressure | High-minus-low service queue-depth-per-created deltas are `-0.315145`, `-0.168067`, and `-0.151263` | More service absorbs queue load, with the largest effect at normal pressure |
| Service-capacity response | Higher service capacity improves completion fraction | Completion-fraction deltas match the backlog deltas with opposite sign: `+0.315145`, `+0.168067`, and `+0.151263` | Completion fraction and load-normalized backlog are tightly coupled queue-flow summaries |
| Work opportunity | Higher service capacity increases realized work events | Work-event deltas are `+18.066667`, `+18.800000`, and `+18.266667` | The service axis changes work opportunity and successful work volume |
| Modest synchronization diagnostic | Lagged service/completion shifts exist but are small | Strongest condition-mean shift is `0.168460`; its seed median is `0.220475`, bootstrap median CI `[-0.052914, 0.447535]`, sign stability `0.67` | Useful descriptive diagnostic, but not a mechanism claim |
| Modest synchronization diagnostic | Lagged service/load-change shifts are weaker | Strongest condition-mean shift is `-0.096587`; its seed median is `-0.144239`, bootstrap median CI `[-0.342856, 0.036087]`, sign stability `0.60` | Direction is not seed-stable enough to carry scientific weight |
| Artifact invariant | Same-tick flow balance tracks queue delta exactly | Flow-balance versus queue-delta correlation is `1.0` across condition means and effect deltas are `0.0` | This validates accounting consistency and must not be interpreted as synchronization |
| Unsupported residual structure | No primary A3 endpoint requires residual lobe grammar | Load, service capacity, completion fraction, and work opportunity explain the observed effects | Do not reopen broad A2 residual-lobe sweeps without a concrete artifact bug |

## Lagged endpoint caveats

The lagged synchronization reader reports the stronger of lag `-1` and lag `+1`
for each condition mean. That best-lag choice is descriptive and can inflate
apparent effects. Any future preregistered synchronization experiment should
choose causal lag direction in advance or report both lags separately.

Lightweight seed-level checks over the existing per-seed metrics show that the
lagged effects are not robust enough for a mechanism claim:

- Strongest service/completion condition-mean shift:
  `normal_pressure/low_service -> normal_pressure/high_service = 0.168460`;
  seed median `0.220475`; bootstrap median CI `[-0.052914, 0.447535]`; sign
  stability `0.67` over 30 paired seeds.
- Next service/completion shifts include confidence intervals that either cross
  zero or have only moderate sign stability, even when the condition mean is
  similar in magnitude.
- Strongest service/load-change condition-mean shift:
  `normal_pressure/high_service -> extreme_pressure/high_service = -0.096587`;
  seed median `-0.144239`; bootstrap median CI `[-0.342856, 0.036087]`; sign
  stability `0.60` over 30 paired seeds.
- The lagged endpoint should therefore remain an exploratory diagnostic until a
  temporal-shift, block-shuffle, or preregistered lag-direction null is added.

## Later multi-hive implication

If OmegaSim later moves to multi-hive Moltbook coupling, the primary
preregistration should use queue-flow/service endpoints rather than lobe
grammar:

- queue inflow and service capacity;
- completion fraction;
- load-normalized backlog;
- queued-task age;
- work-event opportunity and completion;
- preregistered cross-hive service/load phase relations.

Lobe labels should remain secondary unless a genuinely non-queue,
non-action-derived observable is introduced and tested against stronger nulls.

## Frozen next step

Draft a separate multi-hive preregistration only if the project is ready to add
coupling mechanics; otherwise keep the baseline stable and avoid new A2
residual-lobe experiments.
