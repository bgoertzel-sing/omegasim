# A5 Single-Hive Preregistration Audit, 2026-07-01 05:24 PDT

## Scope

This bounded audit checks the current A5 single-hive anticipatory
predictive-control request against the already checked-in preregistration and
smoke scaffold. It does not add simulator mechanics, predictor families,
broader seed sweeps, dashboards, external integrations, A7-family mechanics,
A5.2 implementation, or downstream three-hive coupling.

The active preregistration is
`docs/a5_single_hive_anticipatory_predictive_control_preregistration.md`.
It already defines the requested deterministic single-hive setup: reactive
baseline, low-budget linear or short-memory prediction, medium-budget
deterministic nonlinear prediction, high-budget nonlinear prediction, oracle
prediction, and shuffled or phase-randomized budget-matched nulls.

## Audit Result

The preregistered design surface remains present and bounded:

- prediction is treated as a scarce managed resource, including inter-agent or
  inter-role prediction;
- the prediction-budget axis separates none/reactive, low, medium, high, and
  oracle roles;
- task-arrival totals, demand streams, service capacity, action opportunity,
  pre-prediction work opportunity, prediction spend, and work budget are
  accounting-locked before residual interpretation;
- budget-matched timing-broken nulls are required for intermediate predictor
  interpretation;
- forecast skill per prediction budget, lead-lag allocation, residual phase or
  recurrence, high-level predictability/compressibility, and guardrails remain
  primary endpoints;
- strange-attractor-like, lobe-like, and phase-structure claims remain
  secondary and fail-closed unless they survive the preregistered accounting
  controls and surrogate nulls;
- three-hive delayed anticipatory coupling remains downstream and requires a
  separate preregistration with target/phase nulls and resource-bounded
  cross-hive prediction costs.

The checked-in comparison manifest emitted by `ohdyn.compare_predictive_control`
is the current audit artifact for this surface. It records the
resource-bounded prediction axis, endpoint evidence map, fail-closed decision
checklist, cheap-high-level-regularities contract, comparison-readiness
contract, downstream-extension boundary, and surrogate-null requirements.

## Decision

No broader implementation is authorized by this audit. The smallest existing
deterministic smoke/pilot scaffold is sufficient for the current A5
verification pass. Existing A5 seed `5,6` evidence remains fail-closed for
residual-structure promotion: intermediate predictors improve forecast skill,
but no intermediate predictor has passed all residual/null,
oracle-nontriviality, compression, and guardrail promotion criteria.

