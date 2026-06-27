# A6.2 Longer-Horizon Validation Preregistration

Date: 2026-06-27.

This document preregisters the narrow longer-horizon validation that may follow
the completed A6.2 residual-recurrence analyzer gate. It is a design gate only.
It does not run simulations, add simulator mechanisms, broaden into downstream
multi-hive coupling, or promote A6.

## Prior Result

The seed `1..2` A6.2 gate consumed the existing A6.1 source-preserving null
comparison artifacts and found:

```text
required field status: complete=12
residual recurrence rows: 156, all insufficient_horizon
paired delta rows: 130, all insufficient_horizon
```

That result validated the read-only analyzer contract and the fail-closed
status path. It did not test recurrence scientifically because the 16-tick
smoke horizon is too short.

## Scientific Question

The longer-horizon validation asks only whether the existing single-hive A6
logistic condition produces source-accounted residual recurrence that survives
the same linear and source-preserving null controls when the horizon is long
enough for the preregistered analyzer to compute recurrence metrics.

The validation cannot claim attractors, lobe grammar, synchrony, semantic
field dynamics, causal support, or multi-hive coordination. A positive result
only permits a later preregistered mechanism pilot.

## Frozen Scope

Keep the existing A6 mechanics fixed:

```text
no new actions
no new artifact fields
no new latent variables
no changed utility equations
no changed source-accounting event schema
no real LLM, Lean, Slack, browser, dashboard, or Atomspace integration
no multi-hive coupling
```

The longer-horizon run must derive mechanically from the existing A6 smoke
fixture family:

```text
configs/a6_logistic_appraisal_smoke.yaml
configs/a6_linear_appraisal_smoke.yaml
configs/a6_phase_shuffled_smoke.yaml
configs/a6_threshold_shuffled_smoke.yaml
```

Only the run horizon and experiment IDs may change for the validation configs.
All model and `logistic_appraisal` parameters must remain identical to the
source smoke fixtures unless a future preregistration explicitly freezes a
different parameter value before any run.

## Fixed Validation Design

Use paired deterministic seeds:

```text
seeds: 1, 2
horizon: 96 ticks
```

The 96-tick horizon is the first validation horizon because it is above the
current analyzer's 24-row minimum while remaining bounded enough for a small
implementation run. Do not add seeds or a second horizon in the same run. If
96 ticks is still underdetermined after source/control residualization, close
or redesign before any broadening.

Required conditions:

```text
logistic
linear
phase_shuffled
threshold_shuffled
source_label_shuffled_within_tick
handoff_success_timing_broken_matched_counts
```

The source-preserving null conditions must preserve paired seed, horizon,
action opportunity, handoff-attempt counts, and source-accounting schema. They
must break the preregistered source/timing relationship being tested rather
than changing total opportunity.

Do not add `prediction_expenditure_timing_broken_matched_budget` unless a
fresh source-accounting preflight on the validation artifacts shows nonzero
prediction-expenditure contribution for the target residual endpoint.

## Required Implementation Artifacts

The next implementation run may add only these artifacts:

```text
configs/a6_2_long_horizon_*.yaml
runs/a6_2_long_horizon_compare_seed1_2/
runs/a6_2_long_horizon_residual_recurrence_seed1_2/
docs/results/a6_2_long_horizon_validation_seed1_2.md
```

The comparison directory must contain normal deterministic run artifacts for
each condition/seed. The analysis directory must be produced by the existing
read-only A6.2 analyzer unless a minimal analyzer bug fix is required.

## Required Report Fields

The tracked report must publish:

```text
exact command bundle
config filenames and changed keys
run artifact count
condition/seed completeness
required field completeness
residualization status counts
recurrence status counts
paired delta status counts
logistic-minus-linear deltas by target variable and seed
logistic-minus-source-preserving-null deltas by target variable and seed
backlog-adjusted productivity deltas
dominant artifact-update source shares
decision status
```

## Decision Rules

Close the validation as schema/analyzer-only if any required field is missing,
paired seeds are incomplete, source-accounting event fields are absent, or the
analyzer emits `insufficient_horizon`.

Close A6.2 conservatively if logistic recurrence metrics do not beat the
linear control and both source-preserving nulls on the same target variable,
if signs disagree across seeds, if handoff-success or queue/work source shares
dominate the target endpoint, or if backlog-adjusted productivity is worse
than linear.

Mark A6.2 eligible for a later mechanism pilot only if all of the following
hold for the same target variable:

```text
source schema passes
artifact source accounting passes
residualization computes without missing fields
logistic beats linear on residual recurrence
logistic beats both source-preserving nulls on residual recurrence
paired seed signs agree
dominant source share is not handoff-success or queue/work accounting
backlog-adjusted productivity is not worse than linear
```

Eligibility is not promotion. It only authorizes a future preregistered
mechanism pilot or a more explicit closure decision.

## Next Implementation Step

Create the fixed 96-tick validation configs and the smallest comparison helper
needed to regenerate the six required paired conditions without changing
simulator mechanics. Then run only seeds `1` and `2`, run the existing A6.2
read-only analyzer, publish the tracked validation report, update
`AUTOMATION_STATUS.md`, and stop.
