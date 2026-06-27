# A6.1 Schema/Control Addendum

Date: 2026-06-27.

This addendum is a preregistered design gate for the next A6 step. It follows
the completed seed `1..2` A6 analysis gate and artifact-provenance audit. It is
not a result report and does not authorize broader seeds, multi-hive coupling,
real LLM calls, dashboards, Lean, Slack, browser automation, Atomspace
integration, or downstream Moltbook mechanics.

## Motivation

The current A6 smoke scaffold successfully exercises logistic, linear,
phase-shuffled, and threshold-shuffled analyzer paths. It does not promote A6:
logistic-versus-linear artifact utility is tiny, seed signs disagree, queue
depth is higher, and residual rows remain smoke-scale.

The artifact provenance audit adds a sharper blocker. Logistic artifact utility
and readiness changes are dominated by same-tick handoff-success provenance, so
these fields must be treated as action/handoff-coupled until A6.1 separates
artifact changes by source and controls for queue/work accounting.

## A6.1 Scope

A6.1 may only strengthen the single-hive schema and read-only controls needed
to distinguish artifact dynamics from action arithmetic. It may add fields,
events, analyzers, and deterministic tests. It should not add new scientific
claims or a broad seed run until the schema gate passes.

The allowed implementation unit is:

```text
schema additions -> deterministic smoke validation -> read-only analyzer audit
```

No new mechanism should be interpreted until the analyzer can report that the
required provenance and accounting fields are present for every paired condition
and seed.

## Required Source Separation

A6.1 artifact-field updates must be decomposable into these mutually named
sources:

```text
ambient_artifact_drift
handoff_attempt_effect
handoff_success_effect
handoff_failure_effect
prediction_expenditure_effect
prediction_error_effect
queue_work_accounting_effect
noise_effect
```

For each artifact field and tick, the emitted data must be able to reconstruct:

```text
field_delta_total =
  ambient_artifact_drift
  + handoff_attempt_effect
  + handoff_success_effect
  + handoff_failure_effect
  + prediction_expenditure_effect
  + prediction_error_effect
  + queue_work_accounting_effect
  + noise_effect
```

The reconstruction tolerance for deterministic smoke tests should be exact up
to CSV floating-point formatting. If the implementation clips a field to its
bounded interval, the emitted row must also include the unclipped proposed delta
and the clipping residual.

## Required Event/Metric Fields

For A6-enabled runs, `events.csv` or an equivalent run artifact must identify
the event source for each artifact update:

```text
a6_artifact_update_source
a6_artifact_field
a6_artifact_delta_total
a6_artifact_delta_ambient
a6_artifact_delta_handoff_attempt
a6_artifact_delta_handoff_success
a6_artifact_delta_handoff_failure
a6_artifact_delta_prediction_expenditure
a6_artifact_delta_prediction_error
a6_artifact_delta_queue_work_accounting
a6_artifact_delta_noise
a6_artifact_delta_unclipped
a6_artifact_delta_clip_residual
```

For A6-enabled `metrics.csv`, each tick must expose enough accounting to
residualize artifact endpoints without rereading action labels alone:

```text
a6_prediction_budget_available_tick
a6_prediction_budget_spent_tick
a6_prediction_actions_tick
a6_prediction_error_mean_tick
a6_handoff_attempts_tick
a6_handoff_successes_tick
a6_handoff_failures_tick
a6_queue_depth_tick
a6_work_actions_tick
a6_action_opportunity_tick
a6_service_capacity_tick
```

If any required field is missing, the A6.1 analyzer must mark the row
`missing_required_fields` and avoid promotion language.

## Controls

The A6.1 read-only analyzer must report the following before any broader A6
run:

```text
paired seed completeness
required-field completeness
artifact-delta reconstruction residual
per-field source-share table
handoff-success alias share
prediction-expenditure alias share
queue/work accounting residualization status
logistic-minus-linear paired deltas after source accounting
logistic-minus-shuffle paired deltas after source accounting
```

Minimum conservative statuses:

```text
schema_pass
missing_required_fields
reconstruction_failed
high_handoff_alias_risk
high_prediction_alias_risk
high_queue_work_alias_risk
underdetermined_smoke_scale
eligible_for_a6_1_pilot
```

`eligible_for_a6_1_pilot` requires all of the following:

```text
all required fields present
artifact-delta reconstruction passes
handoff-success share does not dominate artifact utility/readiness deltas
prediction expenditure is accounted for as a cost, not a free oracle
queue/work controls are present and residualized
logistic-vs-linear does not degrade backlog-adjusted productivity
```

This status is only eligibility for a small preregistered A6.1 pilot. It is not
evidence for attractors, lobe grammar, synchrony, recurrence, causality, or
nonlinear collective structure.

## Nulls

A6.1 should keep the existing controls and add source-preserving nulls only
after the schema is complete:

```text
amplitude-matched linear
phase-shuffled
threshold-shuffled
source-label shuffled within tick
handoff-success timing broken with matched counts
prediction-expenditure timing broken with matched budget
```

The source-label shuffle tests whether the interpretation depends on names
attached to update sources. The timing-broken nulls test whether handoff or
prediction effects survive when counts and budgets are matched but temporal
alignment is destroyed.

## Promotion Rule

A6.1 cannot promote from smoke/analyzer status unless artifact utility and
readiness retain a residual signal after subtracting handoff-success,
prediction-expenditure, queue/work, and direct action-opportunity accounting.
The residual signal must also beat the amplitude-matched linear control and the
source-preserving nulls on paired seeds.

Until that happens, A6 remains a useful schema and analyzer scaffold only.
