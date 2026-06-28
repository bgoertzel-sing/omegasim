"""Frozen A7.2 delayed artifact/endogenous-prediction contract.

This module contains schema names and smoke constants only. It intentionally
does not implement simulator mechanics or result-bearing analysis.
"""

from __future__ import annotations


A7_2_ACTIONS = (
    "predict",
    "work",
    "review",
    "synthesize",
)
A7_2_STATE_FIELDS = (
    "forecast_error_lag1",
    "forecast_uncertainty_lag1",
    "prediction_spend",
    "lost_work_opportunity_from_prediction",
    "fatigue",
    "adaptive_prediction_threshold",
    "adaptive_work_threshold",
    "adaptive_review_threshold",
    "adaptive_synthesis_threshold",
    "artifact_readiness",
    "artifact_coherence",
    "artifact_contradiction",
    "artifact_risk",
    "artifact_revision_pressure",
    "selected_action",
    "predict_utility",
    "work_utility",
    "review_utility",
    "synthesize_utility",
    "delayed_forecast_update_queue",
    "delayed_artifact_update_queue",
    "source_ledger_forecast_error",
    "source_ledger_artifact",
    "source_ledger_queue_accounting",
)
A7_2_SOURCE_LEDGER_FIELDS = (
    "source_ledger_forecast_error",
    "source_ledger_artifact",
    "source_ledger_queue_accounting",
    "source_ledger_artifact_readiness_delta",
    "source_ledger_artifact_coherence_delta",
    "source_ledger_artifact_contradiction_delta",
    "source_ledger_artifact_risk_delta",
    "source_ledger_clip_residual",
)
A7_2_CONTROL_FIELDS = (
    "tick",
    "demand_phase",
    "task_arrivals",
    "service_capacity",
    "action_opportunity",
    "work_budget",
    "prediction_spend",
    "remaining_work_budget",
    "backlog",
    "queued_age",
    "completion_fraction",
    "starvation",
    "prediction_spend_volatility",
    "work_budget_volatility",
    "source_ledger_queue_accounting",
)
A7_2_EVENT_FIELDS = (
    "tick",
    "agent_id",
    "event_type",
    "a7_2_condition",
    "selected_action",
    "forecast_update_created_tick",
    "forecast_update_visible_tick",
    "artifact_update_created_tick",
    "artifact_update_visible_tick",
    "prediction_work_cost",
    *A7_2_SOURCE_LEDGER_FIELDS,
)
A7_2_METRIC_FIELDS = tuple(
    f"a7_2_{field}" for field in A7_2_STATE_FIELDS
) + A7_2_CONTROL_FIELDS
A7_2_CONDITIONS = (
    "zero_budget_reactive",
    "intermediate_endogenous_delayed_prediction",
    "high_budget_oracle_smoothing",
    "amplitude_matched_linear_delayed_prediction",
    "same_tick_logistic_prediction",
    "phase_shuffled_lag_input",
    "threshold_shuffled",
    "source_preserving_artifact_label_shuffle",
    "spend_only_replay",
    "artifact_off_source_ledger_null",
)
A7_2_POSITIVE_CONDITION = "intermediate_endogenous_delayed_prediction"
A7_2_NULL_CONDITIONS = tuple(
    condition for condition in A7_2_CONDITIONS if condition != A7_2_POSITIVE_CONDITION
)
A7_2_SMOKE_PARAMETERS = {
    "horizon_ticks": 48,
    "forecast_delay_ticks": 2,
    "artifact_delay_ticks": 3,
    "prediction_cost_work_fraction": 0.25,
    "max_prediction_work_fraction_per_tick": 0.40,
    "fatigue_decay": 0.20,
    "fatigue_increment_predict": 0.08,
    "fatigue_increment_work": 0.05,
    "fatigue_increment_review": 0.04,
    "fatigue_increment_synthesize": 0.06,
    "threshold_learning_rate_error": 0.05,
    "threshold_recovery_rate": 0.02,
    "threshold_min": -2.0,
    "threshold_max": 2.0,
    "utility_slope_predict": 1.20,
    "utility_slope_work": 1.00,
    "utility_slope_review": 1.10,
    "utility_slope_synthesize": 1.15,
    "artifact_clip_min": 0.0,
    "artifact_clip_max": 1.0,
    "artifact_decay": 0.10,
}
A7_2_PRIMARY_ENDPOINTS = (
    "forecast_skill_per_prediction_spend",
    "full_accounting_residual_lag1_predictability",
    "nearest_neighbor_residual_forecast_error",
    "delay_embedding_recurrence_score",
    "residual_transition_compressibility",
    "lead_lag_mediation_error_to_spend_to_artifact_to_residual",
    "source_ledger_reconstruction_status",
)
A7_2_PRODUCTIVITY_GUARDRAILS = {
    "completion_fraction_delta_min": -0.05,
    "backlog_delta_max": 0.10,
    "queued_age_delta_max": 0.10,
    "starvation_delta_max": 0.03,
    "prediction_spend_volatility_delta_max": 0.15,
    "work_budget_volatility_delta_max": 0.15,
}


def a7_2_required_metric_fields() -> tuple[str, ...]:
    """Return the minimum metrics schema declared by the A7.2 contract."""

    return A7_2_METRIC_FIELDS


def a7_2_required_event_fields() -> tuple[str, ...]:
    """Return the minimum event schema declared by the A7.2 contract."""

    return A7_2_EVENT_FIELDS
