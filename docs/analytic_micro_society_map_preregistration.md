# Analytic Micro-Society Map Preregistration

Date: 2026-07-01.

Status: preregistered next implementation gate only. This document authorizes
one small standalone analytic mechanism screen after the analytic delayed-map
null gate closed conservatively. It does not authorize OmegaSim simulator
mechanics, A5/A6/A7 reruns, dashboards, external integrations, multi-hive
coupling, larger sweeps, or attractor/lobe/semantic-dynamics promotion
language.

## Background

The completed analytic delayed-map null gate emitted the four preregistered
conditions: `active_delayed_nonlinear`, `no_delay`, `linearized_response`, and
`delay_shuffled_history`. The seed-1 active condition was bounded and
unsaturated, but active-vs-null recurrence and local-divergence deltas were
mixed. The finite-time local divergence remained negative. Therefore the gate
closed as `fail_closed_mixed_or_null_equivalent`.

This failure most likely means the first analytic map is too contractive or too
close to its nulls to justify a phase diagram. It lacks explicit artifact
readiness, prediction-error feedback, fatigue, and adaptive threshold state.
Those missing mechanisms are scientifically plausible next additions because
they introduce delayed nonlinear feedback and resource competition without
moving to the full OmegaSim agent simulator.

## Question

Can a minimal standalone analytic micro-society map with artifact readiness,
prediction spend/error, and fatigue/adaptive threshold state produce bounded,
unsaturated, nontrivial dynamics that separate from no-delay, linearized, and
delay-shuffled nulls under matched seed, noise path, initial state, and
dimensionless controls?

This is a mechanism-screening question only. Passing would justify a separately
preregistered small phase-diagram design. It would not establish OmegaHive
semantic dynamics, lobe dynamics, causal collective intelligence, or
strange-attractor behavior.

## Frozen State Variables

The next implementation may define exactly one standalone four-state map:

- `artifact_readiness`: bounded proxy for artifact progress/availability.
- `prediction_spend`: bounded prediction effort charged against work.
- `prediction_error`: bounded delayed mismatch between readiness and forecast.
- `fatigue_threshold`: bounded fatigue/adaptive threshold pressure.

The lifted delayed state must be explicit in the summary diagnostics. No hidden
simulator queues, agents, events, real LLM calls, or multi-hive state may be
introduced.

## Dimensionless Controls

The implementation should retain the current analytic axes:

- `rho`: nonlinear feedback gain.
- `delta`: delay pressure.
- `mu`: memory or threshold persistence.
- `kappa`: internal coupling/leakage among the four state variables.
- `nu`: noise-to-drift scale.

All conditions must share seed, tick count, initial state, perturbation size,
noise path, clipping bounds, and all controls except the intended null
manipulation.

## Frozen Update Sketch

The implementation may use bounded sigmoid or `tanh` response functions only.
The intended causal loop is:

```text
delayed readiness and error -> prediction spend
prediction spend -> work deducted from readiness growth
prediction error -> fatigue/adaptive threshold
fatigue/adaptive threshold -> suppresses spend and readiness update
readiness change -> future prediction error
```

This sketch is directional rather than an exact equation. The code must freeze
the exact equations before any result-bearing smoke is interpreted.

## Required Conditions

The next implementation may emit exactly four conditions:

- `active_delayed_micro_society`: delayed nonlinear four-state map.
- `no_delay`: effective delay set to zero, with other controls locked.
- `linearized_response`: local linear response around the configured initial
  state.
- `delay_shuffled_history`: deterministic seed-derived permutation of the
  active delayed-history sequence.

## Required Diagnostics

Emit one summary row per condition with:

- boundedness status and state range;
- saturation fraction;
- lifted-history range and norm summary;
- prediction spend/work-transfer summary;
- prediction-error range;
- fatigue-threshold range;
- recurrence rate, shuffled-surrogate recurrence rate, and delta;
- finite-time local divergence under matched noise;
- active-vs-null recurrence and divergence deltas;
- a fail-closed condition status.

The active condition is only a candidate for later phase-diagram work if it is
bounded, nontrivially unsaturated, and differs from all three nulls in the same
diagnostic direction. Mixed, negative, contractive, saturated, or
null-equivalent results close the gate conservatively.

## Output Contract

The runner must be standalone and write only:

```text
config.yaml
manifest.yaml
micro_society_summary.csv
summary.md
```

It must not write simulator `metrics.csv` or `events.csv` artifacts, call
`ohdyn.run`, call A5/A6/A7 helpers, broaden seeds, start dashboards, or add
external integrations.

## Verification

The next implementation must include focused deterministic tests proving:

- repeated runs with the same config produce byte-stable summary rows;
- exactly the four preregistered conditions are emitted;
- manifest and summary preserve the diagnostic-only/no-promotion boundary;
- no simulator `metrics.csv` or `events.csv` artifacts are written;
- changing the condition list fails closed.

Acceptable smoke verification for that future implementation:

```bash
.venv-conda/bin/python -m pytest tests/test_run_harness.py -k analytic_micro_society -q
.venv-conda/bin/python -m py_compile ohdyn/analytic_micro_society_map.py tests/test_run_harness.py
git diff --check
```

## Interpretation Boundary

This preregistration is a prospective mathematical sandbox control. It exists
because the first analytic delayed-map null gate was bounded but
null-equivalent/mixed, not because it produced promotion evidence. Any future
positive result remains diagnostic until confirmed by a separately
preregistered phase diagram and stronger nulls.
