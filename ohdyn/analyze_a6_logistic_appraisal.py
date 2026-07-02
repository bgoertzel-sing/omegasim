"""Read A6 logistic-appraisal artifacts and emit gate-control outputs."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path
from typing import Any

import yaml


DEFAULT_A6_COMPARE_DIR = Path("runs/a6_logistic_appraisal_compare")
DEFAULT_A6_ANALYSIS_OUT_DIR = Path("runs/a6_logistic_appraisal_analysis")
A6_REQUIRED_CONDITIONS = (
    "logistic",
    "linear",
    "threshold_shuffled",
    "phase_shuffled",
)
A6_ANALYSIS_CONTROL_LEVELS = (
    "load_service_action_opportunity",
    "clock_queue_residualized",
    "amplitude_matched_linear",
    "phase_shuffled",
    "threshold_shuffled",
    "source_label_shuffled_within_tick",
    "handoff_success_timing_broken_matched_counts",
    "budget_matched_prediction_replay",
    "paired_seed_uncertainty",
    "promotion_closure_rules",
)
A6_ANALYSIS_MANIFEST_FIELDS = (
    "control_level",
    "compare_dir",
    "condition_count",
    "seed_count",
    "status",
)
A6_ANALYSIS_ENDPOINT_FIELDS = (
    "condition",
    "seed",
    "tick_count",
    "final_latent_activation_mean",
    "final_latent_focus_mean",
    "final_latent_fatigue_mean",
    "final_latent_prediction_error_abs_mean",
    "final_artifact_novelty",
    "final_artifact_coherence",
    "final_artifact_actionability",
    "final_artifact_provenance_debt",
    "final_artifact_risk",
    "final_artifact_contradiction",
    "final_artifact_readiness",
    "final_artifact_implementation_maturity",
    "final_artifact_communication_maturity",
    "final_artifact_utility",
    "handoff_attempts_total",
    "handoff_successes_total",
    "handoff_failures_total",
    "prediction_budget_spent_total",
    "tasks_created_total",
    "tasks_completed_total",
    "tasks_worked_total",
    "messages_sent_total",
    "completion_fraction",
    "queue_depth",
    "queue_delta_tick",
    "queued_task_age_mean_final",
    "action_opportunity_total",
    "idle_total",
    "message_total",
    "create_task_total",
    "work_task_total",
    "synthesize_total",
    "review_total",
    "formalize_total",
    "maintain_total",
    "predict_total",
    "communicate_total",
    "pause_total",
)
A6_CONTROL_DELTA_FIELDS = (
    "contrast",
    "seed",
    "control_condition",
    "paired",
    "missing_required_fields",
    *(
        f"{field}_delta"
        for field in A6_ANALYSIS_ENDPOINT_FIELDS
        if field not in {"condition", "seed"}
    ),
)
A6_CONTROL_SUMMARY_FIELDS = (
    "contrast",
    "control_condition",
    "outcome_field",
    "paired_seed_count",
    "missing_required_fields",
    "residual_status",
    "mean_raw_variance_delta",
    "mean_residual_variance_delta",
    "mean_raw_lag1_autocorrelation_delta",
    "mean_residual_lag1_autocorrelation_delta",
    "mean_final_artifact_utility_delta",
    "mean_queue_depth_delta",
    "mean_action_opportunity_total_delta",
    "mean_completion_fraction_delta",
    "interpretation",
)
A6_RESIDUAL_PREFLIGHT_FIELDS = (
    "condition",
    "seed",
    "outcome_field",
    "row_count",
    "control_count",
    "degrees_of_freedom",
    "status",
    "missing_control_fields",
    "control_fields_used",
    "raw_variance",
    "residual_variance",
    "raw_lag1_autocorrelation",
    "residual_lag1_autocorrelation",
)
A6_RESIDUAL_TIMESERIES_FIELDS = (
    "condition",
    "seed",
    "tick",
    "outcome_field",
    "status",
    "missing_control_fields",
    "control_fields_used",
    "raw_value",
    "fitted_value",
    "residual_value",
)
A6_RESIDUAL_CONTRAST_SUMMARY_FIELDS = (
    "contrast",
    "seed",
    "control_condition",
    "outcome_field",
    "paired",
    "status",
    "tick_count",
    "control_tick_count",
    "logistic_residual_variance",
    "control_residual_variance",
    "residual_variance_delta",
    "logistic_residual_lag1_autocorrelation",
    "control_residual_lag1_autocorrelation",
    "residual_lag1_autocorrelation_delta",
    "logistic_residual_sign_change_count",
    "control_residual_sign_change_count",
    "residual_sign_change_count_delta",
    "interpretation",
)
A6_RESIDUAL_CONTRAST_ROLLUP_FIELDS = (
    "contrast",
    "control_condition",
    "outcome_field",
    "paired_seed_count",
    "complete_seed_count",
    "incomplete_seed_count",
    "status",
    "statuses_observed",
    "seeds_included",
    "mean_residual_variance_delta",
    "residual_variance_delta_positive_count",
    "residual_variance_delta_negative_count",
    "residual_variance_delta_zero_count",
    "residual_variance_direction_agreement",
    "mean_residual_lag1_autocorrelation_delta",
    "residual_lag1_autocorrelation_delta_positive_count",
    "residual_lag1_autocorrelation_delta_negative_count",
    "residual_lag1_autocorrelation_delta_zero_count",
    "residual_lag1_autocorrelation_direction_agreement",
    "mean_residual_sign_change_count_delta",
    "residual_sign_change_count_delta_positive_count",
    "residual_sign_change_count_delta_negative_count",
    "residual_sign_change_count_delta_zero_count",
    "residual_sign_change_count_direction_agreement",
    "interpretation",
)
A6_COMPARISON_CONSISTENCY_FIELDS = (
    "condition",
    "comparison_csv_path",
    "status",
    "expected_seed_count",
    "observed_seed_count",
    "expected_run_count",
    "observed_run_count",
    "fields_checked",
    "max_abs_difference",
    "mismatched_fields",
    "missing_comparison_fields",
    "interpretation",
)
A6_EFFECTS_CONSISTENCY_FIELDS = (
    "effect_axis",
    "effects_csv_path",
    "status",
    "low_label",
    "high_label",
    "fields_checked",
    "max_abs_difference",
    "mismatched_fields",
    "missing_effect_fields",
    "missing_comparison_conditions",
    "interpretation",
)
A6_ARTIFACT_PROVENANCE_FIELDS = (
    "condition",
    "seed",
    "artifact_field",
    "tick_count",
    "changed_tick_count",
    "total_abs_delta",
    "signed_delta_sum",
    "abs_delta_on_handoff_success_ticks",
    "abs_delta_on_handoff_failure_ticks",
    "abs_delta_on_handoff_attempt_ticks",
    "abs_delta_on_artifact_update_ticks",
    "abs_delta_on_no_a6_event_ticks",
    "handoff_success_event_count",
    "handoff_failure_event_count",
    "handoff_attempt_event_count",
    "artifact_update_event_count",
    "dominant_event_source",
    "dominant_event_delta_share",
    "action_handoff_total",
    "action_predict_total",
    "action_work_task_total",
    "action_create_task_total",
    "action_message_total",
    "action_total",
    "dominant_action_source",
    "dominant_action_share",
    "alias_risk",
    "interpretation",
)
A6_SOURCE_ACCOUNTING_FIELDS = (
    "condition",
    "seed",
    "artifact_field",
    "update_event_count",
    "required_field_status",
    "missing_required_fields",
    "reconstruction_status",
    "max_abs_reconstruction_residual",
    "signed_delta_sum",
    "total_abs_delta",
    "ambient_abs_delta",
    "ambient_share",
    "handoff_attempt_abs_delta",
    "handoff_attempt_share",
    "handoff_success_abs_delta",
    "handoff_success_share",
    "handoff_failure_abs_delta",
    "handoff_failure_share",
    "prediction_expenditure_abs_delta",
    "prediction_expenditure_share",
    "prediction_error_abs_delta",
    "prediction_error_share",
    "queue_work_accounting_abs_delta",
    "queue_work_accounting_share",
    "noise_abs_delta",
    "noise_share",
    "clip_residual_abs_delta",
    "clip_residual_share",
    "dominant_source",
    "dominant_source_share",
    "handoff_success_alias_share",
    "prediction_expenditure_alias_share",
    "queue_work_alias_share",
    "status",
    "interpretation",
)
A6_1_PILOT_NULL_GATE_FIELDS = (
    "contrast",
    "seed",
    "endpoint",
    "paired",
    "logistic_value",
    "control_value",
    "logistic_minus_control_delta",
    "logistic_backlog_adjusted_productivity",
    "control_backlog_adjusted_productivity",
    "backlog_adjusted_productivity_delta",
    "logistic_required_field_status",
    "control_required_field_status",
    "logistic_reconstruction_status",
    "control_reconstruction_status",
    "logistic_handoff_success_alias_share",
    "control_handoff_success_alias_share",
    "residual_status",
    "gate_status",
    "interpretation",
)
A6_FUNCTIONAL_CANDIDATE_GATE_FIELDS = (
    "condition",
    "seed_count",
    "role_nonperiodic_seed_count",
    "functional_movement_seed_count",
    "bounded_unsaturated_seed_count",
    "candidate_seed_count",
    "candidate_rate",
    "mean_artifact_maturity_delta",
    "mean_provenance_debt_delta",
    "mean_risk_delta",
    "mean_prediction_error_abs_delta",
    "mean_functional_score",
    "matched_control_condition",
    "matched_control_seed_count",
    "matched_control_candidate_seed_count",
    "matched_control_candidate_rate",
    "matched_excess_candidate_rate",
    "matched_excess_role_nonperiodic_rate",
    "matched_excess_functional_movement_rate",
    "matched_excess_bounded_unsaturated_rate",
    "matched_excess_artifact_maturity_delta",
    "matched_excess_provenance_debt_improvement",
    "matched_excess_risk_improvement",
    "matched_excess_prediction_error_abs_improvement",
    "matched_excess_functional_score",
    "gate_status",
    "interpretation",
)
A6_BOUNDED_PREDICTION_RESOURCE_FIELDS = (
    "condition",
    "resource_gate_condition",
    "seed_count",
    "observed_resource_conditions",
    "missing_resource_conditions",
    "primary_residual_vector_fields",
    "control_fields_used",
    "mean_confound_r2",
    "residual_recurrence_excess_vs_linear",
    "residual_compression_excess_vs_linear",
    "nonlinear_vs_linear_forecast_delta",
    "budget_efficiency_per_prediction_spend",
    "budget_efficiency_per_work_opportunity_sacrificed",
    "budget_matched_replay_control_status",
    "gate_status",
    "interpretation",
)
_OUTPUT_NAMES = (
    "a6_logistic_appraisal_endpoints.csv",
    "a6_logistic_appraisal_manifest.csv",
    "a6_logistic_appraisal_control_deltas.csv",
    "a6_logistic_appraisal_control_summary.csv",
    "a6_logistic_appraisal_residual_preflight.csv",
    "a6_logistic_appraisal_residual_timeseries.csv",
    "a6_logistic_appraisal_residual_contrast_summary.csv",
    "a6_logistic_appraisal_residual_contrast_rollup.csv",
    "a6_logistic_appraisal_comparison_consistency.csv",
    "a6_logistic_appraisal_effects_consistency.csv",
    "a6_logistic_appraisal_artifact_provenance.csv",
    "a6_logistic_appraisal_source_accounting.csv",
    "a6_1_pilot_null_gate.csv",
    "a6_functional_candidate_gate.csv",
    "a6_bounded_prediction_resource_residual_state_summary.csv",
    "summary.md",
)
_A6_CONTROL_PAIRS = (
    ("logistic_vs_linear", "linear"),
    ("logistic_vs_phase_shuffled", "phase_shuffled"),
    ("logistic_vs_threshold_shuffled", "threshold_shuffled"),
    ("logistic_vs_source_label_shuffled_within_tick", "source_label_shuffled_within_tick"),
    (
        "logistic_vs_handoff_success_timing_broken_matched_counts",
        "handoff_success_timing_broken_matched_counts",
    ),
    (
        "logistic_vs_budget_matched_prediction_replay",
        "budget_matched_prediction_replay",
    ),
)
_A6_1_SOURCE_NULL_CONDITIONS = (
    "source_label_shuffled_within_tick",
    "handoff_success_timing_broken_matched_counts",
)
_A6_OPTIONAL_DERIVED_CONTROL_CONDITIONS = (
    *_A6_1_SOURCE_NULL_CONDITIONS,
    "budget_matched_prediction_replay",
)
_A6_1_PILOT_ENDPOINTS = (
    ("final_artifact_readiness", "a6_artifact_readiness_tick"),
    ("final_artifact_utility", "a6_artifact_utility_tick"),
)
_A6_REQUIRED_CONTROL_FIELDS = (
    "tick",
    "queue_depth",
    "queue_delta_tick",
    "tasks_created_total",
    "tasks_completed_total",
    "tasks_worked_tick",
    "messages_sent_tick",
    "a6_prediction_budget_spent_tick",
    "a6_latent_activation_mean_tick",
    "a6_latent_focus_mean_tick",
    "a6_latent_fatigue_mean_tick",
    "a6_latent_prediction_error_mean_tick",
    "a6_artifact_readiness_tick",
    "a6_handoff_attempts_tick",
    "a6_handoff_successes_tick",
    "a6_handoff_failures_tick",
)
_A6_RESIDUAL_OUTCOME_FIELDS = (
    "a6_latent_activation_mean_tick",
    "a6_latent_focus_mean_tick",
    "a6_latent_fatigue_mean_tick",
    "a6_latent_prediction_error_mean_tick",
    "a6_artifact_novelty_tick",
    "a6_artifact_coherence_tick",
    "a6_artifact_actionability_tick",
    "a6_artifact_provenance_debt_tick",
    "a6_artifact_risk_tick",
    "a6_artifact_contradiction_tick",
    "a6_artifact_readiness_tick",
    "a6_artifact_implementation_maturity_tick",
    "a6_artifact_communication_maturity_tick",
    "a6_artifact_utility_tick",
)
_A6_BOUNDED_RESOURCE_REQUIRED_CONDITIONS = (
    "zero_budget_reactive",
    "intermediate_budget_delayed_logistic",
    "high_oracle_budget_smoothing_comparator",
    "amplitude_matched_linear_prediction",
    "phase_shuffled_delayed_signal",
    "threshold_shuffled_thresholds",
    "budget_matched_prediction_replay",
    "role_or_agent_shuffled_appraisal",
)
_A6_BOUNDED_RESOURCE_CONDITION_MAP = {
    "logistic": "intermediate_budget_delayed_logistic",
    "linear": "amplitude_matched_linear_prediction",
    "phase_shuffled": "phase_shuffled_delayed_signal",
    "threshold_shuffled": "threshold_shuffled_thresholds",
    "source_label_shuffled_within_tick": "role_or_agent_shuffled_appraisal",
    "budget_matched_prediction_replay": "budget_matched_prediction_replay",
}
_A6_BOUNDED_RESOURCE_PRIMARY_VECTOR_FIELDS = (
    "a6_artifact_readiness_tick",
    "a6_artifact_provenance_debt_tick",
    "a6_artifact_risk_tick",
    "a6_prediction_budget_spent_tick",
    "a6_latent_prediction_error_mean_tick",
    "a6_latent_fatigue_mean_tick",
)
_A6_ARTIFACT_AUDIT_FIELDS = (
    "a6_artifact_novelty_tick",
    "a6_artifact_coherence_tick",
    "a6_artifact_actionability_tick",
    "a6_artifact_provenance_debt_tick",
    "a6_artifact_risk_tick",
    "a6_artifact_contradiction_tick",
    "a6_artifact_readiness_tick",
    "a6_artifact_implementation_maturity_tick",
    "a6_artifact_communication_maturity_tick",
    "a6_artifact_utility_tick",
)
_A6_EVENT_SOURCE_FIELDS = (
    "a6_artifact_update_source",
    "a6_artifact_field",
    "a6_artifact_delta_total",
    "a6_artifact_delta_ambient",
    "a6_artifact_delta_handoff_attempt",
    "a6_artifact_delta_handoff_success",
    "a6_artifact_delta_handoff_failure",
    "a6_artifact_delta_prediction_expenditure",
    "a6_artifact_delta_prediction_error",
    "a6_artifact_delta_queue_work_accounting",
    "a6_artifact_delta_noise",
    "a6_artifact_delta_unclipped",
    "a6_artifact_delta_clip_residual",
)
_A6_METRIC_SOURCE_REQUIRED_FIELDS = (
    "a6_prediction_budget_available_tick",
    "a6_prediction_budget_spent_tick",
    "a6_prediction_actions_tick",
    "a6_prediction_error_mean_tick",
    "a6_handoff_attempts_tick",
    "a6_handoff_successes_tick",
    "a6_handoff_failures_tick",
    "a6_queue_depth_tick",
    "a6_work_actions_tick",
    "a6_action_opportunity_tick",
    "a6_service_capacity_tick",
)
_A6_SOURCE_DELTA_FIELDS = (
    ("ambient", "a6_artifact_delta_ambient"),
    ("handoff_attempt", "a6_artifact_delta_handoff_attempt"),
    ("handoff_success", "a6_artifact_delta_handoff_success"),
    ("handoff_failure", "a6_artifact_delta_handoff_failure"),
    ("prediction_expenditure", "a6_artifact_delta_prediction_expenditure"),
    ("prediction_error", "a6_artifact_delta_prediction_error"),
    ("queue_work_accounting", "a6_artifact_delta_queue_work_accounting"),
    ("noise", "a6_artifact_delta_noise"),
)
_A6_EVENT_FIELD_TO_METRIC_FIELD = {
    "artifact_novelty": "a6_artifact_novelty_tick",
    "artifact_coherence": "a6_artifact_coherence_tick",
    "artifact_actionability": "a6_artifact_actionability_tick",
    "artifact_provenance_debt": "a6_artifact_provenance_debt_tick",
    "artifact_risk": "a6_artifact_risk_tick",
    "artifact_contradiction": "a6_artifact_contradiction_tick",
    "artifact_readiness": "a6_artifact_readiness_tick",
    "artifact_implementation_maturity": "a6_artifact_implementation_maturity_tick",
    "artifact_communication_maturity": "a6_artifact_communication_maturity_tick",
}
_A6_UTILITY_FIELD_WEIGHTS = {
    "artifact_coherence": 0.2,
    "artifact_actionability": 0.2,
    "artifact_provenance_debt": -0.2,
    "artifact_risk": -0.2,
    "artifact_contradiction": -0.2,
    "artifact_readiness": 0.2,
    "artifact_implementation_maturity": 0.2,
    "artifact_communication_maturity": 0.2,
}
_A6_RESIDUAL_BASE_CONTROL_FIELDS = (
    "tick",
    "queue_depth",
    "queue_delta_tick",
    "tasks_created_total",
    "tasks_completed_total",
    "tasks_worked_tick",
    "messages_sent_tick",
    "a6_prediction_budget_spent_tick",
)
_A6_ACTIONS = (
    "idle",
    "message",
    "create_task",
    "work_task",
    "synthesize",
    "review",
    "formalize",
    "maintain",
    "predict",
    "communicate",
    "pause",
)
_A6_HANDOFF_ACTIONS = (
    "synthesize",
    "review",
    "formalize",
    "maintain",
    "communicate",
)
_A6_COMPARISON_METRICS_NAME = "a6_logistic_appraisal_comparison_metrics.csv"
_A6_EFFECTS_NAME = "a6_logistic_appraisal_effects.csv"
_A6_COMPARISON_MEAN_FIELD_MAP = {
    "final_latent_activation_mean": "final_latent_activation_mean",
    "final_latent_focus_mean": "final_latent_focus_mean",
    "final_latent_fatigue_mean": "final_latent_fatigue_mean",
    "final_latent_prediction_error_abs_mean": "final_latent_prediction_error_abs_mean",
    "final_artifact_readiness_mean": "final_artifact_readiness",
    "final_artifact_utility_mean": "final_artifact_utility",
    "handoff_attempts_total_mean": "handoff_attempts_total",
    "handoff_successes_total_mean": "handoff_successes_total",
    "handoff_failures_total_mean": "handoff_failures_total",
    "prediction_budget_spent_total_mean": "prediction_budget_spent_total",
    "tasks_created_mean": "tasks_created_total",
    "tasks_completed_mean": "tasks_completed_total",
    "completion_fraction_mean": "completion_fraction",
    "queue_depth_mean": "queue_depth",
    "queued_task_age_mean_final_mean": "queued_task_age_mean_final",
}
_A6_EFFECT_DELTA_FIELDS = (
    "final_latent_activation_mean_delta",
    "final_latent_fatigue_mean_delta",
    "final_latent_prediction_error_abs_mean_delta",
    "final_artifact_readiness_mean_delta",
    "final_artifact_utility_mean_delta",
    "handoff_successes_total_mean_delta",
    "handoff_failures_total_mean_delta",
    "prediction_budget_spent_total_mean_delta",
    "completion_fraction_mean_delta",
    "queue_depth_mean_delta",
    "queued_task_age_mean_final_mean_delta",
)
_A6_COMPARISON_CONSISTENCY_TOLERANCE = 1e-6


def run_a6_logistic_appraisal_analysis(
    compare_dir: str | Path = DEFAULT_A6_COMPARE_DIR,
    out_dir: str | Path = DEFAULT_A6_ANALYSIS_OUT_DIR,
) -> dict[str, Any]:
    compare_path = Path(compare_dir)
    output_path = Path(out_dir)
    _ensure_output_paths_available(output_path)
    runs, missing_required_fields = _read_a6_runs(compare_path)
    conditions = sorted({str(run["condition"]) for run in runs})
    seeds = sorted({int(run["seed"]) for run in runs})
    control_delta_rows = _control_delta_rows(runs, missing_required_fields)
    residual_preflight_rows = _residual_preflight_rows(compare_path)
    residual_timeseries_rows = _residual_timeseries_rows(compare_path)
    residual_contrast_summary_rows = _residual_contrast_summary_rows(
        residual_timeseries_rows
    )
    residual_contrast_rollup_rows = _residual_contrast_rollup_rows(
        residual_contrast_summary_rows
    )
    control_summary_rows = _control_summary_rows(
        control_delta_rows,
        residual_preflight_rows,
        missing_required_fields,
    )
    comparison_consistency_rows = _comparison_consistency_rows(compare_path, runs)
    effects_consistency_rows = _effects_consistency_rows(compare_path)
    artifact_provenance_rows = _artifact_provenance_rows(compare_path)
    source_accounting_rows = _source_accounting_rows(compare_path)
    pilot_null_gate_rows = _a6_1_pilot_null_gate_rows(
        runs,
        source_accounting_rows,
        residual_contrast_rollup_rows,
    )
    functional_candidate_gate_rows = _functional_candidate_gate_rows(compare_path)
    bounded_prediction_resource_rows = _bounded_prediction_resource_rows(
        runs,
        residual_preflight_rows,
        residual_contrast_rollup_rows,
    )
    manifest_rows = [
        {
            "control_level": control_level,
            "compare_dir": str(compare_path),
            "condition_count": len(conditions),
            "seed_count": len(seeds),
            "status": _control_level_status(
                control_level,
                control_delta_rows,
                missing_required_fields,
                residual_preflight_rows,
                control_summary_rows,
            ),
        }
        for control_level in A6_ANALYSIS_CONTROL_LEVELS
    ]

    output_path.mkdir(parents=True, exist_ok=True)
    _write_csv(
        output_path / "a6_logistic_appraisal_endpoints.csv",
        runs,
        A6_ANALYSIS_ENDPOINT_FIELDS,
    )
    _write_csv(
        output_path / "a6_logistic_appraisal_manifest.csv",
        manifest_rows,
        A6_ANALYSIS_MANIFEST_FIELDS,
    )
    _write_csv(
        output_path / "a6_logistic_appraisal_control_deltas.csv",
        control_delta_rows,
        A6_CONTROL_DELTA_FIELDS,
    )
    _write_csv(
        output_path / "a6_logistic_appraisal_control_summary.csv",
        control_summary_rows,
        A6_CONTROL_SUMMARY_FIELDS,
    )
    _write_csv(
        output_path / "a6_logistic_appraisal_residual_preflight.csv",
        residual_preflight_rows,
        A6_RESIDUAL_PREFLIGHT_FIELDS,
    )
    _write_csv(
        output_path / "a6_logistic_appraisal_residual_timeseries.csv",
        residual_timeseries_rows,
        A6_RESIDUAL_TIMESERIES_FIELDS,
    )
    _write_csv(
        output_path / "a6_logistic_appraisal_residual_contrast_summary.csv",
        residual_contrast_summary_rows,
        A6_RESIDUAL_CONTRAST_SUMMARY_FIELDS,
    )
    _write_csv(
        output_path / "a6_logistic_appraisal_residual_contrast_rollup.csv",
        residual_contrast_rollup_rows,
        A6_RESIDUAL_CONTRAST_ROLLUP_FIELDS,
    )
    _write_csv(
        output_path / "a6_logistic_appraisal_comparison_consistency.csv",
        comparison_consistency_rows,
        A6_COMPARISON_CONSISTENCY_FIELDS,
    )
    _write_csv(
        output_path / "a6_logistic_appraisal_effects_consistency.csv",
        effects_consistency_rows,
        A6_EFFECTS_CONSISTENCY_FIELDS,
    )
    _write_csv(
        output_path / "a6_logistic_appraisal_artifact_provenance.csv",
        artifact_provenance_rows,
        A6_ARTIFACT_PROVENANCE_FIELDS,
    )
    _write_csv(
        output_path / "a6_logistic_appraisal_source_accounting.csv",
        source_accounting_rows,
        A6_SOURCE_ACCOUNTING_FIELDS,
    )
    _write_csv(
        output_path / "a6_1_pilot_null_gate.csv",
        pilot_null_gate_rows,
        A6_1_PILOT_NULL_GATE_FIELDS,
    )
    _write_csv(
        output_path / "a6_functional_candidate_gate.csv",
        functional_candidate_gate_rows,
        A6_FUNCTIONAL_CANDIDATE_GATE_FIELDS,
    )
    _write_csv(
        output_path / "a6_bounded_prediction_resource_residual_state_summary.csv",
        bounded_prediction_resource_rows,
        A6_BOUNDED_PREDICTION_RESOURCE_FIELDS,
    )
    (output_path / "summary.md").write_text(
        _summary(
            compare_path,
            runs,
            manifest_rows,
            control_delta_rows,
            residual_preflight_rows,
            residual_timeseries_rows,
            residual_contrast_summary_rows,
            residual_contrast_rollup_rows,
            control_summary_rows,
            comparison_consistency_rows,
            effects_consistency_rows,
            artifact_provenance_rows,
            source_accounting_rows,
            pilot_null_gate_rows,
            functional_candidate_gate_rows,
            bounded_prediction_resource_rows,
            missing_required_fields,
        )
    )
    return {
        "compare_dir": str(compare_path),
        "out_dir": str(output_path),
        "condition_count": len(conditions),
        "seed_count": len(seeds),
        "run_count": len(runs),
        "control_delta_count": len(control_delta_rows),
        "control_summary_count": len(control_summary_rows),
        "residual_preflight_count": len(residual_preflight_rows),
        "residual_timeseries_count": len(residual_timeseries_rows),
        "residual_contrast_summary_count": len(residual_contrast_summary_rows),
        "residual_contrast_rollup_count": len(residual_contrast_rollup_rows),
        "comparison_consistency_count": len(comparison_consistency_rows),
        "effects_consistency_count": len(effects_consistency_rows),
        "artifact_provenance_count": len(artifact_provenance_rows),
        "source_accounting_count": len(source_accounting_rows),
        "a6_1_pilot_null_gate_count": len(pilot_null_gate_rows),
        "functional_candidate_gate_count": len(functional_candidate_gate_rows),
        "bounded_prediction_resource_summary_count": len(
            bounded_prediction_resource_rows
        ),
        "missing_required_fields": sorted(missing_required_fields),
    }


def _read_a6_runs(compare_path: Path) -> tuple[list[dict[str, Any]], set[str]]:
    if not compare_path.exists():
        raise FileNotFoundError(f"A6 comparison/artifact directory does not exist: {compare_path}")
    run_dirs = sorted(path for path in compare_path.iterdir() if path.is_dir())
    if not run_dirs:
        raise ValueError(f"A6 comparison/artifact directory contains no run subdirectories: {compare_path}")

    rows = []
    missing_required_fields: set[str] = set()
    for run_dir in run_dirs:
        config_path = run_dir / "config.yaml"
        metrics_path = run_dir / "metrics.csv"
        manifest_path = run_dir / "manifest.yaml"
        if not config_path.exists() or not metrics_path.exists() or not manifest_path.exists():
            continue
        config = yaml.safe_load(config_path.read_text()) or {}
        logistic_appraisal = config.get("logistic_appraisal")
        if not isinstance(logistic_appraisal, dict):
            continue
        condition = str(logistic_appraisal.get("condition", ""))
        metrics = _read_csv(metrics_path)
        if not metrics:
            continue
        missing_required_fields.update(
            field for field in _A6_REQUIRED_CONTROL_FIELDS if field not in metrics[0]
        )
        seed = int((yaml.safe_load(manifest_path.read_text()) or {}).get("seed", -1))
        last = metrics[-1]
        rows.append(
            {
                "condition": condition,
                "seed": seed,
                "tick_count": len(metrics),
                "final_latent_activation_mean": _number(last, "a6_latent_activation_mean_tick"),
                "final_latent_focus_mean": _number(last, "a6_latent_focus_mean_tick"),
                "final_latent_fatigue_mean": _number(last, "a6_latent_fatigue_mean_tick"),
                "final_latent_prediction_error_abs_mean": abs(
                    _number(last, "a6_latent_prediction_error_mean_tick")
                ),
                "final_artifact_novelty": _number(last, "a6_artifact_novelty_tick"),
                "final_artifact_coherence": _number(last, "a6_artifact_coherence_tick"),
                "final_artifact_actionability": _number(last, "a6_artifact_actionability_tick"),
                "final_artifact_provenance_debt": _number(
                    last, "a6_artifact_provenance_debt_tick"
                ),
                "final_artifact_risk": _number(last, "a6_artifact_risk_tick"),
                "final_artifact_contradiction": _number(last, "a6_artifact_contradiction_tick"),
                "final_artifact_readiness": _number(last, "a6_artifact_readiness_tick"),
                "final_artifact_implementation_maturity": _number(
                    last, "a6_artifact_implementation_maturity_tick"
                ),
                "final_artifact_communication_maturity": _number(
                    last, "a6_artifact_communication_maturity_tick"
                ),
                "final_artifact_utility": _artifact_utility(last),
                "handoff_attempts_total": sum(
                    _number(row, "a6_handoff_attempts_tick") for row in metrics
                ),
                "handoff_successes_total": sum(
                    _number(row, "a6_handoff_successes_tick") for row in metrics
                ),
                "handoff_failures_total": sum(
                    _number(row, "a6_handoff_failures_tick") for row in metrics
                ),
                "prediction_budget_spent_total": sum(
                    _number(row, "a6_prediction_budget_spent_tick") for row in metrics
                ),
                "tasks_created_total": _number(last, "tasks_created_total"),
                "tasks_completed_total": _number(last, "tasks_completed_total"),
                "tasks_worked_total": sum(_number(row, "tasks_worked_tick") for row in metrics),
                "messages_sent_total": sum(_number(row, "messages_sent_tick") for row in metrics),
                "completion_fraction": _safe_ratio(
                    _number(last, "tasks_completed_total"),
                    _number(last, "tasks_created_total"),
                ),
                "queue_depth": _number(last, "queue_depth"),
                "queue_delta_tick": _number(last, "queue_delta_tick"),
                "queued_task_age_mean_final": _number(last, "queued_task_age_mean_tick"),
                "action_opportunity_total": _action_opportunity_total(metrics),
                **{
                    f"{action}_total": _action_total(metrics, action)
                    for action in _A6_ACTIONS
                },
            }
        )
    if not rows:
        raise ValueError(f"No A6 logistic_appraisal run artifacts found in {compare_path}")
    return rows, missing_required_fields


def _control_delta_rows(
    runs: list[dict[str, Any]],
    missing_required_fields: set[str],
) -> list[dict[str, Any]]:
    by_condition_seed = {
        (str(row["condition"]), int(row["seed"])): row
        for row in runs
    }
    seeds = sorted({int(row["seed"]) for row in runs})
    rows: list[dict[str, Any]] = []
    for seed in seeds:
        logistic = by_condition_seed.get(("logistic", seed))
        for contrast, control_condition in _A6_CONTROL_PAIRS:
            control = by_condition_seed.get((control_condition, seed))
            if logistic is None and control is None:
                continue
            if control is None and control_condition in _A6_OPTIONAL_DERIVED_CONTROL_CONDITIONS:
                continue
            row: dict[str, Any] = {
                "contrast": contrast,
                "seed": seed,
                "control_condition": control_condition,
                "paired": str(logistic is not None and control is not None).lower(),
                "missing_required_fields": "|".join(sorted(missing_required_fields)),
            }
            for field in A6_ANALYSIS_ENDPOINT_FIELDS:
                if field in {"condition", "seed"}:
                    continue
                row[f"{field}_delta"] = (
                    round(float(logistic[field]) - float(control[field]), 6)
                    if logistic is not None and control is not None
                    else ""
                )
            rows.append(row)
    return rows


def _control_level_status(
    control_level: str,
    control_delta_rows: list[dict[str, Any]],
    missing_required_fields: set[str],
    residual_preflight_rows: list[dict[str, Any]],
    control_summary_rows: list[dict[str, Any]],
) -> str:
    complete_pairs = [row for row in control_delta_rows if row["paired"] == "true"]
    if missing_required_fields:
        return "control_delta_preflight_missing_fields"
    if not complete_pairs:
        return "control_delta_preflight_incomplete_pairs"
    if control_level in {
        "load_service_action_opportunity",
        "amplitude_matched_linear",
        "phase_shuffled",
        "threshold_shuffled",
        "paired_seed_uncertainty",
    }:
        return "paired_delta_preflight_complete"
    if control_level in _A6_1_SOURCE_NULL_CONDITIONS:
        expected_contrast = f"logistic_vs_{control_level}"
        if any(row["contrast"] == expected_contrast for row in complete_pairs):
            return "a6_1_source_preserving_null_delta_complete"
        return "a6_1_source_preserving_null_not_present"
    if control_level == "budget_matched_prediction_replay":
        expected_contrast = "logistic_vs_budget_matched_prediction_replay"
        if any(row["contrast"] == expected_contrast for row in complete_pairs):
            return "budget_matched_prediction_replay_delta_complete"
        return "budget_matched_prediction_replay_not_present"
    if control_level == "clock_queue_residualized":
        statuses = {str(row["status"]) for row in residual_preflight_rows}
        if not residual_preflight_rows:
            return "residualization_not_yet_computed"
        if any(status.startswith("missing_controls") for status in statuses):
            return "residual_preflight_missing_controls"
        if any(status.startswith("underdetermined") for status in statuses):
            return "residual_preflight_underdetermined_smoke_scale"
        return "residual_preflight_computed"
    if control_level == "promotion_closure_rules" and control_summary_rows:
        return "promotion_not_evaluated_control_summary_written"
    return "promotion_not_evaluated"


def _comparison_consistency_rows(
    compare_path: Path,
    runs: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    comparison_path = compare_path / _A6_COMPARISON_METRICS_NAME
    conditions = sorted({str(row["condition"]) for row in runs})
    derived_by_condition = {
        condition: [row for row in runs if str(row["condition"]) == condition]
        for condition in conditions
    }
    if not comparison_path.exists():
        return [
            {
                "condition": condition,
                "comparison_csv_path": str(comparison_path),
                "status": "missing_comparison_csv",
                "expected_seed_count": "",
                "observed_seed_count": len({int(row["seed"]) for row in condition_runs}),
                "expected_run_count": "",
                "observed_run_count": len(condition_runs),
                "fields_checked": "",
                "max_abs_difference": "",
                "mismatched_fields": "",
                "missing_comparison_fields": "",
                "interpretation": "aggregate comparison CSV absent; consistency preflight not applicable",
            }
            for condition, condition_runs in derived_by_condition.items()
        ]

    comparison_rows = _read_csv(comparison_path)
    comparison_by_condition = {str(row.get("condition", "")): row for row in comparison_rows}
    rows: list[dict[str, Any]] = []
    for condition, condition_runs in derived_by_condition.items():
        comparison_row = comparison_by_condition.get(condition)
        observed_seed_count = len({int(row["seed"]) for row in condition_runs})
        observed_run_count = len(condition_runs)
        if comparison_row is None:
            rows.append(
                {
                    "condition": condition,
                    "comparison_csv_path": str(comparison_path),
                    "status": "missing_condition",
                    "expected_seed_count": "",
                    "observed_seed_count": observed_seed_count,
                    "expected_run_count": "",
                    "observed_run_count": observed_run_count,
                    "fields_checked": "",
                    "max_abs_difference": "",
                    "mismatched_fields": "",
                    "missing_comparison_fields": "",
                    "interpretation": "condition missing from aggregate comparison CSV; consistency blocked",
                }
            )
            continue

        missing_fields = [
            field for field in _A6_COMPARISON_MEAN_FIELD_MAP if field not in comparison_row
        ]
        mismatched_fields: list[str] = []
        differences: list[float] = []
        for comparison_field, endpoint_field in _A6_COMPARISON_MEAN_FIELD_MAP.items():
            if comparison_field not in comparison_row:
                continue
            expected_value = _number(comparison_row, comparison_field)
            observed_value = _mean_available(
                [row.get(endpoint_field, "") for row in condition_runs]
            )
            if observed_value == "":
                continue
            difference = abs(expected_value - float(observed_value))
            differences.append(difference)
            if difference > _A6_COMPARISON_CONSISTENCY_TOLERANCE:
                mismatched_fields.append(comparison_field)
        expected_seed_count = comparison_row.get("seed_count", "")
        expected_run_count = comparison_row.get("run_count", "")
        count_mismatches = []
        if expected_seed_count not in {"", None} and int(float(expected_seed_count)) != observed_seed_count:
            count_mismatches.append("seed_count")
        if expected_run_count not in {"", None} and int(float(expected_run_count)) != observed_run_count:
            count_mismatches.append("run_count")
        mismatched_fields.extend(count_mismatches)
        status = (
            "missing_comparison_fields"
            if missing_fields
            else "mismatch"
            if mismatched_fields
            else "consistent"
        )
        rows.append(
            {
                "condition": condition,
                "comparison_csv_path": str(comparison_path),
                "status": status,
                "expected_seed_count": expected_seed_count,
                "observed_seed_count": observed_seed_count,
                "expected_run_count": expected_run_count,
                "observed_run_count": observed_run_count,
                "fields_checked": "|".join(
                    field
                    for field in _A6_COMPARISON_MEAN_FIELD_MAP
                    if field not in missing_fields
                ),
                "max_abs_difference": _rounded_mean([max(differences)]) if differences else "",
                "mismatched_fields": "|".join(mismatched_fields),
                "missing_comparison_fields": "|".join(missing_fields),
                "interpretation": _comparison_consistency_interpretation(status),
            }
        )
    return rows


def _comparison_consistency_interpretation(status: str) -> str:
    if status == "consistent":
        return "aggregate comparison CSV agrees with run-directory-derived endpoint means"
    if status == "missing_comparison_csv":
        return "aggregate comparison CSV absent; consistency preflight not applicable"
    if status == "missing_comparison_fields":
        return "aggregate comparison CSV is missing fields required for consistency check"
    if status == "missing_condition":
        return "condition missing from aggregate comparison CSV; consistency blocked"
    return "aggregate comparison CSV differs from run-directory-derived endpoint means"


def _effects_consistency_rows(compare_path: Path) -> list[dict[str, Any]]:
    effects_path = compare_path / _A6_EFFECTS_NAME
    comparison_path = compare_path / _A6_COMPARISON_METRICS_NAME
    expected_pairs = (
        ("logistic_vs_linear", "linear", "logistic"),
        ("logistic_vs_phase_shuffled", "phase_shuffled", "logistic"),
        ("logistic_vs_threshold_shuffled", "threshold_shuffled", "logistic"),
    )
    if not effects_path.exists():
        return [
            _missing_effects_row(effect_axis, effects_path, low_label, high_label)
            for effect_axis, low_label, high_label in expected_pairs
        ]
    if not comparison_path.exists():
        return [
            {
                "effect_axis": effect_axis,
                "effects_csv_path": str(effects_path),
                "status": "missing_comparison_csv",
                "low_label": low_label,
                "high_label": high_label,
                "fields_checked": "",
                "max_abs_difference": "",
                "mismatched_fields": "",
                "missing_effect_fields": "",
                "missing_comparison_conditions": "",
                "interpretation": _effects_consistency_interpretation(
                    "missing_comparison_csv"
                ),
            }
            for effect_axis, low_label, high_label in expected_pairs
        ]

    effect_rows = _read_csv(effects_path)
    comparison_rows = _read_csv(comparison_path)
    effects_by_axis = {str(row.get("effect_axis", "")): row for row in effect_rows}
    comparison_by_condition = {
        str(row.get("condition", "")): row for row in comparison_rows
    }
    rows: list[dict[str, Any]] = []
    for effect_axis, low_label, high_label in expected_pairs:
        effect_row = effects_by_axis.get(effect_axis)
        if effect_row is None:
            rows.append(_missing_effect_axis_row(effect_axis, effects_path, low_label, high_label))
            continue

        missing_effect_fields = [
            field for field in _A6_EFFECT_DELTA_FIELDS if field not in effect_row
        ]
        missing_comparison_conditions = [
            label
            for label in (low_label, high_label)
            if label not in comparison_by_condition
        ]
        mismatched_fields: list[str] = []
        differences: list[float] = []
        if not missing_comparison_conditions:
            low = comparison_by_condition[low_label]
            high = comparison_by_condition[high_label]
            for field in _A6_EFFECT_DELTA_FIELDS:
                if field not in effect_row:
                    continue
                base_field = field.removesuffix("_delta")
                if base_field not in low or base_field not in high:
                    missing_effect_fields.append(field)
                    continue
                expected_value = _number(effect_row, field)
                observed_value = _number(high, base_field) - _number(low, base_field)
                difference = abs(expected_value - observed_value)
                differences.append(difference)
                if difference > _A6_COMPARISON_CONSISTENCY_TOLERANCE:
                    mismatched_fields.append(field)

        status = (
            "missing_comparison_conditions"
            if missing_comparison_conditions
            else "missing_effect_fields"
            if missing_effect_fields
            else "mismatch"
            if mismatched_fields
            else "consistent"
        )
        rows.append(
            {
                "effect_axis": effect_axis,
                "effects_csv_path": str(effects_path),
                "status": status,
                "low_label": effect_row.get("low_label", ""),
                "high_label": effect_row.get("high_label", ""),
                "fields_checked": "|".join(
                    field
                    for field in _A6_EFFECT_DELTA_FIELDS
                    if field not in missing_effect_fields
                ),
                "max_abs_difference": _rounded_mean([max(differences)])
                if differences
                else "",
                "mismatched_fields": "|".join(mismatched_fields),
                "missing_effect_fields": "|".join(sorted(set(missing_effect_fields))),
                "missing_comparison_conditions": "|".join(
                    missing_comparison_conditions
                ),
                "interpretation": _effects_consistency_interpretation(status),
            }
        )
    return rows


def _missing_effects_row(
    effect_axis: str,
    effects_path: Path,
    low_label: str,
    high_label: str,
) -> dict[str, Any]:
    return {
        "effect_axis": effect_axis,
        "effects_csv_path": str(effects_path),
        "status": "missing_effects_csv",
        "low_label": low_label,
        "high_label": high_label,
        "fields_checked": "",
        "max_abs_difference": "",
        "mismatched_fields": "",
        "missing_effect_fields": "",
        "missing_comparison_conditions": "",
        "interpretation": _effects_consistency_interpretation("missing_effects_csv"),
    }


def _missing_effect_axis_row(
    effect_axis: str,
    effects_path: Path,
    low_label: str,
    high_label: str,
) -> dict[str, Any]:
    return {
        "effect_axis": effect_axis,
        "effects_csv_path": str(effects_path),
        "status": "missing_effect_axis",
        "low_label": low_label,
        "high_label": high_label,
        "fields_checked": "",
        "max_abs_difference": "",
        "mismatched_fields": "",
        "missing_effect_fields": "",
        "missing_comparison_conditions": "",
        "interpretation": _effects_consistency_interpretation("missing_effect_axis"),
    }


def _effects_consistency_interpretation(status: str) -> str:
    if status == "consistent":
        return "effects CSV deltas agree with aggregate comparison CSV condition means"
    if status == "missing_effects_csv":
        return "effects CSV absent; consistency preflight not applicable"
    if status == "missing_comparison_csv":
        return "aggregate comparison CSV absent; effects consistency blocked"
    if status == "missing_effect_axis":
        return "expected effect axis missing from effects CSV; consistency blocked"
    if status == "missing_effect_fields":
        return "effects CSV is missing delta fields required for consistency check"
    if status == "missing_comparison_conditions":
        return "aggregate comparison CSV lacks one or more conditions for this effect"
    return "effects CSV deltas differ from aggregate comparison CSV condition means"


def _artifact_provenance_rows(compare_path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for run_dir in sorted(path for path in compare_path.iterdir() if path.is_dir()):
        config_path = run_dir / "config.yaml"
        metrics_path = run_dir / "metrics.csv"
        manifest_path = run_dir / "manifest.yaml"
        events_path = run_dir / "events.csv"
        if not (
            config_path.exists()
            and metrics_path.exists()
            and manifest_path.exists()
            and events_path.exists()
        ):
            continue
        config = yaml.safe_load(config_path.read_text()) or {}
        logistic_appraisal = config.get("logistic_appraisal")
        if not isinstance(logistic_appraisal, dict):
            continue
        metrics = [_with_a6_derived_fields(row) for row in _read_csv(metrics_path)]
        if not metrics:
            continue
        condition = str(logistic_appraisal.get("condition", ""))
        seed = int((yaml.safe_load(manifest_path.read_text()) or {}).get("seed", -1))
        event_counts = _a6_event_counts_by_tick(_read_csv(events_path))
        for artifact_field in _A6_ARTIFACT_AUDIT_FIELDS:
            rows.append(
                _artifact_provenance_row(
                    condition,
                    seed,
                    artifact_field,
                    metrics,
                    event_counts,
                )
            )
    return rows


def _artifact_provenance_row(
    condition: str,
    seed: int,
    artifact_field: str,
    metrics: list[dict[str, str]],
    event_counts: dict[int, dict[str, int]],
) -> dict[str, Any]:
    if artifact_field not in metrics[0]:
        return {
            "condition": condition,
            "seed": seed,
            "artifact_field": artifact_field,
            "tick_count": len(metrics),
            "changed_tick_count": "",
            "total_abs_delta": "",
            "signed_delta_sum": "",
            "abs_delta_on_handoff_success_ticks": "",
            "abs_delta_on_handoff_failure_ticks": "",
            "abs_delta_on_handoff_attempt_ticks": "",
            "abs_delta_on_artifact_update_ticks": "",
            "abs_delta_on_no_a6_event_ticks": "",
            "handoff_success_event_count": "",
            "handoff_failure_event_count": "",
            "handoff_attempt_event_count": "",
            "artifact_update_event_count": "",
            "dominant_event_source": "missing_artifact_field",
            "dominant_event_delta_share": "",
            "action_handoff_total": "",
            "action_predict_total": "",
            "action_work_task_total": "",
            "action_create_task_total": "",
            "action_message_total": "",
            "action_total": "",
            "dominant_action_source": "missing_artifact_field",
            "dominant_action_share": "",
            "alias_risk": "missing_artifact_field",
            "interpretation": "artifact field missing from metrics; provenance audit blocked",
        }

    abs_delta_by_event = {
        "handoff_success": 0.0,
        "handoff_failure": 0.0,
        "handoff_attempt": 0.0,
        "artifact_update": 0.0,
        "no_a6_event": 0.0,
    }
    signed_delta_sum = 0.0
    changed_tick_count = 0
    event_totals = {
        "handoff_success": 0,
        "handoff_failure": 0,
        "handoff_attempt": 0,
        "artifact_update": 0,
    }
    action_totals = {
        "handoff": 0.0,
        "predict": 0.0,
        "work_task": 0.0,
        "create_task": 0.0,
        "message": 0.0,
    }
    action_total = 0.0

    previous = metrics[0]
    for row in metrics[1:]:
        tick = int(float(row.get("tick", 0) or 0))
        delta = _number(row, artifact_field) - _number(previous, artifact_field)
        abs_delta = abs(delta)
        if abs_delta > 0:
            changed_tick_count += 1
        signed_delta_sum += delta
        counts = event_counts.get(tick, {})
        handoff_success = int(counts.get("a6_handoff_succeeded", 0))
        handoff_failure = int(counts.get("a6_handoff_failed", 0))
        handoff_attempt = int(counts.get("a6_handoff_attempted", 0))
        artifact_update = int(counts.get("a6_artifact_update", 0))
        event_totals["handoff_success"] += handoff_success
        event_totals["handoff_failure"] += handoff_failure
        event_totals["handoff_attempt"] += handoff_attempt
        event_totals["artifact_update"] += artifact_update
        if handoff_success:
            abs_delta_by_event["handoff_success"] += abs_delta
        if handoff_failure:
            abs_delta_by_event["handoff_failure"] += abs_delta
        if handoff_attempt:
            abs_delta_by_event["handoff_attempt"] += abs_delta
        if artifact_update:
            abs_delta_by_event["artifact_update"] += abs_delta
        if not any(
            counts.get(event_type, 0)
            for event_type in (
                "a6_handoff_succeeded",
                "a6_handoff_failed",
                "a6_handoff_attempted",
                "a6_artifact_update",
                "a6_prediction_spent",
            )
        ):
            abs_delta_by_event["no_a6_event"] += abs_delta

        handoff_actions = sum(_action_tick(row, action) for action in _A6_HANDOFF_ACTIONS)
        action_totals["handoff"] += handoff_actions
        action_totals["predict"] += _action_tick(row, "predict")
        action_totals["work_task"] += _action_tick(row, "work_task")
        action_totals["create_task"] += _action_tick(row, "create_task")
        action_totals["message"] += _action_tick(row, "message")
        action_total += sum(_action_tick(row, action) for action in _A6_ACTIONS)
        previous = row

    total_abs_delta = sum(
        abs(_number(current, artifact_field) - _number(previous_row, artifact_field))
        for previous_row, current in zip(metrics, metrics[1:], strict=False)
    )
    dominant_event_source, dominant_event_delta = _dominant(abs_delta_by_event)
    dominant_action_source, dominant_action_count = _dominant(action_totals)
    dominant_event_share = _safe_ratio(dominant_event_delta, total_abs_delta)
    dominant_action_share = _safe_ratio(dominant_action_count, action_total)
    alias_risk = _artifact_alias_risk(
        artifact_field=artifact_field,
        total_abs_delta=total_abs_delta,
        dominant_event_source=dominant_event_source,
        dominant_event_share=dominant_event_share,
        dominant_action_source=dominant_action_source,
        dominant_action_share=dominant_action_share,
    )
    return {
        "condition": condition,
        "seed": seed,
        "artifact_field": artifact_field,
        "tick_count": len(metrics),
        "changed_tick_count": changed_tick_count,
        "total_abs_delta": round(total_abs_delta, 6),
        "signed_delta_sum": round(signed_delta_sum, 6),
        "abs_delta_on_handoff_success_ticks": round(abs_delta_by_event["handoff_success"], 6),
        "abs_delta_on_handoff_failure_ticks": round(abs_delta_by_event["handoff_failure"], 6),
        "abs_delta_on_handoff_attempt_ticks": round(abs_delta_by_event["handoff_attempt"], 6),
        "abs_delta_on_artifact_update_ticks": round(abs_delta_by_event["artifact_update"], 6),
        "abs_delta_on_no_a6_event_ticks": round(abs_delta_by_event["no_a6_event"], 6),
        "handoff_success_event_count": event_totals["handoff_success"],
        "handoff_failure_event_count": event_totals["handoff_failure"],
        "handoff_attempt_event_count": event_totals["handoff_attempt"],
        "artifact_update_event_count": event_totals["artifact_update"],
        "dominant_event_source": dominant_event_source,
        "dominant_event_delta_share": dominant_event_share,
        "action_handoff_total": round(action_totals["handoff"], 6),
        "action_predict_total": round(action_totals["predict"], 6),
        "action_work_task_total": round(action_totals["work_task"], 6),
        "action_create_task_total": round(action_totals["create_task"], 6),
        "action_message_total": round(action_totals["message"], 6),
        "action_total": round(action_total, 6),
        "dominant_action_source": dominant_action_source,
        "dominant_action_share": dominant_action_share,
        "alias_risk": alias_risk,
        "interpretation": _artifact_alias_interpretation(alias_risk),
    }


def _a6_event_counts_by_tick(events: list[dict[str, str]]) -> dict[int, dict[str, int]]:
    counts_by_tick: dict[int, dict[str, int]] = {}
    for event in events:
        tick_value = event.get("tick", "")
        if tick_value in {"", None}:
            continue
        tick = int(float(tick_value))
        event_type = str(event.get("event_type", ""))
        if not event_type.startswith("a6_"):
            continue
        counts = counts_by_tick.setdefault(tick, {})
        counts[event_type] = counts.get(event_type, 0) + 1
    return counts_by_tick


def _source_accounting_rows(compare_path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for run_dir in sorted(path for path in compare_path.iterdir() if path.is_dir()):
        config_path = run_dir / "config.yaml"
        metrics_path = run_dir / "metrics.csv"
        manifest_path = run_dir / "manifest.yaml"
        events_path = run_dir / "events.csv"
        if not (
            config_path.exists()
            and metrics_path.exists()
            and manifest_path.exists()
            and events_path.exists()
        ):
            continue
        config = yaml.safe_load(config_path.read_text()) or {}
        logistic_appraisal = config.get("logistic_appraisal")
        if not isinstance(logistic_appraisal, dict):
            continue
        metrics = [_with_a6_derived_fields(row) for row in _read_csv(metrics_path)]
        events = _read_csv(events_path)
        if not metrics:
            continue
        condition = str(logistic_appraisal.get("condition", ""))
        seed = int((yaml.safe_load(manifest_path.read_text()) or {}).get("seed", -1))
        metric_fields = set(metrics[0])
        event_fields = set(events[0]) if events else set()
        missing_required_fields = sorted(
            (set(_A6_EVENT_SOURCE_FIELDS) - event_fields)
            | (set(_A6_METRIC_SOURCE_REQUIRED_FIELDS) - metric_fields)
        )
        update_events = [
            row for row in events if row.get("event_type") == "a6_artifact_update"
        ]
        for artifact_field in _A6_ARTIFACT_AUDIT_FIELDS:
            rows.append(
                _source_accounting_row(
                    condition=condition,
                    seed=seed,
                    artifact_field=artifact_field,
                    metrics=metrics,
                    update_events=update_events,
                    missing_required_fields=missing_required_fields,
                )
            )
    return rows


def _source_accounting_row(
    *,
    condition: str,
    seed: int,
    artifact_field: str,
    metrics: list[dict[str, str]],
    update_events: list[dict[str, str]],
    missing_required_fields: list[str],
) -> dict[str, Any]:
    matching_events = _source_events_for_artifact_field(update_events, artifact_field)
    source_abs = {source: 0.0 for source, _ in _A6_SOURCE_DELTA_FIELDS}
    source_signed = {source: 0.0 for source, _ in _A6_SOURCE_DELTA_FIELDS}
    total_abs_delta = 0.0
    signed_delta_sum = 0.0
    clip_residual_abs_delta = 0.0
    max_abs_residual = 0.0
    for event in matching_events:
        weight = _source_event_weight(event, artifact_field)
        source_sum = 0.0
        for source, field in _A6_SOURCE_DELTA_FIELDS:
            delta = weight * _number(event, field)
            source_sum += delta
            source_signed[source] += delta
            source_abs[source] += abs(delta)
        clip_residual = weight * _number(event, "a6_artifact_delta_clip_residual")
        total_delta = weight * _number(event, "a6_artifact_delta_total")
        reconstructed_total = round(source_sum + clip_residual, 6)
        residual = abs(round(total_delta - reconstructed_total, 6))
        max_abs_residual = max(max_abs_residual, residual)
        clip_residual_abs_delta += abs(clip_residual)
        total_abs_delta += abs(total_delta)
        signed_delta_sum += total_delta

    if artifact_field == "a6_artifact_utility_tick":
        total_abs_delta = _metric_total_abs_delta(metrics, artifact_field)
        signed_delta_sum = _metric_signed_delta_sum(metrics, artifact_field)

    source_share_denominator = sum(source_abs.values()) + clip_residual_abs_delta
    source_share = {
        source: _safe_ratio(delta, source_share_denominator)
        for source, delta in source_abs.items()
    }
    clip_residual_share = _safe_ratio(clip_residual_abs_delta, source_share_denominator)
    dominant_source, dominant_source_delta = _dominant(source_abs)
    dominant_source_share = _safe_ratio(dominant_source_delta, source_share_denominator)
    required_status = (
        "missing_required_fields" if missing_required_fields else "schema_pass"
    )
    reconstruction_status = (
        "missing_required_fields"
        if missing_required_fields
        else "reconstruction_failed"
        if max_abs_residual > 1e-6
        else "schema_pass"
    )
    handoff_success_share = source_share["handoff_success"]
    prediction_expenditure_share = source_share["prediction_expenditure"]
    queue_work_share = source_share["queue_work_accounting"]
    status = _source_accounting_status(
        required_status=required_status,
        reconstruction_status=reconstruction_status,
        handoff_success_share=handoff_success_share,
        prediction_expenditure_share=prediction_expenditure_share,
        queue_work_share=queue_work_share,
    )
    return {
        "condition": condition,
        "seed": seed,
        "artifact_field": artifact_field,
        "update_event_count": len(matching_events),
        "required_field_status": required_status,
        "missing_required_fields": "|".join(missing_required_fields),
        "reconstruction_status": reconstruction_status,
        "max_abs_reconstruction_residual": round(max_abs_residual, 6),
        "signed_delta_sum": round(signed_delta_sum, 6),
        "total_abs_delta": round(total_abs_delta, 6),
        "ambient_abs_delta": round(source_abs["ambient"], 6),
        "ambient_share": source_share["ambient"],
        "handoff_attempt_abs_delta": round(source_abs["handoff_attempt"], 6),
        "handoff_attempt_share": source_share["handoff_attempt"],
        "handoff_success_abs_delta": round(source_abs["handoff_success"], 6),
        "handoff_success_share": handoff_success_share,
        "handoff_failure_abs_delta": round(source_abs["handoff_failure"], 6),
        "handoff_failure_share": source_share["handoff_failure"],
        "prediction_expenditure_abs_delta": round(
            source_abs["prediction_expenditure"],
            6,
        ),
        "prediction_expenditure_share": prediction_expenditure_share,
        "prediction_error_abs_delta": round(source_abs["prediction_error"], 6),
        "prediction_error_share": source_share["prediction_error"],
        "queue_work_accounting_abs_delta": round(
            source_abs["queue_work_accounting"],
            6,
        ),
        "queue_work_accounting_share": queue_work_share,
        "noise_abs_delta": round(source_abs["noise"], 6),
        "noise_share": source_share["noise"],
        "clip_residual_abs_delta": round(clip_residual_abs_delta, 6),
        "clip_residual_share": clip_residual_share,
        "dominant_source": dominant_source,
        "dominant_source_share": dominant_source_share,
        "handoff_success_alias_share": handoff_success_share,
        "prediction_expenditure_alias_share": prediction_expenditure_share,
        "queue_work_alias_share": queue_work_share,
        "status": status,
        "interpretation": _source_accounting_interpretation(status),
    }


def _source_events_for_artifact_field(
    events: list[dict[str, str]],
    artifact_field: str,
) -> list[dict[str, str]]:
    if artifact_field == "a6_artifact_utility_tick":
        return [
            event
            for event in events
            if event.get("a6_artifact_field") in _A6_UTILITY_FIELD_WEIGHTS
        ]
    event_field = next(
        (
            raw_field
            for raw_field, metric_field in _A6_EVENT_FIELD_TO_METRIC_FIELD.items()
            if metric_field == artifact_field
        ),
        "",
    )
    return [
        event for event in events if event.get("a6_artifact_field") == event_field
    ]


def _source_event_weight(event: dict[str, str], artifact_field: str) -> float:
    if artifact_field != "a6_artifact_utility_tick":
        return 1.0
    return _A6_UTILITY_FIELD_WEIGHTS.get(str(event.get("a6_artifact_field", "")), 0.0)


def _metric_total_abs_delta(metrics: list[dict[str, str]], artifact_field: str) -> float:
    if artifact_field not in metrics[0]:
        return 0.0
    return sum(
        abs(_number(current, artifact_field) - _number(previous, artifact_field))
        for previous, current in zip(metrics, metrics[1:], strict=False)
    )


def _metric_signed_delta_sum(metrics: list[dict[str, str]], artifact_field: str) -> float:
    if len(metrics) < 2 or artifact_field not in metrics[0]:
        return 0.0
    return _number(metrics[-1], artifact_field) - _number(metrics[0], artifact_field)


def _source_accounting_status(
    *,
    required_status: str,
    reconstruction_status: str,
    handoff_success_share: float,
    prediction_expenditure_share: float,
    queue_work_share: float,
) -> str:
    if required_status == "missing_required_fields":
        return "missing_required_fields"
    if reconstruction_status == "reconstruction_failed":
        return "reconstruction_failed"
    if handoff_success_share >= 0.75:
        return "high_handoff_alias_risk"
    if prediction_expenditure_share >= 0.75:
        return "high_prediction_alias_risk"
    if queue_work_share >= 0.75:
        return "high_queue_work_alias_risk"
    return "underdetermined_smoke_scale"


def _source_accounting_interpretation(status: str) -> str:
    if status == "missing_required_fields":
        return "A6.1 required source/accounting fields are missing; do not interpret"
    if status == "reconstruction_failed":
        return "artifact delta source columns do not reconstruct total delta"
    if status == "high_handoff_alias_risk":
        return "artifact change is dominated by handoff-success source accounting; treat as action-coupled"
    if status == "high_prediction_alias_risk":
        return "artifact change is dominated by prediction-expenditure accounting; treat prediction as a cost alias"
    if status == "high_queue_work_alias_risk":
        return "artifact change is dominated by queue/work accounting; residual controls remain required"
    return "source accounting passes schema reconstruction at smoke scale only; not promotion evidence"


def _a6_1_pilot_null_gate_rows(
    runs: list[dict[str, Any]],
    source_accounting_rows: list[dict[str, Any]],
    residual_contrast_rollup_rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    by_condition_seed = {
        (str(row["condition"]), int(row["seed"])): row for row in runs
    }
    source_by_condition_seed_field = {
        (str(row["condition"]), int(row["seed"]), str(row["artifact_field"])): row
        for row in source_accounting_rows
    }
    residual_by_contrast_endpoint = {
        (str(row["contrast"]), str(row["outcome_field"])): str(row["status"])
        for row in residual_contrast_rollup_rows
    }
    rows: list[dict[str, Any]] = []
    seeds = sorted({seed for condition, seed in by_condition_seed if condition == "logistic"})
    for seed in seeds:
        logistic = by_condition_seed.get(("logistic", seed))
        if logistic is None:
            continue
        for null_condition in _A6_1_SOURCE_NULL_CONDITIONS:
            control = by_condition_seed.get((null_condition, seed))
            if control is None:
                continue
            contrast = f"logistic_vs_{null_condition}"
            for endpoint, artifact_field in _A6_1_PILOT_ENDPOINTS:
                logistic_source = source_by_condition_seed_field.get(
                    ("logistic", seed, artifact_field),
                    {},
                )
                control_source = source_by_condition_seed_field.get(
                    (null_condition, seed, artifact_field),
                    {},
                )
                residual_status = residual_by_contrast_endpoint.get(
                    (contrast, artifact_field),
                    "underdetermined_smoke_scale",
                )
                delta = round(float(logistic[endpoint]) - float(control[endpoint]), 6)
                productivity_delta = round(
                    _backlog_adjusted_productivity(logistic)
                    - _backlog_adjusted_productivity(control),
                    6,
                )
                gate_status = _a6_1_gate_status(
                    logistic_source=logistic_source,
                    control_source=control_source,
                    delta=delta,
                    productivity_delta=productivity_delta,
                    residual_status=residual_status,
                )
                rows.append(
                    {
                        "contrast": contrast,
                        "seed": seed,
                        "endpoint": endpoint,
                        "paired": "true",
                        "logistic_value": logistic[endpoint],
                        "control_value": control[endpoint],
                        "logistic_minus_control_delta": delta,
                        "logistic_backlog_adjusted_productivity": _backlog_adjusted_productivity(
                            logistic
                        ),
                        "control_backlog_adjusted_productivity": _backlog_adjusted_productivity(
                            control
                        ),
                        "backlog_adjusted_productivity_delta": productivity_delta,
                        "logistic_required_field_status": logistic_source.get(
                            "required_field_status",
                            "missing_required_fields",
                        ),
                        "control_required_field_status": control_source.get(
                            "required_field_status",
                            "missing_required_fields",
                        ),
                        "logistic_reconstruction_status": logistic_source.get(
                            "reconstruction_status",
                            "missing_required_fields",
                        ),
                        "control_reconstruction_status": control_source.get(
                            "reconstruction_status",
                            "missing_required_fields",
                        ),
                        "logistic_handoff_success_alias_share": logistic_source.get(
                            "handoff_success_alias_share",
                            "",
                        ),
                        "control_handoff_success_alias_share": control_source.get(
                            "handoff_success_alias_share",
                            "",
                        ),
                        "residual_status": residual_status,
                        "gate_status": gate_status,
                        "interpretation": _a6_1_gate_interpretation(gate_status),
                    }
                )
    return rows


def _backlog_adjusted_productivity(row: dict[str, Any]) -> float:
    denominator = max(
        1.0,
        float(row["queue_depth"]) + float(row["tasks_created_total"]),
    )
    return round(float(row["tasks_completed_total"]) / denominator, 6)


def _a6_1_gate_status(
    *,
    logistic_source: dict[str, Any],
    control_source: dict[str, Any],
    delta: float,
    productivity_delta: float,
    residual_status: str,
) -> str:
    source_rows = (logistic_source, control_source)
    if any(row.get("required_field_status") != "schema_pass" for row in source_rows):
        return "missing_required_fields"
    if any(row.get("reconstruction_status") != "schema_pass" for row in source_rows):
        return "reconstruction_failed"
    if any(str(row.get("status", "")).startswith("high_handoff") for row in source_rows):
        return "high_handoff_alias_risk"
    if productivity_delta < 0.0:
        return "backlog_adjusted_productivity_degrades"
    if delta <= 0.0:
        return "null_removes_endpoint_advantage"
    if residual_status == "underdetermined_smoke_scale":
        return "underdetermined_smoke_scale"
    return "eligible_for_a6_2_preregistration_only"


def _a6_1_gate_interpretation(status: str) -> str:
    if status == "missing_required_fields":
        return "required A6.1 source fields are missing; pilot gate cannot interpret"
    if status == "reconstruction_failed":
        return "artifact source deltas fail reconstruction; pilot gate cannot interpret"
    if status == "high_handoff_alias_risk":
        return "handoff-success source share remains dominant; treat endpoint as action-coupled"
    if status == "backlog_adjusted_productivity_degrades":
        return "logistic endpoint is not accepted because backlog-adjusted productivity degrades"
    if status == "null_removes_endpoint_advantage":
        return "source-preserving null removes or matches the logistic endpoint advantage"
    if status == "underdetermined_smoke_scale":
        return "paired null delta exists, but residual rows remain smoke-scale; no promotion"
    return "eligible only for writing a later A6.2 preregistered residual-recurrence pilot"


def _dominant(values: dict[str, float]) -> tuple[str, float]:
    if not values:
        return "", 0.0
    key, value = max(values.items(), key=lambda item: (item[1], item[0]))
    return key, value


def _artifact_alias_risk(
    *,
    artifact_field: str,
    total_abs_delta: float,
    dominant_event_source: str,
    dominant_event_share: float,
    dominant_action_source: str,
    dominant_action_share: float,
) -> str:
    if total_abs_delta == 0:
        return "no_change"
    direct_handoff_fields = {
        "a6_artifact_coherence_tick",
        "a6_artifact_actionability_tick",
        "a6_artifact_provenance_debt_tick",
        "a6_artifact_risk_tick",
        "a6_artifact_contradiction_tick",
        "a6_artifact_readiness_tick",
        "a6_artifact_implementation_maturity_tick",
        "a6_artifact_communication_maturity_tick",
        "a6_artifact_utility_tick",
    }
    if (
        artifact_field in direct_handoff_fields
        and dominant_event_source
        in {"handoff_success", "handoff_failure", "handoff_attempt"}
        and dominant_event_share >= 0.75
    ):
        return "high_action_alias_risk"
    if dominant_action_source == "handoff" and dominant_action_share >= 0.5:
        return "action_coupled_smoke"
    if dominant_event_source == "artifact_update" and dominant_event_share >= 0.75:
        return "ambient_artifact_update_coupled"
    return "mixed_or_low_alias_risk_smoke"


def _artifact_alias_interpretation(alias_risk: str) -> str:
    if alias_risk == "high_action_alias_risk":
        return "field changes are concentrated on handoff event ticks; treat utility/readiness as action-count coupled until controlled"
    if alias_risk == "action_coupled_smoke":
        return "same-tick action mix is handoff dominated; use as an alias warning, not mechanism evidence"
    if alias_risk == "ambient_artifact_update_coupled":
        return "field changes track scheduled artifact-update ticks; audit distinguishes ambient drift from action effects"
    if alias_risk == "no_change":
        return "field did not change over this smoke run"
    if alias_risk == "missing_artifact_field":
        return "artifact field missing from metrics; provenance audit blocked"
    return "field changes have mixed same-tick sources at smoke scale; do not interpret as causal provenance"


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as handle:
        return list(csv.DictReader(handle))


def _write_csv(path: Path, rows: list[dict[str, Any]], fields: tuple[str, ...]) -> None:
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(fields))
        writer.writeheader()
        writer.writerows(rows)


def _number(row: dict[str, str], field: str) -> float:
    value = row.get(field, "")
    return float(value) if value not in {"", None} else 0.0


def _safe_ratio(numerator: float, denominator: float) -> float:
    return round(numerator / denominator, 6) if denominator else 0.0


def _artifact_utility(row: dict[str, str]) -> float:
    positive = (
        _number(row, "a6_artifact_readiness_tick")
        + _number(row, "a6_artifact_coherence_tick")
        + _number(row, "a6_artifact_actionability_tick")
        + _number(row, "a6_artifact_implementation_maturity_tick")
        + _number(row, "a6_artifact_communication_maturity_tick")
    )
    negative = (
        _number(row, "a6_artifact_provenance_debt_tick")
        + _number(row, "a6_artifact_risk_tick")
        + _number(row, "a6_artifact_contradiction_tick")
    )
    return round((positive - negative) / 5.0, 6)


def _action_opportunity_total(metrics: list[dict[str, str]]) -> float:
    return sum(
        _number(row, field)
        for row in metrics
        for field in row
        if field.startswith("role_") and field.endswith("_tick")
    )


def _action_total(metrics: list[dict[str, str]], action: str) -> float:
    suffix = f"_{action}_tick"
    return sum(
        _number(row, field)
        for row in metrics
        for field in row
        if field.startswith("role_") and field.endswith(suffix)
    )


def _residual_preflight_rows(compare_path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for (
        condition,
        seed,
        enriched_metrics,
        missing_control_fields,
        usable_control_fields,
    ) in _residual_run_contexts(compare_path):
        available_fields = set(enriched_metrics[0])
        for outcome_field in _A6_RESIDUAL_OUTCOME_FIELDS:
            row_count = len(enriched_metrics)
            if outcome_field not in available_fields:
                rows.append(
                    _empty_residual_row(
                        condition,
                        seed,
                        outcome_field,
                        row_count,
                        usable_control_fields,
                        (*missing_control_fields, outcome_field),
                    )
                )
                continue
            values = [_number(row, outcome_field) for row in enriched_metrics]
            controls = [
                [_number(row, field) for field in usable_control_fields]
                for row in enriched_metrics
            ]
            residuals = _ridge_fit(values, controls)["residuals"]
            control_count = len(usable_control_fields)
            degrees_of_freedom = row_count - control_count - 1
            status = (
                "missing_controls_preflight"
                if missing_control_fields
                else "underdetermined_smoke_scale"
                if degrees_of_freedom <= 0
                else "computed"
            )
            rows.append(
                {
                    "condition": condition,
                    "seed": seed,
                    "outcome_field": outcome_field,
                    "row_count": row_count,
                    "control_count": control_count,
                    "degrees_of_freedom": degrees_of_freedom,
                    "status": status,
                    "missing_control_fields": "|".join(missing_control_fields),
                    "control_fields_used": "|".join(usable_control_fields),
                    "raw_variance": round(_variance(values), 6),
                    "residual_variance": round(_variance(residuals), 6),
                    "raw_lag1_autocorrelation": round(_lag1_autocorrelation(values), 6),
                    "residual_lag1_autocorrelation": round(
                        _lag1_autocorrelation(residuals), 6
                    ),
                }
            )
    return rows


def _residual_timeseries_rows(compare_path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for (
        condition,
        seed,
        enriched_metrics,
        missing_control_fields,
        usable_control_fields,
    ) in _residual_run_contexts(compare_path):
        available_fields = set(enriched_metrics[0])
        for outcome_field in _A6_RESIDUAL_OUTCOME_FIELDS:
            if outcome_field not in available_fields:
                continue
            values = [_number(row, outcome_field) for row in enriched_metrics]
            controls = [
                [_number(row, field) for field in usable_control_fields]
                for row in enriched_metrics
            ]
            fit = _ridge_fit(values, controls)
            degrees_of_freedom = len(values) - len(usable_control_fields) - 1
            status = (
                "missing_controls_preflight"
                if missing_control_fields
                else "underdetermined_smoke_scale"
                if degrees_of_freedom <= 0
                else "computed"
            )
            for metric_row, raw_value, fitted_value, residual_value in zip(
                enriched_metrics,
                values,
                fit["fitted"],
                fit["residuals"],
                strict=True,
            ):
                rows.append(
                    {
                        "condition": condition,
                        "seed": seed,
                        "tick": metric_row.get("tick", ""),
                        "outcome_field": outcome_field,
                        "status": status,
                        "missing_control_fields": "|".join(missing_control_fields),
                        "control_fields_used": "|".join(usable_control_fields),
                        "raw_value": round(raw_value, 6),
                        "fitted_value": round(fitted_value, 6),
                        "residual_value": round(residual_value, 6),
                    }
                )
    return rows


def _residual_contrast_summary_rows(
    residual_timeseries_rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    by_condition_seed_outcome: dict[tuple[str, int, str], list[dict[str, Any]]] = {}
    for row in residual_timeseries_rows:
        by_condition_seed_outcome.setdefault(
            (
                str(row["condition"]),
                int(row["seed"]),
                str(row["outcome_field"]),
            ),
            [],
        ).append(row)

    seeds = sorted({seed for _, seed, _ in by_condition_seed_outcome})
    outcomes = sorted({outcome for _, _, outcome in by_condition_seed_outcome})
    rows: list[dict[str, Any]] = []
    for contrast, control_condition in _A6_CONTROL_PAIRS:
        if control_condition in _A6_OPTIONAL_DERIVED_CONTROL_CONDITIONS and not any(
            condition == control_condition for condition, _, _ in by_condition_seed_outcome
        ):
            continue
        for seed in seeds:
            for outcome in outcomes:
                logistic_rows = by_condition_seed_outcome.get(("logistic", seed, outcome), [])
                control_rows = by_condition_seed_outcome.get(
                    (control_condition, seed, outcome),
                    [],
                )
                paired = bool(logistic_rows and control_rows)
                if not paired:
                    rows.append(
                        _empty_residual_contrast_row(
                            contrast,
                            seed,
                            control_condition,
                            outcome,
                            logistic_rows,
                            control_rows,
                        )
                    )
                    continue
                logistic_values = _sorted_residual_values(logistic_rows)
                control_values = _sorted_residual_values(control_rows)
                logistic_variance = _variance(logistic_values)
                control_variance = _variance(control_values)
                logistic_autocorrelation = _lag1_autocorrelation(logistic_values)
                control_autocorrelation = _lag1_autocorrelation(control_values)
                logistic_sign_changes = _sign_change_count(logistic_values)
                control_sign_changes = _sign_change_count(control_values)
                statuses = {str(row["status"]) for row in (*logistic_rows, *control_rows)}
                status = _residual_contrast_status(statuses, logistic_rows, control_rows)
                rows.append(
                    {
                        "contrast": contrast,
                        "seed": seed,
                        "control_condition": control_condition,
                        "outcome_field": outcome,
                        "paired": "true",
                        "status": status,
                        "tick_count": len(logistic_values),
                        "control_tick_count": len(control_values),
                        "logistic_residual_variance": round(logistic_variance, 6),
                        "control_residual_variance": round(control_variance, 6),
                        "residual_variance_delta": round(
                            logistic_variance - control_variance,
                            6,
                        ),
                        "logistic_residual_lag1_autocorrelation": round(
                            logistic_autocorrelation,
                            6,
                        ),
                        "control_residual_lag1_autocorrelation": round(
                            control_autocorrelation,
                            6,
                        ),
                        "residual_lag1_autocorrelation_delta": round(
                            logistic_autocorrelation - control_autocorrelation,
                            6,
                        ),
                        "logistic_residual_sign_change_count": logistic_sign_changes,
                        "control_residual_sign_change_count": control_sign_changes,
                        "residual_sign_change_count_delta": (
                            logistic_sign_changes - control_sign_changes
                        ),
                        "interpretation": _residual_contrast_interpretation(status),
                    }
                )
    return rows


def _empty_residual_contrast_row(
    contrast: str,
    seed: int,
    control_condition: str,
    outcome: str,
    logistic_rows: list[dict[str, Any]],
    control_rows: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "contrast": contrast,
        "seed": seed,
        "control_condition": control_condition,
        "outcome_field": outcome,
        "paired": "false",
        "status": "missing_residual_pair",
        "tick_count": len(logistic_rows),
        "control_tick_count": len(control_rows),
        "logistic_residual_variance": "",
        "control_residual_variance": "",
        "residual_variance_delta": "",
        "logistic_residual_lag1_autocorrelation": "",
        "control_residual_lag1_autocorrelation": "",
        "residual_lag1_autocorrelation_delta": "",
        "logistic_residual_sign_change_count": "",
        "control_residual_sign_change_count": "",
        "residual_sign_change_count_delta": "",
        "interpretation": _residual_contrast_interpretation("missing_residual_pair"),
    }


def _sorted_residual_values(rows: list[dict[str, Any]]) -> list[float]:
    ordered_rows = sorted(rows, key=lambda row: int(float(row.get("tick", 0) or 0)))
    return [float(row["residual_value"]) for row in ordered_rows]


def _sign_change_count(values: list[float]) -> int:
    signs = [1 if value > 0 else -1 if value < 0 else 0 for value in values]
    nonzero_signs = [sign for sign in signs if sign]
    return sum(
        1
        for previous, current in zip(nonzero_signs, nonzero_signs[1:], strict=False)
        if previous != current
    )


def _residual_contrast_status(
    statuses: set[str],
    logistic_rows: list[dict[str, Any]],
    control_rows: list[dict[str, Any]],
) -> str:
    if not logistic_rows or not control_rows:
        return "missing_residual_pair"
    if len(logistic_rows) != len(control_rows):
        return "tick_count_mismatch"
    if any(status.startswith("missing") for status in statuses):
        return "missing_residual_pair"
    if any(status.startswith("underdetermined") for status in statuses):
        return "underdetermined_smoke_scale"
    if statuses == {"computed"}:
        return "computed"
    return "|".join(sorted(statuses))


def _residual_contrast_interpretation(status: str) -> str:
    if status == "computed":
        return "residual timeseries contrast computed; still requires preregistered promotion gate"
    if status == "underdetermined_smoke_scale":
        return "smoke-scale residual timeseries contrast only; not recurrence evidence"
    if status == "tick_count_mismatch":
        return "paired residual traces have unequal tick counts; contrast is incomplete"
    return "residual timeseries pair missing or incomplete; do not interpret"


def _residual_contrast_rollup_rows(
    residual_contrast_rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, str, str], list[dict[str, Any]]] = {}
    for row in residual_contrast_rows:
        grouped.setdefault(
            (
                str(row["contrast"]),
                str(row["control_condition"]),
                str(row["outcome_field"]),
            ),
            [],
        ).append(row)

    rows: list[dict[str, Any]] = []
    for (contrast, control_condition, outcome), group_rows in sorted(grouped.items()):
        complete_rows = [
            row
            for row in group_rows
            if str(row.get("paired", "")) == "true"
            and row.get("residual_variance_delta", "") not in {"", None}
            and row.get("residual_lag1_autocorrelation_delta", "") not in {"", None}
            and row.get("residual_sign_change_count_delta", "") not in {"", None}
        ]
        statuses = sorted({str(row.get("status", "")) for row in group_rows})
        status = _residual_rollup_status(statuses, group_rows, complete_rows)
        variance_stats = _direction_stats(
            [row.get("residual_variance_delta", "") for row in complete_rows]
        )
        autocorrelation_stats = _direction_stats(
            [
                row.get("residual_lag1_autocorrelation_delta", "")
                for row in complete_rows
            ]
        )
        sign_change_stats = _direction_stats(
            [row.get("residual_sign_change_count_delta", "") for row in complete_rows]
        )
        rows.append(
            {
                "contrast": contrast,
                "control_condition": control_condition,
                "outcome_field": outcome,
                "paired_seed_count": sum(
                    1 for row in group_rows if str(row.get("paired", "")) == "true"
                ),
                "complete_seed_count": len(complete_rows),
                "incomplete_seed_count": len(group_rows) - len(complete_rows),
                "status": status,
                "statuses_observed": "|".join(statuses),
                "seeds_included": "|".join(
                    str(int(row["seed"])) for row in sorted(
                        complete_rows,
                        key=lambda item: int(item["seed"]),
                    )
                ),
                "mean_residual_variance_delta": variance_stats["mean"],
                "residual_variance_delta_positive_count": variance_stats["positive"],
                "residual_variance_delta_negative_count": variance_stats["negative"],
                "residual_variance_delta_zero_count": variance_stats["zero"],
                "residual_variance_direction_agreement": variance_stats["agreement"],
                "mean_residual_lag1_autocorrelation_delta": autocorrelation_stats["mean"],
                "residual_lag1_autocorrelation_delta_positive_count": autocorrelation_stats[
                    "positive"
                ],
                "residual_lag1_autocorrelation_delta_negative_count": autocorrelation_stats[
                    "negative"
                ],
                "residual_lag1_autocorrelation_delta_zero_count": autocorrelation_stats[
                    "zero"
                ],
                "residual_lag1_autocorrelation_direction_agreement": autocorrelation_stats[
                    "agreement"
                ],
                "mean_residual_sign_change_count_delta": sign_change_stats["mean"],
                "residual_sign_change_count_delta_positive_count": sign_change_stats[
                    "positive"
                ],
                "residual_sign_change_count_delta_negative_count": sign_change_stats[
                    "negative"
                ],
                "residual_sign_change_count_delta_zero_count": sign_change_stats["zero"],
                "residual_sign_change_count_direction_agreement": sign_change_stats[
                    "agreement"
                ],
                "interpretation": _residual_rollup_interpretation(status),
            }
        )
    return rows


def _residual_rollup_status(
    statuses: list[str],
    group_rows: list[dict[str, Any]],
    complete_rows: list[dict[str, Any]],
) -> str:
    if not complete_rows:
        return "missing_residual_pair"
    if len(complete_rows) != len(group_rows):
        return "incomplete_seed_rollup"
    if any(status.startswith("missing") for status in statuses):
        return "missing_residual_pair"
    if any(status.startswith("tick_count_mismatch") for status in statuses):
        return "tick_count_mismatch"
    if any(status.startswith("underdetermined") for status in statuses):
        return "underdetermined_smoke_scale"
    if statuses == ["computed"]:
        return "computed"
    return "|".join(statuses)


def _direction_stats(values: list[Any]) -> dict[str, Any]:
    numeric = [float(value) for value in values if value not in {"", None}]
    positive = sum(1 for value in numeric if value > 0)
    negative = sum(1 for value in numeric if value < 0)
    zero = sum(1 for value in numeric if value == 0)
    directional = positive + negative
    agreement = ""
    if numeric:
        agreement = str(round(max(positive, negative, zero) / len(numeric), 6))
    return {
        "mean": _rounded_mean(numeric),
        "positive": positive,
        "negative": negative,
        "zero": zero,
        "agreement": agreement if directional or zero else "",
    }


def _residual_rollup_interpretation(status: str) -> str:
    if status == "computed":
        return "read-only residual contrast rollup computed; still requires preregistered promotion gate"
    if status == "underdetermined_smoke_scale":
        return "smoke-scale residual contrast rollup only; direction agreement is not recurrence evidence"
    if status == "incomplete_seed_rollup":
        return "some residual seed contrasts are incomplete; do not interpret as mechanism evidence"
    if status == "tick_count_mismatch":
        return "paired residual traces have unequal tick counts; rollup is incomplete"
    return "residual contrast rollup incomplete; do not interpret"


def _residual_run_contexts(
    compare_path: Path,
) -> list[tuple[str, int, list[dict[str, str]], tuple[str, ...], tuple[str, ...]]]:
    contexts: list[
        tuple[str, int, list[dict[str, str]], tuple[str, ...], tuple[str, ...]]
    ] = []
    for run_dir in sorted(path for path in compare_path.iterdir() if path.is_dir()):
        config_path = run_dir / "config.yaml"
        metrics_path = run_dir / "metrics.csv"
        manifest_path = run_dir / "manifest.yaml"
        if not config_path.exists() or not metrics_path.exists() or not manifest_path.exists():
            continue
        config = yaml.safe_load(config_path.read_text()) or {}
        logistic_appraisal = config.get("logistic_appraisal")
        if not isinstance(logistic_appraisal, dict):
            continue
        metrics = _read_csv(metrics_path)
        if not metrics:
            continue
        condition = str(logistic_appraisal.get("condition", ""))
        seed = int((yaml.safe_load(manifest_path.read_text()) or {}).get("seed", -1))
        enriched_metrics = [_with_a6_derived_fields(row) for row in metrics]
        available_fields = set(enriched_metrics[0])
        action_control_fields = tuple(f"action_{action}_tick" for action in _A6_ACTIONS)
        control_fields = (*_A6_RESIDUAL_BASE_CONTROL_FIELDS, *action_control_fields)
        missing_control_fields = tuple(
            field for field in control_fields if field not in available_fields
        )
        usable_control_fields = tuple(
            field for field in control_fields if field in available_fields
        )
        contexts.append(
            (
                condition,
                seed,
                enriched_metrics,
                missing_control_fields,
                usable_control_fields,
            )
        )
    return contexts


def _control_summary_rows(
    control_delta_rows: list[dict[str, Any]],
    residual_preflight_rows: list[dict[str, Any]],
    missing_required_fields: set[str],
) -> list[dict[str, Any]]:
    residual_by_condition_seed_outcome = {
        (
            str(row["condition"]),
            int(row["seed"]),
            str(row["outcome_field"]),
        ): row
        for row in residual_preflight_rows
    }
    outcomes = sorted({str(row["outcome_field"]) for row in residual_preflight_rows})
    rows: list[dict[str, Any]] = []
    for contrast, control_condition in _A6_CONTROL_PAIRS:
        endpoint_rows = [
            row
            for row in control_delta_rows
            if row["contrast"] == contrast and row["paired"] == "true"
        ]
        if control_condition in _A6_OPTIONAL_DERIVED_CONTROL_CONDITIONS and not endpoint_rows:
            continue
        paired_seeds = sorted(int(row["seed"]) for row in endpoint_rows)
        endpoint_means = {
            field: _mean_available([row.get(field, "") for row in endpoint_rows])
            for field in (
                "final_artifact_utility_delta",
                "queue_depth_delta",
                "action_opportunity_total_delta",
                "completion_fraction_delta",
            )
        }
        for outcome in outcomes:
            raw_variance_deltas: list[float] = []
            residual_variance_deltas: list[float] = []
            raw_autocorrelation_deltas: list[float] = []
            residual_autocorrelation_deltas: list[float] = []
            statuses: set[str] = set()
            for seed in paired_seeds:
                logistic = residual_by_condition_seed_outcome.get(("logistic", seed, outcome))
                control = residual_by_condition_seed_outcome.get(
                    (control_condition, seed, outcome)
                )
                if logistic is None or control is None:
                    statuses.add("missing_residual_pair")
                    continue
                statuses.update({str(logistic["status"]), str(control["status"])})
                _append_delta(
                    raw_variance_deltas,
                    logistic.get("raw_variance", ""),
                    control.get("raw_variance", ""),
                )
                _append_delta(
                    residual_variance_deltas,
                    logistic.get("residual_variance", ""),
                    control.get("residual_variance", ""),
                )
                _append_delta(
                    raw_autocorrelation_deltas,
                    logistic.get("raw_lag1_autocorrelation", ""),
                    control.get("raw_lag1_autocorrelation", ""),
                )
                _append_delta(
                    residual_autocorrelation_deltas,
                    logistic.get("residual_lag1_autocorrelation", ""),
                    control.get("residual_lag1_autocorrelation", ""),
                )
            residual_status = _summary_residual_status(statuses, missing_required_fields)
            rows.append(
                {
                    "contrast": contrast,
                    "control_condition": control_condition,
                    "outcome_field": outcome,
                    "paired_seed_count": len(paired_seeds),
                    "missing_required_fields": "|".join(sorted(missing_required_fields)),
                    "residual_status": residual_status,
                    "mean_raw_variance_delta": _rounded_mean(raw_variance_deltas),
                    "mean_residual_variance_delta": _rounded_mean(residual_variance_deltas),
                    "mean_raw_lag1_autocorrelation_delta": _rounded_mean(
                        raw_autocorrelation_deltas
                    ),
                    "mean_residual_lag1_autocorrelation_delta": _rounded_mean(
                        residual_autocorrelation_deltas
                    ),
                    "mean_final_artifact_utility_delta": endpoint_means[
                        "final_artifact_utility_delta"
                    ],
                    "mean_queue_depth_delta": endpoint_means["queue_depth_delta"],
                    "mean_action_opportunity_total_delta": endpoint_means[
                        "action_opportunity_total_delta"
                    ],
                    "mean_completion_fraction_delta": endpoint_means[
                        "completion_fraction_delta"
                    ],
                    "interpretation": _control_summary_interpretation(residual_status),
                }
            )
    return rows


def _append_delta(target: list[float], high: Any, low: Any) -> None:
    if high in {"", None} or low in {"", None}:
        return
    target.append(float(high) - float(low))


def _mean_available(values: list[Any]) -> str:
    numeric = [float(value) for value in values if value not in {"", None}]
    return _rounded_mean(numeric)


def _rounded_mean(values: list[float]) -> str:
    if not values:
        return ""
    return str(round(sum(values) / len(values), 6))


def _summary_residual_status(statuses: set[str], missing_required_fields: set[str]) -> str:
    if missing_required_fields:
        return "missing_required_fields"
    if not statuses:
        return "missing_residual_pair"
    if any(status.startswith("missing") for status in statuses):
        return "missing_residual_pair"
    if any(status.startswith("underdetermined") for status in statuses):
        return "underdetermined_smoke_scale"
    if statuses == {"computed"}:
        return "computed"
    return "|".join(sorted(statuses))


def _control_summary_interpretation(residual_status: str) -> str:
    if residual_status == "computed":
        return "read-only residual contrast computed; still requires preregistered promotion gate"
    if residual_status == "underdetermined_smoke_scale":
        return "smoke-scale residual contrast only; not recurrence or promotion evidence"
    if residual_status == "missing_required_fields":
        return "required accounting fields missing; control interpretation blocked"
    return "residual contrast incomplete; do not interpret as mechanism evidence"


def _functional_candidate_gate_rows(compare_path: Path) -> list[dict[str, Any]]:
    per_seed: list[dict[str, Any]] = []
    for run_dir in sorted(path for path in compare_path.iterdir() if path.is_dir()):
        config_path = run_dir / "config.yaml"
        metrics_path = run_dir / "metrics.csv"
        manifest_path = run_dir / "manifest.yaml"
        if not (config_path.exists() and metrics_path.exists() and manifest_path.exists()):
            continue
        config = yaml.safe_load(config_path.read_text()) or {}
        logistic_appraisal = config.get("logistic_appraisal")
        if not isinstance(logistic_appraisal, dict):
            continue
        metrics = [_with_a6_derived_fields(row) for row in _read_csv(metrics_path)]
        if not metrics:
            continue
        per_seed.append(
            _functional_candidate_seed_row(
                condition=str(logistic_appraisal.get("condition", "")),
                metrics=metrics,
            )
        )

    rows: list[dict[str, Any]] = []
    by_condition = {
        condition: [row for row in per_seed if row["condition"] == condition]
        for condition in sorted({str(row["condition"]) for row in per_seed})
    }
    matched_control_condition = ""
    matched_control_rows: list[dict[str, Any]] = []
    matched_control_candidate_rate = 0.0
    for condition, rows_for_condition in by_condition.items():
        if condition == "logistic":
            continue
        candidate_rate = _candidate_rate(rows_for_condition)
        if (
            not matched_control_rows
            or candidate_rate > matched_control_candidate_rate
            or (
                candidate_rate == matched_control_candidate_rate
                and condition < matched_control_condition
            )
        ):
            matched_control_condition = condition
            matched_control_rows = rows_for_condition
            matched_control_candidate_rate = candidate_rate

    for condition, seed_rows in by_condition.items():
        candidate_rate = _candidate_rate(seed_rows)
        excess_rate = (
            candidate_rate - matched_control_candidate_rate
            if condition == "logistic"
            else ""
        )
        logistic_matched_excess = (
            _functional_candidate_matched_excess(seed_rows, matched_control_rows)
            if condition == "logistic"
            else {}
        )
        gate_status = _functional_candidate_gate_status(
            condition=condition,
            candidate_rate=candidate_rate,
            matched_control_candidate_rate=matched_control_candidate_rate,
        )
        rows.append(
            {
                "condition": condition,
                "seed_count": len(seed_rows),
                "role_nonperiodic_seed_count": _count_true(seed_rows, "role_nonperiodic"),
                "functional_movement_seed_count": _count_true(seed_rows, "functional_movement"),
                "bounded_unsaturated_seed_count": _count_true(seed_rows, "bounded_unsaturated"),
                "candidate_seed_count": _count_true(seed_rows, "candidate"),
                "candidate_rate": round(candidate_rate, 6),
                "mean_artifact_maturity_delta": _rounded_mean(
                    [float(row["artifact_maturity_delta"]) for row in seed_rows]
                ),
                "mean_provenance_debt_delta": _rounded_mean(
                    [float(row["provenance_debt_delta"]) for row in seed_rows]
                ),
                "mean_risk_delta": _rounded_mean(
                    [float(row["risk_delta"]) for row in seed_rows]
                ),
                "mean_prediction_error_abs_delta": _rounded_mean(
                    [float(row["prediction_error_abs_delta"]) for row in seed_rows]
                ),
                "mean_functional_score": _rounded_mean(
                    [float(row["functional_score"]) for row in seed_rows]
                ),
                "matched_control_condition": matched_control_condition
                if condition == "logistic"
                else "",
                "matched_control_seed_count": len(matched_control_rows)
                if condition == "logistic"
                else "",
                "matched_control_candidate_seed_count": _count_true(
                    matched_control_rows, "candidate"
                )
                if condition == "logistic"
                else "",
                "matched_control_candidate_rate": round(matched_control_candidate_rate, 6)
                if condition == "logistic"
                else "",
                "matched_excess_candidate_rate": round(float(excess_rate), 6)
                if excess_rate != ""
                else "",
                "matched_excess_role_nonperiodic_rate": logistic_matched_excess.get(
                    "role_nonperiodic_rate", ""
                ),
                "matched_excess_functional_movement_rate": logistic_matched_excess.get(
                    "functional_movement_rate", ""
                ),
                "matched_excess_bounded_unsaturated_rate": logistic_matched_excess.get(
                    "bounded_unsaturated_rate", ""
                ),
                "matched_excess_artifact_maturity_delta": logistic_matched_excess.get(
                    "artifact_maturity_delta", ""
                ),
                "matched_excess_provenance_debt_improvement": logistic_matched_excess.get(
                    "provenance_debt_improvement", ""
                ),
                "matched_excess_risk_improvement": logistic_matched_excess.get(
                    "risk_improvement", ""
                ),
                "matched_excess_prediction_error_abs_improvement": logistic_matched_excess.get(
                    "prediction_error_abs_improvement", ""
                ),
                "matched_excess_functional_score": logistic_matched_excess.get(
                    "functional_score", ""
                ),
                "gate_status": gate_status,
                "interpretation": _functional_candidate_interpretation(gate_status),
            }
        )
    return rows


def _functional_candidate_seed_row(
    *,
    condition: str,
    metrics: list[dict[str, str]],
) -> dict[str, Any]:
    first = metrics[0]
    last = metrics[-1]
    artifact_maturity_delta = _mean_values_float(
        [
            _number(last, "a6_artifact_readiness_tick")
            - _number(first, "a6_artifact_readiness_tick"),
            _number(last, "a6_artifact_implementation_maturity_tick")
            - _number(first, "a6_artifact_implementation_maturity_tick"),
            _number(last, "a6_artifact_communication_maturity_tick")
            - _number(first, "a6_artifact_communication_maturity_tick"),
        ]
    )
    provenance_debt_delta = (
        _number(last, "a6_artifact_provenance_debt_tick")
        - _number(first, "a6_artifact_provenance_debt_tick")
    )
    risk_delta = (
        _number(last, "a6_artifact_risk_tick")
        - _number(first, "a6_artifact_risk_tick")
    )
    prediction_error_abs_delta = abs(
        _number(last, "a6_latent_prediction_error_mean_tick")
    ) - abs(_number(first, "a6_latent_prediction_error_mean_tick"))
    functional_movement = (
        artifact_maturity_delta > 0.01
        or provenance_debt_delta < -0.005
        or risk_delta < -0.005
        or prediction_error_abs_delta < -0.005
    )
    functional_score = (
        artifact_maturity_delta
        - provenance_debt_delta
        - risk_delta
        - prediction_error_abs_delta
    )
    role_nonperiodic = _role_sequence_nonperiodic(metrics)
    bounded_unsaturated = _bounded_unsaturated(metrics)
    return {
        "condition": condition,
        "role_nonperiodic": role_nonperiodic,
        "functional_movement": functional_movement,
        "bounded_unsaturated": bounded_unsaturated,
        "candidate": role_nonperiodic and functional_movement and bounded_unsaturated,
        "artifact_maturity_delta": round(artifact_maturity_delta, 6),
        "provenance_debt_delta": round(provenance_debt_delta, 6),
        "risk_delta": round(risk_delta, 6),
        "prediction_error_abs_delta": round(prediction_error_abs_delta, 6),
        "functional_score": round(functional_score, 6),
    }


def _functional_candidate_matched_excess(
    logistic_rows: list[dict[str, Any]],
    control_rows: list[dict[str, Any]],
) -> dict[str, float | str]:
    if not control_rows:
        return {
            "role_nonperiodic_rate": "",
            "functional_movement_rate": "",
            "bounded_unsaturated_rate": "",
            "artifact_maturity_delta": "",
            "provenance_debt_improvement": "",
            "risk_improvement": "",
            "prediction_error_abs_improvement": "",
            "functional_score": "",
        }
    return {
        "role_nonperiodic_rate": round(
            _boolean_rate(logistic_rows, "role_nonperiodic")
            - _boolean_rate(control_rows, "role_nonperiodic"),
            6,
        ),
        "functional_movement_rate": round(
            _boolean_rate(logistic_rows, "functional_movement")
            - _boolean_rate(control_rows, "functional_movement"),
            6,
        ),
        "bounded_unsaturated_rate": round(
            _boolean_rate(logistic_rows, "bounded_unsaturated")
            - _boolean_rate(control_rows, "bounded_unsaturated"),
            6,
        ),
        "artifact_maturity_delta": _matched_mean_delta(
            logistic_rows, control_rows, "artifact_maturity_delta"
        ),
        "provenance_debt_improvement": _matched_mean_improvement(
            logistic_rows, control_rows, "provenance_debt_delta"
        ),
        "risk_improvement": _matched_mean_improvement(
            logistic_rows, control_rows, "risk_delta"
        ),
        "prediction_error_abs_improvement": _matched_mean_improvement(
            logistic_rows, control_rows, "prediction_error_abs_delta"
        ),
        "functional_score": _matched_mean_delta(
            logistic_rows, control_rows, "functional_score"
        ),
    }


def _role_sequence_nonperiodic(metrics: list[dict[str, str]]) -> bool:
    dominant_actions = [
        max(_A6_ACTIONS, key=lambda action: (_action_tick(row, action), action))
        for row in metrics
    ]
    unique_actions = set(dominant_actions)
    if len(unique_actions) < 3:
        return False
    most_common_share = max(dominant_actions.count(action) for action in unique_actions) / len(
        dominant_actions
    )
    if most_common_share >= 0.75:
        return False
    for period in (1, 2, 3, 4):
        if len(dominant_actions) > period * 2 and all(
            action == dominant_actions[index % period]
            for index, action in enumerate(dominant_actions)
        ):
            return False
    return True


def _bounded_unsaturated(metrics: list[dict[str, str]]) -> bool:
    bounded_fields = (
        "a6_latent_activation_mean_tick",
        "a6_latent_focus_mean_tick",
        "a6_latent_fatigue_mean_tick",
        "a6_artifact_novelty_tick",
        "a6_artifact_coherence_tick",
        "a6_artifact_actionability_tick",
        "a6_artifact_provenance_debt_tick",
        "a6_artifact_risk_tick",
        "a6_artifact_contradiction_tick",
        "a6_artifact_readiness_tick",
        "a6_artifact_implementation_maturity_tick",
        "a6_artifact_communication_maturity_tick",
    )
    for row in metrics:
        if any(not 0.0 <= _number(row, field) <= 1.0 for field in bounded_fields):
            return False
        if not -1.0 <= _number(row, "a6_latent_prediction_error_mean_tick") <= 1.0:
            return False
    final_values = [_number(metrics[-1], field) for field in bounded_fields]
    return any(0.05 < value < 0.95 for value in final_values)


def _candidate_rate(rows: list[dict[str, Any]]) -> float:
    return _count_true(rows, "candidate") / len(rows) if rows else 0.0


def _boolean_rate(rows: list[dict[str, Any]], field: str) -> float:
    return _count_true(rows, field) / len(rows) if rows else 0.0


def _count_true(rows: list[dict[str, Any]], field: str) -> int:
    return sum(1 for row in rows if bool(row[field]))


def _mean_values_float(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def _matched_mean_delta(
    logistic_rows: list[dict[str, Any]],
    control_rows: list[dict[str, Any]],
    field: str,
) -> float:
    return round(
        _mean_values_float([float(row[field]) for row in logistic_rows])
        - _mean_values_float([float(row[field]) for row in control_rows]),
        6,
    )


def _matched_mean_improvement(
    logistic_rows: list[dict[str, Any]],
    control_rows: list[dict[str, Any]],
    field: str,
) -> float:
    return round(
        _mean_values_float([float(row[field]) for row in control_rows])
        - _mean_values_float([float(row[field]) for row in logistic_rows]),
        6,
    )


def _functional_candidate_gate_status(
    *,
    condition: str,
    candidate_rate: float,
    matched_control_candidate_rate: float,
) -> str:
    if condition != "logistic":
        return "control_candidate_rate_reported"
    if candidate_rate <= 0.0:
        return "fail_closed_no_logistic_candidates"
    if matched_control_candidate_rate >= candidate_rate:
        return "fail_closed_controls_match_or_exceed"
    return "candidate_exceeds_controls_smoke_only"


def _functional_candidate_interpretation(gate_status: str) -> str:
    if gate_status == "candidate_exceeds_controls_smoke_only":
        return "functional candidate count exceeds controls, but smoke scale still bars promotion language"
    if gate_status == "fail_closed_controls_match_or_exceed":
        return "linear or shuffled controls pass at similar or higher rates; use matched excess-over-control scoring before refinement"
    if gate_status == "fail_closed_no_logistic_candidates":
        return "logistic appraisal produced no functional smoke candidates"
    return "control candidate count reported for matched excess-over-control comparison"


def _bounded_prediction_resource_rows(
    runs: list[dict[str, Any]],
    residual_preflight_rows: list[dict[str, Any]],
    residual_contrast_rollup_rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    observed_resource_conditions = sorted(
        {
            _A6_BOUNDED_RESOURCE_CONDITION_MAP.get(str(row["condition"]), "")
            for row in runs
        }
        - {""}
    )
    missing_resource_conditions = [
        condition
        for condition in _A6_BOUNDED_RESOURCE_REQUIRED_CONDITIONS
        if condition not in observed_resource_conditions
    ]
    replay_status = (
        "present"
        if "budget_matched_prediction_replay" in observed_resource_conditions
        else "missing_required_budget_matched_replay_control"
    )
    gate_status = (
        "schema_only_fail_closed_missing_resource_conditions"
        if missing_resource_conditions
        else "schema_ready_requires_preregistered_result_run"
    )
    by_condition = {
        condition: [row for row in runs if str(row["condition"]) == condition]
        for condition in sorted({str(row["condition"]) for row in runs})
    }
    residual_by_condition = {
        condition: [
            row
            for row in residual_preflight_rows
            if str(row["condition"]) == condition
            and str(row["outcome_field"])
            in _A6_BOUNDED_RESOURCE_PRIMARY_VECTOR_FIELDS
        ]
        for condition in by_condition
    }
    linear_runs = by_condition.get("linear", [])
    logistic_runs = by_condition.get("logistic", [])
    linear_prediction_error = _mean_available(
        [row.get("final_latent_prediction_error_abs_mean", "") for row in linear_runs]
    )
    logistic_prediction_error = _mean_available(
        [row.get("final_latent_prediction_error_abs_mean", "") for row in logistic_runs]
    )
    forecast_delta = (
        round(float(linear_prediction_error) - float(logistic_prediction_error), 6)
        if linear_prediction_error != "" and logistic_prediction_error != ""
        else ""
    )
    linear_rollups = [
        row
        for row in residual_contrast_rollup_rows
        if row["contrast"] == "logistic_vs_linear"
        and row["outcome_field"] in _A6_BOUNDED_RESOURCE_PRIMARY_VECTOR_FIELDS
    ]
    recurrence_excess = _rounded_mean(
        [
            float(row["mean_residual_lag1_autocorrelation_delta"])
            for row in linear_rollups
            if row.get("mean_residual_lag1_autocorrelation_delta", "") != ""
        ]
    )
    compression_excess = _rounded_mean(
        [
            -float(row["mean_residual_sign_change_count_delta"])
            for row in linear_rollups
            if row.get("mean_residual_sign_change_count_delta", "") != ""
        ]
    )
    rows: list[dict[str, Any]] = []
    for condition, condition_runs in by_condition.items():
        seed_count = len({int(row["seed"]) for row in condition_runs})
        confound_r2_values = []
        control_fields = set()
        for residual_row in residual_by_condition.get(condition, []):
            raw_variance = residual_row.get("raw_variance", "")
            residual_variance = residual_row.get("residual_variance", "")
            if raw_variance not in {"", None} and residual_variance not in {"", None}:
                raw_value = float(raw_variance)
                if raw_value > 0:
                    confound_r2_values.append(
                        max(0.0, min(1.0, 1.0 - float(residual_variance) / raw_value))
                    )
            control_fields.update(
                field
                for field in str(residual_row.get("control_fields_used", "")).split("|")
                if field
            )
        prediction_spend = _mean_available(
            [row.get("prediction_budget_spent_total", "") for row in condition_runs]
        )
        action_opportunity = _mean_available(
            [row.get("action_opportunity_total", "") for row in condition_runs]
        )
        artifact_utility = _mean_available(
            [row.get("final_artifact_utility", "") for row in condition_runs]
        )
        rows.append(
            {
                "condition": condition,
                "resource_gate_condition": _A6_BOUNDED_RESOURCE_CONDITION_MAP.get(
                    condition,
                    "unmapped_existing_a6_condition",
                ),
                "seed_count": seed_count,
                "observed_resource_conditions": "|".join(observed_resource_conditions),
                "missing_resource_conditions": "|".join(missing_resource_conditions),
                "primary_residual_vector_fields": "|".join(
                    _A6_BOUNDED_RESOURCE_PRIMARY_VECTOR_FIELDS
                ),
                "control_fields_used": "|".join(sorted(control_fields)),
                "mean_confound_r2": _rounded_mean(confound_r2_values),
                "residual_recurrence_excess_vs_linear": recurrence_excess
                if condition == "logistic"
                else "",
                "residual_compression_excess_vs_linear": compression_excess
                if condition == "logistic"
                else "",
                "nonlinear_vs_linear_forecast_delta": forecast_delta
                if condition == "logistic"
                else "",
                "budget_efficiency_per_prediction_spend": _resource_efficiency(
                    artifact_utility,
                    prediction_spend,
                ),
                "budget_efficiency_per_work_opportunity_sacrificed": _resource_efficiency(
                    artifact_utility,
                    action_opportunity,
                ),
                "budget_matched_replay_control_status": replay_status,
                "gate_status": gate_status,
                "interpretation": _bounded_prediction_resource_interpretation(
                    gate_status,
                    replay_status,
                ),
            }
        )
    return rows


def _resource_efficiency(numerator: Any, denominator: Any) -> str:
    if numerator in {"", None} or denominator in {"", None}:
        return ""
    denominator_value = float(denominator)
    if denominator_value == 0:
        return ""
    return str(round(float(numerator) / denominator_value, 6))


def _bounded_prediction_resource_interpretation(
    gate_status: str,
    replay_status: str,
) -> str:
    if replay_status != "present":
        return "bounded prediction-resource gate is schema-only here; required budget-matched replay control is absent"
    if gate_status == "schema_ready_requires_preregistered_result_run":
        return "schema has required condition labels; result-bearing run still requires preregistered execution"
    return "bounded prediction-resource gate remains fail-closed until all preregistered resource conditions are present"


def _with_a6_derived_fields(row: dict[str, str]) -> dict[str, str]:
    enriched = dict(row)
    enriched["a6_artifact_utility_tick"] = str(_artifact_utility(row))
    for action in _A6_ACTIONS:
        enriched[f"action_{action}_tick"] = str(_action_tick(row, action))
    return enriched


def _action_tick(row: dict[str, str], action: str) -> float:
    suffix = f"_{action}_tick"
    return sum(
        _number(row, field)
        for field in row
        if field.startswith("role_") and field.endswith(suffix)
    )


def _empty_residual_row(
    condition: str,
    seed: int,
    outcome_field: str,
    row_count: int,
    control_fields: tuple[str, ...],
    missing_fields: tuple[str, ...],
) -> dict[str, Any]:
    return {
        "condition": condition,
        "seed": seed,
        "outcome_field": outcome_field,
        "row_count": row_count,
        "control_count": len(control_fields),
        "degrees_of_freedom": row_count - len(control_fields) - 1,
        "status": "missing_controls_or_outcome_preflight",
        "missing_control_fields": "|".join(missing_fields),
        "control_fields_used": "|".join(control_fields),
        "raw_variance": "",
        "residual_variance": "",
        "raw_lag1_autocorrelation": "",
        "residual_lag1_autocorrelation": "",
    }


def _ridge_residuals(values: list[float], controls: list[list[float]]) -> list[float]:
    return _ridge_fit(values, controls)["residuals"]


def _ridge_fit(values: list[float], controls: list[list[float]]) -> dict[str, list[float]]:
    if not values:
        return {"fitted": [], "residuals": []}
    design = [[1.0, *row] for row in controls]
    if not design or not design[0]:
        mean_value = sum(values) / len(values)
        fitted = [mean_value for _ in values]
        return {
            "fitted": fitted,
            "residuals": [value - mean_value for value in values],
        }
    coefficient_count = len(design[0])
    xtx = [
        [
            sum(design[row][left] * design[row][right] for row in range(len(design)))
            for right in range(coefficient_count)
        ]
        for left in range(coefficient_count)
    ]
    xty = [
        sum(design[row][column] * values[row] for row in range(len(design)))
        for column in range(coefficient_count)
    ]
    for index in range(1, coefficient_count):
        xtx[index][index] += 1e-9
    coefficients = _solve_linear_system(xtx, xty)
    fitted = [
        sum(
            coefficients[column] * design[row_index][column]
            for column in range(coefficient_count)
        )
        for row_index, _ in enumerate(values)
    ]
    return {
        "fitted": fitted,
        "residuals": [
            value - fitted_value for value, fitted_value in zip(values, fitted, strict=True)
        ],
    }


def _solve_linear_system(matrix: list[list[float]], values: list[float]) -> list[float]:
    size = len(values)
    augmented = [list(matrix[row]) + [values[row]] for row in range(size)]
    for column in range(size):
        pivot = max(range(column, size), key=lambda row: abs(augmented[row][column]))
        if abs(augmented[pivot][column]) < 1e-12:
            augmented[column][column] += 1e-9
            pivot = column
        augmented[column], augmented[pivot] = augmented[pivot], augmented[column]
        divisor = augmented[column][column]
        if abs(divisor) < 1e-12:
            continue
        augmented[column] = [value / divisor for value in augmented[column]]
        for row in range(size):
            if row == column:
                continue
            factor = augmented[row][column]
            if factor:
                augmented[row] = [
                    augmented[row][col] - factor * augmented[column][col]
                    for col in range(size + 1)
                ]
    return [augmented[row][-1] for row in range(size)]


def _variance(values: list[float]) -> float:
    if not values:
        return 0.0
    mean_value = sum(values) / len(values)
    return sum((value - mean_value) ** 2 for value in values) / len(values)


def _lag1_autocorrelation(values: list[float]) -> float:
    if len(values) < 2:
        return 0.0
    mean_value = sum(values) / len(values)
    numerator = sum(
        (values[index] - mean_value) * (values[index - 1] - mean_value)
        for index in range(1, len(values))
    )
    denominator = sum((value - mean_value) ** 2 for value in values)
    return numerator / denominator if denominator else 0.0


def _summary(
    compare_path: Path,
    runs: list[dict[str, Any]],
    manifest_rows: list[dict[str, Any]],
    control_delta_rows: list[dict[str, Any]],
    residual_preflight_rows: list[dict[str, Any]],
    residual_timeseries_rows: list[dict[str, Any]],
    residual_contrast_summary_rows: list[dict[str, Any]],
    residual_contrast_rollup_rows: list[dict[str, Any]],
    control_summary_rows: list[dict[str, Any]],
    comparison_consistency_rows: list[dict[str, Any]],
    effects_consistency_rows: list[dict[str, Any]],
    artifact_provenance_rows: list[dict[str, Any]],
    source_accounting_rows: list[dict[str, Any]],
    pilot_null_gate_rows: list[dict[str, Any]],
    functional_candidate_gate_rows: list[dict[str, Any]],
    bounded_prediction_resource_rows: list[dict[str, Any]],
    missing_required_fields: set[str],
) -> str:
    conditions = sorted({str(row["condition"]) for row in runs})
    seeds = sorted({int(row["seed"]) for row in runs})
    lines = [
        "# A6 Logistic-Appraisal Analysis Gate",
        "",
        f"- compare dir: {compare_path}",
        f"- run artifacts read: {len(runs)}",
        f"- conditions observed: {', '.join(conditions)}",
        f"- seeds observed: {', '.join(str(seed) for seed in seeds)}",
        "- reran simulations: no",
        f"- paired control delta rows: {len(control_delta_rows)}",
        f"- residual preflight rows: {len(residual_preflight_rows)}",
        f"- residual timeseries rows: {len(residual_timeseries_rows)}",
        f"- residual contrast summary rows: {len(residual_contrast_summary_rows)}",
        f"- residual contrast rollup rows: {len(residual_contrast_rollup_rows)}",
        f"- control summary rows: {len(control_summary_rows)}",
        f"- comparison consistency rows: {len(comparison_consistency_rows)}",
        f"- effects consistency rows: {len(effects_consistency_rows)}",
        f"- artifact provenance rows: {len(artifact_provenance_rows)}",
        f"- source accounting rows: {len(source_accounting_rows)}",
        f"- A6.1 pilot null gate rows: {len(pilot_null_gate_rows)}",
        f"- A6 functional candidate gate rows: {len(functional_candidate_gate_rows)}",
        "- A6 bounded prediction-resource residual-state summary rows: "
        f"{len(bounded_prediction_resource_rows)}",
        "- status: read-only control/residual preflight; not promotion evidence",
        "- missing required fields: "
        + ("none" if not missing_required_fields else ", ".join(sorted(missing_required_fields))),
        "",
        "## Control Levels",
        "",
    ]
    for row in manifest_rows:
        lines.append(f"- {row['control_level']}: {row['status']}")
    lines.extend(
        [
            "",
            "## Gate Reminder",
            "",
            "- Do not promote A6 from smoke artifacts alone.",
            "- Paired deltas are logistic minus the named control within the same seed.",
            "- Residual preflight uses existing per-tick smoke metrics only; underdetermined smoke-scale rows are not recurrence evidence.",
            "- Residual timeseries rows expose fitted and residual values for audit only, not as a recurrence claim.",
            "- Residual contrast summary rows aggregate per-seed residual variance, lag-1 autocorrelation, and sign-change deltas for audit only.",
            "- Residual contrast rollup rows summarize cross-seed direction agreement for audit only; they do not promote A6.",
            "- Comparison consistency preflight checks aggregate CSV arithmetic against existing run artifacts only.",
            "- Effects consistency preflight checks aggregate effect deltas against comparison CSV condition means only.",
            "- Artifact provenance rows attribute same-tick artifact field deltas to recorded A6 events/actions for alias-risk audit only.",
            "- Source accounting rows audit A6.1 required fields, artifact-delta reconstruction, and per-source shares for schema/control eligibility only.",
            "- A6.1 pilot null gate rows compare logistic endpoints to source-preserving nulls with backlog-adjusted productivity; they are smoke-scale gate diagnostics only.",
            "- A6 functional candidate gate rows require bounded unsaturated dynamics, nonperiodic role/action traces, artifact/debt/risk/prediction-error movement, and component matched excess-over-control scoring.",
            "- A6 bounded prediction-resource rows are schema/analyzer scaffolding for the 2026-07-02 pivot; missing zero/high/replay resource controls keep the gate fail-closed.",
            "- Residual latent/artifact recurrence must beat linear, phase-shuffled, and threshold-shuffled controls.",
            "- Load, service, action opportunity, work budget, clock trend, and queue variables remain accounting controls.",
            "",
        ]
    )
    return "\n".join(lines)


def _ensure_output_paths_available(output_path: Path) -> None:
    if output_path.exists() and not output_path.is_dir():
        raise FileExistsError(f"Output path {output_path} exists and is not a directory.")
    collisions = [
        output_name
        for output_name in _OUTPUT_NAMES
        if (output_path / output_name).exists()
    ]
    if collisions:
        names = ", ".join(collisions)
        raise FileExistsError(f"Output path {output_path} already contains A6 analysis artifacts: {names}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Analyze existing A6 logistic-appraisal artifacts without rerunning simulations."
    )
    parser.add_argument(
        "--compare-dir",
        default=str(DEFAULT_A6_COMPARE_DIR),
        help="Directory containing existing A6 run artifact subdirectories.",
    )
    parser.add_argument(
        "--out",
        default=str(DEFAULT_A6_ANALYSIS_OUT_DIR),
        help="Output directory for derived A6 analysis skeleton artifacts.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    run_a6_logistic_appraisal_analysis(args.compare_dir, args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
