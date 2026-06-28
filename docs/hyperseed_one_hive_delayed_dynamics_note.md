# Hyperseed One-Hive Delayed Dynamics Note

Date: 2026-06-28.

Status: design guidance after the fixed A7.2 smoke closed fail-closed. This
note records Ben's follow-up discussion with external AI agents about
Hyperseed ontology, single-hive complexity, and mathematical tuning axes for
strange-attractor-oriented OmegaSim work. It does not reopen A7.2, authorize
post-result A7.2 parameter tuning, or supersede the already authorized
three-hive ring preregistration. It should inform the next preregistration and
possible later one-hive follow-up.

## Core Takeaway

Three hives are diagnostically useful, but not ontologically required for
complex dynamics. A single hive can already be a nonlinear recurrent dynamical
system if it contains:

- multiple internal state variables;
- nonlinear thresholds;
- delayed feedback;
- resource competition;
- memory or artifact fields that affect later action;
- imperfect prediction and control.

In Hyperseed terms, one hive can be a self-modulating germ. Three hives are
interacting germs with ecological semiotic coupling. The one-hive case should
already be capable of endogenous cognitive-metabolic dynamics; the three-hive
ring mainly gives cleaner relational diagnostics such as source attribution,
lead-lag structure, phase offsets, target nulls, and cross-hive mediation.

## Interpretation Of A7.2

The A7.2 fixed smoke was the right first test of this direction because it
introduced delayed artifact-mediated endogenous prediction:

- `predict` invests resource in anticipating future state;
- `work` transforms task/nutrient flow into progress;
- `review` filters artifact/nutrient flow through a membrane-like operation;
- `synthesize` consolidates distributed work into higher-order form;
- delayed forecast/artifact queues prevent same-tick help;
- source ledgers protect against mistaking accounting flow for real
  morphogenesis.

The fixed A7.2 smoke closed fail-closed. That is informative, not a reason to
discard the one-hive hypothesis. It means the particular frozen A7.2 smoke did
not produce residual structure beyond its required nulls at the tiny
preregistered scale. It does not prove that one-hive delayed self-coupling
cannot produce complex dynamics.

## Hyperseed Mapping For OmegaSim

The current simulator has mostly modeled nutrient flow and service metabolism:
arrivals, queues, work opportunity, completion, transfer, and backlog.

The next richer target is germ self-modulation through delayed semiotic
artifacts:

- Seed: shared telos or project attractor.
- Germs: agents, roles, or hives with local state, prediction, memory, and
  action policy.
- Membranes: observation boundaries, trust gates, review filters, delay,
  bandwidth, permissions, and artifact acceptance rules.
- Nutrient flows: messages, tasks, code diffs, proof fragments, experiment
  results, critiques, failed attempts, and artifact updates.
- Morphogenesis: changing division of labor, routing, trust, specialization,
  and durable higher-order artifact formation.

For OmegaSim, a real morphogenesis claim should involve recurrent formation,
deformation, repair, and persistence of higher-order artifacts after controlling
for queue, load, action count, transfer opportunity, and accounting fields.

## Mathematical Frame

A compact way to formalize the search space is as a delayed nonlinear map:

```text
x(t + 1) = F(x(t), x(t - tau_1), ..., a(t), u(t), epsilon(t); theta)
a(t)     = softmax_or_argmax(G(x(t - tau), h(t), b(t); theta_a))
h(t + 1) = H(h(t), prediction_error(t - tau), fatigue(t), artifact(t); theta_h)
```

where:

- `x` is the residual cognitive-metabolic state;
- `a` is action allocation among predict/work/review/synthesize;
- `h` is adaptive threshold/fatigue/memory state;
- `u` is exogenous demand or perturbation;
- `epsilon` is noise or drift;
- `tau` values are forecast, artifact, transfer, and observation delays;
- `theta` contains logistic slopes, coupling strengths, decay rates, costs,
  and membrane permeability.

The useful tuning variables should be made dimensionless where possible.
Suggested axes:

```text
coupling_gain              = logistic_slope * effective_artifact_to_action_gain
delay_relaxation_ratio     = feedback_delay / artifact_or_threshold_relaxation_time
memory_persistence         = 1 - artifact_decay
prediction_cost_ratio      = prediction_work_cost / available_work_opportunity
threshold_adaptation_ratio = threshold_learning_rate / threshold_recovery_rate
hysteresis_strength        = threshold_shift_after_action / baseline_threshold_width
noise_to_signal_ratio      = artifact_or_forecast_noise / deterministic_update_scale
membrane_permeability      = accepted_cross_agent_artifact_flow / proposed_flow
resource_scarcity          = demand_load / service_capacity
heterogeneity_index        = variance(agent_thresholds, delays, roles, or gains)
```

Complex dynamics are most likely near intermediate regimes, not extremes:

- coupling high enough that feedback matters, but not so high that everything
  saturates;
- delay comparable to relaxation time, not nearly zero and not so long that
  feedback is decorrelated;
- memory persistent enough to create state, but leaky enough to keep moving;
- prediction costly enough to create tradeoffs, but not so costly that agents
  never predict;
- membrane permeability intermediate enough for semiotic coupling, not full
  mixing and not isolation;
- heterogeneity sufficient to break symmetry, but not so large that coordination
  collapses.

## Diagnostics For Strange-Attractor-Oriented Search

The diagnostics should separate structured recurrence from noisy irregularity,
ordinary regulation, or throughput phase-locking.

Useful candidates:

- residual delay embeddings after accounting controls;
- largest finite-time Lyapunov exponent or perturbation divergence/reconvergence;
- recurrence plots and recurrence quantification over residual artifact state;
- return maps or Poincare sections on artifact/threshold/fatigue variables;
- spectral entropy and multi-scale entropy;
- permutation entropy for symbolic state motifs;
- correlation dimension only as an exploratory diagnostic, not a promotion
  gate at tiny smoke scale;
- surrogate nulls: phase shuffle, block shuffle, amplitude-matched linear,
  threshold shuffle, same-tick leakage control, spend-only replay, artifact-off
  source-ledger null;
- causal ablations: disable prediction, review, synthesis, fatigue adaptation,
  threshold adaptation, or artifact memory.

The most important distinction is:

```text
better regulation != emergent state-language
```

Better regulation can mean lower backlog, smoother artifact readiness, or
better forecast skill. Emergent state-language requires recurring symbolic or
semiotic motifs in residual artifact dynamics that survive nulls and accounting
controls.

## One-Hive Follow-Up Option

After respecting the A7.2 fail-closed result, a coherent later one-hive follow
up could be a separately preregistered A7.3-style dimensionless sweep. It would
not tune A7.2 retrospectively. It would instead prospectively sweep a small
grid over the dimensionless axes above, with fixed analysis and kill rules.

Candidate purpose:

```text
Find whether a richly self-coupled single hive has a bounded region of
nontrivial residual recurrence that is neither queue accounting nor
simple throughput regulation.
```

Candidate design:

- choose two or three values each for coupling gain, delay/relaxation ratio,
  memory persistence, prediction cost ratio, and threshold-adaptation ratio;
- keep demand/service streams paired and fixed;
- use short deterministic pilot seeds first, then a held-out paired-seed block
  only if the pilot finds a prospectively defined candidate regime;
- preregister no-go regions such as saturation, isolation, zero prediction,
  productivity collapse, and source-ledger leakage;
- require any candidate regime to beat amplitude-matched linear, phase-shuffled,
  threshold-shuffled, spend-only, and artifact-off controls.

This would address Ben's intuition that complex dynamics should be possible
within one hive, while preserving the project's hard-won negative-results
discipline.

## Three-Hive Ring Implication

The next already authorized step remains a separate three-hive ring
preregistration. This note suggests that the ring should not be framed as
"complexity requires multiple hives." Instead, frame it as:

```text
Three hives provide cleaner relational tests for dynamics that may already
exist inside one self-modulating hive.
```

For the ring, the primary nonlinear dependency should probably emphasize
cross-hive artifact readiness plus contradiction/risk, not demand prediction
alone. Demand prediction risks producing throughput phase-locking. Artifact
readiness and contradiction/risk are more likely to create multi-lobed
cognitive state transitions, review/synthesis bursts, and semiotic repair
cycles.

## Recommended Use By Automation

1. Do not alter or reinterpret A7.2 results from this note.
2. In the three-hive preregistration, state explicitly that three hives are a
   diagnostic amplifier, not an ontological requirement for complexity.
3. Include cross-hive artifact readiness and contradiction/risk as primary
   candidate nonlinear dependencies.
4. Add dimensionless tuning axes and attractor diagnostics to the design
   considerations section.
5. If the three-hive preregistration would otherwise become too large, park the
   one-hive dimensionless sweep as a separate future A7.3 preregistration.
