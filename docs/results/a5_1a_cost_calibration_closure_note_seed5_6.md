# A5.1a Cost-Calibration Closure Note, Seeds 5-6

Date: 2026-06-27.

This note closes the bounded A5.1a prediction-spend cost-calibration gate using
the paired-seed `5,6` smoke artifacts generated from
`configs/a5_1_prediction_spend_linear_smoke.yaml`.

No simulations were added for this note. No simulator mechanics, dashboards,
real LLM calls, Lean, Slack, browser automation, Atomspace integrations, live
task boards, multi-hive coupling, or broad seed sweeps were added.

External strategic review handling:

- `../outputs/strategy-reviews/omegasim/latest-review.md`
- `strategic_change_level: major`
- `notify_ben: true`
- Accepted: do not broaden A5.1 before cost/work-loss accounting is controlled;
  use a preregistered cost-calibration/spend-only-null patch.
- Completed in this branch: the A5.1a patch was preregistered, implemented, and
  tested on paired seeds `5,6`.
- Deferred: any delayed logistic endogenous-prediction or multi-hive design
  requires a new preregistration and Ben's explicit choice.

## Decision

A5.1a fails closed. The charged prediction-spend scaffold is useful for
accounting, and each charged linear cost rule improves forecast skill over its
spend-only replay null, but no charged condition passes the preregistered
full-accounting residual gate against that null.

Do not broaden A5.1 seeds or add rescue mechanics from this result. The result
supports a methodological claim only: prediction spend can be charged against
work opportunity and audited with matched spend-only replay nulls.

## Evidence Boundary

The comparison smoke wrote 14 deterministic run artifacts across seven
conditions:

- `linear_harsh_cost`
- `linear_harsh_cost_spend_only_replay`
- `linear_gentle_cost`
- `linear_gentle_cost_spend_only_replay`
- `linear_capped_cost`
- `linear_capped_cost_spend_only_replay`
- `linear_no_cost_diagnostic`

All three charged predictors improved forecast skill over their spend-only
replay null by `0.045425`. Work charges were matched within each positive/null
pair:

| contrast | charged work | remaining work | forecast-skill delta | final queue delta |
| --- | ---: | ---: | ---: | ---: |
| harsh cost minus spend-only replay | 4.0 | 11.0 | 0.045425 | 0.0 |
| gentle cost minus spend-only replay | 2.5 | 12.5 | 0.045425 | -0.5 |
| capped cost minus spend-only replay | 3.5 | 11.5 | 0.045425 | 0.0 |

Those forecast-skill gains did not become promotion-worthy residual structure.
The full-accounting residual predictability contrasts were:

| contrast | full-accounting delta | positive rate | status |
| --- | ---: | ---: | --- |
| harsh cost vs spend-only replay | -0.027 | 0.0 | lower endpoint outside interval |
| gentle cost vs spend-only replay | -0.402 | 0.0 | lower endpoint outside interval |
| capped cost vs spend-only replay | 0.021 | 0.5 | inside interval |

The A5.1a audit therefore reported:

| condition | skill vs replay null | residual vs replay null | guardrails vs replay null | promotion |
| --- | --- | --- | --- | --- |
| linear_harsh_cost | true | false | true | false |
| linear_gentle_cost | true | false | true | false |
| linear_capped_cost | true | false | true | false |

## Interpretation

The cost-calibration patch answered the immediate resource-bounded prediction
question conservatively. Intermediate prediction spend can buy forecast skill,
but in this single-hive scaffold the remaining residual differences are either
explained by work-charge/accounting controls or matched by the spend-only replay
null.

This is not evidence for structured strange-attractor-like dynamics, residual
lobe grammar, or promotion-worthy high-level collective states. Any such claim
would require a new preregistration and a mechanism that survives the
accounting/null gates prospectively.

## Boundary For Future Work

A5.1 should not be reopened by:

- adding broader seeds to the same A5.1a cost-calibration grid;
- adding more linear cost knobs to rescue the negative result;
- treating no-cost predictor diagnostics as promotion evidence;
- treating queue depth, completion fraction, or residual magnitude alone as
  structured-dynamics evidence;
- moving directly from these single-hive artifacts into three-hive coupling.

The next scientific step should be a Ben decision on whether to stop A5-family
work here or preregister a genuinely new delayed semantic/logistic or
multi-hive design with resource-bounded prediction costs and target/phase nulls.
