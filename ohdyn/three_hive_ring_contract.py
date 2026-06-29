"""Frozen three-hive ring contract constants.

This module contains schema names and smoke constants only. It intentionally
does not implement multi-hive simulator mechanics, config loading, or analysis.
"""

from __future__ import annotations


THREE_HIVE_RING_HIVES = (
    "hive_a_explore_research",
    "hive_b_formalize_implement",
    "hive_c_synthesize_review",
)
THREE_HIVE_RING_EDGES = (
    "A_to_B",
    "B_to_C",
    "C_to_A",
)
THREE_HIVE_RING_EDGE_HIVES = (
    ("hive_a_explore_research", "hive_b_formalize_implement"),
    ("hive_b_formalize_implement", "hive_c_synthesize_review"),
    ("hive_c_synthesize_review", "hive_a_explore_research"),
)
THREE_HIVE_RING_ACTIONS = (
    "predict_cross_hive",
    "work_local",
    "review_inbound_artifact",
    "synthesize_outbound_artifact",
    "idle",
)
THREE_HIVE_RING_ROLE_BIASES = {
    "hive_a_explore_research": (
        "novelty_exploration",
        "contradiction_discovery",
    ),
    "hive_b_formalize_implement": (
        "readiness_formalization",
        "implementation_progress",
    ),
    "hive_c_synthesize_review": (
        "coherence_review",
        "risk_resolution",
        "synthesis",
    ),
}
THREE_HIVE_RING_STATE_FIELDS = (
    "local_backlog",
    "local_queued_age",
    "local_service_capacity",
    "local_action_opportunity",
    "local_work_budget",
    "local_prediction_spend",
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
    "inbound_artifact_readiness_lag",
    "inbound_artifact_coherence_lag",
    "inbound_artifact_contradiction_lag",
    "inbound_artifact_risk_lag",
    "cross_hive_forecast_error_lag",
    "cross_hive_forecast_uncertainty_lag",
    "transfer_opportunity",
    "accepted_transfer_count",
    "rejected_transfer_count",
    "selected_action",
)
THREE_HIVE_RING_EDGE_FIELDS = (
    "source_hive",
    "target_hive",
    "proposed_transfer_volume",
    "accepted_transfer_volume",
    "transfer_opportunity",
    "transfer_delay_ticks",
    "membrane_acceptance",
    "cross_hive_prediction_spend",
    "cross_hive_prediction_error",
    "artifact_payload_readiness",
    "artifact_payload_coherence",
    "artifact_payload_contradiction",
    "artifact_payload_risk",
    "source_ledger_transfer",
    "source_ledger_prediction",
    "source_ledger_queue_accounting",
    "source_ledger_artifact_delta",
)
THREE_HIVE_RING_SOURCE_LEDGER_FIELDS = (
    "source_ledger_transfer",
    "source_ledger_prediction",
    "source_ledger_queue_accounting",
    "source_ledger_artifact_delta",
    "source_ledger_artifact_readiness_delta",
    "source_ledger_artifact_coherence_delta",
    "source_ledger_artifact_contradiction_delta",
    "source_ledger_artifact_risk_delta",
    "source_ledger_clip_residual",
)
THREE_HIVE_RING_CONDITIONS = (
    "no_coupling",
    "delayed_logistic_ring",
    "heterogeneous_delay_logistic_ring",
    "amplitude_matched_linear_delayed_ring",
    "same_tick_logistic_ring",
    "target_shuffled_transfer",
    "phase_shuffled_transfer",
    "threshold_shuffled_ring",
    "transfer_opportunity_matched_replay",
    "spend_only_cross_hive_prediction_replay",
    "artifact_off_source_ledger_null",
    "source_preserving_artifact_label_shuffle",
    "high_budget_oracle_smoothing",
)
THREE_HIVE_RING_POSITIVE_CONDITION = "delayed_logistic_ring"
THREE_HIVE_RING_ROBUSTNESS_CONDITION = "heterogeneous_delay_logistic_ring"
THREE_HIVE_RING_POSITIVE_CONTROL = "high_budget_oracle_smoothing"
THREE_HIVE_RING_NULL_CONDITIONS = tuple(
    condition
    for condition in THREE_HIVE_RING_CONDITIONS
    if condition
    not in (
        THREE_HIVE_RING_POSITIVE_CONDITION,
        THREE_HIVE_RING_ROBUSTNESS_CONDITION,
        THREE_HIVE_RING_POSITIVE_CONTROL,
    )
)
THREE_HIVE_RING_SMOKE_PARAMETERS = {
    "seeds": (1, 2),
    "horizon_ticks": 72,
    "ring_hives": 3,
    "ring_edges": ("A_to_B", "B_to_C", "C_to_A"),
    "observation_delay_ticks": 1,
    "transfer_delay_ticks": 3,
    "forecast_delay_ticks": 2,
    "artifact_relaxation_time_ticks": 6,
    "artifact_decay": 0.12,
    "prediction_cost_work_fraction": 0.25,
    "max_prediction_work_fraction_per_tick": 0.35,
    "transfer_cost_work_fraction": 0.15,
    "max_transfer_work_fraction_per_tick": 0.25,
    "fatigue_decay": 0.18,
    "fatigue_increment_predict": 0.08,
    "fatigue_increment_work": 0.05,
    "fatigue_increment_review": 0.04,
    "fatigue_increment_synthesize": 0.06,
    "threshold_learning_rate_error": 0.05,
    "threshold_recovery_rate": 0.02,
    "threshold_min": -2.0,
    "threshold_max": 2.0,
    "utility_slope_cross_predict": 1.15,
    "utility_slope_work": 1.00,
    "utility_slope_review": 1.10,
    "utility_slope_synthesize": 1.15,
    "membrane_permeability": 0.55,
    "artifact_clip_min": 0.0,
    "artifact_clip_max": 1.0,
}
THREE_HIVE_RING_DIMENSIONLESS_MANIFEST_FIELDS = (
    "coupling_gain",
    "delay_relaxation_ratio",
    "prediction_cost_ratio",
    "transfer_cost_ratio",
    "memory_persistence",
    "threshold_adaptation_ratio",
)
THREE_HIVE_RING_PRIMARY_ENDPOINTS = (
    "residual_cross_hive_delay_embedding_recurrence",
    "residual_phase_differentiated_motif_score",
    "lead_lag_mediation_neighbor_artifact_to_local_action_to_local_artifact",
    "residual_target_predictability_from_lagged_neighbor_artifact",
    "residual_transition_compressibility",
    "source_ledger_reconstruction_status",
    "productivity_guardrail_status",
)
THREE_HIVE_RING_RESIDUAL_CONTROLS = (
    "tick",
    "demand_phase",
    "local_task_arrivals",
    "local_service_capacity",
    "local_action_opportunity",
    "local_work_budget",
    "local_backlog",
    "local_queued_age",
    "local_prediction_spend",
    "lost_work_opportunity_from_prediction",
    "proposed_transfer_volume",
    "accepted_transfer_volume",
    "transfer_opportunity",
    "transfer_work_cost",
    "role_bias",
    "source_hive",
    "target_hive",
)
THREE_HIVE_RING_PRODUCTIVITY_GUARDRAILS = {
    "mean_completion_fraction_min_baseline_ratio": 0.80,
    "mean_backlog_max_baseline_ratio": 1.25,
    "mean_queued_age_max_baseline_ratio": 1.25,
    "prediction_or_transfer_cost_fraction_max": 0.45,
    "accepted_transfer_volume_min_per_directed_edge": 1,
    "source_ledger_reconstruction_status_required": "pass",
}
THREE_HIVE_RING_SCHEMA_SMOKE_MANIFEST_FIELDS = (
    "condition",
    "seed",
    "config",
    "run_dir",
    "tick_count",
    "hive_count",
    "edge_count",
    "metric_schema_fields",
    "event_schema_fields",
    "source_ledger_schema_fields",
    "artifact_status",
    "scientific_status",
)
THREE_HIVE_RING_PREFLIGHT_COMPLETENESS_FIELDS = (
    "condition",
    "seed",
    "run_dir",
    "config_path",
    "manifest_path",
    "metrics_schema_path",
    "events_schema_path",
    "source_ledger_schema_path",
    "metrics_path",
    "events_path",
    "required_artifact_status",
    "metric_schema_status",
    "event_schema_status",
    "source_ledger_schema_status",
    "missing_metric_schema_fields",
    "missing_event_schema_fields",
    "missing_source_ledger_fields",
    "metrics_events_status",
    "status",
    "interpretation",
)
THREE_HIVE_RING_PREFLIGHT_MANIFEST_FIELDS = (
    "compare_dir",
    "out_dir",
    "expected_condition_count",
    "observed_condition_count",
    "expected_seed_count",
    "observed_seed_count",
    "expected_run_count",
    "observed_run_count",
    "missing_condition_seed_pairs",
    "schema_pass_count",
    "metrics_events_present_count",
    "status",
)
THREE_HIVE_RING_MECHANICS_MANIFEST_FIELDS = (
    "condition",
    "seed",
    "config",
    "run_dir",
    "tick_count",
    "hive_count",
    "edge_count",
    "metrics_rows",
    "events_rows",
    "source_ledger_rows",
    "mechanics_status",
    "scientific_status",
)
THREE_HIVE_RING_ANALYZER_COMPLETENESS_FIELDS = (
    "condition",
    "seed",
    "metrics_path",
    "events_path",
    "source_ledger_path",
    "metric_row_count",
    "event_row_count",
    "source_ledger_row_count",
    "required_field_status",
    "missing_required_fields",
    "status",
    "interpretation",
)
THREE_HIVE_RING_ANALYZER_SOURCE_LEDGER_FIELDS = (
    "condition",
    "seed",
    "event_ledger_status",
    "hive_ledger_status",
    "status",
    "interpretation",
)
THREE_HIVE_RING_ANALYZER_RESIDUAL_FIELDS = (
    "condition",
    "seed",
    "target_field",
    "row_count",
    "missing_required_fields",
    "control_fields_used",
    "residualization_status",
    "residual_variance",
    "lag1_autocorrelation",
    "nearest_neighbor_forecast_mae",
    "transition_compressibility_proxy",
    "status",
    "interpretation",
)
THREE_HIVE_RING_ANALYZER_NULL_CONTRAST_FIELDS = (
    "contrast",
    "seed",
    "control_condition",
    "target_field",
    "paired",
    "status",
    "positive_status",
    "control_status",
    "lag1_autocorrelation_delta",
    "nearest_neighbor_forecast_mae_delta",
    "transition_compressibility_delta",
    "gate_status",
    "interpretation",
)
THREE_HIVE_RING_ANALYZER_GUARDRAIL_FIELDS = (
    "seed",
    "baseline_condition",
    "completion_fraction_ratio",
    "backlog_ratio",
    "queued_age_ratio",
    "prediction_or_transfer_cost_fraction",
    "accepted_transfer_volume_min_per_directed_edge",
    "source_ledger_reconstruction_status",
    "status",
    "interpretation",
)
THREE_HIVE_RING_ANALYZER_MANIFEST_FIELDS = (
    "compare_dir",
    "out_dir",
    "condition_count",
    "seed_count",
    "run_count",
    "status",
)
THREE_HIVE_RING_SOURCE_LEDGER_CSV_FIELDS = (
    "tick",
    "condition",
    "seed",
    "hive_id",
    *THREE_HIVE_RING_SOURCE_LEDGER_FIELDS,
)


def _unique_fields(fields: tuple[str, ...]) -> tuple[str, ...]:
    return tuple(dict.fromkeys(fields))


def three_hive_ring_required_metric_fields() -> tuple[str, ...]:
    """Return the minimum per-hive metrics schema declared by the contract."""

    return _unique_fields(
        (*THREE_HIVE_RING_STATE_FIELDS, *THREE_HIVE_RING_RESIDUAL_CONTROLS)
    )


def three_hive_ring_required_event_fields() -> tuple[str, ...]:
    """Return the minimum transfer/event schema declared by the contract."""

    return _unique_fields(
        (
            "tick",
            "condition",
            "seed",
            "edge_id",
            *THREE_HIVE_RING_EDGE_FIELDS,
            *THREE_HIVE_RING_SOURCE_LEDGER_FIELDS,
        )
    )
