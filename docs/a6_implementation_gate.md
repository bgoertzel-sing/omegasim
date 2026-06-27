# A6 Implementation Gate

This gate freezes the minimum A6 smoke-scaffold contract before any broad
simulation sweep. It is intentionally narrower than the full A6/A7/A8 roadmap:
single hive only, no external integrations, no dashboards, no real LLM calls,
no Lean/Slack/browser/Atomspace coupling, and no downstream semantic-field or
three-hive mechanics.

## Scope

The first A6 implementation may add a deterministic opt-in config section named
`logistic_appraisal`. When absent, A0/A1, A2, A4, and A5 artifacts must remain
byte-reproducible for fixed seeds and output paths.

The first A6 smoke scaffold should preserve the existing baseline population
size of 15 agents, the single task queue, the NetworkX bus graph, YAML config
loading, seeded randomness, `config.yaml`, `manifest.yaml`, `metrics.csv`,
`events.csv`, and `summary.md`.

## Frozen State Vector

Each agent should carry these bounded latent appraisal fields:

```text
activation
focus
fatigue
novelty_appetite
risk_sensitivity
handoff_threshold
prediction_error
```

Each field should be numeric, deterministic, and clamped to a fixed interval.
The initial smoke interval should be `[0.0, 1.0]` for all fields except
`prediction_error`, which may use `[-1.0, 1.0]`.

The shared artifact state should contain:

```text
artifact_novelty
artifact_coherence
artifact_actionability
artifact_provenance_debt
artifact_risk
artifact_contradiction
artifact_readiness
artifact_implementation_maturity
artifact_communication_maturity
```

These fields must not be aliases for queue depth, queue delta, or action counts.
Queue and action variables may influence them only through explicit update
terms reported in the design or code.

## Frozen Action Utility Equations

A6 action selection should use a softmax over utilities. The initial action set
should be the baseline actions plus only these A6 actions:

```text
synthesize
review
formalize
maintain
predict
communicate
pause
```

For action `a` and agent `i`, the smoke utility form is:

```text
U_i^a(t) =
  base_i^a
  + appraisal_gain_i^a * sigmoid(slope_i^a * (signal_i^a(t - delay_i^a) - threshold_i^a))
  + role_bias_i^a
  - fatigue_cost_i^a(t)
  - risk_cost_i^a(t)
  - prediction_cost_i^a(t)
```

The smoke scaffold should include paired amplitude-matched linear controls using
the same signals, delays, seeds, and action budgets. The nonlinear condition is
not promotable unless its residual latent-state structure beats these linear
controls and the preregistered shuffle/null controls.

## Artifact Handoff Rules

The first functional nonlinear loop should be thresholded artifact handoff:

```text
explore/create_task -> synthesize -> review -> formalize/work_task -> communicate/maintain
```

Minimal handoff gates:

```text
synthesize when artifact_novelty exceeds handoff_threshold and fatigue is below overload
review when artifact_readiness exceeds handoff_threshold
formalize when artifact_coherence and actionability exceed threshold and provenance debt is bounded
communicate when communication maturity exceeds threshold and risk is bounded
maintain when provenance debt, contradiction, risk, or fatigue exceeds threshold
```

Failed or delayed handoffs should update fatigue, contradiction, provenance
debt, and prediction error. These updates must be deterministic for a given
seed.

## Seed And Noise Streams

Use separate deterministic streams derived from the run seed:

```text
baseline_action_stream
appraisal_noise_stream
artifact_update_stream
prediction_noise_stream
control_shuffle_stream
```

Paired conditions must share baseline action opportunity, task inflow,
appraisal noise, and artifact-update noise unless the condition explicitly
defines a shuffle/null perturbation.

## Smoke Configs

Create only short smoke fixtures at first:

```text
configs/a6_logistic_appraisal_smoke.yaml
configs/a6_linear_appraisal_smoke.yaml
configs/a6_threshold_shuffled_smoke.yaml
configs/a6_phase_shuffled_smoke.yaml
```

The first fixtures should use short tick counts suitable for deterministic
tests. They are not evidence for a scientific claim.

## Output Schema Additions

For A6-enabled runs, `metrics.csv` should add:

```text
a6_condition
a6_appraisal_gain
a6_sigmoid_slope
a6_prediction_budget
a6_prediction_budget_spent_tick
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
a6_handoff_attempts_tick
a6_handoff_successes_tick
a6_handoff_failures_tick
```

For A6-enabled runs, `events.csv` should add event types for:

```text
a6_appraisal_update
a6_artifact_update
a6_handoff_attempted
a6_handoff_succeeded
a6_handoff_failed
a6_prediction_spent
a6_threshold_adapted
```

Baseline event schemas should remain stable for non-A6 configs.

## Deterministic Tests

Before any A6 sweep, add focused tests that verify:

```text
non-A6 configs preserve existing A0/A1 artifact schemas
A6 config loading rejects unknown fields and invalid probabilities
A6 smoke runs are deterministic for fixed seed and config
linear and logistic smoke conditions share paired noise streams
A6 metrics/events contain the frozen schema fields
A6 summary reports handoff totals and latent/artifact endpoint values
threshold-shuffled and phase-shuffled controls preserve matched action opportunity
```

## Read-Only Analyzer Skeleton

The first analyzer should consume existing A6 comparison artifacts and write
only derived CSV/Markdown outputs. It should not rerun simulations.

Minimum controls:

```text
load, service, action opportunity, work budget, clock trend, and queue residualization
amplitude-matched linear control
phase-shuffled control
threshold-shuffled control
paired-seed uncertainty
promotion and closure rule evaluation
```

Promotion beyond A6 smoke requires residual latent/artifact recurrence that
survives these controls while preserving bounded backlog-adjusted productivity
and non-degraded artifact utility.

## Next Step

Implement only the config dataclasses, smoke fixtures, schema constants, and
deterministic tests needed for this gate. Do not run a broad simulation sweep.
