# OmegaSim Provisional Experiment Roadmap

Accepted by Ben on 2026-06-27.

Update 2026-06-27: A6/A6.1/A6.2 are now closed conservatively. Ben accepted
proceeding to A7 as the next preregistered direction. A7 is a new
semantic-field design gate, not a promotion of A6.2 and not permission to
broaden A6.2 seeds.

Supersession note 2026-06-27: this older accepted roadmap has been superseded
by the current source-of-truth automation status after the reopened A5,
A5.1a, and A7 long-horizon gates closed conservatively. The current posture is
closed awaiting Ben's decision; the non-active A7.2 decision document does not
authorize new runs or mechanics.

This roadmap replaces the closed A5 no-op posture as the provisional direction
for OmegaSim experimentation. It does not authorize an unbounded rewrite or a
large simulation sweep. The immediate next task is now to convert A7 into a
minimal, testable implementation gate.

## Roadmap Order

1. **A6: Single-hive logistic-appraisal smoke scaffold**
   - Add latent motivational/appraisal state not reducible to queue depth.
   - Add thresholded artifact handoff as the first functional nonlinear loop.
   - Add sigmoid/softmax action selection over appraisal signals.
   - Add hysteresis, adaptive thresholds, fatigue, and costly prediction only
     in the smallest form needed for smoke tests.
   - Preserve deterministic artifacts and paired-seed discipline.

2. **A6 analysis gate**
   - Record latent state, artifact state, thresholds, fatigue, prediction
     expenditure, and prediction error.
   - Residualize load, service, action opportunity, work budget, clock trend,
     and queue variables before making lobe or recurrence claims.
   - Compare delayed logistic/hysteretic/costly prediction against
     amplitude-matched linear, same-tick logistic, phase-shuffled, and
     threshold-shuffled controls.

3. **A7: Semantic-field version**
   - Add a richer semantic activation field only after A6 artifacts and
     controls are stable.
   - Let agents act on novelty, coherence, contradiction, risk, trust, and
     artifact readiness rather than queue state alone.

4. **A8: Three-hive Moltbook ring**
   - Move beyond two hives for serious phase and target nulls.
   - Use at least three biased hives: exploration/research, formalization/
     implementation, and synthesis/review.
   - Test phase-differentiated artifact grammar rather than mere synchrony.

## Immediate Next Step

Create an A7 implementation gate before any broad experiment:

```text
freeze semantic/artifact state vector
freeze logistic and linear action utility equations
freeze semantic/artifact field update rules
freeze prediction-budget accounting
freeze source-preserving null semantics
define paired seed/noise streams
define smoke configs
define output schemas
write deterministic artifact tests
write read-only analysis skeleton
run only a tiny smoke grid
```

## Non-Goals

Do not start with:

```text
large parameter sweeps
three-hive mechanics
real LLM calls
dashboards
Lean/Slack/browser/Atomspace integrations
new queue-derived lobe labels as primary endpoints
claims from raw backlog, throughput, or action counts
```

## Promotion Standard

Promote beyond A7 smoke only if the logistic semantic-field condition shows
useful structured recurrence in residual semantic/artifact state, not merely
worse queueing, more handoff churn, or a source-accounting artifact. It must
beat amplitude-matched linear controls, semantic-off controls, source-preserving
shuffle/null controls, preserve or improve artifact utility, and maintain
bounded backlog-adjusted productivity.
