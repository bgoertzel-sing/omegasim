# A4 Delayed-Coupling Follow-Up Null Preregistration

This document preregisters the next A4 analysis step after the two-hive
seed `100..129` holdout. It is a design artifact only. It does not add
simulator mechanics, change configs, run new seed sweeps, introduce three-hive
coupling, add lobe labels, or reinterpret the A4 holdout as evidence for an
independent lobe grammar.

## Strategic Review Handling

The latest external strategic review at
`../outputs/strategy-reviews/omegasim/latest-review.md` is marked
`strategic_change_level: minor` and `notify_ben: false`.

Accepted recommendation: keep the A4 path bounded, interpret the existing
two-hive holdout through preregistered queue-flow/service endpoints, and avoid
new mechanics unless a follow-up null design first shows that the delayed
coupling signal is not explained by transfer volume, delivery timing, service
opportunity, queued age, or action mix.

No recommendation is rejected. No Ben notification is required and no strategic
pivot is made.

## Background

The first two-hive A4 holdout on seeds `100..129` found robust transfer-volume
accounting for full-transfer coupling. It also found bootstrap-supported
delayed-minus-none effects on selected cross-hive synchronization endpoints,
including load-backlog correlation at lag `0` and completion-fraction
correlation at lags `0` and `2`.

The same delayed condition changed work-event totals and queued-task age. Those
fields are preregistered explanatory variables, so the current result remains a
queue-flow/service record with delayed-coupling synchronization diagnostics,
not an independent phase-control or lobe-grammar claim.

The two-hive shuffled condition is not a meaningful target-randomization null:
with two hives, each source hive has only one legal non-source target. It is a
schema, conservation, and source-opportunity check only.

## Primary Question

Do the delayed-minus-none synchronization endpoints survive analysis-only nulls
that preserve the existing two-hive holdout's transfer volume, source
opportunity, and delivery-timing marginals while disrupting temporal alignment
between the two hive trajectories?

## Immediate Follow-Up Choice

Use an analysis-only temporal/block-shuffle null over the existing two-hive
artifacts before implementing any three-hive mechanics.

This is the immediate follow-up because it directly addresses the current
scientific uncertainty with the smallest reproducibility risk. The existing
artifacts already contain per-tick hive trajectories and coupling events, so an
analysis-only null can test whether the delayed synchronization endpoints are
stronger than expected under matched transfer timing and local trajectory
structure. A future three-hive target-null design remains scientifically
sensible, but it should be deferred until this read-only null indicates that
temporal alignment survives conservative controls.

## Null Design

The analyzer should consume the existing holdout root:

```bash
runs/a4_two_hive_holdout_seed100_129
```

and should write a new ignored run-analysis directory plus a committed summary
under `docs/results/`.

For each paired seed and coupling mode, construct deterministic null replicates
from the emitted `hive_metrics.csv`, `cross_hive_metrics.csv`, and
`coupling_events.csv` without rewriting run artifacts.

The primary null should be a circular block shift:

- preserve each hive's within-hive time series exactly;
- preserve each mode's tick count, transfer count, source opportunity count,
  and delivery-timing distribution;
- shift one hive's time series relative to the other by deterministic offsets
  that exclude `0` and the configured causal delay;
- use fixed block sizes chosen before execution, initially `5`, `10`, and `20`
  ticks;
- compute the same lag `0` and lag `2` endpoints as the holdout analyzer after
  the shift;
- use deterministic ordering, no random runtime state, and a manifest of all
  offsets or blocks used.

A secondary null may be added in the same analyzer only if it remains
analysis-only: block-permutation within each seed/mode that preserves
within-block order, the number of blocks, and each hive's marginal trajectory
values. It must be reported separately from the circular-shift null.

## Primary Endpoints

Use the same A4 delayed-coupling endpoints already reported by the read-only
holdout analyzer:

- load-normalized backlog correlation at lag `0`;
- load-normalized backlog correlation at lag `2`;
- completion-fraction correlation at lag `0`;
- completion-fraction correlation at lag `2`;
- queued-age divergence final;
- completion-fraction divergence final.

Primary comparisons remain:

- delayed minus none;
- direct minus none as a non-delayed full-transfer contrast;
- shuffled minus none only as a two-hive schema/source-opportunity control;
- direct minus shuffled only as a contract check, not a phase null.

## Decision Rules

Treat the delayed synchronization endpoint as still explained by
queue-flow/service accounting if any of the following holds:

- its observed delayed-minus-none effect falls inside the central null interval
  for the temporal/block-shuffle controls;
- null-centered observed-minus-null effects have unstable sign support across
  paired seeds;
- the effect disappears after accounting for work-event totals, queued-task
  age, completion fraction, transfer count, or action mix;
- the effect appears equally in direct or shuffled controls under the same null.

Promote only to a new preregistered mechanics design, not to a mechanism claim,
if delayed-minus-none effects remain outside the null interval with stable
paired-seed signs and are not explained by the accounting fields above.

## Three-Hive Deferral Rule

Do not implement three-hive target-null mechanics in the immediate next step.

Draft a three-hive target-null preregistration only if the analysis-only null
leaves a delayed synchronization residual that is stable enough to justify new
mechanics. That later design must specify target-shuffle semantics, transfer
volume matching, source-opportunity matching, delivery-timing matching, seed
streams, conservation tests, and paired-seed uncertainty before any simulator
code is changed.

## Verification Requirements

The follow-up analyzer, when implemented, must be read-only with respect to the
original holdout run directories and must have focused tests for:

- deterministic null replicate construction;
- append-safe output behavior;
- fixed endpoint schema;
- exclusion of zero and causal-delay shifts from the primary null;
- byte-reproducible outputs for the same inputs.

No real LLM calls, dashboards, Lean, Slack, browser automation, Atomspace
integrations, live task boards, new lobe architectures, or broad A2/A3 sweeps
are in scope.
