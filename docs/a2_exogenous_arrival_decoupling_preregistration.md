# A2 Exogenous-Arrival Decoupling Preregistration

This preregisters the next mechanism-discriminating experiment after the
service-capacity holdout, trajectory controls, decision synthesis, and
queue-blind lobe robustness pass. It is a design document only; this run does
not add simulator mechanics or launch a new grid.

## Motivation

The current A2 evidence supports a conservative interpretation:

- task-creation pressure robustly increases load-normalized backlog;
- service capacity reduces backlog and increases execution-oriented dynamics;
- pressure-induced lobe locking survives an action-only queue-blind relabeling
  pass, but demand is still implemented through the `create_task` action weight.

The unresolved confound is that `model.task_creation_pressure` changes task
arrivals by changing agent action selection. That can also change action mix,
work opportunity, and lobe labels. The next experiment should vary task
arrivals independently from agent `create_task` choice before treating
pressure-induced trajectory locking as evidence for residual lobe dynamics.

## Hypotheses

Primary hypothesis:

- If pressure-induced trajectory locking is mainly load accounting, exogenous
  arrivals should increase load-normalized backlog and queued age, but
  queue-blind action-lobe effects should weaken once `create_task` action
  pressure is held fixed.

Residual-dynamics hypothesis:

- If there is a residual lobe-dynamics signal, exogenous arrivals should still
  reduce transition entropy, lengthen dwell runs, or increase task-generation
  dwell share after controlling for created/completed balance, work events, and
  action mix.

Action-budget hypothesis:

- If the prior pressure result is mostly an action-budget artifact, varying
  exogenous arrivals while holding `create_task` pressure fixed should produce
  weaker queue-blind locking than the existing pressure grid, even when raw
  backlog grows.

## Proposed Mechanics

Add an opt-in config block in a future implementation:

```yaml
exogenous_arrivals:
  enabled: true
  rate_per_tick: 0.0
  task_class_shares:
    near_term_external: 0.45
    long_term_research: 0.25
    internal_improvement: 0.20
    housekeeping: 0.10
```

Design constraints:

- Keep `model.task_creation_pressure: 1.0` in all primary exogenous-arrival
  conditions.
- Keep baseline attention shares and `attention_policy.selection_strategy:
  quota_balance`.
- Generate arrivals at a tick boundary independent of agent action choice.
- Record exogenous task creation with a distinct event type such as
  `exogenous_task_arrived`, while preserving existing `task_created` events for
  agent-created tasks.
- Use deterministic seed-derived random streams so each run remains
  reproducible by seed.
- Preserve A0/A1 artifact contracts: normalized `config.yaml`, manifest,
  `metrics.csv`, `events.csv`, and `summary.md`.
- Do not add real LLM calls, dashboards, Lean, Slack, browser automation,
  Atomspace integrations, or multi-hive coupling.

## Conditions

Use a small preregistered grid before any larger seed extension:

- `endogenous_control`: no exogenous arrivals, `task_creation_pressure: 1.0`.
- `exogenous_low`: low exogenous arrival rate, `task_creation_pressure: 1.0`.
- `exogenous_medium`: medium exogenous arrival rate,
  `task_creation_pressure: 1.0`.
- `exogenous_high`: high exogenous arrival rate, `task_creation_pressure: 1.0`.

The arrival-rate values should be chosen from a short calibration run so that
the medium/high exogenous conditions roughly bracket the created-task totals
seen in the existing `1.8` and `2.2` task-creation-pressure fixtures. The
calibration must be recorded, and the final chosen rates must be fixed before
running the holdout grid.

If the primary grid is ambiguous, a later second-stage design may add a
fixed-action-opportunity variant that records attempted work separately from
successful queued-task work. That should not be added in the first
implementation unless the primary grid cannot distinguish demand-load effects
from action-budget effects.

## Primary Outcomes

Primary load/action accounting:

- exogenous arrivals, agent-created tasks, and total created tasks;
- completed tasks, work events, and completion fraction;
- create-task, work-task, idle, and message action counts;
- created-completed balance;
- queue depth normalized by created tasks;
- queue depth normalized by created-completed balance;
- queued-task mean and max age.

Primary trajectory outcomes:

- baseline lobe transition entropy and normalized transition entropy;
- baseline dwell run count, mean dwell length, max dwell length, and
  backlog-growth dwell share;
- queue-blind transition entropy;
- queue-blind task-generation dwell share;
- queue-blind execution dwell share.

Secondary outcomes:

- value per work event;
- attention capture pressure;
- per-class queued/completed/worked totals.

## Analysis Rules

- Treat raw final queue depth as load accounting, not as an emergent lobe
  dynamics endpoint.
- Compare exogenous-arrival effects against the existing coupled
  `task_creation_pressure` pressure grid only after normalizing by total
  created tasks and created-completed balance.
- Report paired seed-bootstrap sign stability for primary effects before
  extending seed counts.
- Reuse the label-count-preserving null control for baseline lobe trajectories.
- Reuse queue-blind lobe labeling as an analysis-only robustness check, not as a
  replacement lobe architecture.
- Separate robust findings from candidate mechanisms in the summary.

## Decision Rule

Run the implementation only if the code change can preserve deterministic A0/A1
behavior and append-safe artifacts. After the first exogenous-arrival holdout:

- proceed to broader residual-lobe experiments only if queue-blind trajectory
  locking remains sign-stable after load/action accounting and null adjustment;
- treat the result as mostly load accounting if backlog grows but queue-blind
  transition/dwell effects weaken or fail sign-stability;
- treat the result as action-budget coupling if action mix shifts explain most
  of the trajectory response despite fixed `task_creation_pressure`;
- stop and request strategic review if exogenous arrivals reverse the existing
  pressure interpretation or produce a scientifically novel pattern.
