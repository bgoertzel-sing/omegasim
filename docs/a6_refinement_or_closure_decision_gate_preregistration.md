# A6 Refinement-or-Closure Decision Gate Preregistration

Date: 2026-07-01 22:24 PDT.

This document preregisters exactly one narrow A6 decision gate after the
reopened thresholded-appraisal smoke result in
`docs/results/a6_matched_excess_smoke_seed1_2_20260701.md`. It is a design
artifact only. It does not authorize new simulator mechanics, broader seed
sweeps, A5/A7/analytic-map reruns, dashboards, external integrations, real LLM
calls, paid compute, or downstream multi-hive coupling.

## Current Evidence

Ben's 2026-07-01 21:00 PDT direction reopened OmegaSim on the single-hive A6
thresholded-appraisal path, with primary attention on cognitively meaningful
artifact/provenance/risk/prediction-error dynamics rather than raw role
switching.

The completed seed `1,2` matched-excess smoke gate found:

```text
logistic candidate_rate: 1.0
matched_control_condition: linear
matched_control_candidate_rate: 1.0
matched_excess_candidate_rate: 0.0
matched_excess_role_nonperiodic_rate: 0.0
matched_excess_functional_movement_rate: 0.0
matched_excess_bounded_unsaturated_rate: 0.0
matched_excess_artifact_maturity_delta: 0.0
matched_excess_provenance_debt_improvement: 0.0
matched_excess_risk_improvement: 0.0
matched_excess_prediction_error_abs_improvement: 0.009219
matched_excess_functional_score: 0.009219
gate_status: fail_closed_controls_match_or_exceed
```

This is a fail-closed result: the logistic appraisal condition did not exceed
the amplitude-matched linear control on candidate rate or the core functional
component rates. The small prediction-error excess is not sufficient for
promotion.

## Scientific Question

This gate asks only:

```text
Given that the seed 1,2 smoke matched-control gate failed closed, should the
current A6 thresholded-appraisal line close at this boundary, or is exactly one
future A6 refinement scientifically justified before closure?
```

The gate is intentionally a decision synthesis over existing A6 artifacts and
the checked-in A6 design notes. It must not create new result-bearing
simulations or add model mechanisms.

## Allowed Inputs

The decision synthesis may read only:

```text
docs/a6_thresholded_appraisal_reboot_direction_20260701.md
docs/results/a6_matched_excess_smoke_seed1_2_20260701.md
docs/a6_logistic_appraisal_attractor_preregistration.md
docs/a6_1_schema_control_addendum.md
docs/a6_1_pilot_null_preregistration.md
docs/a6_2_residual_recurrence_preregistration.md
docs/a6_2_long_horizon_validation_preregistration.md
AUTOMATION_STATUS.md
README.md
```

It may optionally inspect ignored `/tmp` or `runs/` A6 analysis artifacts if
they already exist locally, but it must not depend on their presence for the
tracked decision.

## Required Output

The next implementation step may add one tracked result note:

```text
docs/results/a6_refinement_or_closure_decision_20260701.md
```

That note must report:

```text
source documents reviewed
matched-excess fail-closed facts
whether each GPT-5.5-Pro recommendation was accepted, deferred, or rejected
closure argument
single-refinement argument, if any
decision status
exactly one next step
```

## Decision Rules

Choose `close_a6_current_model` if any of the following holds:

```text
linear matched control equals or exceeds logistic on candidate rate
linear matched control equals or exceeds logistic on all core functional rates
phase-shuffled or threshold-shuffled controls pass the simple candidate screen
the only logistic excess is small prediction-error movement
available evidence does not identify a specific mechanism change that is both
  scientifically necessary and separately preregisterable
```

Choose `preregister_one_a6_refinement` only if the synthesis identifies a
specific, minimal, testable refinement that directly targets the observed
control equivalence without broad seed tuning. A valid refinement must freeze
all of the following before any run:

```text
one mechanism change or one analyzer endpoint change, not both
same seed discipline or a separately justified tiny seed set
same matched demand/service/action/work accounting locks
appraisal, amplitude-matched linear, phase-shuffled, and threshold-shuffled controls
candidate rule requiring excess over controls, not just within-condition pass
fail-closed closure rule if controls match again
```

If no such refinement can be stated concretely in the decision note, the gate
must close A6 at the current model boundary.

## Non-Goals

Do not use this gate to add:

```text
new simulator mechanics
new action classes
new artifact fields
broad seed sweeps
A5, A7, or analytic-map reruns
three-hive or multi-hive coupling
real external tool integrations
dashboard or browser automation
promotion, attractor, lobe-grammar, or semantic-dynamics claims
```

## Next Implementation Step

Write only `docs/results/a6_refinement_or_closure_decision_20260701.md`, then
update `AUTOMATION_STATUS.md` with the decision and exactly one next step.
