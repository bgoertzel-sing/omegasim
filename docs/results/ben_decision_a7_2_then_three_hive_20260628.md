# Ben Decision: A7.2 Then Three-Hive Ring

Date: 2026-06-28.

## Decision

Ben instructed OmegaSim to proceed first with an A7.2-style mechanism: delayed
artifact-mediated endogenous prediction in a single hive. After that, whether
the A7.2 result is positive or negative, OmegaSim should proceed to the
three-hive ring experiment family without waiting for another human decision.

This decision resolves the prior A5-exit governance pause. The current
source-of-truth action is no longer to ask Ben whether to open A7.2; it is to
open A7.2 as a bounded preregistered gate.

## Active A7.2 Task

Freeze the A7.2 mechanism before running it:

- agents choose among `predict`, `work`, `review`, and `synthesize`;
- prediction consumes scarce work opportunity;
- action utilities use lagged logistic dependence on forecast error, artifact
  readiness, contradiction/risk, fatigue, and adaptive thresholds;
- forecast and artifact effects are delayed or lagged, never same-tick leakage;
- endpoints, nulls, closure rules, slopes, thresholds, delays, costs, and caps
  are fixed before the first A7.2 smoke run.

The first implementation should be small and deterministic. It should test
whether an intermediate endogenous-prediction condition produces residual
structure beyond accounting controls and matched nulls, not merely whether
forecast skill or throughput changes.

## Downstream Three-Hive Task

After A7.2 closes, draft a separate three-hive ring preregistration and then
run the bounded experiment family. That downstream preregistration should use:

- cross-hive prediction costs;
- delayed artifact transfer;
- target and phase nulls;
- transfer-opportunity controls;
- no-coupling, linear, same-tick logistic, delayed logistic, heterogeneous
  delay, prediction-cost-feedback, and adaptive-threshold variants.

## Still Out Of Scope

Do not broaden A5-family seeds, tune A7.2 after seeing residual plots, start
the three-hive ring before its own preregistration, add dashboards or external
integrations, or make lobe-like, strange-attractor-like, semantic-dynamics, or
causal collective-structure claims without passing the preregistered residual
and null standards.
