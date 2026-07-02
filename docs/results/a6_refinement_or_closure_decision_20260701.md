# A6 Refinement-or-Closure Decision

Date: 2026-07-01.

Status: read-only decision synthesis for the reopened A6 thresholded-appraisal
single-hive path. This note follows
`docs/a6_refinement_or_closure_decision_gate_preregistration.md`. It does not
add simulator mechanics, run broader sweeps, rerun A5/A7/analytic-map work,
add dashboards or integrations, use real LLM calls, add paid compute, add
multi-hive coupling, or support promotion language.

## Source Documents Reviewed

Allowed preregistered inputs reviewed:

```text
README.md
AUTOMATION_STATUS.md
docs/a6_thresholded_appraisal_reboot_direction_20260701.md
docs/a6_refinement_or_closure_decision_gate_preregistration.md
docs/results/a6_matched_excess_smoke_seed1_2_20260701.md
docs/a6_logistic_appraisal_attractor_preregistration.md
docs/a6_1_schema_control_addendum.md
docs/a6_1_pilot_null_preregistration.md
docs/a6_2_residual_recurrence_preregistration.md
docs/a6_2_long_horizon_validation_preregistration.md
```

Local guard/status context was also checked. The guard reported
`repo_write_allowed=true`, `state=open`, and recommended writing only this
decision note.

## Matched-Excess Facts

The reopened A6 smoke result in
`docs/results/a6_matched_excess_smoke_seed1_2_20260701.md` found:

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

The linear control matched the logistic condition on candidate rate and all
core functional component rates. Phase-shuffled and threshold-shuffled
controls also passed the simple candidate screen. The only positive matched
excess was a small prediction-error improvement, which the preregistered gate
explicitly treats as insufficient for promotion.

Prior A6/A6.1/A6.2 records reinforce this interpretation. Source accounting
showed artifact endpoints were vulnerable to handoff/action arithmetic, the
A6.1 source-preserving nulls removed endpoint advantages, and the A6.2
96-tick residual-recurrence validation did not beat the linear and
source-preserving null controls on the same target with paired seed agreement.

## GPT-5.5-Pro Recommendations

Accepted:

- Use appraisal, amplitude-matched linear, phase-shuffled, and
  threshold-shuffled controls as the primary contrast surface.
- Treat artifact maturity, provenance debt, risk, prediction error, prediction
  spend, fatigue, thresholds, and hysteresis as the scientifically relevant A6
  variables rather than raw role switching.
- Require matched excess over controls before any promotion language.
- Fail closed when linear or shuffled controls pass at similar rates.

Deferred:

- A budget-matched prediction replay null remains deferred for this exact
  decision because the current gate is read-only and the completed matched
  excess result already fails closed against the linear and shuffled controls.
  Adding another null would be new implementation work outside this gate.

Rejected:

- None. The external review's earlier guard-recovery and initial A6 gate
  implementation advice has already been completed, so this run follows the
  newer source-of-truth status rather than duplicating it.

## Closure Argument

The preregistered decision rules select `close_a6_current_model` if the linear
matched control equals or exceeds logistic on candidate rate, if it equals or
exceeds logistic on all core functional rates, if shuffled controls pass the
simple candidate screen, or if the only logistic excess is small
prediction-error movement.

All four closure triggers apply here:

```text
linear matched control candidate_rate == logistic candidate_rate
linear matched control core functional rates == logistic core functional rates
phase_shuffled and threshold_shuffled pass the simple candidate screen
only nonzero logistic excess is small prediction-error movement
```

This makes the current A6 thresholded-appraisal model useful as an accounting
and control scaffold but not as evidence for accounting-robust nonlinear
collective dynamics. Closing the current model also avoids the failure mode of
rescuing a control-equivalent result by broadening seeds or adding mechanisms
after seeing the outcome.

## Single-Refinement Argument

No single future A6 refinement is scientifically justified from this evidence
within the current gate.

A valid refinement would need to identify exactly one mechanism change or one
analyzer endpoint change that directly targets the observed linear/shuffled
control equivalence before any run. The available evidence does not isolate
such a change. The prior A6 trail already tried source-accounting, nulls, and a
longer horizon; those checks closed because the relevant endpoints remained
control-equivalent, under source/null pressure, or tied to handoff accounting.

Parameter tuning, seed broadening, another horizon extension, or adding more
A6 mechanisms would therefore be post hoc rescue work rather than a narrow
preregisterable refinement.

## Decision Status

```text
decision_status: close_a6_current_model
interpretation: fail_closed_controls_match_or_exceed
promotion_allowed: false
preregister_one_a6_refinement: false
```

Do not promote A6, broaden A6 seeds, add new A6 mechanics, rerun A5/A7 or
analytic-map gates, add dashboards or external integrations, or move to
downstream multi-hive coupling from this result.

## Exactly One Next Step

Await Ben's next scientific direction or explicit preregistration request
before adding further OmegaSim mechanics or runs.
