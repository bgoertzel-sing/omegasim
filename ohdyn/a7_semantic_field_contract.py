"""Frozen A7 semantic-field implementation gate contract.

This module intentionally contains no simulator mechanics. It centralizes the
state fields, source ledgers, null names, equations, and schema additions that
future A7 simulator/analyzer code must use without silent drift.
"""

from __future__ import annotations


A7_FIELD_VALUES = (
    "semantic_novelty",
    "semantic_coherence",
    "semantic_contradiction",
    "semantic_risk",
    "artifact_readiness",
    "trust_weighted_salience",
)
A7_PREDICTION_FIELDS = (
    "prediction_budget_spent",
    "prediction_error",
)
A7_STATE_FIELDS = (
    *A7_FIELD_VALUES,
    *A7_PREDICTION_FIELDS,
)
A7_SOURCE_COMPONENTS = (
    "ambient_decay",
    "self_contribution",
    "peer_contribution",
    "artifact_handoff",
    "prediction_expenditure",
    "prediction_error",
    "queue_work_accounting",
    "semantic_noise",
    "clip_residual",
)
A7_SOURCE_DELTA_FIELDS = tuple(
    f"a7_delta_{source}" for source in A7_SOURCE_COMPONENTS
)
A7_CONTROL_FIELDS = (
    "tick",
    "queue_depth",
    "queue_delta_tick",
    "tasks_created_total",
    "tasks_completed_total",
    "a7_service_capacity_tick",
    "a7_action_opportunity_tick",
    "a7_work_budget_tick",
    "a7_work_actions_tick",
    "a7_prediction_actions_tick",
    "a7_handoff_attempts_tick",
    "a7_handoff_successes_tick",
    "a7_handoff_failures_tick",
)
A7_CONDITIONS = (
    "a7_logistic_semantic_coupling",
    "semantic_off_baseline",
    "amplitude_matched_linear_semantic_coupling",
    "source_preserving_semantic_label_shuffle",
    "semantic_field_phase_shuffle",
    "prediction_budget_timing_broken_matched_count_null",
)
A7_POSITIVE_CONDITION = "a7_logistic_semantic_coupling"
A7_NULL_CONDITIONS = tuple(
    condition for condition in A7_CONDITIONS if condition != A7_POSITIVE_CONDITION
)
A7_RNG_STREAMS = (
    "baseline_action_stream",
    "semantic_update_stream",
    "prediction_noise_stream",
    "semantic_control_shuffle_stream",
)
A7_UTILITY_EQUATIONS = (
    "linear: U_i(a,t)=b_a+w_a dot A(t-1)-c_pred spend_i(t)-c_fatigue fatigue_i(t)",
    "logistic: P_i(a,t)=sigmoid(beta_a*(U_i(a,t)-theta_i(t)))",
    "threshold: theta_i(t+1)=clip(theta_i(t)+eta_err*prediction_error_i(t)-eta_rest*idle_i(t))",
)
A7_UPDATE_EQUATIONS = (
    "field: A_k(t+1)=clip(rho_k*A_k(t)+sum_s delta_{k,s}(t)+epsilon_k(t))",
    "source: Delta A_k(t)=sum_s delta_{k,s}(t)+clip_residual_k(t)",
    "prediction_error: e_i(t)=target_peer_need_i(t+lead)-forecast_i(t)",
    "budget: prediction_budget_spent_i(t)<=prediction_budget_per_tick and competes with work budget",
)
A7_METRIC_FIELDS = tuple(
    f"a7_{field}_tick" for field in A7_STATE_FIELDS
) + tuple(f"a7_{field}_mean_tick" for field in A7_STATE_FIELDS)
A7_EVENT_FIELDS = (
    "tick",
    "agent_id",
    "event_type",
    "a7_condition",
    "a7_semantic_field",
    "a7_delta_total",
    *A7_SOURCE_DELTA_FIELDS,
)
A7_ANALYZER_COMPLETENESS_FIELDS = (
    "condition",
    "seed",
    "metrics_path",
    "events_path",
    "row_count",
    "required_field_status",
    "missing_required_fields",
    "source_reconstruction_status",
    "null_artifact_status",
    "status",
    "interpretation",
)
A7_ANALYZER_MANIFEST_FIELDS = (
    "compare_dir",
    "condition_count",
    "seed_count",
    "run_count",
    "status",
)
A7_ANALYZER_SMOKE_REPORT_FIELDS = (
    "condition",
    "seed",
    "field_variation_status",
    "varying_field_count",
    "max_field_range",
    "prediction_work_budget_competition_status",
    "prediction_spend_ticks",
    "work_budget_reduction_ticks",
    "total_prediction_budget_spent",
    "near_threshold_occupancy_status",
    "mean_near_threshold_occupancy",
    "max_near_threshold_occupancy",
    "source_reconstruction_status",
    "scientific_interpretation_status",
)
A7_ANALYZER_RESIDUAL_FIELDS = (
    "condition",
    "seed",
    "target_field",
    "row_count",
    "residualization_status",
    "missing_required_fields",
    "control_fields_used",
    "residual_variance",
    "lag1_autocorrelation",
    "linear_ar_forecast_mae",
    "nearest_neighbor_forecast_mae",
    "backlog_adjusted_productivity",
    "status",
    "interpretation",
)
A7_ANALYZER_NULL_CONTRAST_FIELDS = (
    "contrast",
    "seed",
    "control_condition",
    "target_field",
    "paired",
    "status",
    "positive_status",
    "control_status",
    "residual_variance_delta",
    "lag1_autocorrelation_delta",
    "linear_ar_forecast_mae_delta",
    "nearest_neighbor_forecast_mae_delta",
    "backlog_adjusted_productivity_delta",
    "gate_status",
    "interpretation",
)


def a7_required_metric_fields() -> tuple[str, ...]:
    """Return the minimum metrics schema required by the A7 analyzer gate."""

    return (*A7_METRIC_FIELDS, *A7_CONTROL_FIELDS)


def a7_required_event_fields() -> tuple[str, ...]:
    """Return the minimum event schema required for source reconstruction."""

    return A7_EVENT_FIELDS


def missing_fields(
    available_fields: set[str] | frozenset[str],
    required_fields: tuple[str, ...],
) -> tuple[str, ...]:
    """Return required fields absent from an artifact header."""

    return tuple(field for field in required_fields if field not in available_fields)
