# A5.1 Prediction-Spend Competition Preregistration

## Purpose

This preregisters the next bounded A5 follow-up after the closed single-hive
predictive-control result. The prior A5 scaffold showed that deterministic
bounded predictors can improve forecast skill under matched demand streams, but
the seed `7..16` evidence did not support residual structured dynamics after
load, service, action-opportunity, task-volume, and work-budget accounting.

A5.1 asks a narrower question that the first A5 scaffold did not test directly:
what happens when prediction expenditure itself competes with work opportunity?
This is a new preregistered design gate, not a seed broadening of the closed
A5 result and not an import of A6/A7 mechanics.

## Hypothesis

Inter-agent or inter-role prediction is a scarce managed resource. Zero
prediction leaves agents reactive; oracle-like prediction may smooth away the
collective residuals that would otherwise be scientifically interesting.
Intermediate prediction spend may create forecast errors that are structured
enough to guide high-level allocation while still leaving nontrivial residual
collective dynamics.

The primary hypothesis is therefore not "more prediction is better." It is
that low or medium prediction spend may yield better forecast skill per unit
budget, stronger lead-lag allocation to future demand, and richer but still
partly predictable residual collective states than either zero-spend reactivity
or high-spend/oracle smoothing.

## Scope

A5.1 remains deterministic and single-hive:

- one existing OmegaSim hive, queue, action set, attention classes, and artifact
  contract;
- no real LLM calls, dashboards, Lean, Slack, browser automation, Atomspace
  integrations, live task boards, or broad three-hive mechanics;
- no multi-hive transfer, target coupling, or phase coupling;
- paired seeds and matched deterministic demand streams across all conditions.

Three-hive delayed anticipatory coupling remains downstream. It requires a
separate preregistration with target and phase nulls, matched transfer
opportunity, and resource-bounded cross-hive prediction costs.

## Experimental Setup

The task-arrival stream must be fixed by seed and condition-independent config.
Every condition must receive matched task-arrival totals, class-demand stream,
service capacity, action opportunity, and total per-tick decision budget before
prediction spend is charged.

Prediction spend is deducted from an explicit work-opportunity budget. A
condition may use prediction to alter attention allocation or service priority,
but it must report the cost paid and the remaining work budget each tick.
Prediction cannot silently add service capacity or task completions.

The first implementation after this preregistration should add only the
smallest deterministic scaffold needed for one smoke/pilot:

- per-condition prediction-spend budget;
- per-tick prediction cost charged before work-task service;
- forecast-share, forecast-error, and forecast-skill fields already aligned
  with the A5 artifact style;
- work-budget-remaining and prediction-spend fields sufficient for accounting;
- generated paired condition configs derived from the existing A5 smoke fixture.

## Conditions

Use paired seeds and matched demand streams across:

1. Reactive baseline: no prediction spend and quota-style response.
2. Low-budget predictor: short-memory or linear forecast with low spend.
3. Medium-budget nonlinear predictor: deterministic nonlinear forecast with
   bounded memory and medium spend.
4. High-budget nonlinear predictor: deterministic nonlinear forecast with
   larger memory or update cost and higher spend.
5. Oracle predictor: future demand known, charged as a high-cost smoothing
   positive control rather than a target dynamics condition.
6. Budget-matched timing-broken nulls: shuffled or phase-randomized predictors
   preserving each predictor's spend and marginal forecast structure while
   breaking useful timing.

The linear, medium nonlinear, high nonlinear, and oracle conditions must each
have a spend-matched null or explicitly fail closed for unsupported controls.

## Primary Endpoints

Primary endpoints are:

- forecast skill per unit prediction spend;
- lead-lag relation between attention or service allocation and future demand;
- residual phase structure after accounting for load, service capacity, action
  opportunity, task volume, prediction spend, and remaining work budget;
- recurrence or return-map structure in delay embeddings of residual predictive
  state variables;
- predictability or compressibility of emergent high-level collective states;
- guardrails for final backlog, queued age, completion fraction, class
  starvation, prediction-spend volatility, and work-budget volatility.

Throughput, completion fraction, and queue improvement are guardrails. They are
not sufficient evidence for structured collective dynamics.

## Accounting Controls And Nulls

Every analysis must include accounting levels that isolate:

- clock and deterministic demand phase;
- task-arrival totals and class-demand shares;
- service capacity and action opportunity;
- work completed, work budget remaining, and prediction spend;
- backlog, queued age, and class starvation;
- budget-matched timing-broken predictor nulls.

The study fails closed if a predictor's apparent residual structure is explained
by these controls or is matched by its spend-matched timing-broken null.

## Promotion And Closure Rules

A5.1 may be promoted beyond smoke only if the same intermediate-spend condition:

- improves forecast skill per unit spend over reactive and spend-matched nulls;
- shows allocation that leads future demand rather than tracking current backlog
  only;
- retains nonzero, structured forecast errors;
- shows residual recurrence or high-level predictability after full accounting;
- beats high-budget/oracle smoothing on nontrivial residual structure;
- satisfies backlog, age, completion, starvation, and volatility guardrails.

Close A5.1 conservatively if all apparent structure is explained by demand,
queueing, service, action opportunity, prediction spend, or remaining work
budget. Any strange-attractor-like or lobe-like language is secondary and is
unsupported unless the full preregistered accounting and surrogate-null gates
pass first.
