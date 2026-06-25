# A3 Queue-Flow and Service-Capacity Preregistration

This document preregisters the next OmegaSim research stage after the frozen A2
decision synthesis. It is a design artifact only: it does not add simulator
mechanics, run a new grid, or reinterpret the existing A2 lobe evidence.

## Motivation

The A2 exogenous-arrival decision synthesis freezes the current interpretation:
OmegaSim demonstrates robust load/accounting effects and action-budget-mediated
trajectory structure, but it does not demonstrate an independent residual lobe
grammar under the current simulator and label scheme.

A3 should therefore move away from broad residual-lobe exploration. The next
scientific question is whether queue inflow, service capacity, and work
opportunity produce reproducible flow regimes that can be measured without
leaning on lobe labels derived from the same manipulated queue/action fields.

## Strategic Review Handling

The external strategic review in
`../outputs/strategy-reviews/omegasim/latest-review.md` was marked
`strategic_change_level: major` and `notify_ben: true`. Its recommendation to
freeze A2 as load/action-accounting dominated and stop broad residual-lobe
mechanism sweeps is accepted as scientifically sensible.

Direction shift: A3 treats queue-flow, service capacity, load-normalized
backlog, queued-task age, and work-opportunity accounting as primary. Ben should
be notified that the A2 residual-lobe search is closed unless a concrete
artifact bug is found.

## Scope

Allowed A3 work:

- analysis-only validation using existing A2 artifacts;
- deterministic queue-flow and service-capacity comparisons;
- load-normalized backlog, queued-age, completion-fraction, and action/work
  opportunity endpoints;
- explicitly preregistered service/queue-flow synchronization endpoints;
- stronger null checks if they use existing artifacts or a narrowly justified
  deterministic fixture.

Out of scope until this preregistration is revised:

- real LLM calls;
- dashboards;
- Lean, Slack, browser automation, or Atomspace integrations;
- multi-hive coupling;
- new lobe observables derived directly from queue depth, queue delta, or the
  same manipulated action counts;
- broad A2 residual-lobe seed sweeps or simulator mechanisms added to rescue
  the residual-lobe hypothesis.

## Primary Questions

1. Does increasing demand relative to service capacity monotonically increase
   load-normalized backlog and queued-task age under fixed deterministic seeds?
2. Does increasing service capacity reduce load-normalized backlog and improve
   completion fraction at fixed demand?
3. Do queue-flow imbalance measures explain trajectory summaries that previously
   looked like lobe structure?
4. Are any synchronization or desynchronization effects visible between service
   opportunity, completion fraction, and queue-flow balance without using
   queue-derived lobe labels as primary endpoints?

## Proposed Conditions

Reuse existing exogenous-arrival and service-capacity machinery when possible.
If new fixtures are needed, keep them minimal and preregistered before running a
holdout:

- demand axis: endogenous control, low exogenous arrivals, medium exogenous
  arrivals, high exogenous arrivals;
- service axis: low service capacity, baseline service capacity, high service
  capacity;
- policy: baseline attention shares with `quota_balance`;
- `model.task_creation_pressure: 1.0` for exogenous-demand conditions;
- deterministic seeds declared before each run.

Do not add multi-hive coupling in A3. If later work needs multi-hive behavior,
write a separate preregistration with queue-flow/service synchronization as the
primary endpoint before adding coupling mechanics.

## Primary Endpoints

Load and service:

- total created tasks, agent-created tasks, and exogenous arrivals;
- completed tasks, work events, and completion fraction;
- created-completed balance;
- queue depth normalized by total created tasks;
- queue depth normalized by created-completed balance;
- queued-task mean age and max age;
- work-service-capacity setting and realized work-event count.

Action accounting:

- create-task, work-task, message, and idle action counts;
- task-work opportunity versus successful queued-task work;
- value per work event as an efficiency endpoint, not as a lobe endpoint.

Queue-flow structure:

- per-tick created-completed balance;
- per-tick backlog pressure;
- first differences of load-normalized backlog and queued-task age;
- dwell or persistence summaries over queue-flow imbalance states, if the state
  labels are preregistered from load/service fields rather than lobe labels.

Synchronization endpoints:

- correlation or lag agreement between service opportunity and completion
  fraction;
- correlation or lag agreement between created-completed balance and
  load-normalized backlog change;
- cross-condition changes in these measures under fixed seeds.

Baseline and queue-blind lobe summaries may be reported as secondary diagnostics
only. They should not be used as evidence for independent lobe grammar without a
new, non-action-derived observable and a stronger null model.

## Analysis Rules

- Treat raw queue depth as load accounting.
- Interpret queue-derived lobe labels as diagnostics, not primary mechanisms.
- Compare conditions using paired seeds whenever possible.
- Report sign stability or paired bootstrap intervals for primary endpoints
  before expanding seed counts.
- Separate load/accounting findings, action-budget findings, and residual
  unexplained structure in every summary.
- Stop and request urgent strategic review if a result reverses the frozen A2
  interpretation or shows a scientifically novel pattern that changes the
  research direction.

## Decision Rule

Proceed beyond A3 queue-flow/service analysis only if the primary endpoints show
a reproducible pattern that cannot be explained by load, service capacity,
completion fraction, work opportunity, or action mix. Otherwise, treat A3 as a
mechanism-clean accounting stage and use it to specify any later multi-hive
Moltbook coupling around queue-flow/service synchronization rather than lobe
grammar.
