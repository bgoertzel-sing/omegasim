# Ben Decision Note: A5 Complete And Fail-Closed

Date: 2026-06-29.

## Status

The explicit A5 single-hive anticipatory predictive-control request is already
implemented at the bounded preregistration/scaffold level. The concise
preregistration is
`docs/a5_single_hive_anticipatory_predictive_control_preregistration.md`.
It defines the deterministic single-hive setup, resource-bounded prediction
hypothesis, matched accounting controls, reactive/intermediate/oracle/null
condition set, primary residual endpoints, and fail-closed interpretation
rules.

The existing smoke scaffold remains the only authorized A5 implementation
surface: `configs/a5_predictive_linear_smoke.yaml`,
`ohdyn.compare_predictive_control`, and
`ohdyn.analyze_a5_residual_accounting`.

## Evidence Boundary

The seed `5,6` smoke verifies deterministic execution and forecast-skill
separation across the preregistered predictor axis. Intermediate predictors can
improve forecast skill over reactive and timing-broken null conditions.

That is not enough for a dynamics claim. The read-only residual-accounting
analyzer remains fail-closed: no intermediate-budget condition passes the full
promotion rule requiring forecast skill, accounting-controlled residual/null
structure, nontriviality relative to oracle smoothing, compression or
predictability of high-level states, and guardrail compliance.

A5 therefore supports harness competence and a useful negative result only. It
does not support lobe-like, strange-attractor-like, residual phase-structure,
semantic-dynamics, or causal collective-structure claims.

## Decision Needed

Ben should choose whether OmegaSim should stay closed awaiting a fresh
preregistration, or whether the next scientific stage should be a new
one-hive dimensionless delayed-dynamics sweep that directly exposes
coupling gain, delay/relaxation ratio, memory persistence, prediction-cost
ratio, and threshold-adaptation ratio.

## Non-Goals

Do not broaden A5 with new predictor knobs, broader seeds, parameter sweeps,
new simulator mechanics, committed result-bearing run artifacts, dashboards,
integrations, extra hives, or promotion language without a fresh
preregistration.
