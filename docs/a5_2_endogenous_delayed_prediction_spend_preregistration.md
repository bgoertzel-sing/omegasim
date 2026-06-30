# A5.2 Endogenous Delayed Prediction-Spend Preregistration Draft

Status: non-active draft. This document records a possible next single-hive
scientific axis after the A5 and A7.3 fail-closed evidence. It does not
authorize simulator runs, analyzer runs, parameter sweeps, dashboards, external
integrations, real LLM calls, downstream multi-hive coupling, or promotion
language. Activation requires an explicit future status update from Ben.

## Motivation

Prior A5-family gates showed that bounded predictors can improve forecast
skill under matched hidden demand streams, but did not pass residual/null,
oracle-nontriviality, compression, or productivity guardrails. A7.3 fixed
validation also closed fail-closed against the preregistered null gates. The
remaining scientific gap is whether prediction effort chosen endogenously by
agents, charged against work, and coupled through delayed artifact/peer
feedback can create nontrivial residual dynamics after accounting controls.

## Hypothesis

An intermediate endogenous prediction-spend regime may produce delayed
residual structure only when all of the following are true:

- prediction spend is chosen from delayed uncertainty, error, peer activity,
  artifact readiness or risk, fatigue, and adaptive thresholds;
- prediction consumes scarce work opportunity;
- prediction affects future artifact state only after a fixed delay;
- later error, fatigue, and threshold updates depend on the delayed outcome;
- controls preserve demand, arrivals, service, backlog, queued age, action
  opportunity, work budget, prediction spend, and lost work.

The null expectation is fail-closed: apparent recurrence or synchrony is
assumed to be demand, queue, service, action-opportunity, or accounting leakage
unless the fixed controls and null contrasts reject that explanation.

## Frozen Mechanism Sketch

For agent `i` at tick `t`, prediction spend for `t+1` is selected by a bounded
logistic policy:

```text
P(predict_i,t+1) = sigmoid(
  beta_0
  + beta_u * delayed_uncertainty_i,t-d
  + beta_e * delayed_error_i,t-d
  + beta_p * peer_prediction_activity_t-d
  + beta_a * artifact_readiness_or_risk_t-d
  - beta_f * fatigue_i,t
  - beta_theta * adaptive_threshold_i,t
)
```

Prediction spend deducts from the same per-tick work budget used for service,
cleanup, implementation, and research actions. Any predictive advantage is
applied only through delayed artifact or task-priority updates; same-tick
effects are blocked.

## Conditions

The fixed one-hive condition family should include:

- zero-budget reactive baseline;
- intermediate endogenous delayed prediction-spend condition;
- high-budget or oracle-like smoothing condition;
- no-delay or same-tick-blocked null;
- amplitude-matched linear policy;
- cost-free prediction null;
- spend-only replay null with identical spend ticks and lost work;
- phase-shuffled delayed input null;
- threshold-shuffled null;
- artifact-off null;
- Markov-preserving macro-state surrogate.

## Primary Endpoints

Primary endpoints are residual-only and must be computed after accounting for
matched demand phase, arrivals, service capacity, backlog, queued age, action
opportunity, work budget, prediction spend, and lost work:

- held-out residual nonlinear-vs-linear forecast delta;
- recurrence/surrogate z-scores on coarse residual macro-state strings;
- finite-time local divergence in residual lifted state;
- compression improvement of residual macro-state strings;
- prediction-cost fraction and lost-work fraction guardrails;
- fatigue, threshold, saturation, and delayed-source integrity audits.

Queue depth, throughput, action counts, prediction spend, and timing synchrony
are manipulation checks only, not primary promotion endpoints.

## Promotion Gates

Promotion requires paired-seed agreement, source-ledger delay integrity, and
all primary endpoints beating every fixed null without productivity guardrail
failure. Any missing condition, missing seed, rank-deficient residual design
matrix, spend/accounting mismatch, same-tick leakage, or failed null contrast
closes the gate fail-closed.

## Non-Goals

This draft does not reopen A5 rescue tuning, A7.3 reruns, downstream multi-hive
coupling, dashboards, Lean, Slack, browser automation, Atomspace integration,
or real LLM calls. It also does not support lobe-like, strange-attractor-like,
semantic-dynamics, or collective-intelligence claims before a future activated
validation passes the frozen gates above.
