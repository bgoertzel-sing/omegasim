# A6.2 Residual-Recurrence Preregistration

Date: 2026-06-27.

This document preregisters the smallest acceptable A6.2 reopening after the
A6/A6.1 conservative closure. It is a design gate only. It does not authorize
new simulator mechanisms, broad seed sweeps, downstream multi-hive coupling,
dashboards, real LLM calls, Lean, Slack, browser automation, Atomspace
integration, or promotion language.

## Prior Boundary

The completed A6 analysis gate showed that the analyzer can emit paired
control deltas, residual preflights, residual timeseries, residual contrast
rollups, artifact-provenance rows, and source-accounting rows. It did not
promote A6: logistic-minus-linear artifact utility was tiny, seed signs
disagreed, mean queue depth was higher, mean completion fraction was lower,
and residual rows were labeled `underdetermined_smoke_scale`.

The completed A6.1 source-accounting audit showed that fresh artifacts expose
required source fields and reconstruct artifact deltas. It still retained
large handoff-success alias shares in readiness and utility rows.

The completed A6.1 pilot/null gate then showed conservative closure: all eight
pilot-null rows were labeled `null_removes_endpoint_advantage`, and the
source-preserving nulls matched or exceeded the logistic readiness/utility
endpoints on paired seeds `1` and `2`.

Therefore A6.2 must not be a continuation-by-seed-broadening of A6.1. It may
only ask whether source-accounted residual trajectories contain recurrence
structure under stricter preflights and null controls.

## Scientific Question

A6.2 asks:

```text
After removing clock trend, queue/load variables, action opportunity, work
budget, service capacity, direct handoff/action arithmetic, and source-labeled
artifact-update accounting, do source-accounted latent/artifact residuals show
nontrivial recurrence structure in the logistic condition that is not present
in amplitude-matched linear or source-preserving null controls?
```

This question is about eligibility for a later mechanism study only. A6.2
cannot claim attractors, lobe grammar, synchrony, causal support, or nonlinear
collective structure from smoke artifacts.

## Fixed Inputs

The first A6.2 implementation must derive from the existing single-hive A6
fixtures:

```text
configs/a6_logistic_appraisal_smoke.yaml
configs/a6_linear_appraisal_smoke.yaml
configs/a6_phase_shuffled_smoke.yaml
configs/a6_threshold_shuffled_smoke.yaml
```

The initial implementation must remain paired and deterministic. Use only
seeds `1` and `2` until the A6.2 analyzer contract passes. If the smoke horizon
is too short for recurrence interpretation, the result must be labeled
`insufficient_horizon` rather than rescued by broadening seeds in the same run.

## Required Conditions

A6.2 must include these existing conditions:

```text
logistic
linear
phase_shuffled
threshold_shuffled
source_label_shuffled_within_tick
handoff_success_timing_broken_matched_counts
```

Do not add `prediction_expenditure_timing_broken_matched_budget` unless a fresh
source-accounting preflight shows nonzero prediction-expenditure share for the
target latent/artifact residual endpoints. In the current A6.1 audit,
prediction share is zero for readiness and utility, so that null is deferred.

## Target Variables

The primary recurrence variables are source-accounted residual versions of:

```text
a6_latent_activation_mean_tick
a6_latent_focus_mean_tick
a6_latent_fatigue_mean_tick
a6_latent_prediction_error_mean_tick
a6_artifact_novelty_tick
a6_artifact_coherence_tick
a6_artifact_actionability_tick
a6_artifact_provenance_debt_tick
a6_artifact_risk_tick
a6_artifact_contradiction_tick
a6_artifact_readiness_tick
a6_artifact_implementation_maturity_tick
a6_artifact_communication_maturity_tick
```

Artifact variables must be residualized after source accounting. Readiness and
utility-like composites are not primary variables unless the analyzer reports
that handoff-success, queue/work, and source-preserving null alias risks do not
dominate them.

## Required Controls

For every condition and seed, residualization must account for:

```text
tick index / clock trend
queue depth
tasks created
tasks completed
service capacity
action opportunity
work actions
prediction actions
prediction budget spent
handoff attempts
handoff successes
handoff failures
artifact-update source shares
```

If any required field is absent, the analyzer must emit
`missing_required_fields` and stop before recurrence interpretation. If fields
are present but paired seeds, conditions, or null artifacts are incomplete, the
status must be `paired_seed_incomplete`.

## Required Recurrence Outputs

The first A6.2 analyzer/report must publish:

```text
paired seed completeness
required control/source-field completeness
residualization status per target variable
residual variance by condition, seed, and variable
lag-1 autocorrelation by condition, seed, and variable
delay-embedded recurrence rate by condition, seed, and variable
return-interval coefficient of variation by condition, seed, and variable
linear autoregressive forecast error by condition, seed, and variable
simple nonlinear forecast error by condition, seed, and variable
logistic-minus-linear paired deltas
logistic-minus-source-preserving-null paired deltas
smoke eligibility status
```

The initial delay embedding may use fixed small smoke-safe parameters, but they
must be reported in the output. If there are too few usable timepoints after
lagging or residualization, the row status must be `insufficient_horizon`.

## Decision Rules

A6.2 remains schema/analyzer-only if any required source field is missing,
artifact-delta reconstruction fails, paired seeds are incomplete, or recurrence
rows are `insufficient_horizon` or `underdetermined_smoke_scale`.

A6.2 is a conservative closure if logistic recurrence metrics do not beat the
linear control and both source-preserving nulls on the same target variable, if
the effect sign disagrees across paired seeds, or if backlog-adjusted
productivity degrades versus linear.

A6.2 is eligible for a later preregistered mechanism pilot only if all of the
following hold on paired seeds:

```text
source schema passes
artifact-delta reconstruction passes
residualization status passes
logistic beats linear on the same residual recurrence endpoint
logistic beats both source-preserving nulls on the same endpoint
effect sign is consistent across paired seeds
handoff-success and queue/work alias risks are not dominant for that endpoint
backlog-adjusted productivity is not worse than linear
row status is neither insufficient_horizon nor underdetermined_smoke_scale
```

Eligibility is not promotion. It only permits a future preregistered mechanism
pilot or a carefully justified longer-horizon design.

## Non-Goals

Do not add these in the first A6.2 implementation:

```text
new cognitive mechanisms
new action classes
new artifact fields
new broad seed ranges
three-hive or multi-hive coupling
semantic-field A7 mechanics
real external tool integrations
dashboard or browser automation
attractor or lobe-grammar claims
```

## Next Implementation Step

Implement the smallest read-only A6.2 analyzer path that consumes an existing
A6.1 source-preserving null comparison directory, emits the required
residual-recurrence CSV/status rows, adds focused deterministic tests for
missing fields and insufficient horizon handling, and publishes a tracked
seed `1..2` A6.2 gate report. Do not change simulator mechanics or broaden
seeds in that implementation step.
