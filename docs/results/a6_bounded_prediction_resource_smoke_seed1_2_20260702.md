# A6 Bounded Prediction-Resource Smoke Result

Date: 2026-07-02.

Status: fail-closed smoke/accounting result; no promotion language.

## Scope

This note records one tiny paired-seed A6 bounded prediction-resource smoke
authorized by `AUTOMATION_STATUS.md` after the 2026-07-02 GPT-5.5-Pro major
review pivot away from a dense A6 phase diagram.

Commands run:

```bash
.venv-conda/bin/python -m ohdyn.compare_a6_logistic_appraisal \
  --seeds 1 2 \
  --include-bounded-resource-replay \
  --out /tmp/omegasim_a6_bounded_resource_compare_seed1_2

.venv-conda/bin/python -m ohdyn.analyze_a6_logistic_appraisal \
  --compare-dir /tmp/omegasim_a6_bounded_resource_compare_seed1_2 \
  --out /tmp/omegasim_a6_bounded_resource_analysis_seed1_2
```

The smoke used the checked-in deterministic A6 fixtures plus derived
schema/control artifact conditions. It did not add simulator mechanics, run a
dense phase diagram, broaden seeds, rerun A5/A7/analytic gates, add external
integrations, or use downstream multi-hive coupling.

## Observed Resource Surface

The analyzer observed all fixed bounded-resource labels:

```text
amplitude_matched_linear_prediction
budget_matched_prediction_replay
high_oracle_budget_smoothing_comparator
intermediate_budget_delayed_logistic
phase_shuffled_delayed_signal
role_or_agent_shuffled_appraisal
threshold_shuffled_thresholds
zero_budget_reactive
```

The resource summary for the logistic/intermediate condition reported:

```text
seed_count=2
missing_resource_conditions=none
budget_matched_replay_control_status=present
mean_confound_r2=0.995713
residual_recurrence_excess_vs_linear=-0.120242
residual_compression_excess_vs_linear=-0.5
nonlinear_vs_linear_forecast_delta=0.009219
budget_efficiency_per_prediction_spend=1.242752
budget_efficiency_per_work_opportunity_sacrificed=0.001338
gate_status=schema_ready_requires_preregistered_result_run
```

The functional candidate gate remained fail-closed:

```text
logistic candidate_rate=1.0
matched_control_condition=budget_matched_prediction_replay
matched_control_candidate_rate=1.0
matched_excess_candidate_rate=0.0
matched_excess_role_nonperiodic_rate=0.0
matched_excess_functional_movement_rate=0.0
matched_excess_bounded_unsaturated_rate=0.0
matched_excess_artifact_maturity_delta=0.0
matched_excess_provenance_debt_improvement=-0.02
matched_excess_risk_improvement=0.0
matched_excess_prediction_error_abs_improvement=-0.07518
matched_excess_functional_score=-0.09518
gate_status=fail_closed_controls_match_or_exceed
```

The direct comparison effects also failed to support the intermediate
resource candidate. Logistic did not improve artifact utility against the
budget-matched replay, zero-budget, high/oracle, or role/agent-shuffled
resource controls. The zero-budget and role/agent-shuffled controls matched
the logistic candidate on the smoke-scale utility surface, while the replay
control exceeded it on the functional score used by the candidate gate.

## Interpretation Boundary

This smoke validates that the fixed bounded-resource labels and replay control
can be emitted and analyzed for paired seeds `1,2`. It does not establish a
bounded prediction-resource mechanism, residual recurrence, lobe dynamics,
semantic dynamics, or strange-attractor-like behavior.

Because the matched replay control was selected as the matched control and
matched/exceeded the logistic candidate on the preregistered smoke gate, this
bounded A6 slice closes conservatively at the current derived-control boundary.
The accepted GPT-5.5-Pro direction shift remains in force: do not run the
dense A6 phase diagram as a rescue.

## Next Step

Make one bounded decision note choosing whether to stop A6 current-model work
again or preregister a stricter implementation gate with real, non-derived
prediction-budget mechanics before any further result-bearing runs.
