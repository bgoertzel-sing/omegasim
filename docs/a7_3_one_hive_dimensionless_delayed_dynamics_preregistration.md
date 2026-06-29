# A7.3 One-Hive Dimensionless Delayed Dynamics Preregistration

Status: active initial implementation preregistration opened by Ben's
2026-06-29 instruction that OmegaSim should proceed, not pause.

This is a fresh line. It does not reopen A7.2, the three-hive ring, or A5 as
result-bearing experiments. Those gates remain fail-closed historical evidence.
This file freezes the initial A7.3 smoke contract for implementation.

## Scientific Question

Can a single OmegaHive, with delayed nonlinear self-coupling, costly prediction,
artifact-mediated memory, adaptive thresholds, fatigue, and logistic
cross-agent activity dependence, produce robust residual dynamical structure
that survives null controls and looks like genuine endogenous cognitive
metabolism rather than demand echoes, accounting artifacts, or throughput
phase-locking?

The first gate is not a broad sweep and not a strange-attractor claim. It is a
contract and smoke gate for a bounded one-hive delayed nonlinear dynamical
system whose state is explicit enough to support later recurrence, Lyapunov,
source-ledger, and surrogate-null analysis.

## Mechanism Sketch

Each agent has an activity allocation over roles such as predict, work, review,
synthesize, and rest. The probability or intensity of each role is a logistic
function of delayed hive variables and delayed peer-agent variables:

```text
a_i,r(t+1) = sigmoid(
    b_i,r
  + G_i,r * z_i,r(t)
  + H_i,r * peer_i,r(t - tau_peer)
  - C_i,r * cost_i,r(t)
  + noise_i,r(t)
)
```

Here `z_i,r(t)` may include delayed prediction error, artifact readiness,
artifact coherence, contradiction/risk, fatigue, uncertainty, memory pressure,
and recent action imbalance. The peer term is the key Ben-motivated nonlinear
dependency: one agent's activity should have logistic-shaped dependence on
another agent's recent activity or artifact signal.

Prediction is costly: time spent predicting reduces immediate work capacity.
Artifacts are delayed: a prediction or synthesis artifact cannot affect
activity in the same tick that creates it. Thresholds adapt slowly: repeated
prediction error or contradiction can lower or raise future thresholds, but only
through delayed updates.

## Lifted State

Every run must log a lifted delayed state sufficient for read-only analysis:

```text
x(t) = [
  agent_role_activities(t),
  delayed_agent_role_activities(t-k),
  artifact_readiness(t),
  artifact_coherence(t),
  contradiction_risk(t),
  prediction_error(t),
  prediction_uncertainty(t),
  fatigue(t),
  adaptive_thresholds(t),
  work_backlog(t),
  prediction_spend(t),
  memory_pressure(t),
  task_arrivals(t)
]
```

The lifted state, source ledger, and metrics must be emitted without requiring
reruns. Any analysis stage must be read-only over those artifacts.

## Dimensionless Controls

The initial implementation should expose these named controls:

```text
rho    = nonlinear coupling gain / relaxation rate
delta  = dominant feedback delay / relaxation time
mu     = memory persistence / adaptation time
kappa  = role-channel leakage or peer-coupling spread / within-role coupling
nu     = stochastic perturbation scale / deterministic signal scale
chi    = prediction cost / work opportunity
eta    = threshold adaptation rate / relaxation rate
```

The first smoke only needs a tiny fixed grid over a subset of these controls.
The broader sweep is deferred until the smoke contract, schemas, and nulls pass.

## Required Conditions

The initial A7.3 smoke should include at least these conditions:

- Low-gain contraction baseline: `rho` below the expected bifurcation region.
- No-delay control: `delta = 0` or same-tick influence blocked to the minimum.
- Linearized control: replace logistic peer dependence with a matched linear
  response.
- Artifact-off control: remove delayed artifact readiness/coherence influence.
- Prediction-cost control: preserve prediction labels while removing real cost.
- Phase-shuffled control: preserve marginal activity but break delayed
  temporal alignment.
- Threshold-shuffled control: preserve threshold distribution but break causal
  timing.
- Full A7.3 mechanism: delayed logistic peer dependence plus costly prediction,
  artifacts, fatigue, and adaptive thresholds.

## Primary Promotion Gates

A condition may only be discussed as scientifically interesting if all of these
pass:

- Boundedness: state variables remain compact and no instability is just numeric
  blow-up or saturation.
- Productivity: the hive remains meaningfully active and does not win by doing
  no work.
- Source integrity: source ledgers prove delayed variables are delayed and
  same-tick leakage is absent.
- Residual structure: delayed lifted-state predictors explain held-out
  residual dynamics beyond simple demand, backlog, and service accounting.
- Null dominance: the full mechanism beats all preregistered nulls on the
  primary residual and recurrence diagnostics.
- Recurrence evidence: recurrence structure is stronger than phase-shuffled and
  threshold-shuffled controls.
- Finite-time divergence check: Lyapunov-style local divergence is positive in
  the candidate region and not positive in the low-gain contraction baseline.

Failure of any gate is fail-closed. It can motivate a new preregistration but
cannot be used as evidence for strange-attractor-like dynamics.

## Initial Next Implementation Step

Add a minimal config/schema and deterministic smoke harness for A7.3 that emits
metrics, events, source ledger, and lifted state artifacts. Then add a read-only
preflight analyzer that verifies the gates above on those artifacts.
