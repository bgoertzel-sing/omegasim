# A6 Matched-Excess Smoke Result, Seeds 1-2

Date: 2026-07-01.

Status: bounded smoke-scale result note for the reopened A6
thresholded-appraisal path. This note documents the matched excess-over-control
candidate gate only. It does not add simulator mechanics, broaden seeds, rerun
A5/A7/analytic-map work, add dashboards or integrations, or support promotion
language.

## Inputs

Fresh verification used the checked-in four-condition A6 smoke comparison and
read-only analyzer:

```bash
.venv-conda/bin/python -m ohdyn.compare_a6_logistic_appraisal \
  --seeds 1 2 \
  --out /tmp/omegasim_a6_matched_excess_compare_seed1_2

.venv-conda/bin/python -m ohdyn.analyze_a6_logistic_appraisal \
  --compare-dir /tmp/omegasim_a6_matched_excess_compare_seed1_2 \
  --out /tmp/omegasim_a6_matched_excess_analysis_seed1_2
```

The analyzer consumed eight run artifacts: four conditions crossed with seeds
`1` and `2`.

```text
logistic
linear
phase_shuffled
threshold_shuffled
```

The run was read-only after simulation generation into `/tmp`; the analyzer
did not rerun simulations.

## Functional Candidate Gate

The `a6_functional_candidate_gate.csv` smoke result was:

| condition | candidate_rate | mean_artifact_maturity_delta | mean_provenance_debt_delta | mean_risk_delta | mean_prediction_error_abs_delta | mean_functional_score | gate_status |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| `linear` | 1.0 | 0.180899 | -0.410000 | -0.240000 | 0.083646 | 0.747252 | `control_candidate_rate_reported` |
| `logistic` | 1.0 | 0.180899 | -0.410000 | -0.240000 | 0.074428 | 0.756471 | `fail_closed_controls_match_or_exceed` |
| `phase_shuffled` | 1.0 | 0.042172 | -0.360000 | -0.240000 | 0.101893 | 0.540278 | `control_candidate_rate_reported` |
| `threshold_shuffled` | 1.0 | 0.140699 | -0.405000 | -0.240000 | 0.097438 | 0.688260 | `control_candidate_rate_reported` |

The logistic row selected `linear` as the matched control. Both logistic and
linear had two candidate seeds out of two:

```text
logistic candidate_rate: 1.0
matched_control_condition: linear
matched_control_candidate_rate: 1.0
matched_excess_candidate_rate: 0.0
matched_excess_role_nonperiodic_rate: 0.0
matched_excess_functional_movement_rate: 0.0
matched_excess_bounded_unsaturated_rate: 0.0
matched_excess_artifact_maturity_delta: 0.0
matched_excess_provenance_debt_improvement: 0.0
matched_excess_risk_improvement: 0.0
matched_excess_prediction_error_abs_improvement: 0.009219
matched_excess_functional_score: 0.009219
```

## Interpretation

The gate closes conservatively. At seed `1,2` smoke scale, the logistic
thresholded-appraisal condition does not produce excess candidate status over
the amplitude-matched linear control. Logistic has a small matched excess on
prediction-error improvement and functional score, but the candidate-rate and
core component rates are tied with the matched control. Phase-shuffled and
threshold-shuffled controls also pass the simple candidate-count screen.

This is a useful wiring and analysis result, not evidence for A6 promotion.
The current A6 model should not be described as demonstrating lobe dynamics,
structured attractors, semantic dynamics, or accounting-robust collective
intelligence. The scientifically sensible GPT-5.5-Pro recommendation to center
matched controls and fail-closed interpretation is accepted here: controls
match or exceed the candidate-count screen, so the result is a refinement or
closure signal rather than a positive finding.

## Boundary

Do not respond to this result by broadening seeds, adding downstream
multi-hive coupling, adding external integrations, or promoting from raw role
switching. Any next A6 work should be separately preregistered and should
explain how it will create functional artifact/debt/risk/prediction-error
movement that exceeds amplitude-matched linear and shuffled controls.
