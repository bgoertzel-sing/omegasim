# A3 queue-flow/service interpretation, seeds 70..99

This interpretation reads the existing A3 artifact:

- `runs/a3_queue_flow_service_analysis_seed70_99_20260625/summary.md`
- `runs/a3_queue_flow_service_analysis_seed70_99_20260625/queue_flow_service_metrics.csv`
- `runs/a3_queue_flow_service_analysis_seed70_99_20260625/queue_flow_service_effects.csv`

It does not add a simulation grid, simulator mechanics, dashboard, LLM call, or
new lobe observable. It follows `docs/a3_queue_flow_service_preregistration.md`
and treats A2 as frozen by
`docs/results/a2_exogenous_arrival_decision_synthesis_seed70_99.md`.

External strategic review handling:

- `../outputs/strategy-reviews/omegasim/latest-review.md`
- `strategic_change_level: major`
- `notify_ben: true`
- Accepted: freeze A2 as load/action-accounting dominated, stop broad residual
  lobe-mechanism sweeps, and prioritize decision synthesis over further A2
  residual-lobe search.
- Direction shift: A3 uses queue-flow, service capacity, load-normalized
  backlog, queued age, completion fraction, and work-opportunity accounting as
  primary endpoints. Ben should be notified because the external review marked
  this as a major strategic change.
- Deferred: stronger queue-blind trajectory nulls or first-order
  Markov-preserving nulls remain scientifically sensible analysis-only checks,
  but they are not needed for this queue-flow/service interpretation.
- Rejected: no recommendation was rejected.

## Decision summary

The A3 artifact supports a mechanism-clean accounting interpretation. Demand
pressure and exogenous arrivals increase load-normalized backlog and queued age.
Higher service capacity reduces load-normalized backlog, increases completion
fraction, and increases work events at fixed pressure. These effects are
adequately explained by queue inflow, finite service capacity, and work
opportunity.

The analysis does not reveal a residual unexplained structure that would reopen
the A2 lobe-grammar hypothesis. Baseline and queue-blind lobe summaries remain
secondary diagnostics only.

## Classified claims

| Classification | Claim | Evidence | Interpretation |
| --- | --- | --- | --- |
| Load accounting | Fixed-service pressure increases load-normalized backlog | Extreme-minus-normal pressure queue-depth-per-created deltas are `0.205410` at low service, `0.298512` at baseline service, and `0.369292` at high service | Higher demand relative to service capacity leaves more created tasks queued; this is the strongest A3 effect and does not require a lobe-grammar explanation |
| Load accounting | Exogenous arrivals increase load while agent create pressure stays fixed | Endogenous-to-high-exogenous queue-depth-per-created delta is `0.241756`; agent-created tasks stay near control at `41.433333` to `40.166667`; exogenous-created tasks rise to `38.100000` | The exogenous condition reproduces backlog pressure without raising agent task-creation pressure, supporting the A2 load/accounting conclusion |
| Service-capacity response | Higher service capacity reduces backlog at every pressure level | High-minus-low service-capacity queue-depth-per-created deltas are `-0.315145`, `-0.168067`, and `-0.151263` for normal, high, and extreme pressure | Service capacity absorbs load, with the largest marginal backlog reduction at normal pressure |
| Service-capacity response | Higher service capacity improves completion fraction at every pressure level | Completion-fraction deltas mirror backlog deltas: `+0.315145`, `+0.168067`, and `+0.151263` | The queue-depth-per-created and completion-fraction relationship is direct accounting under these closed task-flow summaries |
| Work-opportunity synchronization | More service capacity increases realized work events | Work-event deltas are `+18.066667`, `+18.800000`, and `+18.266667` for normal, high, and extreme pressure | The service-capacity axis primarily changes available and realized work opportunity |
| Work-opportunity synchronization | Service/completion correlation shifts are small relative to load effects | The strongest service/completion correlation shift is `+0.110715` for normal-pressure high-minus-low service capacity; high exogenous arrivals shift it by `-0.058790` | These correlations are useful diagnostics, but they are not strong enough to claim a new synchronization mechanism |
| Residual unexplained structure | No primary A3 endpoint requires residual lobe grammar | Flow-balance-to-queue-delta correlation is `1.0` in all rows, and queue-depth-per-created-completed-balance is `1.0` in all rows | The current primary endpoints are explained by queue-flow accounting; residual lobe claims stay unsupported |

## Effect reading

The strongest load-normalized backlog effect is the fixed-high-service
normal-to-extreme pressure contrast: queue-depth per created task rises by
`0.369292`, while completion fraction falls by `0.369292` and queued-task mean
age rises by `1.737159`. This is a load/accounting result because the pressure
axis increases task creation and reduces relative completion under finite
service.

The strongest service-capacity effect is at normal pressure: high-minus-low
service capacity lowers queue-depth per created task by `0.315145`, raises
completion fraction by `0.315145`, adds `18.066667` work events, and lowers
final queued-task mean age by `1.601838`. This is a service-capacity response,
not a residual lobe effect.

The exogenous-arrival axis is the cleanest demand-decoupling check. With fixed
agent task-creation pressure and baseline service capacity, high exogenous
arrivals raise total created tasks from `41.433333` to `78.266667`, lower
completion fraction from `0.492230` to `0.250474`, and raise queue-depth per
created task from `0.507770` to `0.749526`. Agent-created tasks remain close to
control, so the effect is demand load rather than create-action pressure.

## Interpretation guardrails

Raw queue depth and queue-depth-per-created-completed-balance should continue
to be treated as accounting fields. The all-row
`flow_balance_queue_delta_corr_mean = 1.0` result confirms that the current
flow-balance correlation endpoint is mostly an identity check, not an
independent synchronization discovery.

Service/completion correlation is a reasonable secondary diagnostic, but the
observed shifts are modest and change sign across demand conditions. It should
not be promoted to a primary mechanism claim without a separate preregistered
lagged or cross-condition synchronization test.

Baseline and queue-blind lobe summaries remain secondary diagnostics. No A3
result here justifies reopening broad A2 residual-lobe sweeps or adding new
simulator mechanisms to rescue the lobe-grammar hypothesis.

## Next step

Add one narrowly preregistered A3 analysis-only check for lagged
service/queue-flow synchronization using existing per-tick artifacts, with
flow-balance identity fields excluded from the primary synchronization endpoint.
