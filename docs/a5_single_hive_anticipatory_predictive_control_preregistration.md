# A5 Single-Hive Anticipatory Predictive-Control Preregistration

## Purpose

This document reopens A5 as the next explicitly requested scientific stage:
single-hive anticipatory predictive-control dynamics. It supersedes the prior
closed/no-op automation posture for this bounded stage only. The A2/A3/A4 and
A5.1a lessons remain binding: apparent structure must survive controls for
load, service capacity, action opportunity, task arrivals, work budget,
prediction spend, and null predictors before any dynamics claim is promoted.

The stage is deterministic, single-hive, and abstract/numeric. It must not add
real LLM calls, dashboards, Lean, Slack, browser automation, Atomspace
integrations, live task boards, or three-hive mechanics. Three-hive delayed
anticipatory coupling is downstream and requires a separate preregistration
with target and phase nulls plus resource-bounded cross-hive prediction costs.

## Hypothesis

Inter-agent or inter-role prediction is itself a scarce managed resource. Zero
prediction leaves the hive reactive. Perfect or oracle-like prediction may
smooth away the residual dynamics of interest. Intermediate prediction budgets
may create forecast errors that are structured enough to guide high-level
allocation while still leaving nontrivial collective residuals.

The primary question is whether intermediate prediction budgets produce richer
but still partially predictable residual collective dynamics than zero-budget
reactivity or oracle prediction. Structured strange-attractor-like patterns, if
they appear, are useful only if they provide simpler high-level regularities
that agents can predict cheaply under limited prediction budget.

## Setup

Use one existing OmegaSim hive with the current agent population, action set,
queue, four attention classes, and output artifact contract. A deterministic
hidden demand-share process shifts future task pressure over:

- `near_term_external`
- `long_term_research`
- `internal_improvement`
- `housekeeping`

Controllers may shift attention allocation or service priority using forecasts
of future task pressure. All conditions must match task-arrival totals, the
class-demand stream, service capacity, action opportunity, and work budget.
Prediction spend must be reported explicitly; when prediction is charged to
work, the pre-charge work opportunity, charged prediction work units, and
remaining work budget must be available for accounting.

## Determinism and Accounting Locks

All conditions must be derived from the same base configuration and paired
seeds. Predictor condition is the only intended contrast. The simulator must
not change task-arrival totals, class-demand totals, service-capacity knobs,
action set, agent count, action-opportunity schedule, or total work budget
between conditions. Any prediction charge must be represented as an explicit
budget transfer from available work opportunity rather than as hidden extra
capacity.

The comparison must include budget-matched timing-broken nulls for every
intermediate predictor being interpreted. A positive intermediate-budget claim
is invalid if it can be reproduced by a shuffled, phase-randomized, or
spend-only replay null that preserves prediction spend while breaking useful
forecast timing.

## Conditions

Compare paired-seed, matched-stream conditions:

1. Reactive baseline: no forecast and no prediction spend.
2. Low-budget predictor: linear or short-memory forecast.
3. Medium-budget nonlinear predictor: deterministic nonlinear forecast with
   bounded memory.
4. High-budget nonlinear predictor: larger deterministic nonlinear forecast or
   longer memory.
5. Oracle predictor: future demand known as a smoothing positive control, not
   a target dynamics condition.
6. Shuffled or phase-randomized predictor nulls: budget-matched timing-broken
   controls preserving spend and marginal forecast structure while breaking
   useful timing.

The prediction-budget axis is therefore none/reactive, low, medium, high, and
oracle. Intermediate-budget positives must beat both reactive and their
budget-matched nulls before they can be interpreted as useful anticipation.
Oracle is a smoothing positive control and a ceiling for forecast availability,
not the target dynamics condition.

## Primary Endpoints

Primary endpoints are:

- forecast skill per unit prediction budget;
- lead-lag relation between attention/service allocation and future demand;
- residual phase structure after load, service, task-arrival, action
  opportunity, work-budget, and prediction-spend controls;
- recurrence or return-map structure in delay embeddings of residual
  predictive-state variables;
- predictability or compressibility of emergent high-level collective states;
- guardrails for backlog, queued age, completion fraction, class starvation,
  prediction-spend volatility, and work-budget volatility.

Throughput and queue improvement are guardrails, not evidence of structured
dynamics by themselves.

## Decision Rules

A5 fails closed unless the same intermediate-budget condition:

- improves forecast skill per unit budget over reactive and timing-broken
  nulls;
- allocates attention or service ahead of future demand rather than merely
  tracking current backlog;
- retains nonzero, structured forecast errors;
- shows residual recurrence or high-level predictability after full accounting;
- remains more dynamically nontrivial than oracle smoothing;
- satisfies backlog, queued-age, completion, starvation, and volatility
  guardrails.

Any strange-attractor-like, lobe-like, or phase-structure claim is secondary.
It is unsupported unless the preregistered accounting controls and surrogate
nulls pass first.

## Initial Scaffold

The initial smoke/pilot may use the existing deterministic A5 scaffold:

```bash
python -m ohdyn.run --config configs/a5_predictive_linear_smoke.yaml --seed 5 --out runs/a5_predictive_linear_seed5
python -m ohdyn.compare_predictive_control --seeds 5 6 --out runs/a5_predictive_control_compare
python -m ohdyn.analyze_a5_residual_accounting --compare-dir runs/a5_predictive_control_compare --out runs/a5_residual_accounting
```

No broader seed sweep, new simulator mechanics, dashboard, integration, or
multi-hive coupling is authorized by this preregistration.

As of the 2026-06-29 A5 automation request, this document is the active
single-hive preregistration for the bounded predictive-control stage. The
checked-in scaffold above is sufficient for the authorized smoke/pilot: any
additional predictor family, longer horizon, wider seed grid, or delayed
multi-hive coupling requires a separate preregistered scientific axis.
