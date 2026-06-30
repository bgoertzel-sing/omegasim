# A5.2 Endogenous Delayed Prediction-Spend Preregistration

Date: 2026-06-30.

## Purpose

This preregisters the next bounded A5 design gate after the single-hive
anticipatory predictive-control smoke and the A5.1a cost-calibration closure.
Those earlier gates showed that deterministic predictors can improve forecast
skill under matched demand streams, and that prediction spend can be charged
against work opportunity, but no A5-family condition has survived the
preregistered residual/null promotion rules.

A5.2 asks a narrower resource-bounded question before any new simulator run:
can endogenous, delayed prediction-spend decisions create residual collective
dynamics that remain useful and partially predictable after accounting for
demand, service, action opportunity, work budget, charged spend, and timing
nulls?

This document is preregistration only. It does not authorize implementation,
broader seeds, dashboards, external integrations, A7-family mechanics, or
three-hive coupling until Ben explicitly selects this gate for implementation.

## Hypothesis

Prediction is a scarce managed resource, not a free observer. Perfect
prediction can smooth away the dynamics of interest, while zero prediction
leaves the hive reactive. The interesting regime may require agents to decide
when to spend limited prediction budget under delayed feedback.

The A5.2 hypothesis is that intermediate endogenous prediction spend, with a
delay between spend, forecast availability, and service-priority adjustment,
may produce richer but still partially predictable residual collective states
than zero-spend reactivity, fixed exogenous spend, spend-only replay nulls, or
oracle smoothing. A positive result would mean that structured forecast errors
and delayed budget allocation create useful high-level regularities that are
cheaper to predict than detailed task-level trajectories.

## Scope

A5.2 remains deterministic, single-hive, and abstract/numeric:

- one existing OmegaSim hive, queue, action set, attention classes, and artifact
  contract;
- no real LLM calls, Lean, Slack, browser automation, Atomspace integrations,
  live task boards, dashboards, or human-in-the-loop task boards;
- no two-hive or three-hive transfer, target coupling, or phase coupling;
- paired seeds and matched deterministic demand streams across all conditions;
- no committed result-bearing run artifacts until a later implementation
  instruction explicitly opens this gate.

Three-hive delayed anticipatory coupling remains downstream. It requires a
separate preregistration with target and phase nulls, matched transfer
opportunity, and resource-bounded cross-hive prediction costs.

## Mechanism To Freeze Before Implementation

The first implementation, if later authorized, must be the smallest
deterministic scaffold that adds endogenous delayed prediction spend to the
existing single-hive A5 surface. It should freeze these rules before running a
pilot:

- a per-tick prediction-spend decision made from observable hive state only;
- a limited prediction budget reservoir or per-tick cap, with any spend charged
  against the same work-opportunity ledger used by A5.1a;
- a deterministic delay between spend and usable forecast influence;
- a deterministic decay or expiration rule for forecasts that were bought but
  not yet used;
- explicit recording of spend decision inputs, pre-charge work opportunity,
  charged prediction work units, remaining work budget, forecast availability,
  and delayed forecast influence.

The endogenous spend controller may shift attention allocation or service
priority only through the preregistered delayed forecast channel. It must not
silently add task arrivals, service capacity, action opportunities, agent
count, work budget, or task-completion capacity.

## Conditions

Use paired seeds and matched demand streams across:

1. Reactive baseline: no prediction spend and no forecast influence.
2. Fixed low-budget predictor: existing low-budget linear or short-memory
   predictor with exogenous spend timing.
3. Endogenous low-budget predictor: low spend chosen from observable state with
   delayed forecast influence.
4. Endogenous medium-budget nonlinear predictor: bounded nonlinear forecast,
   endogenous spend timing, and delayed forecast influence.
5. Endogenous high-budget nonlinear predictor: larger bounded forecast budget,
   included as a smoothing/overfit contrast rather than the target condition.
6. Oracle predictor: future demand known, interpreted only as a smoothing
   positive control.
7. Spend-only replay nulls: same charged prediction work units on the same
   ticks as each endogenous condition, but with useful forecast timing removed.
8. Timing-broken predictor nulls: shuffled or phase-randomized forecasts that
   preserve marginal forecast structure and spend budget while breaking useful
   timing.

Every endogenous positive condition must have both a spend-only replay null and
a timing-broken predictor null before any residual-structure interpretation is
allowed.

## Accounting Locks

All conditions must match task-arrival totals, class-demand stream, service
capacity, action opportunity, agent count, action set, pre-charge work budget,
and deterministic demand process. Prediction condition may change only:

- when prediction spend is charged;
- when delayed forecast influence becomes available;
- how attention or service priority responds to the available forecast.

Analysis must explicitly control for demand phase, current backlog, queued age,
task arrivals, service opportunity, pre-charge work budget, charged spend,
remaining work budget, forecast availability, and spend-delay state. A5.2 fails
closed if an apparent residual is reproduced by spend timing alone, by
work-budget loss alone, or by a timing-broken/null forecast with matched spend.

## Primary Endpoints

Primary endpoints are:

- forecast skill per charged prediction work unit;
- lead-lag relation between spend decisions, forecast availability, attention or
  service allocation, and future demand;
- residual phase structure after the full accounting locks above;
- recurrence or return-map structure in delay embeddings of residual
  predictive-state variables, including spend-delay state;
- predictability or compressibility of emergent high-level collective states;
- comparison of residual predictability against fixed-spend, spend-only replay,
  timing-broken, reactive, and oracle controls;
- guardrails for final backlog, queued age, completion fraction, class
  starvation, prediction-spend volatility, remaining-work volatility, and
  forecast-influence volatility.

Throughput, completion fraction, lower backlog, or higher forecast skill alone
are guardrails or competence checks. They are not evidence for structured
collective dynamics.

## Decision Rules

A5.2 may proceed beyond a smoke/pilot only if the same intermediate endogenous
prediction-spend condition:

- improves forecast skill per charged work unit over reactive, fixed-spend, and
  both matched nulls;
- allocates spend and service ahead of future demand rather than merely
  tracking current backlog;
- retains nonzero, structured forecast errors;
- shows residual recurrence or high-level predictability after all accounting
  controls;
- remains more dynamically nontrivial than high-budget or oracle smoothing;
- satisfies backlog, queued-age, completion, starvation, and volatility
  guardrails.

Any strange-attractor-like, lobe-like, phase-structure, or emergent-state claim
is secondary and fails closed unless the preregistered accounting controls,
spend-only replay nulls, timing-broken nulls, and guardrails all pass first.

## Initial Implementation Boundary

If Ben later authorizes A5.2 implementation, the first code change should be a
single deterministic smoke scaffold and focused tests only. It should not add
dashboards, external services, live integrations, multi-hive mechanics, broad
seed sweeps, or committed scientific result artifacts.

Until that explicit implementation instruction exists, this preregistration is
the complete A5.2 artifact.
