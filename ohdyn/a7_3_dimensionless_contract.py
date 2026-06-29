"""Frozen A7.3 one-hive dimensionless delayed-dynamics contract.

This module contains schema names, smoke constants, and source-invariant names
only. It intentionally does not make scientific claims about dynamics.
"""

from __future__ import annotations


A7_3_ACTIONS = (
    "predict",
    "work",
    "review",
    "synthesize",
    "rest",
)
A7_3_DIMENSIONLESS_CONTROLS = (
    "rho",
    "delta",
    "mu",
    "kappa",
    "nu",
    "chi",
    "eta",
)
A7_3_CONDITIONS = (
    "low_gain_contraction",
    "full_delayed_logistic",
    "no_delay_same_tick_blocked",
    "amplitude_matched_linear",
    "artifact_off",
    "cost_free_prediction",
    "spend_only_replay",
    "phase_shuffled_lag",
    "threshold_shuffled",
)
A7_3_POSITIVE_CONDITION = "full_delayed_logistic"
A7_3_NULL_CONDITIONS = tuple(
    condition for condition in A7_3_CONDITIONS if condition != A7_3_POSITIVE_CONDITION
)
A7_3_SMOKE_PARAMETERS = {
    "seeds": (1, 2),
    "horizon_ticks": 64,
    "agent_count": 15,
    "feedback_delay_ticks": 3,
    "relaxation_time_ticks": 6,
    "artifact_memory_decay": 0.12,
    "threshold_recovery_rate": 0.02,
    "threshold_learning_rate": 0.05,
    "prediction_cost_work_fraction": 0.25,
    "max_prediction_work_fraction_per_tick": 0.35,
    "nonlinear_coupling_gain": 1.35,
    "low_gain_coupling_gain": 0.25,
    "linear_gain": 0.70,
    "peer_coupling_spread": 0.20,
    "noise_to_signal": 0.01,
    "artifact_clip_min": 0.0,
    "artifact_clip_max": 1.0,
}
A7_3_LIFTED_STATE_FIELDS = (
    "tick",
    "agent_role_activity_predict",
    "agent_role_activity_work",
    "agent_role_activity_review",
    "agent_role_activity_synthesize",
    "agent_role_activity_rest",
    "delayed_agent_role_activity_predict",
    "delayed_agent_role_activity_work",
    "delayed_agent_role_activity_review",
    "delayed_agent_role_activity_synthesize",
    "delayed_agent_role_activity_rest",
    "peer_activity_lag_predict",
    "peer_activity_lag_work",
    "peer_activity_lag_review",
    "peer_activity_lag_synthesize",
    "peer_activity_lag_rest",
    "artifact_readiness",
    "artifact_coherence",
    "contradiction_risk",
    "prediction_error",
    "prediction_uncertainty",
    "fatigue",
    "adaptive_threshold_predict",
    "adaptive_threshold_work",
    "adaptive_threshold_review",
    "adaptive_threshold_synthesize",
    "adaptive_threshold_rest",
    "work_backlog",
    "prediction_spend",
    "lost_work_opportunity_from_prediction",
    "memory_pressure",
    "task_arrivals",
    "demand_phase",
)
A7_3_CONTROL_FIELDS = (
    "tick",
    "demand_phase",
    "task_arrivals",
    "service_capacity",
    "action_opportunity",
    "work_budget",
    "work_backlog",
    "queued_age",
    "completion_fraction",
    "prediction_spend",
    "lost_work_opportunity_from_prediction",
    "memory_pressure",
)
A7_3_SOURCE_LEDGER_FIELDS = (
    "source_ledger_delay_integrity",
    "source_ledger_peer_activity_lag",
    "source_ledger_artifact_memory",
    "source_ledger_prediction_cost",
    "source_ledger_queue_accounting",
    "source_ledger_threshold_update",
    "source_ledger_phase_shuffle",
    "source_ledger_threshold_shuffle",
    "source_ledger_clip_residual",
)
A7_3_EVENT_FIELDS = (
    "tick",
    "condition",
    "seed",
    "agent_id",
    "event_type",
    "selected_action",
    "feedback_created_tick",
    "feedback_visible_tick",
    "same_tick_influence_blocked",
    "prediction_work_cost",
    *A7_3_SOURCE_LEDGER_FIELDS,
)
A7_3_METRIC_FIELDS = tuple(
    dict.fromkeys(
        (
            *A7_3_DIMENSIONLESS_CONTROLS,
            *A7_3_LIFTED_STATE_FIELDS,
            *A7_3_CONTROL_FIELDS,
            *A7_3_SOURCE_LEDGER_FIELDS,
        )
    )
)
A7_3_SOURCE_LEDGER_CSV_FIELDS = (
    "tick",
    "condition",
    "seed",
    *A7_3_SOURCE_LEDGER_FIELDS,
)
A7_3_MECHANICS_MANIFEST_FIELDS = (
    "condition",
    "seed",
    "config",
    "run_dir",
    "tick_count",
    "metrics_rows",
    "events_rows",
    "source_ledger_rows",
    "lifted_state_rows",
    "mechanics_status",
    "scientific_status",
)
A7_3_PRIMARY_ENDPOINTS = (
    "residual_lifted_state_delay_embedding_recurrence",
    "nonlinear_vs_linear_residual_forecastability",
    "finite_time_divergence_low_gain_control",
    "phase_shuffle_recurrence_contrast",
    "threshold_shuffle_recurrence_contrast",
    "source_ledger_reconstruction_status",
    "boundedness_status",
    "productivity_guardrail_status",
)
A7_3_DELAY_SOURCE_INVARIANTS = (
    "feedback_visible_tick_greater_than_created_tick_unless_no_delay_control",
    "same_tick_influence_blocked_for_positive_condition",
    "peer_activity_lag_fields_populated_from_prior_tick",
    "artifact_updates_visible_only_after_feedback_delay",
    "spend_only_replay_preserves_prediction_work_deductions",
    "artifact_off_preserves_queue_accounting_controls",
)
A7_3_PRODUCTIVITY_GUARDRAILS = {
    "completion_fraction_min": 0.02,
    "work_backlog_max": 40.0,
    "prediction_spend_fraction_max": 0.45,
    "source_ledger_delay_integrity_required": "pass",
}
A7_3_VALIDATION_PARAMETERS = {
    "seeds": (1, 2),
    "horizon_ticks": 256,
    "minimum_rows_for_recurrence": 128,
    "train_fraction": 0.60,
    "holdout_fraction": 0.40,
    "embedding_lags": (1, 3, 6, 12),
    "recurrence_radius_quantile": 0.10,
    "surrogate_repetitions": 32,
    "local_divergence_neighbor_count": 8,
    "promotion_requires_all_nulls": True,
}
A7_3_VALIDATION_TARGET_FIELDS = (
    "artifact_readiness",
    "artifact_coherence",
    "contradiction_risk",
    "prediction_error",
    "prediction_uncertainty",
    "fatigue",
    "memory_pressure",
    "work_backlog",
)
A7_3_VALIDATION_RESIDUAL_CONTROLS = (
    "demand_phase",
    "task_arrivals",
    "service_capacity",
    "action_opportunity",
    "work_budget",
    "work_backlog",
    "queued_age",
    "completion_fraction",
    "prediction_spend",
    "lost_work_opportunity_from_prediction",
    "memory_pressure",
)
A7_3_VALIDATION_ENDPOINTS = (
    "source_ledger_delay_reconstruction_pass",
    "bounded_lifted_state_pass",
    "productivity_guardrail_pass",
    "heldout_residual_forecast_improvement",
    "delay_embedding_recurrence_rate",
    "phase_shuffle_surrogate_contrast",
    "threshold_shuffle_surrogate_contrast",
    "linear_control_forecastability_contrast",
    "finite_time_local_divergence_contrast",
)
A7_3_VALIDATION_PROMOTION_GATES = (
    "preflight_manifest_status_eligible",
    "all_conditions_and_seeds_present",
    "all_source_ledgers_pass",
    "boundedness_passes_without_saturation_or_blowup",
    "productivity_passes_for_positive_and_null_conditions",
    "full_mechanism_beats_low_gain_contraction",
    "full_mechanism_beats_no_delay_same_tick_blocked",
    "full_mechanism_beats_amplitude_matched_linear",
    "full_mechanism_beats_artifact_off",
    "full_mechanism_beats_cost_free_prediction",
    "full_mechanism_beats_spend_only_replay",
    "full_mechanism_beats_phase_shuffled_lag",
    "full_mechanism_beats_threshold_shuffled",
    "finite_time_divergence_exceeds_low_gain_baseline",
)


def a7_3_required_metric_fields() -> tuple[str, ...]:
    """Return the minimum metrics schema declared by the A7.3 contract."""

    return A7_3_METRIC_FIELDS


def a7_3_required_event_fields() -> tuple[str, ...]:
    """Return the minimum event schema declared by the A7.3 contract."""

    return A7_3_EVENT_FIELDS
