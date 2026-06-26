# A5 Closure Note, Predictive-Control Seeds 7..16

This note closes the current A5 single-hive predictive-control research loop
using the fresh confirmatory seed `7..16` artifacts and the frozen promotion
rules in `docs/a5_confirmatory_addendum.md`.

No simulations were rerun for this closure note. No simulator mechanics,
multi-hive coupling, new lobe labels, dashboards, LLM calls, Lean, Slack,
browser automation, Atomspace integration, or external services were added.

External strategic review handling:

- `../outputs/strategy-reviews/omegasim/latest-review.md`
- `strategic_change_level: minor`
- `notify_ben: false`
- Accepted: preregister practical guardrail tolerances, use budget-matched
  timing-broken nulls, run only a fresh bounded confirmatory seed set, and close
  conservatively if forecast-skill gains do not survive residual accounting.
- Rejected: no recommendation was rejected.

## Decision

Freeze A5 single-hive predictive control as a forecast-skill manipulation that
does not demonstrate promotion-worthy residual structured dynamics.

The seed `7..16` confirmatory artifacts support a narrow positive claim:
intermediate predictors improve forecast skill under matched demand streams.
They do not support a broader claim that bounded prediction creates residual
lobe grammar, strange-attractor-like collective structure, or an interpretable
mechanism that survives load, service, action-opportunity, task-volume, and
work-budget accounting.

Do not add multi-hive anticipatory coupling, richer lobe architectures, new
simulator mechanics, dashboards, real LLM calls, Lean, Slack, browser
automation, Atomspace integrations, or external services from this A5 result.

## Evidence Boundary

The confirmatory summary in `docs/results/a5_confirmatory_seed7_16.md` reports
60 deterministic paired simulations across reactive, linear, nonlinear, oracle,
linear-budget shuffled, and nonlinear-budget shuffled conditions. Final task
creation was matched at a mean of `74.2` tasks for every condition.

Forecast skill improved for both intermediate predictors:

| contrast | forecast-skill delta |
| --- | ---: |
| linear minus reactive | 0.033517 |
| linear minus shuffled | 0.045425 |
| nonlinear minus reactive | 0.084033 |
| nonlinear minus nonlinear_shuffled | 0.095941 |

Those gains did not satisfy the preregistered residual-structure promotion
rule. The primary full-accounting `residual_state_predictability_r2` contrasts
were all inside paired label-permutation intervals:

| contrast | mean delta | positive delta rate | interpretation |
| --- | ---: | ---: | --- |
| linear minus reactive | 0.114949 | 0.5 | inside paired label-permutation interval |
| linear minus shuffled | -0.053977 | 0.5 | inside paired label-permutation interval |
| nonlinear minus reactive | 0.077593 | 0.7 | inside paired label-permutation interval |
| nonlinear minus nonlinear_shuffled | -0.091333 | 0.3 | inside paired label-permutation interval |

The promotion audit therefore failed closed:

- linear passed forecast-skill criteria and practical guardrails, but did not
  pass residual-structure or oracle nontriviality criteria;
- nonlinear passed forecast-skill criteria, but failed practical guardrails and
  did not pass residual-structure criteria.

## Interpretation

A5 adds a useful methodological result to the OmegaSim sequence: prediction
budget and forecast timing can be manipulated deterministically while keeping
demand streams and task creation matched. The confirmatory run then follows the
same pattern as the earlier A2-A4 work: apparent structure is not enough once
the analysis asks whether it remains beyond load, service, action opportunity,
and accounting controls.

The scientifically defensible endpoint is conservative. Resource-bounded
prediction improves forecast skill in this scaffold, but the current
single-hive design does not show residual structured dynamics worth promoting.

## Stop Conditions

Do not reopen A5 for more mechanics or larger seed sweeps from the seed `7..16`
result alone.

Acceptable reasons to reopen A5 are limited to:

- a concrete artifact or analyzer bug that changes the recorded result;
- a narrow read-only validation over existing artifacts;
- a separately preregistered future design explicitly requested before any new
  simulator mechanics are implemented.

If future work revisits anticipatory prediction, the next artifact should be a
new preregistration, not code. It should define the scientific claim, primary
residual endpoints, budget-matched nulls, guardrails, seed streams, and closure
rules before implementation.
