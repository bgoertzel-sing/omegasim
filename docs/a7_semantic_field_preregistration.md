# A7 Semantic-Field Preregistration

Accepted start date: 2026-06-27.

A7 is the next OmegaSim target after the conservative A6.2 closure. It asks
whether adding a source-accounted semantic/artifact activation field can create
productive, compressible, residual structure that the A6 logistic-appraisal
mechanism alone did not produce.

A7 is not a broad sweep, not a multi-hive experiment, and not an A6.2 promotion.
The first step is a design and implementation gate.

## Scientific Question

Can a single hive develop nontrivial, partly predictable collective dynamics
when each agent's activity has a logistic-shaped dependence on other agents'
recent semantic/artifact contributions, under limited prediction and attention
resources?

The intended positive case is not chaos for its own sake. The target is a
productive structured regime:

- semantic novelty, coherence, contradiction, risk, trust, and readiness vary
  in a coupled way;
- agents can approximately predict the high-level pattern without spending
  unlimited resources;
- the resulting trajectory is compressible but not merely periodic;
- the effect survives accounting controls and source-preserving nulls.

## Mechanism Hypothesis

If agents perfectly predict each other's needs, dynamics may collapse into a
stable low-interest regime. If agents have no predictive signal, dynamics may
collapse into noise or queue pressure. A7 targets the intermediate regime:
limited predictors create errors, those errors create new semantic structure to
predict, and the group may settle into a structured strange-attractor-like
grammar whose high-level pattern is easier to predict than its micro-details.

The concrete mechanism should therefore include:

- a shared semantic/artifact activation vector `A(t)`;
- per-agent appraisal variables derived from recent self and peer
  contributions to `A(t)`;
- finite prediction/attention budget spent on estimating future peer needs or
  artifact-field changes;
- logistic action utilities whose inputs include source-accounted semantic
  field variables rather than queue variables alone;
- bounded update rules so failures remain interpretable.

## Initial State Vector

The first A7 implementation gate should freeze a small source-accounted state
vector before code:

```text
semantic_novelty
semantic_coherence
semantic_contradiction
semantic_risk
artifact_readiness
trust_weighted_salience
prediction_budget_spent
prediction_error
```

Names may change before implementation, but the frozen schema must separate:

- semantic/artifact field values;
- agent prediction expenditure;
- prediction error;
- source contributions to each field;
- queue/load/action accounting controls.

## Primary Comparisons

The first A7 smoke comparison should be paired-seed and minimal:

```text
A7 logistic semantic-field coupling
  versus
semantic-off A6.2-compatible baseline
  versus
amplitude-matched linear semantic-field coupling
  versus
source-preserving semantic-label shuffle
  versus
semantic-field phase shuffle
  versus
prediction-budget timing-broken matched-count null
```

Do not broaden seeds until the schema, source accounting, and analyzer contract
pass on a tiny paired smoke.

## Primary Observables

A7 should not rely on raw backlog, throughput, or queue-derived lobe labels as
primary evidence. The first analyzer should publish:

- source-field completeness and reconstruction status;
- residual recurrence metrics on semantic/artifact state after controlling for
  queue/load/action/service fields;
- field-level source-share tables;
- prediction-budget and prediction-error trajectories;
- compressibility or grammar proxy for residual semantic-state transitions;
- backlog-adjusted productivity and artifact utility safeguards;
- paired-seed direction agreement.

## Required Nulls And Controls

Any positive A7 interpretation must beat all of these:

- amplitude-matched linear semantic-field coupling;
- semantic-off baseline;
- source-preserving semantic-label shuffle;
- phase-shuffled semantic-field trajectory;
- prediction-budget timing-broken matched-count null;
- full queue/load/action/service accounting residualization.

The analyzer must fail closed if source fields are missing, residualization
cannot compute, null artifacts are incomplete, or the positive condition wins
only by degrading productivity.

## Promotion Standard

A7 is eligible for a later mechanism pilot only if the first gate shows:

1. all required source and control fields present;
2. semantic-field deltas reconstruct from named source components;
3. logistic semantic coupling beats linear and all preregistered nulls on the
   same residual semantic-state target;
4. paired seeds agree in direction;
5. backlog-adjusted productivity is not worse than controls;
6. the residual transition pattern is compressible but not simply periodic.

If these conditions fail, A7 should close as another clarifying negative result
or be redesigned before any seed broadening.

## First Automation Task

Create an A7 implementation gate before simulator work:

```text
freeze A7 state vector and field update equations
freeze logistic and linear action-utility equations
freeze prediction-budget accounting
freeze null semantics
define artifact/event/metric schema additions
write deterministic schema/source-accounting tests
write read-only analyzer skeleton
run only a tiny paired smoke after tests pass
```

No real LLM calls, dashboards, Lean, Slack, browser automation, Atomspace
integrations, live task boards, or multi-hive coupling are authorized by this
gate.
