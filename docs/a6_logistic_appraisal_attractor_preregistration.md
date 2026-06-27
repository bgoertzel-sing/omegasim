# A6 Logistic-Appraisal Attractor Preregistration

This document records Ben's 2026-06-27 post-A5 direction for a new OmegaSim
research phase. It is a design/preregistration artifact, not simulator code. It
supersedes "more pressure" or "more seeds" as the next plausible route toward
complex dynamics.

Do not implement A6 mechanics until this design has been reviewed and converted
into a concrete implementation plan with smoke tests, artifact schemas, and
analysis controls. The aim is not to add logistic dynamics as an arbitrary chaos
generator. The aim is to model bounded, thresholded cognitive appraisal:
agents ignore weak signals, engage sharply near salience thresholds, saturate
under overload, and adapt thresholds based on fatigue, trust, risk, novelty,
prediction error, and recent success.

## Motivation From A2-A5

The existing OmegaSim evidence is negative in a useful way:

- A2 pressure/attention results are dominated by queue load, action opportunity,
  and service capacity.
- A3 freezes the single-hive interpretation as queue-flow/service accounting.
- A4 delayed two-hive synchrony produced an interesting diagnostic, but
  opportunity/load/action/transfer controls moved the residual inside the null.
- A5 prediction improved forecast skill, but did not produce residual
  structured dynamics beyond load, service, action opportunity, task volume,
  and work-budget accounting.

Therefore the next experiment should introduce state variables and response
mechanisms that are not queue-depth proxies. The candidate target is a
thresholded artifact and appraisal lifecycle:

```text
explore
  -> synthesize
  -> review
  -> formalize / implement
  -> communicate
  -> new exploration
```

Delays, failed handoffs, prediction errors, fatigue, and adaptive thresholds
should make this lifecycle structured but non-periodic.

## Core Scientific Hypothesis

Structured strange-attractor-like dynamics are more likely when agents have:

- latent motivational state;
- semantic/artifact state independent of queues;
- sigmoid or softmax action selection over appraisal signals;
- delayed cross-role influence;
- hysteresis and adaptive thresholds;
- prediction as a costly endogenous action;
- mild noise and heterogeneity;
- functional loops that serve artifact improvement, review, implementation,
  communication, and maintenance.

The predicted sweet spot is near critical surfaces:

```text
task inflow close to service capacity
semantic novelty close to overload threshold
artifact readiness close to review threshold
risk close to escalation threshold
prediction error close to coordination threshold
resource use close to maintenance threshold
```

Too little gain should produce dull linear response. Too much gain should
produce saturation, lock-in, or crude oscillation. The target regime is
near-threshold, delayed, bounded, mildly noisy, and history-dependent.

## New State Variables

A6 should add latent or semi-latent state that is not merely another name for
queue depth:

```text
agent motivational state
semantic field state
artifact maturity state
prediction-error state
trust/provenance state
fatigue/overload state
attention-threshold state
```

These variables should become the substrate for future lobe discovery. Existing
queue/action lobe labels may remain compatibility diagnostics, but they must
not be primary evidence for attractor structure.

## Role Set

The first A6 single-hive model may replace or augment the current generic roles
with cognitively interpretable role biases:

```text
explorer
synthesizer
formalizer
implementer
reviewer
coordinator
maintainer
communicator
```

This is still abstract and numeric. It should not call real LLMs, Lean, Slack,
browsers, Atomspace, live task boards, or external services.

## Latent State Per Role Or Agent

Each role or agent should carry a compact motivational/appraisal vector, for
example:

```text
activation
arousal
focus
resolution
risk_sensitivity
novelty_appetite
fatigue
thresholds
```

A later richer version may map this to a simplified OpenPsi/MetaMo-style layer:

```text
M_i = (
  valence,
  arousal,
  approach_dominance,
  resolution,
  focus_threshold,
  securing_exteroception
)

G_i = (
  help,
  curiosity,
  novelty,
  ethics,
  social,
  task_closure,
  self_improvement,
  individuation,
  transcendence
)
```

For the first implementation, keep the dimensionality small and deterministic.

## Semantic And Artifact Field

The simulator should include a shared semantic/artifact activation field:

```text
A(t) = [
  research_novelty,
  theorem_proof_salience,
  implementation_salience,
  external_communication_salience,
  risk_provenance_debt,
  synthesis_coherence,
  contradiction_tension,
  maintenance_infrastructure_salience,
  artifact_readiness,
  trust_weighted_import_salience
]
```

Agents act on this field and respond to it. Examples:

- explorer-like agents increase novelty and uncertainty;
- formalizer-like agents consume proof candidates and can increase proof
  failure bursts;
- synthesizer-like agents increase coherence and artifact readiness;
- reviewer-like agents reduce unsupported-claim salience but increase review
  pressure;
- maintainer-like agents reduce maintenance entropy and later lower failure
  probability.

## Logistic Appraisal And Action Selection

For each agent or role `i`, maintain action utilities for modes such as:

```text
explore
message
create_task
work_task
synthesize
review
formalize
delegate
predict
escalate
maintain
pause
communicate
reframe
```

Actions should be selected via softmax:

```text
P_i(a,t) = exp(U_i^a(t) / T_i) / sum_b exp(U_i^b(t) / T_i)
```

Each utility receives sigmoidally gated appraisal inputs:

```text
U_i^a(t) =
  b_i^a
  + sum_j K_ij^a * sigmoid(k_ij^a * (S_j(t - tau_ij) - theta_ij^a))
  + W_i^a M_i(t)
  + V_i^a G_i(t)
  - fatigue_cost_i^a(t)
  - risk_cost_i^a(t)
```

Here `S_j` should be an appraisal signal, not merely raw activity. Candidate
signals:

```text
semantic novelty produced by j
artifact readiness from j
unresolved contradiction from j
proof failure burst from j
review criticism from j
risk signal from j
trust-weighted imported claim from j
prediction error caused by j
maintenance stress caused by j
```

## Thresholded Artifact Handoff

The strongest minimal candidate mechanism is thresholded artifact handoff.
Each artifact can carry:

```text
novelty
coherence
actionability
provenance_debt
risk
contradiction
readiness
implementation_maturity
communication_maturity
```

Define readiness abstractly, for example:

```text
readiness_a =
  w1 * novelty_a
  + w2 * coherence_a
  + w3 * actionability_a
  - w4 * provenance_debt_a
  - w5 * risk_a
```

Then role actions are naturally thresholded:

```text
P(review artifact a) =
  sigmoid(k * (readiness_a - theta_review))

P(communicate artifact a) =
  sigmoid(k * (readiness_a - theta_comm))
  * (1 - sigmoid(k * (risk_a - theta_risk)))

P(reframe artifact a) =
  sigmoid(k * (contradiction_a - theta_reframe))

P(implement artifact a) =
  sigmoid(k * (actionability_a - theta_impl))
```

This creates lobe transitions for functional reasons: artifacts ripen, trigger
role shifts, get reviewed, become safe, then propagate.

## Learnable Novelty As An Inverted-U

Curiosity should not be monotone in novelty. Agents should prefer learnable
novelty: not too boring and not too chaotic.

Use an inverted-U response:

```text
C(n) =
  sigmoid(k * (n - theta_low))
  * (1 - sigmoid(k * (n - theta_high)))
```

Qualitative behavior:

```text
too little novelty -> boredom, low exploration
moderate novelty -> curiosity, exploration, synthesis
too much novelty -> overload, securing, review, compression request
```

This creates a natural loop:

```text
exploration creates novelty
novelty becomes overload
overload triggers synthesis/review
synthesis reduces uncertainty
reduced uncertainty permits exploration again
```

## Prediction As A Costly Endogenous Action

A5 showed that forecast skill alone is insufficient. In A6, prediction should
be an action that consumes budget now and has delayed payoffs:

```text
predict:
  consumes work budget now
  improves forecast later
  reduces uncertainty if successful
  increases fatigue if overused
  may trigger coordination if prediction error is high
```

Per-agent or per-role budget can be represented as:

```text
B_i(t) =
  B_i_total
  - B_i_work(t)
  - B_i_message(t)
  - B_i_predict(t)
  - B_i_review(t)
```

Prediction error should feed arousal and coordination pressure:

```text
error_i(t + tau) = actual_i(t + tau) - predicted_i(t + tau)

M_i_arousal(t + 1) <- M_i_arousal(t) + alpha * abs(error_i(t))

P_i(coordinate) <- sigmoid(k * (abs(error_i) - theta_coord))
```

Prediction bursts should be part of the target dynamics, not merely external
controller inputs.

## Hysteresis And Adaptive Thresholds

Plain logistic response may settle into simple periodic or saturated behavior.
Add memory:

```text
h_i(t + 1) = rho * h_i(t) + (1 - rho) * a_i(t)
```

Let thresholds drift:

```text
theta_i^a(t + 1) =
  theta_0_i^a
  + lambda_load * load_i(t)
  + lambda_fatigue * fatigue_i(t)
  - lambda_success * success_i^a(t)
  + lambda_risk * risk_i(t)
```

This makes lobe transitions history-dependent instead of memoryless queue
responses.

## Functional Feedback Loops

A6 should implement a small number of cognitively meaningful loops rather than
generic nonlinear feedback.

### Loop A: Exploration-Synthesis-Review

```text
exploration increases semantic novelty
semantic novelty plus partial coherence triggers synthesis
synthesis creates artifact candidates
artifact candidates trigger review
review reduces risk/provenance debt
low risk plus high coherence triggers implementation or communication
```

### Loop B: Proof-Bottleneck Reframing

```text
theorem/proof candidate generation increases proof candidates
formalization consumes candidates slowly
repeated proof failure increases contradiction tension
contradiction tension triggers conceptual reframing
reframing changes theorem candidate distribution
successful proof reduces tension and triggers synthesis
```

### Loop C: Communication-Risk

```text
communication pressure rises with artifact maturity
external-risk appraisal rises with communication pressure
review rises sigmoidally after risk threshold
successful review permits communication
failed review returns artifact to synthesis
```

### Loop D: Maintenance-Resource

```text
tool/resource stress rises with activity
maintenance probability rises after threshold
maintenance temporarily reduces productive capacity
maintenance later lowers failure probability and queue friction
```

## First Experiment Family

### A6 Single-Hive Role-Coupled Motivational Model

Start with one hive. Do not start with three hives or real external tools.

Conditions:

```text
1. no cross-role coupling
2. amplitude-matched linear coupling
3. same-tick logistic coupling
4. delayed logistic coupling
5. delayed logistic coupling with hysteresis
6. delayed logistic coupling with adaptive thresholds
7. delayed logistic coupling with costly prediction
```

Primary contrast:

```text
delayed logistic + hysteresis + prediction cost
  versus
amplitude-matched linear
```

Success criterion:

```text
more residual recurrent structure
better or equal artifact utility
not worse backlog-adjusted productivity
survives shuffled/null controls
```

### A7 Semantic-Field Version

After A6 establishes clean artifacts and controls, add the semantic activation
field `A(t)` and let agents act on novelty, coherence, contradiction, risk,
and artifact readiness. This is the first version where a genuinely
multi-lobed cognitive attractor becomes plausible.

### A8 Three-Hive Moltbook Ring

Do not use two hives again for serious phase/target nulls. Use at least three
hives:

```text
Hive A: exploration/research biased
Hive B: formalization/implementation biased
Hive C: synthesis/review biased
```

Couple them through artifact and appraisal signals:

```text
artifact readiness
unresolved contradiction
proof failure burst
review debt
semantic novelty
trust-weighted import salience
```

The target global grammar is phase-differentiated:

```text
A explores -> B formalizes -> C reviews/synthesizes -> A reframes
```

rather than mere synchronization.

## Parameter Sweep Plan

Initial sweeps should target intermediate regimes:

```text
coupling slope k:
  0, 0.5, 1, 2, 4, 8, 12

threshold percentile theta:
  30%, 50%, 70% of baseline signal distribution

delay tau:
  0, 1, 2, 4, 8, 16 ticks

memory rho:
  0, 0.3, 0.6, 0.85, 0.95

fatigue gain:
  0, low, medium, high

prediction cost:
  0, low, medium, high

noise:
  0, 0.01, 0.03, 0.1
```

Expected useful regime:

```text
moderate-to-high k
theta near normal operating range
tau comparable to natural dwell time
rho around 0.6-0.9
nonzero prediction cost
small but nonzero stochasticity
```

## Observables And Analysis

Primary observables should come from residualized latent state:

```text
Y_t = residualized[
  M_t,
  G_t,
  A_t,
  artifact_t,
  prediction_error_t,
  trust_t,
  fatigue_t,
  threshold_t,
  graph_features_t
]
```

Residualize out:

```text
queue depth
queue delta
task inflow
service capacity
work budget
action opportunity
transfer volume
clock trend
```

Suggested pipeline:

```text
1. collect full latent state vectors
2. residualize load/service/action variables
3. delay-embed residual vectors
4. run PCA/UMAP/diffusion maps
5. cluster with HDBSCAN or HMM/HSMM
6. infer lobe transition grammar
7. compare to phase-shuffled, threshold-shuffled, and linearized controls
8. compute recurrence, compression, nonlinear forecastability, and perturbation recovery
```

Avoid making raw queue depth, raw task creation, or current baseline lobe labels
the primary observables.

## Functional Attractor Score

Do not optimize for chaos. Define success as useful structured recurrence:

```text
nontrivial recurrence:
  trajectories revisit similar regions but not exactly periodically

multi-lobe structure:
  exploration, synthesis, review, implementation, maintenance, communication

bounded queue health:
  not just endless backlog

artifact improvement:
  quality, support, coherence, or maturity improves over cycles

useful novelty:
  semantic field explores without dissolving into noise

recovery:
  after perturbation, the hive returns to a productive lobe grammar

compressible-but-not-periodic lobe strings:
  structure without mere clockwork
```

A possible score:

```text
FAS =
  artifact_quality
  + useful_novelty
  + recovery
  + crossrole_coordination
  + grammar_score
  - wasted_work
  - backlog_penalty
  - pathology_penalty
```

Good lobe phrases:

```text
explore -> synthesize -> review -> implement
explore -> formalize -> reframe -> formalize -> synthesize
communicate -> review -> communicate
maintenance -> work -> synthesis
```

Pathological phrases:

```text
explore -> explore -> explore -> explore
review -> review -> review -> review
communicate -> communicate -> communicate
task_generation -> task_generation -> task_generation
```

## Nulls And Controls

Promotion requires comparison against:

```text
no cross-role coupling
amplitude-matched linear coupling
same-tick logistic coupling
phase-shuffled coupling
threshold-shuffled coupling
Markov-preserving macro-state shuffles
load/service/action residual controls
budget-matched prediction controls
```

Any positive claim must show more residual recurrent structure than
amplitude-matched linear controls, survive the shuffled/null controls, and not
come from worse queueing or endless dwell.

## Promotion Rule

Promote A6 only if all conditions hold:

1. The delayed logistic/hysteretic/prediction-cost condition has more residual
   recurrent structure than amplitude-matched linear coupling.
2. The effect survives load, service, action opportunity, work budget, clock,
   and artifact throughput controls.
3. The effect survives phase-shuffled, threshold-shuffled, and macro-state null
   controls.
4. Artifact utility is better or equal to controls.
5. Backlog-adjusted productivity is not worse than controls.
6. The lobe grammar is compressible but not periodic.
7. The system recovers from small perturbations into a productive grammar.

If these conditions do not hold, close A6 as another clarifying negative result
and do not proceed to A7/A8 without a new design.

## Implementation Gate

Before code:

- freeze the exact A6 state vector;
- freeze action names and action utility equations;
- define artifact fields and update rules;
- define random/noise streams and paired-seed handling;
- define output schemas for latent state, artifact state, and residual analysis;
- write smoke tests for deterministic artifacts;
- write read-only analyzers before holdout interpretation;
- choose a tiny smoke grid before any larger sweep.

The first code change should implement only the smoke-scaffold contract and
tests. Do not add dashboards, external integrations, real LLM calls, or
multi-hive mechanics in the first A6 implementation.
