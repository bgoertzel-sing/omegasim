# A5 Anticipatory Predictive-Control Preregistration

## Purpose

This preregisters the next OmegaSim stage after the A4 two-hive closure. A4
remains frozen as queue-flow, service, action-opportunity, and accounting
evidence, not as independent lobe grammar or strange-attractor evidence.

Ben explicitly requested a new attractor-oriented direction on 2026-06-26:
test whether agents that allocate bounded resources to predicting future needs
can generate structured collective dynamics. This document reopens OmegaSim for
that bounded A5 design.

## Core Hypothesis

Perfect prediction may smooth collective dynamics, while zero prediction leaves
agents purely reactive. The interesting regime may be intermediate prediction
budget: agents predict enough to find high-level recurring patterns, but not
enough to eliminate forecast error. Those errors can create new collective
dynamics, which then become something the agents must predict.

Structured strange-attractor-like patterns, if they appear, may be useful as a
resource-saving compromise: the group develops simpler high-level regularities
that are cheaply predictable even when detailed inter-agent prediction is too
expensive.

## First Experiment Family

Start with one hive before adding multi-hive coupling. The single-hive scaffold
should preserve the existing deterministic OmegaSim artifact discipline and
avoid real LLM calls, dashboards, browsers, Lean, Slack, Atomspace integrations,
or live task boards.

The hive receives a deterministic hidden demand process that changes future task
pressure across the existing attention classes:

- `near_term_external`
- `long_term_research`
- `internal_improvement`
- `housekeeping`

Controllers may adjust attention shares or service priority using forecasts of
future task pressure, while total task-arrival volume, service capacity, action
opportunity, and work budget remain matched across conditions.

## Conditions

Use paired seeds and matched demand streams across:

1. Reactive baseline: no forecast, existing quota-style response.
2. Low-budget predictor: short-memory or linear predictor.
3. Medium-budget nonlinear predictor: small deterministic nonlinear model.
4. High-budget nonlinear predictor: larger deterministic nonlinear model or
   longer memory, still bounded.
5. Oracle predictor: future demand known, positive control for coordination.
6. Budget-matched shuffled or phase-randomized predictors: nulls preserving
   each predictor's budget and marginal forecast structure while breaking
   useful timing.

The key experimental axis is prediction budget, measured by the model class,
memory window, fitted parameters, update frequency, or an explicit normalized
budget score.

## Primary Endpoints

Fail closed unless the result survives the following accounting controls and
surrogate nulls:

- forecast skill per unit prediction budget;
- whether attention allocation leads future demand rather than merely tracking
  current backlog;
- residual phase structure after controlling for load, service capacity, action
  opportunity, task volume, and work budget;
- recurrence or return-map structure in delay embeddings of residual predictive
  state variables;
- predictability or compressibility of emergent high-level collective states;
- guardrails for backlog, queued age, completion fraction, class starvation, and
  volatility.

Cross-condition claims should treat CE-like throughput or queue improvement as
guardrails, not as sufficient evidence for structured dynamics.

## Decision Rules

Promote A5 beyond a smoke/pilot only if an intermediate-budget predictor shows
more residual structure than reactive and shuffled controls while remaining more
nontrivial than the oracle condition. A plausible positive pattern is:

- low or medium prediction budget improves forecast skill over null;
- forecast errors remain nonzero and structured;
- residual collective states show recurrent but non-periodic geometry;
- the recurrent structure is more compressible/predictable at a high level than
  detailed task-level trajectories;
- accounting controls do not explain the effect.

If all apparent structure is explained by backlog, service capacity, work
opportunity, or demand volume, close A5 as another accounting result.

For promotion from the single-hive pilot, guardrails use explicit zero
tolerance relative to the reactive baseline under matched seeds: final backlog
must not increase, final queued age must not increase, completion fraction must
not decrease, and no attention class may show a new starvation pattern.
Starvation is operationalized as a final-state attention class with queued work
remaining and zero completed tasks. This is intentionally strict because the
first A5 question is whether resource-bounded prediction adds residual
structure without buying it through worse queueing or work allocation. Any
later numeric tolerance for a larger holdout must be preregistered before that
holdout runs.

## Downstream Multi-Hive Stage

Three-hive delayed anticipatory coupling is downstream, not the first
implementation step. It should only proceed after the single-hive evidence is
interpretable. A future multi-hive preregistration should include meaningful
target and phase nulls, delayed transfer timing, cross-hive prediction budgets,
and controls for transfer volume and source opportunity.
