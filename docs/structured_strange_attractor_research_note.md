# Structured Strange-Attractor Research Note

This note records a forward-looking hypothesis for OmegaSim. It should inform
future experiment design when the current A4 queue-flow/service review gate and
any approved A4 holdouts are complete, or if Ben explicitly asks for a pivot
toward attractor-oriented simulations. It is not approval to interrupt the
current A4 sequence, add broad simulator mechanics, or reopen A2/A3 lobe-grammar
searches.

## Core Intuition

The envisioned structured strange-attractor scenario is unlikely to arise from
more task pressure alone. The A2/A3 evidence already suggests that raw pressure
mostly produces queueing, load, service-capacity, and work-opportunity dynamics.

The more plausible setup is a near-critical, delayed, multi-hive
attention-allocation system:

- several hives with partially different specialties;
- each hive operating near, but not far beyond, service capacity;
- tasks transferred among hives with explicit delays;
- attention allocated among urgent external work, long-term research,
  housekeeping, and internal self-improvement;
- adaptive reallocation based on lagged signals such as backlog age, recent
  failures, novelty, overload, and value;
- hysteresis or memory, so the system does not immediately revert when pressure
  relaxes.

This combination has the ingredients needed for structured but non-periodic
macro-dynamics:

- nonlinear priority and overload thresholds;
- delayed task and status signals that can induce overcorrection;
- bounded attention or service capacity forcing real tradeoffs;
- heterogeneous time scales across task classes;
- coupled subsystems where one hive's delay or cleanup changes another hive's
  load;
- trajectory memory, so current behavior depends on recent history rather than
  current queue state alone.

## Candidate Future Scenario

A future attractor-oriented stage could simulate three or more hives with task
classes such as:

- high-priority external work;
- long-term research;
- internal self-improvement;
- housekeeping and artifact hygiene.

The system should allow endogenous creation of internal-improvement or
housekeeping tasks when stress, novelty, error accumulation, stale backlog, or
coordination failures cross thresholds. Those tasks should compete for bounded
attention rather than being treated as free repairs.

A representative qualitative cycle to look for:

```text
urgent external surge
  -> research starvation
  -> error or stale-backlog accumulation
  -> housekeeping / self-improvement burst
  -> temporary capacity recovery
  -> research burst
  -> new overload or coordination imbalance
```

The target is not a simple periodic loop. The target is a reproducible basin of
structured recurrence in which macro-states recur with variable timing,
amplitude, and order because delayed coupling and bounded attention keep
perturbing the trajectory.

## Suggested Observables

Future runs should define attractor-oriented observables before implementation.
Candidates:

- per-class attention share versus target share;
- per-class queued age, oldest task age, and stale-task count;
- backlog and completion fraction per hive and task class;
- delayed transfer inflow/outflow per hive;
- internal-improvement and housekeeping burst timing;
- recovery time after overload events;
- phase relations among hives at preregistered lags;
- recurrence of coarse macro-states under paired seeds;
- sensitivity to small initial-condition or delay perturbations;
- divergence/reconvergence of trajectories after matched shocks;
- recurrence plots or coarse state-transition motifs over load, attention, and
  task-class composition.

Any lobe-like or attractor-like claim should remain secondary unless these
observables are separated from direct queue-depth/action-count definitions and
validated against appropriate null controls.

## Experimental Discipline

Before attempting this richer scenario, the agent should preserve the discipline
learned from A2/A3/A4:

- preregister primary estimands and null controls;
- separate accounting identities from scientific endpoints;
- use paired seeds and deterministic provenance;
- keep smoke/preflight artifacts analyzable before holdouts;
- avoid interpreting load effects as emergent structure;
- avoid new lobe labels unless they are not derived directly from manipulated
  queue or action fields.

The likely next scientific path, after A4 is handled, is not simply "higher
pressure." It is a carefully bounded extension from multi-hive queue-flow
coupling toward adaptive, delayed, quota-governed attention allocation with
memory.
