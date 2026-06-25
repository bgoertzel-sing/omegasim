# A4 Multi-Hive Queue-Flow and Service Preregistration

This document preregisters the next OmegaSim stage before any multi-hive
simulator mechanics are added. It is a design artifact only. It does not change
the simulator, add coupling, run new sweeps, reinterpret A2/A3 evidence, or add
new lobe labels.

## Strategic Review Handling

The latest external strategic review at
`../outputs/strategy-reviews/omegasim/latest-review.md` is marked
`strategic_change_level: minor` and `notify_ben: false`.

Accepted recommendation: stop making closure-only A2/A3 commits and, if
OmegaSim remains active, draft a preregistered multi-hive queue-flow/service
study plan before any simulator changes. The review also recommends making the
A4 primary estimands, coupling contrasts, lag handling, null-control semantics,
RNG provenance, and queue-flow conservation identities explicit before any
implementation. This preregistration follows that recommendation.

No recommendation is rejected. A temporal-shift or block-shuffle null for A3
lagged synchronization remains scientifically sensible, but is deferred because
A3 lagged effects are not promoted to mechanism claims.

## Background

A0/A1 infrastructure is complete: deterministic YAML-loaded runs, 15 static
OmegaHive-like agents, one task queue, one NetworkX bus graph, metrics/events
output, `summary.md`, reproducibility tests, role/action metrics, lobe labels,
and lobe-transition/dwell summaries are already covered.

A2/A3 single-hive evidence is frozen as a load/accounting and service-capacity
result. Current artifacts support queue inflow/outflow, completion fraction,
load-normalized backlog, queued-task age, service capacity, and work-event
opportunity as primary explanatory variables. They do not support an
independent residual lobe-grammar claim under the current simulator and label
scheme.

## Boundary

Do not implement multi-hive coupling until this preregistration has been
reviewed and converted into a concrete implementation plan.

Out of scope for this preregistration:

- real LLM calls;
- dashboards;
- Lean, Slack, browser automation, or Atomspace integrations;
- live task boards or external services;
- new queue/action-derived lobe labels;
- broad A2/A3 residual-lobe sweeps;
- simulator changes made only to rescue the lobe-grammar hypothesis.

## Primary Question

When multiple deterministic hives are coupled through a shared queue-flow layer,
do service/load phase relations show reproducible coordination or
desynchronization effects that are not explained by each hive's own inflow,
outflow, completion fraction, load-normalized backlog, queued age, work-event
opportunity, or action mix?

## Proposed Minimal Model

Start from the existing A0/A1 single-hive harness and add the smallest
multi-hive extension needed to test queue-flow/service relations:

- fixed number of hives, initially two or three;
- each hive has its own agents, queue, bus graph, seed stream, metrics, and
  summary;
- one explicit shared layer can transfer or route tasks between hive queues;
- coupling is deterministic and controlled entirely by YAML config;
- all coupling decisions are recorded as events;
- per-hive and cross-hive metrics are emitted in stable CSV schemas.

The first implementation should remain abstract and numeric. It should not call
real LLMs or external systems.

## Conditions

Use paired seeds across all conditions.

Primary coupling axis:

- no coupling control;
- direct deterministic coupling;
- delayed coupling control;
- shuffled coupling control.

Primary contrasts, fixed before any holdout:

- direct minus no-coupling;
- delayed minus no-coupling;
- shuffled minus no-coupling;
- direct minus shuffled as the coupling-structure contrast when transfer
  volumes and timing marginals are comparable.

Primary demand/service axis:

- fixed exogenous-load controls for each hive;
- low, baseline, and high service capacity where needed;
- no changes to task-creation pressure unless explicitly preregistered.

Initial hive count:

- prefer two hives for the first implementation smoke and holdout;
- add a third hive only after the two-hive artifact contract is stable.

## Primary Endpoints

The primary estimands are the paired-seed condition effects on the fields below.
No best-lag endpoint is primary; lagged analyses must report fixed lag `0` and
the preregistered causal lag(s) implied by the configured coupling delay.

Per hive:

- total inflow, outflow, created tasks, completed tasks, and exogenous arrivals;
- completion fraction;
- load-normalized backlog;
- queued-task mean and max age;
- work-event opportunity and realized work events;
- action mix and role/action totals.

Cross-hive:

- task-transfer counts and direction;
- service/load phase relation at preregistered lags;
- cross-hive load-normalized backlog correlation;
- cross-hive completion-fraction correlation;
- cross-hive queued-age divergence;
- coupling effect versus no-coupling, delayed-coupling, and shuffled-coupling
  controls.

Secondary diagnostics:

- existing baseline lobe labels and queue-blind action labels may be emitted
  per hive for continuity;
- lobe diagnostics must not be used as mechanism evidence unless a new
  non-queue, non-action-derived observable and stronger null model are
  preregistered first.

## Coupling-Control Semantics

The first implementation must keep coupling controls interpretable as
queue-flow/service controls rather than as accidental load changes.

- `none`: no transfer attempts are completed and transfer probability must be
  `0.0`.
- `direct`: eligible transfer decisions arrive in the target hive on the same
  tick, after the source-hive local event that emitted the task and before the
  next tick's local scheduling.
- `delayed`: eligible transfer decisions preserve source hive, target hive,
  task payload, and task provenance, but arrive exactly `delay_ticks` after the
  decision tick. The configured `delay_ticks` is the preregistered causal lag to
  report alongside lag `0`.
- `shuffled`: eligible transfer decisions preserve the same deterministic
  transfer-opportunity schedule as the paired direct run when feasible, but
  shuffle target assignment or delivery order using the coupling RNG stream.
  The first implementation must document which marginals are preserved. At
  minimum it must preserve seed, coupling mode, tick count, transfer probability,
  source-hive opportunity counts, and total transfer-attempt counts for a
  paired seed.

If transfer-volume matching is not implemented for a control, the artifact and
summary must name that limitation, and any affected result must be treated as a
load-volume contrast rather than a phase-structure contrast.

## Queue-Flow Conservation

The multi-hive artifact contract must include deterministic conservation fields
and tests so accounting identities are separated from scientific endpoints.

Per hive, each tick must reconcile:

```text
queue_delta =
  local_agent_created
  + exogenous_arrivals
  + inbound_transfers
  - completed_tasks
  - outbound_transfers
  - explicit_drops
```

`explicit_drops` is zero unless a future preregistration adds a drop mechanism.
Aggregate multi-hive queue balance must also reconcile total local creation,
exogenous arrivals, completions, and transfer conservation. Same-tick
queue-balance correlations are artifact diagnostics only; they are not
scientific synchronization endpoints.

## Decision Rules

Promote a cross-hive coordination claim only if all of the following hold:

- the endpoint was preregistered before the run;
- paired-seed effects have stable sign support;
- confidence intervals exclude zero for the primary comparison;
- the effect survives delayed or shuffled coupling controls;
- the effect is not explained by per-hive inflow, outflow, completion fraction,
  load-normalized backlog, queued age, work-event opportunity, or action mix.

Otherwise, interpret the result as queue-flow/service accounting or an
exploratory diagnostic.

## First Implementation Gate

Before writing simulator code, freeze the concrete implementation contract below.
The first code change should implement only this contract and its smoke tests.

### YAML Shape

Use an opt-in `hives` section. Absence of `hives` keeps the existing single-hive
A0/A1 behavior unchanged.

```yaml
run:
  experiment_id: a4_two_hive_smoke
  ticks: 100

model:
  agent_count: 15
  actions:
    - idle
    - message
    - create_task
    - work_task

hives:
  - hive_id: hive_a
    seed_offset: 0
    exogenous_arrival_rate: 1.0
    work_service_capacity: 1.0
  - hive_id: hive_b
    seed_offset: 1000
    exogenous_arrival_rate: 1.0
    work_service_capacity: 1.0

coupling:
  mode: none
  transfer_probability: 0.0
  delay_ticks: 0
  shuffle_seed_offset: 2000
```

Allowed initial `coupling.mode` values are `none`, `direct`, `delayed`, and
`shuffled`. `delayed` requires `delay_ticks > 0`; `none` requires
`transfer_probability: 0.0`; `direct` and `shuffled` require
`transfer_probability >= 0.0`. The first implementation should reject duplicate
`hive_id` values, blank IDs, negative rates, negative service capacity, and
unknown coupling modes before writing artifacts.

### Artifact Contract

For a multi-hive run, write the existing top-level artifacts plus per-hive and
cross-hive companions. All files remain append-safe: if any enabled output file
already exists, fail before writing partial artifacts.

- `config.yaml`: normalized complete config, including `hives` and `coupling`.
- `manifest.yaml`: existing manifest fields plus `hive_count`, `hive_ids`, and
  `coupling_mode`.
- `metrics.csv`: top-level aggregate tick metrics, preserving existing A0/A1
  field names where meaningful.
- `events.csv`: top-level event stream, including all coupling events.
- `summary.md`: aggregate run summary with one short per-hive section and one
  coupling section.
- `hive_metrics.csv`: one row per `tick,hive_id` with per-hive queue-flow,
  service, age, action, role/action, lobe diagnostic, and attention fields.
- `hive_events.csv`: one event row per hive-local agent/task event with
  `hive_id` and deterministic `task_id` provenance.
- `coupling_events.csv`: one row per attempted or completed transfer with
  `tick`, `source_hive_id`, `target_hive_id`, `task_id`,
  `coupling_mode`, `delay_ticks`, `transfer_decision`, and `arrival_tick`.
- `cross_hive_metrics.csv`: one row per tick with transfer counts, per-hive
  load-normalized backlog values, queued-age divergence, completion-fraction
  relation fields, and preregistered lagged service/load phase fields.

Keep existing single-hive artifact schemas byte-compatible for configs without
`hives`.

### Seed Streams

Derive deterministic random streams from the CLI seed without sharing mutable
RNG state across hives:

- hive stream seed: `cli_seed + hive.seed_offset`, with unique offsets required
  across hives;
- coupling stream seed: `cli_seed + coupling.shuffle_seed_offset`, with the
  coupling offset distinct from all hive offsets;
- delayed-transfer ordering: stable sort by `arrival_tick`, then
  `source_hive_id`, `target_hive_id`, `task_id`;
- task IDs: include `hive_id`, tick, agent ID or `exogenous`, and a per-hive
  monotonic counter.

The same config, seed, and output flags must produce byte-identical artifacts
across output directories. Changing only output directory paths must not enter
any artifact content.

Paired-seed comparisons should reuse the same per-hive streams across coupling
modes and reserve the coupling stream only for transfer decisions or shuffled
controls. A change in coupling mode must not silently reseed hive-local task
creation, exogenous-arrival, or work-selection streams.

### Smoke-Test Expectations

The first multi-hive implementation must add tests proving:

- configs without `hives` still pass the current A0/A1 reproducibility tests;
- a two-hive `mode: none` config writes all multi-hive artifacts and creates no
  completed transfers;
- same-seed two-hive runs are byte-identical across output directories;
- different seeds change at least one stochastic artifact;
- `direct`, `delayed`, and `shuffled` smoke fixtures produce deterministic
  coupling event schemas;
- invalid duplicate hive IDs and invalid coupling settings fail before partial
  output files are created.
- per-hive and aggregate conservation identities reconcile on every tick for
  `none`, `direct`, `delayed`, and `shuffled` smoke fixtures.

### Holdout Boundary

Do not run a scientific A4 holdout until the two-hive smoke contract is stable.
The preregistered first holdout should use paired seeds `100..129`, two hives,
fixed exogenous load per hive, and the four coupling modes
`none/direct/delayed/shuffled`. Primary comparisons are direct-minus-none,
delayed-minus-none, and shuffled-minus-none for cross-hive service/load phase
relations, load-normalized backlog correlation, completion-fraction
correlation, queued-age divergence, and transfer volume. Interpret lobe fields
as secondary diagnostics only.

Before writing simulator code, confirm:

- no new external-system integrations are needed;
- no A2/A3 residual-lobe experiment is being reopened;
- the implementation can preserve single-hive artifact compatibility.

Only after that gate is written should the repository add multi-hive mechanics.

## Gate Review Record

Automation review date: 2026-06-25.

Review basis:

- `AUTOMATION_STATUS.md` is the source of truth and says A0/A1 is complete,
  A2/A3 are frozen, and the only next step is to review this A4 implementation
  gate before simulator mechanics are added.
- The latest external strategic review is `strategic_change_level: minor` and
  `notify_ben: false`. It recommends stopping closure-only A2/A3 commits and
  drafting a preregistered multi-hive queue-flow/service study plan before any
  simulator change.
- The existing A0/A1 tests cover deterministic YAML loading, artifact emission,
  role/action metrics, lobe labels, lobe-transition summaries, and same-seed
  reproducibility for the single-hive baseline.

Gate acceptance:

- Scientific objective is narrow enough for a first A4 code increment: test
  queue-flow/service phase relations under preregistered coupling controls,
  without treating lobe diagnostics as mechanism evidence.
- Implementation surface is opt-in: configs without `hives` must preserve the
  existing single-hive config model, simulator behavior, artifact schemas, and
  byte-reproducibility.
- Coupling modes, seed streams, task-ID provenance, artifact names, append-safe
  output behavior, and invalid-config checks are specified before code changes.
- The first holdout boundary is blocked until the two-hive smoke contract is
  implemented and passing.

Pre-code blockers:

- A human/research review should confirm that the YAML and artifact schemas
  above are the desired first A4 interface. The automation should not silently
  broaden the scope into three-hive mechanics, dashboards, external
  integrations, or new lobe architectures.
- The first code change must be a smoke-contract implementation only. It should
  add no scientific holdout runs and no A2/A3 reruns.

Permitted first implementation slice after this gate is approved:

- config dataclasses and validation for opt-in `hives` and `coupling`;
- a two-hive `mode: none` smoke fixture plus direct/delayed/shuffled minimal
  fixtures;
- per-hive/cross-hive artifact writers with append-safe failure behavior;
- reproducibility and invalid-config tests listed in the smoke expectations.

Everything else remains out of scope until those tests pass.
