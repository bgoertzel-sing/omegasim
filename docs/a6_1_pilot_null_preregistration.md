# A6.1 Pilot/Null Preregistration

Date: 2026-06-27.

This document preregisters the smallest A6.1 pilot/null design after the
completed A6 analysis gate and A6.1 source-accounting audit. It is a design
artifact only. It does not authorize broad seed sweeps, downstream multi-hive
coupling, dashboards, real LLM calls, Lean, Slack, browser automation,
Atomspace integration, or promotion language.

## Current Evidence

The A6 seed `1..2` analysis gate established that the read-only analyzer can
emit paired control deltas, residual preflights, residual timeseries,
contrast rollups, artifact-provenance rows, and source-accounting rows.

The source-accounting audit over fresh source-schema artifacts established
that A6.1 artifact-update source fields are present and reconstruct total
artifact deltas. It did not promote A6: residual rows are still smoke-scale,
and artifact readiness/utility retain handoff-success alias risk.

## Scientific Question

The A6.1 pilot asks a narrower question than the full A6 attractor program:

```text
Do logistic appraisal artifact-readiness and artifact-utility differences
retain any residual signal after source-preserving nulls and backlog-adjusted
productivity controls, or are they explainable as handoff/action arithmetic?
```

This pilot is not allowed to claim attractors, lobe grammar, synchrony,
causality, or nonlinear collective structure. A positive result only makes a
future preregistered A6.2 residual-recurrence pilot eligible.

## Fixed Inputs

The first implementation pass must derive from the existing single-hive A6
smoke fixtures:

```text
configs/a6_logistic_appraisal_smoke.yaml
configs/a6_linear_appraisal_smoke.yaml
configs/a6_phase_shuffled_smoke.yaml
configs/a6_threshold_shuffled_smoke.yaml
```

Use only paired deterministic seeds `1` and `2` until the null implementation
and analyzer contract pass. The pilot may regenerate source-field-complete
artifacts from those fixtures, but it must not broaden seeds in the same step.

The initial implementation unit is:

```text
source-preserving null configs or transforms
  -> deterministic smoke comparison
  -> read-only analyzer rows
  -> tracked pilot gate report
```

## Required Conditions

The pilot must include the existing four A6 conditions:

```text
logistic
linear
phase_shuffled
threshold_shuffled
```

It must add only the smallest source-preserving nulls needed to test the
current blocker:

```text
source_label_shuffled_within_tick
handoff_success_timing_broken_matched_counts
```

The source-label shuffle preserves tick-level artifact update magnitudes and
the set of source labels but breaks the interpretation attached to source
names. The handoff-success timing-broken null preserves handoff-success counts
and artifact update budgets while breaking temporal alignment with the
artifact-field trajectory.

Prediction-expenditure timing-broken nulls are deferred unless prediction
expenditure has nonzero material share in the source-accounting audit for
artifact readiness or artifact utility. In the current audit, prediction share
is zero for those logistic rows, so adding that null now would expand the pilot
without testing the observed blocker.

## Required Analyzer Outputs

The A6.1 pilot analyzer/report must publish:

```text
paired seed completeness
required source-field completeness
artifact-delta reconstruction residuals
per-field source-share table
handoff-success alias share for readiness and utility
source-label-shuffled deltas
handoff-success-timing-broken deltas
backlog-adjusted productivity deltas
logistic-minus-linear paired endpoint deltas
logistic-minus-null paired endpoint deltas
residual status labels
```

Backlog-adjusted productivity is preregistered as:

```text
tasks_completed_total / max(1, queue_depth + tasks_created_total)
```

The analyzer may also report alternative diagnostics, but this field is the
gating productivity control for the pilot.

## Decision Rules

The pilot remains schema/analyzer-only if any required source field is missing,
artifact-delta reconstruction fails, paired seeds are incomplete, or residual
rows remain underdetermined.

The pilot is a conservative closure if logistic readiness/utility advantages
are removed by either source-preserving null, handoff-success share remains
dominant, or backlog-adjusted productivity degrades versus linear.

The pilot is eligible for a later A6.2 residual-recurrence preregistration only
if all of the following hold on paired seeds:

```text
source schema passes
artifact-delta reconstruction passes
logistic beats linear on artifact readiness or utility
logistic beats both source-preserving nulls on the same endpoint
handoff-success share is not dominant for that endpoint
backlog-adjusted productivity is not worse than linear
residual rows are not labeled underdetermined_smoke_scale
```

Eligibility is not promotion. It only permits writing the next preregistered
pilot for residual recurrence over source-accounted fields.

## Non-Goals

Do not add these in the first A6.1 pilot implementation:

```text
new cognitive mechanisms
new action classes
new artifact fields
new seed ranges
three-hive or multi-hive coupling
semantic-field A7 mechanics
real external tool integrations
dashboard or browser automation
attractor or lobe-grammar claims
```

## Next Implementation Step

Implement the smallest read-only source-preserving null path for
`source_label_shuffled_within_tick` and
`handoff_success_timing_broken_matched_counts`, add focused deterministic
tests, run only paired seeds `1` and `2`, and publish
`docs/results/a6_1_pilot_null_gate_seed1_2.md`.
