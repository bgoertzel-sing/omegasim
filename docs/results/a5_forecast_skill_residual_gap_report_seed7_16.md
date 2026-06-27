# A5 Forecast-Skill/Residual-Gap Diagnostic, Seeds 7..16

This read-only diagnostic uses the existing A5 confirmatory artifacts:

- `runs/a5_predictive_control_confirmatory_seed7_16_20260626/`
- `runs/a5_residual_accounting_confirmatory_seed7_16_20260626/`
- `docs/results/a5_confirmatory_seed7_16.md`
- `docs/results/a5_closure_note_seed7_16.md`

No simulations were rerun. No simulator mechanics, multi-hive coupling, real
LLM calls, dashboards, Lean, Slack, browser automation, Atomspace integration,
or external services were added.

External strategic review handling:

- `../outputs/strategy-reviews/omegasim/latest-review.md`
- `strategic_change_level: none`
- `notify_ben: false`
- Recommendation: strengthen the A6 analyzer before broadening A6.
- Deferred for this run: `AUTOMATION_STATUS.md` is currently the source of
  truth and its single next step is the A5 residual-gap report. The A6
  analyzer recommendation remains scientifically sensible after A5 closure.

## Decision

The gap is best explained by accounting-confirmed closure. A5 predictors
improve forecast skill under matched deterministic demand streams, but the
observable downstream differences are absorbed by load, action-opportunity,
and class work/completion accounting controls or fail the budget-matched null
comparison.

This report does not promote A5 and does not reopen the single-hive
predictive-control scaffold for new mechanics or larger seed sweeps.

## Forecast Skill Versus Allocation

The comparison aggregate shows the intended forecast manipulation:

| contrast | forecast-skill delta | future-allocation alignment delta | allocation residual abs delta | queue-depth delta |
| --- | ---: | ---: | ---: | ---: |
| linear minus reactive | 0.033517 | -0.007833 | 0.068591 | 0.4 |
| linear minus shuffled | 0.045425 | 0.027497 | -0.032554 | 0.5 |
| nonlinear minus reactive | 0.084033 | 0.020151 | 0.102352 | 1.0 |
| nonlinear minus nonlinear_shuffled | 0.095941 | 0.055481 | 0.001207 | 1.1 |
| oracle minus nonlinear | 0.038010 | -0.007971 | -0.039349 | -0.4 |

The forecast-skill signal is real within this scaffold, but it does not map
cleanly to a stronger residual collective-state signal. The two intermediate
predictors improve forecast skill while slightly worsening or failing to
improve completion fraction and queue depth. The linear and nonlinear
budget-matched shuffled contrasts also show that timing advantage is not
enough to produce promotion-worthy residual dynamics.

## Accounting Control Audit

Primary residual-state predictability does not survive the preregistered
full-accounting gate:

| contrast | raw r2 delta | load/opportunity r2 delta | full-accounting r2 delta | full-accounting status |
| --- | ---: | ---: | ---: | --- |
| linear minus reactive | -0.052386 | -0.149921 | 0.114949 | inside interval |
| linear minus shuffled | -0.198367 | 0.057851 | -0.053977 | inside interval |
| nonlinear minus reactive | -0.244945 | -0.128446 | 0.077593 | inside interval |
| nonlinear minus nonlinear_shuffled | -0.390926 | 0.079326 | -0.091333 | inside interval |
| oracle minus nonlinear | 0.076291 | 0.002262 | 0.122901 | inside interval |

Allocation-future residuals also clarify the mechanism. Raw and clock-demand
levels contain detectable allocation differences, but the residual endpoint is
zeroed by the `load_opportunity` and `full_accounting` levels for all listed
promotion-relevant contrasts. This supports the explanation that forecast
effects are mediated through ordinary demand, queue, action-opportunity, and
class accounting fields rather than through an independent residual lobe
grammar.

## Candidate Explanations

| candidate | diagnostic result |
| --- | --- |
| Predictors forecast demand, but fixed work budget limits conversion into distinct collective trajectories. | Supported. Forecast skill improves, but completion and queue guardrails do not improve and sometimes degrade. |
| Full-accounting controls absorb apparent structure. | Supported. The primary full-accounting `residual_state_predictability_r2` contrasts remain inside paired label-permutation intervals. |
| Endpoint too coarse or too queue-coupled. | Plausible but not actionable without a new preregistration. No analyzer bug is evident from the current artifacts. |
| Budget-matched shuffled nulls preserve enough marginal forecast shape. | Supported. Intermediate predictors beat shuffled controls on forecast skill, but not on the full-accounting residual gate. |
| Oracle smoothing reduces residual dynamics while intermediate predictors do not create a distinct regime. | Partly supported. Oracle improves forecast skill over nonlinear, but its full-accounting residual predictability contrast is also inside interval. |

## Conclusion

A5 should remain closed. The scientifically defensible claim is narrow:
bounded predictors improved forecast skill in a deterministic single-hive
fixture. They did not create residual structured dynamics that survive
load/opportunity/accounting controls and budget-matched timing-broken nulls.

The next coherent non-A5 step is the already accepted A6 analysis gate:
strengthen the read-only A6 analyzer with paired accounting, residual, and
null-control deltas before any broader A6 simulation or promotion claim.
